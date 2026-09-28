---
name: davinci-tutorial-builder
description: Install or verify DaVinci Resolve, configure the samuelgursky/davinci-resolve-mcp integration, and execute an approved long-form tutorial edit safely using Resolve's editing, Fusion, Color, and Fairlight tools. Use when an agent must prepare a missing Resolve environment, ingest and relink original media, build the story cut, apply front/side/screen/B-roll views, create J/L cuts, isolate a presenter with mask-first Magic Mask or tracked masks, build reusable motion graphics, automate music and SFX, preserve A-roll quality, verify timeline changes, render samples, and finish a source-safe master.
---

# DaVinci Tutorial Builder

Use Resolve as the master edit and finishing environment. Execute the reviewed plan; do not invent a new visual system while operating the timeline.

## Required inputs

- passing `DAVINCI_MCP_SETUP_REPORT.md`; when absent, run the bundle-level autonomous Resolve installation and MCP setup before opening production media
- `EPISODE_BRIEF.json`
- source inventory and original media
- `edit_blueprint.json`
- `broll_plan.json` and approved assets
- `style_profile.json`
- `motion_graphics_plan.json`
- `audio_plan.json`
- rights and provenance manifests
- approved look-development range or explicit instruction to create it

Read:

- `references/mcp-setup.md`
- `references/resolve-build-protocol.md`
- `references/track-template.md`
- `references/source-quality-and-conform.md`
- `references/mask-first-compositing.md`
- `references/session-proven-workflow.md` when the edit uses animated plates, a full-length composite replacement, or post-render finishing

## Connection and safety preflight

0. If Resolve is missing, fails to launch, or no passing setup report exists, read the bundle-level `DAVINCI_MCP_FIRST_TIME_SETUP.md`; install the approved stable edition and dependencies, configure the MCP, and pass the disposable tests before continuing. Do not ask the user to perform routine installation. Escalate only an unavoidable administrator, official registration, Studio activation, or reboot gate.
1. Open the verified Resolve installation and the correct duplicate project. Prefer Studio; treat a free-edition bridge or GUI-only path as conditional until it passes the documented runtime tests.
   When the user has explicitly authorized free Resolve through its interface, run a disposable create/edit/save/render test first. If it passes, continue through UI control and verify each consequential operation by timeline readback or rendered evidence. Record unsupported operations, and do not silently move the production edit to another editor.
2. Confirm the current edition/version, MCP server version, transport, server mode, project, timeline, and media state.
3. Use compound mode unless a verified task requires the granular surface.
4. Inspect available capabilities rather than assuming tool names.
5. Verify timeline resolution, frame rate, start timecode, audio sample rate, color management, and output path.
6. Verify that original camera and production-audio files are online.
7. Confirm all operations target a duplicate timeline.
8. Begin a trace or execution record when the MCP supports it.

The MCP is an execution bridge, not the editor-in-chief. Use the blueprint and specialist plans as the creative authority.

## Source-quality rules

- Relink to original camera files before visual finishing.
- Never use a Palmier delivery render as A-roll.
- Treat a Palmier reference movie as timing evidence only.
- Use proxies for playback only; verify full-resolution relink before sample and final renders.
- Do not transcode original A-roll merely to simplify automation.
- Preserve an untouched production-dialogue source and a muted scratch reference.
- Compare original and timeline A-roll at 100% for compression, noise, detail, edge ringing, and color shifts.

## Build sequence

### 1. Ingest and organize

Create deterministic bins and IDs for:

```text
01_CAMERA_ORIGINALS
02_SCREEN
03_AUDIO_ORIGINALS
04_OWNED_BROLL
05_LICENSED_ASSETS
06_GENERATED_ASSETS
07_GRAPHICS
08_MUSIC_SFX
09_SEQUENCES
10_RENDERS
```

Record source path, hash, frame rate, timecode, rights/provenance, proxy state, and blueprint ID. Do not rely on fuzzy filenames after ingest.

### 2. Synchronize and conform

- Align production audio, face camera, side camera, and screen recording.
- Verify sync near the start, middle, and end.
- Keep production dialogue on one continuous semantic track.
- If importing Palmier FCPXML, relink to originals and run the conform checklist before changing the edit.
- Stop when source ranges, speed, transforms, or sync do not match the reference.

### 3. Build the clean story cut

Follow retake decisions and the blueprint. Repair dialogue cuts with handles, room tone, and short crossfades. Do not add graphics, music, generated assets, or decorative transitions until the story cut is coherent.

### 4. Apply view grammar

Build FACE, DESK, SCREEN, BROLL, HOST_OVER_CONTENT, COMPARE, GRAPHIC, and HOLD beats from the approved plan.

- Use the side camera for physical workflow and orientation.
- Use the screen for legible instruction.
- Use approved B-roll for evidence or explanation.
- Keep the presenter visible only where trust or interpretation benefits.
- Use a designed hold when the viewer needs reading time.

