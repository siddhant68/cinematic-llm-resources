---
name: ltx-reel
description: Turn one idea into a finished multi-clip video generated locally with LTX-2.5, then hand it to publishing. Use whenever someone wants more than a single clip: a sample reel, a set of b-roll shots, a sequence, a short film, a demo reel for a team, several variations of an idea, or says things like "make me a few clips", "generate a reel", "produce a set of samples", "turn this concept into a video", or "make something I can show the team". Also use when generated clips already exist and need assembling, QC-ing as a set, or preparing for upload. Orchestrates the ltx-video skill for generation and the youtube-publish or youtube-episode skills for release.
---

# Reel from a concept

Single clip? Use `ltx-video` directly. This skill is for anything that needs more
than one shot, or that ends in something published.

## The pipeline

```
concept -> shot plan -> batch generate -> QC the set -> assemble -> publish
             (you)      (ltx-video)     (clipcheck)    (ffmpeg)   (youtube-*)
```

Only the first and last steps need judgement. The middle is scripted.

## 1. Shot plan

Turn the concept into 3-6 shots. Write the plan as a table and show it before
generating anything, because generation is 8 minutes a clip and structural changes
are free before that and expensive after.

For each shot record: id, one-line intent, duration, and whether it needs a
reference image.

Two rules that matter more than they look:

**Vary the shot size.** Wide, medium, macro. A reel of five wide landscapes reads
as one clip repeated. This is the single biggest difference between a set that
looks intentional and one that looks like output.

**Give each shot one job.** One subject, one camera move, one light source. If a
shot needs two things to happen, it is two shots. See `ltx-video`'s
`references/prompt-craft.md` for what the model will and will not do.

## 2. Generate as a batch

Write a batch file, one entry per shot, and run it in the background. Read
`ltx-video/references/parameters.md` for the flags.

```bash
cd ~/Documents/Applications/ComfyUI
./venv/bin/python ltxgen.py --batch /path/reel.json --stages 2 --res 1280x704
```

**Restart ComfyUI before a batch of more than three clips.** A machine in swap
turned an 8 minute render into 74. Check `sysctl -n vm.swapusage` first.

Budget roughly 8 minutes per 4 second clip at 1280x704 two-stage, 16 for 8 seconds.
Tell the user the total before starting.

## 3. QC the set

```bash
./venv/bin/python ~/.claude/skills/ltx-video/scripts/clipcheck.py output/video/reel_*.mp4
```

Then watch them. `clipcheck` catches black renders, wrong frame counts and silent
audio. It does not catch a shot that is simply bad, and roughly one shot in four
will need a reseed or a prompt rewrite. Plan for that rather than shipping the
first pass.

## 4. Assemble

Order for contrast, not for the order you generated in. Alternate wide and close,
loud and quiet.

```bash
# concat, re-encoding so clips with differing audio align
printf "file '%s'\n" /abs/path/*.mp4 > /tmp/reel.txt
ffmpeg -f concat -safe 0 -i /tmp/reel.txt -c:v libx264 -crf 18 -c:a aac out.mp4
```

If shots need trimming, crossfades or music, hand to `episode-edit`.

## 5. Publish

Hand the master to `youtube-publish` for a single video, or `youtube-episode` if
there is a script and it needs chapters and Shorts. For vertical cutdowns use
`youtube-shorts-funnel`.

Generated clips have no dialogue, so a reel usually wants either music or a voice
track added at the edit stage. Say so rather than publishing silent.

## Where your judgement matters

**The shot plan.** Turning one idea into a set that has range. This is the whole
job; everything after is execution.

**Concept selection.** If the user's idea is something the model does badly, say so
and offer the version that works, before spending 40 minutes rendering it.

**Which takes survive.** Generate more than you need and cut. A four-shot reel from
six generations is better than four generations all of which ship.

**Order and pacing.** The same five clips in a different order is a different piece.

## Honest limits

- No dialogue, no lip sync
- Clips are independent; characters will not match across shots unless you use the
  same reference keyframe in each
- 8 seconds is a practical per-clip ceiling on this machine
- Audio is per-clip and will jump at every cut unless you replace or duck it
