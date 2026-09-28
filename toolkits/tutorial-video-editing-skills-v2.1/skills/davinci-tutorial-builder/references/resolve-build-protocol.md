# Resolve build protocol

## Inspect, plan, apply, verify

Use this loop for every section:

1. Read current timeline, tracks, clip IDs, and source mappings.
2. Convert only approved plan items into operations.
3. Inspect risk and blast radius.
4. Dry-run when supported.
5. Apply a bounded section.
6. Read back the resulting state.
7. Render representative frames/ranges for visual changes.
8. Listen through audio edits in real time.
9. Record operation trace, plan IDs, exceptions, and evidence.

## Deterministic mapping

Create one source map and reuse it:

```json
{
  "face_main": "01_CAMERA_ORIGINALS/face_main.mov",
  "desk_main": "01_CAMERA_ORIGINALS/desk_main.mov",
  "screen_main": "02_SCREEN/demo.mov",
  "mic_main": "03_AUDIO_ORIGINALS/lav.wav"
}
```

Do not select clips by fuzzy filename after mapping.

## Story cut before design

Build the dialogue spine and retake decisions first. Use timeline markers for uncertain choices. Keep handles and do not ripple-delete an ambiguous section without a review state.

## Visual execution order

1. Base camera program.
2. Screen and approved B-roll.
3. Host PIP or cutout.
4. Masks and screen callouts.
5. Motion graphics and captions.
6. Music, SFX, color, and final texture.

This order makes collisions and source quality easier to inspect.

## Completion evidence

A section is complete only when it has:

- operation/trace record
- timeline readback
- representative visual evidence
- sync and audio review
- plan item status
- exception list
