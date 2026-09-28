# Cinematic Director Playbook

## Purpose

Use this reference to make performance prompts feel authored by a film director while remaining feasible for generative video.

## 1. Camera scale and lens language

Use approximate lens feel as a storytelling tool, not a technical ornament.

| Coverage | Typical lens feel | Best use |
|---|---:|---|
| Environmental wide | 24–32 mm | Establish geography, reveal travel, end on architecture |
| Full / medium-wide | 35–50 mm | Read complete choreography and costume physics |
| Medium | 50–65 mm | Torso, gesture, hands, relationship to background |
| Close-up | 75–100 mm | Face, breath, concentration, delight, fatigue, transformation |
| Extreme detail | 85–120 mm | Feet, hand, eye, pendant, sweat, fabric, contact |

Do not change scale just to create variety. Change scale when the viewer's attention should change.

Lens numbers are approximate directing anchors. Pair critical lens language with the intended visual effect: `75–85 mm intimate close-up, shallow enough to isolate her face while preserving the arch as soft texture`.

## 2. Camera movement vocabulary

Prefer smooth, readable movement:

- shallow arc: 20–45 degrees around a mostly fixed performer;
- tracking: move with traveling choreography;
- counter-move: camera moves against a turn/dance path to create energy;
- slow push-in: increase intimacy or concentration;
- slow pull-back: release tension or return the performer to the environment;
- low lateral track: emphasize feet, hem, ground contact, or speed;
- foreground reveal/occlusion: pass behind flowers, columns, fountain, fabric, or architecture for motivated edits.

Use larger orbits only when choreography and geography can remain legible. Avoid repetitive orbiting around every pose.

Treat camera coverage as prioritized visual grammar, not a requirement that every described setup become a separate hard cut inside one generation.

## 3. Energy profiles

### Calm / meditative

- Longer takes and holds.
- Camera generally slower than performer.
- Use breath and micro-expression close-ups.
- Cut while the body is stable.
- Let cloth, hair, water, foliage, and light provide secondary motion.

### Playful / energetic dance

- Preserve a wide/full-body master for readable dance.
- Add 35–50 mm traveling coverage that moves with or against her path.
- Use detail or face coverage on stable, repeated, landing, or recovery beats rather than during maximum limb complexity.
- Let hair and skirt motion create wipes and transitions.
- Allow the performer to travel between zones; map the route explicitly.
- Use more frequent changes of scale than yoga, but do not turn the dance into a montage.
- Camera can feel delighted by the performance: responsive, fluid, slightly playful, never frantic.

### Duel / impact action

- Establish distance, handedness, obstacles, and screen direction first.
- Keep attacks readable in wider coverage.
- Save close-ups for anticipation, grip, eyes, impact detail, recovery, or aftermath.
- Use speed changes and brief stillness to make impact feel heavier.

### Intimate grooming / transformation

- Keep the camera restrained when hands, hair, cloth, jewelry, or knots are doing complex work.
- Favor medium or medium-close framing that can read face and hands together.
- Let breath, posture, gaze, and small physical corrections carry the drama.
- Use the completed posture or expression as the visual payoff rather than adding an elaborate camera flourish.

### Intimate / emotional

- Favor longer lenses and restrained movement.
- Let eyeline changes precede head/body movement.
- Use hands, breath, and tiny facial changes as inserts or focal beats.

## 4. Spatial blocking

### Circular court

Use the central feature as 0 and map the rim as a clock face.

Example:

- 12: arch / keep
- 3: open valley / sunrise
- 6: broad paving
- 9: bench / flowers

Assign zones such as `Zone A = 4–5 o'clock, about two metres from fountain rim`.

Camera positions may be at other clock points. State explicitly:

`THE CAMERA MOVES; THE PERFORMANCE ZONE DOES NOT.`

For a traveling sequence, define the route:

`4:30 -> 5 -> 6 -> 7 -> 8:30`.

Pair clock positions with semantic anchors such as `9 o'clock / bench side` and `12 o'clock / arch side`. Treat exact numbers as continuity aids rather than claims of geometric precision from the video model.

### Rectangular or linear location

Use named landmarks instead:

- north arcade;
- east window wall;
- central carpet;
- south doorway;
- west balcony.

Give the performer a route relative to these anchors.

### World space vs screen space

Use world-space geography for continuity and screen-relative language only as a local framing aid.

A reverse camera angle can flip screen-left and screen-right. It must not move the sun, bench, arch, doorway, fountain, or performer to another part of the set.

## 5. Lighting continuity

Map the light source into the same world coordinate system.

Example:

`Low morning sun originates from 3 o'clock.`

Then describe camera-relative consequences:

- from one camera side it is three-quarter key;
- from the reverse side it becomes side/backlight;
- pale stone or fountain water provides fill;
- arch interiors remain cooler.

The source never jumps merely because the shot reverses.

Use progressive lighting only when time passes:

`cool dawn ambient -> warm rim -> broader honey-gold side light`.

Do not replace fixed-world light logic with a repeated instruction such as `backlight from camera-right` across changing camera sides.

## 6. Choreography readability

For every named move, provide literal mechanics.

Good:

`TREE POSE — VRKSASANA: weight fully in left foot; right sole rests against the inside of the left calf below the knee; hands return toward the sternum.`

Bad:

`She does tree pose beautifully.`

For dance, names can be production shorthand rather than strict real-world taxonomy. If uncertain about the formal name, state a descriptive name and mechanics rather than mislabeling it.

Useful dance phrase components:

- preparation step;
- traveling cross-step;
- half turn / full clockwise turn;
- pivot;
- weight transfer;
- arm sweep;
- skirt-led turn;
- suspended beat;
- playful recoil;
- side travel;
- controlled landing;
- gaze/spotting point.

