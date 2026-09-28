#!/usr/bin/env python3
"""
ltxgen - parameterised LTX-2.5 video generator for ComfyUI on Apple Silicon.

Builds the workflow, queues it, waits, then VERIFIES the output actually contains
a picture. On Apple Silicon this model intermittently emits NaN and produces a
completely black file while reporting success, so a black result is automatically
retried with a new seed rather than silently delivered.

  # single clip
  ./ltxgen.py --prompt "..." --res 1280x704 --seconds 4 --out lighthouse

  # with reference keyframes (path:frame, frame defaults to 0)
  ./ltxgen.py --prompt "..." --ref open.png:0 --ref close.png:-1 --out duel

  # batch
  ./ltxgen.py --batch clips.json

Run with the ComfyUI venv python:
  ~/Documents/Applications/ComfyUI/venv/bin/python ltxgen.py ...
"""
import argparse, json, os, random, sys, time, urllib.request, urllib.error, glob, subprocess

HOST = os.environ.get("LTXGEN_HOST", "http://127.0.0.1:8188")
# Resolved from ComfyUI's own tree, not from __file__.  SaveVideo writes into
# ComfyUI/output/video and LoadImage reads from ComfyUI/input, so deriving these
# from the script's location only worked while the script lived inside ComfyUI.
COMFY = os.environ.get("COMFY_ROOT", os.path.join(os.path.expanduser("~"), "Documents", "Applications", "ComfyUI"))
OUTDIR = os.path.join(COMFY, "output", "video")
INDIR = os.path.join(COMFY, "input")

MODELS = {
    "unet":  "ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors",
    "clip":  "gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors",
    "vae":   "ltx-2.5-video-vae-bf16.safetensors",
    "avae":  "ltx-2.5-audio-vae-bf16.safetensors",
    "upsc":  "ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors",
}
# Pixel-space finishing, applied after the VAE decode.  The latent upsampler in
# stage 2 is a refinement pass inside the sampler; these are the separate
# "motion enhancement / upscale" legs that sit between a render and delivery.
POST = {
    "interp":  "rife_v4.26_heavy.safetensors",  # RIFE optical-flow interpolation
}
# Both are 4x and both are downsampled to the delivery size afterwards.  The
# default is the plain CNN because this is per-frame work: UltraSharpV2 is a DAT
# transformer (2116 tensors against 702) and on MPS that difference is minutes
# per clip, not seconds.  Reach for it on a hero shot or a still, not a reel.
UPSCALERS = {
    "fast":    "4x-UltraSharp.pth",             # RRDBNet, classic ESRGAN
    "quality": "4x-UltraSharpV2.safetensors",   # DAT transformer, much slower
}
SIG_BASE   = "1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0"
SIG_REFINE = "0.85, 0.7250, 0.4219, 0.0"

DEFAULT_NEG = ("cartoon, anime, illustration, video game, 3d render, cgi, plastic skin, "
               "extra limbs, extra fingers, malformed hands, deformed face, warped geometry, "
               "flicker, strobing, duplicated subject, text, subtitles, watermark, logo, "
               "overexposed, blown highlights, washed out, low quality, blurry, jpeg artifacts")


# ---------------------------------------------------------------- helpers

def snap(v, m):
    return max(m, int(round(v / m)) * m)


def resolve_res(res, stages):
    """Width/height must divide by 32. Two-stage halves them first, so it needs 64."""
    w, h = (int(x) for x in res.lower().split("x"))
    m = 64 if stages == 2 else 32
    w2, h2 = snap(w, m), snap(h, m)
    if (w2, h2) != (w, h):
        print(f"  note: {w}x{h} snapped to {w2}x{h2} (must divide by {m} for {stages}-stage)")
    return w2, h2


