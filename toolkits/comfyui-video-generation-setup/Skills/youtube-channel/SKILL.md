---
name: youtube-channel
description: Set up and maintain the channel itself — name, handle, About description, banner, trailer, sections and playlists. Use whenever a channel is being created or rebranded, whenever a user asks what to call a channel or what to write in the About box, whenever a banner, channel art, avatar or trailer is being made, whenever playlists or channel sections need organising, and whenever a channel "looks amateur" or inconsistent. Distinct from youtube-publish, which handles a single video's metadata.
---

# The channel

Per-video packaging decides whether one video gets clicked. The channel decides
whether someone who liked it stays. These are set once and refined rarely, which
is exactly why they end up half-finished.

Companion to `youtube-publish`. Complete component map, including which of these
matters most, is in `../youtube-publish/references/components.md`.

## The thing that makes a channel look professional

Not polish. **Consistency of a small number of decisions, applied everywhere.**

An amateur channel makes each asset from scratch: a different thumbnail layout
each week, a banner in one palette, an avatar in another, playlist titles like
`Part 3`. Every piece is individually fine. Together they say nobody is running
this.

A professional channel fixes a handful of constraints — one type treatment, one
palette, one or two layouts, one voice — and varies only content inside them.
Recognition compounds: roughly two thirds of viewers can recall a brand after
three consistent exposures, and a channel that never repeats itself never starts
that clock.

So the deliverable here is not a banner. It is a **small set of rules**, written
down in `channel.md`, that every later asset obeys.

## Order

1. **Name and handle** — hardest to change, do first
2. **Positioning line** — one sentence; everything else is derived from it
3. **About description** — first 150 characters do the work
4. **Palette and type** — inherited from `frame-design`, not invented here
5. **Avatar and banner** — built from 3 and 4
6. **Playlists** — before the video that promises them
7. **Sections** — the channel page's information architecture
8. **Trailer** — last; it needs videos to point at

## 1. Name and handle

Prioritise recall over keywords. YouTube does not document channel-name keywords
as a meaningful ranking lever, and clarity beats stuffing.

- **A personal name** suits a channel built on one person's expertise and buys
  room to range across topics — the audience follows the person.
- **A descriptive name** gives a cold-start channel immediate clarity about what
  it is.
- **The hybrid** — a name plus one clarifying word — usually wins for a channel
  like this: personal authority plus a subject a stranger can parse in one
  glance.

Check the handle is free on YouTube and ideally on the one or two other places
you'll post. Do this before anything else; renaming later costs every asset.

## 2. The positioning line

One sentence, written for a stranger: **who it's for, and what they get.**

> For people building AI film pipelines: the filmmaking decisions that have to
> happen before a video model generates a frame.

Everything downstream derives from this — the About box, the banner text, the
trailer script, the way playlists are named. Write it before any of them, and
rewrite it when it stops being true.

## 3. About description

Same rule as a video description: **the first 100–150 characters do the work**,
appearing in search results and on the channel page before the fold.

- Open with the positioning line, or a tighter version of it
- Then two or three lines: what kind of videos, how often, who you are
- Then links
- **No keyword lists.** They read as spam to a human and now trigger spam
  classification anyway.

There is a separate *channel keywords* field in advanced settings. Low value,
but free — put the obvious five or six terms there instead of in the prose.

## 4. Palette and type

Do not invent these. The channel already has them: `frame-design` holds the
palette and type scale, and the burned-in captions have been using amber
highlights on desaturated grey and navy in every frame of every video.

```
ground   #2A2E33   deep  #10141A   accent  #F5A524
```

The same three colours run through thumbnails, banner, avatar and end cards.
That repetition *is* the brand. See
`../youtube-publish/references/thumbnail-craft.md`.

## 5. Avatar and banner

**Avatar** renders at 48px in comments. That is the real constraint — a
photograph of a face works, a logo with words does not. Test at 48px the way
thumbnails are tested at 120px.

**Banner**: upload at **2560×1440**, 6 MB max.

The rule almost everyone gets wrong: **only the centre 1235×338 is visible on
every device.** TV shows the full image, desktop shows a wide strip, mobile
shows barely more than that centre. Anything that must be read — the positioning
line, the upload schedule — goes inside the safe centre. Everything outside it is
atmosphere that most viewers never see.

So a banner is really a 1235×338 design with a 2560×1440 bleed. Compose it that
way round.

## 6. Playlists

The most under-used surface on YouTube. **Playlist titles and descriptions are
independently indexed** and can rank in YouTube and Google search on their own —
a second entry point to videos you already made. They also raise session depth,
because the next video autoplays.

- **Title as a searchable phrase.** `Building an AI film pipeline, stage by
  stage` — not `Series Part 3`.
- **Write the description.** 5,000 characters available; a few hundred is right.
  Say **why the order matters**, so the viewer keeps clicking Next.
- **Add videos at upload**, not in a cleanup pass later.

The opening script already promises viewers *"a playlist where I'll be breaking
the entire system down stage by stage."* That is a commitment made on camera. It
should exist before the video that promises it goes out.

## 7. Sections

Up to 12 shelves — the channel page's information architecture. A working order
for a niche channel:

```
trailer  →  strongest playlist  →  Shorts shelf  →  recent uploads  →  secondary playlists
```

Lead with the playlist that best explains what the channel is, not with "recent
uploads". Recency is not an argument for subscribing.

## 8. Trailer

Shown to non-subscribers on the channel page. **30–60 seconds.**

It answers exactly one question: *what do I get if I subscribe?* It is not a
highlight reel and not a personal introduction. Structure that works:

```
0-5s    the specific problem this channel is about
5-25s   the sharpest single proof you can show
25-45s  what kind of videos come out, and how often
45-60s  one clear ask
```

Make it last. It needs real videos to point at, and a trailer promising content
that does not exist yet is the fastest way to lose the subscriber it just won.

## Write it down

The output of this skill is `channel.md` in the repo — name, handle, positioning
line, palette, type, banner safe-area copy, playlist list, section order. Every
later asset reads from it.

A channel style guide that lives only in someone's head produces a channel that
looks like nobody is running it, which is precisely the thing this skill exists
to prevent.

## Checks

- Handle is free and matches elsewhere
- Positioning line names an audience and an outcome
- About: first 150 characters stand alone, no keyword list
- Avatar legible at 48px
- Banner: everything readable inside the centre 1235×338
- Playlists titled as searchable phrases, descriptions written
- Sections lead with a playlist, not recent uploads
- Trailer under 60s and every promise in it is already true
