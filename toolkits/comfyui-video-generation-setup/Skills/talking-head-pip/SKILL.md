---
name: talking-head-pip
description: Place a second-angle talking head as a picture-in-picture over full-frame content, with rounded corners and a glowing accent border. Use whenever a portrait or secondary camera angle needs to sit alongside a screen recording, B-roll, slide, or any visual that takes the full frame, and whenever a user mentions PIP, picture-in-picture, talking head corner, floating cam, webcam overlay, or a glowing border around a speaker.
---

# Talking-Head Picture-in-Picture

The PIP exists so the speaker doesn't disappear when the frame is given to
something else. It should read as presence, not as a competing window.

## Sizing and placement

**Constrain on height, not width.** For a 9:16 insert, height is what binds: 28%
of a 1920 frame is 538×956, which is 88% of a 1080 frame — that is not a PIP, it
is a second full-height panel covering the content. Use:

```
max_width_ratio  <= 0.18-0.20 of frame width
max_height_ratio <= 0.55-0.65 of frame height    <- usually the binding limit
```

At 1920×1080 that lands around 364×648 (19% w / 60% h). Below ~15% width the face
stops carrying expression at phone size. Choose within the range according to how
dense the underlying material is — busy screen recordings want a smaller PIP.

**Vertical:** anchor to the bottom edge with a 40–60px margin, letting the frame
crop mid-torso. A full head-to-waist portrait floating in the middle of the frame
reads as a video call. Cropping into the bottom edge reads as designed.

**Horizontal:** put it on the side *away* from where the underlying content wants
attention. Screen recordings and documents are read left-to-right and top-down,
so bottom-right is the default. If the content has a right-side panel, flip it.

**Reframe the source, don't just scale it.** A landscape second angle scaled into
a portrait box leaves the subject small and badly placed. Crop to 9:16 around the
face first, positioning eyeline roughly a third from the top, then scale. If the
angle was shot portrait natively, crop only for headroom.

**Check the caption collision.** A bottom-right PIP and bottom-centre captions
both live in the lower third. Either raise the captions' `MarginV` while the PIP
is on screen, or move the PIP up. Discovering this in the final render is common
and annoying.

## The glowing border

Build it with `scripts/render_pip.py` from a typed spec rather than by hand. A
rounded, glowing, animated PIP is a ~12-node filtergraph; hand-editing it
reliably introduces errors that fail at parse time or, worse, render something
subtly wrong.

```bash
python scripts/render_pip.py --spec pip.json --base base.mp4 -o out.mp4
python scripts/render_pip.py --spec pip.json --base base.mp4 --print-only
```

Two separate elements, and conflating them is why glows often look muddy:

1. **A crisp edge** — 2–3px, high opacity, defines the shape.
2. **A soft halo** — a blurred, colour-matched bloom sitting *behind* the PIP,
   extending 20–40px.

The halo is what creates separation from the background; the crisp edge is what
makes it look intentional rather than like a compression artifact.

```json
{
  "source": "portrait.mov",
  "source_range": {"start": 121.2, "end": 129.6},
  "sync_offset": -0.083,
  "position": "bottom_right",
  "max_width_ratio": 0.19,
  "max_height_ratio": 0.60,
  "margin": 48, "corner_radius": 24,
  "edge_width": 2, "edge_color": "#FFFFFF",
  "halo_opacity": 0.22, "halo_blur": 24, "halo_spread": 72,
  "audio_source": "master",
  "fade": 0.25
}
```

Four things the renderer handles that hand-written graphs get wrong, each found
by actually running it:

- **`#` comments inside a quoted `filter_complex` are parsed as filter text** and
  break the graph. Filtergraphs cannot be commented.
- **Size syntax is `WxH`, not `W:H`.** `color=c=white:s=546:904` fails with
  "Unable to parse option value as image size".
- **`-map 1:a` fails outright when the PIP camera has no audio track**, which is
  common for a second angle. And when it *does* have audio, you almost never want
  it — the master mix is the approved audio. Default to `0:a`.
- **A blurred rectangle is not a glow.** The halo mask must be the PIP-shaped
  rounded rect centred in a *larger* transparent plate, then blurred. If the mask
  fills its own plate, the blur has nothing to fall off into and the plate's
  square boundary shows as a hard edge behind the rounded corners. The plate needs
  roughly **3× the blur sigma** of transparent margin — the renderer enforces
  `halo_spread >= 3 * halo_blur`.

**Match the glow colour**Match the glow colour to the video's accent, not to white by default.** White
is clean and neutral, and it works. But a glow in the project's accent colour ties
the PIP into the palette and looks considered rather than templated. Whichever you
choose, keep it identical across every video in a series — this is the kind of
detail that reads as a brand.

**Keep the glow subtle.** At full opacity it looks like a stream overlay. 40–60%
alpha with a wide blur reads as premium; a hard bright ring reads as Twitch.

## Entry and exit

The PIP should not cut in and out hard. A 200–300ms scale-and-fade from ~92% to
100% with cubic easing is enough — it registers as an arrival without drawing
attention. Never use linear easing; it looks mechanical.

Bring the PIP in **on an L-cut**: the speaker's audio is already running from the
full-frame shot, and the PIP appears under continuing speech. Cutting picture and
audio together announces the transition.

## When *not* to use it

If the full-frame content needs real attention — dense text, a detailed diagram,
anything the viewer must read — the PIP competes and both lose. Drop to audio-only
over the content and bring the speaker back full-frame afterward. A PIP that is
always present stops being a signal.

## Verification

Sample frames at the PIP's entry, mid-hold, and exit. Check: the face isn't
cropped at the chin or crown; the glow isn't clipping at the frame edge; the PIP
isn't covering anything on the base layer that matters; captions aren't
underneath it; and the edge doesn't shimmer during motion — if it does, the glow
sigma is too tight for the encode.
