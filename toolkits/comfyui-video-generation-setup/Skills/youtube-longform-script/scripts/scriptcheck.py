#!/usr/bin/env python3
"""Lint a long-form video script for cadence, repetition, structure and voice.

Usage:
    python3 scriptcheck.py <script.md> [--wpm 150] [--cadence]

Checks:
  * runtime, from the spoken word count
  * cadence   - beat-length distribution (the teleprompter tell)
  * repetition - antithesis density, re-listed sets, section-opener sameness
  * structure  - every row of the structure table has a written section
  * voice      - AI-tell vocabulary, dashes, banned openers and closers
  * shorts     - Short seeds are well formed, and no legacy lift markers remain

VO extraction handles the format this skill actually emits: a `[VO]` marker on
its own line, followed by plain spoken lines until the next marker or heading.
Blockquoted VO is also accepted. If extraction finds implausibly little text the
report says so loudly, because a clean report on an unparsed script is worse
than no report.

Exit code is 0 always: this is advice, not a gate. A flagged word that is
genuinely the right word should stay.
"""

import argparse
import re
import statistics
import sys
from collections import defaultdict, Counter

# Words rare in speech, common in generated text. Grouped for a readable report.
AI_TELLS = {
    "verbs": ["leverage", "leveraging", "utilize", "utilizing", "facilitate",
              "streamline", "streamlining", "harness", "harnessing", "foster",
              "cultivate", "delve", "empower", "elevate"],
    "adverbs": ["fundamentally", "essentially", "ultimately", "crucially",
                "notably", "arguably"],
    "nouns": ["landscape", "ecosystem", "paradigm", "realm", "tapestry",
              "game-changer", "gamechanger", "treasure trove"],
    "adjectives": ["robust", "seamless", "cutting-edge", "comprehensive"],
}

PHRASE_TELLS = [
    "in today's fast-paced world", "at the end of the day", "deep dive",
    "let's dive in", "lets dive in", "without further ado", "needle-mover",
    "when it comes to", "the world of", "it's not just", "it is not just",
]

BANNED_OPENERS = [
    "hey guys", "hi guys", "what's up guys", "whats up guys",
    "welcome back", "before we get started", "before we begin",
    "in this video, we will", "in this video we will", "in this video, i will",
]

BANNED_CLOSERS = [
    "thanks for watching", "thank you for watching", "in conclusion",
    "that's all for today", "thats all for today", "don't forget to like",
    "dont forget to like", "smash that like", "like and subscribe",
]

# Openers that recap instead of arriving. Connection is fine; recap is not.
THROAT_CLEARING = [
    "so as we saw", "as we saw", "now that we understand", "now that we know",
    "as i mentioned", "like i said", "as discussed", "to recap",
    "as i explained", "remember when i said",
]

# The antithesis construction: a negated identity near the head of the sentence,
# usually followed by the real answer. Strong once, a tic by the fifth use.
ANTITHESIS = re.compile(
    r"^[^.?!]{0,45}\b("
    r"isn'?t|is not|aren'?t|are not|wasn'?t|were not|"
    r"doesn'?t|does not|don'?t|do not|didn'?t|"
    r"can'?t|cannot|won'?t|will not|"
    r"not only|not just|never"
    r")\b", re.I)

CADENCE = {
    "median_lo": 12, "median_hi": 18,
    "short_share_max": 0.35,   # share of beats under 8 words
    "long_share_min": 0.15,    # share of beats over 20 words
}

MARKER = re.compile(r"^[\s⁠ `]*\[([A-Z][A-Z\-]*)\]")


def extract_vo(lines):
    """Return (beats, mode). beats is [(lineno, text)] of spoken paragraphs."""
    beats, in_vo, saw_marker, quoted = [], False, False, []
    for i, raw in enumerate(lines, 1):
        s = raw.strip().lstrip("⁠  ").strip()
        m = MARKER.match(s)
        if m:
            saw_marker = True
            in_vo = (m.group(1) == "VO")
            continue
        if not s:
            continue
        if s.startswith(("#", "---", "|", "```", ">", "- ", "* ", "1.")):
            if s.startswith(">"):
                t = s.lstrip("> ").strip()
                if t:
                    quoted.append((i, t))
            if s.startswith(("#", "---")):
                in_vo = False
            continue
        if in_vo:
            beats.append((i, s))
    if beats:
        return beats, f"{len(beats)} spoken beats after [VO] markers"
    if quoted:
        return quoted, f"{len(quoted)} blockquoted lines (no [VO] blocks found)"
    if saw_marker:
        return [], "markers found but no spoken text parsed"
    fallback = [(i, l.strip()) for i, l in enumerate(lines, 1)
                if l.strip() and not l.strip().startswith(("#", "|", "```", "`["))]
    return fallback, "all prose lines (no markers found)"


