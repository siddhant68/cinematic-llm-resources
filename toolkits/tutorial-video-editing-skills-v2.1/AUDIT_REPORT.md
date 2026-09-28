# Audit and redesign report

Audit date: 2026-09-10

## Diagnosis

The earlier editing system treated polish as a checklist of transitions, zooms, captions, whooshes, and B-roll insertions. That encouraged local decoration without a single editorial model of the lesson. The redesigned bundle treats the spoken argument, viewer comprehension, and source quality as the control layer.

The most important changes are:

1. Separate story direction, B-roll production, view design, motion graphics, audio finishing, editor execution, and QC without allowing them to invent competing plans.
2. Require one shared `EPISODE_BRIEF.json`, `edit_blueprint.json`, and consolidated approval gate.
3. Define the real visual language as FACE, DESK, SCREEN, BROLL, HOST_OVER_CONTENT, COMPARE, GRAPHIC, and HOLD rather than random angle switching.
4. Use owned proof and exact screen demonstrations before stock or generated imagery.
5. Require a rights ledger and download receipt for stock, music, and SFX.
6. Treat generated footage as illustration unless it genuinely depicts a generated result; never present it as documentary proof.
7. Turn typography into an information architecture with section openers, memory anchors, comparisons, and a final recap.
8. Make hard cuts, J-cuts, L-cuts, room tone, action/gaze matches, and proof/payoff structure the default continuity tools. Effects remain optional.
9. Use mask-first presenter isolation when global chroma keying fails, with a framed-PIP fallback after two focused repair passes.
10. Preserve original A-roll through every handoff and finish from the originals in DaVinci Resolve.

## Final skill architecture

| Skill | Single responsibility |
|---|---|
| `tutorial-edit-director` | Source inventory, retake cleanup, dialogue spine, sections, retention map, edit blueprint, and orchestration gates |
| `tutorial-broll-producer` | Beat-level B-roll ideation, supplied-media mapping, licensed sourcing, downloads, LTX/Higgsfield prompts, budgets, textures, and provenance |
| `tutorial-view-design` | Camera/view choice, screen focus, host-over-content layout, PIP/cutout design, mask-first planning, captions, and visual continuity |
| `tutorial-motion-graphics` | Section system, memory anchors, step lists, comparisons, diagrams, Fusion template specification, and final recap |
| `tutorial-audio-finish` | Dialogue continuity, room tone, music/SFX sourcing, guarded downloads, tempo map, automation, Fairlight finish, and loudness review |
| `davinci-tutorial-builder` | Source-safe Resolve conform, masks, Fusion, Fairlight, color, timeline readback, renders, and final master |
| `palmier-tutorial-builder` | Optional transcript/multicam rough cut and early FCPXML handoff only by default |
| `tutorial-qc` | Editorial, structural, rights, composite, graphics, audio, source-quality, and technical render review |

## Tool decision

DaVinci Resolve Studio is the master editor and finishing environment. LTX/ComfyUI and Higgsfield generate approved visual assets. Palmier is optional for synchronization, transcript cleanup, and a structural rough cut when it saves time.

Higgsfield and Palmier are not alternatives: one generates media and the other edits. The meaningful choice is whether to edit directly in Resolve or use Palmier briefly before an early FCPXML conform.

## Source-quality correction

The earlier hybrid model risked using a Palmier export as the source for the final Resolve timeline. That is now prohibited. The transfer package must contain FCPXML, original media, source/path manifests, edit notes, production audio, and a reference movie. Resolve must relink the original camera and screen files. The reference movie is timing evidence only.

## Green-screen correction

The bundle no longer assumes a chroma key should solve every presenter shot. It segments difficult motion, tracks the presenter with person/object masks, uses positive and holdout masks, performs localized green cleanup only where useful, despills separately, and tests the matte over diagnostic backgrounds. A clean framed PIP is preferred over a visibly unstable cutout.

## Retention correction

The request for a hook at every cut has been translated into a professional rule: every edit point should preserve continuity or renew curiosity, but most cuts should not carry a visible transition effect. Valid bridges include continuous speech, a question answered by proof, a gaze/screen-focus match, an action match, natural sound, a section marker, contrast, or a delayed payoff.

## Removed or isolated material

The editing context excludes unrelated cinematic-generation, LTX-reel, generic image-generation, channel-strategy, long-form-scriptwriting, and Shorts-funnel skills. LTX is represented only as one optional generated-asset route inside the B-roll producer. YouTube publishing remains in its own bundle.
