---
name: tutorial-broll-producer
description: Plan, source, download, generate, and document B-roll for long-form tutorial videos built from face camera, side camera, screen recordings, scripts, and user-owned footage. Use when an agent must decide exactly what visual belongs under each spoken beat, prioritize supplied proof footage, find commercially usable stock stills or clips, prepare LTX/ComfyUI or Higgsfield prompts, budget generation credits, choose an appropriate B-roll texture, maintain a rights ledger, or present a complete B-roll ideation package before editing or paid generation.
---

# Tutorial B-roll Producer

Treat B-roll as evidence and explanation, not wallpaper. Plan it only after the story cut and before full-timeline styling.

## Required inputs

- `EPISODE_BRIEF.json`
- `edit_blueprint.json`
- full script, teleprompter script, and final or provisional transcript
- source inventory and all user-owned B-roll
- target editor and delivery format
- allowed stock sources and commercial-use policy
- LTX/ComfyUI configuration and exact checkpoint license, when enabled
- separate Higgsfield B-roll and thumbnail credit caps

Read:

- `references/broll-planning-and-placement.md`
- `references/asset-sourcing-and-rights.md`
- `references/generation-workflow.md` when generated footage is allowed
- `references/texture-treatment-matrix.md` before assigning a look
- `references/session-proven-broll.md` when footage repeats, adjacent B-roll covers one thought, an opening proof montage is planned, or generated geometry fails locally

## Required outputs

Produce:

```text
planning/BROLL_IDEATION.md
planning/broll_plan.json
planning/generation_prompts.md
planning/higgsfield_spend_plan.json
assets/asset_manifest.json
assets/rights_ledger.csv
assets/download_receipts.json
```

Validate the plan:

```bash
python scripts/validate_broll_plan.py planning/broll_plan.json
```

Download only reviewed, verified entries:

```bash
python scripts/download_approved_assets.py assets/asset_manifest.json --dry-run
python scripts/download_approved_assets.py assets/asset_manifest.json
```

## Workflow

### 1. Decompose the spoken argument

For every section and beat, identify:

- the exact line or idea being supported
- its narrative function
- the audience question at that moment
- the visual job: evidence, demonstration, orientation, emotion, analogy, comparison, pacing breath, or payoff
- whether the viewer needs the host's face at the same time
- the ideal duration and entry/exit bridge

Do not begin by searching nouns from the script. Begin by defining the information job.

### 2. Map supplied footage first

Inspect every user-owned asset. Record:

- stable source ID and file path
- what it genuinely proves or demonstrates
- usable source ranges
- image quality and orientation
- natural sound value
- intended beat or section from the episode brief
- rights status
- conflicts, continuity, or misleading implications

Use exact result footage, failures, screen recordings, and before/after evidence before generic stock. Never ignore a supplied usage note merely because another asset is visually prettier.

### 3. Decide the best visual form

For each beat, choose one:

- `owned_broll`
- `screen_recording`
- `still_image`
- `licensed_stock_video`
- `licensed_stock_still`
- `motion_graphic`
- `generated_video`
- `generated_still`
- `host_only`
- `host_over_content`
- `intentional_hold`

A motion graphic is often more truthful than a literal stock clip for systems, steps, abstract agents, or data flow. A clean host shot is better than irrelevant B-roll.

### 4. Create a sourcing brief before searching

Write precise search concepts, not broad nouns. Include:

- visual subject and action
- camera scale and movement
- location/context
- required negative constraints
- emotional tone
- orientation and duration
- whether logos, readable UI, identifiable people, or releases are acceptable

Search only after the brief exists.

### 5. Source and verify legal candidates

Use current official license information. Preferred starting points include Pexels, Pixabay, Mixkit, and true public-domain collections. For every candidate, record the asset page, creator, exact license, license URL, attribution requirement, restrictions, and date checked.

Reject:

- search-result previews without a source page
- clips ripped from YouTube, social media, films, television, news, or another creator
- assets with unclear commercial rights
- footage whose trademarks, people, artwork, private property, or embedded audio introduce unresolved rights
- a model or checkpoint whose weights license is unknown or noncommercial

Download only when `license_status` is `verified` and `approved_for_download` is true. Save a local hash and receipt. Free does not mean rights-free.

### 6. Identify generation gaps

Generate only when owned media, screen proof, licensed stock, or a motion graphic cannot communicate the beat well enough.

