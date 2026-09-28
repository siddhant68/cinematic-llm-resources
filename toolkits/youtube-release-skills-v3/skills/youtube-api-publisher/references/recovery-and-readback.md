# Recovery and readback

## Before retrying

Check `upload_state.json`. If it contains a video ID, inspect that video in YouTube Studio or run the uploader with `--resume-video-id`. Do not start another media upload simply because a later step failed.

## State file

The state file records:

- manifest path and fingerprint
- video ID
- upload timestamp
- completed post-upload steps
- final readback payload
- last error

It must not contain OAuth tokens or client secrets.

The uploader refuses to reuse a state file whose stored manifest fingerprint differs. Prefer a new state path; use `--allow-state-mismatch` only for an operator-reviewed recovery.

## Retriable failures

The script uses bounded exponential backoff for network errors and selected server or rate responses. It does not endlessly retry authentication, validation, copyright, quota exhaustion, or permission failures.

## Readback checks

After upload, compare:

- returned video ID
- title
- description prefix or hash
- privacy status
- publish time, when scheduled
- made-for-kids declaration
- synthetic-media disclosure when returned
- processing state

Readback confirms the API resource. It does not replace viewing the uploaded video, captions, thumbnail, and watch page in Studio.
