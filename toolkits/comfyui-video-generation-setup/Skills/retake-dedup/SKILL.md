---
name: retake-dedup
description: Remove repeated takes from a single continuous recording of someone reading a script, keeping the last occurrence of each line. Use this whenever footage was recorded by reading from a script and the speaker re-said lines after stumbling, restarted paragraphs, or left dead air between attempts — and generally whenever a user mentions retakes, flubs, false starts, "I repeated myself", stumbles, or cleaning up a scripted voiceover or talking-head recording. Also use when a script file exists alongside the footage, even if the user only asks to "clean up" or "tighten" the recording.
---

# Retake Dedup

Cleans a single-take scripted recording down to the good bits by removing every
superseded attempt at a line.

## Why this is not a text-similarity problem

The naive approach — find near-duplicate sentences in the transcript and delete
the earlier ones — fails on real footage. Retakes are rarely verbatim (a
different word breaks each time), scripts contain deliberate repetition
("everything for me, and everything for you"), and a similarity threshold can't
tell a stumble from a rhetorical echo.

The reliable framing: **the speaker is reading a script, so the script is a
reference sequence and the transcript is a noisy walk along it.** Speech
progresses forward through the script. Every *backward jump* is a retake.

The implementation assigns phrases to script spans with a **global dynamic
program**: it maximises total alignment score over assignments that are monotonic
and non-overlapping in script space. Unassigned phrases are retakes or ad-libs.

Global matters, and an earlier greedy version proved why. A flub whose true span
is already claimed by the good take will happily grab a *spurious* earlier match
— "discipline is about design" matching the "discipline is about" inside a
different sentence — and that one bad placement then leaves no room for every
phrase before it. One local error destroys the whole prefix. Choosing placements
one at a time cannot recover from that; choosing them together can.

Last-occurrence selection falls out of the optimisation via a small tie-bias
toward later phrases, rather than being a post-hoc filter. Deliberate repetition
is protected because two identical scripted lines are two genuine positions, so
assigning both scores higher than assigning either alone.

This is not a solved problem in general, and the approach is not novel in kind:
Descript ships **Remove Retakes** and **Edit for Clarity**, and any
transcript-based editor can delete a highlighted range. What is specific here is
**script-referenced selection of the last complete take at each intended script
position**, which needs the script as a reference sequence rather than
similarity between transcript spans.

Cases this handles that similarity matching does not:

- **Nested retakes.** Flub, retry, flub the retry, retry again — each attempt
  supersedes the last.
- **Paragraph restarts.** A take that was *good* still gets dropped if the
  speaker later re-read the whole paragraph containing it. Chained supersession
  falls out of the algorithm for free.
- **Non-verbatim flubs.** A cut-off "designing an enviro—" still aligns to its
  script span and gets superseded.
- **Legitimate repetition.** Repeated wording occupies *different script
  positions*, so both instances survive. This is regression-tested for a repeated
  sentence, a repeated paragraph opening, and a three-time refrain — an earlier
  version of this skill failed all three.
- **Ad-libs.** Speech that matches nowhere in the script is kept and flagged, not
  deleted. Speech that matches only *above* the ceiling is a superseded attempt
  and is dropped. That distinction is what separates "I went off script here"
  from "I said this again later".

## Workflow

**1. Transcribe with word-level timestamps.** Phrase- or sentence-level output
destroys the sub-second gap data every later step depends on. Use verbatim mode —
do not let the ASR normalise away fillers and false starts, because those are the
editorial signal. ElevenLabs Scribe is the usual choice; WhisperX with
`--word_timestamps` works offline.

Verify the parse before trusting anything downstream — ASR schemas differ and a
segment-level file will silently misalign:

```bash
python scripts/align_retakes.py --transcript words.json --dump-words | head
```

The loader flattens WhisperX `segments[].words[]`, ElevenLabs Scribe `words[]`
with `spacing`/`audio_event` entries, and bare word lists. It **exits with an
error** rather than guessing if the input turns out to be segment-level.

**2. Run the aligner.**

```bash
python scripts/align_retakes.py \
  --script script.txt \
  --transcript words.json \
  --source A \
  -o edl.json --report
```

