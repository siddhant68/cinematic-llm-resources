#!/usr/bin/env python3
"""
analyze_framing.py — Measure where the subject actually sits in frame, across
time, so the layout system is built from the footage rather than from one frame.

Frame design is stage 0: caption regions, PIP regions and lower-third safe areas
are constraints every later stage respects. Deciding them from a single frame is
how you discover at composite time that the PIP covers the speaker's hand.

A single bounding box is the wrong summary. A seated speaker is narrow at the
head and wide at the shoulders, so one box says "the subject spans 75% of the
frame" while the upper two-thirds are in fact wide open. What a layout needs is
an **occupancy heatmap**: for every cell of the frame, the fraction of sampled
frames in which the subject covers it. A candidate overlay region is then scored
directly — max occupancy over its cells — instead of guessed at.

  python analyze_framing.py footage.mov --frames 48 --json framing.json
  python analyze_framing.py footage.mov --probe 0.62,0.62,0.19,0.34   # x,y,w,h fractions

Occupancy thresholds used for the verdict:
  <0.02   clear      — safe for a persistent overlay
  <0.15   marginal   — safe for a brief overlay, or with a drop shadow
  >=0.15  occupied   — an overlay here covers the speaker
"""

import argparse
import io
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE", "ffprobe")

CLEAR, MARGINAL = 0.02, 0.15


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = sh([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
            "stream=width,height", "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1", path])
    vals = r.stdout.split()
    if len(vals) < 3:
        sys.exit(f"could not probe {path}")
    return int(vals[0]), int(vals[1]), float(vals[2])


def grab(path, t, w, h):
    r = subprocess.run(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}",
         "-i", path, "-frames:v", "1", "-vf", f"scale={w}:{h}",
         "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    if not r.stdout:
        return None
    return np.asarray(Image.open(io.BytesIO(r.stdout)).convert("RGB"), dtype=np.float32)


def subject_mask(rgb):
    """True where the pixel is NOT screen-green.

    Relative rather than absolute: green leads the other channels by a margin
    scaled to local brightness, so the 41-level top-to-bottom falloff on this
    screen does not change the classification. Skin, hair, a black shirt and a
    black chair all fail the greenness test, which is what we want — the chair
    is a real object an overlay would collide with.
    """
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = np.maximum(rgb.max(axis=-1), 1.0)
    return ((g - np.maximum(r, b)) / lum) < 0.08


