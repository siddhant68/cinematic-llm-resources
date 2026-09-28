---
name: bg-plate-loop
description: Generate or source a seamlessly looping background plate to sit behind a keyed subject, using first/last-frame control so the loop point is invisible. Use whenever a background video, backdrop, background plate, or looping background is needed behind a green-screened speaker, and whenever a user asks for an abstract or ambient background that will repeat without being noticeable.
---

# Background Plate Loops

A plate that loops every 10–15 seconds behind a 10-minute video will repeat 40+
times. The entire craft is making that repetition invisible.

## What makes a loop noticeable

The viewer notices a loop when they can **time** it. Anything that gives them a
clock does that:

- An object that enters and exits frame
- A distinct shape passing a landmark
- A rhythmic pulse or flash
- A camera move that arrives somewhere and resets
- Any recognisable "event"

Anything the eye can track becomes a metronome, and once noticed it cannot be
un-noticed.

## What works instead

Motion without events. The plate should feel *alive* but have nothing to follow:

- Slow drifting gradients and colour fields
- Out-of-focus bokeh, drifting rather than travelling
- Particulate haze, dust, slow smoke
- Volumetric light shifting angle imperceptibly
- Very slow parallax on abstract geometry, no full traversal
- Liquid or ink diffusion, without a clear start state

**Relevance to the script should be thematic, not literal.** If the video is
about focus, a slow cool-blue drift with soft depth cues supports it. Actual
imagery of eyes, targets or clocks becomes a literal object that loops — the
worst case. The plate carries *tone*, and the B-roll carries meaning.

## Making the loop seamless

**Set it up at generation time, then verify.** Kling 3.0 Omni FLF accepts a first
*and* last frame. Supplying the same still for both makes the endpoints *look*
alike — it does **not** guarantee that motion velocity matches across the seam. A
plate can end on the right frame while still drifting in the wrong direction, and
the discontinuity reads as a twitch every loop. Treat "seamless loop" as a vendor
claim and test it.

Workflow:

1. Generate or choose a **still** for the look — a frame of the aesthetic you
   want. An image model is cheaper than video generation for iterating on this.
2. Submit to Kling 3.0 Omni FLF with that image as **both** first and last frame.
3. Prompt for the *motion*, not the content — the content is already fixed by the
   frames. "Slow drifting haze, gentle parallax, no objects entering frame,
   continuous ambient motion."
4. Generate 10–15s. Longer plates loop less often but cost more and rarely help,
   since the eye adapts to the aesthetic within a few seconds anyway.

Crossfading a non-loopable clip back onto itself is the fallback, not the plan.
It always softens the seam, and the softening itself becomes the rhythmic event
you were avoiding.

### Verify the seam

```bash
# last frame and first frame, side by side
ffmpeg -v error -sseof -0.04 -i plate.mp4 -frames:v 1 -y last.png
ffmpeg -v error -i plate.mp4 -frames:v 1 -y first.png
# difference: a good loop is near-black
ffmpeg -v error -i last.png -i first.png -filter_complex \
  "blend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG" \
  -f null - 2>&1 | tail -2
```

Endpoint similarity is necessary but not sufficient. Also check **motion
continuity**: sample a few frames either side of the seam and confirm the
direction and speed of drift match. The cheapest real test is to concatenate the
plate to itself three times and watch it — if your eye finds the seam, so will a
viewer's, forty times over.

**Archive generated plates immediately.** Vendor hosting is not permanent storage.
Save the file, the prompt, the seed, the model version and the cost alongside it.

### Consider not generating at all

For most of a talking-head video the background does not need to be a generated
video clip. Cheaper and often better:

- a **still image** with slow parallax (`zoompan`, or a scale-and-crop drift)
- a slow gradient or volumetric shift rendered procedurally
- controlled noise or grain over a solid field
- a defocused still of a real location

These loop perfectly by construction, cost nothing, and never twitch. Spend
generation credits on plates where the motion itself is doing editorial work.

## Before generating: check the free libraries

Abstract looping backgrounds are the **one category where free stock genuinely
competes with generation.** Pixabay in particular carries a deep library of 4K
abstract loops, particles and gradients, many built to loop, free for commercial
use without attribution. Coverr was founded on background loops specifically.

Search those first. Generation credits are better spent on shots that don't
exist.

## Preparing the plate for compositing

Whatever the source, the plate almost always needs pushing back:

```bash
ffmpeg -stream_loop -1 -i plate.mp4 -i fg_keyed.mov -filter_complex "
  [0:v]scale=1920:1080:force_original_aspect_ratio=increase,
       crop=1920:1080,gblur=sigma=12,eq=brightness=-0.06:saturation=0.9[bg];
  [bg][1:v]overlay=shortest=1,format=yuv420p" -c:a copy comp.mp4
```

- **Blur it more than feels right.** `sigma=8–20`. The plate is set dressing. Blur
  buys depth separation, hides the loop, and covers matte imperfections at once.
- **Darken until the subject clearly reads as the brightest thing in frame.**
  `eq=brightness=-0.06` is a starting point, not a percentage — the filter's value
  is not a perceptual luminance ratio. Judge it on the composite, not the number.
- **Desaturate slightly** unless the colour is doing deliberate work.
- **Scale to fill and crop**, never `scale=W:H` alone — a plate with a different
  aspect ratio will be stretched, and stretched motion is very visible.
- **`-stream_loop -1`** loops the input rather than concatenating copies, and
  `overlay=shortest=1` ends the composite when the foreground does.
- **Constrain the plate to the frame it has to support**: no high-frequency motion
  behind the hair line, no bright object repeatedly crossing frame, negative space
  where captions and the PIP will sit, and low contrast directly behind the face.

If the subject still doesn't separate after blurring and darkening, the fix is a
**light wrap** (see `greenscreen-comp`), not more blur.

## Verification

Play the composite across at least three loop cycles and watch the *background*
rather than the subject — the opposite of how you'll watch every other check.
If you can identify the loop point, note the timestamp: whatever is happening
there is the event to remove or blur out.

Then watch it once normally. If you notice the background at all during ordinary
viewing, it is too active.
