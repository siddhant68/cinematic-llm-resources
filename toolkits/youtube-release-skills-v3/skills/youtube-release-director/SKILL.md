---
name: youtube-release-director
description: Create and validate the complete YouTube packaging and release package for a finished long-form tutorial. Use when turning the final edit, script, channel context, and audience promise into title candidates, title-thumbnail pairs, thumbnail briefs, description, chapters, captions, tags, playlist placement, pinned-comment copy, community-post copy, cards, end-screen plan, A/B test variants, disclosures, rights records, schedule, or release_manifest.json. Coordinate youtube-thumbnail-builder, youtube-api-publisher, youtube-studio-finisher, and youtube-launch-optimizer; do not publish without an approved release gate.
---

# YouTube Release Director

Own one authoritative package from final edit to launch handoff. This is not only an upload-preparation task. Build a truthful click promise, preserve the video's structure, and create the metadata and continuation path that help the right viewer choose and continue watching.

## Required inputs

- QC-passed final master and exact duration
- final script/transcript, captions, and chapter timecodes
- target viewer, problem, and one-sentence outcome
- channel positioning, tone, existing playlists, and relevant prior videos
- opening 30-60 seconds and final call to action
- thumbnail source frames, portraits, screenshots, and result images
- rights and provenance ledgers from editing
- intended visibility, timezone, and release constraints
- made-for-kids, paid-promotion, and altered/synthetic-media decisions
- separate thumbnail-generation budget
- channel Analytics context when accessible: search terms, returning viewers, top recent videos, and audience activity

Block final approval when the master is provisional, production rights are unresolved, or the package promises a result the video does not deliver.

## Required output

```text
release-package/
  release_manifest.json
  packaging_plan.json
  description.txt
  release_notes.md
  captions/en.srt
  thumbnails/
    thumbnail-a-upload.jpg
    thumbnail-b-upload.jpg
    thumbnail-c-upload.jpg
  review/
    title-candidates.md
    title-thumbnail-rationale.md
    thumbnail-plan.json
    pinned-comment.txt
    community-post.txt
    studio-finish-plan.md
    launch-monitoring-plan.md
  production_provenance/
    rights_ledger.csv
    visual_download_receipts.json
    audio_rights_manifest.json
    audio_download_receipts.json
    generated_assets_log.json
    thumbnail_generation_spend.json
```

Only reference files that exist. Run the manifest and caption validators before handoff.

## Workflow

### 1. Reconcile the actual final video

Verify:

- master path, duration, resolution, frame rate, and audio
- exact opening promise and first proof
- visible section names and chapter boundaries
- final CTA and end-screen-safe final 5-20 seconds
- no open blocker or major QC issue

Use the rendered video, not an outdated script, as the source of truth.

### 2. Define the packaging brief

Write:

- target viewer
- current pain or desired outcome
- credible transformation
- strongest proof in the video
- primary discovery mode: search, browse, suggested, subscriber, or mixed
- why this video is distinct
- what the first 30 seconds deliver
- logical next video or playlist

Do not begin thumbnail generation until this brief is stable.

### 3. Develop titles systematically

Read `references/title-description-comment-playbook.md`.

Generate a broad internal list, then shortlist up to three materially different candidates:

- **Search-led:** clear topic and outcome using language the intended viewer is likely to use.
- **Browse-led:** understandable tension, curiosity, or transformation without vagueness.
- **Proof-led:** foreground a concrete result, experiment, or failure-to-solution journey.

Score candidates on clarity, specificity, credibility, audience fit, first-minute alignment, and truncation risk. Keep the important words early. Avoid episode numbers and channel branding at the front unless they are essential.

Tags are secondary. Use a small, relevant set mainly for context, alternate phrasing, product names, and common misspellings. Never stuff tags into the description.

### 4. Develop title and thumbnail as pairs

For each shortlisted title, specify:

- thumbnail concept
- focal subject/result
- optional zero-to-four-word thumbnail text
- evidence source and exact frame/asset
- emotion or tension, when genuine
- what the image adds beyond the title
- misleading interpretations to avoid

