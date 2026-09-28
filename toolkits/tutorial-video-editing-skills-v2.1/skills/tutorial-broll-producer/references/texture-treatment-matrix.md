# B-roll texture and treatment matrix

Texture supports meaning. It must not reduce legibility or disguise weak material.

| Profile | Use for | Treatment | Avoid |
|---|---|---|---|
| `clean_digital` | screen recordings, UI, diagrams, product proof | crisp scaling, neutral color, restrained sharpening, no grain | bloom, film grain, chromatic aberration, fake depth blur |
| `natural_proof` | owned result footage, real failures, demonstrations | modest exposure/color match, preserve natural sound and detail | heavy LUTs, fake camera shake, dramatic vignettes |
| `subtle_filmic` | human process, atmosphere, reflective moments | gentle contrast curve, very light grain/halation, controlled motion | crushed blacks, heavy teal-orange, grain over faces or text |
| `technical_system` | architecture, agents, data flow, abstract process | clean grid/line overlays, measured parallax, labeled nodes, restrained scan | sci-fi HUD clutter, constant glitch, fake code rain |
| `archival_documentary` | genuine historical/public-domain material or clearly labeled reconstruction | source/date label, conservative contrast, optional subtle texture | making new footage look like evidence, excessive dust/gate weave |
| `hypothetical_idea` | future state, metaphor, conceptual illustration | slightly softer contrast, controlled bloom, slower motion, label when needed | presenting it as actual output or observed fact |
| `failure_warning` | errors, broken workflow, risk | cooler or lower-saturation emphasis, selective highlight, measured impact | red glitch on every error, alarm sounds, unreadable overlays |
| `generated_harmonized` | generated footage next to real footage | match fps, motion cadence, sharpness, grain, contrast, and light direction | hiding artifacts with aggressive texture or blur |

## Intensity scale

- `0`: no added texture
- `1`: barely perceptible unification
- `2`: visible but subordinate to content
- `3`: stylized; use only for a deliberate section or metaphor

Screen recordings should normally remain at 0. Actual proof should normally remain at 0 or 1.

## Transition compatibility

- Clean digital: hard cut, J/L cut, clean push only when following screen geography.
- Natural proof: hard cut, action match, sound bridge.
- Subtle filmic: dissolve only for genuine time/emotional change.
- Technical system: graphic bridge or line continuation when structure changes.
- Archival: source-card or motivated temporal bridge.
- Hypothetical: soft reveal when clearly entering an illustrative mode.
- Failure: short impact or interruption only at a meaningful failure point.
