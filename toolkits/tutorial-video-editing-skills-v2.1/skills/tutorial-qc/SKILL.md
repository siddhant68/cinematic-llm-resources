---
name: tutorial-qc
description: Review a rendered long-form tutorial and its planning files for story, retention, source quality, B-roll relevance and rights, mask-first green-screen composites, host-over-content layouts, screen readability, typography structure, motion graphics, J/L cuts, music and SFX balance, captions, and technical delivery. Use after a look-development sample or final Resolve/Palmier render, when an edit feels abrupt or amateur, or before handing the master to the YouTube release workflow.
---

# Tutorial Video QC

QC has two layers: automated measurements and editorial review. Neither replaces the other. Never report a pass from tool output alone.

## Required inputs

- rendered look-development sample or master
- `EPISODE_BRIEF.json`
- `source_inventory.json`
- `edit_blueprint.json`
- `broll_plan.json`
- `style_profile.json`
- `motion_graphics_plan.json`
- `audio_plan.json`
- rights/provenance manifests
- final captions and chapter plan when available
- original A-roll reference frames or clips

## Output

Produce `review/qc_report.md` with findings grouped as:

- `BLOCKER`: cannot publish
- `MAJOR`: materially harms comprehension, rights, quality, or professionalism
- `MINOR`: visible polish issue
- `NOTE`: optional improvement

Every finding must include timecode/range, evidence, impact, exact correction, responsible skill/stage, and verification method.

Read `references/session-proven-final-qc.md` before reviewing a delivery that has post-render trims, caption burns, remuxing, repeated generated clips, or multiple environment grades.

## 1. Watch-through passes

Perform at least:

1. uninterrupted story/retention watch
2. view, B-roll, composite, and graphics watch
3. audio-only or eyes-closed dialogue/music watch
4. phone-size readability watch
5. technical and source-quality inspection

Review the opening, every section boundary, every generated/stock asset, every difficult mask, every music-state change, and the final recap/end-screen range.

## 2. Story and structure

Can a new viewer state:

- the opening promise
- the current section
- why the shown visual matters
- the result or rule at the end

Flag:

- title/thumbnail promise not addressed early
- sections with no visible or audible identity
- open questions without payoff
- B-roll that interrupts the argument
- too many visual changes without new information
- long monologue stretches with no memory anchor
- final recap missing section headers or introducing new content

## 3. Cut continuity and tempo

At every noticeable cut, check:

- dialogue waveform and room tone continuity
- J/L-cut timing
- motion, gaze, cursor, shape, and screen-geography match
- sufficient anticipation and follow-through
- readable holds
- whether the transition effect has a structural reason

Flag abrupt simultaneous audio/picture changes, overused punches/whips, or fixed-cadence camera switching. Do not prescribe more effects before checking audio and timing.

Search the final transcript around every ripple splice for repeated two-to-six-word phrases, then confirm by listening. Also scan for short A-roll islands between adjacent B-roll clips; a one-frame to one-second return to the host is usually a continuity defect unless the plan names a reason for it.

## 4. View grammar and host presence

Flag:

- desk shot when exact UI must be read
- full face shot during critical on-screen instruction
- irrelevant or noun-matched B-roll
- presenter absent during an important interpretation/reaction
- permanent PIP that unnecessarily shrinks content
- PIP/cutout covering UI, proof, captions, or end-screen zone
- arbitrary view changes that do not improve comprehension

## 5. B-roll relevance, quality, and rights

For every inserted asset, verify:

- linked plan item and spoken claim
- actual information job
- owned/licensed/generated status
- source page, license, attribution, and hash where required
- no misleading documentary implication from generated footage
- no unresolved trademark, person, property, artwork, or embedded-audio issue
- no obvious loops, morphing, unreadable text, or continuity errors
- no unwanted production equipment, watermarks, prompt residue, or background objects that contradict the intended scene
- texture profile fits the role

Block release for unknown rights or a generated asset presented as factual evidence without clear context.

## 6. Green-screen and mask-first composite

Inspect normal playback and diagnostic frames for:

- green spill or gray halo
- missing fingers, hair, glasses, or motion blur
- transparent skin/clothing
- background attached to subject
- edge chatter/flicker
- bad chair, laptop, microphone, or prop exclusion
- mismatched exposure, color temperature, sharpness, noise, perspective, or light direction
- floating body or implausible shadow

When visible at normal playback, require repair or use the framed-PIP fallback. Do not pass a broken cutout because it looks acceptable in a still frame.

## 7. A-roll source-quality guard

Verify final A-roll is linked to the original camera media, not a Palmier render or web-compressed reference. Check:

- proxy/full-resolution status
- resolution and frame-rate conversion
- focus and detail
- compression blocking
- denoise smearing
- sharpening halos
- skin texture and color
- render cache quality

Compare source and render at 100%. Block release for unintended quality loss that can be avoided by relinking or render settings.

## 8. Typography and motion graphics

Review at full size and phone size. Check:

- section opener present and correctly timed
- memory anchors summarize rather than repeat transcript
- role hierarchy is obvious
- copy, spelling, line breaks, contrast, and hold time
- safe areas and collisions
- animation direction/easing consistency
- no excessive bounce, glow, glitch, pulse, or kinetic word emphasis
- final recap includes every major section header in order
- end-screen space remains clear

## 9. Screen readability

Check the smallest important UI/text on a phone-size preview. Flag:

- zoom arriving after the spoken detail
- zoom that removes needed context
- cursor/callout misalignment
- host or captions covering controls
- film grain, bloom, blur, or texture applied to screen recordings
- motion that prevents inspection

## 10. Audio

Listen for:

- clipped or unintelligible words
- room-tone holes and jumpy edits
- over-denoise or voice-isolation artifacts
- compression pumping
- level mismatch between takes
- music masking dense knowledge, names, numbers, code, or caveats
- music remaining at one constant level through the entire episode
- natural sound or SFX competing with speech
- SFX without a visible event
- abrupt cue starts/ends not aligned to phrase or structure
- unlicensed or unattributed music/SFX

Listen on headphones, laptop speakers, and phone at low volume.

## 11. Captions and YouTube structure

Check final-audio alignment, technical terms, names, line breaks, reading speed, and collision with UI/graphics. Verify chapter timecodes come from the final timeline. Inspect the last 5-20 seconds for end-screen-safe composition.

## 12. Technical analysis

Run:

```bash
python scripts/qc_media.py master.mp4 --json review/qc_media.json
```

Inspect every black, freeze, silence, stream, duration, frame-rate, resolution, and audio warning in context. Intentional events must be documented rather than automatically removed.

## Publish blockers

Block release when any remains:

- missing/offline/corrupt media
- final A-roll sourced from an unintended intermediate
- sync drift or clipped/unintelligible dialogue
- unresolved rights or required attribution
- generated illustration misrepresented as evidence
- visibly broken mask/cutout
- captions covering essential content or materially wrong
- screen instruction unreadable
- black/frozen frames not intentionally designed
- missing section/final-recap structure
- music or SFX materially masking speech
- export settings inconsistent with the approved master

## Closeout

After corrections, re-render the affected range and verify the fix. Do not close a finding from a timeline state change alone.
