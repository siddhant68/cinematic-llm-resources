# Resolve Fusion template specification

## Template construction principles

- Build templates as reusable Fusion Titles or Macros with stable IDs.
- Use Text+ for typography.
- Expose only controls an editor or agent should change.
- Keep animation timing relative to clip length when practical.
- Use published safe-area positions rather than absolute episode-specific coordinates.
- Keep node names stable and descriptive.
- Avoid third-party fonts, plugins, and effects unless the project brief explicitly supplies and licenses them.

## Common exposed controls

```text
Copy
Font family
Font weight
Font size
Line spacing
Tracking
Text color
Accent color
Background opacity
Alignment
Safe-area anchor
Max width
Entrance duration
Hold duration
Exit duration
Motion amount
Optional icon or line toggle
```

## Suggested node naming

```text
TXT_Main
TXT_Secondary
BG_Panel
SHAPE_Accent
MASK_Reveal
XFORM_Layout
ANIM_In
ANIM_Out
MERGE_Final
MEDIA_OUT
```

## Agent build sequence

1. Create one template in a disposable or look-development timeline.
2. Populate realistic longest-case copy.
3. Review at full frame and phone-size preview.
4. Check captions, host PIP, screen UI, and end-screen collisions.
5. Save the template with the stable ID.
6. Duplicate through the episode only after approval.
7. Read back Text+ copy and timing after programmatic writes.

## Palmier limitation

When the project will move from Palmier to Resolve, do not rely on Palmier motion graphics surviving FCPXML. Export the structural cut early and build final graphics in Resolve.
