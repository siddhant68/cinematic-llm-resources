---
name: episode-edit
description: Edit a raw green-screen talking-head recording into a finished YouTube master — take selection from the script, chroma key, background, colour grade, kinetic captions, typography, B-roll and audio. Use whenever a user hands over raw footage plus the script it was read from and wants it edited, cut, composited or "made watchable", says "edit this video", "cut this down", "make this shippable", or provides footage with a generation budget. This is the edit orchestrator; it produces the master that youtube-episode then publishes.
---

# Editing an episode, end to end

The user hands over **raw footage, the script it was read from, and a generation
budget.** This turns that into a master. Publishing it is `youtube-episode`,
which starts where this finishes.

The script is not reference material, it is the **spine**. It decides which take
survives, where the sections are, where the labels go, which transitions are
motivated, and where B-roll belongs. A script with headings and `[VO]` markers
carries all of that already — read it, don't re-derive it.

## The rule that governs everything here

| Deterministic — a script decides | Creative — you decide |
|---|---|
| Which take survives at each script position | Which flagged take to keep when it is close |
| Section boundaries and their frames | Which boundaries earn a transition |
| Cut points, frame snapping, durations | Where a punch-in lands, and how far |
| Key parameters, once measured | The background, and the look |
| Loudness, true peak, QC thresholds | Which line becomes hero typography |
| Caption timing | Caption styling and the accent colour |
| B-roll frames from `[B-ROLL]` cues | Which clip answers the cue |

**Never invent a cut point, a duration or a threshold.** Run the tool that
computes it. **Never let a tool decide what the video is about.**

If a tool refuses, it found a real problem. Fix the input, don't route around it.

## Setup, once per machine

```bash
PY=~/Developer/video-pipeline/.venv/bin/python
export FFMPEG=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg
export FFPROBE=/opt/homebrew/opt/ffmpeg-full/bin/ffprobe
```

**Use `ffmpeg-full`, never the `ffmpeg` on PATH.** Homebrew's slim formula has no
libass, so `subtitles`, `ass` and `drawtext` do not exist and caption work fails
in ways that do not name the cause. Two venvs on purpose: `.venv` (3.14) for
everything, `.venv-align` (3.12, torch) for forced alignment.

Palmier must be running and signed in — `manage_project list` is the check.

## Order

Read `RUNBOOK.md` for the commands. The order matters and several steps are
one-way doors.

### 1. Measure before deciding anything

```bash
$PY preflight.py FOOTAGE --json edit/preflight.json
```

Ends in a verdict. Blockers produce silently wrong output — fix them before
spending time on the edit. Run `frame-design/scripts/analyze_framing.py` once
per *shoot setup* (not per video) to get the occupancy heatmap that decides
where captions, PIP and panels can live.

### 2. Transcribe, then fix the timings

```bash
$PY transcribe.py FOOTAGE --out-dir edit/cache
.venv-align/bin/python align_words.py --media FOOTAGE --transcript W -o A
```

**Do not skip the alignment.** Whisper transcribes this footage accurately and
times it badly — measured, its word timings implied 2 silence gaps ≥0.4s where
`silencedetect` finds 33, with runs of words collapsed onto whole seconds. Every
cut, caption and section boundary reads those numbers.

### 3. Sections, from the script

```bash
$PY sections.py --script SCRIPT.md --transcript A --fps 60 -o edit/sections.json
```

Locates each section by its opening spoken words and carries its `[B-ROLL]` cues
through with frames. Sections it cannot find are reported `unlocated` rather than
guessed — **do not place a label or transition for those.**

Frames are in the transcript's own timebase. Run it on the source transcript to
plan; re-run on the post-cut transcript to place.

### 4. Take selection

```bash
$PY skills/retake-dedup/scripts/align_retakes.py --script SCRIPT.md \
    --transcript A -o edit/edl_takes.json --report
```

**Read the report.** It optimises for script position, not delivery quality —
it cannot hear that the third attempt was flat. Anything flagged REVIEW is a
decision you must put to the user, because dropping it removes dialogue.

Its known limit: it chooses *between* takes, it does not catch a false start
*inside* one. Scan the transcript for stutters and cut those with Palmier's
`remove_words` at step 6.

### 5. Build in Palmier

Palmier is the editor. Everything visible happens here. See `RUNBOOK.md` for the
call sequence; the decisions that matter:

**The key.** Measure with `greenscreen-comp/scripts/analyze_key.py`, then use
`apply_effect key.chroma`. On the reference footage `keyHue 0.30, tolerance 0.34,
softness 0.11, spill 0.84` holds across the whole clip. Verify at five points
spanning the runtime including the darkest part of the screen — one still frame
proves nothing about temporal stability.

**Spill is the thing people get wrong.** Green in the hair is spill, not a bad
matte. But `spill 1.0` over-corrects and leaves a *magenta* edge. Pair a moderate
spill with an `apply_color` hue-curve that kills green saturation on the host
only (targetHue 120 and 150 → satScale 0). Safe because nothing on a person is
legitimately green, and the background is a different clip.

**The background is a place, not a texture.** Grade it against measured scopes,
not by eye: `inspect_color(clipId, reference)` returns the gap. One caveat —
on a keyed clip the transparent region drags the black measurement to zero, so
**ignore its "raise blacks" hint**; everything else is sound.

**Colour-grade the A-roll properly.** Under-grading reads as "faded" and is the
most common complaint. Push contrast and vibrance further than feels right on a
first pass, then pull back once.

### 6. Cut craft, in Palmier