**3. Read the report before rendering.** It prints one line per phrase with its
script span, match score, completeness, and keep/drop decision.

Anything marked **REVIEW** needs a human. The tool raises that flag when it has
made a choice it cannot justify from the transcript alone:

- **Two complete takes of the same span.** Policy keeps the later one, but
  delivery quality is not observable in a transcript. If the earlier read was
  better, override with `--policy best_score` or edit the EDL.
- **Unmatched speech that was kept.** Off-script material. Sometimes the best
  moment in the video; sometimes "hang on, my dog is barking."
- **Disfluency-only phrases.** Never dropped silently.

**The tool does not decide delivery quality.** It has no access to clipping,
noise, energy, speaking rate, or whether you looked away from camera. Selecting
the latest complete take is a reasonable default and a wrong one often enough
that the review flags exist.

**4. Hand `edl.json` to the render step.** Ranges are already snapped to word
boundaries and padded.

## Tuning

Defaults suit a conversational read at ~150 wpm. Adjust when the report looks
wrong, one knob at a time:

| Symptom | Knob |
|---|---|
| Phrases split mid-sentence | raise `--gap` (0.45 → 0.6) |
| Two takes merged into one phrase | lower `--gap` (0.45 → 0.35) |
| Good takes wrongly superseded | raise `--overlap` (0.6 → 0.75) |
| Flubs surviving as separate keeps | lower `--overlap` (0.6 → 0.5) |
| Real lines flagged as unscripted | lower `--min-score` (0.55 → 0.45) |
| Ad-libs wrongly matched to script | raise `--min-score` (0.55 → 0.65) |
| Speaker jumped back many paragraphs | raise `--lookback` (160 → 400) |
| Later take kept but earlier was better | `--policy best_score`, or edit the EDL |
| Too many close calls flagged | lower `--review-threshold` (0.15 → 0.08) |

`--pad-in` / `--pad-out` control breathing room at cut edges. Stay inside
30–200ms: ASR timestamps drift 50–100ms and the padding absorbs it. Tighter reads
punchier, looser reads more cinematic.

## Tests

```bash
python tests/test_align.py
```

18 cases covering deliberate repetition, repeated paragraph openings, refrains,
cut-off flubs, nested retakes, full paragraph restarts, skipped lines, ad-libs,
ASR omissions, spoken-number normalisation, WhisperX and Scribe schemas,
segment-level rejection, semantically-loaded words that must not be treated as
filler, close-call review flagging, and output shape.

Run these after any change to the matcher. The suite discriminates between all
three implementations written so far:

| version | approach | score |
|---|---|---|
| v1 | per-phrase fuzzy match + overlap filter | 12/18 |
| v2 | greedy backward walk with a ceiling | 17/18 |
| v3 (current) | global DP over candidate spans | **18/18** |

**A known limitation, deliberately left visible:** a flub and its restart with
*no silence between them* land in one phrase and cannot be separated by silence
gaps. The phrase survives with both readings. Lowering `--gap` helps but risks
splitting real phrases. The report shows it rather than guessing.

## Note on filler words

Only true non-lexical disfluencies (`um`, `uh`, `erm`, `hmm`, `mm`) are ignored
during alignment scoring. Words like **like, so, right, okay, yeah, know are
deliberately not on that list** — they are frequently scripted or carry meaning,
and treating them as disposable corrupts both the alignment and the read. No word
is ever removed from the output because it appears on the list; the list only
affects match scoring.

## What this step does not do

It removes *superseded* speech. It does not remove silence inside a kept take,
choose between two equally-valid takes on delivery, or make any visual decision.
Silence trimming inside kept ranges is a separate, easier pass —
`silencedetect` will find them:

```bash
ffmpeg -i input.mp4 -af silencedetect=noise=-30dB:d=0.6 -f null - 2>&1 | grep silence
```

Be conservative there. Removing every pause produces a breathless read that is
noticeably worse than the original. Pauses before an important line are doing
work.

## Handoff

`edl.json` carries `ranges` (the cut list) and `decisions` (the full per-phrase
audit trail). Keep `decisions` — when the user says "put back the bit about
X", it's how you find what was dropped and why, without re-running anything.

Never re-transcribe a source that hasn't changed. Cache the transcript JSON.
