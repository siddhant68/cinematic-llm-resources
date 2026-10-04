---
name: cinematic-sequence-director
description: Direct flowing cinematic video-generation sequences from character references, environment references, scripts, prior rendered continuity, and example prompts. Use when ChatGPT needs to plan or rewrite one or more connected AI-video clips with strong camera coverage, choreography, lighting, spatial geography, prop continuity, transitions, performance arcs, or paste-ready prompts for models such as Seedance or Kling, especially when matching cinematic quality across scenes or preserving continuity between generated clips. Also use it to budget how many beats fit in a clip's duration, to decide between a deliberate cut sequence and a true single take, and to plan storyboard and grid references.
---

# Cinematic Sequence Director

## Objective

Turn the user's source materials into a small number of **paste-ready cinematic generation prompts** that feel directed as one continuous film sequence rather than a list of disconnected shots.

Preserve the freedom and flow of generative video. Use spatial and continuity constraints to stabilize the world, not to micromanage every frame.

Read [references/director-playbook.md](references/director-playbook.md) for camera, lighting, choreography, continuity, complexity allocation, and evidence rules. Read [references/output-template.md](references/output-template.md) before drafting the final prompts.

When the sequence has faces that must act, emotional changes, two people looking at each other, or dialogue, also load the `ai-performance-director` skill. This skill owns camera, structure, geography and time; that one owns the performance and the reference images that shape it.

## Input contract

Use the following inputs when supplied:

1. **Character reference images** — authority for identity, face, body proportions, hair state, costume, jewelry, footwear, and visible condition.
2. **Environment reference images** — authority for architecture, landmarks, vegetation, furniture, paths, scale, and spatial relationships.
3. **Approved prior renders / supplied keyframes** — authority for the realized continuity state entering the new clip: body position, orientation, prop location, hair state, footwear state, exertion, and the visible part of the set.
4. **Source script / continuity script** — authority for story intent, time of day, emotional state, props, required actions, and states not already contradicted by approved rendered footage.
5. **Prompt Type 1** — source for descriptive movement, performance texture, pacing, physical realism, and prose style.
6. **Prompt Type 2** — source for technical shot intent, lens/framing, camera vocabulary, constraints, and clip-specific details.
7. **Target duration** — total duration to cover. Respect user-specified clip count/durations when given.
8. **Optional provider/model constraints** — duration limits, start/end frames, multi-shot behavior, reference limitations, retry budget, etc.

Do not blindly concatenate Prompt Type 1 and Prompt Type 2. **Synthesize** them into one directorial plan.

### Authority by domain

Do not use one global precedence rule when different sources govern different facts.

- Use current character references for identity and intended costume/hair design.
- Use current environment references for set architecture and durable landmarks.
- Use an approved prior render or supplied transition frame for what has already visibly happened: where a prop was left, which hand holds it, body orientation, footwear state, hair state, and the exact transition pose.
- Use the source script for intended story beats that have not yet been realized on screen.
- Use Prompt Type 1/2 as inspiration and technical guidance, not as authority when they contradict newer evidence.
- An explicit current user instruction overrides older materials.

If an approved render and the old script disagree about a realized continuity fact, preserve the approved render unless the user asks to retcon it. Example: if the rendered scene visibly leaves a ribbon on the bench, the next scene must retrieve that ribbon from the same bench position even if an older script said it remained on the wrist.

## Workflow

### 1. Extract the continuity state before directing

Establish:

- exact character identity and visible appearance;
- costume, hair, footwear, jewelry, props;
- physical condition: fresh, flushed, sweaty, wet, injured, etc.;
- time of day and weather;
- emotional/performance mode;
- required action/choreography order;
- starting and ending state;
- previous/next scene continuity requirements.

Create a compact **continuity ledger** for persistent objects and states when they matter:

- object / state;
- current holder or exact world-space location;
- current orientation or attachment;
- next intended use;
- required transition if the state changes.

A pickup must originate from the object's last visible location. A removed costume item or footwear must not reappear without an explicit or editorially defensible transition. Do not let camera changes silently move props.

Treat names in movement prose as useful shorthand, but preserve the literal physical action too.

### 2. Profile the environment as a fixed film set

Build a stable mental overhead map from the environment references.

Choose 4–6 durable landmarks. For a circular space, prefer a **clock-face map** with the dominant central landmark as 0. For a rectangular/linear space, use directional zones and named landmarks.

Define separately:

- **world-space landmarks** — never move because the camera moves;
- **performance zones** — where the character is allowed to act;
- **camera positions** — may move independently around the fixed set;
- **light source direction** — fixed in world space unless story time materially advances.

If only one environment view exists, infer conservatively. Do not invent a new wing, doorway, fountain, staircase, or major landmark merely to create another angle.

