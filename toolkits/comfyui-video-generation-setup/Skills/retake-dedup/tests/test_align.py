#!/usr/bin/env python3
"""
Regression tests for align_retakes.py.

Each case builds a synthetic word-level transcript from an utterance stream and
asserts which script text survives. Run:  python tests/test_align.py

Cases marked KNOWN-LIMIT document behaviour that is intentionally imperfect and
is surfaced to the user via the review flag rather than silently guessed.
"""
import json
import os
import random
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ALIGN = os.path.join(HERE, "..", "scripts", "align_retakes.py")

PASS = FAIL = 0
FAILURES = []


def build_words(utts, seed=1, wpm_jitter=True):
    """utts: list of (text, gap_before_seconds) -> word-level transcript list."""
    random.seed(seed)
    words, t = [], 0.0
    for text, gap in utts:
        t += gap
        for w in text.split():
            dur = 0.16 + (random.random() * 0.20 if wpm_jitter else 0.1)
            words.append({"word": w, "start": round(t, 3), "end": round(t + dur, 3)})
            t += dur + 0.03 + (random.random() * 0.05 if wpm_jitter else 0.02)
    return words


def run(script_text, words_obj, extra=None):
    with tempfile.TemporaryDirectory() as d:
        sp = os.path.join(d, "s.txt")
        wp = os.path.join(d, "w.json")
        op = os.path.join(d, "o.json")
        open(sp, "w").write(script_text)
        json.dump(words_obj, open(wp, "w"))
        cmd = [sys.executable, ALIGN, "--script", sp, "--transcript", wp, "-o", op]
        if extra:
            cmd += extra
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            return None, r.stdout + r.stderr
        return json.load(open(op)), r.stdout


