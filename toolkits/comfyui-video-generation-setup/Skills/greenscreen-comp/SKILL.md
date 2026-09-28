---
name: greenscreen-comp
description: Key a green screen and composite the subject over a background plate so it looks like one photographed image rather than a sticker on a photo. Use whenever footage has a green or blue screen behind the subject, whenever a user mentions chroma key, keying, background replacement, despill, green spill, matte edges, or compositing a talking head over a generated or stock background — and also when a composite already exists but "looks fake", "looks pasted on", or has fringing, halos, or chattering edges.
---

# Green Screen Compositing

Most bad composites fail for one of two reasons: the matte was pulled from a
screen that couldn't support it, or the subject and plate were never made to
share a lighting environment. Both are decided before you write a filter chain.

## Step 1: Measure before you key

```bash
python scripts/analyze_key.py footage.mp4 --frames 12
```

This samples the frame edges (where the subject isn't) and reports the three
numbers that decide everything:

- **Chroma separation** — how far green sits above red and blue. A properly lit
  chroma-green cyc gives 90–140. Below 60, the screen barely differs from a green
  cast on skin, and no similarity value separates them cleanly.
- **Saturation** — a real chroma screen reads 0.7+. Below 0.5 the green has
  drifted toward grey and will fight midtones in the subject.
- **Vertical falloff** — luma difference between the top and bottom of the
  screen. Above ~30 levels, a single `similarity` cannot cover both: tune for the
  bright top and the dark bottom stays opaque; tune for the bottom and the top
  eats into hair.

**A weak measurement means "benchmark before committing", not "AI matting will
win".** A still frame cannot predict temporal stability, hair behaviour under
motion, or how a keyer performs with multiple screen samples. It tells you the
single-value FFmpeg key is unlikely to be enough — that is all. Run the A/B in
Step 2 on real motion before choosing.

## Step 2: Pick the path the measurement points to

### Path A — direct key (strong screen)

```bash
ffmpeg -i fg.mp4 -i plate.mp4 -filter_complex "
 [0:v]chromakey=0x00FF00:0.12:0.06,despill=type=green:mix=0.5:expand=0.15[fg];
 [1:v][fg]overlay=shortest=1,format=yuv420p" -c:a copy out.mp4
```

### Path B — flatten, then key (uneven lighting)

Normalise the screen's illumination so one similarity value works top to bottom.

**Do not divide the whole frame by a blurred copy of itself.** That is the
tempting one-liner and it is wrong: the blur field includes the subject, so the
division alters skin tones, amplifies noise, behaves unpredictably on
gamma-encoded footage, and produces halos around the body.

Correct approaches, in order of preference:

1. **Clean plate.** Shoot 5 seconds of the empty lit screen before or after the
   take, with the same lighting and camera settings. Divide by *that* — it
   contains only the illumination gradient, no subject. This is the professional
   method and costs five seconds of shooting.
2. **Spatially-varying key.** Sample the screen colour in several regions and key
   in bands with per-band similarity, rather than one global value.
3. **Masked flatten.** Build a rough garbage matte around the subject, compute the
   blur field from background pixels only, then apply.

If a clean plate is available, use it. It makes the rest of this trivial.

```bash
ffmpeg -i fg.mp4 -filter_complex "
 [0:v]split[a][b];
 [b]gblur=sigma=90[bg];
 [a][bg]blend=all_mode=divide:all_opacity=1,
 eq=contrast=1.15:saturation=1.4[flat]" -map "[flat]" flattened.mp4
```

Key `flattened.mp4` to generate the *matte only*, then apply that matte to the
**original** footage — never to the flattened version, which has mangled skin
tones. Extract the alpha with `alphaextract`, then recombine with `alphamerge`.

### Path C — segmentation matting (weak screen, or no screen at all)

A learned matte ignores the backdrop entirely and segments the person, so an
underlit or wrinkled screen stops mattering. Options, with the constraint that
actually decides this:

**Check the licence before you download anything.** Several of the best-performing
matting models are research releases that do not permit commercial use, and a
monetised channel is commercial use.

| Model | Quality | Licence | Usable on a monetised channel? |
|---|---|---|---|
| MatAnyone / MatAnyone2 | Best edge + temporal stability | **NTU S-Lab 1.0 — non-commercial** | **No**, not without written permission from the authors |
| SAM2Matting | Strong zero-shot | **Non-commercial CC** | **No** |
| RobustVideoMatting | Softer on hair, fast, real time | GPL-3.0 | **Yes** for producing video you publish. Copyleft attaches to *distributing the software*, not to footage you render with it. |
| FCP Keyer + Magnetic Mask | Very good, interactive | Licensed with Final Cut | **Yes** |
| fal.ai — Bria `green-screen-despill`, VEED chromakey | Good, hosted | Commercial via vendor | **Yes**, per-frame pricing |

So the practical shortlist for a monetised YouTube workflow is **FCP's own tools,
a hosted commercial API, or RVM** — not the top of the research leaderboard.
MatAnyone is worth an email if you want it; the authors list a commercial-use
contact.

Record for every model you use: model version, source commit, code licence,
weights licence (these can differ), and whether commercial use is permitted.
Weights trained on a restricted dataset can carry restrictions the code licence
does not mention.

Output a matte as a PNG sequence or an alpha-carrying format (VP9 `yuva420p`,
or ProRes 4444). Do not round-trip alpha through H.264 — it has no alpha channel
and the transparency will be silently discarded.

## Step 2b: Benchmark before committing

Cut a representative 20–30 second segment containing head movement, hand
movement, hair movement, at least one motion-blurred gesture, and both the
brightest and darkest part of the screen. Run every candidate on that same
segment and score:

- hair detail and edge softness
- hand and finger edges during motion
- **temporal stability** — does the alpha chatter frame to frame?
- residual green spill
- render time per minute of footage
- manual correction effort per minute
- commercial-use compatibility

Choose from the scores, not from a still-frame measurement. This costs an hour
once and settles the approach for every future video shot on the same setup.

## Step 3: Make the composite believable

Keying gives you a cut-out. These four steps are what make it look photographed.
Skipping them is the single biggest reason AI-assembled composites read as fake.

**Despill properly, not by desaturating.** `despill=type=green:mix=0.5:expand=0.2`
removes the green bounce on hair and shoulder edges while leaving other colours
alone. Reaching for `hue=s=0.9` instead drains the whole image.

**Match black level and contrast to the plate first.** Sample the darkest part of
the plate and the darkest part of the subject. If the subject's blacks sit lower,
the eye reads two separate images. Lift with `colorlevels` before any creative
grade.

**Add a light wrap.** Real light from a background spills around the edges of a
foreground subject. Composites lack this, which is why edges look cut. Blur the
plate heavily, mask it to a few pixels inside the subject's alpha, and screen it
over the edge. This one step does more than any amount of matte tuning.

**Match, then composite, then look.** The order matters and "grade them together"
alone is too coarse:

1. Normalise / denoise the camera footage.
2. Build and refine the matte.
3. Despill and repair contaminated edge colour.
4. **Match foreground to background**: white balance, exposure, black and white
   points, contrast, sharpness, depth of field, grain, light direction.
5. Composite.
6. Add light wrap.
7. Apply one global look across the composite.
8. Check skin tone and legal ranges on scopes.

Step 4 is the one that gets skipped and the one that matters most. A frontally,
brightly lit face over a dark side-lit "cinematic" plate will never sit right —
the light directions disagree. Choose plates with a broad source near the camera
direction unless you are prepared to relight the foreground.

## Step 4: Edge hygiene

- Erode the matte by ~1px and blur the alpha by ~0.5–1px. A mathematically
  perfect edge looks digital; real lenses are slightly soft.
- Check hair, shoulders, and any place the subject overlaps the darkest part of
  the screen — not the middle of the frame, which always looks fine.
- Check *motion* frames, not still ones. Chattering alpha only shows up in
  playback. Sample five consecutive frames at a gesture.

## Working with a looping background plate

The user's plate is a short generated clip looped behind the whole video, so
loop seams and motion are the two risks.

**Make the loop seamless at generation time, not in post.** Kling 3.0 Omni FLF
takes a first *and* last frame — set them to the same image and the clip returns
to its start. This beats crossfading a loop, which always softens the seam.

**Keep the plate boring on purpose.** A background that loops every 10 seconds
must not contain anything the eye can track and time: no objects crossing frame,
no distinct shapes entering and leaving, no rhythmic pulse. Slow drifting
gradients, particulate haze, out-of-focus bokeh, and gentle volumetric light read
as continuous motion without giving the viewer a clock. If you can tell where the
loop restarts, the plate is too eventful.

**Defocus and darken it.** The plate is set dressing, not content. Blur it beyond
what feels necessary (`gblur=sigma=8–20`) and pull it down 15–25% in luma. This
buys three things at once: the loop becomes harder to notice, the subject
separates from it, and the composite gains apparent depth. It also hides matte
imperfections.

**Loop with `-stream_loop -1`** on the input rather than concatenating copies,
and let `overlay=shortest=1` end the composite when the foreground ends.

## Ordering

Key → despill → match black level → composite → light wrap → grade → *then*
everything else. Subtitles and overlays come last of all, after every composite
step, or they end up underneath something.