Use numeric coordinates, lens values, angles, and distances as directing anchors, not as assumptions of exact model obedience. Pair important numbers with plain-language meaning, e.g. `10:30 / arch side / across the fountain`, or `about a three-quarter turn, ending toward the keep`.

Do not replace world-space anchors with only screen-left/screen-right when reverse angles are planned. Screen-relative directions may flip; world geography must not.

### 3. Choose the generation architecture

Design the total requested duration first, and budget it before writing any beat. Overloaded clips come out rushed: the model compresses every listed action to fit, and the result reads as hurried or mugging.

**Time budget.** Every beat on screen is **cause → action → settle**. Use these minimums, measured on Seedance 2.5 renders:

| Unit | Minimum on screen |
|---|---|
| Establish or connect (a look, a touch, a small smile) | 3–4 s |
| Environment event building before it lands (gust, light change, rider approaching) | 2–3 s |
| One face change (trigger → change → held face) | 3 s |
| Laugh or big release | 2.5 s + 0.5 s settle |
| One hand or prop verb (pluck, hand over, tuck) | 1–1.5 s each, + 0.5 s final hold |
| One spoken line | words ÷ 2.5 per second, + 0.5 s before and after |
| A shot, if you cut | at least 3.5 s; shots of 2.4–3.7 s felt choppy |

- **Total = sum of the minimums × 1.2.** End on a 1–2 s held moment that is still moving.
- **Rule of thumb: about one beat per 4 s.** A 13 s clip holds 3 beats; a 20 s clip holds 5.
- **If the beats don't fit, drop beats. Never compress them.** Evidence: 7 beats in 20 s was rushed; the same story cut to 5 beats in 20 s landed.
- Show the budget as a small table in the directorial map.

- If the user specifies the number of clips/scenes, obey it.
- If one requested sequence is longer or more complex than a reliable single generation, split it into the **fewest useful clips**.
- For a roughly 30-second performance with no other constraint, normally prefer **two flowing clips of about 14–16 seconds each**, adjusting around the choreography rather than forcing equal halves.
- Do not return to one-action-per-clip fragmentation.

Choose the breakpoint because it is cinematically invisible or emotionally natural, not because a timer expired.

Prefer breakpoints such as:

- full or partial occlusion behind fountain/column/tree/person;
- spinning skirt or hair crossing frame;
- camera passing behind foreground foliage or architecture;
- a travel move from one performance zone to another;
- a clean pose/beat hold;
- a breath or musical phrase ending;
- an intentional change of direction or energy.

Define the final frame/state of Clip A and opening state of Clip B so continuity is explicit.

If a transition uses an occlusion, substantial natural obscuration is usually enough; do not demand mathematically complete hiding unless the edit truly requires it.

### 4. Account for the user's render budget

When the user has multiple attempts, keep more ambitious alternatives available and repair only demonstrated failures.

When the user has only one realistic render attempt, **reduce simultaneous risk without flattening the scene**:

- preserve the central choreography and emotional beat;
- preserve spatial geography and lighting continuity;
- simplify only the highest-risk simultaneous demand;
- do not automatically fragment the scene into many short clips.

Use the complexity-allocation rule:

> **When the performer is doing the hardest thing, let the camera become simpler. When the performer is in a simpler or stable phase, the camera may become more expressive.**

Examples:

- full spin + long skirt + loose hair -> stable readable full-body camera;
- hair tying or intricate hand work -> quiet medium camera;
- straightforward travel -> tracking or counter-move can add energy;
- stable recovery beat -> close-up or subtle push may reveal emotion.

Avoid stacking several high-risk axes at once unless the user specifically wants the gamble.

### 5. Set performance energy before choosing camera work

Infer the sequence's energy from the script and user request.

Examples:

- meditative/yoga -> long holds, restrained arcs, slow pushes, breath details;
- playful dance -> traveling camera, counter-moves, footwork, face reactions, skirt/hair motion, more frequent but motivated angle changes;
- duel/action -> readable geography first, then impact details and controlled dynamic movement;
- intimate grooming/transformation -> hands, breath, eyes, posture, restrained camera;
- emotional beat -> longer lenses, subtle pushes, eyeline and hand detail.

Do not apply the same camera rhythm to every activity.

### 6. Design choreography and camera together

For every major movement phrase, answer four things:

1. **What exactly does the performer do?**
2. **Where in the fixed environment do they do it?**
3. **What is the best camera scale/movement for that beat?**
4. **What emotional or physical detail should the viewer notice?**

Use recognized pose/step/movement names when confident, followed by a literal physical description.

For dance, pair any production shorthand with explicit footwork/body direction so a video model does not have to infer the move from the name alone.

