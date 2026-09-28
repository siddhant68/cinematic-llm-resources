#!/usr/bin/env python3
"""
align_retakes.py — Select the intended take at each script position from a
continuous scripted recording.

MODEL
-----
The speaker reads a script. The transcript is a walk along that script that moves
forward, occasionally jumps backward (a retake), sometimes skips, and sometimes
inserts unscripted speech.

Alignment runs BACKWARD through the transcript with a descending ceiling: each
phrase must claim a script span strictly earlier than everything after it. Two
consequences a forward or position-independent matcher does not get:

  * "Keep the last occurrence" becomes structural, not a post-hoc filter. The
    final phrase claims its span first; earlier attempts find no room below the
    ceiling and are marked superseded.
  * Deliberately repeated script lines are protected. Two identical lines are two
    genuine script positions, so both spoken instances find a home.

Selection is separate from alignment. Alignment produces take groups; a policy
then chooses among them and flags close calls for human review.

USAGE
  python align_retakes.py --script s.txt --transcript w.json -o edl.json --report
  python align_retakes.py --transcript w.json --dump-words     # verify ASR parsing

TRANSCRIPT INPUT
  Auto-detects bare word lists, {"words":[...]}, ElevenLabs Scribe, and WhisperX
  nested {"segments":[{"words":[...]}]}.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from typing import List, Optional, Tuple, Dict

# ---------------------------------------------------------------- normalisation

# ONLY non-lexical disfluencies. Words such as "like", "so", "right", "okay",
# "yeah" and "know" are frequently scripted or semantically load-bearing and are
# deliberately absent. This set affects ALIGNMENT SCORING ONLY -- no word is ever
# removed from the output because it appears here.
DISFLUENCIES = {"um", "umm", "uh", "uhh", "erm", "hmm", "mm", "mhm"}

_PUNCT = re.compile(r"[^\w\s']")
_WS = re.compile(r"\s+")

_NUM_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12", "hundred": "100", "thousand": "1000",
}


def norm_token(tok: str) -> str:
    t = _PUNCT.sub("", tok.lower()).strip()
    if not t:
        return ""
    return _NUM_WORDS.get(t, t)


def tokenize_script(text: str) -> List[str]:
    return [t for t in (norm_token(w) for w in _WS.sub(" ", text).split(" ")) if t]


# ---------------------------------------------------------------- data model

@dataclass
class Word:
    text: str
    start: float
    end: float
    conf: Optional[float] = None
    norm: str = ""

    def __post_init__(self):
        if not self.norm:
            self.norm = norm_token(self.text)


@dataclass
class Phrase:
    idx: int
    words: List[Word]
    start: float
    end: float
    s_start: Optional[int] = None
    s_end: Optional[int] = None
    score: float = 0.0
    complete: bool = False
    keep: bool = True
    reason: str = ""
    superseded_by: Optional[int] = None
    group: Optional[int] = None
    review: bool = False
    covered_above_ceiling: bool = False
    cand_span: Optional[Tuple[int, int]] = None
    trimmed: Optional[str] = None

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)

    @property
    def duration(self) -> float:
        return self.end - self.start

    @property
    def span_len(self) -> int:
        return 0 if self.s_start is None else self.s_end - self.s_start


# ---------------------------------------------------------------- input parsing

def _iter_word_dicts(node, depth=0):
    """Find the deepest word-level dicts. Handles WhisperX segments[].words[],
    Scribe words[], and bare lists."""
    if depth > 6:
        return
    if isinstance(node, dict):
        for key in ("words", "word_timestamps"):
            if isinstance(node.get(key), list) and node[key]:
                for w in node[key]:
                    yield from _iter_word_dicts(w, depth + 1)
                return
        if isinstance(node.get("segments"), list):
            for s in node["segments"]:
                yield from _iter_word_dicts(s, depth + 1)
            return
        if ("word" in node or "text" in node) and "start" in node:
            yield node
        return
    if isinstance(node, list):
        for item in node:
            yield from _iter_word_dicts(item, depth + 1)


def load_words(path: str) -> List[Word]:
    with open(path) as f:
        data = json.load(f)

    words: List[Word] = []
    for item in _iter_word_dicts(data):
        if item.get("type") in ("audio_event", "spacing"):
            continue
        txt = item.get("word", item.get("text", ""))
        if not isinstance(txt, str) or not txt.strip():
            continue
        try:
            st = float(item["start"])
            en = float(item.get("end", item["start"]))
        except (KeyError, TypeError, ValueError):
            continue
        conf = item.get("score", item.get("confidence", item.get("probability")))
        try:
            conf = float(conf) if conf is not None else None
        except (TypeError, ValueError):
            conf = None
        w = Word(txt.strip(), st, en, conf)
        if w.norm:
            words.append(w)

    if not words:
        sys.exit("No timestamped words parsed. Run --dump-words to inspect, and "
                 "confirm the ASR ran in word-level (not segment) mode.")

    multiword = sum(1 for w in words if " " in w.text.strip())
    if multiword > len(words) * 0.3:
        sys.exit(f"Parsed {len(words)} items but {multiword} contain spaces — this "
                 "looks like SEGMENT-level output. Retake alignment needs word-level "
                 "timestamps. Re-transcribe with word timing enabled.")

    words.sort(key=lambda w: w.start)
    return words


def split_phrases(words: List[Word], gap: float, max_words: int) -> List[Phrase]:
    phrases: List[Phrase] = []
    cur: List[Word] = []
    for w in words:
        if cur and (w.start - cur[-1].end >= gap or len(cur) >= max_words):
            phrases.append(Phrase(len(phrases), cur, cur[0].start, cur[-1].end))
            cur = []
        cur.append(w)
    if cur:
        phrases.append(Phrase(len(phrases), cur, cur[0].start, cur[-1].end))
    return phrases


# ---------------------------------------------------------------- alignment

def match_in_window(ptoks: List[str], script: List[str], lo: int, hi: int,
                    prefer_latest: bool = True
                    ) -> Tuple[Optional[int], Optional[int], float, float]:
    """Best span for ptoks inside script[lo:hi] -> (start, end, score, coverage).

    prefer_latest matters when the same text appears more than once in the
    window. SequenceMatcher returns the EARLIEST longest match; the backward walk
    needs the LATEST. Reversing both sequences before matching flips that, then
    indices are mapped back to forward coordinates.
    """
    if not ptoks or hi <= lo:
        return None, None, 0.0, 0.0
    window = script[lo:hi]
    L = len(window)

    if prefer_latest:
        sm = SequenceMatcher(a=window[::-1], b=ptoks[::-1], autojunk=False)
        blocks = [b for b in sm.get_matching_blocks() if b.size > 0]
        if not blocks:
            return None, None, 0.0, 0.0
        matched = sum(b.size for b in blocks)
        # reversed index r maps to forward index L - r - size
        s_start = lo + (L - (blocks[-1].a + blocks[-1].size))
        s_end = lo + (L - blocks[0].a)
    else:
        sm = SequenceMatcher(a=window, b=ptoks, autojunk=False)
        blocks = [b for b in sm.get_matching_blocks() if b.size > 0]
        if not blocks:
            return None, None, 0.0, 0.0
        matched = sum(b.size for b in blocks)
        s_start = lo + blocks[0].a
        s_end = lo + blocks[-1].a + blocks[-1].size

    span = max(1, s_end - s_start)

    score = matched / len(ptoks)
    coverage = matched / span
    if coverage < 0.55:                    # scattered common words, not a match
        score *= coverage / 0.55
    return s_start, s_end, score, coverage


def candidates(ptoks, script, k=4, min_score=0.4):
    """Top-k plausible script spans for a phrase, anywhere in the script.

    Coarse pass: slide a window and count token overlap. Refine the best local
    maxima with SequenceMatcher. Returning several candidates is what lets the DP
    reject a locally-attractive but globally-impossible placement.
    """
    n, m = len(script), len(ptoks)
    if not m or not n:
        return []
    want = set(ptoks)
    win = max(m, 3)
    # coarse overlap score at each start position
    coarse = []
    for i in range(0, max(1, n - win + 1)):
        seg = script[i:i + win]
        hits = sum(1 for t in seg if t in want)
        coarse.append((hits / max(1, m), i))
    coarse.sort(reverse=True)

    picked, out = [], []
    for sc, i in coarse:
        if sc < min_score * 0.6:
            break
        if any(abs(i - j) < max(2, win // 2) for j in picked):
            continue          # keep candidates spread out
        picked.append(i)
        lo = max(0, i - win // 2)
        hi = min(n, i + win + win // 2)
        s0, s1, score, cov = match_in_window(ptoks, script, lo, hi,
                                             prefer_latest=False)
        if s0 is not None and score >= min_score:
            out.append((s0, s1, score, cov))
        if len(out) >= k:
            break
    # de-duplicate identical spans, keep the best score
    best = {}
    for s0, s1, score, cov in out:
        cur = best.get((s0, s1))
        if cur is None or score > cur[0]:
            best[(s0, s1)] = (score, cov)
    return [(s0, s1, sc, cv) for (s0, s1), (sc, cv) in
            sorted(best.items(), key=lambda kv: -kv[1][0])][:k]


def align_dp(phrases, script, min_score, tie_bias=1e-3):
    """Globally optimal assignment of phrases to script spans.

    A greedy walk fails here: a flub that cannot fit its true span will happily
    take a spurious earlier one, and that single choice then makes every earlier
    phrase impossible. Observed in practice, so the placement has to be chosen
    globally rather than one phrase at a time.

    Maximise total alignment score over assignments that are monotonic and
    non-overlapping in script space. Unassigned phrases are retakes or ad-libs.
    `tie_bias` nudges equal-scoring alternatives toward the LATER phrase, which
    is what makes last-occurrence selection fall out of the optimisation.
    """
    cands = []
    for ph in phrases:
        pt = [w.norm for w in ph.words if w.norm and w.norm not in DISFLUENCIES]
        cands.append(candidates(pt, script, k=4, min_score=min_score) if pt else [])

    # frontier: end_pos -> (total_score, prev_state_key, chosen_span, phrase_idx)
    frontier = {0: (0.0, None, None, None)}
    history = [dict(frontier)]

    for i, ph in enumerate(phrases):
        nxt = dict(frontier)                       # option: skip this phrase
        for end_pos, (score, _, _, _) in frontier.items():
            for (s0, s1, sc, cov) in cands[i]:
                if s0 < end_pos:
                    continue                        # would overlap / go backward
                total = score + sc + tie_bias * i
                cur = nxt.get(s1)
                if cur is None or total > cur[0]:
                    nxt[s1] = (total, end_pos, (s0, s1, sc, cov), i)
        # prune dominated states: a later end position with no better score is
        # never useful, and the frontier would otherwise grow without bound
        pruned, best_so_far = {}, -1.0
        for ep in sorted(nxt):
            sc_ = nxt[ep][0]
            if sc_ > best_so_far + 1e-12:
                pruned[ep] = nxt[ep]
                best_so_far = sc_
        frontier = pruned
        history.append(dict(frontier))

    if not frontier:
        return
    end_pos = max(frontier, key=lambda e: frontier[e][0])
    assigned = {}
    step = len(phrases)
    while step > 0:
        state = history[step].get(end_pos)
        if state is None:
            break
        total, prev, span, pidx = state
        if span is not None and pidx == step - 1:
            assigned[pidx] = span
            end_pos = prev
        step -= 1

    for i, ph in enumerate(phrases):
        pt = [w.norm for w in ph.words if w.norm and w.norm not in DISFLUENCIES]
        if not pt:
            ph.reason = "disfluency-only"
            ph.review = True
            continue
        if i in assigned:
            s0, s1, sc, cov = assigned[i]
            ph.s_start, ph.s_end, ph.score = s0, s1, sc
            ph.complete = cov >= 0.75 and len(pt) >= 0.75 * (s1 - s0)
            continue
        # unassigned: does it match the script at all?
        best = cands[i][0] if cands[i] else None
        if best and best[2] >= min_score:
            ph.s_start, ph.s_end, ph.score = best[0], best[1], best[2]
            ph.complete = best[3] >= 0.75 and len(pt) >= 0.75 * (best[1] - best[0])
            ph.keep = False
            ph.reason = "superseded"
            ph.covered_above_ceiling = True
            ph.cand_span = (best[0], best[1])
        else:
            ph.score = best[2] if best else 0.0
            ph.reason = "unscripted"
            ph.review = True



def rescue_partial_supersede(phrases: List[Phrase], script: List[str],
                             min_unique: float = 0.35) -> None:
    """Recover unique dialogue from phrases the DP could only drop whole.

    The dynamic program assigns non-overlapping script spans, so when a retake
    begins mid-phrase — the speaker restarts a sentence he had already begun —
    only one of the two phrases can be assigned. The other is marked superseded
    and, before this pass, was deleted entirely.

    That is wrong whenever the dropped phrase also carries script the winner does
    not cover. Observed on real footage: a phrase spanning script 115-139 was
    dropped because the next phrase claimed 134-165, discarding tokens 115-134
    ("A light should feel like it came from somewhere. A window, a lamp, a door,
    a fire, the sun") which appear nowhere else in the edit. The render succeeds
    and a sentence is simply gone, which is the worst class of failure here.

    So: measure how much of the dropped phrase's span is genuinely re-covered.

      re-covered >= 1 - min_unique   ->  a true retake, stays dropped
      otherwise                      ->  trim to the unique part and keep it,
                                         or if no clean word boundary exists,
                                         keep it whole and flag REVIEW

    Trimming never invents a boundary: it maps script positions back to word
    indices through the same matcher used to align, and only cuts where a word
    boundary actually falls.
    """
    claimed = [(p.s_start, p.s_end) for p in phrases
               if p.keep and p.s_start is not None]
    if not claimed:
        return

    for ph in phrases:
        if ph.keep or ph.reason != "superseded" or ph.cand_span is None:
            continue
        s0, s1 = ph.cand_span
        if s1 <= s0:
            continue
        span = set(range(s0, s1))
        covered = set()
        for c0, c1 in claimed:
            covered |= span & set(range(c0, c1))
        unique = span - covered
        frac_unique = len(unique) / len(span)
        if frac_unique < min_unique:
            continue                                  # a real retake; leave dropped

        # Where does the re-covered part begin? Alignment is monotonic, so the
        # unique material is a prefix (overlap at the end) or a suffix.
        cut = min(covered) if covered else s1
        prefix_unique = cut > s0

        idx_map, ptoks = [], []
        for wi, w in enumerate(ph.words):
            if w.norm and w.norm not in DISFLUENCIES:
                idx_map.append(wi)
                ptoks.append(w.norm)
        if not ptoks:
            continue

        sm = SequenceMatcher(a=ptoks, b=script[s0:s1], autojunk=False)
        boundary = None
        if prefix_unique:
            # last phrase-token that maps strictly before `cut`
            best_i = None
            for bi, bj, bn in sm.get_matching_blocks():
                if bn == 0:
                    continue
                for k in range(bn):
                    if s0 + bj + k < cut:
                        best_i = bi + k
            if best_i is not None:
                boundary = idx_map[best_i] + 1
                ph.trimmed = "tail"
        else:
            first_i = None
            for bi, bj, bn in sm.get_matching_blocks():
                if bn == 0:
                    continue
                for k in range(bn):
                    if s0 + bj + k >= max(covered) + 1 and first_i is None:
                        first_i = bi + k
            if first_i is not None:
                boundary = idx_map[first_i]
                ph.trimmed = "head"

        if boundary is None or not (0 < boundary < len(ph.words)):
            # cannot cut cleanly — keep the whole phrase and make a human look
            ph.keep = True
            ph.review = True
            ph.reason = f"partial-supersede ({frac_unique:.0%} unique, not trimmable)"
            ph.superseded_by = None
            continue

        if ph.trimmed == "tail":
            ph.words = ph.words[:boundary]
            ph.s_end = cut
        else:
            ph.words = ph.words[boundary:]
            ph.s_start = max(covered) + 1
        ph.start = ph.words[0].start
        ph.end = ph.words[-1].end
        ph.keep = True
        ph.review = True
        ph.reason = f"trimmed-{ph.trimmed} ({frac_unique:.0%} unique kept)"
        ph.superseded_by = None


def group_takes(phrases: List[Phrase]) -> Dict[int, List[Phrase]]:
    """Attach unaligned phrases to the aligned phrase they were retrying."""
    groups: Dict[int, List[Phrase]] = {}
    gid = 0
    for i, ph in enumerate(phrases):
        if ph.s_start is None or ph.covered_above_ceiling:
            continue
        ph.group = gid
        members = [ph]
        j = i - 1
        while j >= 0 and phrases[j].s_start is None and phrases[j].reason == "unscripted":
            cand = phrases[j]
            a = [w.norm for w in cand.words if w.norm not in DISFLUENCIES]
            b = [w.norm for w in ph.words if w.norm not in DISFLUENCIES]
            if a and b and SequenceMatcher(a=a, b=b, autojunk=False).ratio() >= 0.5:
                cand.group = gid
                cand.keep = False
                cand.reason = "failed-attempt"
                cand.superseded_by = ph.idx
                members.insert(0, cand)
            else:
                break
            j -= 1
        groups[gid] = members
        gid += 1
    return groups


def apply_policy(phrases: List[Phrase], groups: Dict[int, List[Phrase]],
                 policy: str, review_threshold: float) -> None:
    for members in groups.values():
        aligned = [m for m in members if m.s_start is not None]
        if len(aligned) < 2:
            continue
        complete = [m for m in aligned if m.complete] or aligned
        chosen = complete[-1] if policy == "last_complete" else max(
            complete, key=lambda m: m.score)
        for m in aligned:
            if m is not chosen:
                m.keep = False
                m.reason = m.reason or "superseded"
                m.superseded_by = chosen.idx
        runners = [m for m in complete if m is not chosen]
        if runners and abs(max(r.score for r in runners) - chosen.score) < review_threshold:
            chosen.review = True


def flag_ceiling_close_calls(phrases: List[Phrase], review_threshold: float) -> None:
    """A superseded take that was itself COMPLETE means two viable reads existed.
    Policy keeps the later one, but delivery quality is not observable here, so
    the surviving take is flagged for human confirmation."""
    by_span: Dict[Tuple[int, int], List[Phrase]] = {}
    for p in phrases:
        if p.s_start is None:
            continue
        by_span.setdefault((p.s_start, p.s_end), []).append(p)
    for members in by_span.values():
        if len(members) < 2:
            continue
        survivors = [m for m in members if m.keep]
        rivals = [m for m in members if not m.keep and m.complete]
        if survivors and rivals:
            best_rival = max(r.score for r in rivals)
            if abs(best_rival - survivors[-1].score) < review_threshold:
                survivors[-1].review = True


def mark_orphans(phrases: List[Phrase], max_dur: float, require_both: bool) -> None:
    """An aside surrounded by dropped attempts is part of the flub. Requires BOTH
    neighbours dropped by default — one is not evidence enough to delete speech."""
    for i, p in enumerate(phrases):
        if p.s_start is not None or not p.keep:
            continue
        if p.duration > max_dur:
            p.review = True
            continue

        prev_dropped = [q for q in phrases[max(0, i - 3):i] if not q.keep
                        and q.s_start is not None]
        next_kept = [q for q in phrases[i + 1:i + 4] if q.keep
                     and q.s_start is not None]
        next_dropped = any(not q.keep for q in phrases[i + 1:i + 3])

        # Strongest signal: the material dropped just before this aside is
        # re-read just after it. That makes the aside a restart announcement
        # ("let me take that again"), not content.
        restart_marker = any(
            d.s_start is not None and k.s_start is not None
            and min(d.s_end, k.s_end) - max(d.s_start, k.s_start) > 0
            for d in prev_dropped for k in next_kept)

        cond = restart_marker or (
            (bool(prev_dropped) and next_dropped) if require_both
            else (bool(prev_dropped) or next_dropped))

        if cond:
            p.keep = False
            p.reason = "restart-marker" if restart_marker else "flub-aside"
        else:
            p.review = True


# ---------------------------------------------------------------- output

def build_ranges(phrases, source, pad_in, pad_out, join_gap):
    kept = [p for p in phrases if p.keep]
    if not kept:
        return []
    ranges, members = [], [kept[0]]
    cur_s, cur_e = kept[0].start, kept[0].end
    for p in kept[1:]:
        if p.start - cur_e <= join_gap:
            cur_e, _ = p.end, members.append(p)
        else:
            ranges.append(_mk(source, cur_s, cur_e, members, pad_in, pad_out))
            cur_s, cur_e, members = p.start, p.end, [p]
    ranges.append(_mk(source, cur_s, cur_e, members, pad_in, pad_out))
    return ranges


def _mk(source, s, e, members, pad_in, pad_out):
    return {"source": source,
            "start": round(max(0.0, s - pad_in), 3),
            "end": round(e + pad_out, 3),
            "quote": " ".join(m.text for m in members)[:400],
            "phrases": [m.idx for m in members],
            "review": any(m.review for m in members)}


def report(phrases):
    out = [f"{'#':>4} {'time':>16} {'span':>11} {'sc':>5} {'cmp':>4} keep  note",
           "-" * 94]
    for p in phrases:
        span = f"{p.s_start}-{p.s_end}" if p.s_start is not None else "--"
        note = p.reason + (f" by #{p.superseded_by}" if p.superseded_by is not None else "")
        if p.review:
            note = ("REVIEW " + note).strip()
        out.append(f"{p.idx:>4} {p.start:>7.2f}-{p.end:<7.2f} {span:>11} "
                   f"{p.score:>5.2f} {'Y' if p.complete else '.':>4} "
                   f"{' ok ' if p.keep else 'DROP'}  {note}")
        out.append(f"       {p.text[:84]}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--script")
    ap.add_argument("--transcript", required=True)
    ap.add_argument("-o", "--out")
    ap.add_argument("--source", default="A")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--dump-words", action="store_true")
    ap.add_argument("--gap", type=float, default=0.45)
    ap.add_argument("--max-phrase-words", type=int, default=40)
    ap.add_argument("--min-score", type=float, default=0.55)
    ap.add_argument("--lookback", type=int, default=160)
    ap.add_argument("--policy", choices=["last_complete", "best_score"],
                    default="last_complete")
    ap.add_argument("--review-threshold", type=float, default=0.15)
    ap.add_argument("--pad-in", type=float, default=0.05)
    ap.add_argument("--pad-out", type=float, default=0.08)
    ap.add_argument("--join-gap", type=float, default=0.6)
    ap.add_argument("--adlib-max-dur", type=float, default=2.5)
    ap.add_argument("--orphan-any-neighbour", action="store_true")
    args = ap.parse_args()

    words = load_words(args.transcript)
    if args.dump_words:
        for w in words:
            print(f"{w.start:8.3f} {w.end:8.3f}  {w.text}")
        print(f"\n{len(words)} words parsed.")
        return
    if not args.script:
        sys.exit("--script is required unless using --dump-words")

    with open(args.script) as f:
        script = tokenize_script(f.read())
    phrases = split_phrases(words, args.gap, args.max_phrase_words)

    align_dp(phrases, script, args.min_score)
    rescue_partial_supersede(phrases, script)
    groups = group_takes(phrases)
    apply_policy(phrases, groups, args.policy, args.review_threshold)
    flag_ceiling_close_calls(phrases, args.review_threshold)
    mark_orphans(phrases, args.adlib_max_dur, not args.orphan_any_neighbour)

    ranges = build_ranges(phrases, args.source, args.pad_in, args.pad_out, args.join_gap)
    raw = words[-1].end - words[0].start
    kept = sum(r["end"] - r["start"] for r in ranges)
    dropped = [p for p in phrases if not p.keep]
    review = [p for p in phrases if p.review]

    if args.report:
        print(report(phrases), "\n")
    print(f"script tokens : {len(script)}")
    print(f"phrases       : {len(phrases)}  ({len(dropped)} dropped)")
    for r in ("superseded", "failed-attempt", "flub-aside"):
        n = sum(1 for p in dropped if p.reason == r)
        if n:
            print(f"  {r:<15}: {n}")
    print(f"duration      : {raw:.1f}s -> {kept:.1f}s  ({kept/raw*100:.0f}%)")
    print(f"ranges        : {len(ranges)}")
    if review:
        print(f"\n{len(review)} phrase(s) NEED REVIEW — check before rendering:")
        for p in review[:15]:
            print(f"  #{p.idx} [{p.start:7.2f}] {p.reason or 'close call':<16} {p.text[:56]}")

    if args.out:
        decisions = []
        for p in phrases:
            d = asdict(p); d.pop("words"); d["text"] = p.text
            decisions.append(d)
        with open(args.out, "w") as f:
            json.dump({"version": 2, "sources": {args.source: None}, "ranges": ranges,
                       "stats": {"raw_duration_s": round(raw, 2),
                                 "kept_duration_s": round(kept, 2),
                                 "phrases_total": len(phrases),
                                 "phrases_dropped": len(dropped),
                                 "needs_review": len(review)},
                       "decisions": decisions}, f, indent=2)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
