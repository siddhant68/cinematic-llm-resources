---
name: tutorial-motion-graphics
description: Design restrained, reusable motion graphics and typography that make a long-form tutorial's structure visible. Use when an agent must convert a monologue into section openers, memory anchors, step lists, comparisons, UI callouts, diagrams, lower thirds, chapter recaps, or a final summary of section headers; specify Fusion-ready templates and animation behavior; prevent unreadable or decorative text; or produce and validate motion_graphics_plan.json before building graphics in DaVinci Resolve or Palmier.
---

# Tutorial Motion Graphics

Use motion graphics to expose the argument. Do not use them to decorate every sentence.

## Required inputs

- `EPISODE_BRIEF.json`
- `edit_blueprint.json`
- approved section names and viewer outcomes
- `style_profile.json`
- B-roll plan and screen-focus decisions
- brand references when available
- target resolution, frame rate, safe areas, and caption layout

Read:

- `references/typography-story-system.md`
- `references/motion-language.md`
- `references/resolve-fusion-template-spec.md` for DaVinci execution
- `references/session-proven-captions.md` when using active-word captions or dialogue-paused section cards

## Required outputs

```text
planning/motion_graphics_plan.json
planning/graphics_copy.md
planning/fusion_template_manifest.json
```

Validate the plan:

```bash
python scripts/validate_motion_graphics_plan.py planning/motion_graphics_plan.json
```

## Story system

### 1. Name the sections

Give every major section a concise 2-7 word name that tells the viewer what changes. Do not use vague labels such as `Part 2` or `More details`.

Each section should include:

- a short opener
- zero to three memory anchors while the idea develops
- an optional local recap after dense material
- one transition or audio bridge into the next section

The ending should assemble all major section headers in order and add one final operating rule or conclusion.

### 2. Use a limited role hierarchy

Use these roles:

- `episode_title`
- `section_open`
- `hero_claim`
- `memory_anchor`
- `step_list`
- `comparison_label`
- `screen_callout`
- `data_point`
- `lower_third`
- `local_recap`
- `final_recap`
- `caption`

Do not make all roles visually loud. Section openers and hero claims can lead. Labels, callouts, and captions should remain subordinate.

### 3. Write graphics copy, not transcript cards

Graphics should summarize, label, compare, sequence, or reveal. They should not repeat a full spoken paragraph.

Defaults:

- section open: 2-7 words
- hero claim: no more than 8 words
- memory anchor: 2-6 words
- step label: short verb-led phrase
- screen callout: only enough text to direct attention
- final recap: one line per section plus one conclusion

Break a complex sentence into sequential visual states rather than shrinking a paragraph.

### 4. Choose the least complex graphic that works

Use this order:

1. Clean text over an existing frame.
2. Text plus one shape or line.
3. Screen callout anchored to the demonstrated UI.
4. Step or comparison layout.
5. Simple diagram or process animation.
6. Full-frame graphic only when the visual itself is the explanation.

Do not create a 3D or particle treatment for information a well-timed label can communicate.

### 5. Plan every graphic as a timed event

Each item must record:

- linked section and beat
- exact start and end
- role and copy
- information job
- evidence or source it labels
- composition and safe-area zone
- relationship to captions, host, and screen point of interest
- entrance, hold, and exit
- motion family and speed class
- optional SFX tied to a visible landing
- minimum readable hold
- confidence and review status

### 6. Build a reusable template system

For Resolve, use stable Fusion template IDs:

```text
MG_EPISODE_TITLE
MG_SECTION_OPEN
MG_HERO_CLAIM
MG_MEMORY_ANCHOR
MG_STEP_LIST
MG_UI_CALLOUT
MG_COMPARE
MG_DATA_POINT
MG_LOWER_THIRD
MG_LOCAL_RECAP
MG_FINAL_RECAP
```

Expose editable controls for copy, font, weight, size, line spacing, color, alignment, safe-area placement, accent, background opacity, in/hold/out duration, and motion amount. Keep the templates deterministic enough that an agent can reuse them without rebuilding the node tree.

### 7. Use one motion language

Choose one easing family and three speed classes:

- `micro`: labels and callouts
- `standard`: section text and step changes
- `structural`: full-section or recap transitions

Default movement should be short, smooth, and directional. Use opacity and position before scale, rotation, blur, or elastic motion. Do not use bounce, pulse, glow, chromatic aberration, glitch, or kinetic word-by-word emphasis by default.

### 8. Protect readability

Review every graphic at full resolution and at phone size.

- Keep essential text inside the configured safe area.
- Do not cover UI controls, faces, hands, proof, subtitles, or YouTube end-screen zones.
- Maintain sufficient contrast without oversized boxes.
- Hold long enough to read once at natural speed.
- Use no more than two type families and a small weight hierarchy.
- Preserve screen recordings as crisp digital images; do not add film grain behind small text.

Inspect the actual composited frame, including background architecture and decorative lines. Text that is inside a nominal safe area can still become unreadable when a letter intersects a window frame, horizon, rule, face, hand, or caption.

For full subtitles, a restrained active-word color may track the spoken word when that treatment has been established for the series. Keep the inactive words stable, use one accent color, preserve whole-line readability, and verify the highlight against the final audio after every ripple edit.

Use dedicated section screens at real topic changes when a monologue needs stronger structure. Let the card name the new question or decision, then return to evidence quickly; do not use section cards as decorative interruptions.

### 9. Coordinate with B-roll and audio

Motion graphics may replace weak stock or generated B-roll for abstract ideas. Share timecodes with the B-roll plan so only one primary visual treatment competes for attention.

Use SFX only for a visible structural event, such as a title landing, comparison reveal, node connection, or recap stack. Never attach a whoosh to every text appearance.

Music may lift under a full-frame section bridge or final recap, but dialogue remains primary.

### 10. Review in the look-development sample

The sample must contain:

- one section opener
- one memory anchor
- one UI callout or comparison
- captions at the same time as another graphic
- host-over-content collision check
- final or local recap behavior

Do not apply templates to the entire episode until hierarchy, motion, and phone-size readability pass.

## Final recap contract

The final recap must:

1. Use the final approved section order.
2. Include every major section header once.
3. Add one concise conclusion or operating rule.
4. Leave space for the spoken conclusion and planned YouTube end screen.
5. Avoid introducing a new argument.

## Handoff

Pass the validated plan, graphics copy, and template manifest to `davinci-tutorial-builder` or the explicitly selected editor adapter. Pass a rendered sample to `tutorial-qc`.