Pair foot direction with world direction when continuity matters.

Do not obsess over exact rotation degrees when the ending orientation is the story-critical fact. `Three-quarter counter-turn ending toward the keep` is usually more useful than numeric precision alone.

## 7. Motivated close-ups

A close-up should answer a story question.

Examples:

- Is she struggling? -> ankle/foot tremor.
- Is she enjoying herself? -> face immediately after a successful turn.
- Is the dance energetic? -> feet/hem on a repeated or stable travel phrase.
- Is concentration returning? -> eyes finding a fixed point.
- Is the morning warming? -> light catching hair/sweat/skin texture.
- Is continuity intact? -> pendant, hand, prop, footwear detail.
- Has her public composure returned? -> eyes, shoulders, chin, and breath after grooming.

Avoid details with no narrative or kinetic purpose.

**Evidence rule:** if a close-up was omitted from a successful render as a precaution, that omission is not evidence that close-ups fail. Keep motivated close-ups available unless actual output demonstrates a problem.

## 8. Complexity allocation

Do not spend maximum complexity on performer and camera at the same instant unless the scene specifically requires it.

Use this default:

> **Complex performer action -> simpler camera. Simpler performer action -> camera may become more expressive.**

Examples:

- full spin + long skirt + loose hair -> stable full-body framing;
- intricate hair tying -> quiet medium framing;
- prop handoff -> readable camera, no aggressive orbit;
- straightforward circular travel -> tracking/counter-move is appropriate;
- landing or recovery -> motivated close-up or subtle push;
- static emotional beat -> camera can slowly release or reframe.

This is a risk allocation rule, not a ban on dynamic combinations. Increase complexity again when actual renders show the model can handle it reliably.

## 9. Continuity transitions between generated clips

Best transitions conceal the model boundary inside ordinary film grammar.

Strong choices:

1. Fountain/column/tree partially or fully occludes the performer.
2. Hair or skirt sweeps across much of frame during a turn.
3. Camera passes behind foreground leaves/flowers/architecture.
4. Performer exits one side and emerges from a spatially mapped new angle.
5. End on a pose/beat hold; begin next clip on the same hold before releasing.
6. End on a turn facing away; begin from a reverse angle after the turn completes.

Do not use a hard breakpoint during a unique complex action unless there is a strong visual concealment or the user explicitly wants a visible edit.

Substantial occlusion is normally enough for a hidden handoff; do not force perfect 100% obstruction if that requirement makes the staging harder.

If using an image handoff, prefer a clean, informative frame. A motion-blurred or mostly occluded literal last frame may be worse conditioning than a deliberately concealed edit.

## 10. Physics and secondary motion

Describe realistic lag:

`weight -> torso -> limbs -> hair/skirt/pendant -> settle`.

For dance, allow secondary motion to amplify energy:

- skirt continues half a beat after torso stops;
- hair follows the turn and settles later;
- pendant swings once and returns;
- foot plants before the next weight transfer.

For grooming or prop work:

- cloth compresses against skin;
- folded fabric holds shape after release;
- hands stop before ribbon ends settle;
- hair remains under gravity while upper sections are gathered;
- pendant movement stays small and follows the hand rather than teleporting to center.

Never ask fabric or hair to behave like weightless particles.

## 11. Prop and state continuity ledger

For persistent objects, record the last visible state before directing the next scene.

Track:

- exact object identity;
- holder or world-space placement;
- relationship to nearby landmarks;
- orientation if visually important;
- next pickup/use;
- whether the transition has been shown.

Examples:

- ribbon left on north bench -> retrieve that same ribbon from the same bench location;
- slippers aligned directly under bench -> remain there through barefoot scenes -> visibly or editorially transition back onto feet before the departure shot;
- pendant off-center after movement -> only center it when the script shows the adjustment;
- cloth returned to tray edge -> do not duplicate it in the character's hand later.

If approved rendered footage contradicts an older continuity note, preserve what the audience already saw unless the user requests a retcon.

## 12. Performance transformations

Avoid abrupt labels such as `she becomes regal`, `she switches to queen mode`, or `she looks confident` when the scene can show the transformation physically.

Build the change through a sequence such as:

`breath settles -> hands complete task -> weight evens -> spine lengthens -> shoulders lower/level -> eyes redirect outward -> chin rises slightly -> expression resolves`.

Eyes often lead attention changes before the head and body. Use that order for observant, controlled characters.

## 13. One-attempt / budget-constrained generation

When the user has only one practical render attempt:

- preserve the scene's central movement and emotional payoff;
- preserve world geography and fixed lighting;
- keep a small number of strong camera phases rather than many mandatory micro-setups;
- reduce only the highest-risk simultaneous demand;
- do not automatically split a flowing performance into multiple short generations;
- make hero actions readable rather than stacking them with an aggressive orbit or unrelated insert;
- end on a clean state useful for the next scene.

Do not confuse conservative one-attempt staging with a permanent creative limitation.

## 14. Learning from generated results

Use actual user-approved renders as evidence.

Classify observations as:

- **VALIDATED SUCCESS** — technique was present and worked in the render;
- **OBSERVED FAILURE** — technique was present and visibly failed;
- **UNTESTED** — technique was removed, changed, or never rendered.

Only the first two support a real empirical lesson.

Do not infer failure from an omission. For example, removing a close-up because of budget risk and then receiving a good render does not prove the close-up would have failed.

Prefer targeted adaptation from observed failures over speculative simplification of a successful directing system.

## 15. Constraint density

Prefer a small number of strong constraints over a wall of negatives.

Always protect:

- identity;
- costume/hair/footwear;
- persistent props and their last-known positions;
- geography;
- light direction;
- action order;
- transition state.

Add activity-specific failure prevention only where needed.
