# Thumbnail craft

Everything here is downstream of one fact, so start with it.

## The 120px test is the only test

In a phone feed a thumbnail renders around **120 pixels wide**. You design at
1280×720 and it is judged at a tenth of that. Almost every thumbnail failure is
someone designing at 100% zoom and shipping something that dissolves into mush at
the size where the decision actually gets made.

So: **every thumbnail gets checked at 120px before it ships.** `thumb_qc.py`
does it automatically, but the eye test is simpler — shrink it, look away, look
back, and see whether you can tell what it is in under a second. If you have to
squint, it has already failed. Nothing below matters more than this.

Two consequences that people resist:

- **Detail is a cost, not a feature.** A beautifully rendered scene with six
  things in it reads as grey noise at 120px. One big shape reads.
- **Small text does not exist.** If a word is not readable at 120px, it is not
  in the thumbnail — it is just texture that makes the thumbnail muddier.

## Thumbnail and title are one unit

They ship together, they get judged together, and the single most common waste is
making them say the same thing.

- **The thumbnail shows. The title says.** If the thumbnail already shows a
  screen full of black video frames, the title should not say "black frames" —
  it should say what that *means* (`the render lied`).
- Together they should form **one promise with a gap in it**. Thumbnail
  establishes the subject; title opens the question; the video closes it.
- Write both before you finish the edit, not after. If you cannot package it,
  the video's idea is not sharp enough yet — and that is much cheaper to find out
  before the edit than after.

## The curiosity gap, and the trap in it

The best thumbnails **raise a question without answering it.** Show enough to
establish the topic, withhold the resolution.

The trap: a gap that the video never closes is clickbait, and YouTube now
measures viewer satisfaction directly. An overpromising package buys one click
and costs you the next ten recommendations. The rule that keeps you honest:
**the gap must be closed in the video, on camera, in a way a viewer would agree
was the answer.**

For this channel that is easy, because the material is genuinely surprising. The
black renders, the flat GPU graph, the light with no source — the honest framing
is already the strong framing. That is a luxury; do not throw it away by
inventing a bigger claim than the footage supports.

## Two or three elements. Never four.

The working set:

```
face  +  artifact  +  text        the workhorse
artifact  +  text                 when the evidence is the story
face  +  text                     when the claim is the story
```

Anything beyond three competes. The script's own line about composition applies
exactly: *if everything is screaming for attention, nothing has attention.*

One focal subject should occupy roughly **30–50% of the frame.** Below that it
reads as a texture; above it there is no room for the second element.

## Text: three words

Three is the target, four the ceiling, zero is legitimate. Every additional word
shrinks the type and costs legibility at 120px, which is the only size that
counts.

- **Heavy, condensed, tight tracking.** `Avenir Next Condensed Heavy` and
  `Impact` are both installed locally and both work. Light or regular weights
  vanish at small size.
- **Contrast comes from the type having its own ground** — a solid block, a hard
  stroke, or a deep drop shadow. Text floating directly on a photograph is the
  most common legibility failure.
- **Never centre a wall of text over a face.** Give each its own third.
- Sentence fragments beat sentences. `NO SOURCE` beats `The light has no source`.

## Colour

- **Saturated subject against a desaturated or complementary ground.** That
  separation is what survives downscaling — hue contrast holds at 120px when
  detail contrast does not.
- **Avoid YouTube's own chrome**: pure red and white read as interface, not
  content, and get lost against the player.
- **Keep the bottom-right corner clear.** The duration badge sits there and will
  cover whatever you put underneath it.
- A **signature palette becomes a visual shortcut** — viewers learn to recognise
  your videos before they read anything. Linus Tech Tips' blue and orange, and
  Vsauce's purple, are the standard examples.

### This channel already has a palette — use it

The burned-in captions use **amber keyword highlights on desaturated grey and
navy.** That is already the channel's signature, appearing in every frame of
every video. Reusing it in thumbnails costs nothing and buys recognition:

```
ground   #2A2E33  desaturated grey    the studio background
deep     #10141A  near-black navy     the shirt, panel grounds
accent   #F5A524  amber               the caption highlight. the brand.
hot      #FF6B35  warm orange         second accent, use sparingly
text     #FFFFFF  white               body of the type
```

Take the accent from `frame-design`'s palette if it ever diverges — one source of
truth for colour, same as everything else in this pipeline.

## What NOT to do on this channel specifically

This matters more here than the generic advice, because the generic advice is
written for challenge channels.

**No shocked face.** The 2026 shift in educational, tech and finance niches is
away from exaggerated expressions — genuine micro-expression now outperforms the
open-mouthed stare, and on a channel whose stated tone is *"calm throughout, the
material is surprising on its own and does not need selling"*, a MrBeast face is
a promise the video does not keep. The mismatch shows up in the first thirty
seconds of retention.

**No fake arrows pointing at nothing, no red circles around a blank area.** The
audience is technical and reads it instantly as a tell.

