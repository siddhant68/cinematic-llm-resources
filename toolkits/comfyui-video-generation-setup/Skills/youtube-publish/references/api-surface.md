# API surface

Full research and architecture: `docs/4-PUBLISH-PIPELINE-DESIGN.md`. The short
version, because it decides how the upload actually happens.

## The verification lock

> All videos uploaded via the `videos.insert` endpoint from unverified API
> projects created after 28 July 2020 will be restricted to private viewing mode.

It is a **lock, not a privacy setting** — the video cannot be made public
afterwards. It **cannot be appealed**. And there is **no privacy-status
workaround**: uploading as private and promoting later does not dodge it,
because the restriction binds at the API-project level.

A new Google Cloud project is unverified by definition. So an API-first upload
fills the channel with permanently dead videos.

**File the [audit form](https://support.google.com/youtube/contact/yt_api_form)
on day one** — it is free, and if it clears, the upload leg becomes API. Do not
block on it.

## The split

The restriction is scoped, in Google's wording, to `videos.insert` alone.

| Leg | How | Until |
|---|---|---|
| The file | Browser, via Studio | the audit clears |
| All metadata | Data API | works today, unverified |
| Pin, end screens, cards | Browser | permanently — no API exists |

**Verify before trusting:** upload one throwaway video by hand, then try
`videos.update` and `thumbnails.set` against it from an unverified project. If
those are blocked too, the metadata leg moves to the browser.

## Quota

Uploads moved to their own bucket in 2026. Guides quoting 1,600 units are two
revisions stale.

| Method | Cost |
|---|---|
| `videos.insert` | **1** — own bucket, 100 calls/day |
| `videos.update` | 50 |
| `thumbnails.set` | 50 |
| `playlistItems.insert` | 50 |
| `commentThreads.insert` | 50 |
| `captions.insert` | 400 |

A full publish is ~550 units plus one upload call. Neither ceiling binds.

## Cannot, at any quota

Pin a comment · end screens · cards · thumbnail A/B (Test & Compare) ·
community posts · channel layout. Every one of these is an engagement surface
YouTube added without an API, which is why the browser leg is permanent
infrastructure rather than a stopgap.