`remove_silence` for dead air, `remove_words` for stutters the take selector
missed. Both ripple the timeline. Punch-ins on emphasis lines only — even spacing
is what makes an edit read as automated.

### 7. B-roll

Read `broll-direction` first. The evidence hierarchy is the point: **their own
output → their own screen recording → before/after → diagram → free stock →
generated.** Generic decorative stock is usually a sign the sentence needed no
visual at all.

The script's `[B-ROLL]` cues say where coverage was planned. Use them. When a
script has no `[B-ROLL]` markers, its `[V]` blocks are the visual brief —
`sections.py` carries them through as `visual_cues`.

**Triage every cue before costing anything. Most are not generations:**

| The cue asks for | Where it belongs |
|---|---|
| On-screen words, a title card, a term appearing | Palmier `add_texts` — free |
| A list, label, definition or text comparison | Palmier typography — free |
| "Talking head", "stay on face" | nothing — hold the shot |
| Their own output, screen recording, before/after | their footage |
| A real object, place or texture | free stock |
| Something that must be *specifically* this, and does not exist | Higgsfield |

**If the cue is text, it is never a generation.** A cue like
`Words appear one by one: SHOT. CAMERA. FRAME.` is a type animation — generating
it would cost credits, take longer, and look worse than your own typography
layer, which already has the font, the accent colour and the motion.

Then, for whatever survives triage, **write the requirement before the prompt**:
one sentence saying what must be true in the frame for the spoken line to land.
That sentence is the `rationale` in the plan, and it is what you check the output
against — not whether the image is pretty.

Judge candidates by **bits per pixel per frame**, not resolution:
`bitrate / (width × height × fps)`. Below ~0.06 expect visible blocking. Prefer
natively-4K sources and downscale — that averages compression artifacts away.

Free stock before generated, every time. State which source was searched and why
it lacked the shot before spending anything.

**When generating, read `references/higgsfield.md` first.** It carries the real
model constraints and measured credit costs, not guesses. Three things there
change the arithmetic:

- **Kling runs 3–15s, not 8.** The 8s cap is from older versions.
- **`sound` defaults to `on` and costs 33% more.** B-roll sits under a
  voiceover — always pass `sound: "off"`.
- **Iterate on 2-credit stills, not 7.5-credit video.** Explore the look with
  `nano_banana_pro`, then feed the chosen frame to Kling as `start_image`. One
  video generation, already art-directed.

Preflight every request with `get_cost: true` and keep a running total. Batch
independent prompts with `generate_video_batch` / `generate_image_batch` rather
than firing them one at a time.

### 8. Captions and typography — after ALL cutting

**Captions are generated last.** Any ripple edit after they exist leaves holes in
them; regenerate rather than patch. This is the single most repeated mistake.

**Caption every dialogue track.** `add_clips` pushes linked audio onto a second
track when spans overlap by even one frame, and `add_captions` takes one track —
so captioning A1 alone silently misses everything on A2.

### 9. Export, loudness, QC

Palmier exports the picture. **Loudness is ffmpeg's job** — Palmier has no LUFS
target and its export lands around −36 LUFS. Two-pass `loudnorm` to −14 LUFS at
**−1.5 dBTP**, not −1.0: the AAC master overshoots the PCM peak.

```bash
$PY skills/qc-review/scripts/qc_review.py MASTER --target-lufs -14
```

Exit 1 means defects. Fix the cause and re-render, capped at three passes. A
clean report is permission to watch it, not a substitute.

### 10. Hand off

`export_project mode=fcpxml fcpxmlTarget=fcp` for a Final Cut finishing pass —
optional, the master is deliverable without it. Then load `youtube-episode` with
the master, the script and the remaining budget.

## Reference files

`references/higgsfield.md` — Nano Banana Pro and Kling 3.0: exact parameters,
measured costs, the image-first workflow, and the prompting do's and don'ts for
each. Read it before any generation.

## Stop and ask

Proceed on reversible, low-risk choices and record the assumption. **Stop** when
the action removes content, spends generation credits, picks an asset with
uncertain rights, changes the matte strategy, or publishes anything.

A REVIEW flag from the take selector is not yours to resolve.

## Where to actually be creative

**Be creative about:** the background — what place this person should appear to
be in, and whether it competes with them. Which single line earns hero
typography. The accent colour, once, then everywhere. Which section boundaries
deserve a transition and which should just cut. Where a punch-in lands and how
far. Which clip answers a B-roll cue — the one that makes the *argument*, not the
one that matches the noun. Whether a moment is better with nothing on screen but
the face.

**Do not be creative about:** cut points, frame snapping, loudness targets, true
peak, caption timing, key parameters once measured, QC thresholds, section
frames, or whether a refusing tool can be worked around. Those have answers and
the tools already know them.

## Taste

The failure mode of automated editing is uniformity, not error: even cut spacing,
a transition at every boundary, B-roll on a metronome, every line captioned
identically. All technically correct and unmistakably machine-made.

Vary pacing with content. Let silence sit before an important line. Prefer a
match cut to a transition. When in doubt, don't add the effect.

## Known limits worth naming to the user

- **Delivery.** If the speaker reads from a prompter, measure their rate. Below
  ~120 wpm against a conversational 140–160 is a reading pace, and no edit fixes
  it. Say so — it is a shoot problem with shoot solutions.
- **Source bitrate.** Check it early. Under ~2 Mbps at 1080p, detail is gone
  before the edit starts and grading will amplify what is left.
- **Audio band balance.** Measure above 8 kHz and below 120 Hz. Missing top end
  cannot be created by EQ; boosting it only raises noise.
