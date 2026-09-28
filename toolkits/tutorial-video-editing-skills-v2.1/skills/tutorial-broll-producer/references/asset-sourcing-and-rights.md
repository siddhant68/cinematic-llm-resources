# Asset sourcing and rights

## Preferred sources

Start with official asset pages from:

- Pexels
- Pixabay
- Mixkit
- government or institutional public-domain collections
- YouTube Audio Library for music and SFX

This list is a starting point, not an automatic approval list. Check the current asset-specific license at download time.

## Required rights ledger fields

```text
asset_id
local_path
asset_type
source_page_url
direct_download_url
creator
license_name
license_url
license_checked_at
commercial_use
modification_allowed
attribution_required
attribution_text
people_or_property_release_notes
trademark_or_logo_notes
embedded_audio_status
restrictions
local_sha256
approval_status
```

## Approval levels

- `verified`: exact license reviewed and use appears permitted
- `conditional`: use depends on attribution, release, crop, mute, or another action
- `unresolved`: insufficient information; do not use
- `rejected`: rights or relevance problem

## What a platform license does not automatically solve

Check separately for:

- recognizable people and model releases
- private property and artwork
- trademarks, product interfaces, and logos
- music embedded in a stock video
- false endorsement or sensitive use
- editorial-only restrictions
- attribution wording

## Download policy

- Download from the asset's official page or authorized CDN.
- Do not scrape a search-engine preview.
- Keep the source page URL even when the direct media URL expires.
- Save the license page or a text receipt when permitted.
- Compute SHA-256 after download.
- Do not overwrite an existing file with different bytes without review.
- Keep unapproved candidates in `assets/quarantine/`.

## User-owned assets

Mark an asset `owned` only when the user created it or has rights to use it. Record third-party content visible or audible inside it. Ownership of a recording does not automatically clear music, artwork, brands, or other people's footage embedded in the recording.
