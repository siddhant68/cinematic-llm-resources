# Covers and carousel slides

The cover is an editorial choice. Watch the actual finished video, choose a moment that represents the post, extract that frame, and review it at full size before adding type. A film and its tutorial should have distinct covers while keeping the series' color and typography recognizable. The cover must remain legible when Instagram shows the centre 4:5 feed region and the smaller profile tile.

## Extract a candidate frame

```sh
ffmpeg -ss 19.5 -i /absolute/path/film.mp4 -frames:v 1 /absolute/path/release/film-rain-19.5.jpg
```

Choose the time by viewing the video, not by always taking the midpoint. Inspect the exported frame for eyes, action, lighting, blur, and space for text. Reel 008 used a rain close-up for the film and a dust/sunbeam frame for the tutorial.

## Render a feed-safe cover

Save a JSON specification beside the frame:

```json
{
  "type": "feed-safe-cover",
  "outputDir": "film-cover",
  "image": "film-rain-19.5.jpg",
  "textTop": 1110,
  "handleTop": 1570,
  "eyebrow": "THE FILM · 28 SECONDS",
  "title": "WEATHER.",
  "subtitle": "Four scenes. Four kinds of air."
}
```

```sh
node art.mjs /absolute/path/release/film-cover-art.json
```

This creates `film-cover/cover_1080x1920.png`. `feed-safe-cover` checks that the supplied text positions stay within the centre feed region. The specific image and words still require visual review, including a small profile-grid preview. Other layouts in `art.mjs` include `two-frame-cover`, `portrait-cover`, and `four-panel-cover`; select them only when their framing suits the release.

## Original-image carousel

For a portrait image, use `contain-carousel` to place the complete source inside a 1080×1350 slide. Do not let Instagram silently crop the original. A slide specification can mix image slides and optional text slides:

```json
{
  "type": "contain-carousel",
  "outputDir": "carousel",
  "slides": [
    {"image": "../resources/images/01_dust.png", "label": "01 · DUST · START FRAME"},
    {"image": "../resources/stills/01_dust_middle.png", "label": "02 · DUST · CLIP MIDDLE"},
    {"label": "THE FULL PACK", "title": "COPY THE PROMPTS", "body": "Find the link in the caption."}
  ]
}
```

The output files are `carousel/slide_01.png` and so on. Put those paths in the `slides` array of the carousel upload manifest in exactly the intended order. Verify the first, a middle, and the final rendered slide before uploading; after publishing, check at least the first and last slides on Instagram. Reel 008 used four ChatGPT start frames followed by start/middle/end stills of each clip, 16 slides total.

For a video carousel, `prepare_video_carousel.py` accepts a JSON file with `sourceVideos`, `music`, `outputDir`, and optional `musicOffsetSeconds`. It preserves each portrait source inside 4:5 and mixes the supplied music into every slide. Use music only under terms that allow the planned Instagram post and keep the source/credit record with the release.
