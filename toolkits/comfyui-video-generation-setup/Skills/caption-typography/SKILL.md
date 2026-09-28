---
name: caption-typography
description: Design and burn subtitles that match a video's colour theme, plus a distinct emphasis treatment for hero lines. Use whenever subtitles, captions, burned-in text, karaoke captions, word highlighting, lower thirds, or on-screen typography are being added, whenever a user wants certain lines to stand out or "hit differently", and whenever caption styling needs to stay consistent across multiple videos in a series.
---

# Caption Typography

Two tiers, and the discipline is in keeping them two. **Body captions** are read
without being noticed. **Hero lines** are the three to six moments in a video
that carry the argument. If everything is emphasised, nothing is.

## Tier 1 — body captions

The defaults that survive contact with real footage:

- **Chunk 3–5 words** for long-form, 2 words for short-form. Word-by-word reads
  as frantic in a 10-minute video. Full sentences are unreadable at the pace of
  speech.
- **Break on punctuation and natural pauses**, never on a fixed word count that
  splits a phrase.
- **Sentence case for long-form, UPPERCASE for short-form.** Uppercase at length
  is fatiguing and slower to read.
- **Bottom margin 60–80px** at 1080p for long-form, higher (`MarginV=100+`) for
  vertical where UI overlays the lower third.
- **Weight over size.** A bold face at moderate size reads better on a phone than
  a light face scaled up.

### Making them match the video's colour theme

The mistake is tinting the *text*. Coloured caption text loses contrast against
footage and becomes hardest to read exactly when it matters. Instead: **keep the
text white or near-white and put the theme colour in the box behind it**, darkened
until white text clears roughly 4.5:1 contrast.

Generate the ASS with `scripts/build_captions.py` rather than hand-writing the
style line. Three things about ASS are counter-intuitive enough that hand-writing
it fails silently, and all three were verified empirically against libass 0.17:

**1. Alpha is INVERTED.** `00` is opaque, `FF` is transparent. `&HB3...` is not
70% opaque — it is 70% *transparent*, i.e. about 30% opaque. 70% opacity is
roughly `&H4D...`. The script takes opacity as 0..1 and converts.

**2. Channel order is BGR, not RGB.** The format is `&HAABBGGRR`. Pasting an RGB
hex silently swaps red and blue. Theme `#241A14` becomes `&H4D141A24`.

**3. Under `BorderStyle=3` or `4`, the box is painted from `OutlineColour`, not
`BackColour`.** `BackColour` is the shadow. Putting the theme colour in
`BackColour` — the obvious reading of the field name — renders no visible box at
all. Verified: theme colour in `OutlineColour` renders the box; the same value in
`BackColour` renders nothing.

**4. `BorderStyle=3` reuses the `Outline` value as box padding.** `Outline=0` with
`BorderStyle=3` renders bare text and no box, and the render still succeeds. Use
`Outline=6-10`.

Also set **`PlayResX` / `PlayResY`**. Without them libass guesses a script
resolution and `FontSize` means something different at every render size — the
most common cause of "the captions changed size when I exported at 4K".

`BorderStyle=4` (per-line box) is a libass extension, not portable ASS. Fine for
ffmpeg burn-in, unreliable if the file is opened elsewhere.

```bash
python scripts/build_captions.py --transcript words.json \
  --out-ass captions.ass --out-srt captions.srt \
  --play-res 1920x1080 --font Inter --font-size 54 \
  --theme-color '#241A14' --box-opacity 0.70 --border-style 3 \
  --max-cps 17 --max-chars 42
```

### Reading speed is a hard constraint, not a preference

The builder validates and refuses to pretend a cue is readable when it isn't:

- **Characters per second ≤ 17** for a general adult audience. Above ~20 the
  viewer is choosing between reading and watching.
- **≤ 42 characters per line, max 2 lines.** This is the Netflix profile — a
  useful reference point, not a universal law, but a sane default for long-form.
- **Minimum 1.0s on screen**, hard floor 0.4s.
- **Break on sentence, then clause, then length** — never on a fixed word count,
  which splits phrases mid-thought.

For a 15–20 minute technical video, aggressive 2–3 word short-form chunking is
exhausting. Use calm phrase captions for explanation and save the energy for
hero lines.

### Always produce an accessibility sidecar

Burned-in design captions are not accessible captions: they can't be turned off,
translated, or read by a screen reader, and YouTube can't index them. Always emit
`--out-srt` (or `--out-vtt`) alongside the burn-in and upload it as a real
subtitle track. This costs one flag.

## Tier 2 — hero lines

Identify hero lines **from the script, before the edit** — they should be the
lines the video exists to deliver, chosen deliberately, not the ones that happen
to sound punchy in the transcript. Three to six in a ten-minute video. More than
that and the treatment stops signalling anything.

What changes for a hero line, in order of how much you should reach for it:

1. **Scale and position.** Larger, moved off the bottom third toward centre or
   upper third. Position change alone is a strong signal because it breaks the
   pattern the viewer has settled into.
2. **The theme colour, now on the text.** This is where the accent colour earns
   its keep — it appears rarely enough to mean something.
3. **Word-level highlight.** Each word changes colour as spoken. Requires
   word-level timestamps and the ASS `\k` family. `{\k}` switches instantly;
   `{\kf}` sweeps a fill across the word.
4. **Entry animation.** A scale-up or fade using `\t()` transforms. Use sparingly
   — a hero line that bounces looks like short-form, which may not be the
   register you want.

**Two timing systems live in ASS and mixing them is the classic bug**: karaoke
tags (`\k`, `\kf`) are in **centiseconds**, animation tags (`\t`) are in
**milliseconds**. `{\k100}` is one second; `{\t(0,100,...)}` is a tenth of one.

```
Dialogue: 0,0:01:12.40,0:01:15.90,Hero,,0,0,0,,{\k45}Discipline {\k30}is {\k60}environment
```

## Rendering

Generate ASS from word-level timestamps, then burn once:

```bash
ffmpeg -i comp.mp4 -vf "ass=captions.ass" -c:v libx264 -crf 18 -c:a copy out.mp4
```

Use the `ass` filter for styled or karaoke captions and `subtitles=file.srt:force_style='...'`
only when every line shares one style. `force_style` **overrides** an ASS file's
own header — passing both silently discards your styling.

Timestamps must be on the **output timeline**, not the source. After cutting,
`output_time = word_time - range_start + range_offset`. Getting this wrong is why
captions drift progressively out of sync as a video plays.

`libass` must be compiled in. `ffmpeg -filters | grep -E "^ ..\. (ass|subtitles)"`
confirms it.

## Ordering

**Captions go on last, after every overlay and composite.** They are the top
layer of the image, and anything drawn after them will cover them. This failure
is silent — the render succeeds and the captions are simply gone behind a B-roll
insert.

## Verification

Check the rendered file, not the ASS file:

- Sample frames *during* captioned speech. An empty frame proves nothing.
- Check the longest line for wrapping off-screen and the shortest for a box
  that's too tight.
- Check a caption that lands over the brightest part of the footage and one over
  the busiest — those are where contrast fails.
- Check on a phone-sized viewport. Desktop legibility is not evidence.
- Confirm sync at the *end* of the video, where drift accumulates.
