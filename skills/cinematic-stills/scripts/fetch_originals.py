#!/usr/bin/env python3
"""Download the full-size originals of the pins you picked, show them side by side, and log them in sources.json.

usage: fetch_originals.py <group_dir> <slot_prefix> <idx> [<idx> ...] [--query "the search query"]
  e.g. fetch_originals.py work/pinterest/room r 3 7 12 --query "stone chamber oil lamp night film still"
  Writes <group_dir>/orig_NN_<pinId>.jpg, a strip <group_dir>/../orig_<group>.jpg, and appends entries to
  <group_dir>/../sources.json: {slot, pin, orig, query, file, why:""}. Fill in "why" yourself (what each pin is FOR).
"""
import json, pathlib, subprocess, sys
from PIL import Image

args = sys.argv[1:]
query = ''
if '--query' in args:
    q = args.index('--query'); query = args[q + 1]; args = args[:q] + args[q + 2:]
d = pathlib.Path(args[0]).expanduser().resolve(); prefix = args[1]; idx = [int(x) for x in args[2:]]
lines = [l.split(maxsplit=2) for l in (d / 'list.txt').read_text().splitlines() if l.strip() and not l.strip().endswith(' pins')]
src_file = d.parent / 'sources.json'
sources = json.loads(src_file.read_text()) if src_file.exists() else []
strip = []
for n, i in enumerate(idx, 1):
    pid, path = lines[i][0], lines[i][1]
    f = d / f'orig_{i:02d}_{pid}.jpg'
    im, used = None, None
    for base in ('originals', '736x'):
        url = f'https://i.pinimg.com/{base}/' + path
        subprocess.run(['curl', '-s', '-o', str(f), url])
        try:
            im = Image.open(f); im.load(); used = url; break
        except Exception:
            im = None
    if im is None:
        print(i, 'FAILED'); continue
    print(i, pid, im.size, f.stat().st_size // 1024, 'KB')
    sources.append({'slot': f'{prefix}{n}', 'pin': f'https://www.pinterest.com/pin/{pid}/', 'orig': used,
                    'query': query, 'file': str(f.relative_to(d.parent)), 'why': ''})
    im = im.convert('RGB'); im.thumbnail((10000, 700)); strip.append(im)
if strip:
    S = Image.new('RGB', (sum(i.width for i in strip), 700), 'white'); x = 0
    for im in strip: S.paste(im, (x, 0)); x += im.width
    S.save(d.parent / f'orig_{d.name}.jpg', quality=85)
src_file.write_text(json.dumps(sources, indent=1, ensure_ascii=False))
print('logged', len(strip), 'in', src_file)
