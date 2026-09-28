---
name: palmier-tutorial-builder
description: Use Palmier as an optional transcript-aware rough-cut environment for a long-form tutorial with front camera, side camera, screen recording, production audio, and approved B-roll. Use when an agent must synchronize sources, remove repeated takes, build the dialogue spine, perform basic multicam/view switching, or export an early DaVinci-targeted FCPXML while preserving original A-roll. Use Palmier-only finishing only when explicitly selected; do not build masks, color, final typography, music automation, or effects before a planned Resolve handoff.
---

# Palmier Tutorial Builder

Default role: rough-cut accelerator. DaVinci Resolve remains the master finishing system unless `EPISODE_BRIEF.json` explicitly selects Palmier-only delivery.

## Required inputs

- `EPISODE_BRIEF.json`
- `edit_blueprint.json`
- source inventory and original media
- retake decisions
- selected handoff mode

Read:

- `references/palmier-build-protocol.md`
- `references/palmier-capability-map.md`
- `references/resolve-handoff.md` for every Resolve-bound project
- `references/session-proven-handoff.md` before handing a rough cut to a Resolve finishing session

## Choose the path

### Palmier rough cut to Resolve

Use for:

- source ingest and organization
- synchronization
- transcript generation/alignment
- repeated-take cleanup
- continuous dialogue spine
- basic face/desk/screen/B-roll switching
- edit markers and notes
- early FCPXML export

Do not finish masks, chroma key, color, PIP styling, typography, motion graphics, crop keyframes, audio fades, music automation, SFX, or master delivery in Palmier. Current FCPXML does not preserve several of those treatments.

### Palmier-only edit

Use only when the episode brief explicitly accepts the quality/control tradeoff. Follow the full blueprint, view, graphics, audio, and QC plans, but still build a look-development sample before scaling.

## Preflight

1. Duplicate the Palmier project or timeline.
2. Inspect the live Agent/MCP tool catalog and use current tool definitions.
3. Inventory source duration, resolution, frame rate, codec, audio, and transcript status.
4. Map stable blueprint IDs to media/clip IDs.
5. Select the production microphone as the audio spine.
6. Verify sync near the start, middle, and end.
7. Confirm handoff mode before adding any treatment.

## Rough-cut workflow

### 1. Synchronize

Create or update a multicam group for face, side/desk, screen, and microphone sources. Prefer reliable timecode; otherwise use waveform sync and verify visually.

Mute camera scratch tracks after sync but keep them available for reference.

### 2. Align script and takes

Use the full script, teleprompter script, transcript, and waveform to find false starts, sentence repeats, paragraph restarts, and alternate takes. Preserve the best complete intended performance. Mark ambiguous repetition rather than deleting it automatically.

### 3. Build the dialogue spine

Create the structural story cut before graphics, music, or effects. Repair cuts with room tone and short fades only when the project will remain in Palmier; for Resolve handoff, keep handles and record the intended repair because audio fades do not survive current DaVinci FCPXML.

### 4. Apply basic view intent

Use only the blueprint's primary view decisions:

- FACE for trust, claims, and interpretation
- DESK for physical process and orientation
- SCREEN for exact instruction
- BROLL for approved evidence and examples
- HOLD for reading or reflection

Use HOST_OVER_CONTENT or COMPARE only when a basic transform is needed to establish timing. Expect to rebuild final geometry and styling in Resolve.

Do not switch views at a fixed cadence.

### 5. Mark specialist work

Create markers or notes for:

- mask-first presenter isolation
- screen zoom/callout
- approved B-roll item ID
- motion graphic ID
- music state
- SFX cue
- color or quality repair
- review-required retake

These markers become the Resolve finishing checklist.

### 6. Export early

For Resolve-bound work, stop after structural editing. Export:

```text
DaVinci-targeted FCPXML
reference movie for timing only
source manifest and path map
retake decisions
edit blueprint
handoff notes
```

Transfer original camera, screen, and audio files. Do not replace them with the reference movie.

## Palmier-only background removal

When Palmier-only delivery is explicitly selected and chroma key previously failed:

- use tracked Magic Mask or manual mask controls first
- segment clips at pose/occlusion changes
- preserve hair and hands
- exclude chair, microphone, laptop, and props
- use chroma key only as localized cleanup when possible
- inspect over contrasting backgrounds
- fall back to framed PIP when the mask is unstable

For a Resolve handoff, skip Palmier mask finishing because Palmier effects and mask data do not transfer through FCPXML.

## Palmier-only finishing

Only on an explicitly approved Palmier-only project:

- use current layout operations for PIP/split view
- use real text/caption objects
- use restrained fades/keyframes
- use the approved B-roll and motion-graphics plans
- apply music/SFX automation in Palmier
- inspect representative frames and listen after every section
- render a look-development sample and run QC

## Non-negotiable rules

- Never modify or overwrite source originals.
- Never use a Palmier delivery render as Resolve A-roll.
- Never finish non-transferable work before a Resolve handoff.
- Never claim a capability from stale documentation; inspect live tools.
- Never delete an ambiguous take without a review state.
- Never add effects or view changes at a fixed interval.
- Never claim successful handoff until Resolve relinks originals and conform checks pass.
