# First-time YouTube API and Studio setup

This guide is for the fresh AI-agent session. Perform routine setup yourself. Ask the user only for login/2FA, OAuth consent, channel-owner judgments, or information you are not authorized to invent.

## Goal

Establish a verified private-first path that can:

- upload the final master
- set supported metadata
- upload one primary thumbnail
- upload captions
- add the video to playlists
- read the video back
- finish cards, end screen, A/B testing, comment pinning, and publication in YouTube Studio

## 1. Verify the channel and feature access

1. Open YouTube Studio in the authorized account.
2. Record the channel name, handle, and channel ID.
3. Confirm custom thumbnails are available.
4. Confirm advanced features are enabled or begin the official enablement process. Advanced features are needed for functions such as native title/thumbnail testing and pinned comments.
5. Record whether the channel is in the YouTube Partner Programme and whether monetization controls are available.
6. Do not change channel-wide defaults without documenting the change.

If login, 2FA, identity verification, or channel selection is required, pause only for that exact step and resume immediately afterward.

## 2. Create or reuse a Google Cloud project

1. Use an existing user-approved project when available; otherwise create a dedicated project for this publishing workflow.
2. Enable **YouTube Data API v3**.
3. Configure the OAuth consent screen for the intended use.
4. Create an OAuth client of type **Desktop app**.
5. Download the client secret JSON into the local `secure/` directory, not the skill folder.
6. Never print, commit, or package the client secret or OAuth refresh token.

Official YouTube documentation states that uploads from unverified API projects created after July 28, 2020 can be restricted to private viewing until the project completes the required compliance audit. This workflow uploads privately first regardless.

## 3. Install publisher dependencies

From the `youtube-api-publisher` skill directory:

```bash
python -m pip install -r assets/requirements.txt
```

Keep the token path outside the skill:

```text
secure/client_secret.json
secure/youtube_token.json
```

## 4. Validate the release package

Before authentication or upload:

```bash
python skills/youtube-release-director/scripts/validate_release_manifest.py \
  release-package/release_manifest.json

python skills/youtube-release-director/scripts/validate_captions.py \
  release-package/captions/en.srt \
  --video-duration FINAL_DURATION_SECONDS
```

The primary API thumbnail must be JPEG or PNG and no larger than 2 MB. Keep a separate lossless master.

## 5. Run a dry run

```bash
python skills/youtube-api-publisher/scripts/youtube_upload.py \
  release-package/release_manifest.json \
  --client-secrets secure/client_secret.json \
  --token secure/youtube_token.json \
  --state release-package/upload_state.json \
  --dry-run
```

Review title, privacy, schedule, video path, thumbnail, captions, playlists, subscriber notification, and Studio-only tasks.

## 6. Authorize and upload privately

After `release_gate.private_upload_approved` is true and all packaging-readiness fields pass:

```bash
python skills/youtube-api-publisher/scripts/youtube_upload.py \
  release-package/release_manifest.json \
  --client-secrets secure/client_secret.json \
  --token secure/youtube_token.json \
  --state release-package/upload_state.json
```

Complete OAuth consent in the intended channel account. Verify the returned video ID and readback. Do not upload a duplicate when the command is interrupted; inspect `upload_state.json` first.

## 7. Finish in Studio

Keep the video private while checking:

- HD processing
- copyright and restrictions
- monetization/ad suitability
- title, description, chapters, captions, thumbnail, playlist, and disclosures
- cards and end screen
- title/thumbnail A/B test eligibility and variants
- mobile/desktop/TV presentation

A top-level comment can be created through the API, but pinning is a Studio/watch-page action. Comments are not available on private videos, so post and visibly pin the approved comment after the video becomes comment-eligible according to the release plan.

## 8. Publish only with explicit approval

Do not schedule, set unlisted, or publish until `public_release_approved` and `release_gate.publish_approved` are true. After the visibility change, reopen the viewer-facing page and verify all visible elements. Then create the `studio_release_record.md`.

## 9. Prepare launch review

Save the exact publish time and initial variant state. Create analytics review placeholders for 24 hours, 72 hours, and 7 days. Do not promise background monitoring unless the environment supports a scheduled task; otherwise provide a restart prompt for the next analytics review.

## Official references reviewed for this pack

- YouTube Data API `videos.insert`
- YouTube Data API `thumbnails.set`
- YouTube Data API comments and comment threads
- YouTube Help: custom thumbnails
- YouTube Help: A/B test titles and thumbnails
- YouTube Help: video chapters
- YouTube Help: end screens and info cards
- YouTube Help: pinned comments
