#!/usr/bin/env python3
"""
render_pip.py — Composite a portrait talking head over full-frame content.

Takes a typed spec instead of a hand-written filtergraph, because the filtergraph
for a rounded, glowing, animated PIP is long enough that hand-editing it reliably
introduces syntax errors. Emits the command, or runs it.

  python render_pip.py --spec pip.json --base base.mp4 -o out.mp4
  python render_pip.py --spec pip.json --base base.mp4 --print-only

SPEC (all keys optional except source):
{
  "source": "portrait.mov",
  "source_range": {"start": 121.2, "end": 129.6},
  "sync_offset": -0.083,          // seconds; + means PIP source is late
  "position": "bottom_right",     // bottom_right | bottom_left
  "max_width_ratio": 0.19,        // of frame width
  "max_height_ratio": 0.60,       // of frame height  (binding constraint)
  "margin": 48,
  "corner_radius": 24,
  "edge_width": 2,
  "edge_color": "white",
  "halo_opacity": 0.22,
  "halo_blur": 24,
  "halo_spread": 40,
  "audio_source": "master",       // master | pip | none
  "fade": 0.25                    // entrance/exit seconds, 0 to disable
}

NOTES
  * PIP height is the binding constraint for 9:16 inserts. A 28%-width portrait
    at 1920 is 538x956 -- 88% of a 1080 frame. The spec clamps on BOTH axes and
    height usually wins.
  * The halo is masked to the rounded shape, not a blurred rectangle, so it does
    not show square corners behind rounded ones.
  * Audio defaults to the master (base) track. The PIP camera is a picture
    source; its audio is usually the wrong one and often absent entirely.
"""

import argparse
import json
import subprocess
import sys


def probe(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "json", path],
        capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffprobe failed on {path}:\n{r.stderr}")
    s = json.loads(r.stdout)["streams"][0]
    return int(s["width"]), int(s["height"])


def has_audio(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
         "stream=index", "-of", "csv=p=0", path],
        capture_output=True, text=True)
    return bool(r.stdout.strip())


def even(n):
    n = int(round(n))
    return n if n % 2 == 0 else n + 1