### 5. Build mask-first presenter isolation

For clips marked `mask_first`:

1. Keep the original presenter clip on the upper video layer and the background below.
2. Split the clip at major pose, occlusion, prop, hand, chair, or camera changes.
3. Use Magic Mask Person/Features when available and reliable. Add positive strokes for face, torso, hair, arms, and hands and negative strokes for chair, laptop, microphone, and background.
4. Track each segment forward and backward.
5. Add alpha output and verify matte routing.
6. Refine the matte conservatively.
7. Use Fusion Polygon/holdout masks for persistent problems and keyframe only the difficult range.
8. Use a localized keyer for residual green only when it improves the matte.
9. Despill separately and protect legitimate greens.
10. Match foreground and background exposure, white balance, sharpness, noise, and light direction.
11. Inspect against black, white, textured, and skin-toned diagnostic backgrounds.
12. Render a motion sample with hair and hand movement.

Interactive Magic Mask strokes may not be exposed through the public scripting API. Use permitted desktop/UI control if available. When it is not available, use scriptable Fusion masks or mark the exact UI-only step. Never pretend the matte was completed.

When the matte remains broken after two focused passes, use the approved framed PIP fallback.

### 6. Build host-over-content

Use the style profile's geometry, then adapt placement to the point of interest. Verify:

- face and eyes remain readable
- host does not cover UI, captions, evidence, or end-screen zone
- scale, eyeline, edge treatment, and shadow are coherent
- entrance and exit do not interrupt dialogue
- layout remains stable unless the content requires a move

Do not add thick borders, glow, bounce, or floating movement by default.

### 7. Apply B-roll and screen focus

Use only approved plan items. Preserve natural sound when it adds proof. Apply the recorded texture profile. Keep screen recordings crisp and do not add film grain, bloom, or fake lens effects to small UI.

Use zooms only for legibility and spatial relationships. Establish context, move before the detail is needed, settle, hold, and return only when the wider view matters.

### 8. Build Fusion motion graphics

Create or reuse the stable template IDs from `tutorial-motion-graphics`. Validate one realistic longest-copy example of each required template before scaling.

For every graphic:

- set copy and duration from the plan
- verify safe-area placement
- check host, UI, caption, and end-screen collisions
- read back Text+ content when modified programmatically
- render representative frames
- preserve the approved motion family and speed class

Do not substitute low-quality generic titles when a template operation fails. Place a review marker and report the unsupported action.

### 9. Build cuts and transitions

Use hard cuts, J-cuts, L-cuts, action/gaze matches, audio bridges, and graphic matches first. Stagger audio and picture to remove abruptness. Add a dissolve, push, whip, or other stylized transition only when the blueprint records a structural reason and the look-development sample approved it.

Do not attach an effect to every cut.

### 10. Finish audio in Fairlight

Follow `audio_plan.json`:

- maintain the dialogue, natural sound, music, SFX, and reference track roles
- match phrase gain before bus processing
- use room tone and fades at dialogue edits
- automate music by section and cue
- duck or remove music under dense knowledge
- let music rise only in non-dialogue B-roll or planned montage
- tie SFX to visible events
- verify rights before use

Inspect automation readback where the MCP exposes it and listen in real time.

### 11. Color and texture

Match front and side cameras before applying a creative look. Preserve skin texture and avoid excessive denoise or sharpening. Apply B-roll texture per plan; screen recording remains clean digital. Verify generated assets match neighboring contrast, motion cadence, and light direction without disguising artifacts.

### 12. Look-development gate

Build the approved 60-90 second range containing every important mode. Render it from full-resolution sources and run QC. Do not copy templates, masks, audio treatment, or transitions through the full episode until the sample passes.

### 13. Full build loop

For every section:

1. Read timeline state.
2. Convert approved beats into a bounded operation plan.
3. Inspect risk and dry-run where available.
4. Apply only the current section.
5. Read back clip placement, in/out, track, transform, text, and audio state.
6. Render representative frames or a short range.
7. Compare against the blueprint and plan IDs.
8. Record exceptions and next action.

### 14. Render and verify

- Verify output resolution, frame rate, color space, codec, audio streams, captions, and file path.
- Confirm full-resolution media online and proxy mode disabled for final delivery.
- Render a short final-settings sample before the master.
- Run `tutorial-qc` on the rendered file.
- Reopen reported timecodes in Resolve and fix the correct source layer.
- Export an execution report or change log when available.

## Non-negotiable rules

- Never modify source originals or the only timeline copy.
- Never finish from a Palmier-rendered A-roll file.
- Never accept a broken matte to preserve a cutout layout.
- Never use a transition to hide unresolved timing or sync.
- Never create PIP without collision checks.
- Never claim success from a tool response alone.
- Never depend on an unstable free-edition scripting workaround for the production path.
- When free Resolve UI control is the authorized path, prove it on a disposable timeline before touching the production timeline.
