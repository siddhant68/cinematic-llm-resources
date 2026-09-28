# Editor and generation-tool decision

## Decision

Use DaVinci Resolve Studio as the primary editor and finishing system.

Use Palmier only as an optional rough-cut accelerator for synchronization, transcript cleanup, and basic angle switching. Skip Palmier when its FCPXML conform introduces more correction work than it saves.

Use LTX/ComfyUI and Higgsfield to generate missing visual assets. They are not substitutes for an editor.

## Default stack

```text
Planning: tutorial skill set
Generation: LTX locally, then Higgsfield for approved high-value gaps
Editing and finish: DaVinci Resolve Studio
Publishing: YouTube release/upload skill set
```

## Why Resolve is primary

The target format needs controlled tracked masks, dependable host-over-content compositing, reusable Fusion typography, multicam and screen workflows, camera matching, Fairlight automation, and source-quality verification. Keeping those stages inside one Resolve project avoids destructive render handoffs.

## When Palmier is still useful

Use it when transcript-based retake cleanup and rough multicam work are measurably faster. Stop after the structural cut. Export DaVinci-targeted FCPXML, original media, path map, and a reference movie. Rebuild every finishing layer in Resolve.

## Quality rule

Original A-roll is the source of truth. Every tool may reference it; no tool may replace it with a flattened delivery file before final export.
