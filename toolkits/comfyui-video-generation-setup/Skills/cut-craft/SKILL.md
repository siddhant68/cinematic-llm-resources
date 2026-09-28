---
name: cut-craft
description: Plan and execute split edits — J-cuts, L-cuts, cutaways, match cuts — so cuts feel invisible instead of abrupt. Use whenever a cut list or EDL is being assembled, whenever a user mentions J cuts, L cuts, split edits, crossover cuts, jump cuts, cutaways, pacing, rhythm, or says the edit feels "choppy", "abrupt", "robotic", or "like it jumps" — and whenever B-roll or a second angle is being placed over continuous narration.
---

# Cut Craft

A cut is invisible when the audience's attention is already moving when the
picture changes. Every technique here is a way of arranging that.

## The schema change this requires

Most agent EDLs give each range a single `start` and `end`, forcing audio and
video to cut at the same instant. That is a **straight cut**.

To be clear, because the opposite claim is common and wrong: **straight cuts are
not choppy, and they carry the majority of the edit in most polished
talking-head videos.** Choppiness comes from cutting at the wrong *moment*, not
from failing to offset the audio. Split edits are a tool for a specific job —
the visual source changes while approved narration continues — not a treatment
to apply at every boundary. Forcing a J-cut onto every retake join makes an edit
feel mannered.

What the schema needs to *permit* split edits is independent audio and video in
and out points.

Extend every range like this:

```json
{
  "source": "A",
  "start": 12.54, "end": 16.96,          // picture in / out
  "a_start": 12.20, "a_end": 17.40,      // sound in / out
  "cut_in": "J", "cut_out": "L",
  "quote": "...", "reason": "..."
}
```

- `a_start < start` → **J-cut**: you hear the next shot before you see it.
- `a_end > end` → **L-cut**: you keep hearing the previous shot after the picture
  has moved on.
- Omit the audio fields → straight cut.

If audio and video are extracted separately and recombined, `-c copy` concat no
longer works for the audio track. Extract video ranges and audio ranges as
separate streams, concat each, then mux. Keep the 30ms audio fade at every audio
boundary regardless — a hard audio splice pops even when it is perfectly timed.

## Which cut, and when

**L-cut (audio runs past the picture)** is the workhorse for a talking head
cutting to B-roll. The speaker keeps talking; the picture moves to the thing
they're describing. The viewer's ear provides continuity while the eye gets
something new. This is the default whenever narration is continuous and the
visual changes.

**J-cut (audio arrives before the picture)** creates anticipation. The next
sentence starts under the outgoing shot, so by the time the picture changes the
viewer already knows why. Strongest going *into* a new section or a hard claim —
the audio lead makes the visual arrival feel motivated rather than arbitrary.

**Straight cut** is correct when the change *is* the point: a hard topic pivot, a
punchline, a beat of silence. Used deliberately it lands. Used by default it
reads as an assembly, not an edit.

**Cutaway** hides a cut you couldn't otherwise make. If two kept ranges don't
join cleanly on picture — the subject's head is in a different position, the hand
is mid-gesture — a cutaway over the join removes the problem entirely, because
there is no longer a visible jump to notice. This is the primary reason to reach
for B-roll, ahead of illustration.

**Jump cut** is a style, not an accident. Rapid same-framing cuts read as energy
in short-form. In a long-form talking head they read as a mistake unless the
whole video is built that way. Pick one and be consistent.

## Where to place the cut

Audio boundaries are the most *reliable* source of cut candidates in a scripted
talking head, and the right default — but they are not the only motivation. A cut
can also be motivated by breath, sentence completion, gesture, blink, gaze shift,
movement direction, action inside B-roll, a graphic change, a musical phrase, or
simply the time a viewer needs to absorb what was just said. When the audio says
"cut here" and the picture says "not yet", the picture usually wins.

Starting from audio, pick in this order:

1. **Silence ≥ 400ms.** Cleanest. Almost always safe.
2. **150–400ms phrase boundaries.** Usable, but check the frame first — the
   speaker may be mid-gesture.
3. **Under 150ms.** Unsafe. You are inside a phrase.

Then: **never cut inside a word**, and **pad every edge 30–200ms**. ASR
timestamps drift 50–100ms; padding absorbs the drift. Tighter for pace, looser
for a cinematic feel.

For split edits, offset audio by **200–600ms**. Under 200ms it isn't perceived as
a split edit, just as sloppy sync. Over 600ms on a J-cut, the viewer starts
wondering why they're hearing someone they can't see.

## Rhythm

Cut length should follow content, not a metronome. Uniform cut spacing is the
clearest signature of an automated edit — real editors vary it because meaning
varies.

Some reliable moves: hold longer on a line that needs to land; cut faster
through setup and enumeration; **let a beat of silence sit before an important
line** rather than trimming it, because the pause is what marks the line as
important; extend past a laugh or a reaction rather than cutting on it, since the
reaction is the beat.

When a cut feels wrong and the timing looks right, the problem is usually the
frame on either side, not the moment. Check both.

## Visual continuity

Timing alone does not make a cut work. Check these on the frames either side:

- **Shot size.** Cutting between two near-identical framings reads as a glitch.
  Change size meaningfully, or cover the join with a cutaway.
- **Eye-trace.** Where the viewer is looking at the outgoing frame should be near
  something worth looking at in the incoming one.
- **Cut on action.** A cut during a gesture is far less visible than one during
  stillness.
- **Avoid blinks and mid-gesture freezes** at the cut point — both read as errors.
- **Movement direction** should be consistent across the cut unless the change is
  the point.
- **Punch-ins are limited by source resolution.** A 1080p delivery from 4K source
  allows a ~2x punch-in; from a 1080p source it allows none without visible
  softening. Check the source before planning a punch-in as a "free" angle.

## Match cuts

If two shots share a shape, a movement direction, or a compositional line, cut on
that similarity and the transition disappears. Worth actively looking for at
section boundaries, where you'd otherwise reach for an effect. A match cut always
beats a transition.

## Self-check

Render, then sample the output at every cut boundary (±1.5s) and check for:
picture jump or flash; an audio spike at the splice that slipped past the fade;
sync drift between the audio and video ranges after concat; and split-edit
offsets that landed inside a word after padding.

If the cut list was built from a transcript, verify against the *rendered file*,
not the plan. The plan is where the intent lives; the render is where the errors
are.
