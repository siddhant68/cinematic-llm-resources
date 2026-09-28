# Fresh-agent workflow for tutorial video production

This bundle is an operating system for a tutorial video built from:

- a front-facing A-roll camera
- a side or desk camera
- a screen recording
- user-owned B-roll and result footage
- optional licensed stock footage and stills
- optional generated B-roll from local LTX/ComfyUI or Higgsfield
- a full script, teleprompter script, and optionally a transcript
- a replacement background for green-screen recordings

The recommended production path is:

```text
LTX or Higgsfield -> generated assets only
Palmier           -> optional rough cut only
DaVinci Resolve   -> master edit, masks, graphics, sound, color, and export
YouTube bundle    -> package, private upload, Studio review, and release
```

Higgsfield and Palmier are not alternatives. Higgsfield generates assets. Palmier edits. DaVinci Resolve is the primary finishing environment. **Resolve is not assumed to be preinstalled:** the fresh agent must install and verify it before the first episode when no passing setup report exists.

## What to provide to the fresh agent

Create one project folder and include:

```text
project/
  inputs/
    full_script.md
    teleprompter_script.txt
    transcript.srt                 # optional but strongly preferred
    face_camera.*
    side_camera.*
    screen_recording.*
    production_mic.*
    replacement_background.*      # image or video
    owned_broll/
    brand/
  EPISODE_BRIEF.json
  skills/
```

Copy `EPISODE_BRIEF_TEMPLATE.json` to `EPISODE_BRIEF.json` and replace every placeholder. For every user-owned video, state its intended role or the moments it can support. Do not rely on filenames alone.

At minimum, provide:

1. Full script and teleprompter script.
2. Every camera, screen, and audio source.
3. Replacement background and the requested removal method. Use `mask_first` when chroma keying has failed.
4. User-owned B-roll with intended uses.
5. Separate Higgsfield credit caps for B-roll and thumbnails.
6. Whether local LTX/ComfyUI may be used and the exact checkpoint license.
7. Delivery resolution, frame rate, aspect ratio, target duration, and YouTube intent.
8. DaVinci installation permissions, preferred edition, Studio-license availability, free-edition fallback permission, and whether a system restart is allowed.

A zero or missing Higgsfield cap means no paid generation. The agent may still prepare prompts and estimates.

## Install and activate the skills

Install the eight editing skills individually. In clients that support auto-discovery, copy each skill folder into the client's skills directory. In clients that accept ZIP uploads, use the individual `installable/<skill-name>/skill.zip` file rather than the grouped bundle.

Keep the active context small:

```text
tutorial-edit-director
tutorial-broll-producer
tutorial-view-design
tutorial-motion-graphics
tutorial-audio-finish
tutorial-qc
davinci-tutorial-builder
```

Load `palmier-tutorial-builder` only when Palmier will create the rough cut or final edit. Do not activate both builder skills unless the task explicitly includes a handoff.

## First-time DaVinci installation and MCP setup

Before editing, give the fresh agent `DAVINCI_MCP_FIRST_TIME_SETUP.md` and include its autonomous setup block in the opening prompt. **Do not pre-assume that DaVinci Resolve, Node.js, Python, FFmpeg, or the MCP is installed.** The agent must detect and install missing approved components, launch Resolve, complete a disposable edit/render test, configure the MCP, perform read-only and reversible write/readback tests, and produce `planning/DAVINCI_MCP_SETUP_REPORT.md` before touching the real project.

The agent should download only the latest compatible stable Resolve installer from Blackmagic Design. DaVinci Resolve Studio is the preferred production path because direct external scripting and key AI finishing features are available there. Install Studio only when a valid license is available; do not purchase it or expose an activation key. When no Studio license is available and the episode brief permits it, install the current free edition, but treat MCP automation as unproven until the current upstream bridge passes an end-to-end disposable test.

The agent must handle routine downloading, installation, configuration, restarts of Resolve/the MCP client, and testing itself. It should request user involvement only for a genuine non-automatable administrator/UAC prompt, official download form data it is not authorized to invent, Studio activation, or a computer reboot. It must not silently switch the production edit to Palmier when Resolve automation is blocked.

