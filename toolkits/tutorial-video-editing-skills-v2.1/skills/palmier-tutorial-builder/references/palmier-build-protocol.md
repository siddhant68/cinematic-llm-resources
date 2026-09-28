# Palmier rough-cut protocol

## Read and map

- inspect the current project/timeline and live tool catalog
- map source IDs to media IDs once
- verify all originals remain available
- create a duplicate timeline

## Synchronize

- use timecode when trustworthy
- otherwise use waveform sync
- check start, middle, and end
- choose one production microphone
- mute, do not delete, camera scratch audio

## Retake cleanup

- align script, teleprompter, transcript, and waveform
- preserve best complete intended take
- retain handles
- mark ambiguous repeats
- do not use semantic similarity as an automatic delete command

## Structural view changes

Place only enough FACE, DESK, SCREEN, BROLL, and HOLD switches to express editorial intent. Final PIP, masks, typography, screen zooms, audio automation, color, and transitions belong in Resolve for the recommended path.

## Handoff markers

Use deterministic markers for:

```text
MASK
PIP
SCREEN_FOCUS
BROLL:<item-id>
MG:<graphic-id>
MUSIC:<cue-id>
SFX:<cue-id>
REVIEW
```

## Export package

Export FCPXML for DaVinci Resolve, a reference movie, source/path manifests, retake decisions, blueprint, and handoff notes. Keep the reference movie clearly labeled `REFERENCE_ONLY`.