def strip_md(t):
    t = re.sub(r"[*_`]+", "", t)
    return t.strip()


def find_terms(lines, terms, whole_word=True):
    hits = defaultdict(list)
    for lineno, text in lines:
        low = text.lower()
        for term in terms:
            if whole_word and " " not in term:
                if re.search(r"\b" + re.escape(term) + r"\b", low):
                    hits[term].append(lineno)
            elif term in low:
                hits[term].append(lineno)
    return hits


def report_section(title, hits, note=""):
    if not hits:
        print(f"  OK  {title}")
        return 0
    total = sum(len(v) for v in hits.values())
    print(f"  !!  {title} ({total} found)")
    if note:
        print(f"      {note}")
    for term, linenos in sorted(hits.items(), key=lambda kv: -len(kv[1])):
        shown = ", ".join(f"L{n}" for n in linenos[:6])
        more = f" +{len(linenos) - 6} more" if len(linenos) > 6 else ""
        print(f"      '{term}' -> {shown}{more}")
    return total


def check_cadence(beats):
    """The teleprompter tell: uniformly short beats."""
    print("CADENCE")
    counts = [len(strip_md(t).split()) for _, t in beats]
    if not counts:
        print("  --  no spoken beats to measure")
        return 0
    med = statistics.median(counts)
    short = sum(1 for c in counts if c < 8) / len(counts)
    long_ = sum(1 for c in counts if c > 20) / len(counts)
    issues = 0

    verdict = "OK " if CADENCE["median_lo"] <= med <= CADENCE["median_hi"] else "!! "
    if med < CADENCE["median_lo"]:
        issues += 1
    print(f"  {verdict} median beat length: {med:.0f} words "
          f"(target {CADENCE['median_lo']}-{CADENCE['median_hi']})")
    if med < CADENCE["median_lo"]:
        print("      short beats each get their own pause. At this median the read")
        print("      becomes a litany. Join related beats; keep the short ones for")
        print("      landings. See references/conversation-and-cadence.md")

    verdict = "OK " if short <= CADENCE["short_share_max"] else "!! "
    if short > CADENCE["short_share_max"]:
        issues += 1
    print(f"  {verdict} beats under 8 words: {short*100:.0f}% "
          f"(target under {CADENCE['short_share_max']*100:.0f}%)")

    verdict = "OK " if long_ >= CADENCE["long_share_min"] else "!! "
    if long_ < CADENCE["long_share_min"]:
        issues += 1
    print(f"  {verdict} beats over 20 words: {long_*100:.0f}% "
          f"(target at least {CADENCE['long_share_min']*100:.0f}%)")
    if long_ < CADENCE["long_share_min"]:
        print("      no long beats means no momentum; nothing to land against")

    # Longest run of consecutive short beats.
    run = best = 0
    for c in counts:
        run = run + 1 if c < 8 else 0
        best = max(best, run)
    if best >= 6:
        issues += 1
        print(f"  !!  longest run of consecutive short beats: {best}")
        print("      six or more in a row is the vertical-list read")
    else:
        print(f"  OK  longest run of consecutive short beats: {best}")

    # Questions answered immediately = lecture cadence.
    qs = [i for i, (_, t) in enumerate(beats) if strip_md(t).endswith("?")]
    if len(qs) >= 5:   # below this the share is noise, not a pattern
        closed = sum(1 for i in qs
                     if i + 1 < len(beats)
                     and not strip_md(beats[i + 1][1]).endswith("?"))
        share = closed / len(qs)
        verdict = "OK " if share < 0.85 else "!! "
        if share >= 0.85:
            issues += 1
        print(f"  {verdict} questions: {len(qs)}, {share*100:.0f}% answered "
              f"immediately")
        if share >= 0.85:
            print("      a question the asker always answers is lecture cadence;")
            print("      leave some for the viewer")
    print()
    return issues


