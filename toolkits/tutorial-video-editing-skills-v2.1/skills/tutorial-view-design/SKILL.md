---
name: tutorial-view-design
description: Design the visual grammar for a long-form tutorial using front-camera A-roll, side or desk camera, screen recording, B-roll, comparison layouts, and presenter-over-content compositions. Use when an agent must decide which view best communicates each beat, isolate a presenter from a failed green-screen setup using mask-first tracking, build readable PIP or cutout layouts, plan screen zooms, J/L-cut visual handoffs, restrained transitions, captions, safe areas, and a reusable style_profile.json without adding decorative effects at a fixed cadence.
---

# Tutorial View Design

Choose the view that best carries the information. Do not alternate cameras merely to create activity.

## Required inputs

- `EPISODE_BRIEF.json`
- `edit_blueprint.json`
- approved `broll_plan.json`
- source inventory and representative frames
- background replacement asset
- target canvas, safe areas, captions, and end-screen plan
- brand references when available

Read:

- `references/view-grammar.md`
- `references/greenscreen-and-host-overlay.md`
- `references/typography-motion.md` for cross-skill boundaries
- `references/session-proven-environments.md` when a masked host sits over animated plates or the background changes lighting/time of day by section

## Required output

Produce `style_profile.json` and annotate every blueprint beat that needs a layout, screen focus, overlay, crop, or transition treatment.

Validate:

```bash
python scripts/validate_style_profile.py style_profile.json
```

## View modes

### FACE

Use for trust, opening promise, important claims, interpretation, emotion, caveats, personal experience, and conclusion.

### DESK

Use for physical orientation, hands on the laptop, hardware, posture, or a transition into work. Do not use it when the audience must read small UI.

### SCREEN

Use for exact reproducible instruction. Keep it crisp, full-frame when necessary, and zoom only to improve legibility or show spatial relationships.

### BROLL

Use approved evidence, examples, results, failures, atmosphere, and visual breathing room. Follow the B-roll plan rather than adding noun-matched footage.

### HOST_OVER_CONTENT

Use when facial presence adds trust or interpretation while the viewer studies content. Choose between a framed PIP and an isolated presenter cutout.

### COMPARE

Use for before/after, two methods, two outputs, or side-by-side alternatives. Keep scale, crop, labels, and visual weight fair.

### GRAPHIC

Use when a diagram, list, or structured explanation is more truthful than footage. The motion-graphics skill owns the graphic design and animation plan.

### HOLD

Use a stable shot when the viewer needs time to read, think, or absorb a result. A hold is not a failure to edit.

## Decision rules

1. Identify the information job.
2. Select the primary visual source.
3. Decide whether the host's face improves that job.
4. Protect the point of interest and captions.
5. Choose the simplest composition that remains readable.
6. Define the entry and exit bridge.
7. Inspect representative frames before reusing the treatment.

## Mask-first background replacement

When full-frame chroma keying has failed, default to tracked person/object isolation.

### Source-safe layer order

```text
Top: original presenter source with alpha/mask
Middle: optional shadow, edge, or integration layer
Bottom: replacement background or approved content
```

Never pre-render or replace the original A-roll before the final Resolve render.

### Segmented mask workflow

1. Split the presenter shot at major pose, occlusion, hand-crossing, chair, laptop, or camera changes.
2. Use Magic Mask Person/Features or an equivalent tracked person/object mask as the starting matte.
3. Add positive strokes or masks to preserve face, torso, hair, arms, and hands.
4. Add negative/holdout masks for chair, microphone, laptop, props, and persistent green leaks.
5. Track forward and backward per segment; do not force one track across a discontinuity.
6. Refine black/white matte levels, in/out ratio, and feather conservatively.
7. Inspect edges at normal playback, 100%, and 200% over black, white, textured, and skin-toned backgrounds.
8. Use localized chroma cleanup only inside remaining green regions when it improves the mask.
9. Despill separately and protect legitimate green clothing or objects.
10. Match exposure, white balance, sharpness, noise, grain, and contact shadow to the new background.

When the replacement background contains a table, desk, wall seam, horizon, or other strong perspective cue, align the presenter and foreground furniture to that cue before refining color. A desk edge should meet the photographed surface at the same height and inclination across the frame; otherwise the composite reads as two unrelated planes.

If the matte remains visibly unstable after two focused refinement passes, use a clean framed PIP or crop rather than publishing halos, missing fingers, or transparent hair.

## Framed PIP

Use when the content is primary and the host remains a human anchor.

- Start around 18-26% of frame width and adapt to the shot.
- Place it in the clearest safe region, not a fixed corner.
- Move or remove it when the screen point of interest changes.
- Use a subtle outline or shadow only when separation is required.
- Avoid glow, thick borders, arbitrary rounding, or animated bobbing by default.
- Preserve the host's eyeline and readable face size.

## Isolated host cutout

Use when the presenter should feel integrated with the content and the matte is dependable.

- Anchor feet/torso deliberately rather than floating mid-frame.
- Preserve hair, hands, glasses, microphone, and motion blur.
- Match scale, perspective, light direction, and contrast.
- Add a subtle contact shadow only where it makes spatial sense.
- Keep essential content, captions, and end-screen areas clear.

## Screen focus and zoom

Use zooms for legibility, not energy.

- Establish the full interface first unless the viewer already knows the context.
- Start the move before the spoken detail requires it.
- Settle while the user needs to read or inspect.
- Hold long enough to comprehend.
- Return only when broader context becomes relevant.
- Avoid repeated punch-in/punch-out cycles on the host.

## Cuts and transitions

Default to:

- hard cut
- J-cut
- L-cut
- action or gaze match
- sound bridge
- graphic match

Use a dissolve for real time/emotional change, a push when screen geography continues, or a section bridge when the argument changes. Do not add an effect to every cut. Every cut should have a continuity or curiosity bridge, but most do not need a transition plugin.

## Captions and structure

Reserve caption space in every layout. Use full subtitles for accessibility and selective emphasis only for high-value words or technical terms. Do not stack captions, section labels, callouts, and host PIP in the same region.

The motion-graphics skill owns section openers, memory anchors, lists, diagrams, and final recap. This skill owns their safe placement relative to footage and the host.

## Look-development gate

Build one 60-90 second sample containing all important view modes and at least one difficult mask segment. Inspect:

- UI legibility
- host scale and eyeline
- matte edges and spill
- caption collisions
- section graphic placement
- cut rhythm and audio continuity
- desktop and phone-size readability

Do not duplicate a flawed layout through the full episode.

## Non-negotiable rules

- No fixed camera-switch timer.
- No desk shot when exact UI must be read.
- No global chroma key when the approved method is mask-first.
- No broken cutout when a clean PIP would work.
- No PIP covering evidence or controls.
- No decorative zoom, glow, pulse, bounce, or whip by default.
- No full-episode rollout before look-development review.
