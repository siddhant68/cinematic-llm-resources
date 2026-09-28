# Source quality and conform

## Original-media policy

The highest-quality camera file is the source of truth. A proxy, reference movie, transcode, generated enhancement, or Palmier render may help review but may not silently replace the original.

## Palmier FCPXML conform

Import the DaVinci-targeted FCPXML, then:

1. Match timeline frame rate, resolution, and start timecode.
2. Relink every media item to originals.
3. Verify ten or more edit points, every section boundary, the longest screen passage, and final minute.
4. Check source in/out, speed, transforms, crops, track order, and static volume.
5. Rebuild audio fades/automation, masks, Palmier effects/color, text backgrounds, crop keyframes, edge softness/rounding, and Lottie graphics because these are not preserved by current Palmier FCPXML.
6. Render a conform sample and compare timing to the reference movie.

## Proxy guard

Before final render, verify:

- no offline clips
- originals or approved mezzanine media are online
- proxy-only and optimized-media overrides are disabled or Resolve is explicitly set to use originals
- render cache does not contain stale low-quality frames
- timeline scaling and debayer/decode settings are appropriate

## A-roll visual comparison

At representative frames compare source and timeline at 100%:

- focus and texture
- compression blocking
- chroma subsampling artifacts
- denoise smearing
- sharpening halos
- skin tone and white balance
- scaling/crop

Use a conservative treatment and prefer a natural limited-camera image over aggressive artificial sharpness.