def check_repetition(beats, lines):
    """Repetition that a vocabulary check cannot see."""
    print("REPETITION")
    issues = 0

    anti = [ln for ln, t in beats if ANTITHESIS.search(strip_md(t))]
    share = len(anti) / len(beats) if beats else 0
    if len(anti) >= 12 or share > 0.06:
        issues += 1
        print(f"  !!  antithesis construction: {len(anti)} uses "
              f"({share*100:.0f}% of beats)")
        print("      'X isn't Y, it's Z' is strong once and a tic by the fifth use")
        print("      " + ", ".join(f"L{n}" for n in anti[:10]) +
              (f" +{len(anti)-10} more" if len(anti) > 10 else ""))
    else:
        print(f"  OK  antithesis construction: {len(anti)} uses")

    # One-word beats repeated: the named set read aloud more than once.
    singles = Counter(strip_md(t).lower().rstrip(".!?")
                      for _, t in beats if len(strip_md(t).split()) == 1)
    relisted = {k: v for k, v in singles.items() if v > 1 and len(k) > 2}
    if relisted:
        issues += 1
        total = sum(relisted.values())
        print(f"  !!  re-listed set items: {len(relisted)} terms, {total} reads")
        print("      a named set is read aloud in full once; elsewhere refer to it")
        for k, v in sorted(relisted.items(), key=lambda kv: -kv[1])[:8]:
            print(f"      '{k}' x{v}")
    else:
        print("  OK  no named set read aloud more than once")

    # Section openers that share a shape.
    openers = []
    cur = None
    for i, raw in enumerate(lines, 1):
        if re.match(r"^#{1,2} ", raw):
            cur = i
        elif cur is not None:
            for ln, t in beats:
                if ln > cur:
                    openers.append((ln, strip_md(t)))
                    break
            cur = None
    if openers:
        shapes = Counter()
        for _, t in openers:
            if ANTITHESIS.search(t):
                shapes["antithesis (X isn't Y)"] += 1
            elif t.endswith("?"):
                shapes["question"] += 1
        for shape, n in shapes.items():
            if len(openers) and n / len(openers) > 0.25:
                issues += 1
                print(f"  !!  {n} of {len(openers)} sections open with: {shape}")
                print("      vary the opening shape; under a fifth is the target")
        if not any(n / len(openers) > 0.25 for n in shapes.values()):
            print(f"  OK  section openers vary ({len(openers)} sections checked)")

    hits = find_terms(beats, THROAT_CLEARING, whole_word=False)
    issues += 1 if hits else 0
    report_section("recap-style section openers", hits,
                   "connecting is good; recapping the previous section is not")
    print()
    return issues


def check_structure(lines):
    """Every row of the structure table should have a written section."""
    print("STRUCTURE")
    src = "".join(lines)
    rows = set()
    for m in re.finditer(r"^\|\s*(\d{1,2})\s*\|", src, re.M):
        rows.add(int(m.group(1)))
    written = set()
    for m in re.finditer(r"^#{1,2}\s*(\d{1,2})\s*[—\-–:]", src, re.M):
        written.add(int(m.group(1)))
    if not rows:
        print("  --  no numbered structure table found; skipping")
        print()
        return 0
    missing = sorted(rows - written)
    extra = sorted(written - rows)
    issues = 0
    if missing:
        issues += 1
        print(f"  !!  promised in the table, not written: "
              f"{', '.join(f'{n:02d}' for n in missing)}")
        print("      the table is a contract: write the section or drop the row")
    else:
        print(f"  OK  all {len(rows)} table rows have a written section")
    if extra:
        print(f"  !!  written but not in the table: "
              f"{', '.join(f'{n:02d}' for n in extra)}")
        issues += 1
    print()
    return issues


