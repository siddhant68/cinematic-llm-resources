# Writing prompts for LTX-2.5

The prompt does more for output quality than any setting. Read this before
writing one.

## The shape that works

**One flowing paragraph, present tense, 120-160 words**, covering six concerns in
roughly this order:

1. **Shot and lens.** "Wide cinematic shot on a 35mm lens, shallow depth of field."
2. **Scene.** Where, what time, what is in the frame.
3. **Action, chronological.** Use explicit markers: *Initially… A moment later…
   Simultaneously…* The model follows temporal ordering when you give it.
4. **Subject detail.** Clothing, materials, hair, surfaces. Concrete nouns.
5. **Camera.** One move. "The camera pushes in very slowly, one unbroken move."
6. **Audio.** Describe it. "Audio: heavy surf on rock, wind across stone, a distant
   foghorn." Audio generates in the same pass and specifying it measurably helps.

## Rules that matter

**Never use comma-separated tags.** `lighthouse, storm, dusk, cinematic, 4k` is a
Stable Diffusion habit and it degrades LTX output. It confuses the temporal
attention. Write sentences.

**Physical cues, never emotion labels.** "His jaw tightens and he looks away"
works. "He is sad" does not.

**One light logic per shot.** Name the source: "one hard shaft of daylight from a
high window on the left, everything else in shadow". Mixed or unstated lighting
produces mush.

**One camera move.** Not three. "Slowly pushes in" or "tracks right", not "pushes
in then pans then cranes up".

**Long prompts are free.** The tokenizer pads everything to 1024 tokens, so a
three-word prompt costs the same as a rich paragraph. There is no reason to be
terse.

## What the model does reliably

- Single subject, slow deliberate camera
- Landscape and atmosphere: weather, water, fog, snow, fire
- Macro and abstract: liquid, ink, smoke, glass, texture
- Reflections, bokeh, rain on glass, defocused light
- One human figure in a held pose or slow movement
- Synchronized audio, genuinely good
- Multi-shot sequences that hold continuity across a cut

## What it struggles with

From the model's own documentation: *a static wall is easier than a moving face, a
reflective object, a readable sign or a fast camera move.*

- Fast action, fight choreography, sports
- Several characters interacting
- Hands doing detailed work, instruments being played correctly
- Readable text or signage
- Crowded frames
- Mixed or changing light

**If the request lands here, say so and offer the version that works.** A duel
rendered as fast swordplay between two people fails. The same duel as a slow
push-in on locked blades succeeds. Offer the trade; do not silently substitute.

## Worked example

Idea: *"a lighthouse in a storm"*

```
Wide cinematic shot on a 35mm lens. A lone stone lighthouse stands on black
volcanic rock at the edge of a dark northern sea, its lamp turning slowly in heavy
dusk. Storm swell rolls in from the left and breaks white against the base of the
tower. Initially the beam sweeps away from camera across low cloud. A moment later
it rotates back toward the lens and washes the wet rock in a pale gold bar of
light. Spray drifts through the foreground on the wind. The camera drifts slowly to
the right and very slightly upward, one steady unbroken dolly move, never fast.
Cold blue grey overcast light everywhere, with the lighthouse lamp as the only warm
source in the frame. Audio: heavy surf breaking on rock, wind moving across stone,
the low distant note of a foghorn.
```

Six concerns, chronological, one light source, one camera move, audio named.

## Negative prompts

**They are not evaluated at the default settings.** Both CFG values are 1.0, and
at that scale ComfyUI skips the unconditional pass, so the negative conditioning
never reaches the model. See `parameters.md`.

This means the positive prompt is the only lever you have on artifacts. If a shot
comes back with warped hands, do not add "malformed hands" to the negative —
change the shot so the hands are not the subject, or describe what they are
actually doing.

## Reference images

A reference **forces that frame to become that image**. It is a keyframe, not a
style hint.

Good: an actual film still of the scene, at the target aspect ratio.
Useless: character turnarounds, mood boards, empty location plates, anything on a
flat studio background.

**The more common failure is right content, wrong framing.** A perfectly good
close-up portrait is still the wrong reference for "walking through a garden",
because frame 0 becomes that close-up and a few seconds is not enough to pull back
to a wide shot. The result is a portrait that drifts, not a walk.

When the reference framing contradicts the requested action, say so and offer both:
direct the shot to the reference's framing (a tracking close-up where the walk
reads through parallax and body sway), or drop the reference and describe the
person in the prompt so the camera is free. The first keeps identity, the second
keeps the shot. Let the user pick; do not quietly pick for them.

Also check the aspect ratio before you generate. A mismatched reference is
centre-cropped without warning. See `parameters.md`.

If the user supplies the wrong kind, offer to write image-generation prompts for
proper keyframes instead. Ask for them at 2x the render resolution, and insist the
negative includes `character sheet, turnaround, multiple views, grey background`,
since image models default to those when handed a turnaround as input.

Placement: `:0` for the opening frame, `:-1` for the closing frame. First and last
is the pattern the official template uses and it is the safest. A mid-clip
reference over-constrains and can cause a visible jump; drop `--ref-strength` to
0.7-0.9 if you use one.
