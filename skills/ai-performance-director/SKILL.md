---
name: ai-performance-director
description: Direct believable acting from AI video models (Seedance 2.5, Kling, Wan, Veo): facial expressions, emotional changes, laughs, surprise, flirting, eyelines between two people, hands handling props, dialogue delivery, and hair and wind that move like real hair. Use whenever a generated clip needs a character to feel or react, whenever a script has emotional beats, glances, banter or dialogue, whenever a previous clip overacted, looked flat, had dead eyes, the wrong eyeline, plastic or frozen hair, or felt rushed, and whenever someone asks how to make an AI face act or how many beats fit in N seconds. Pairs with cinematic-sequence-director, which owns camera, shot structure and geography; this skill owns the performance, the timing budget and the reference images that shape it.
---

# AI Performance Director

Video models perform what they are told, literally and at full size. A good AI performance comes from four things:
- **a cause the camera can see**;
- **a face designed in advance**;
- **enough seconds for it to happen**;
- **references that don't contradict each other**.

This skill encodes what worked and failed on real renders. Everything below comes from the 2026-09-30 series:
- video B original vs redo
- "The Wind Takes the Flowers", takes 1 and 2
- DUST WALL
- the garden clips

The evidence is in `references/evidence.md`. Tags: [seen] means it happened on screen; [untested] means it's reasoned but not yet rendered.

## Workflow

1. **Budget the time first** (section A). If the beats don't fit, cut beats before writing a single word of performance.
2. **Write each beat as cause → change → hold** (section B).
3. **Design the key faces as stills** in ChatGPT: the end face of each emotional turn (section C).
4. **Build references and audit every image** (section D).
5. **Write the prompt:** a performance block and a weather line in every time block (section E). For dialogue, see section F.
6. **Generate, then check at 4 frames a second** with `scripts/qc_beats.sh` (section G). Change only what failed.

## A. The time budget (why "N things in 13 s" comes out rushed)

Every beat on screen has three parts: **cause → action → settle**. The audience needs the settle to read it. Overload the model and it compresses everything, which reads as rushed or mugging.

| Unit | Minimum on screen |
|---|---|
| Establish or connect (a look, a small smile, a touch) | 3–4 s |
| Environment event building (gust, light change, a horse approaching) | 2–3 s before it lands |
| One face change (trigger → change → held face) | 3 s |
| Laugh or big release | 2.5 s + 0.5 s settle |
| One hand or prop verb (pluck, hold up, tuck, hand over) | 1–1.5 s each, + 0.5 s hold at the end |
| One spoken line | words ÷ 2.5 per second, + 0.5 s before and after [untested for lip sync] |
| A shot, if you cut | at least 3.5 s |
| A big camera size change | counts as a new shot, because the model will cut there |

**The rules:**
- **Total = sum of the minimums × 1.2.** Always leave 1–2 s of held, still-moving ending.
- **About one beat per 4 s:** 13 s holds 3 beats, 20 s holds 5.
- **At most one face change per 3 s,** per character.
- **If it doesn't fit, drop beats. Never compress them.** [seen] Take 1 had 7 beats in 20 s and was rushed. Take 2 had 5 beats in 20 s and landed.

## B. The expression method

1. **Every face beat is a change between two opposite faces** (guarded → amused, calm → startled). A face that starts where it ends has nowhere to go.
2. **A visible or audible trigger comes one beat before the face moves**: a gust, his line, her glance, an object. [seen] The gust caused believable surprise; his empty hand caused her laugh.
3. **Write the change as a timed chain in the order a real face moves:** eyes → brows → breath → mouth → head, over 1–2 s, then hold.
   - Example: "(4.8) her eyes widen; (5.1) her breath catches and her lips part; (5.8–8.0) her eyes follow the flowers up to frame right, and her head tips back after them."
4. **Never name mugging expressions.** Pout, smirk, eye-roll, wink, nose scrunch, raised eyebrow, "sassy", "mock-stern", "really?". [seen] "Pout" rendered as a duck-face. Describe muscles and behaviour instead: "one corner of her mouth lifts", "she presses her lips together to hold back a smile".
5. **Restraint is a ceiling, not a performance.** Restraint text alone gives control but flatness [seen, video B redo]. Get size from a strong cause, not from adjectives.
6. **Body carries big emotions.** A laugh is "bursts into a laugh, leans back on both hands, head back, shoulders shaking" plus about 2.5 s [seen]. "Laughs" in 1 s barely registers [seen].
7. **Surprise drifts toward a gaping "O".** Write "lips part", and add "a wide open gaping mouth" to AVOID [seen].
8. **Faces stay human:** "real, unposed faces, pores visible, no retouching".

## C. Design faces first, as stills

