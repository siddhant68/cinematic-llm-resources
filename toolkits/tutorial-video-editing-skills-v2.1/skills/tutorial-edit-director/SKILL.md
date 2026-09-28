---
name: tutorial-edit-director
description: Orchestrate a professional long-form tutorial edit from front-camera A-roll, side or desk camera, screen recording, production audio, user-owned B-roll, full script, teleprompter script, and optional transcript. Use when an agent must inventory sources, preserve original quality, remove repeated takes, build a coherent dialogue spine, define sections and retention payoffs, plan J/L cuts and view changes, create edit_blueprint.json, coordinate B-roll, motion graphics, music, DaVinci Resolve or Palmier, and enforce planning and look-development gates before full editing.
---

# Tutorial Edit Director

Direct the explanation before directing the effects. The viewer should always know what is being claimed, what is being shown, and how the current beat advances the promise.

## Required inputs

- completed `EPISODE_BRIEF.json`
- full script and teleprompter script
- transcript with timecodes when available
- all camera, screen, microphone, background, and owned B-roll files
- target duration, resolution, frame rate, and aspect ratio
- generation and download permissions
- editor and handoff choice

Validate the brief first:

```bash
python scripts/validate_episode_brief.py EPISODE_BRIEF.json
```

Read:

- `references/editorial-pass.md`
- `references/edit-blueprint-spec.md`
- `references/retention-and-cut-logic.md`
- `references/session-proven-editorial.md` for dialogue deduplication, section-card holds, proof-to-payoff openings, and late picture-only revisions

## Required outputs

```text
planning/source_inventory.json
planning/preflight_report.md
planning/retake_decisions.json
planning/edit_blueprint.json
planning/edit_notes.md
edit/story_cut_timeline
edit/lookdev_timeline
```

Validate the blueprint:

```bash
python scripts/validate_edit_blueprint.py planning/edit_blueprint.json
```

## Orchestration order

1. Validate the episode brief.
2. Protect and inventory original sources.
3. Synchronize production audio, cameras, and screen recording.
4. Align full script, teleprompter text, transcript, and recorded takes.
5. Build one clean dialogue story cut.
6. Define sections, open questions, evidence, payoffs, and final takeaway.
7. Create the editor-neutral blueprint.
8. Run `tutorial-broll-producer`.
9. Run `tutorial-view-design`.
10. Run `tutorial-motion-graphics`.
11. Run `tutorial-audio-finish` for the audio plan.
12. Present the consolidated planning package and paid-generation estimate.
13. Build and approve a 60-90 second look-development sample.
14. Run exactly one primary editor adapter for the full build.
15. Run audio finishing and `tutorial-qc` on a rendered master.

Palmier is optional. DaVinci Resolve is the default master editor.

## 1. Protect and inspect the sources

- Treat camera originals and production audio as immutable.
- Hash or uniquely identify originals and record paths.
- Probe duration, resolution, frame rate, codec, color metadata, audio channels, and timecode.
- Mark proxy, generated, downloaded, or intermediate media explicitly.
- Never use a Palmier delivery render as the Resolve A-roll source.
- Verify sync near the beginning, middle, and end.
- Choose one production microphone as the continuous dialogue spine.
- Keep camera scratch audio muted after sync but do not delete it.

When a source is missing, corrupt, mismatched, or ambiguous, record the issue. Do not silently compensate with unrelated media.

## 2. Align performances without flattening intent

Use script and transcript alignment to detect false starts, repeated sentences, paragraph restarts, pauses, and alternate takes. The default preference is the last complete intended performance, not simply the last matching phrase.

Preserve:

- deliberate repetition used for emphasis
- natural breaths and thinking beats that support delivery
- better earlier takes when the later take is incomplete or visibly worse
- handles around uncertain edits

Mark ambiguous choices `review_required`. Use the existing retake-alignment script as evidence, not as an autonomous delete command.

## 3. Build the clean dialogue spine