def render_heatmap(occ, w, h, path):
    img = (np.clip(occ, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(img).resize((w, h), Image.NEAREST).save(path)


def score_region(occ, fx, fy, fw, fh):
    H, W = occ.shape
    x0, x1 = int(fx * W), int(round((fx + fw) * W))
    y0, y1 = int(fy * H), int(round((fy + fh) * H))
    x1, y1 = max(x1, x0 + 1), max(y1, y0 + 1)
    cell = occ[y0:y1, x0:x1]
    return float(cell.max()), float(cell.mean())


def verdict(mx):
    if mx < CLEAR:
        return "CLEAR"
    if mx < MARGINAL:
        return "MARGINAL"
    return "OCCUPIED"



# ---------------------------------------------------------------- clear rects

def largest_clear_rect(occ, thresh, aspect=None, tol=0.12, px_w=1920, px_h=1080):
    """Largest axis-aligned rectangle whose every cell is below `thresh`.

    Standard maximal-rectangle-in-histogram sweep, O(rows*cols). When `aspect`
    (w/h) is given, the widest rectangle matching that ratio within `tol` wins
    instead of the largest by area — a PIP has a fixed shape, so the biggest
    free blob is not the useful answer.
    """
    H, W = occ.shape
    free = (occ < thresh).astype(np.int32)
    heights = np.zeros(W, dtype=np.int32)
    best = None
    for y in range(H):
        heights = np.where(free[y] > 0, heights + 1, 0)
        stack = []
        for x in range(W + 1):
            cur = heights[x] if x < W else 0
            start = x
            while stack and stack[-1][1] >= cur:
                sx, sh_ = stack.pop()
                w, h = x - sx, int(sh_)
                if h == 0 or w == 0:
                    start = sx
                    continue
                fw, fh = w / W, h / H
                if aspect is not None:
                    # compare PIXEL aspect: the grid cells are not square, so a
                    # frame-fraction ratio is not the shape you see on screen.
                    if fh <= 0:
                        start = sx
                        continue
                    got = (fw * px_w) / (fh * px_h)
                    if abs(got - aspect) / aspect > tol:
                        start = sx
                        continue
                score = fw * fh
                cand = (score, sx, y - h + 1, x, y + 1)
                if best is None or score > best[0]:
                    best = cand
                start = sx
            stack.append((start, cur))
    if best is None:
        return None
    _, x0, y0, x1, y1 = best
    return (x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H)


def fmt_rect(r, W, H):
    if r is None:
        return "none found"
    x, y, w, h = r
    return (f"x {x*100:5.1f}%  y {y*100:5.1f}%  w {w*100:5.1f}%  h {h*100:5.1f}%   "
            f"[{int(x*W):4d},{int(y*H):4d} {int(w*W):4d}x{int(h*H):4d}px]")


# candidate regions as (name, x, y, w, h) in frame fractions
CANDIDATES = [
    ("PIP bottom-right      ", 0.78, 0.38, 0.19, 0.60),
    ("PIP bottom-left       ", 0.03, 0.38, 0.19, 0.60),
    ("PIP top-right         ", 0.78, 0.02, 0.19, 0.60),
    ("side panel right 1/3  ", 0.66, 0.00, 0.34, 1.00),
    ("side panel left 1/3   ", 0.00, 0.00, 0.34, 1.00),
    ("upper-right quadrant  ", 0.55, 0.03, 0.42, 0.42),
    ("upper-left quadrant   ", 0.03, 0.03, 0.42, 0.42),
    ("caption band (low)    ", 0.10, 0.80, 0.80, 0.14),
    ("caption band (raised) ", 0.10, 0.72, 0.80, 0.13),
    ("lower third bar       ", 0.05, 0.70, 0.45, 0.16),
    ("top banner            ", 0.05, 0.02, 0.90, 0.10),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--frames", type=int, default=48)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--json", help="write the full report here")
    ap.add_argument("--heatmap", help="write a PNG occupancy heatmap here")
    ap.add_argument("--probe", action="append", default=[],
                    help="extra region to score: x,y,w,h as frame fractions")
    ap.add_argument("--grid", type=int, default=96, help="heatmap columns")
    a = ap.parse_args()

    W, H, dur = probe(a.input)
    t1 = a.end if a.end is not None else dur
    gw = a.grid
    gh = int(round(gw * H / W))

    print(f"\n{'='*74}\nFRAME DESIGN — occupancy across time\n{'='*74}")
    print(f"  source     {os.path.basename(a.input)}  {W}x{H}  {dur:.2f}s")
    print(f"  sampling   {a.frames} frames over {a.start:.1f}-{t1:.1f}s  "
          f"(grid {gw}x{gh})")

    acc = np.zeros((gh, gw), dtype=np.float32)
    n = 0
    heads = []
    for t in np.linspace(a.start, max(a.start, t1 - 0.05), a.frames):
        rgb = grab(a.input, float(t), gw, gh)
        if rgb is None:
            continue
        m = subject_mask(rgb)
        acc += m
        n += 1
        # head position: topmost row with any subject, and its horizontal centre
        ys, xs = np.nonzero(m)
        if len(ys):
            top = ys.min()
            band = xs[ys <= top + max(1, gh // 20)]
            if len(band):
                heads.append((float(top / gh), float(band.mean() / gw)))
    if not n:
        sys.exit("no frames analysed")
    occ = acc / n

    if heads:
        ht = np.array([h[0] for h in heads])
        hx = np.array([h[1] for h in heads])
        print(f"\n  headroom      {ht.min()*100:.1f}%-{ht.max()*100:.1f}% of height "
              f"(median {np.median(ht)*100:.1f}%)")
        print(f"  head centre x {hx.min()*100:.1f}%-{hx.max()*100:.1f}% of width "
              f"(median {np.median(hx)*100:.1f}%, drift {(hx.max()-hx.min())*100:.1f}%)")

    print(f"\n  {'region':<24}{'max':>7}{'mean':>8}   verdict")
    print(f"  {'-'*24}{'-'*7}{'-'*8}   {'-'*9}")
    results = {}
    probes = list(CANDIDATES)
    for p in a.probe:
        x, y, w, h = (float(v) for v in p.split(","))
        probes.append((f"probe {p:<18}"[:24], x, y, w, h))
    for name, x, y, w, h in probes:
        mx, mn = score_region(occ, x, y, w, h)
        print(f"  {name:<24}{mx:>7.3f}{mn:>8.3f}   {verdict(mx)}")
        results[name.strip()] = {"rect": [x, y, w, h], "max": round(mx, 4),
                                 "mean": round(mn, 4), "verdict": verdict(mx)}

    clear = [k for k, v in results.items() if v["verdict"] == "CLEAR"]
    marg = [k for k, v in results.items() if v["verdict"] == "MARGINAL"]
    print(f"\n  CLEAR    : {', '.join(clear) if clear else 'none'}")
    print(f"  MARGINAL : {', '.join(marg) if marg else 'none'}")
    print(f"\n  A region is CLEAR only if the subject never entered it in any sampled")
    print(f"  frame. MARGINAL means occasional collision — usable for a short overlay")
    print(f"  or one with a shadow, not for a persistent element.")

    # ---- largest genuinely clear rectangles, found rather than guessed
    print(f"\n  LARGEST CLEAR RECTANGLES (occupancy < {CLEAR})")
    for label, asp in (("free-form (max area) ", None),
                       ("16:9 content panel   ", 16 / 9),
                       ("9:16 portrait PIP    ", 9 / 16),
                       ("1:1 square           ", 1.0)):
        r = largest_clear_rect(occ, CLEAR, asp, px_w=W, px_h=H)
        print(f"    {label} {fmt_rect(r, W, H)}")
        results[f"largest_clear_{label.strip()}"] = (
            {"rect": [round(v, 4) for v in r]} if r else None)

    print(f"\n  LARGEST MARGINAL RECTANGLES (occupancy < {MARGINAL})")
    for label, asp in (("free-form (max area) ", None),
                       ("16:9 content panel   ", 16 / 9)):
        r = largest_clear_rect(occ, MARGINAL, asp, px_w=W, px_h=H)
        print(f"    {label} {fmt_rect(r, W, H)}")

    if a.heatmap:
        render_heatmap(occ, W // 2, H // 2, a.heatmap)
        print(f"\n  wrote {a.heatmap}")
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"source": a.input, "width": W, "height": H,
                       "duration": dur, "frames_sampled": n,
                       "grid": [gw, gh],
                       "occupancy": occ.round(4).tolist(),
                       "regions": results}, f, indent=2)
        print(f"  wrote {a.json}")
    print()


if __name__ == "__main__":
    main()
