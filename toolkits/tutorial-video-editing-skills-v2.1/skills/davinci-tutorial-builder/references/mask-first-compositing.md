# Mask-first compositing in Resolve

## Segment first

One long mask track is fragile. Split at:

- cuts and retakes
- large pose changes
- arms crossing torso
- hands entering/leaving frame
- laptop, chair, microphone, or prop occlusion
- fast motion blur
- lighting or exposure change

## Matte construction

1. Place the background under the original presenter clip.
2. Use Magic Mask Person/Features when available.
3. Mark positive subject regions and negative exclusion regions.
4. Track forward and backward within the segment.
5. Add alpha output.
6. Inspect matte view and composite view.
7. Add Fusion garbage/holdout masks where the AI mask is consistently wrong.
8. Manually keyframe only the difficult range.
9. Use localized keying for residual green only.
10. Despill separately.

## Diagnostic backgrounds

Test over:

- solid black
- solid white
- fine high-contrast texture
- skin-toned or warm background

Different backgrounds reveal green spill, gray halos, missing hair, transparent skin, and edge chatter.

## Integration

Match:

- exposure and black level
- white balance and saturation
- light direction and softness
- sharpness, noise, and grain
- perspective and scale
- contact shadow when spatially justified

## Fallback

After two focused repair passes, switch to a framed PIP or alternate camera when the matte is still visible at normal playback. The viewer should notice the explanation, not the edge of the presenter.