Keep high-risk simultaneous actions limited. Do not ask the model to solve intricate hand contact, a face close-up, a full spin, prop transfer, and a complex camera orbit at the same instant.

### 7. Direct camera coverage as a film sequence

Use a deliberate range of coverage, selected because each angle reveals something new:

- environmental wide / master;
- full-body or medium-wide for readable choreography;
- medium for torso, expression, hands, and relationship to background;
- close-up for face, breath, eyes, hands, satisfaction, fatigue, or transformation;
- extreme detail for feet, fingers, pendant, sweat, fabric, or contact when truly motivated.

Specify approximate lens feel when useful. Vary lenses intentionally; do not decorate every beat with arbitrary focal lengths.

Keep character world position independent from camera position. Explicitly state when a reverse angle, close-up, or arc **does not mean the performer has moved**.

Do not overcut. Let important movement phrases complete in readable coverage. Close-ups should usually occur during a hold, stable step, landing, recovery, predictable repetition, or other lower-risk moment. Energetic dance may cut on motion, but preserve body logic across the cut.

Treat a list of camera ideas as a **coverage priority**, not a demand that every idea become a separate hard cut inside the generation. Combine compatible phases into flowing coverage when duration is tight.

**Cuts vs one take: what the model actually does** (Seedance 2.5, observed):

- **A described shot list becomes hard cuts** at exactly the listed boundaries. A six-shot structure gave 5 cuts.
- **A described big framing change becomes a cut even when the prompt says "no cuts".** Examples: push in to a close-up, pull back to a two-shot, push in again. Asking for three such moves gave three cuts.
- **A true single take needs near-constant framing:** one slow move in one direction (for example a gentle push-in from a medium to a medium-close). That held as one take.
- So decide first: **a cut sequence** (plan each cut on an action beat, each shot at least 3.5 s, with action continuing across the cut), or **one take** (one framing family, one gentle move). Don't ask for "no cuts" and then describe several shot sizes.

**The camera must not follow particles** such as petals, dust, sparks or leaves. A camera that tracks them makes them look frozen in the frame. Hold the camera and let them cross the frame and leave it.

### 8. Light the world, not each shot independently

Derive the lighting from script time, weather, and environment.

Define:

- source direction in world space;
- key/back/rim relationship;
- fill from stone, water, walls, sky, foliage, or practicals;
- background light;
- how the light evolves over the total sequence.

When the camera crosses to another side, describe how the **same fixed light source** now becomes side-light, backlight, rim light, etc. Never flip the sun merely to flatter a new angle.

Use light to support the performance arc. Keep it physically plausible and visually specific.

**Describe the air in every time block.** Each timed block of the prompt gets an "AIR" line: what the wind, hair, cloth, grass and particles are doing at that moment. Without it, hair freezes into one shape and particles hang.
- **Wind comes as gusts at named seconds with calm in between.** A "steady wind" renders as one frozen windswept pose.
- **For objects that break or fly, state all three:**
  - how they break: "torn apart in their hands, never as one bunch";
  - how fast they move: "each crosses the frame in about a second, blurred";
  - how they end: "falls and lands on the bonnet".
- **Rim-light moving hair and fabric against a darker background** so the motion reads.

### 9. Protect identity and continuity without suffocating motion

Lock only continuity-critical facts:

- same character identity;
- same costume/hair/jewelry/footwear state;
- same persistent props and exact last-known placements;
- same set geography;
- same light direction;
- same travel direction when continuity depends on it;
- physically plausible cloth/hair/pendant inertia;
- progressive exertion rather than resets.

If a prop or state must change, stage the change once and carry the new state forward.

Avoid long generic negative-prompt dumps. Include hard constraints that prevent likely failures for the particular sequence.

### 10. Make each clip independently usable

Each final clip prompt must restate the essential reference state and geography it needs. Do not make Clip B depend on the model remembering text from Clip A.

However, connect clips with an explicit continuity opening such as:

- `Clip A ends while her body is mostly hidden behind the fountain.`
- `Clip B begins from the reverse side as she emerges, completing the same clockwise movement.`
- `The ribbon remains on the north bench in the exact spot established earlier; she retrieves that same ribbon before tying her hair.`

When a clean image handoff is available and useful, use it. Do not force a poor, motion-blurred, or heavily occluded last frame as a start image merely because it is chronologically last; an editorially concealed transition may be more robust.

A clean frame from an approved earlier take makes an excellent start image for a retake: it keeps the look, the staging and the identities identical.

### 10b. Storyboards and grids as references

