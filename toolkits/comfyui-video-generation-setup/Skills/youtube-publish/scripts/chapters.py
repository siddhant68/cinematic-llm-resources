#!/usr/bin/env python3
"""Turn a long-form script's sections into real, validated YouTube chapters.

    chapters.py --script EP.md --transcript words.json -o chapters.txt
    chapters.py --script EP.md --timeline renders/timeline.json -o chapters.txt
    chapters.py --script EP.md --planned            # planned times, for review only

A `youtube-longform-script` file already contains the section structure — IDs,
titles and planned run times, plus the spoken VO under each heading. That is the
segmentation, done deliberately, with open loops planted and closed across
specific sections. Do not re-segment it.

What the script does NOT contain is when those sections actually happen. Its
`0:00-1:00` is an intention; the render is what exists. So the timestamps come
from the video:

  --transcript   align each section's first spoken line to the ASR transcript.
                 Works for any video, including ones this pipeline didn't cut.
  --timeline     use renders/timeline.json, when the pipeline did cut it.
  --planned      the script's own times. Never publish these.

YouTube fails chapters silently — one bad timestamp and the whole block renders
as plain text, with no error anywhere. Everything here is validated before it is
written.
"""

import argparse
import glob
import json
import os
import re
import sys

MIN_CHAPTER = 10.0        # seconds; YouTube's floor
MIN_CHAPTERS = 3
ANCHOR_WORDS = 9          # words of a section's first VO line used to locate it


# ------------------------------------------------------------------ parsing

def parse_script(path):
    """Sections from a youtube-longform-script file: id, title, planned span,
    and the first spoken line, which is the anchor used to locate the section."""
    with open(path) as fh:
        text = fh.read()

    # ### S1 — Cold open: the render that lied
    heads = list(re.finditer(r"^###\s+(S\d+[a-z]?)\s*[—–-]\s*(.+?)\s*$", text, re.M))
    if not heads:
        sys.exit(f"error: no '### S<n> — Title' section headings in {path}.\n"
                 f"  Is this a youtube-longform-script output?")

    sections = []
    for i, h in enumerate(heads):
        body = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        planned = re.search(r"`(\d+:\d{2})\s*-\s*(\d+:\d{2})`", body)
        vo = re.findall(r"^>\s*(.+?)\s*$", body, re.M)
        spoken = [v for v in vo if not v.startswith("*(")]
        sections.append({
            "id": h.group(1),
            "title": re.sub(r"\*\*|`", "", h.group(2)).strip(),
            "planned_start": to_seconds(planned.group(1)) if planned else None,
            "planned_end": to_seconds(planned.group(2)) if planned else None,
            "anchor": spoken[0] if spoken else None,
        })
    return sections


def to_seconds(stamp):
    parts = [int(p) for p in stamp.split(":")]
    return parts[0] * 60 + parts[1] if len(parts) == 2 else \
        parts[0] * 3600 + parts[1] * 60 + parts[2]


def stamp(sec):
    sec = max(0, int(sec))
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).split()


# ---------------------------------------------------------------- alignment

def load_words(pattern):
    paths = sorted(glob.glob(os.path.expanduser(pattern)))
    if not paths:
        sys.exit(f"error: no transcript matched {pattern!r}")
    data = json.load(open(paths[-1]))
    words = data.get("words") or data
    return [{"w": (x.get("word") or x.get("text") or "").strip(),
             "t": float(x["start"])} for x in words if (x.get("word") or x.get("text"))]


def align(sections, words):
    """Locate each section's first spoken line in the transcript.

    Speech runs forward through the script, so each search starts after the
    previous section's hit. That monotonic constraint is what stops a repeated
    phrase from matching the wrong occurrence."""
    toks = [norm(w["w"])[0] if norm(w["w"]) else "" for w in words]
    cursor, out = 0, []

    for sec in sections:
        if not sec["anchor"]:
            out.append((sec, None, "no spoken line in this section"))
            continue
        anchor = norm(sec["anchor"])[:ANCHOR_WORDS]
        if len(anchor) < 3:
            out.append((sec, None, "anchor too short to match"))
            continue

        best, best_score = None, 0.0
        for i in range(cursor, max(cursor, len(toks) - len(anchor)) + 1):
            window = toks[i:i + len(anchor)]
            if not window:
                break
            hits = sum(1 for a, b in zip(anchor, window) if a == b)
            score = hits / len(anchor)
            if score > best_score:
                best, best_score = i, score
                if score == 1.0:
                    break

        if best is None or best_score < 0.5:
            out.append((sec, None,
                        f"could not locate {sec['anchor'][:40]!r} (best {best_score:.0%})"))
            continue
        out.append((sec, words[best]["t"], f"matched {best_score:.0%}"))
        cursor = best + 1
    return out


