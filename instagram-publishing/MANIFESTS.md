# Inputs and commands

Run the commands from `instagram-publishing/scripts` after `npm ci`. The scripts need `ffprobe` on `PATH`. Paths inside a manifest resolve relative to that manifest file, so a release can stay together in its own directory.

## Reel manifest

```json
{
  "account": "cinematic_llm",
  "video": "FILM-FEED-SAFE.mp4",
  "cover": "film-cover/cover_1080x1920.png",
  "captionFile": "film-caption.txt",
  "aiLabel": true
}
```

`video` is a 9:16 MP4 between 3 and 180 seconds. `cover` is a 9:16 PNG or JPG. `captionFile` contains the exact caption, up to 2,200 characters. The account and AI label are required. The `--check` step validates those fields and reports the media dimensions and a deterministic run ID.

```sh
node upload.mjs --manifest /absolute/path/to/release/film-instagram.json --check
node upload.mjs --manifest /absolute/path/to/release/film-instagram.json --stage
node upload.mjs --manifest /absolute/path/to/release/film-instagram.json --publish
```

`--stage` opens Edge and reaches the final ready-to-share screen, then stops without sharing. The publish run uses the same inputs. A simple `--check` is usually sufficient when the UI has been stable and the media has been visually reviewed.

## Carousel manifest

```json
{
  "account": "cinematic_llm",
  "slides": ["carousel/slide_01.png", "carousel/slide_02.png"],
  "captionFile": "resources-caption.txt",
  "aiLabel": true,
  "crop": "4:5"
}
```

Use 2–20 PNG, JPG, or MP4 slides. Every slide must have the same selected ratio (`4:5` or `1:1`) and be at least 600 pixels wide. Put the slides in the manifest's display order. Music for video slides must be mixed into those files before upload; the web carousel composer has not provided an album-wide music step in this workflow.

```sh
node carousel.mjs --manifest /absolute/path/to/release/carousel-instagram.json --check
node carousel.mjs --manifest /absolute/path/to/release/carousel-instagram.json --stage
node carousel.mjs --manifest /absolute/path/to/release/carousel-instagram.json --publish
```

## Feed and profile crops

Instagram can show a centre 4:5 preview of a 9:16 Reel in the feed, even when the composer is correctly set to 9:16. A cover or text near the top/bottom may disappear there. The optional `prepare_feed_safe.py` helper places the entire original frame inside the centre 4:5 portion of a new 1080×1920 Reel with a blurred surround. It preserves the original shot but makes its details smaller. Review the output before use.

```sh
python3 prepare_feed_safe.py /absolute/path/source.mp4 /absolute/path/feed-safe.mp4
```

The separate cover should have its main title near the centre so the profile grid crop also works. For image carousels, build actual 4:5 slides, such as 1080×1350, instead of relying on Instagram to crop a portrait source. `art.mjs` renders layouts from a JSON specification; `prepare_video_carousel.py` packages vertical video clips into 4:5 slides with a supplied music file.

## State and evidence

The scripts keep local evidence in `scripts/.runs/<run-id>/`: `state.json`, UI screenshots, and page text. `published` includes the URL. `share_clicked` means the final click may have reached Instagram, so check the profile before any retry. Never delete a run record merely to force a second upload. `.profile/` and `.runs/` are ignored by Git and contain private session or account data.