def resolve_frames(seconds, fps):
    """Frame count must satisfy (n-1) % 8 == 0."""
    n = int(round(seconds * fps)) + 1
    n = ((n - 1) // 8) * 8 + 1
    return max(9, n)


def build(p):
    """Return a ComfyUI API-format workflow dict from a params dict."""
    w, h, fr, fps = p["w"], p["h"], p["frames"], p["fps"]
    two = p["stages"] == 2
    bw, bh = (w // 2, h // 2) if two else (w, h)

    g = {
        "1":  {"class_type": "UNETLoader", "inputs": {"unet_name": MODELS["unet"], "weight_dtype": "default"}},
        "2":  {"class_type": "CLIPLoader", "inputs": {"clip_name": MODELS["clip"], "type": "ltxv", "device": "default"}},
        "3":  {"class_type": "VAELoader",  "inputs": {"vae_name": MODELS["vae"]}},
        "4":  {"class_type": "VAELoader",  "inputs": {"vae_name": MODELS["avae"]}},
        "5":  {"class_type": "CLIPTextEncode", "inputs": {"text": p["prompt"],   "clip": ["2", 0]}},
        "6":  {"class_type": "CLIPTextEncode", "inputs": {"text": p["negative"], "clip": ["2", 0]}},
        "7":  {"class_type": "EmptyLTXVLatentVideo", "inputs": {"width": bw, "height": bh, "length": fr, "batch_size": 1}},
        "8":  {"class_type": "LTXVEmptyLatentAudio", "inputs": {"frames_number": fr, "frame_rate": fps, "batch_size": 1, "audio_vae": ["4", 0]}},
        "10": {"class_type": "LTXVConditioning", "inputs": {"positive": ["5", 0], "negative": ["6", 0], "frame_rate": float(fps)}},
        "12": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": p["sampler"]}},
        "13": {"class_type": "ManualSigmas", "inputs": {"sigmas": SIG_BASE}},
        "14": {"class_type": "RandomNoise", "inputs": {"noise_seed": p["seed"]}},
    }

    # LoRAs patch the transformer once; both stage guiders use the patched model.
    model = ["1", 0]
    node = 70
    for name, strength in p["loras"]:
        g[str(node)] = {"class_type": "LoraLoaderModelOnly", "inputs": {
            "model": model, "lora_name": name, "strength_model": strength}}
        model = [str(node), 0]
        node += 1

    pos, neg, lat = ["10", 0], ["10", 1], ["7", 0]

    # reference keyframes -> chained AddGuide on the stage-1 latent
    nid = 40
    for path, idx in p["refs"]:
        g[str(nid)]     = {"class_type": "LoadImage", "inputs": {"image": os.path.basename(path)}}
        g[str(nid + 1)] = {"class_type": "LTXVAddGuide", "inputs": {
            "positive": pos, "negative": neg, "vae": ["3", 0], "latent": lat,
            "image": [str(nid), 0], "frame_idx": idx, "strength": p["ref_strength"]}}
        pos, neg, lat = [str(nid + 1), 0], [str(nid + 1), 1], [str(nid + 1), 2]
        nid += 2

    g["9"]  = {"class_type": "LTXVConcatAVLatent", "inputs": {"video_latent": lat, "audio_latent": ["8", 0]}}
    g["11"] = {"class_type": "LTXVDualCFGGuider", "inputs": {
        "model": model, "positive": pos, "negative": neg,
        "video_cfg": p["video_cfg"], "audio_cfg": p["audio_cfg"]}}
    g["15"] = {"class_type": "SamplerCustomAdvanced", "inputs": {
        "noise": ["14", 0], "guider": ["11", 0], "sampler": ["12", 0],
        "sigmas": ["13", 0], "latent_image": ["9", 0]}}
    g["16"] = {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": ["15", 0]}}

    vid_latent, audio_latent = ["16", 0], ["16", 1]

    # guides append frames to the sequence; strip them before upscale/decode
    if p["refs"]:
        g["30"] = {"class_type": "LTXVCropGuides", "inputs": {"positive": pos, "negative": neg, "latent": vid_latent}}
        pos, neg, vid_latent = ["30", 0], ["30", 1], ["30", 2]

    if two:
        g["50"] = {"class_type": "LatentUpscaleModelLoader", "inputs": {"model_name": MODELS["upsc"]}}
        g["51"] = {"class_type": "LTXVLatentUpsampler", "inputs": {
            "samples": vid_latent, "upscale_model": ["50", 0], "vae": ["3", 0]}}
        g["52"] = {"class_type": "LTXVConcatAVLatent", "inputs": {"video_latent": ["51", 0], "audio_latent": audio_latent}}
        g["53"] = {"class_type": "ManualSigmas", "inputs": {"sigmas": SIG_REFINE}}
        g["54"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": p["seed"] + 1}}
        g["55"] = {"class_type": "LTXVDualCFGGuider", "inputs": {
            "model": model, "positive": pos, "negative": neg,
            "video_cfg": p["video_cfg"], "audio_cfg": p["audio_cfg"]}}
        g["56"] = {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["54", 0], "guider": ["55", 0], "sampler": ["12", 0],
            "sigmas": ["53", 0], "latent_image": ["52", 0]}}
        g["57"] = {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": ["56", 0]}}
        vid_latent, audio_latent = ["57", 0], ["57", 1]

    # Spatial tiling only. temporal_size must exceed the clip length or the decoder
    # chunks in time and leaves a visible seam every (temporal_size - temporal_overlap)
    # frames. ComfyUI's own decoder defaults to no temporal chunking (tile_t=999);
    # a value of 32/8 here put a seam every 24 frames, i.e. once per second at 24fps.
    g["17"] = {"class_type": "VAEDecodeTiled", "inputs": {
        "samples": vid_latent, "vae": ["3", 0],
        "tile_size": 512, "overlap": 64,
        "temporal_size": max(64, fr + 8), "temporal_overlap": 8}}
    frames_out, out_fps = ["17", 0], float(fps)

    # Upscale BEFORE interpolation, and in chunks.
    #
    # Order: the upscaler is the expensive stage, so it runs on the original
    # frame count rather than the interpolated one -- at x2 that is half the
    # work -- and RIFE then estimates flow on frames that already carry the
    # final detail.
    #
    # Chunking: the 4x model turns a 576x1024 frame into 2304x4096, and
    # ImageUpscaleWithModel allocates the whole output batch at once.  For 121
    # frames that is a 13 GB tensor, for 241 frames 27 GB, on a machine with
    # ~16 GB free after the model is resident.  Slicing the batch, resampling
    # each slice down to the delivery size immediately, and concatenating keeps
    # only one chunk at 4x, so peak cost is chunk_size/total of the above.
    if p["upscale"] > 1.0:
        g["62"] = {"class_type": "UpscaleModelLoader", "inputs": {
            "model_name": UPSCALERS.get(p["upscale_model"], p["upscale_model"])}}
        chunk = max(1, p["upscale_chunk"])
        node, accumulated = 100, None
        for start in range(0, fr, chunk):
            length = min(chunk, fr - start)
            g[str(node)] = {"class_type": "ImageFromBatch", "inputs": {
                "image": frames_out, "batch_index": start, "length": length}}
            g[str(node + 1)] = {"class_type": "ImageUpscaleWithModel", "inputs": {
                "upscale_model": ["62", 0], "image": [str(node), 0]}}
            g[str(node + 2)] = {"class_type": "ImageScale", "inputs": {
                "image": [str(node + 1), 0], "upscale_method": "lanczos",
                "width": p["final_w"], "height": p["final_h"], "crop": "disabled"}}
            piece = [str(node + 2), 0]
            if accumulated is None:
                accumulated = piece
            else:
                g[str(node + 3)] = {"class_type": "ImageBatch", "inputs": {
                    "image1": accumulated, "image2": piece}}
                accumulated = [str(node + 3), 0]
            node += 4
        frames_out = accumulated

    # RIFE emits (n-1)*mult + 1 frames, so multiplying fps by the same factor
    # keeps duration and audio sync exact.  This buys smoothness, not slow motion.
    if p["interpolate"] > 1:
        g["60"] = {"class_type": "FrameInterpolationModelLoader", "inputs": {"model_name": POST["interp"]}}
        g["61"] = {"class_type": "FrameInterpolate", "inputs": {
            "interp_model": ["60", 0], "images": frames_out, "multiplier": p["interpolate"]}}
        frames_out = ["61", 0]
        out_fps = float(fps * p["interpolate"])

    vid_out = {"images": frames_out, "fps": out_fps}
    if p["audio"]:
        g["18"] = {"class_type": "LTXVAudioVAEDecode", "inputs": {"samples": audio_latent, "audio_vae": ["4", 0]}}
        vid_out["audio"] = ["18", 0]
    g["19"] = {"class_type": "CreateVideo", "inputs": vid_out}
    g["20"] = {"class_type": "SaveVideo", "inputs": {
        "video": ["19", 0], "filename_prefix": f"video/{p['out']}", "format": "auto", "codec": "auto"}}
    return g


def verify(path):
    """(frames, pixel_std, audio_rms, (w, h)). pixel_std ~0 means black.

    Streams one frame at a time. Materialising every frame as float64 costs about
    2 GB for a 4s 720p clip, which thrashes badly on a machine already in swap.
    """
    import av, numpy as np
    n, sstd, dims = 0, 0.0, (0, 0)
    c = av.open(path)
    for f in c.decode(video=0):
        sstd += float(f.to_ndarray(format="rgb24").std())   # uint8 in, scalar out
        dims = (f.width, f.height)
        n += 1
    c.close()
    std = sstd / n if n else 0.0

    sq, cnt = 0.0, 0
    try:
        c2 = av.open(path)
        for f in c2.decode(audio=0):
            a = f.to_ndarray().astype("float32", copy=False)
            sq += float((a.astype("float64") ** 2).sum()); cnt += a.size
        c2.close()
    except Exception:
        pass
    rms = (sq / cnt) ** 0.5 if cnt else 0.0
    return n, std, rms, dims


def queue_and_wait(wf, label, timeout=7200):
    body = json.dumps({"prompt": wf, "client_id": "ltxgen"}).encode()
    req = urllib.request.Request(f"{HOST}/prompt", data=body, headers={"Content-Type": "application/json"})
    try:
        pid = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())["prompt_id"]
    except urllib.error.HTTPError as e:
        d = json.loads(e.read().decode())
        print(f"  REJECTED: {d.get('error',{}).get('message')}")
        for nid, v in d.get("node_errors", {}).items():
            for x in v.get("errors", []):
                print(f"    node {nid} [{v.get('class_type')}]: {x.get('message')} :: {str(x.get('details'))[:120]}")
        return None, 0.0
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            h = json.loads(urllib.request.urlopen(f"{HOST}/history/{pid}", timeout=30).read().decode())
        except Exception:
            time.sleep(5); continue
        if pid in h:
            st = h[pid]["status"]
            if st.get("completed") or st.get("status_str") == "error":
                dt = time.time() - t0
                if st.get("status_str") == "error":
                    for m in st.get("messages", []):
                        if m[0] == "execution_error":
                            print(f"  ERROR {m[1].get('node_type')}: {str(m[1].get('exception_message'))[:150]}")
                    return None, dt
                return h[pid], dt
        time.sleep(4)
    print("  TIMEOUT"); return None, time.time() - t0


def generate(p):
    print(f"\n=== {p['out']} ===")
    print(f"  {p['w']}x{p['h']}  {p['frames']} frames = {p['frames']/p['fps']:.2f}s @{p['fps']}fps  "
          f"{p['stages']}-stage  seed {p['seed']}" + (f"  refs {len(p['refs'])}" if p['refs'] else ""))
    post = []
    if p["interpolate"] > 1:
        post.append(f"RIFE x{p['interpolate']} -> {p['fps'] * p['interpolate']}fps")
    if p["upscale"] > 1.0:
        post.append(f"upscale x{p['upscale']:g} -> {p['final_w']}x{p['final_h']} "
                    f"({p['upscale_model']}, {p['upscale_chunk']}-frame chunks)")
    if p["loras"]:
        post.append("loras " + ", ".join(f"{n}@{s:g}" for n, s in p["loras"]))
    if post:
        print("  post: " + "  ·  ".join(post))
    if p["dry_run"]:
        print("  (dry run)"); return None

    for attempt in range(p["retries"] + 1):
        rec, dt = queue_and_wait(build(p), p["out"])
        if rec is None:
            return None
        files = sorted(glob.glob(os.path.join(OUTDIR, f"{p['out']}_*.mp4")))
        if not files:
            print("  no output file"); return None
        f = files[-1]
        n, std, rms, dims = verify(f)
        want_n = (p["frames"] - 1) * p["interpolate"] + 1
        want_wh = (p["final_w"], p["final_h"]) if p["upscale"] > 1.0 else (p["w"], p["h"])
        ok = std > 1.0 and n == want_n and dims == want_wh
        if std <= 1.0:
            tag = "BLACK/NaN"
        elif n != want_n:
            tag = f"frame count {n} != {want_n}"
        elif dims != want_wh:
            tag = f"size {dims[0]}x{dims[1]} != {want_wh[0]}x{want_wh[1]}"
        else:
            tag = "ok"
        print(f"  {dt:6.1f}s  frames={n} {dims[0]}x{dims[1]} std={std:5.2f} rms={rms:.4f}  [{tag}]")
        if ok:
            side = os.path.splitext(f)[0] + ".params.json"
            json.dump({k: v for k, v in p.items() if k != "dry_run"}, open(side, "w"), indent=1)
            return f
        if attempt < p["retries"]:
            p["seed"] = random.randint(1, 2**31)
            print(f"  black render, retrying with seed {p['seed']}")
            try: os.remove(f)
            except OSError: pass
    print("  gave up after retries")
    return None


def stage_refs(refs, frames, target=None):
    """Copy refs into ComfyUI/input and resolve negative frame indices.

    LTXVAddGuide resizes a reference to the output dimensions with crop="center"
    and says nothing when the aspect ratios differ, so a portrait fed to a
    widescreen render loses the top of the head.  Warn before spending the time.
    """
    out = []
    for r in refs:
        path, _, idx = r.partition(":")
        idx = int(idx) if idx else 0
        if idx < 0:
            idx = frames + idx          # -1 -> last frame
        idx = (idx // 8) * 8            # snap to a latent boundary
        if target:
            try:
                from PIL import Image
                with Image.open(path) as im:
                    rw, rh = im.size
                ra, ta = rw / rh, target[0] / target[1]
                if abs(ra - ta) / ta > 0.02:
                    print(f"  warning: reference {os.path.basename(path)} is {rw}x{rh} "
                          f"({ra:.2f}:1) but output is {target[0]}x{target[1]} ({ta:.2f}:1); "
                          f"it will be centre-cropped. Crop it yourself to control what is lost.")
            except Exception:
                pass
        dst = os.path.join(INDIR, os.path.basename(path))
        if os.path.abspath(path) != os.path.abspath(dst):
            import shutil; shutil.copy(path, dst)
        out.append((dst, idx))
    return out


def make_params(a, prompt, out, refs=None):
    frames = resolve_frames(a.seconds, a.fps)
    w, h = resolve_res(a.res, a.stages)
    loras = []
    for entry in (a.lora or []):
        name, _, strength = entry.partition(":")
        loras.append((name, float(strength) if strength else 1.0))
    # Final delivery size after the pixel upscale.  Kept on the 2-grid so the
    # H.264 encoder never has to pad an odd dimension.
    final_w = int(round(w * a.upscale / 2)) * 2
    final_h = int(round(h * a.upscale / 2)) * 2
    return {
        "prompt": prompt, "negative": a.negative, "out": out,
        "w": w, "h": h, "frames": frames, "fps": a.fps,
        "seed": a.seed if a.seed is not None else random.randint(1, 2**31),
        "stages": a.stages, "sampler": a.sampler,
        "video_cfg": a.video_cfg, "audio_cfg": a.audio_cfg,
        "audio": not a.no_audio, "refs": stage_refs(refs or a.ref or [], frames, (w, h)),
        "ref_strength": a.ref_strength, "retries": a.retries, "dry_run": a.dry_run,
        "loras": loras, "upscale": a.upscale, "interpolate": a.interpolate,
        "upscale_chunk": a.upscale_chunk, "upscale_model": a.upscale_model,
        "final_w": final_w, "final_h": final_h,
    }


def main():
    ap = argparse.ArgumentParser(description="Generate LTX-2.5 clips through ComfyUI.")
    ap.add_argument("--prompt"); ap.add_argument("--prompt-file")
    ap.add_argument("--batch", help="JSON file: [{out, prompt, seconds?, res?, seed?, refs?}, ...]")
    ap.add_argument("--negative", default=DEFAULT_NEG)
    ap.add_argument("--res", default="1280x704")
    ap.add_argument("--seconds", type=float, default=4.0)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--ref", action="append", help="path[:frame], frame may be negative")
    ap.add_argument("--ref-strength", type=float, default=1.0)
    ap.add_argument("--stages", type=int, choices=[1, 2], default=2)
    ap.add_argument("--sampler", default="euler_ancestral")
    ap.add_argument("--video-cfg", type=float, default=1.0)
    ap.add_argument("--audio-cfg", type=float, default=1.0)
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--lora", action="append", metavar="NAME[:STRENGTH]",
                    help="LTX LoRA applied to the transformer, repeatable")
    ap.add_argument("--upscale", type=float, default=1.0, metavar="N",
                    help="pixel upscale after decode, e.g. 2.0; uses a 4x ESRGAN then resamples down")
    ap.add_argument("--interpolate", type=int, default=1, choices=[1, 2, 3, 4], metavar="N",
                    help="RIFE frame interpolation; fps is multiplied to match, so duration is unchanged")
    ap.add_argument("--upscale-model", default="fast", metavar="NAME",
                    help="'fast' (CNN, the default), 'quality' (DAT transformer, far slower), "
                         "or an explicit filename from models/upscale_models")
    ap.add_argument("--upscale-chunk", type=int, default=16, metavar="N",
                    help="frames per upscale pass; lower it if the upscale stage pushes the machine into swap")
    ap.add_argument("--retries", type=int, default=2, help="reseed and retry on a black render")
    ap.add_argument("--out", default="clip")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    try:
        urllib.request.urlopen(f"{HOST}/system_stats", timeout=10)
    except Exception:
        print(f"ComfyUI not reachable at {HOST}. Start it with ./start.sh"); sys.exit(1)

    jobs = []
    if a.batch:
        for item in json.load(open(a.batch)):
            sub = argparse.Namespace(**vars(a))
            for k in ("seconds", "res", "seed", "stages", "fps", "negative", "ref_strength",
                      "upscale", "interpolate", "lora", "upscale_chunk", "upscale_model"):
                if k in item: setattr(sub, k, item[k])
            jobs.append(make_params(sub, item["prompt"], item["out"], item.get("refs")))
    else:
        prompt = a.prompt or (open(a.prompt_file).read().strip() if a.prompt_file else None)
        if not prompt: ap.error("need --prompt, --prompt-file or --batch")
        jobs.append(make_params(a, prompt, a.out))

    made, t0 = [], time.time()
    for p in jobs:
        f = generate(p)
        if f: made.append(f)
    print(f"\n{len(made)}/{len(jobs)} clips in {(time.time()-t0)/60:.1f} min")
    for f in made: print("  " + f)


if __name__ == "__main__":
    main()
