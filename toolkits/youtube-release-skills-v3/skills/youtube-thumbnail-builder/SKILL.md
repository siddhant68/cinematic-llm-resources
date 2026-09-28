---
name: youtube-thumbnail-builder
description: Design, build, and validate high-quality YouTube thumbnail candidates for long-form tutorial videos. Use when turning an approved title-and-thumbnail strategy into up to three actual 16:9 thumbnail files from video frames, owned portraits, screenshots, cleared assets, or approved generated elements; when extracting sharp source frames; when composing typography and cutouts; when producing mobile-size review boards; or when preparing an API-safe thumbnail under 2 MB. Pair every thumbnail with a specific title promise and do not upload or publish the video.
---

# YouTube Thumbnail Builder

Build actual thumbnail assets only after `youtube-release-director` has defined the viewer promise and approved up to three materially different title/thumbnail concepts.

## Required inputs

- final or near-final video master
- packaging brief or `release-package/review/title-thumbnail-rationale.md`
- up to three approved title candidates
- user-owned portraits, cutouts, screenshots, output images, or exact frame timecodes
- channel visual references and font preferences when available
- rights/provenance for every external or generated element
- dedicated thumbnail-generation budget and approval state

Never synthesize the creator's face when a real frame or owned portrait can communicate the idea. Do not use an invented likeness, fabricated result, fake interface state, or proof absent from the video.

## Outputs

```text
release-package/
  thumbnails/
    sources/
    thumbnail-a-master.png
    thumbnail-a-upload.jpg
    thumbnail-b-master.png
    thumbnail-b-upload.jpg
    thumbnail-c-master.png
    thumbnail-c-upload.jpg
    thumbnail-review-board.jpg
  review/
    thumbnail-plan.json
    thumbnail-rationale.md
    thumbnail-validation.json
```

Create only the number of candidates the release plan requires. Do not force three weak variants.

## Workflow

### 1. Lock the pair, not the image alone

For each candidate, state:

- intended viewer
- traffic context: search-led, browse-led, subscriber-led, or mixed
- title
- thumbnail idea
- what the image adds that the title does not repeat
- factual proof in the video
- likely misunderstanding to avoid

Reject a concept when the title and image make different promises.

### 2. Choose a distinct concept family

Prefer materially different tests such as:

- **Outcome/proof:** show the finished result or a strong before/after.
- **Problem/tension:** show the failure, contrast, or obstacle the tutorial resolves.
- **System/process:** show the distinctive workflow, architecture, or transformation.

Changing only text color, facial expression, or border treatment is not a meaningful A/B variant.

### 3. Source images in this order

1. sharp frame from the finished video
2. owned portrait or product/result image
3. owned screenshot or designed composite
4. cleared external asset
5. approved generated element

Use `scripts/extract_thumbnail_frames.py` for exact timecodes. Inspect motion blur, eye direction, hand shape, interface state, and compression before choosing a frame.

When paid generation is permitted, first produce the final prompt, model, resolution, number of outputs, exact current credit estimate, and maximum attempts. Stop at the configured cap. Record model, job ID, references, cost, and license/provenance.

### 4. Compose for small-size recognition

Read `references/thumbnail-strategy.md` and `references/layout-and-export.md`.

Use these defaults unless the concept justifies otherwise:

- one dominant subject or result
- one secondary supporting element at most
- zero to four words of thumbnail text
- title and image should complement rather than duplicate each other
- a clear focal hierarchy visible at 320x180 and 160x90
- no important subject, text, or UI detail against the outer crop edge
- no tiny collage, paragraph, or full-screen screenshot
- preserve truthful skin, product, and result appearance

Typography must be manually line-broken and optically placed. Do not accept a layout merely because text technically fits.

### 5. Build deterministic composites

Create one JSON layout per candidate and run:

```bash
python scripts/build_thumbnail.py \
  --layout release-package/review/thumbnail-a-layout.json \
  --master release-package/thumbnails/thumbnail-a-master.png \
  --upload release-package/thumbnails/thumbnail-a-upload.jpg
```

The layout script supports backgrounds, image layers, rectangles, gradients, and stroked text. Use an owned or licensed font path. When no font is supplied, the script attempts a common system sans font and reports what it used.

Keep a lossless master. Create a separate JPEG or PNG upload derivative under 2 MB for the YouTube Data API.

### 6. Validate visually and technically

Run:

```bash
python scripts/validate_thumbnail.py \
  release-package/thumbnails/thumbnail-a-upload.jpg \
  --report release-package/review/thumbnail-a-validation.json \
  --preview-dir release-package/thumbnails/previews
```

Then compare all candidates in one review board at:

- full resolution
- 320x180
- 160x90
- grayscale
- title shown beside the thumbnail

Reject candidates with unreadable text, weak subject separation, deceptive emphasis, awkward cutout edges, face distortion, UI clutter, or a promise not delivered in the first part of the video.

### 7. Handoff

Provide the approved upload files and rationale to `youtube-release-director`. The release manifest should identify:

- primary thumbnail
- A/B variants
- paired title for each variant
- source/provenance files
- mobile review status
- generation spend when applicable

## Non-negotiable rules

- Never fabricate a result, testimonial, interface state, or emotional reaction.
- Never use copyrighted images without a recorded license or permission.
- Never hide generated-element provenance.
- Never put more information in the thumbnail than a viewer can parse at phone size.
- Never replace the creator's real face with an AI likeness without explicit approval and a supplied reference.
- Never overwrite lossless masters while compressing upload derivatives.
- Never claim a thumbnail will make a video succeed; optimize for an honest, comprehensible click decision.