Pass approved concepts to `youtube-thumbnail-builder`. Prefer real frames and owned assets before generated elements. Use Higgsfield only after approving the concept and current exact cost.

Do not treat color changes as separate A/B concepts. Candidate differences should test different viewer hypotheses.

### 5. Write the description

Use this order:

1. two or three opening lines that continue the title promise
2. concise statement of what the viewer will learn or see
3. relevant resource or promised download
4. final manual chapters
5. next video or playlist
6. creator/channel context
7. required credits, affiliate disclosure, and generated-media disclosure
8. no more than a few directly relevant hashtags when useful

Use a unique description. Include one or two important topic phrases naturally in the title and opening description, but do not keyword-stuff or repeat the title mechanically.

### 6. Build chapters and captions from the final master

Manual chapters must begin at `00:00`, contain at least three ascending entries, and give every chapter at least 10 seconds. Match the visible section structure so the viewer can reconstruct the tutorial.

Correct caption timing, names, acronyms, code, and technical terms after the final edit. Never upload a pre-edit transcript as final captions.

### 7. Write the pinned comment

Create one approved top-level comment with a clear job:

- deliver the promised skill file or resource
- ask a specific experience-based question
- clarify an important nuance or correction
- link to the logical next video or playlist

Do not copy the description or ask for empty engagement. The comment may be posted by the API when explicitly allowed, but pinning must be verified in YouTube Studio after comments are available.

### 8. Plan continuation and launch support

Specify:

- playlist placement
- end screen target and layout
- card timecodes and purpose, only where relevant
- optional community post with a distinct insight, image, poll, or question
- subscriber-notification choice
- schedule based on channel strategy and audience data when available, not a generic “best time” claim
- public, unlisted, or scheduled release flow
- 24-hour, 72-hour, and 7-day analytics checkpoints

### 9. Decide A/B variants

When eligible, prepare up to three title and/or thumbnail variants for YouTube Studio's native concurrent test. Every variant must be honest and materially distinct. Do not select a candidate solely for expected CTR; the native test evaluates watch-time performance.

Record whether the video is eligible. Private, Made for Kids, mature, Shorts, scheduled live, and some Premiere states may be ineligible for the test.

### 10. Reconcile rights and disclosures

For every stock, music, SFX, generated, and thumbnail asset, confirm source, creator/model, license, attribution, commercial-use status, restrictions, local hash, and final time range or thumbnail usage.

Make an explicit altered/synthetic-media disclosure decision from current policy and actual content. Do not assume all AI-assisted assets require the same answer.

### 11. Validate and gate

Run:

```bash
python scripts/validate_release_manifest.py release-package/release_manifest.json
python scripts/validate_captions.py release-package/captions/en.srt --video-duration FINAL_DURATION_SECONDS
```

Block handoff when any of these remain unresolved:

- final master or QC status
- title/opening mismatch
- thumbnail not built or not reviewed at phone size
- title/thumbnail candidates not meaningfully distinct
- chapters or captions out of sync
- broken links or missing promised resource
- unresolved rights or disclosure
- unapproved paid generation spend
- ambiguous visibility, schedule, or subscriber notification
- pinned comment, continuation path, or launch plan missing

## Handoff sequence

1. Send approved thumbnail concepts to `youtube-thumbnail-builder`.
2. Validate the completed release package.
3. Send the manifest to `youtube-api-publisher` for private-first upload.
4. Send the video ID and Studio plan to `youtube-studio-finisher`.
5. After publication, send analytics snapshots to `youtube-launch-optimizer`.

## Non-negotiable rules

- Never promise virality or guaranteed growth.
- Never create packaging that the opening does not pay off.
- Never publish before rights, captions, and disclosures pass.
- Never use thumbnail-generation credits without the dedicated approval and cap.
- Never rely on tags as the primary discovery strategy.
- Never treat a successful API upload as a completed release.
