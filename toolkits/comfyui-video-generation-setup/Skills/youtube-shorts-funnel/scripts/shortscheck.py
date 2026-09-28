#!/usr/bin/env python3
"""Lint a YouTube Shorts script for pacing, spec compliance, and funnel health.

Usage:
    python3 shortscheck.py <script.md> [--wps 2.6]

Shorts are spoken faster than long-form (~2.4-2.8 words/sec vs ~2.5 for
long-form's 150wpm). Pacing errors are the most common problem in a written
Shorts script: lines that read fine on the page take four seconds to say and
blow the beat budget.

The funnel checks are the important ones. A Short that passes every retention
check and has no bridge has failed at its only job.

Exit code is always 0: advice, not a gate.
"""

import argparse
import re
import sys

BANNED_CTA = [
    "subscribe", "hit the bell", "like and share", "smash that",
    "don't forget to like", "dont forget to like",
]

WEAK_BRIDGE = [
    "check out my channel", "link in bio", "more on my channel",
    "full video on my channel", "watch the full video", "learn more",
    "check the description",
]

# Phrases that indicate the bridge names a SPECIFIC gap rather than gesturing
# vaguely at "more". Deliberately broad: a false pass is cheaper than nagging
# about a bridge that is already doing its job.
STRONG_BRIDGE_SIGNALS = [
    "the other", "i show", "including", "with timestamps", "not in this",
    "full breakdown", "the rest", "the exact", "where that", "how they",
    "how i", "the failures", "the one that", "what i changed", "and what",
    "all eight", "all five", "all six", "all seven",
]

BANNED_OPENERS = [
    "hey guys", "hi guys", "what's up", "whats up", "welcome back",
    "in this video", "before we", "let me tell you",
]

LOOP_WORDS = ["loop", "loops back", "match the opening", "matches the first"]
CLICK_WORDS = ["click", "bridge", "callout", "pinned comment", "end frame"]


def spoken_lines(lines):
    """Extract spoken content: table SPOKEN column, or blockquotes."""
    out = []
    for i, raw in enumerate(lines, 1):
        s = raw.strip()
        if s.startswith("|") and s.count("|") >= 3:
            cells = [c.strip() for c in s.split("|")[1:-1]]
            if len(cells) >= 2 and cells[1] and not set(cells[1]) <= set("-: "):
                low = cells[1].lower()
                if low not in ("spoken", "spoken audio", "audio"):
                    out.append((i, cells[1]))
        elif s.startswith(">"):
            t = s.lstrip("> ").strip()
            if t:
                out.append((i, t))
    return out


def find(lines, terms):
    hits = {}
    for lineno, text in lines:
        low = text.lower()
        for t in terms:
            if t in low:
                hits.setdefault(t, []).append(lineno)
    return hits


def show(label, hits, advice=""):
    if not hits:
        print(f"  OK  {label}")
        return 0
    n = sum(len(v) for v in hits.values())
    print(f"  !!  {label} ({n})")
    if advice:
        print(f"      {advice}")
    for t, ls in sorted(hits.items(), key=lambda kv: -len(kv[1])):
        print(f"      '{t}' -> {', '.join(f'L{x}' for x in ls[:5])}")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--wps", type=float, default=2.6,
                    help="spoken words per second (default 2.6)")
    args = ap.parse_args()

    try:
        with open(args.script, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError as e:
        print(f"could not read {args.script}: {e}", file=sys.stderr)
        return 1

    src = "".join(lines)
    low_src = src.lower()
    spoken = spoken_lines(lines)

    print(f"\n=== shortscheck: {args.script} ===")
    if not spoken:
        print("no spoken lines found (expected a SPOKEN table column or blockquotes)\n")
        return 0

    words = sum(len(t.split()) for _, t in spoken)
    secs = words / args.wps
    print(f"scope: {len(spoken)} spoken lines, {words} words\n")

    print("PACING")
    print(f"  ~{secs:.0f}s of speech at {args.wps} words/sec")
    if secs > 60:
        print("  !!  over 60s: retention gate drops to ~40-45%. Cut, or accept lower reach.")
    elif secs < 15:
        print("  !!  under 15s: may not clear absolute watch-time even at full retention")
    elif 30 <= secs <= 45:
        print("  OK  inside the 30-45s working default")
    else:
        print("  OK  workable, 30-45s is the safer target")

    # The hook line: first spoken line must be sayable in ~1.5s
    hook_no, hook = spoken[0]
    hw = len(hook.split())
    ht = hw / args.wps
    print(f"\nHOOK (L{hook_no})")
    print(f"  \"{hook[:70]}{'...' if len(hook) > 70 else ''}\"")
    if ht > 2.0:
        print(f"  !!  ~{ht:.1f}s to say ({hw} words). Target under 1.5s. Cut it down.")
    else:
        print(f"  OK  ~{ht:.1f}s to say ({hw} words)")
    show("banned openers", find([(hook_no, hook)], BANNED_OPENERS),
         "the hook starts on frame 1; no greeting, no framing")

    print("\nFUNNEL")
    banned = show("subscribe-style CTA", find(spoken, BANNED_CTA),
                  "for a watch-hours goal the click is worth more than the sub")
    weak = show("vague bridge language", find(spoken, WEAK_BRIDGE),
                "name the destination AND the specific thing not in this Short")
    strong = find(spoken, STRONG_BRIDGE_SIGNALS)
    if strong:
        print(f"  OK  specific-bridge language present ({sum(len(v) for v in strong.values())} signals)")
    else:
        print("  !!  no specific-bridge language found")
        print("      a bridge needs a named gap ('the other five', 'including the run where it fails')")

    has_pin = "pinned comment" in low_src
    print(f"  {'OK ' if has_pin else '!! '} pinned comment {'present' if has_pin else 'MISSING - highest-intent surface, costs nothing'}")
    has_end = "end frame" in low_src or "end card" in low_src
    print(f"  {'OK ' if has_end else '!! '} end frame {'present' if has_end else 'not specified'}")
    has_dest = "destination:" in low_src
    print(f"  {'OK ' if has_dest else '!! '} destination {'named' if has_dest else 'NOT NAMED - write this before the script'}")

    print("\nLOOP vs CLICK")
    loop_hit = any(w in low_src for w in LOOP_WORDS)
    click_hit = any(w in low_src for w in CLICK_WORDS)
    declared = "loop or click:" in low_src
    if declared:
        print("  OK  choice is declared in the script header")
    elif loop_hit and click_hit:
        print("  !!  both loop and bridge language present, no declared choice")
        print("      these compete for the same final seconds. Pick one and say which.")
    elif loop_hit:
        print("  !!  loop designed, no bridge detected")
        print("      a loop without a bridge earns reach and sends nobody")
    else:
        print("  OK  no loop/click conflict detected")

    print("\nSPEC")
    for key, label in (("9:16", "aspect ratio"), ("safe zone", "caption safe zone"),
                       ("on-screen text", "on-screen text")):
        print(f"  {'OK ' if key in low_src else '?  '} {label} {'noted' if key in low_src else 'not mentioned'}")

    dashes = sum(1 for _, t in spoken if "—" in t or "–" in t)
    print(f"  {'!! ' if dashes else 'OK '} em/en dashes in spoken lines: {dashes}"
          + ("  (use '..' for a pause)" if dashes else ""))

    print("\nSUMMARY")
    issues = banned + weak + (0 if strong else 1) + (0 if has_pin else 1) + dashes
    print(f"  {issues} items to review" if issues else "  clean")
    print("  the funnel checks matter most: views without clicks is a failed Short.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
