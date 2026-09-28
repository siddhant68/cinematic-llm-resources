# Official API boundaries

Reviewed against official YouTube Data API documentation on 2026-09-12.

## Supported by this publisher

`videos.insert` can upload video media and set writable fields including title, description, tags, category, default language, privacy, publish time, made-for-kids declaration, altered/synthetic-media disclosure, embeddability, and public-statistics visibility.

The API also exposes:

- `thumbnails.set` for one primary custom thumbnail
- `captions.insert`
- `playlistItems.insert`
- `commentThreads.insert` for a top-level comment
- `videos.list` for readback

The current thumbnail upload endpoint has a 2 MB media limit. Keep a lossless thumbnail master and provide a separate API-safe upload derivative.

## Studio-only or not reliably covered by this publisher

Use `youtube-studio-finisher` for:

- end screens
- cards
- pinning a comment
- native title and thumbnail A/B tests
- monetization and ad-suitability review
- copyright/checks UI decisions
- final device and watch-page review
- community posts

A top-level comment can be created through the API, but private videos do not provide a normal comment surface. The default private-first workflow therefore posts and pins the approved comment after the video becomes comment-eligible.

## Project restrictions

Official documentation states that videos uploaded through unverified API projects created after 2020-07-28 are restricted to private viewing until the project passes a compliance audit. The script remains private-first even for verified projects.

## Quota

Current documentation uses a separate daily Video Uploads bucket for `videos.insert` and ordinary units for supporting actions such as thumbnail, caption, playlist, and comment operations. Inspect the current Google Cloud quota dashboard and API errors rather than hard-coding retries for quota exhaustion.
