# Palmier to Resolve handoff

## Stop point

Export after the structural cut and basic angle decisions. Do not invest in finishing that will not survive interchange.

## Transfer package

```text
project.fcpxml
REFERENCE_ONLY.mp4
production microphone original
source_manifest.json
path_map.csv
retake_decisions.json
edit_blueprint.json
handoff_notes.md
all original camera, screen, audio, and approved asset files
```

## Current DaVinci FCPXML coverage

Palmier documents that DaVinci-targeted FCPXML carries clip placement, trims, speed, track order, text styling, transforms, flips, crop, opacity, static volume, source timecode, and supported visual keyframes.

It does not carry audio-volume keyframes, audio fades, text background boxes, crop keyframes, Palmier color/effects, edge softness, edge rounding, or Lottie clips.

Masks and Palmier finishing effects should be treated as non-transferable.

## Resolve conform gate

In Resolve:

1. Import the correct FCPXML version for the installed Resolve version.
2. Relink every item to original media.
3. Verify timeline settings and start timecode.
4. Compare source ranges, speed, transforms, track order, and sync.
5. Check at least ten edit points and every section boundary.
6. Rebuild all non-transferable finishing work.
7. Render a conform sample from originals.

Block finishing when any clip remains linked to the Palmier reference render or an unintended proxy.
