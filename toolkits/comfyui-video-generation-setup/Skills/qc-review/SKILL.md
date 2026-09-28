---
name: qc-review
description: Check a rendered video file for the defects that do not raise an error — black frames at a cut, captions drifting or running past the end, loudness and true-peak off spec, clipping, a grade that jumps between segments, duration not matching the EDL. Use before showing any render to anyone, whenever a video "looks fine but feels off", whenever captions seem out of sync, and always before publishing a master. Also use after any change to the renderer, because these failures are silent by nature.
---

# QC Review

The render exits 0. The file plays. Something is still wrong.

That is the normal failure mode of an automated edit, and it is why this stage
exists. Nothing in the pipeline raises an error when a cut lands on a black
frame, when captions were built on the source timeline instead of the output one,
when the AAC master overshoots the true-peak ceiling the limiter respected, or
when one segment was graded and its neighbour was not. The only way to find any
of it is to measure the rendered file.

```bash
python scripts/qc_review.py master.mp4 \
    --edl edit/edl.json \
    --timeline edit/renders/timeline.json \
    --captions edit/captions.ass \
    --target-lufs -14 --json edit/qc/qc.json
```

Exit code is 1 if anything FAILed, so it drops straight into a loop.

## What it checks, and why each one earns its place

**1 Duration** — against `timeline.json`, the durations the renderer *actually
produced*, not the EDL's nominal ones. Those differ: ffmpeg renders `ceil` of a
segment's frame count, so an unsnapped EDL runs long by up to one frame per cut.
Measured on this project at +182ms over 10 cuts before frame snapping was added.

**2 Cut boundaries** — mean luma one frame either side of every join. A large
jump is a visible picture jump; on a single-camera talking head the joins should
be nearly invisible and anything above ~18 luma levels wants a look.

**3 Frames** — `blackdetect` and `freezedetect`. Black frames inside the body
mean a cut landed past the end of a source. Leading and trailing black are
ignored, because those are usually intentional.

**4 Audio** — clipping via **`Peak count`**, not `Flat factor`: a hard-clipped
file has been measured here reporting `Flat factor: 0.00` alongside
`Peak count: 240`. Then integrated loudness and true peak against the declared
target. Check true peak on the **delivery encode**, not the mezzanine — a PCM
file normalised to exactly −1.0 dBTP came back at −0.83 dBTP after AAC, over
spec. Normalise to −1.5 and let the codec spend the headroom.

**5 Captions** — do all cues fit inside the output; does the last cue end
suspiciously early (the signature of captions built on the wrong timeline); is
`PlayResX/Y` declared; and does any `BorderStyle=3` style have `Outline=0`, which
renders bare text with no box and still succeeds.

**6 Grade** — luma across the runtime. A spread means segments were graded
inconsistently, which is what happens when a grade is applied to some segments
and not others.

## Reading the output

A finding is **FAIL** only when it is a defect. Everything else is **WARN**,
because a report that flags everything gets skipped, and a skipped report is
worse than no report.

When a check fails, fix the cause and re-render — do not tune the threshold.

## What it cannot tell you

It cannot tell you whether the cut was the right one, whether a pause was
rhetorical, whether the B-roll illustrated the line or distracted from it, or
whether the composite reads as real. **A clean QC report is a precondition for
showing someone the video, not a substitute for watching it.**

Cap repair at three passes. An agent repeatedly "improving" a creative edit
without human review oscillates or degrades it — after three, report what is left
rather than looping.

## When not to

Do not run it on intermediates. `cut.mov` has no captions and no final loudness,
so the caption and audio sections will fail on a file that is entirely correct for
its stage. QC the master, or pass `--skip captions,audio` when you deliberately
want an early look at picture only.
