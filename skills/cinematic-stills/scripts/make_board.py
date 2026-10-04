#!/usr/bin/env python3
"""Build an exact board/grid from approved stills: real pixels, no labels, no redrawing.

Use this (not a ChatGPT-drawn board) whenever a board goes INTO a video model and panel 1 must be the clip's exact
start frame, or for side-by-side checks (lookalike check, before/after, contact sheets for review).

usage: make_board.py --cols 2 --out board.png [--panel 720x1280] [--gap 8] [--gap-color white] [--fit cover|contain] img1 img2 ...
  --panel   size of every panel (default 720x1280 = 9:16). Images are fitted with a centre crop (cover) or letterbox (contain).
  Panels are filled left-to-right, top-to-bottom. Video models read a multi-panel board as a CUT LIST (one cut per panel
  boundary); a 2x2 grid labelled "moments inside one continuous shot" in the prompt adds no cuts.
"""
import argparse
from PIL import Image, ImageOps

ap = argparse.ArgumentParser()
ap.add_argument('images', nargs='+'); ap.add_argument('--cols', type=int, default=2); ap.add_argument('--out', required=True)
ap.add_argument('--panel', default='720x1280'); ap.add_argument('--gap', type=int, default=8)
ap.add_argument('--gap-color', default='white'); ap.add_argument('--fit', choices=['cover', 'contain'], default='cover')
a = ap.parse_args()
pw, ph = map(int, a.panel.lower().split('x'))
rows = (len(a.images) + a.cols - 1) // a.cols
W = a.cols * pw + (a.cols - 1) * a.gap; H = rows * ph + (rows - 1) * a.gap
board = Image.new('RGB', (W, H), a.gap_color)
for k, p in enumerate(a.images):
    im = Image.open(p).convert('RGB')
    im = ImageOps.fit(im, (pw, ph), Image.LANCZOS) if a.fit == 'cover' else ImageOps.pad(im, (pw, ph), Image.LANCZOS, color='black')
    board.paste(im, ((k % a.cols) * (pw + a.gap), (k // a.cols) * (ph + a.gap)))
board.save(a.out)
print(a.out, board.size, f'{len(a.images)} panels, {rows}x{a.cols}')
