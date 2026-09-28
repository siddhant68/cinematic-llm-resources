---
name: youtube-studio-finisher
description: Complete, verify, and document all YouTube Studio work remaining after a private-first upload. Use when checking HD processing, copyright and restrictions, monetization, captions, chapters, playlists, cards, end screens, title-and-thumbnail A/B tests, pinned comments, community-post support, mobile/desktop/TV presentation, scheduling, or final publication. Use available logged-in browser or desktop automation with visual readback; require the approved release manifest and explicit publish approval, and never claim Studio-only work succeeded without checking the visible result.
---

# YouTube Studio Finisher

Finish the private-first upload in the correct YouTube channel. The Data API upload is only a transport step; the release is incomplete until Studio-only configuration and watch-page review pass.

## Required inputs

- uploaded video ID
- approved `release_manifest.json`
- final master, captions, thumbnails, description, and release notes
- title/thumbnail A/B candidates
- approved pinned comment and optional community-post copy
- operator access to the intended YouTube channel
- explicit `release_gate.publish_approved: true` before scheduling or publishing

## Output

Produce `studio_release_record.md` with:

- channel identity and video ID
- processing, copyright, restrictions, and monetization status
- exact title, description, thumbnail, playlist, and disclosures
- captions and chapters status
- cards and end screen
- A/B test mode and variants
- top-level comment and pinning status
- optional community post status
- desktop, mobile, and TV review notes
- final visibility, date, time, and timezone
- unresolved issues and manual steps

Use `assets/studio_release_record.template.md`.

## Automation boundary

Use browser/desktop automation when available and already authorized. Read the page after each change and capture enough evidence to verify success. Do not rely on brittle selectors without visual/state confirmation.

Pause only for genuinely unavailable account access, login/2FA, required consent, monetization self-certification that needs the owner's judgment, or an explicit publish approval missing from the manifest. Do not claim completion when the session cannot access Studio.

## Workflow

### 1. Identity and processing gate

Open the exact video and verify:

- channel identity
- video ID
- title
- duration
- primary thumbnail
- standard and HD processing

Review copyright, restrictions, and policy notices. Stop on an unresolved block or duplicate upload.

### 2. Details and disclosures

Compare Studio with the manifest:

- title and description
- chapters
- primary thumbnail
- playlist
- language and category
- audience setting
- paid-promotion declaration when relevant
- altered/synthetic-media disclosure when relevant
- recording date/location only when intentionally supplied

Do not make unrecorded metadata changes. Update the release record and manifest when a correction is necessary.

### 3. Captions and chapters

Inspect:

- hook and first minute
- names, acronyms, code, and product names
- every chapter boundary
- fast cuts and pauses
- final CTA

Confirm manual chapters begin at `00:00`, are visible on the watch page, and match the final video's section structure.

### 4. Monetization, checks, and restrictions

Complete required checks and ad-suitability declarations truthfully. Record the result shown by Studio. Do not infer a clean status merely because another screen lacks a warning.

### 5. Cards

Add only planned cards with a clear purpose. A card should answer a question or provide the logical next resource after the viewer has enough context to care. Avoid placing it over dense instruction.

Record timecode, target, and purpose. Do not exceed current platform limits.

### 6. End screen

Use the final 5-20 seconds of an eligible video. Prefer a simple continuation layout:

- one next video or playlist
- one subscribe element

Ensure elements do not cover the presenter, captions, key proof, or CTA. Preview the actual watch-page overlay.

### 7. Native title/thumbnail A/B test

When eligible, configure the approved mode:

- title only
- thumbnail only
- title and thumbnail

Use two or three materially different variants. Do not start with misleading candidates. YouTube's native test uses watch-time performance, so record the variants and allow the experiment to run rather than judging only by CTR.

The feature is currently desktop-only and unavailable for some states and content types, including private videos, Made for Kids content, mature content, Shorts, and certain live/Premiere cases. A new-upload test may be configured before release but begins only when the video becomes eligible and published.

### 8. Comment and pinning

Post the approved top-level comment via API or watch page. Pin it manually in Studio/watch page and verify the visible pin.

Comments are unavailable on private videos. When the video remains private until a scheduled release, complete pinning immediately after publication or use an approved unlisted review state if appropriate. Do not switch privacy merely to pin without the release plan authorizing it.

The pinned comment should deliver a resource, ask a specific question, clarify something important, or lead to the next relevant video. Do not duplicate the description.

### 9. Optional community post

When enabled and the channel is eligible, create or schedule the approved post. Use a distinct visual, poll, failure lesson, or discussion prompt rather than copying the title and link.

### 10. Watch-page review

Review the private, unlisted, scheduled, or public page on:

- desktop
- mobile portrait and landscape
- television or large-screen preview when practical

Check title truncation, thumbnail crop, description opening, chapters, captions, links, HD processing, audio, disclosures, cards, and end screen. Scrub the opening, every chapter boundary, and final 30 seconds.

### 11. Release

Schedule or publish only when:

- all release-gate fields are true
- checks and rights are clean
- title/thumbnail package is approved
- captions and chapters are correct
- end screen and continuation path are ready
- exact date, time, and timezone are confirmed

After the visibility change, reopen the viewer-facing page and verify the state. Complete the comment pinning and any public-only A/B/community tasks. Then hand the video ID and release record to `youtube-launch-optimizer`.

## Rules

- Keep the upload private until the release gate passes.
- Never treat an API upload as a completed release.
- Never publish without explicit approval in the release manifest.
- Never claim a comment is pinned without viewing the pinned state.
- Never claim an A/B test started while the video is ineligible.
- Never add cards or end screens simply because slots exist.
- Never publish with unresolved captions, rights, disclosures, checks, or restrictions.