- **A multi-panel shot map is a cut list.** The model cuts at every panel boundary. Use one only when you want those cuts. It is excellent for a deliberate sequence (a six-beat thriller board worked as intended).
- **A 2×2 detail grid labelled as moments inside one shot adds no cuts.** Label it "four moments inside ONE continuous shot; it adds no shots and no cuts". It gives large, readable panels for the hardest moment: hand and prop work, or a physical event in phases. Draw the end state that must be visible (e.g. "hand comes away, the poppy is clearly visible").
- **Every panel leaks everything in it:** sky, light, faces, eyelines, props. "Use it for the wind only" did not stop a grid's storm clouds from darkening the whole sky. Every panel must be right in every respect, or it must not be attached.
- **Don't attach stills of fast motion** (petals or dust frozen mid-air). They come back as frozen motion. Describe speed in the text instead.
- **Always add:** "Its panel labels are notes for you only and never appear in the video." No label text leaked with this line.
- Audit every reference before upload: eyelines, expressions, sky and light, and whether anything covers what must be seen. The `ai-performance-director` skill has the full checklist.

### 10c. Two people in one frame

- **Stage them so the eyeline is obvious:** side-on, or clearly at frame left and frame right.
- **Write every eyeline by screen direction and target:** "she looks up and to frame right, into his eyes".
- **Never use "the lens" to stand for a person.** Always add "neither of them looks into the lens".
- A point-of-view camera that still shows the other person's shoulder makes the looker stare at the audience instead of at the partner.

### 11. Learn only from evidence that actually exists

Treat user-approved generated results as valuable empirical evidence, but generalize conservatively.

- If a technique was present in a successful render, it is evidence that the technique can work in that context.
- If a risky technique was removed before a successful render, **do not infer that the removed technique would have failed**.
- Do not blacklist close-ups, camera moves, turns, lenses, or edit styles merely because they were omitted as a precaution.
- Distinguish **validated success**, **observed failure**, and **untested hypothesis**.
- Prefer targeted changes based on actual failures over speculative simplification of an already successful directing approach.

This evidence discipline applies when carrying lessons from one scene to another. Preserve the successful principles without turning untested risk mitigations into permanent rules.

### 12. Direct transformations through behavior, not labels

When the dramatic beat is an internal transformation, express it through visible progression rather than an abrupt instruction such as `becomes regal`.

Useful sequence:

`breath changes -> hands settle -> weight redistributes -> shoulders level -> spine lengthens -> eyes redirect -> expression resolves`.

The eyes often change before the head and body. Let posture and attention communicate composure, fatigue, delight, fear, or readiness.

### 13. Run the directorial quality gate

Before returning the answer, verify all of the following:

- total durations approximately sum to the user's target;
- the time-budget table fits (about one beat per 4 s, face changes at least 3 s apart, every shot at least 3.5 s); if not, beats were cut rather than compressed;
- the cut plan is explicit: either a deliberate cut sequence, or one take with near-constant framing, never "no cuts" alongside several shot sizes;
- no multi-panel shot map is attached unless its cuts are wanted; detail grids are labelled as moments inside one shot;
- every attached reference was audited for eyelines, expressions, sky and light, and nothing that contradicts the text is attached;
- every time block has an AIR line; wind comes in timed gusts; particles have a speed and an ending; the camera never follows particles;
- two-person eyelines are written by screen direction, and nobody looks into the lens;
- required choreography/actions are covered in correct order;
- named movements are paired with clear physical descriptions;
- each performer has a predictable world-space position;
- persistent props have a valid holder/location before and after the sequence;
- removed footwear or accessories do not reappear without a transition;
- environment landmarks never teleport, mirror, or rotate;
- camera angles are varied and motivated without overcutting;
- at least one wide/full-body view preserves choreography readability when needed;
- close-ups reveal story/performance details rather than existing for decoration;
- lighting direction is physically consistent across reverse angles;
- energy and camera rhythm match the scene's emotion;
- the clip breakpoint is a usable continuity bridge;
- Clip B has a precise opening state from Clip A;
- costume/hair/props/exertion states do not reset;
- difficult performer actions are not unnecessarily stacked with difficult camera moves;
- prompts remain flowing enough for generative video rather than becoming frame-by-frame animation instructions.

Fix any failure before responding.

## Output requirements

Return:

1. **A concise directorial map** — total duration, clip split, performance zones, principal light direction, transition strategy, and important continuity carryover.
2. **One complete paste-ready prompt per generated clip**, following [references/output-template.md](references/output-template.md).
3. **A brief final note only when useful** explaining the key continuity/directing decision or deliberate risk allocation.

Do not output a generic shot list unless the user asks for one. The primary deliverable is **continuous cinematic generation prompts**.

When the user asks for a specific activity, adapt the camera tempo, performance language, movement names, and emotional behavior to that activity instead of copying a successful prior scene literally. Preserve the directing principles, not the surface choreography.
