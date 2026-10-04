#!/usr/bin/env python3
"""Numbered contact sheet of harvested Pinterest pins, for picking by eye.

usage: contact_sheet.py <group_dir>
  <group_dir>/list.txt holds lines "<pinId> <pinimg path> [alt text]" from pinterest_harvest.js.
  Writes <group_dir>/NN_<pinId>.jpg (236 px thumbs) and <group_dir>/../sheet_<group>.jpg (8 columns, yellow index numbers).
Run with a Python that has Pillow
"""
import pathlib, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

d = pathlib.Path(sys.argv[1]).expanduser().resolve()
lines = [l.split(maxsplit=2) for l in (d / 'list.txt').read_text().splitlines() if l.strip() and not l.strip().endswith(' pins')]
thumbs = []
for i, parts in enumerate(lines):
    pid, path = parts[0], parts[1]
    f = d / f'{i:02d}_{pid}.jpg'
    if not f.exists():
        subprocess.run(['curl', '-s', '-o', str(f), 'https://i.pinimg.com/236x/' + path])
    try:
        im = Image.open(f).convert('RGB')
    except Exception:
        continue
    im.thumbnail((236, 330))
    thumbs.append((i, im))
cols, W, H = 8, 240, 334
rows = (len(thumbs) + cols - 1) // cols
sheet = Image.new('RGB', (cols * W, max(rows, 1) * H), 'white')
dr = ImageDraw.Draw(sheet)
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 28)
for k, (i, im) in enumerate(thumbs):
    x, y = (k % cols) * W, (k // cols) * H
    sheet.paste(im, (x, y))
    dr.rectangle([x, y, x + 44, y + 34], fill='black')
    dr.text((x + 4, y + 2), str(i), fill='yellow', font=font)
out = d.parent / f'sheet_{d.name}.jpg'
sheet.save(out, quality=82)
print(len(thumbs), 'thumbs ->', out)
