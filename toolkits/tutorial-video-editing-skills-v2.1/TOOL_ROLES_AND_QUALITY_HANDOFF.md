# Tool roles and source-quality handoff

## Final decision

Use DaVinci Resolve Studio as the master editing and finishing environment. When Resolve is absent, the fresh agent must install and verify it before production work; Studio is preferred when licensed, and a free-edition control path must pass runtime tests before use.

Use LTX/ComfyUI and Higgsfield only to create new visual assets. Use Palmier only when its transcript and multicam tools save enough time to justify a controlled early rough-cut handoff.

## Responsibility matrix

| Tool | Primary job | Do | Do not |
|---|---|---|---|
| LTX on ComfyUI | Local generated B-roll drafts and selected finals | Iterate cheaply, use references, log checkpoint and license | Do not assume repository code license covers model weights |
| Higgsfield | High-value generated B-roll and thumbnail candidates | Estimate credits first, submit approved prompts, download outputs immediately, log job/model/spend | Do not use it as the timeline editor or auto-retry ambiguous charged jobs |
| Palmier | Optional ingest, sync, transcript cleanup, rough multicam switching | Build the structural cut and export FCPXML early | Do not finish masks, color, typography, SFX automation, or master audio before Resolve handoff |
| DaVinci Resolve Studio | Master edit and finish | Relink originals, mask, composite, build Fusion graphics, mix in Fairlight, color, QC, export | Do not edit from a flattened Palmier render when originals exist |
| YouTube bundle | Release package and publishing | Validate rights, captions, chapters, thumbnail, upload private, finish in Studio | Do not publish while rights, processing, disclosures, or QC remain unresolved |

## Recommended direct path

```text
Original media + scripts
        |
        v
Planning and B-roll/graphics/audio design
        |
        +--> LTX/Higgsfield generated assets
        +--> verified licensed stock assets
        |
        v
DaVinci Resolve Studio master project
        |
        v
Resolve master render
        |
        v
YouTube release bundle
```

## Optional Palmier rough-cut path

```text
Original camera files
        |
        v
Palmier: sync + retake cleanup + basic angle decisions
        |
        +--> FCPXML for DaVinci Resolve
        +--> low-bitrate reference movie for visual comparison only
        +--> edit decision notes
        |
        v
DaVinci Resolve: import FCPXML and relink ORIGINAL camera files
        |
        v
Rebuild masks, graphics, color, audio automation, and final transitions
```

## Palmier-to-Resolve transfer package

Transfer all of the following together:

```text
project.fcpxml
reference_movie.mp4
audio_reference.wav or production mic original
source_manifest.json
path_map.csv
original camera and screen files
edit_blueprint.json
retake_decisions.json
handoff_notes.md
```

The reference movie is for comparison, not as a source clip.

## Conform verification

Before finishing:

1. Confirm timeline resolution, frame rate, start timecode, and audio sample rate.
2. Relink every clip to original media.
3. Compare at least ten edit points, including the opening, every section boundary, the longest screen segment, and the final minute.
4. Confirm source in/out frames, speed changes, transforms, and sync.
5. Confirm no proxy or offline media remains.
6. Compare the A-roll source and Resolve viewer at 100%.
7. Render a one-minute conform sample and compare it against the Palmier reference only for timing, never for image quality.

## Why finishing must happen after handoff

Palmier's current DaVinci FCPXML export carries clip placement, trims, speed, track order, text styling, transforms, flips, crop, opacity, static volume, source timecode, and supported visual keyframes. It does not carry audio volume keyframes, audio fades, text background boxes, crop keyframes, Palmier color/effects, edge softness, edge rounding, or Lottie clips.

Therefore the handoff must happen after structural editing, not after final design.

## Quality guard

Block final export when any A-roll clip is sourced from:

- a Palmier delivery render
- a web-compressed preview
- a generated or enhanced substitute when the original exists
- an offline proxy not relinked to full resolution
- a mismatched frame-rate conversion without review

When noise reduction or sharpening is required, use a conservative Resolve node and compare against the source at normal playback and 100% magnification. More processing is not automatically more detail.
