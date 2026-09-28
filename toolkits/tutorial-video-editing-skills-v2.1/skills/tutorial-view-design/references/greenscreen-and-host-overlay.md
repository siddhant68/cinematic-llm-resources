# Mask-first green-screen and host overlay

## Why mask-first

Uneven lighting, spill, wrinkles, compression, motion blur, hair, and green objects can make a full-frame key unstable. A tracked person/object mask provides a stronger base, while localized keying can still help in clean residual areas.

## DaVinci Resolve Studio workflow

1. Put the replacement background below the original presenter clip.
2. Duplicate the timeline before matte work.
3. Split long clips at cuts, large pose changes, foreground crossings, and occlusions.
4. On the Color page, use Magic Mask Person or Features to identify the subject. Add strokes to face, torso, arms, hands, and hair; subtract chair, laptop, microphone, or background when needed.
5. Track each segment forward and backward.
6. Add alpha output and route the matte correctly.
7. Refine matte cleanliness and edge size conservatively.
8. Use Fusion Polygon masks for garbage/holdout areas or manual correction around difficult hands, hair, or props.
9. Use a localized keyer only on remaining green areas if it improves the composite.
10. Apply spill suppression separately from the mask.
11. Match foreground/background exposure, color temperature, sharpness, noise, and light direction.
12. Add a subtle shadow only when the compositing geometry calls for it.
13. Test on four diagnostic backgrounds and render a motion sample.

Magic Mask is a Studio feature. Its interactive strokes may not be fully exposed through Resolve's scripting API. Use permitted UI/desktop control where available; otherwise use MCP-supported Fusion masks and report any UI-only step honestly.

## Palmier-only workflow

Use Palmier's tracked Magic Mask or mask controls rather than returning immediately to chroma key. Inspect hair, hands, chair, laptop, spill, and motion at representative frames.

For a Palmier-to-Resolve project, do not finish the mask in Palmier. Palmier FCPXML does not carry Palmier masks/effects. Export the structural cut early and build the final matte in Resolve.

## Failure criteria

Reject the matte when any of these is visible at normal playback:

- green fringe around hair or clothes
- transparent skin, hair, glasses, or hands
- clipped fingers or arm edges
- background attached to the subject
- crawling or flickering edge
- floating body with no spatial contact
- foreground light direction contradicting the background

After two focused passes, use framed PIP or an alternate camera if the cutout remains broken.
