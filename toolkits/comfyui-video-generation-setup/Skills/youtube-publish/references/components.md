# Every component, and what separates professional from AI-level

The complete surface list, ordered by leverage. Most creators optimise four of
these and leave twelve empty.

## What "professional, not AI-level" actually means

This is the whole brief, so it goes first. The difference is not polish — a lot
of AI output is *more* polished than professional work. Four real distinctions:

**1. Restraint, not maximisation.** AI-assisted packaging maximises every dial:
more glow, more saturation, more elements, more adjectives, more keywords. A
professional makes one thing loud and everything else quiet. If a thumbnail has
a bright subject, a bright background, big text *and* an arrow, nothing reads at
120px. Every element you add taxes the one that matters.

**2. A system, not a set of one-offs.** Amateurs design each thumbnail from
scratch and each is fine in isolation. Professionals define a system — two or
three layouts, a fixed type treatment, a fixed palette, a fixed logo position —
and vary only the content inside it. Recognition comes from *repetition of
structure*, not from any single image. Roughly two thirds of viewers can recall
a brand after three consistent exposures; a channel where every thumbnail is a
different design never gets that compounding.

**3. Real material over rendered material.** This is the strongest single tell.
AI images read as fake through over-smooth skin, glassy eyes, flat lighting,
props that mean nothing, and mangled text. Real photographs have grain, pores
and asymmetry. Through late 2025 and early 2026 the algorithm explicitly
demoted hyper-polished AI thumbnails, and real human micro-expressions measure
around 22% higher on long-term click satisfaction than their polished AI
equivalents. **The professional workflow is hybrid: real photo for the face and
the evidence, generative only for backgrounds, plates and elements that cannot
be shot.**

**4. Specific beats clever, everywhere.** `16 of 37 renders came out black` is
professional. `You won't BELIEVE what happened` is not. Specificity is the
cheapest credibility available and it is the thing generative tools are worst at,
because they regress to the average phrasing of their training data.

The test for any component below: **would this still be right if you had to use
it a hundred times?** Systems survive that question. One-offs do not.

---

## Per-video components

### 1. Thumbnail — highest leverage
Decides click-through, which decides distribution. Full craft in
`thumbnail-craft.md`. The one rule: judge it at 120px.

### 2. Title — highest leverage
Two jobs at once: tell the classifier what this is, make a person click. Full
craft in `packaging.md`. Front-load the subject, 40–65 characters, and never
repeat what the thumbnail already shows.

### 3. Description — medium leverage, low effort
Not a keyword dump. Two audiences: a viewer deciding whether to commit, and a
classifier deciding who to show it to. Both are served by the same thing — a
plain, specific sentence about what the video actually contains. See
`description-anatomy.md`. Keyword stuffing now triggers spam classification.

### 4. Chapters — high leverage, entirely mechanical
What you called "sections". They raise session time, and each chapter becomes a
deep-link that can surface in search on its own. Free, and **silently broken by
one bad timestamp**. Rules and generation in `SKILL.md`.

Chapter titles are not section headings. `Memory: the answer nobody expects` is
a script heading. `Why 4.5× the pixels costs 2 GB` is a chapter — it names what
the viewer gets by jumping there.

### 5. End screen — the strongest next-click surface
Last 5–20 seconds, needs a video ≥25s. Browser-only, no API.

The layout that performs is **one full-size video element plus a subscribe
button** — two choices, no decision paralysis. Video-element CTR on that layout
runs roughly double a four-element grid. For a series, pick the specific next
episode; "best for viewer" only wins for loosely related content.

The thing most people miss: **say it out loud too.** A spoken CTA in the ten
seconds before the end screen, matching what appears on screen, converts
markedly better than the visual alone. That means the end screen is a *scripting*
decision, not a post-production one — the script has to leave room for it.

### 6. Pinned comment — see `pinned-comment.md`
There is a real tension here worth reading before you write one.

### 7. Captions (uploaded, not auto)
Auto-captions mangle technical vocabulary reliably. The uploaded track is also
what the translation layer reads. Nearly free given the pipeline already has
aligned word timings.

