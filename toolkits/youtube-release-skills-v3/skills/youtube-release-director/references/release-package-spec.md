# Release package specification

## Core manifest

`release_manifest.json` is the operational source of truth for the API and Studio handoff. Keep creative rationale in companion files rather than stuffing it into the manifest.

Required areas:

- final video file
- metadata and description path
- privacy, schedule, audience, and disclosure state
- chapters
- primary thumbnail and A/B variants
- captions
- playlists
- optional top-level comment
- Studio-only tasks
- release gate with separate packaging, private-upload, and public-release approvals
- rights and generated-asset provenance
- thumbnail generation budget

## Creative companion files

- `packaging_plan.json`: target viewer, promise, discovery mode, title/thumbnail pairs, and next-video path
- `title-candidates.md`: broad list, scoring, shortlist, and rejection reasons
- `thumbnail-plan.json`: source assets, layouts, pairings, and spend
- `pinned-comment.txt`: approved comment copy
- `community-post.txt`: optional launch post copy
- `launch-monitoring-plan.md`: metrics, checkpoints, and decision rules

## Publishing boundary

The Data API can upload the video, metadata, one primary thumbnail, captions, playlist placement, and a top-level comment. Studio remains responsible for pinning, end screens, cards, monetization/checks, native title/thumbnail tests, and final visual review.

## Separate approval semantics

`release_gate.private_upload_approved` authorizes creating or updating the private YouTube resource after all package-readiness checks pass. `release_gate.publish_approved` independently authorizes public, unlisted, or scheduled release. A normal private-first upload should keep `publish_approved` false until Studio finishing and owner review are complete.