- Make the end face of each key turn as a ChatGPT still, with the identity image and angle sheet attached. Write the face as muscles: "brows lifted, lips parted on a caught breath, eyes up and to frame right".
- Pass it to the video model as "Image N = her face at about X s: expression only, not a separate shot" [seen: stills A and C reproduced almost pose for pose].

## D. References: the images are part of the prompt

1. **Every image leaks everything in it**: sky, light, faces, eyelines, props. "Use it for X only" does not stop the leak. [seen] A wind grid's storm clouds darkened the whole sky, and its amused faces fought a "crestfallen" line.
2. **Audit every image before upload:**
   - Where does every pair of eyes point?
   - What expression is on each face?
   - What light and sky is it?
   - Is any hand covering what must be seen?
   
   [seen] A reference with her gazing past him made the video's eyeline miss him.
3. **Grids:**
   - A multi-panel storyboard is a **cut list**: the model cuts at every panel boundary [seen: six panels gave 5 cuts].
   - A 2×2 grid labelled "four moments inside ONE continuous shot; adds no cuts" gives detail with no cuts [seen twice].
   - Draw the end state you need to see, for example "hand comes away, poppy visible".
   - Add: "Its labels are notes for you only and never appear in the video" [seen: no text leaked].
   - If a grid panel also shows the opening moment, it must match the start frame exactly. Otherwise the clip opens on the grid panel instead of the start image [seen: a stylised 3D test].
4. **Don't give stills of fast motion** (particles, hair, fabric in flight). They come back frozen. Describe speed in words instead [seen].
5. **Hair structure lives in the identity image.** A sculpted short curl bob stays stiff whatever the prompt says [seen]. Use loose hair with weight.
6. **A start frame from an approved take** keeps look and staging identical across retakes [seen].

## E. Writing the prompt

- Keep the structure of cinematic-sequence-director: geography, references, time blocks, sound, AVOID.
- **In each time block, write three lines:**
  - the performance chain;
  - **THE AIR:** what the wind, hair, cloth and particles do right now;
  - the camera.

  [seen] A weather line per block ended frozen petals and frozen hair.
- **Wind comes in gusts at named seconds, with calm in between.** Never "steady wind", which renders as one frozen windswept shape [seen]. Hair follows head moves a moment later, and the ends settle last. Rim-light the hair against a dark background so it reads.
- **Particles and objects:**
  - state their speed ("each petal crosses the frame in about a second, blurred");
  - state how they break ("torn apart in their hands, never as one bunch");
  - state how they end ("falls and lands on the bonnet").
  - **The camera never follows particles**, or they freeze in frame [seen].
- **Two people:**
  - stage them side-on, or clearly at frame left and frame right;
  - write eyelines by screen direction ("up and to frame right, into his eyes");
  - **never use "the lens" to mean a person**; add "neither looks into the lens".
- **A true single take needs near-constant framing:** one slow move in one direction. Big size changes (push to a close-up, pull back, push again) become cuts even when the prompt says "no cuts" [seen].
- **AVOID only this take's likely failures**, and keep it short.

## F. Dialogue [untested: the first dialogue film will validate this]

- **Budget:** about 2.5 words per second of speech, plus 0.5 s before and after each line. Use at most 2 short lines per 5 s. The **speaker's** face doesn't change mid-line. The **listener's** face should work *during* the line: small changes (a brow, a breath, eyes moving) land on trigger words inside it, and the big changes come in the silence after it.
- **Put the camera on the listener for the important lines.** The speaker is heard with their mouth off-screen or soft in the foreground, and the listener's face tells the story. Split long lines into phrases with short pauses, so each phrase lands on the listener's face before the next one starts. (This was the creator's direction for dialogue films.)
- In the prompt, write "we hear him; his mouth is not visible; her lips stay closed and still while he speaks".
- **The listener's face is half the scene.** Give every line a reaction beat on the listener (trigger → change → hold). Flirting is mostly timing: the pause, the glance down and back, the smile held back.
- **Put each line in quotes, with who says it, when, and how:**
  - `(6.0–8.0 s) HE says, low and amused: "…"`
  - Do not write "lips moving as if talking" in AVOID for dialogue clips; write "no one speaks except the lines given".
- **Keep lines short and speakable.** Subtext beats exposition.
- **Decide the voice route before writing:** model-native speech vs separate TTS plus lip-sync (for example MuseTalk). Then test one line before the whole scene.

## G. Checking a render

- `scripts/qc_beats.sh <video.mp4> <outdir> "name start dur" ...` prints every cut (scene score above 0.3), a 1 fps sheet, and 4 fps strips per beat.
- **Check per beat:**
  - the start face and end face are present;
  - the change happens on camera;
  - eyelines hold;
  - no banned face;
  - particles and hair are moving;
  - the number of cuts matches the plan;
  - no text leaked.
- **Checking by eye at normal speed misses these faults.** Always use the strips.
- **After a miss, classify it:** seen failure, validated success, or untested. Fix only what failed.
