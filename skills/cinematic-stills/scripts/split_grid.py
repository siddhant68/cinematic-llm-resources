#!/usr/bin/env python3
"""Cut a generated grid / angle sheet / storyboard into its panels.

usage: split_grid.py sheet.png --rows 2 --cols 3 --out-dir panels/ [--crop916]
  Finds the gutters (uniform light or dark lines between panels) by scanning row/column profiles; falls back to an equal
  split if none are found. --crop916 also centre-crops each panel to 9:16 for use as a video start frame.
  ALWAYS look at the panels afterwards: wide panels in a grid lose face detail; if a panel will be a
  start frame, prefer regenerating that angle as its own full-size still (Stage 4) over upscaling a grid cell.
"""
import argparse, pathlib
from PIL import Image, ImageStat

ap = argparse.ArgumentParser()
ap.add_argument('image'); ap.add_argument('--rows', type=int, required=True); ap.add_argument('--cols', type=int, required=True)
ap.add_argument('--out-dir', required=True); ap.add_argument('--crop916', action='store_true')
a = ap.parse_args()
im = Image.open(a.image).convert('RGB'); W, H = im.size
g = im.convert('L')

def bands(length, n, line_stats):
    """Return n (start, end) spans. A gutter line has very low variance and is near-white or near-black."""
    flat = [i for i, (mean, std) in enumerate(line_stats) if std < 6 and (mean > 235 or mean < 20)]
    runs, cur = [], []
    for i in flat:
        if cur and i != cur[-1] + 1:
            runs.append(cur); cur = []
        cur.append(i)
    if cur: runs.append(cur)
    inner = [r for r in runs if 0 < r[0] and r[-1] < length - 1]
    step = length / n
    cuts = []
    for k in range(1, n):  # pick the gutter run nearest each expected boundary
        target = k * step
        near = [r for r in inner if abs((r[0] + r[-1]) / 2 - target) < step * 0.25]
        cuts.append(min(near, key=lambda r: abs((r[0] + r[-1]) / 2 - target)) if near else [int(target), int(target)])
    edges = [0] + [c for r in cuts for c in (r[0], r[-1] + 1)] + [length]
    return [(edges[2 * i], edges[2 * i + 1]) for i in range(n)]

col_stats = [(ImageStat.Stat(g.crop((x, 0, x + 1, H))).mean[0], ImageStat.Stat(g.crop((x, 0, x + 1, H))).stddev[0]) for x in range(W)]
row_stats = [(ImageStat.Stat(g.crop((0, y, W, y + 1))).mean[0], ImageStat.Stat(g.crop((0, y, W, y + 1))).stddev[0]) for y in range(H)]
xs, ys = bands(W, a.cols, col_stats), bands(H, a.rows, row_stats)
out = pathlib.Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
n = 0
for r, (y0, y1) in enumerate(ys):
    for c, (x0, x1) in enumerate(xs):
        n += 1
        p = im.crop((x0, y0, x1, y1))
        if a.crop916:
            w, h = p.size; tw = int(h * 9 / 16)
            p = p.crop(((w - tw) // 2, 0, (w - tw) // 2 + tw, h)) if tw <= w else p.crop((0, (h - int(w * 16 / 9)) // 2, w, (h - int(w * 16 / 9)) // 2 + int(w * 16 / 9)))
        f = out / f'panel_{n:02d}.png'; p.save(f); print(f, p.size)
