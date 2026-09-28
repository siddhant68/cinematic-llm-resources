#!/usr/bin/env python3
"""
analyze_key.py — Measure a green screen before keying it, and recommend a strategy.

Keying failures are almost always decided before you type a filter: the screen is
unevenly lit, or too desaturated to separate from skin tones. This measures both
and tells you which of three approaches will actually work.

Usage:
  python analyze_key.py footage.mp4                 # samples 12 frames
  python analyze_key.py footage.mp4 --frames 24
  python analyze_key.py frame.png                   # single still
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

LUMA = np.array([0.299, 0.587, 0.114])


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def extract_frames(path, n, tmpdir):
    dur = probe_duration(path)
    if dur is None:
        return [path]
    frames = []
    for i in range(n):
        t = dur * (i + 0.5) / n
        out = os.path.join(tmpdir, f"f{i:03d}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", path,
                        "-frames:v", "1", "-y", out], check=False)
        if os.path.exists(out):
            frames.append(out)
    return frames


def edge_regions(a, margin_frac=0.14):
    """Sample left/right vertical strips and the top band — where the subject isn't."""
    h, w, _ = a.shape
    m = max(8, int(w * margin_frac))
    top = max(8, int(h * 0.10))
    return [a[:, :m], a[:, w - m:], a[:top, :]]


def analyse(paths):
    seps, sats, hues, lumas = [], [], [], []
    band_means = []
    for p in paths:
        a = np.asarray(Image.open(p).convert("RGB"), dtype=float)
        strips = edge_regions(a)
        px = np.vstack([s.reshape(-1, 3) for s in strips])

        R, G, B = px[:, 0], px[:, 1], px[:, 2]
        seps.append(G - np.maximum(R, B))

        mx, mn = px.max(1), px.min(1)
        d = mx - mn
        sats.append(np.where(mx > 0, d / np.maximum(mx, 1), 0))
        lumas.append(px @ LUMA)

        nz = d > 0
        if nz.any():
            r_, g_, b_, mxn, dn = R[nz], G[nz], B[nz], mx[nz], d[nz]
            h = np.where(mxn == g_, 60 * (2 + (b_ - r_) / dn),
                np.where(mxn == r_, 60 * (((g_ - b_) / dn) % 6),
                                    60 * (4 + (r_ - g_) / dn)))
            hues.append(h % 360)

        # vertical falloff on this frame
        hh = a.shape[0]
        lum = a @ LUMA
        m = max(8, int(a.shape[1] * 0.14))
        cols = np.hstack([lum[:, :m], lum[:, -m:]])
        band_means.append([cols[int(hh * i / 4):int(hh * (i + 1) / 4)].mean()
                           for i in range(4)])

    sep = np.concatenate(seps)
    sat = np.concatenate(sats)
    hue = np.concatenate(hues) if hues else np.array([0.0])
    lum = np.concatenate(lumas)
    bands = np.array(band_means).mean(0)

    return {
        "frames": len(paths),
        "chroma_separation_mean": float(sep.mean()),
        "chroma_separation_p5": float(np.percentile(sep, 5)),
        "saturation_mean": float(sat.mean()),
        "hue_mean_deg": float(hue.mean()),
        "hue_std_deg": float(hue.std()),
        "luma_mean": float(lum.mean()),
        "luma_std": float(lum.std()),
        "vertical_falloff": float(bands[0] - bands[-1]),
        "band_means": [float(b) for b in bands],
    }


def verdict(m):
    sep, sat = m["chroma_separation_mean"], m["saturation_mean"]
    fall, hstd = abs(m["vertical_falloff"]), m["hue_std_deg"]

    notes, score = [], 0
    if sep >= 90:
        notes.append(f"chroma separation {sep:.0f} — strong"); score += 2
    elif sep >= 60:
        notes.append(f"chroma separation {sep:.0f} — workable"); score += 1
    else:
        notes.append(f"chroma separation {sep:.0f} — WEAK (want 90+). "
                     "Screen is underlit or the camera is desaturating it.")

    if sat >= 0.65:
        notes.append(f"saturation {sat:.2f} — good"); score += 2
    elif sat >= 0.45:
        notes.append(f"saturation {sat:.2f} — marginal"); score += 1
    else:
        notes.append(f"saturation {sat:.2f} — WEAK (want 0.7+). "
                     "Green is washed toward grey; it will fight skin tones.")

    if fall <= 12:
        notes.append(f"vertical falloff {fall:.0f} — evenly lit"); score += 2
    elif fall <= 30:
        notes.append(f"vertical falloff {fall:.0f} — uneven, flatten first"); score += 1
    else:
        notes.append(f"vertical falloff {fall:.0f} luma levels — VERY uneven. "
                     "A single similarity value cannot cover top and bottom.")

    if hstd <= 10:
        notes.append(f"hue spread ±{hstd:.0f}° — consistent"); score += 1
    else:
        notes.append(f"hue spread ±{hstd:.0f}° — inconsistent")

    if score >= 6:
        strat = ("DIRECT KEY. chromakey with despill will hold. "
                 "Start similarity 0.12, blend 0.06.")
    elif score >= 3:
        strat = ("FLATTEN THEN KEY. Normalise the background illumination first "
                 "(see SKILL.md 'Flatten pass'), then key. Expect similarity "
                 "0.18-0.26 after flattening.")
    else:
        strat = ("USE AI MATTING, NOT CHROMA KEY. The screen does not separate "
                 "well enough for a clean edge. A learned matte (MatAnyone / RVM) "
                 "ignores the screen entirely and will beat any chromakey tuning "
                 "you do here. Key only as a fallback.")

    # crude starting params scaled by how bad the screen is
    sim = 0.12 if sep >= 90 else (0.20 if sep >= 60 else 0.30)
    blend = 0.06 if fall <= 12 else (0.12 if fall <= 30 else 0.20)
    return notes, strat, sim, blend


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--frames", type=int, default=12)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as td:
        if args.input.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            paths = [args.input]
        else:
            paths = extract_frames(args.input, args.frames, td)
        if not paths:
            sys.exit("Could not extract frames.")
        m = analyse(paths)

    notes, strat, sim, blend = verdict(m)

    if args.json:
        print(json.dumps({**m, "strategy": strat,
                          "suggested_similarity": sim,
                          "suggested_blend": blend}, indent=2))
        return

    print(f"Sampled {m['frames']} frame(s), edge regions only.\n")
    for n in notes:
        print(f"  - {n}")
    print(f"\n  luma across screen: mean {m['luma_mean']:.0f}, "
          f"std {m['luma_std']:.1f}")
    print(f"  top->bottom bands : "
          f"{' '.join(f'{b:.0f}' for b in m['band_means'])}")
    print(f"\nSTRATEGY: {strat}")
    print(f"\nStarting point if you key:")
    print(f"  chromakey=0x00FF00:{sim}:{blend},despill=type=green:mix=0.5")
    print(f"  Tune similarity in 0.02 steps. Check hair and shoulders, not the "
          f"middle of the frame.")


if __name__ == "__main__":
    main()