For every gap, state:

- why generation is justified
- whether the result is illustrative or evidentiary
- LTX or Higgsfield choice and reason
- duration, framing, motion, lighting, continuity, and negative constraints
- reference images/video and their rights
- projected current credit cost
- number of attempts allowed
- fallback when the result fails

Never present generated illustrative footage as documentary proof.

### 7. Budget Higgsfield explicitly

Use separate budget pools:

```text
B-roll credit cap
Thumbnail credit cap
Contingency reserve
```

Query the current displayed or API estimate using the exact model, duration, resolution, and output count before submission. Record planned and actual spend per asset.

Rules:

- A zero or absent cap means prompts only.
- Reserve the configured contingency; do not plan to spend the entire cap.
- Prefer one well-specified output over an unreviewed batch.
- Do not auto-retry a charged request whose status is ambiguous.
- Stop when the per-asset attempt limit or budget would be exceeded.
- Download successful outputs immediately and record model, job ID, seed when available, inputs, and rights/provenance.

### 8. Prepare LTX/ComfyUI prompts

Use LTX for local iteration when the configured workflow and exact checkpoint license permit commercial use. Record the checkpoint and license URL. Structure prompts chronologically: opening state, primary action, camera behavior, environmental response, and ending state.

Do not assume the repository's software license also licenses the model weights.

### 9. Assign texture by information role

Use the texture matrix. Do not apply one channel-wide film effect to all B-roll.

- Keep UI and screen recordings clean and crisp.
- Keep user-owned proof natural and minimally treated.
- Use subtle filmic texture for human process or emotional atmosphere.
- Use archival treatment only for genuine or explicitly reconstructed archival material.
- Use restrained grid/line treatment for technical systems.
- Use softer hypothetical treatment for ideas or future-state illustration.
- Match generated media to neighboring shots through contrast, motion cadence, grain, sharpness, and color; do not disguise factual uncertainty.

Record the purpose and intensity in the plan.

### 10. Plan placement and transitions

Every B-roll entry needs:

- start and end relative to the spoken line
- whether picture leads audio, follows audio, or lands on a keyword/action
- host visibility decision
- crop or screen focus
- natural sound use
- texture treatment
- entry and exit bridge
- minimum readable hold

Use J-cuts, L-cuts, action matches, gaze matches, motion direction, and audio bridges. Do not insert a transition effect merely because the source changes.

When two adjacent B-roll shots support consecutive parts of the same thought, cut directly from the first B-roll to the second. Do not expose a short A-roll fragment between them unless the host's reaction or a deliberate structural reset carries meaning.

Before placing generated footage, watch the complete candidate at normal speed and reject it for semantic mismatch, unwanted production gear, watermarks, warped anatomy or text, implausible geometry, unstable motion, or a cadence that will not cut with its neighbors. A beautiful shot that does not prove the spoken claim is unusable.

When a supplied sequence is also being reserved for a separate film, use only the source ranges that precisely prove the current narration. Preserve the majority of the footage and record each chosen range so another edit can avoid accidental overuse.

### 11. Present the ideation gate

Show the user one consolidated report with:

1. B-roll timeline by section and line.
2. Supplied assets selected and rejected, with reasons.
3. Licensed candidates, local previews, and rights status.
4. Motion-graphic alternatives.
5. Generation gaps and paste-ready LTX/Higgsfield prompts.
6. Current estimated credits, contingency, and maximum attempts.
7. Texture and sound treatment.
8. Unresolved decisions and fallbacks.

Free candidates may be downloaded into quarantine. Do not spend Higgsfield credits or scale the full edit before this report is shown.

## Editorial standards

- Avoid generic noun matching.
- Avoid B-roll that contradicts the speaker or implies evidence not present.
- Avoid cutting away from an important facial reaction.
- Avoid changing visuals faster than the audience can inspect them.
- Avoid decorative texture on screen recordings.
- Avoid repeated stock shots, obvious AI loops, warped text, or branded artifacts.
- Use intentional visual holds so the episode can breathe.

## Handoff

Pass approved `broll_plan.json`, local asset paths, rights/provenance files, natural-sound notes, and generation outputs to `tutorial-view-design`, `tutorial-motion-graphics`, the selected editor builder, `tutorial-audio-finish`, and `tutorial-qc`.