def from_timeline(sections, timeline_path):
    tl = json.load(open(timeline_path))
    segs = tl.get("segments") or []
    if not segs:
        sys.exit(f"error: {timeline_path} has no segments")
    by_id, t = {}, 0.0
    for s in segs:
        sid = s.get("section") or s.get("id")
        if sid and sid not in by_id:
            by_id[sid] = t
        t += float(s.get("duration", 0))
    return [(sec, by_id.get(sec["id"]),
             "from timeline" if sec["id"] in by_id else "no segment with this id")
            for sec in sections]


# --------------------------------------------------------------- validation

def validate(rows, duration=None):
    """The five rules. All of them, or YouTube ignores the whole block."""
    fails, warns = [], []
    placed = [(s, t) for s, t, _ in rows if t is not None]

    if len(placed) < MIN_CHAPTERS:
        fails.append(f"{len(placed)} chapters located; YouTube needs at least "
                     f"{MIN_CHAPTERS}")
    if placed and placed[0][1] > 0.5:
        fails.append(f"first chapter is at {stamp(placed[0][1])}; it must be 0:00. "
                     f"Force it with --force-zero, or check the alignment.")
    times = [t for _, t in placed]
    if times != sorted(times):
        fails.append("chapters are not in ascending order — alignment picked the "
                     "wrong occurrence somewhere")
    for i in range(len(placed) - 1):
        gap = placed[i + 1][1] - placed[i][1]
        if gap < MIN_CHAPTER:
            fails.append(
                f"{placed[i][0]['id']} → {placed[i+1][0]['id']} is {gap:.0f}s, "
                f"under the {MIN_CHAPTER:.0f}s minimum. Drop one of them from the "
                f"chapter list, or merge them under a single title — the section "
                f"structure stays as it is, only the chapters change.")
    if duration and times and times[-1] > duration:
        fails.append(f"last chapter {stamp(times[-1])} is past the end "
                     f"({stamp(duration)})")

    missing = [s["id"] for s, t, _ in rows if t is None]
    if missing:
        warns.append(f"not located, and left out: {', '.join(missing)}")
    return fails, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--script", required=True)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--transcript", help="aligned word timings JSON (glob ok)")
    src.add_argument("--timeline", help="renders/timeline.json")
    src.add_argument("--planned", action="store_true",
                     help="the script's own times — for review, never for publishing")
    ap.add_argument("--duration", type=float, help="video length, for bounds checking")
    ap.add_argument("--force-zero", action="store_true",
                    help="pin the first located chapter to 0:00")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()

    sections = parse_script(args.script)
    print(f"  {len(sections)} sections in {os.path.basename(args.script)}",
          file=sys.stderr)

    if args.transcript:
        rows = align(sections, load_words(args.transcript))
    elif args.timeline:
        rows = from_timeline(sections, args.timeline)
    else:
        rows = [(s, s["planned_start"], "planned") for s in sections]
        print("  WARNING: planned times. These are an intention, not the render — "
              "do not publish them.", file=sys.stderr)

    if args.force_zero:
        rows = [(s, (0.0 if i == 0 else t), n) for i, (s, t, n) in enumerate(rows)]

    for s, t, note in rows:
        mark = stamp(t) if t is not None else "  --  "
        print(f"    {s['id']:4s} {mark:>8s}  {s['title'][:52]:54s} {note}",
              file=sys.stderr)

    fails, warns = validate(rows, args.duration)
    for w in warns:
        print(f"  warn  {w}", file=sys.stderr)
    for f in fails:
        print(f"  FAIL  {f}", file=sys.stderr)
    if fails:
        print("\n  chapters not written — YouTube would have silently ignored them.\n",
              file=sys.stderr)
        return 1

    lines = [f"{stamp(t)} {s['title']}" for s, t, _ in rows if t is not None]
    block = "\n".join(lines)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
        with open(args.out, "w") as fh:
            fh.write(block + "\n")
        print(f"\n  wrote {args.out} ({len(lines)} chapters)", file=sys.stderr)
        print("  Titles are the script's section headings. Rewrite them to name what "
              "a viewer gets by jumping there.", file=sys.stderr)
    else:
        print(block)
    return 0


if __name__ == "__main__":
    sys.exit(main())