def norm(s):
    s = re.sub(r"[^\w\s']", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def kept_text(edl):
    return norm(" ".join(r["quote"] for r in edl["ranges"]))


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        FAILURES.append(name)
        print(f"  FAIL  {name}   {detail}")


# ------------------------------------------------------------------ cases

def t_deliberate_repetition():
    """Regression: v1 dropped the first of two identical scripted lines."""
    script = "Never give up. Never give up."
    edl, _ = run(script, build_words([("never give up", 0.5), ("never give up", 0.8)]))
    got = kept_text(edl)
    check("deliberate repeated line preserved", got == norm(script),
          f"got '{got}'")


def t_repeated_opening_phrase():
    """Two paragraphs starting with the same phrase must not collapse."""
    script = ("Here is the thing about focus. It compounds. "
              "Here is the thing about rest. It repairs.")
    edl, _ = run(script, build_words([
        ("here is the thing about focus", 0.5), ("it compounds", 0.6),
        ("here is the thing about rest", 0.7), ("it repairs", 0.6)]))
    got = kept_text(edl)
    check("repeated opening phrase in two paragraphs", got == norm(script),
          f"got '{got}'")


def t_refrain_three_times():
    script = "Do the work. Rest. Do the work. Rest. Do the work."
    edl, _ = run(script, build_words([
        ("do the work", 0.5), ("rest", 0.6), ("do the work", 0.6),
        ("rest", 0.6), ("do the work", 0.6)]))
    check("three-time refrain preserved", kept_text(edl) == norm(script),
          f"got '{kept_text(edl)}'")


def t_simple_retake():
    script = "Discipline is about designing an environment."
    edl, _ = run(script, build_words([
        ("discipline is about design", 0.5),
        ("discipline is about designing an environment", 0.9)]))
    check("cut-off flub dropped, good take kept",
          kept_text(edl) == norm(script), f"got '{kept_text(edl)}'")


def t_nested_retake_and_paragraph_restart():
    """The original end-to-end case: nested flubs + full paragraph re-read."""
    script = ("Here is what happens in your brain. Every decision burns a finite pool. "
              "By four the pool is empty.")
    edl, _ = run(script, build_words([
        ("here is what happens in your brain", 0.5),
        ("every decision burns a finite", 0.5),
        ("every decision burns a finite pool", 0.7),
        ("by four the pool is", 0.5),
        ("let me take that again", 1.2),
        ("here is what happens in your brain", 0.8),
        ("every decision burns a finite pool", 0.5),
        ("by four the pool is empty", 0.6)]))
    check("nested retakes + paragraph restart",
          kept_text(edl) == norm(script), f"got '{kept_text(edl)}'")


def t_whisperx_nested():
    """Regression: v1 treated each WhisperX segment as a single word."""
    wx = {"segments": [
        {"start": 0.5, "end": 1.6, "text": "never give up",
         "words": [{"word": "never", "start": 0.5, "end": 0.8, "score": 0.9},
                   {"word": "give", "start": 0.85, "end": 1.1, "score": 0.9},
                   {"word": "up", "start": 1.15, "end": 1.6, "score": 0.9}]}]}
    edl, out = run("Never give up.", wx)
    check("WhisperX segments[].words[] flattened",
          edl is not None and kept_text(edl) == "never give up",
          f"got '{kept_text(edl) if edl else out[:120]}'")


def t_scribe_shape():
    scribe = {"words": [
        {"text": "never", "start": 0.5, "end": 0.8, "type": "word"},
        {"text": " ", "start": 0.8, "end": 0.85, "type": "spacing"},
        {"text": "give", "start": 0.85, "end": 1.1, "type": "word"},
        {"text": "up", "start": 1.15, "end": 1.6, "type": "word"},
        {"text": "(laughter)", "start": 1.7, "end": 2.1, "type": "audio_event"}]}
    edl, _ = run("Never give up.", scribe)
    check("Scribe word/spacing/audio_event handled",
          kept_text(edl) == "never give up", f"got '{kept_text(edl)}'")


def t_segment_level_rejected():
    """Segment-level input must fail loudly, not silently misalign."""
    seg = [{"text": "never give up entirely", "start": 0.5, "end": 2.0},
           {"text": "and keep going forward", "start": 2.1, "end": 4.0}]
    edl, out = run("Never give up entirely and keep going forward.", seg)
    check("segment-level input rejected with clear error",
          edl is None and "SEGMENT-level" in out, f"got: {out[:120]}")


def t_semantic_filler_not_dropped():
    """'like', 'so', 'right' are scripted here and must survive."""
    script = "So it works like this, right? That is the whole idea."
    edl, _ = run(script, build_words([
        ("so it works like this right", 0.5), ("that is the whole idea", 0.6)]))
    got = kept_text(edl)
    check("semantic 'so/like/right' preserved",
          all(w in got for w in ["so", "like", "right"]), f"got '{got}'")


def t_adlib_between_good_takes_kept():
    """An aside with only ONE dropped neighbour must be kept, not deleted."""
    script = "First point here. Second point here."
    edl, _ = run(script, build_words([
        ("first point", 0.5),
        ("first point here", 0.7),
        ("by the way this matters a lot to me personally", 0.6),
        ("second point here", 0.6)]))
    got = kept_text(edl)
    check("ad-lib with one dropped neighbour kept", "by the way" in got,
          f"got '{got}'")


def t_skipped_script_line():
    script = "Line one here. Line two here. Line three here."
    edl, _ = run(script, build_words([
        ("line one here", 0.5), ("line three here", 0.7)]))
    got = kept_text(edl)
    check("skipped script line handled",
          "line one here" in got and "line three here" in got and "two" not in got,
          f"got '{got}'")


def t_asr_omission():
    script = "The quick brown fox jumps over the lazy dog."
    edl, _ = run(script, build_words([("the quick brown fox jumps over lazy dog", 0.5)]))
    check("ASR dropped a word -> still aligns and keeps",
          len(edl["ranges"]) == 1, f"ranges={len(edl['ranges'])}")


def t_number_normalisation():
    script = "It took 3 hours and 2 minutes."
    edl, _ = run(script, build_words([("it took three hours and two minutes", 0.5)]))
    check("spoken numbers align to digits", len(edl["ranges"]) == 1 and
          edl["stats"]["phrases_dropped"] == 0)


def t_no_silence_between_flub_and_restart():
    """Flub immediately followed by restart, no pause -> one phrase."""
    script = "Remove the decision entirely."
    words = build_words([("remove the deci remove the decision entirely", 0.5)])
    edl, _ = run(script, words)
    got = kept_text(edl)
    check("KNOWN-LIMIT: no-silence restart flagged not silently mangled",
          "remove the decision entirely" in got, f"got '{got}'")


def t_close_call_flagged_for_review():
    """Two complete takes of the same line -> keep last, flag for review."""
    script = "This single shift changed everything."
    edl, out = run(script, build_words([
        ("this single shift changed everything", 0.5),
        ("this single shift changed everything", 0.9)]))
    check("duplicate complete takes -> review flag raised",
          edl["stats"]["needs_review"] >= 1 or "REVIEW" in out,
          f"needs_review={edl['stats']['needs_review']}")


def t_output_shape():
    script = "Alpha beta gamma. Delta epsilon zeta."
    edl, _ = run(script, build_words([
        ("alpha beta gamma", 0.5), ("delta epsilon zeta", 0.6)]))
    r = edl["ranges"][0]
    check("EDL range carries required fields",
          all(k in r for k in ("source", "start", "end", "quote", "review"))
          and edl["version"] == 2)


def t_padding_never_negative():
    edl, _ = run("Go now.", build_words([("go now", 0.0)]))
    check("padding never produces negative start", edl["ranges"][0]["start"] >= 0)


def t_flub_with_no_room_must_not_steal_earlier_span():
    """Regression: a flub whose true span is taken must NOT grab a spurious
    earlier match. The greedy walk did, and that one bad placement then made
    every earlier phrase impossible."""
    script = ("Most people think discipline is about willpower. It isn't. "
              "Discipline is about designing an environment.")
    edl, _ = run(script, build_words([
        ("most people think discipline is about willpower", 0.5),
        ("it isn't", 0.5),
        ("discipline is about design", 0.6),
        ("discipline is about designing an environment", 0.9)]))
    got = kept_text(edl)
    check("flub cannot steal an earlier span (cascade regression)",
          got == norm(script), f"got '{got}'")



def t_partial_supersede_keeps_unique_content():
    """Regression: a retake that begins MID-PHRASE must not delete the unique
    material in front of it.

    Observed on real footage. The speaker says "...a fire, the sun. You can
    stylize it heavily.", pauses, then restarts at "You can stylize it heavily.
    But the frame...". The DP can only assign one of the two overlapping spans,
    so the first phrase was dropped whole — silently discarding "A light should
    feel like it came from somewhere. A window, a lamp, a door, a fire, the sun",
    which appears nowhere else. The render succeeds and a sentence is gone.

    Correct behaviour: trim the first phrase to its unique part and keep it.
    """
    script = ("A light should feel like it came from somewhere. "
              "A window, a lamp, a door, a fire, the sun. "
              "You can stylize it heavily. "
              "But the frame should still have internal logic.")
    edl, out = run(script, build_words([
        ("a light should feel like it came from somewhere", 0.5),
        ("a window a lamp a door a fire the sun you can stylize it heavily", 0.5),
        ("you can stylize it heavily but the frame should still have internal logic", 0.8),
    ]))
    got = kept_text(edl)
    check("partial supersede trims rather than deletes unique content",
          "came from somewhere" in got and "a window a lamp a door" in got
          and got.count("stylize it heavily") == 1,
          f"got '{got}'")


def t_partial_supersede_flags_review():
    """A trim is a content-removing decision, so it must reach the operator."""
    script = ("A light should feel like it came from somewhere. "
              "A window, a lamp, a door, a fire, the sun. "
              "You can stylize it heavily. "
              "But the frame should still have internal logic.")
    edl, out = run(script, build_words([
        ("a light should feel like it came from somewhere", 0.5),
        ("a window a lamp a door a fire the sun you can stylize it heavily", 0.5),
        ("you can stylize it heavily but the frame should still have internal logic", 0.8),
    ]), extra=["--report"])
    check("a trimmed phrase is flagged for review",
          "trimmed" in out.lower() and "REVIEW" in out,
          f"report did not surface the trim")


def t_full_supersede_still_drops():
    """The fix must not resurrect genuine retakes. A phrase whose span is
    substantially re-covered is still a retake and still gets dropped."""
    script = "Discipline is about designing an environment that makes it easy."
    edl, _ = run(script, build_words([
        ("discipline is about designing an environment that makes", 0.5),
        ("discipline is about designing an environment that makes it easy", 0.8),
    ]))
    got = kept_text(edl)
    check("fully superseded retake is still dropped",
          got == norm(script), f"got '{got}'")


ALL = [t_flub_with_no_room_must_not_steal_earlier_span, t_deliberate_repetition, t_repeated_opening_phrase, t_refrain_three_times,
       t_simple_retake, t_nested_retake_and_paragraph_restart, t_whisperx_nested,
       t_scribe_shape, t_segment_level_rejected, t_semantic_filler_not_dropped,
       t_adlib_between_good_takes_kept, t_skipped_script_line, t_asr_omission,
       t_number_normalisation, t_no_silence_between_flub_and_restart,
       t_close_call_flagged_for_review, t_output_shape, t_padding_never_negative,
       t_partial_supersede_keeps_unique_content, t_partial_supersede_flags_review,
       t_full_supersede_still_drops]

if __name__ == "__main__":
    print(f"Running {len(ALL)} cases against align_retakes.py\n")
    for fn in ALL:
        try:
            fn()
        except Exception as e:
            FAIL += 1
            FAILURES.append(fn.__name__)
            print(f"  ERROR {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{PASS} passed, {FAIL} failed")
    if FAILURES:
        print("failed: " + ", ".join(FAILURES))
    sys.exit(1 if FAIL else 0)