def rounded_mask_expr(plate_w, plate_h, shape_w, shape_h, r):
    """Alpha for a rounded rect of shape_w x shape_h CENTRED in a plate of
    plate_w x plate_h. The plate is larger than the shape when the mask will be
    blurred: the blur needs transparent margin to fall off into, otherwise the
    plate's own square boundary shows as a hard edge."""
    r = max(0, min(int(r), min(shape_w, shape_h) // 2))
    cx, cy = plate_w / 2.0, plate_h / 2.0
    ix, iy = shape_w / 2.0 - r, shape_h / 2.0 - r     # straight-edge half-extents
    if r == 0:
        return (f"if(lte(abs(X-{cx:.1f})\\,{shape_w/2.0:.1f})*"
                f"lte(abs(Y-{cy:.1f})\\,{shape_h/2.0:.1f})\\,255\\,0)")
    return (f"if(gt(hypot(max(0\\,abs(X-{cx:.1f})-{ix:.1f})\\,"
            f"max(0\\,abs(Y-{cy:.1f})-{iy:.1f}))\\,{r})\\,0\\,255)")


def build(spec, base_path, out_path):
    bw, bh = probe(base_path)
    src = spec["source"]
    sw, sh = probe(src)

    # --- size: clamp on both axes, height usually binds for 9:16 ---
    max_w = bw * float(spec.get("max_width_ratio", 0.19))
    max_h = bh * float(spec.get("max_height_ratio", 0.60))
    ar = 9 / 16.0
    w = min(max_w, max_h * ar)
    h = w / ar
    W, H = even(w), even(h)

    margin = int(spec.get("margin", 48))
    radius = int(spec.get("corner_radius", 24))
    edge = int(spec.get("edge_width", 2))
    edge_color = spec.get("edge_color", "white")
    halo_op = float(spec.get("halo_opacity", 0.22))
    halo_blur = int(spec.get("halo_blur", 24))
    spread = int(spec.get("halo_spread", 40))
    # A Gaussian needs ~3 sigma of transparent margin to fall to zero. With less,
    # the halo plate's own square boundary shows as a hard edge.
    min_spread = int(3 * halo_blur)
    if spread < min_spread:
        spread = min_spread
    fade = float(spec.get("fade", 0.25))
    pos = spec.get("position", "bottom_right")

    GW, GH = even(W + 2 * spread), even(H + 2 * spread)
    EW, EH = even(W + 2 * edge), even(H + 2 * edge)

    # --- crop the source to 9:16 around centre (face-tracked crop can override) ---
    crop_w = min(sw, sh * ar)
    crop_h = crop_w / ar
    cx = spec.get("crop_x", (sw - crop_w) / 2)
    cy = spec.get("crop_y", 0)

    f = []
    # 1. reframe + scale
    f.append(f"[1:v]crop={even(crop_w)}:{even(crop_h)}:{int(cx)}:{int(cy)},"
             f"scale={W}:{H},setsar=1[cam]")
    # 2. rounded alpha mask at PIP size
    f.append(f"color=c=black:s={W}x{H}:d=1,format=gray,"
             f"geq=lum='{rounded_mask_expr(W, H, W, H, radius)}'[mask]")
    f.append("[cam][mask]alphamerge[camr]")
    # 3. crisp edge: same rounded shape, slightly larger, behind the cam
    f.append(f"color=c={edge_color}:s={EW}x{EH}:d=1,format=gray,"
             f"geq=lum='{rounded_mask_expr(EW, EH, EW, EH, radius + edge)}'[emask]")
    f.append(f"color=c={edge_color}:s={EW}x{EH}:d=1[ecol]")
    f.append("[ecol][emask]alphamerge[edge]")
    # 4. halo: rounded shape at spread size, blurred, low alpha
    f.append(f"color=c={edge_color}:s={GW}x{GH}:d=1,format=gray,"
             f"geq=lum='{rounded_mask_expr(GW, GH, W + spread, H + spread, radius + spread // 2)}',"
             f"gblur=sigma={halo_blur}[gmask]")
    f.append(f"color=c={edge_color}:s={GW}x{GH}:d=1[gcol]")
    f.append(f"[gcol][gmask]alphamerge,"
             f"colorchannelmixer=aa={halo_op:.3f}[halo]")

    # --- placement ---
    if pos == "bottom_left":
        ex, ey = margin - edge, f"H-h-{margin - edge}"
        gx, gy = margin - spread, f"H-h-{margin - spread}"
        px, py = margin, f"H-h-{margin}"
        ex_s, gx_s, px_s = str(max(0, ex)), str(max(0, gx)), str(px)
    else:
        ex_s = f"W-w-{max(0, margin - edge)}"
        gx_s = f"W-w-{max(0, margin - spread)}"
        px_s = f"W-w-{margin}"
        ey = f"H-h-{max(0, margin - edge)}"
        gy = f"H-h-{max(0, margin - spread)}"
        py = f"H-h-{margin}"

    # --- optional fade in/out on the PIP stack only ---
    sr = spec.get("source_range")
    enable = ""
    if sr:
        # window on the OUTPUT timeline
        t0, t1 = float(sr["start"]), float(sr["end"])
        enable = f":enable='between(t,{t0},{t1})'"
        if fade > 0:
            for lbl in ("halo", "edge", "camr"):
                f.append(f"[{lbl}]fade=t=in:st={t0}:d={fade}:alpha=1,"
                         f"fade=t=out:st={max(t0, t1 - fade)}:d={fade}:alpha=1"
                         f"[{lbl}f]")
            halo_l, edge_l, cam_l = "[halof]", "[edgef]", "[camrf]"
        else:
            halo_l, edge_l, cam_l = "[halo]", "[edge]", "[camr]"
    else:
        halo_l, edge_l, cam_l = "[halo]", "[edge]", "[camr]"

    f.append(f"[0:v]{halo_l}overlay={gx_s}:{gy}{enable}[b1]")
    f.append(f"[b1]{edge_l}overlay={ex_s}:{ey}{enable}[b2]")
    f.append(f"[b2]{cam_l}overlay={px_s}:{py}{enable},format=yuv420p[out]")

    # --- audio: master by default, and only if it exists ---
    audio_src = spec.get("audio_source", "master")
    maps = ["-map", "[out]"]
    if audio_src == "master" and has_audio(base_path):
        maps += ["-map", "0:a"]
    elif audio_src == "pip" and has_audio(src):
        maps += ["-map", "1:a"]

    # --- input-side trim/sync for the PIP source ---
    pre = []
    off = float(spec.get("sync_offset", 0.0))
    if off:
        pre += ["-itsoffset", f"{off:.4f}"]

    cmd = (["ffmpeg", "-hide_banner", "-i", base_path]
           + pre + ["-i", src,
                    "-filter_complex", ";".join(f)]
           + maps
           + ["-c:v", "libx264", "-crf", "18", "-preset", "medium",
              "-c:a", "copy", "-y", out_path])

    meta = {"frame": f"{bw}x{bh}", "pip": f"{W}x{H}",
            "pip_pct": f"{100*W/bw:.1f}% w / {100*H/bh:.1f}% h",
            "audio": audio_src if "-map" in maps[2:] else "none"}
    return cmd, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("-o", "--out", default="pip_out.mp4")
    ap.add_argument("--print-only", action="store_true")
    args = ap.parse_args()

    spec = json.load(open(args.spec))
    cmd, meta = build(spec, args.base, args.out)

    print(f"frame {meta['frame']}  ->  PIP {meta['pip']}  ({meta['pip_pct']}), "
          f"audio: {meta['audio']}")
    if meta_warn := (int(meta["pip"].split("x")[1]) / int(meta["frame"].split("x")[1])):
        if meta_warn > 0.66:
            print(f"  WARNING: PIP is {meta_warn*100:.0f}% of frame height — "
                  "likely covering too much. Lower max_height_ratio.")

    if args.print_only:
        print("\n" + " ".join(
            f"'{c}'" if (" " in c or ";" in c) else c for c in cmd))
        return

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2500:], file=sys.stderr)
        sys.exit(f"\nffmpeg failed (exit {r.returncode})")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
