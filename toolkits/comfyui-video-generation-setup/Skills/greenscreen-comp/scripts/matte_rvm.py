#!/usr/bin/env python3
"""
matte_rvm.py — Segmentation matte with RobustVideoMatting, for footage whose
green screen cannot be keyed.

Why this rather than a chroma key: measured on this footage, chroma separation is
62 (want 90+), saturation 0.43 (want 0.70+) and the screen falls off 41 luma
levels top to bottom. A single similarity value cannot cover both ends. Tested
directly — `chromakey` dissolves the subject at every threshold from 0.16 to
0.28, and `colorkey` either leaves the screen at 0.16 or punches through the
forehead and hair at 0.30. A learned matte segments the *person* and ignores the
backdrop, so an unevenly lit wrinkled screen stops mattering.

**Licence, which is the deciding factor here.** RVM is GPL-3.0. Copyleft attaches
to distributing *software*, not to footage rendered with it, so a monetised
channel can use the output. MatAnyone and MatAnyone2 (NTU S-Lab 1.0) and
SAM2Matting (non-commercial CC) are technically strong and **barred** for
commercial use without written permission. Do not swap this for one of those
because a leaderboard says it scores better.

  python matte_rvm.py in.mov -o host_clean.mov            # ProRes 4444 + alpha
  python matte_rvm.py in.mov -o comp.mov --background plate.mp4
  python matte_rvm.py in.mov -o test.mov --start 60 --duration 6   # benchmark

The matte is produced ONCE, before compositing, and everything downstream
composites rather than re-keys.

A note on the chair: RVM segments people. The office chair behind the speaker is
not a person, so it is matted out along with the screen. That is usually what you
want — but check it, because a chair back that half-survives looks worse than one
that is fully gone.
"""

import argparse
import os
import subprocess
import sys
import time

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE", "ffprobe")

DEFAULT_MODEL = os.path.expanduser(
    "~/Developer/video-pipeline/models/rvm_mobilenetv3_fp32.torchscript")


