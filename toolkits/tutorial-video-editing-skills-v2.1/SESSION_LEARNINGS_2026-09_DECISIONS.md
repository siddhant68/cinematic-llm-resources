# Session-proven decisions: cinematic AI-pipeline episode

Use these as decision shortcuts when the same conditions recur. They are not universal style presets. The completed reference was a 14:19 talking-head tutorial with generated narrative B-roll, active-word captions, animated environment plates, section cards, music, and SFX.

## Editorial and lock preservation

- Build and approve the dialogue spine before styling. After every ripple removal, search the nearby final transcript for repeated two-to-six-word phrases, then listen across the splice; waveform closure alone missed repeated introductions and repeated claims.
- When a section card feels rushed, hold the card and pause the dialogue together. A 0.75-second complete A/V hold worked here; extending picture alone would have shifted captions or made narration run beneath the card.
- Treat late picture-only changes as conform work. Preserve the approved duration map, dialogue trims, section holds, caption timing, ambience, music, and SFX, then rebuild them deterministically on the replacement picture.
- The opening became clearer when “not one generation” was shown as a 2x2 proof grid (dance, yoga, flower close-up, walking), followed by the bench payoff full-screen exactly when the speaker named the shot he valued most. Use this pattern only when plurality followed by one decisive proof is the argument.
- Keep the central workflow thesis near the opening and return to it in the final line so the episode reads as one argument.

## B-roll and generated-shot repair

- Repeating B-roll is useful when narration deliberately revisits the same evidence, such as explaining audience eye movement twice. Repetition must be tied to the repeated claim, not used as filler.
- For adjacent B-roll clauses, cut B-roll directly to B-roll. A short A-roll flash reads as an error unless the presenter reaction is the point.
- If a generated clip has one defective interval and appears repeatedly, repair or exclude that source interval once and use the clean derivative for every occurrence. Recheck all appearances; this episode repeated the same bench geometry defect at three timeline locations.
- Watch generated clips at normal speed, not only as contact-sheet stills. Reject or trim morphing limbs, object intersections, phasing through furniture, unstable text, and implausible geometry.
- Preserve source aspect ratio when no upscale exists. A clean 4:3 presentation is preferable to stretching evidence to 16:9.

## Presenter and changing environments

- Animate static background plates subtly: slow cloud/weather motion, restrained practical-light variation, distant rain or birds. Movement should survive a still-frame comparison but should not compete with speech.
- Change environment at real section boundaries. Keep each plate loopable and audition the loop seam at normal playback before duplicating it.
- Align geometry before grading: tabletop height/inclination, horizon, perspective, subject scale, and contact point must read as one space.
- Match the foreground separately for each environment. Do not apply one global temperature shift across sunset, rainy night, early morning, and mist.
- Grade the isolated presenter before compositing: exposure, contrast, white balance, saturation, and gamma first; despill separately; then add a low-opacity edge wrap sampled from that background. Background-colored wrap reduced the cutout edge without turning skin orange or softening hair into a halo.
- Preserve natural skin and shirt detail. In the completed pass, the rainy environment needed the largest exposure/saturation reduction, while sunset and morning needed restrained warmth rather than a dominant orange cast.
- A full-length source-safe composite intermediate is acceptable when the original camera remains immutable, the operation is done on a duplicated timeline, the intermediate has the exact expected frame count, and every overlay/audio track is read back unchanged. It is a replacement layer, not a new editorial master.

## Captions, typography, and section events

- Generate captions from the final conformed audio and maintain a spelling/glossary override list. Human review caught ordinary-word errors (“garden”, “expensive”) that timing validation did not.
- After any ripple edit, hold insertion, or opening replacement, regenerate/reconform both active-word burn-ins and accessibility SRT; check first cue, last cue, and several words around every splice.
- Active-word orange works when inactive text remains stable and high-contrast. Inspect over the final moving background, not a nominal safe-area mockup.
- A section card is a structural event: readable picture hold, deliberate dialogue pause/room tone, optional recurring SFX, and music-state change should share one verified final-master timecode.

## Music, SFX, and encoded delivery

- Programme loudness does not prove music is audible. Compare a representative ducked music stem against dialogue. Roughly 15-20 LU below dialogue was a useful starting range here, followed by real listening.
- Record music source gain, sidechain threshold/ratio, attack/release, and measured post-duck level separately. A low threshold plus 5:1 ducking made a nominally present bed effectively disappear; a gentler 2.5:1 pass restored audibility without masking speech.
- Use one restrained recurring SFX family for verified section cards, beginning slightly before the visual landing when appropriate. Do not place effects on ordinary B-roll cuts.
- Reset music to an intentional phrase/beat at the opening and important structural cues; do not force dialogue edits onto the beat grid.
- Preserve rhetorical silences. Short silence detections can be intentional and must be inspected in context.
- Measure the final AAC file. This workflow needed extra pre-encode true-peak headroom; the accepted color-integrated delivery measured -14.14 LUFS and -1.20 dBTP at 48 kHz stereo.
- Carry exact attribution into the publish handoff. The music used here is “Digital Lemonade” by Kevin MacLeod, CC BY 4.0, edited for timing/level and mixed under dialogue.

## Resolve execution and render proof

- Begin with live read-only verification: Resolve product/version, project, current timeline, start/end frame, track counts, media online state, and available methods.
- Duplicate/version the approved timeline before replacing a long underlying layer. Read back item count per track, inserted clip name, absolute start/end, duration, transform, opacity, and composite mode.
- Pin a known video render preset. On builds without readable render settings, explicit `ExportVideo:true` is not enough to rule out inherited audio-only state.
- If the guarded render workflow requires a temporary target, use the actual system `TMPDIR`, render there, verify the job output before deleting the job, then move the verified file to a new non-overwriting production path.
- Verify the rendered file against known frame count/duration and require both video and audio streams. A Resolve “Complete” status is not delivery proof.
- Capture processed timeline frames from each environment and difficult overlay state. When B-roll covers the presenter at a chosen sample, move to a nearby A-roll frame rather than inferring the underlying composite.
- Keep an execution trace/report for consequential timeline changes and retain the previous master checksum.

## QC on the actual final master

- Run QC after every downstream finishing step, not only on the Resolve mezzanine. Post-render trims, caption burns, opening replacements, and audio remuxing can create new defects.
- Count decoded frames and compare duration with the approved map. Verify raster, frame rate, pixel format, audio channels/sample rate, loudness, and true peak.
- Treat black/freeze/silence detection as triage. This episode’s dark detections were intentional 0.8-second section cards; two roughly 1.2-second quiet ranges were deliberate pacing.
- Inspect one representative presenter frame from every environment and motion samples around hair, hands, and gesture extremes. A still can hide edge chatter.
- Recheck every reuse of a generated clip after repairing a local defect.
- Preserve and hash the previously approved master before creating a new version. Deliver to a new path and compare checksums when copying or hard-linking the final.

## Palmier-to-Resolve boundary

- This production finished in Resolve. Do not move a Resolve-authorized edit to Palmier because an operation is inconvenient.
- For Palmier rough cuts, export structure early and hand original media plus retake/marker decisions to Resolve. Do not bake environment composites, grades, active-word captions, music automation, or section-card timing into an interchange expected to preserve them.
- After conform, verify original A-roll and exact record timing before building the full-length composite replacement or any downstream finish.