Before B-roll, graphics, music, or decorative transitions:

- remove false starts and unwanted gaps
- repair dialogue edits with room tone and short crossfades
- use alternate camera views only when they hide a necessary cut or improve meaning
- preserve natural sentence rhythm
- keep the host visible for trust, reaction, important claims, and interpretation
- leave enough space for the viewer to absorb demonstrations and results

A clean story cut should work as audio with simple camera coverage.

After every ripple edit or take replacement, audit the new splice in context. Recheck nearby transcript words for duplicated or dropped phrases, listen across the cut, and inspect the picture sequence. A technically closed gap can still create repeated speech or an exposed one-second A-roll flash.

## 4. Build section and retention architecture

For each section, define:

- viewer question at entry
- promise or tension
- evidence or demonstration
- one to three memory anchors
- payoff
- bridge to the next section

For the opening, show credible proof or tension early, then state the promise. For the ending, restate the section sequence and final operating rule without adding a new argument.

When the episode has one central workflow claim, state it near the opening and return to it in the closing. The repeated thesis should explain what the workflow accomplished; it should not be a generic brand reminder.

Do not mechanically create a hook on every cut. Instead, ensure each edit point carries one useful continuity or curiosity bridge:

- speech or room tone continuing across the cut
- picture arriving before the spoken label
- motion, gaze, shape, or screen geography matching
- a question waiting for proof
- proof replacing verbal explanation
- contrast between before and after
- progress through a named section
- a payoff to an earlier setup

Use a hard cut when it already communicates the change.

## 5. Create the blueprint

The blueprint separates editorial intent from editor commands. Every beat must record:

- linked section and time range
- spoken idea and narrative function
- visual purpose
- primary view and source candidates
- host visibility
- transition type and reason
- retention device or continuity bridge
- optional B-roll, screen focus, text, graphic, music, and SFX references
- confidence and review requirement

Do not let editor limitations alter the story plan. Adapt execution later.

## 6. Run the specialist plans

### B-roll

Require exact placement, owned-media mapping, legal-source receipts, generation gaps, paste-ready prompts, texture treatment, and current credit estimate.

### View and compositing

Choose FACE, DESK, SCREEN, BROLL, HOST_OVER_CONTENT, COMPARE, GRAPHIC, or HOLD based on the information role. Use mask-first presenter isolation when chroma keying has failed.

### Motion graphics

Plan section openers, memory anchors, steps, screen callouts, comparisons, and the final section-header recap.

### Audio

Plan silence, room tone, music states, ducking, transitions, natural sound, and event-linked SFX. Resolve rights before download or use.

## 7. Planning gate

Before any paid Higgsfield generation or full-timeline styling, show one consolidated report containing:

- source and retake findings
- section/retention map
- complete B-roll ideation and exact placements
- licensed-source shortlist and rights status
- LTX/Higgsfield prompts and projected credits
- view and green-screen plan
- typography and motion-graphics plan
- music/SFX direction
- proposed look-development range

A missing approval does not prevent planning. It prevents paid generation and full-scale execution.

## 8. Look-development gate

Build 60-90 seconds that contains all major modes:

- front camera
- side/desk camera
- readable screen
- B-roll
- host over content
- mask-first background replacement
- section text and one motion graphic
- captions
- music automation and one motivated SFX
- a section transition

Review desktop and phone-size playback. Revise the grammar before duplicating it through the episode.

## 9. Full build and verification

- Work one section at a time.
- Inspect, plan, apply, read back, and render representative frames.
- Preserve source handles and reversible decisions.
- Use the approved grammar rather than inventing new effects late.
- Run QC on the rendered output, not just the timeline.

## Non-negotiable rules

- No source-original modification.
- No paid generation before the plan and estimate are shown.
- No unlicensed download or unknown model-weight license.
- No effect without a communication purpose.
- No fixed view-switch cadence.
- No whoosh on every cut.
- No full-episode styling before look-development review.
- No success claim without timeline readback and rendered evidence.