## Required workflow

### Stage 0 - Preflight and immutable source inventory

The agent must:

- validate `EPISODE_BRIEF.json`
- probe every source for duration, resolution, frame rate, codec, audio channels, and timecode
- hash or otherwise uniquely identify camera originals
- copy nothing over the originals
- create proxies only through an editor workflow that relinks full-resolution media for export
- identify missing, corrupt, duplicate, or mismatched sources
- verify sync near the beginning, middle, and end

Output:

```text
planning/source_inventory.json
planning/preflight_report.md
```

### Stage 1 - Story cut and retention map

Use `tutorial-edit-director` to align the script, teleprompter text, transcript, and recorded takes. Preserve the best complete intended performance; do not simply retain the last semantically similar sentence. Build one clean dialogue spine before adding visual decoration.

Plan the opening promise, section progression, open questions, proof, payoffs, and final takeaway. A retention device can be a question, visual proof, changed point of view, audio lead, contrast, progress marker, or delayed payoff. It does not need to be a transition effect.

Output:

```text
planning/edit_blueprint.json
planning/edit_notes.md
edit/story_cut_timeline
```

### Stage 2 - B-roll ideation, sourcing, and generation gap analysis

Use `tutorial-broll-producer` before inserting B-roll. It must plan each beat in detail and answer:

- What claim or action needs visual support?
- Is the visual evidence, demonstration, orientation, emotion, analogy, or breathing room?
- Can a user-owned clip support it?
- Is a screen recording or diagram more truthful than generic stock?
- Can a commercially usable still or clip be sourced legally?
- Does the remaining gap genuinely justify generation?
- Should the host remain visible over the content?
- What texture treatment fits the information role?

Source priority:

1. User-owned proof and screen recordings.
2. Exact product/result footage supplied by the user.
3. Clearly licensed public-domain or stock assets.
4. A diagram or motion graphic made for the explanation.
5. Generated illustrative footage.

The agent may download free candidates only after verifying the exact asset license and recording a rights receipt. It must never rip clips from YouTube, social media, films, news sites, or search-result previews merely because they are visible online.

Output:

```text
planning/BROLL_IDEATION.md
planning/broll_plan.json
planning/generation_prompts.md
planning/higgsfield_spend_plan.json
assets/asset_manifest.json
assets/rights_ledger.csv
assets/download_receipts.json
```

The user must be shown the complete ideation, candidate sources, generation prompts, and projected paid spend before Higgsfield submission.

### Stage 3 - View, mask, typography, and motion-graphics design

Use `tutorial-view-design` for FACE, DESK, SCREEN, BROLL, HOST_OVER_CONTENT, COMPARE, GRAPHIC, and HOLD decisions.

For green-screen footage, default to mask-first isolation rather than a full-frame chroma key:

1. Keep the original A-roll clip untouched and place the replacement background below it.
2. Segment the shot at major pose, occlusion, or hand-crossing changes.
3. Track the person with Magic Mask or an equivalent person/object mask.
4. Add small positive strokes or masks to retain face, torso, hair, arms, and hands.
5. Add holdout or garbage masks for the chair, laptop, microphone, and persistent background leaks.
6. Refine the matte conservatively. Avoid wide feathering that creates a halo.
7. Apply localized chroma cleanup only to residual green regions when it improves the mask; do not return to a destructive global key.
8. Despill without removing natural green from clothing, objects, or skin reflections.
9. Match exposure, white balance, sharpness, noise, and contact shadow to the replacement background.
10. Test the composite over black, white, textured, and skin-toned backgrounds at 100% and 200% zoom.

When the matte remains unstable after two focused refinement passes, switch that beat to a designed framed PIP or split layout. A clean frame is more professional than a visibly broken cutout.

Use `tutorial-motion-graphics` to turn the monologue into a visible information structure. Every major section should have an opener; dense sections should have memory anchors; the ending should reassemble the section headers into a concise recap.

Output:

```text
planning/style_profile.json
planning/motion_graphics_plan.json
planning/graphics_copy.md
```

### Stage 4 - Music, SFX, and tempo plan

Use `tutorial-audio-finish` to create the audio plan before downloading music or SFX.

