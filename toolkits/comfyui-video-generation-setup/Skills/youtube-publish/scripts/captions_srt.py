#!/usr/bin/env python3
"""Serialise forced-aligned word timings to an SRT caption track.

    captions_srt.py --words edit/cache/words_*.json -o publish/captions.srt
    captions_srt.py --words W --timeline edit/renders/timeline.json -o C.srt

The pipeline already produces word-level timings for burned-in captions. Those
are on the OUTPUT timeline, which is the only timeline YouTube cares about, so
the same data serialises here for free.

Uploading a caption track is worth the two minutes: auto-captions mangle
technical vocabulary reliably (vmmap, int8, MPS, safetensors), and the uploaded
track is what YouTube's translation layer reads. Burned-in captions do not do
this job — YouTube cannot read pixels.
"""

import argparse
import glob
import json
import os
import sys

# Caption lines people can actually read: roughly one breath, two lines.
MAX_CHARS = 84
MAX_SECONDS = 6.0
MAX_GAP = 0.7          # a pause longer than this ends the cue
MIN_DURATION = 0.9     # a cue shorter than this flashes


def ts(seconds):
    if seconds < 0:
        seconds = 0.0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def load_words(pattern):
    paths = sorted(glob.glob(os.path.expanduser(pattern)))
    if not paths:
        sys.exit(f"error: no transcript matched {pattern!r}")
    if len(paths) > 1:
        print(f"  note: {len(paths)} matched, using {os.path.basename(paths[-1])}",
              file=sys.stderr)
    with open(paths[-1]) as fh:
        data = json.load(fh)
    words = data.get("words") or data
    if not isinstance(words, list) or not words:
        sys.exit(f"error: {paths[-1]} has no word list")
    out = []
    for w in words:
        text = (w.get("word") or w.get("text") or "").strip()
        if not text:
            continue
        out.append({"text": text, "start": float(w["start"]), "end": float(w["end"])})
    return out


def group(words):
    """Break on pauses and sentence ends before length, so cues land on the
    phrasing rather than on a character count."""
    cues, cur = [], []
    for w in words:
        if cur:
            gap = w["start"] - cur[-1]["end"]
            span = w["end"] - cur[0]["start"]
            width = len(" ".join(x["text"] for x in cur)) + 1 + len(w["text"])
            ends_sentence = cur[-1]["text"][-1:] in ".?!"
            if gap > MAX_GAP or span > MAX_SECONDS or width > MAX_CHARS or ends_sentence:
                cues.append(cur)
                cur = []
        cur.append(w)
    if cur:
        cues.append(cur)
    return cues


def wrap(text):
    """Two balanced lines, because one long line gets clipped on mobile."""
    if len(text) <= 42:
        return text
    words = text.split()
    best, target = None, len(text) / 2
    for i in range(1, len(words)):
        a = " ".join(words[:i])
        if best is None or abs(len(a) - target) < abs(len(best) - target):
            best = a
    return best + "\n" + text[len(best):].strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--words", required=True, help="aligned word-timings JSON (glob ok)")
    ap.add_argument("--timeline", help="renders/timeline.json, to validate the span")
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()

    words = load_words(args.words)

    # whisper.cpp word mode emits no punctuation or casing, so cue breaks fall
    # back to pauses alone and the track reads as one long run-on. These are
    # scripted videos, so the punctuation exists in the script — align the
    # transcript to it first (retake-dedup/scripts/align_retakes.py) and feed
    # the aligned words in here.
    punctuated = sum(1 for w in words if w["text"][-1:] in ".,?!")
    if punctuated == 0:
        print(f"warning: none of {len(words)} words carry punctuation, so cues "
              f"break on pauses only and the captions will read as run-on text.\n"
              f"  these are scripted videos — align the transcript to the script "
              f"first and pass the aligned words instead.", file=sys.stderr)

    cues = group(words)

    if args.timeline and os.path.exists(args.timeline):
        with open(args.timeline) as fh:
            tl = json.load(fh)
        dur = tl.get("duration") or sum(
            seg.get("duration", 0) for seg in tl.get("segments", []))
        if dur:
            last = words[-1]["end"]
            if last > dur + 0.5:
                print(f"warning: captions run to {last:.1f}s but the render is "
                      f"{dur:.1f}s. The words are on the wrong timeline — remap "
                      f"them with remap_words.py --timeline first.", file=sys.stderr)

    lines = []
    for i, cue in enumerate(cues, 1):
        start = cue[0]["start"]
        end = max(cue[-1]["end"], start + MIN_DURATION)
        if i < len(cues):
            end = min(end, cues[i][0]["start"] - 0.02)
        text = wrap(" ".join(w["text"] for w in cue))
        lines.append(f"{i}\n{ts(start)} --> {ts(end)}\n{text}\n")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        fh.write("\n".join(lines))

    total = words[-1]["end"] - words[0]["start"]
    print(f"  {args.out}")
    print(f"  {len(cues)} cues from {len(words)} words over {total:.1f}s")


if __name__ == "__main__":
    main()