### 8. Cards — low leverage, use sparingly
Teaser CTR is about 1–3%, click-through under 1%. They fire during peak
attention, so use them for *context* ("this is the environment-blocking video I
mentioned"), never to promote the next video — that is the end screen's job.

### 9. Playlist membership
Do this at upload, not later. See the playlist section below.

### 10. Altered-content disclosure — mandatory, and directly relevant here
YouTube requires disclosure when realistic content could be mistaken for a real
person, place or event and was made with generative AI. Enforcement is active,
and YouTube detects and labels some synthetic media whether or not you declare
it.

For this channel the line runs roughly:

| Content | Disclose? |
|---|---|
| A generated photoreal scene of two people duelling | **Yes** — a realistic scene that never occurred |
| A generated photoreal room, street, or interior | **Yes** |
| Clearly stylised or animated output | No |
| Screen recordings, terminal output, real footage of you | No |
| AI used for editing assistance, colour, upscaling | No |

Declaring it does **not** reduce reach, ranking, recommendations or
monetisation — YouTube has said so explicitly. On a channel whose whole subject
is AI filmmaking, disclosing is also just consistent with the content. Set it
per-video; there is a field in the Details step.

### 11. Tags — nearly worthless, one job left
Catching misspellings and casing variants of proper nouns: `ComfyUI`,
`comfy ui`, `LTX-2.5`, `LTX 2.5`. Ten to fifteen. Do not stuff.

### 12. Hashtags — real but small, with a cliff
Over 15 across title and description together and YouTube ignores **all** of
them. First three in the description render above the title, but only if the
title has none. Three to five.

### 13. Fields that silently cost you
`madeForKids` (true by accident disables comments, end screens, cards and
notifications) · `defaultAudioLanguage` (unset means no translated reach) ·
`categoryId` · `notifySubscribers` · `publishAt` · paid-promotion disclosure if
a video is ever sponsored.

---

## Channel-level components

These are set once and refined rarely, which is exactly why they get neglected.
Full craft in the `youtube-channel` skill.

### Channel name and handle
Prioritise recall over keywords — YouTube does not document channel-name
keywords as a meaningful ranking lever. A personal name suits a channel built on
one person's expertise and buys room to range across topics; a descriptive name
gives a cold-start channel clarity. The hybrid — a name plus one clarifying word
— is usually the right answer for a channel like this one.

### Channel description (the About box)
Same rule as video descriptions: the **first 100–150 characters** do the work,
in search results and on the channel page. Say who it's for and what they get.
No keyword lists.

### Channel keywords
A separate field in advanced settings. Genuinely low-value, but free.

### Channel banner
Upload at **2560×1440** (6 MB max). The **1235×338 centre is the only region
visible on every device** — TV shows the whole thing, mobile shows barely more
than that centre strip. Everything that must be read goes inside it; everything
outside is atmosphere. Most amateur banners fail here by centring text in the
*full* image.

### Channel trailer
Shown to non-subscribers on the channel page. 30–60 seconds. It answers one
question: *what do I get if I subscribe?* Not a highlight reel.

### Channel sections
Up to 12 shelves, and they are the channel page's information architecture. A
working order for a niche channel: trailer → strongest playlist → Shorts shelf →
recent uploads → secondary playlists.

### Playlists — the most under-used surface on this list
**Playlist titles and descriptions are independently indexed** and can rank in
YouTube and Google search on their own. A playlist is a second entry point to
the same videos, and it raises session depth because the next video autoplays.

- Title it as a searchable phrase, not `Series Part 3`
- Descriptions take 5,000 characters and should explain **why the order matters**
- Add videos at upload time

Your opening script already promises viewers "a playlist where I'll be breaking
the entire system down stage by stage". That is a commitment already made on
camera — it should exist before the video that promises it goes out.

### Watermark, About links, featured channels
Small. Set them once.

---

## Ranked, if you only do some of it

1. Thumbnail and title, designed as one unit
2. The first 30 seconds of the video itself
3. Chapters
4. End screen with a spoken CTA to match
5. Playlists, with real titles and descriptions
6. Pinned comment posted before the video goes public
7. Uploaded captions
8. Channel about + banner safe area + trailer
9. Altered-content disclosure (mandatory, not optional)
10. Hashtags, then tags

Items 1 and 2 are craft. Everything from 3 down is mechanical and can be made
consistent by the pipeline — which is the point of these skills.
