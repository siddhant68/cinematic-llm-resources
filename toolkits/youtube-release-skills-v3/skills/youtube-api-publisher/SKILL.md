---
name: youtube-api-publisher
description: Upload an approved YouTube tutorial release package through the official YouTube Data API v3 using OAuth and resumable media upload. Use when publishing a final master from release_manifest.json, setting supported snippet and status metadata, uploading the primary thumbnail and checked caption tracks, adding the video to playlists, optionally creating a top-level comment only when the video is already comment-eligible, and reading the uploaded resource back. Default to private, require explicit flags for scheduling or non-private visibility, and never automate unsupported Studio features with brittle browser selectors.
---

# YouTube API Publisher

Publish only an approved release package from `youtube-release-director`. This skill handles supported Data API operations; it does not configure end screens, cards, comment pinning, monetization, or Studio A/B tests.

## Before first use

Read:

- `references/oauth-setup.md`
- `references/api-boundaries.md`
- `references/recovery-and-readback.md`

Install dependencies:

```bash
python -m pip install -r assets/requirements.txt
```

Create a Google Cloud OAuth Desktop client, enable YouTube Data API v3, and download the client secret JSON. Keep client secrets and OAuth tokens outside the skill folder and source control.

## Required inputs

- approved `release_manifest.json`
- existing master, description, thumbnail, and caption files referenced by the manifest
- OAuth desktop client secrets
- operator approval of the channel account shown during OAuth

Run the release manifest validator before uploading.

## Safe default workflow

### 1. Dry-run

```bash
python scripts/youtube_upload.py release-package/release_manifest.json \
  --client-secrets /secure/client_secret.json \
  --token /secure/youtube_token.json \
  --state release-package/upload_state.json \
  --dry-run
```

Review the exact title, privacy, schedule, files, playlist IDs, subscriber-notification setting, and API actions.

### 2. Private upload

```bash
python scripts/youtube_upload.py release-package/release_manifest.json \
  --client-secrets /secure/client_secret.json \
  --token /secure/youtube_token.json \
  --state release-package/upload_state.json
```

The default path requires all packaging-readiness checks plus `release_gate.private_upload_approved: true`. It does not require `publish_approved` for a private upload, and it refuses immediate public, unlisted, or scheduled release without the separate publication approval and explicit flags.

### 3. Resume post-upload steps

If the media upload succeeded but a thumbnail, caption, playlist, or readback step failed, rerun with the recorded video ID:

```bash
python scripts/youtube_upload.py release-package/release_manifest.json \
  --client-secrets /secure/client_secret.json \
  --token /secure/youtube_token.json \
  --state release-package/upload_state.json \
  --resume-video-id VIDEO_ID
```

This resumes from an existing video resource; it does not pretend to serialize an interrupted upload session across processes.

### 4. Handoff to Studio

Pass the returned video ID and manifest to `youtube-studio-finisher`. Keep the video private until checks, end screen, cards, A/B test, and final watch-page review are complete.

## Explicit safety flags

- `--allow-unapproved`: bypass packaging and upload approvals for a deliberate local/API test; never use it for a normal release
- `--allow-nonprivate`: permit an immediate `public` or `unlisted` API state
- `--allow-schedule`: permit a future `publish_at` schedule
- `--post-comment`: allow the optional top-level comment only when the video is already unlisted/public and comment-eligible; private-first releases normally defer this to Studio
- `--skip-assets`: skip thumbnail, captions, playlists, and comment
- `--allow-state-mismatch`: deliberately reuse a state path whose stored manifest fingerprint differs; otherwise use a new state file

Use these only when the dry-run clearly shows the intended operation.

## API behavior

The uploader:

1. resolves paths relative to the manifest
2. loads the checked description text
3. validates release state and files
4. authorizes with OAuth
5. uploads with a resumable request and bounded exponential backoff
6. records the video ID and completed steps in a state file
7. uploads the primary thumbnail
8. uploads declared caption tracks
9. inserts the video into declared playlists
10. optionally creates one top-level comment when the release state permits comments
11. reads back snippet, status, content, and processing information

Do not report success until readback returns the expected video ID and metadata.

## Non-negotiable rules

- Never embed OAuth secrets or refresh tokens in a skill or repository.
- Never default to public.
- Never use browser selectors as a silent fallback.
- Never claim end screens, cards, pinning, A/B testing, or monetization were completed through this script.
- Never rerun a failed full upload without first checking whether a video ID was already created.
- Never upload captions generated before the final edit without review.
- Never expect comment creation or pinning to work while the video remains private; defer the approved pinned comment to `youtube-studio-finisher`.