def probe(path):
    r = subprocess.run(
        [FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    v = r.stdout.split()
    w, h = int(v[0]), int(v[1])
    num, den = v[2].split("/")
    fps = float(num) / float(den)
    return w, h, fps, float(v[3])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--background",
                    help="composite over this still or video instead of "
                         "emitting alpha")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--duration", type=float)
    ap.add_argument("--downsample", type=float, default=0.25,
                    help="RVM internal scale. 0.25 suits 1080p; lower is faster "
                         "and softer on hair, higher is slower and can chatter.")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "mps"])
    ap.add_argument("--despill", type=float, default=0.5,
                    help="green spill removal strength 0..1 (0 disables). The "
                         "matte gives you a clean edge; it does NOT remove the "
                         "green the screen cast onto hair and shoulders, which "
                         "is what makes a composite read as fake.")
    ap.add_argument("--fg-grade",
                    help="eq= parameters applied to the FOREGROUND before "
                         "compositing, e.g. 'brightness=-0.03:saturation=0.95'. "
                         "Matching the subject to the plate — white balance, "
                         "exposure, black point — does more for realism than any "
                         "amount of matte tuning. A frontally-lit face over a "
                         "dark side-lit plate will never sit right.")
    ap.add_argument("--fg-temp", type=float, default=0.0,
                    help="warm(+)/cool(-) shift on the foreground, -1..1, via "
                         "colorbalance midtones")
    ap.add_argument("--light-wrap", type=float, default=0.0,
                    help="light wrap strength 0..1. Real light from a background "
                         "spills around a foreground subject's edges; composites "
                         "lack it, which is why they look cut out. This is the "
                         "single highest-value step after the matte itself.")
    ap.add_argument("--wrap-width", type=float, default=12.0,
                    help="how far the wrap reaches inside the edge, in pixels")
    ap.add_argument("--encoder", default="prores_videotoolbox",
                    choices=["prores_videotoolbox", "prores_ks"],
                    help="prores_videotoolbox uses the Apple Silicon media engine "
                         "and is several times faster; prores_ks is the software "
                         "encoder, slower but available everywhere.")
    ap.add_argument("--matte-only", action="store_true",
                    help="write the alpha as a greyscale video, for inspection")
    a = ap.parse_args()

    import numpy as np
    import torch

    if not os.path.exists(a.model):
        sys.exit(f"model not found: {a.model}\n"
                 "  curl -fL -o models/rvm_mobilenetv3_fp32.torchscript \\\n"
                 "    https://github.com/PeterL1n/RobustVideoMatting/releases/"
                 "download/v1.0.0/rvm_mobilenetv3_fp32.torchscript")

    dev = a.device
    if dev == "auto":
        dev = "mps" if torch.backends.mps.is_available() else "cpu"

    W, H, fps, dur = probe(a.input)
    n_expect = int(round((a.duration if a.duration else dur - a.start) * fps))
    print(f"  source   {W}x{H} @ {fps:.3f} fps, {dur:.2f}s")
    print(f"  matting  {a.start:.2f}s + "
          f"{a.duration if a.duration else dur - a.start:.2f}s "
          f"(~{n_expect} frames) on {dev}")

    model = torch.jit.load(a.model, map_location=dev)
    model.eval()

    # decode -> raw RGB frames
    dec = [FFMPEG, "-hide_banner", "-loglevel", "error"]
    if a.start:
        dec += ["-ss", f"{a.start:.6f}"]
    dec += ["-i", a.input]
    if a.duration:
        dec += ["-t", f"{a.duration:.6f}"]
    dec += ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    din = subprocess.Popen(dec, stdout=subprocess.PIPE, bufsize=10 ** 8)

    # encode
    enc = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", f"{fps}", "-i", "-"]
    despill = (f"despill=type=green:mix={a.despill}:expand=0"
               if a.despill > 0 else None)

    if a.background:
        # composite here rather than downstream: the alpha never has to survive
        # an intermediate encode, which is where fringing usually appears
        # ---- foreground treatment, in order: despill, then grade to the plate
        fchain = []
        if despill:
            fchain.append(despill)
        if a.fg_temp:
            t = max(-1.0, min(1.0, a.fg_temp))
            fchain.append(f"colorbalance=rm={t*0.12:.4f}:gm={t*0.01:.4f}:"
                          f"bm={-t*0.12:.4f}")
        if a.fg_grade:
            fchain.append(f"eq={a.fg_grade}")
        fpre = ",".join(fchain) if fchain else "null"

        bgchain = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                   f"crop={W}:{H},setsar=1")

        if a.light_wrap > 0:
            # Light wrap: a band of the BLURRED BACKGROUND, laid just inside the
            # subject's own edge. The band comes from the difference between the
            # alpha and a blurred copy of it, so it hugs the silhouette exactly
            # and needs no separate matte.
            sigma = max(1.0, a.wrap_width)
            fc = (
                f"[0:v]{fpre},split=2[fg1][fga];"
                f"[fga]alphaextract,split=2[a1][a2];"
                f"[a1]gblur=sigma={sigma:.2f}[ab];"
                f"[a2][ab]blend=all_mode=difference,"
                f"eq=contrast=3.0:brightness={-0.5 + a.light_wrap * 0.5:.3f},"
                f"format=gray[band];"
                f"[1:v]{bgchain},split=2[bg][bgw];"
                f"[bgw]gblur=sigma={sigma*3:.2f},format=gbrp[bgb];"
                f"[bgb][band]alphamerge[wrap];"
                f"[bg][fg1]overlay=shortest=1[comp];"
                f"[comp][wrap]overlay=shortest=1[v]"
            )
        else:
            fc = (f"[0:v]{fpre}[fg1];[1:v]{bgchain}[bg];"
                  f"[bg][fg1]overlay=shortest=1[v]")

        enc += ["-stream_loop", "-1", "-i", a.background,
                "-filter_complex", fc,
                "-map", "[v]"]
        if a.encoder == "prores_videotoolbox":
            enc += ["-c:v", "prores_videotoolbox", "-profile:v", "2",
                    "-pix_fmt", "p210"]
        else:
            enc += ["-c:v", "prores_ks", "-profile:v", "2"]
    elif a.matte_only:
        enc += ["-filter_complex", "[0:v]alphaextract[v]", "-map", "[v]",
                "-c:v", "prores_ks", "-profile:v", "3"]
    else:
        # ProRes 4444 carries the alpha channel; 422 would silently drop it
        if despill:
            enc += ["-vf", despill]
        enc += ["-c:v", "prores_ks", "-profile:v", "4444",
                "-pix_fmt", "yuva444p10le", "-alpha_bits", "16"]
    enc += ["-an", a.out]
    dout = subprocess.Popen(enc, stdin=subprocess.PIPE)

    frame_bytes = W * H * 3
    rec = [None] * 4
    n = 0
    t0 = time.time()
    alpha_sum = 0.0

    with torch.no_grad():
        while True:
            buf = din.stdout.read(frame_bytes)
            if len(buf) < frame_bytes:
                break
            arr = np.frombuffer(buf, dtype=np.uint8).reshape(H, W, 3)
            src = (torch.from_numpy(arr.copy()).to(dev)
                   .permute(2, 0, 1).unsqueeze(0).float() / 255.0)
            fgr, pha, *rec = model(src, *rec, a.downsample)
            # premultiplied-safe: RVM returns foreground colour and alpha
            rgba = torch.cat([fgr, pha], dim=1)[0].clamp(0, 1)
            alpha_sum += float(pha.mean())
            out = (rgba.permute(1, 2, 0) * 255).to(torch.uint8).cpu().numpy()
            dout.stdin.write(out.tobytes())
            n += 1
            if n % 60 == 0:
                el = time.time() - t0
                print(f"    {n} frames  {n/el:.1f} fps  "
                      f"{n/max(1,n_expect)*100:.0f}%", flush=True)

    din.stdout.close()
    dout.stdin.close()
    dout.wait()
    din.wait()

    el = time.time() - t0
    print(f"\n  {n} frames in {el:.1f}s ({n/max(el,0.01):.1f} fps)")
    if n:
        cov = alpha_sum / n
        print(f"  mean alpha coverage {cov*100:.1f}% of frame")
        if cov < 0.05:
            print("  WARNING: almost nothing was matted — check the input")
        elif cov > 0.75:
            print("  WARNING: almost everything was kept — the model may not "
                  "have found a person")
    print(f"  wrote {a.out}")
    print("\n  Watch the edges under motion, not a still frame. What matters is "
          "temporal\n  stability at the hair line and around a moving hand — a "
          "matte that is\n  perfect on one frame and chatters across ten is worse "
          "than a softer stable one.")


if __name__ == "__main__":
    main()