def check_shorts(lines):
    """Short seeds, and no legacy lift markers."""
    print("SHORT SEEDS")
    src = "".join(lines)
    seeds = len(re.findall(r"►\s*SHORT SEED", src))
    legacy = len(re.findall(r"SHORT (STARTS|ENDS)", src))
    issues = 0
    if legacy:
        issues += 1
        print(f"  !!  {legacy} legacy SHORT STARTS/ENDS markers found")
        print("      lift markers are withdrawn: they produce clips with no bridge.")
        print("      replace with ► SHORT SEED blocks and let youtube-shorts-funnel")
        print("      rebuild the Short. See 'The Shorts boundary' in SKILL.md")
    if seeds == 0 and not legacy:
        print("  --  no Short seeds marked (fine if none of the sections earn one)")
    elif seeds:
        print(f"  OK  {seeds} Short seeds marked")
        if seeds > 6:
            print(f"  !!  {seeds} is a lot; 3-6 strong seeds beats one per section")
            issues += 1
        for field in ("CLAIM:", "PROOF:", "WITHHELD:"):
            n = len(re.findall(re.escape(field), src))
            if n < seeds:
                issues += 1
                print(f"  !!  {field} present in {n} of {seeds} seeds")
                if field == "WITHHELD:":
                    print("      WITHHELD is what the eventual bridge promises;")
                    print("      a seed without it produces a generic CTA")
    print()
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--wpm", type=int, default=150,
                    help="spoken words per minute (default 150)")
    ap.add_argument("--cadence", action="store_true",
                    help="cadence and repetition only")
    args = ap.parse_args()

    try:
        with open(args.script, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError as e:
        print(f"could not read {args.script}: {e}", file=sys.stderr)
        return 1

    beats, scope = extract_vo(lines)
    words = sum(len(strip_md(t).split()) for _, t in beats)
    minutes = words / args.wpm if args.wpm else 0

    print(f"\n=== scriptcheck: {args.script} ===")
    print(f"scope: {scope}\n")

    print("RUNTIME")
    print(f"  {words:,} spoken words at {args.wpm} wpm = ~{minutes:.1f} min")
    file_words = sum(len(l.split()) for l in lines)
    if file_words > 800 and words < file_words * 0.25:
        print()
        print("  !!  EXTRACTION LOOKS WRONG")
        print(f"      the file holds ~{file_words:,} words and only {words:,} were")
        print("      read as spoken. Every check below is running on a fraction of")
        print("      the script, so a clean report means nothing. Check that spoken")
        print("      lines follow a `[VO]` marker.")
    elif minutes < 20:
        print("      note: short for a long-form episode; check for unwritten sections")
    print()

    cad = check_cadence(beats)
    rep = check_repetition(beats, lines)

    if args.cadence:
        print("SUMMARY")
        print(f"  {cad} cadence issues, {rep} repetition issues\n")
        return 0

    struct = check_structure(lines)
    shorts = check_shorts(lines)

    print("PUNCTUATION")
    dash_hits = defaultdict(list)
    for lineno, text in beats:
        for ch, name in (("—", "em dash"), ("–", "en dash")):
            if ch in text:
                dash_hits[name].append(lineno)
        if "--" in text:
            dash_hits["double hyphen"].append(lineno)
    report_section("dashes in spoken lines", dash_hits,
                   "use '..' for a pause, or split into sentences")
    print()

    print("VOCABULARY")
    tell_total = 0
    for group, terms in AI_TELLS.items():
        tell_total += report_section(f"AI-tell {group}", find_terms(beats, terms))
    tell_total += report_section("AI-tell phrases",
                                 find_terms(beats, PHRASE_TELLS, whole_word=False))
    print()

    print("OPENERS / CLOSERS")
    report_section("banned openers",
                   find_terms(beats, BANNED_OPENERS, whole_word=False))
    report_section("banned closers",
                   find_terms(beats, BANNED_CLOSERS, whole_word=False))
    print()

    print("SUMMARY")
    dash_total = sum(len(v) for v in dash_hits.values())
    print(f"  cadence {cad} | repetition {rep} | structure {struct} | "
          f"seeds {shorts} | dashes {dash_total} | vocabulary {tell_total}")
    if not any((cad, rep, struct, shorts, dash_total, tell_total)):
        print("  clean")
    print("  reminder: flags are advice. Keep a word if it is genuinely right.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