The plan must define:

- speech pace and section energy
- where silence or room tone is stronger than music
- where music begins, changes, lifts, ducks, and ends
- licensed source and attribution requirement for every track
- SFX linked to a visible event or structural cue
- scene-level automation rather than one constant music level

Use music with sparse arrangement and no competing vocal line under technical explanation. Lower it further for dense knowledge. Raise it only during non-dialogue proof, montage, or transitions, then return under speech before the next sentence.

Output:

```text
planning/audio_plan.json
planning/music_direction.md
assets/audio_rights_manifest.json
assets/audio_download_receipts.json
```

### Stage 5 - Review the complete plan

Before paid generation or full editing, show the user:

- section and retention map
- B-roll plan with exact placement
- licensed-source shortlist and rights status
- LTX/Higgsfield prompts
- projected Higgsfield credits by B-roll and thumbnail
- motion-graphics plan and typography roles
- music direction and SFX palette
- the 60-90 second look-development range

Free licensed candidates may already be downloaded into a quarantine folder. Do not treat them as approved for the edit until their relevance and license receipt are reviewed.

### Stage 6 - Build and approve one look-development sample

Build 60-90 seconds that includes:

- face camera
- side/desk camera
- readable screen recording
- user-owned or licensed B-roll
- host over content
- a mask-first background replacement
- section typography and at least one motion graphic
- captions
- music automation
- one motivated SFX
- a section transition

Review the sample at full size and phone size. Lock the grammar only after it works as one system.

### Stage 7 - Build the full episode in DaVinci Resolve

Work one section at a time. Use hard cuts, J-cuts, L-cuts, action matches, gaze matches, and audio bridges as the default continuity tools. Do not add an effect to every cut.

Every edit point must carry at least one useful bridge:

- continuous speech or room tone
- movement direction
- gaze or screen focus
- an unanswered question
- evidence replacing explanation
- a section marker
- contrast or payoff

A plain cut with a strong bridge is preferable to a flashy transition without meaning.

### Stage 8 - Finish, QC, and YouTube handoff

Finish masks, Fusion graphics, color, Fairlight automation, captions, and export in Resolve. Run `tutorial-qc` against the rendered file.

Pass these files to the YouTube bundle:

```text
master video
final captions
chapter timecodes
rights_ledger.csv
audio_rights_manifest.json
audio_download_receipts.json
generated_assets_log.json
thumbnail candidates and spend log
final script/transcript
```

Upload private first. Complete copyright, thumbnail, captions, cards, end screen, and watch-page review before publishing.

## A-roll quality preservation rules

These rules are mandatory because the camera source has little quality headroom:

- Never use a Palmier-rendered or AI-upscaled A-roll file as the Resolve source when the original exists.
- Never round-trip the master A-roll through H.264 between tools.
- For Palmier-to-Resolve, transfer FCPXML plus original media and a reference movie. Relink Resolve to the camera originals.
- Match the edit timeline to source frame rate unless delivery requirements explicitly differ.
- Use proxies only for playback. Verify full-resolution relink before every final render.
- Do not bake color, denoise, keying, typography, or audio automation into the Palmier handoff.
- Keep at least one untouched source-audio track until final delivery.
- Compare original and final A-roll at 100% for focus, compression, noise, skin texture, edge ringing, and color shifts.

## Fresh-session handoff prompt

Copy the prompt in `FRESH_SESSION_HANDOFF_PROMPT.md`. Attach this README, `DAVINCI_MCP_FIRST_TIME_SETUP.md`, the skills, `EPISODE_BRIEF.json`, and all project inputs.

## Definition of done

The episode is not done merely because a timeline rendered. It is done when:

- a new viewer can state the promise, current section, and final takeaway
- every B-roll shot adds evidence, clarity, orientation, emotion, or breathing room
- the presenter remains visible where trust or reaction matters
- screen details are readable on a phone
- typography reveals the structure without repeating whole paragraphs
- cuts feel continuous without transition clutter
- dialogue is consistently intelligible
- music and SFX have documented rights
- the final Resolve render uses the original A-roll media
- all blocker and major QC findings are closed
