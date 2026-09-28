---
name: frame-design
description: Define the layout system — safe areas, caption region, PIP region, content panels, type scale and palette — before any cutting or compositing begins. Use whenever a new channel, series or shoot setup is being started, whenever a user asks where captions, B-roll, a PIP, a logo or on-screen text should go, whenever overlays collide with the speaker, and whenever an edit looks inconsistent between videos. Always use this before placing the first overlay, because every later stage is constrained by these decisions.
---

# Frame Design

This is stage 0. Not stage 7.

Where the subject sits, where the PIP goes, where captions live, how much
headroom — these are constraints everything downstream respects. Deciding them
last means discovering at composite time that the captions collide with the PIP,
and by then the cut is locked and the fix is a compromise.

The other reason to do it first: **consistency is the thing that reads as a
brand.** The failure mode of automated editing is not a bad frame, it is video #1
with a 4px border at 37px margin and video #7 with 3px at 42px, because the layout
was re-derived each time. Decide once, write it to a file, and have every later
stage read that file.

## Measure before you design

Do not design a layout from one frame. A seated speaker is narrow at the head and
wide at the shoulders, and drifts across the clip. A single bounding box will tell
you the subject spans 75% of the frame while the upper two-thirds are wide open.

```bash
python scripts/analyze_framing.py footage.mov --frames 60 \
    --json framing.json --heatmap occupancy.png
```

This samples N frames, builds a per-cell **occupancy heatmap** — the fraction of
sampled frames in which the subject covers that cell — and then *finds* the
largest genuinely clear rectangles instead of you guessing coordinates. It reports
them free-form and at 16:9, 9:16 and 1:1, because a PIP has a fixed shape and the
biggest free blob is rarely the useful answer.

Read the heatmap image. It is usually a pyramid: head at the top, shoulders
flaring to fill the bottom corners. That shape is what decides your layout.

### The thresholds

| Occupancy | Verdict | Means |
|---|---|---|
| < 0.02 | **CLEAR** | The subject never entered. Safe for a persistent element. |
| < 0.15 | **MARGINAL** | Occasional collision. Brief overlays, or add a drop shadow. |
| ≥ 0.15 | **OCCUPIED** | An overlay here covers the speaker. |

Score the *union* across time, not the mean. A layout that clears the mean will
collide the moment the speaker gestures.

## The decisions to make, in order

Each one constrains the next, so take them in this order.

**1. Safe areas.** 5% action-safe, 10% title-safe from every edge. Not
superstition — phone UI, platform chrome and TV overscan all eat the margin.

**2. The subject's home position.** From the heatmap: median head centre and the
drift range. If drift exceeds ~10% of frame width, every element keyed to the
subject's position must track it or be placed outside the drift envelope.

**3. Caption region.** Decide before the PIP, because captions are the element
that cannot move — viewers look for them in one place. If the region is
OCCUPIED (usual for a seated mid-shot), captions sit *over* the subject and
therefore need a box, not an outline.

**4. PIP region.** Must not collide with the caption region. Constrain on
**height, not width** — 28% of frame width for a 9:16 insert is 88% of frame
height, which is not a PIP, it is a second video.

**5. Content panels.** Where B-roll, code, diagrams and screen recordings go. Use
the measured 16:9 clear rectangle. If it is too small to be legible, the answer is
full-frame content with the speaker as a PIP — not a shrunken panel.

**6. Type scale and palette.** One scale, one palette, both written to the layout
file. See `caption-typography` for the caption tier specifically.

## Two layouts, and how to choose

**Speaker-dominant with corner content.** The speaker stays full size; content
lives in a measured clear corner. Works when the clear rectangle is at least ~30%
of frame width — below that the content is unreadable on a phone.

**Content-dominant with speaker PIP.** Content takes the frame; the speaker drops
to a portrait insert. Necessary when the content is a screen recording, code, or
anything with fine detail. Text in a corner panel at 30% width is illegible; the
same text full-frame is fine.

Most channels need both. Decide which one each B-roll item gets **when you place
it**, based on whether the content has readable detail — and record the choice in
the EDL, not in your head.

## Write it to a file

The output of this stage is `frame-design.json`, read by every later stage:

```json
{
  "canvas":   { "width": 1920, "height": 1080, "fps": 60 },
  "safe":     { "action": 0.05, "title": 0.10 },
  "subject":  { "head_centre_x": 0.472, "drift": 0.149, "headroom": 0.130 },
  "captions": { "region": [0.10, 0.78, 0.80, 0.14], "over_subject": true,
                "border_style": 3 },
  "pip":      { "region": [0.729, 0.02, 0.26, 0.70], "corner_radius": 24 },
  "content":  { "panel_16x9": [0.646, 0.05, 0.354, 0.389], "fullframe_ok": true },
  "palette":  { "bg": "#101418", "accent": "#FFC15E", "text": "#FFFFFF" }
}
```

Nothing downstream should contain a hardcoded margin. If a stage needs a number,
it reads it from here.

## When not to

**Do not redesign per video.** The layout is a series-level decision. Re-run the
analyser when the *shoot setup* changes — new camera position, new chair, new
framing — not when the topic changes.

**Do not design around one difficult shot.** If a single gesture breaks an
otherwise good layout, cut away for that gesture. Do not shrink every element in
every video to accommodate two seconds.

**Do not fill clear space because it is clear.** An empty upper corner is
composition, not waste. The measurement tells you what is *available*, not what is
*required*.

## Known limitations

- The subject mask is "not screen-green". On non-green backgrounds it does not
  work — supply a mask another way, or sample the background colour explicitly.
- The mask includes the chair, the desk and anything else in frame. That is
  usually correct for collision purposes — they are real objects an overlay would
  sit on top of — but it means the "subject" envelope is larger than the person.
- Occupancy is sampled, not continuous. A gesture between two samples is missed.
  Raise `--frames` for a final layout decision; 60 is enough to plan with.