**Design quality is content quality here.** On a challenge channel a crude
thumbnail is fine. On a channel about *composition, framing and light*, a badly
composed thumbnail is a live demonstration that you cannot do the thing you are
teaching. Apply the video's own lessons to its packaging: one focal subject,
believable light, foreground/midground separation, an unbalanced frame only when
it means something.

**The evidence is the asset.** The strongest thumbnails available to this channel
are not illustrations — they are real artefacts that already exist in the
footage: the grid of sixteen black renders, Activity Monitor with the GPU flat at
zero, `42 GB` next to `48 GB`, the lamp burning on a woodpile. Their credibility
is the whole point, and no generated image can borrow it.

## Using generative models without looking generative

You have Higgsfield (Nano Banana Pro, GPT Image 2, Soul, Seedream, Flux). The
question is not whether to use it but **where in the frame it is allowed**.

### The hybrid rule

```
face and evidence   →  real footage, always
background / plate  →  generative, freely
elements, textures  →  generative, freely
type                →  always the compositor, never the model
```

The reason is measurable rather than aesthetic. AI faces read as fake through
over-smooth skin, glassy eyes and flat lighting; real photographs carry grain,
pores and asymmetry. Through late 2025 and early 2026 the algorithm demoted
hyper-polished AI thumbnails, and real micro-expressions measure around 22%
higher on long-term click satisfaction. On a channel *about* AI filmmaking, a
plastic AI face is also the worst possible advertisement for your own pipeline.

**Never let a model render your text.** Even the best text-rendering models
produce subtly wrong letterforms, inconsistent spacing and no control over the
type system. The compositor already fits type to the frame exactly and keeps it
consistent across a series. Generate the plate, composite the type.

### The tells to check for before shipping

- skin like plastic; no pores, no grain, no shine variation
- eyes glassy, catchlights identical in both, or subtly misaligned
- lighting with no discernible source — the exact failure your own LIGHT video
  is about, which would be an embarrassing thing to ship
- props that mean nothing, hands that do not resolve
- symmetry that is too perfect
- saturation past what a camera would produce

Add grain and let the plate sit *behind* real material rather than replacing it.

### Where it genuinely earns its place here

- background plates for `statement` and `face-artifact`, when the footage has no
  usable backdrop
- an environment or character plate for cinematic-pipeline episodes, where the
  subject *is* generated imagery — there the generated look is the content
- abstract textures and gradients under type

### Practical

Higgsfield ships a hosted MCP: OAuth through the account, no API key, 30+ models
behind `generate_image` and `generate_video`, output up to 4K. Add the server
and the tools appear. Generate at 16:9, save into `assets/`, and reference the
file from a thumbnail spec exactly like a frame grab — the compositor does not
care where a plate came from.

Keep generated plates in the repo next to the spec. A thumbnail you cannot
regenerate is a thumbnail you cannot iterate on.

## Templates

Four, matching the shapes above. `render_thumbnail.py --template <name>`.

| Template | Shape | Use when |
|---|---|---|
| `evidence` | Artifact fills the frame, 2–3 words in a corner block | The screenshot *is* the story — black renders, a graph, a log |
| `face-artifact` | Face in one third, artifact in the other, text banded | The workhorse. A person explaining a specific thing |
| `contrast-pair` | Hard vertical split, two states, one word each side | The content is a comparison — broken/fixed, warm/cool, before/after |
| `statement` | Type only on a coloured ground, one supporting mark | A pure claim with no good visual |

`contrast-pair` deserves special note on this channel: much of the material *is*
a visual comparison, and a split thumbnail demonstrates the video's claim rather
than describing it. That is the rare case where the thumbnail is itself an
argument.

## The objective checks

`thumb_qc.py` enforces what can be measured. It is not a substitute for looking
at the thing, in the same way `qc_review.py` is not a substitute for watching the
video.

| Check | Threshold | Why |
|---|---|---|
| Dimensions | exactly 1280×720 | Anything else gets rescaled by YouTube, softly |
| File size | < 2 MB | Hard API limit; upload fails above it |
| 120px legibility | text height ≥ 6px at 120px wide | Below this, words are texture |
| Global contrast | luma std ≥ 45 | Flat images disappear in a feed |
| Focal dominance | largest region 25–60% of frame | One subject, with room for a second element |
| Duration-badge safe zone | bottom-right 190×60px clear | The badge covers it otherwise |
| Edge safety | nothing critical in outer 4% | Cropping varies across surfaces |
| Element count | ≤ 3 distinct regions | Clutter check |

A clean report means it is shippable, not that it is good. Shrink it to 120px and
look at it.

## A/B testing

YouTube's **Test & Compare** runs three thumbnails on live traffic and picks the
winner on watch time — the right metric, since it will not reward a thumbnail
that wins clicks and loses viewers. It is Studio-only, with no API, and appears
to be gated on channel size; verify availability before planning around it.

Until then: the compositor emits variants from one spec, so producing three real
candidates costs a parameter change. Swap them by hand and watch the first 48
hours. Change **one variable at a time** — a new photo and new text at once tells
you nothing about either.
