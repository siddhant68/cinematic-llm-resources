# Higgsfield — Nano Banana Pro and Kling 3.0

Everything here was read from the live model catalogue or measured with
`get_cost: true`, which preflights a price without submitting a job. Re-measure
rather than trusting these numbers if a plan hinges on them.

Check the balance and plan first: `balance` → `{credits, subscription_plan_type}`.

---

## The two models, exactly

### `nano_banana_pro` — images

| | |
|---|---|
| Provider | Google (Gemini 3 Pro Image) |
| `resolution` | `1k` · `2k` (default) · `4k` |
| Aspect ratios | 1:1, 3:2, 2:3, 4:3, 3:4, 4:5, 5:4, 9:16, 16:9, 21:9 |
| Reference media | role `image_references`, up to 14 |
| Strengths | text rendering, diagrams, photoreal, layout reasoning |

It *reasons about the scene* before drawing, which is why it holds a layout and
renders legible text where most image models smear it. That makes it the right
tool for a diagram, a labelled frame, or a title card — not just a pretty plate.

### `kling3_0` — video

| | |
|---|---|
| `duration` | **3–15 seconds** (default 5) |
| `mode` | `std` (default) · `pro` · `4k` |
| `sound` | `on` (default) · `off` |
| Aspect ratios | 16:9, 9:16, 1:1 |
| Reference media | roles `start_image`, `end_image` |

**Two corrections to common assumptions:**

1. **Kling is not capped at 8 seconds.** It runs 3–15. The 8s figure comes from
   older Kling versions.
2. **`sound` defaults to `on`, and audio costs 33% more.** B-roll sits under a
   voiceover, so it must be silent. **Always pass `sound: "off"`.** Forgetting it
   is a pure waste of a third of the video budget.

`start_image` / `end_image` are the first/last-frame controls. Passing the same
still as both is what makes a plate loop.

---

## Measured costs

Images (`nano_banana_pro`):

| resolution | credits |
|---|---|
| 2k | **2** |
| 4k | **4** |

Video (`kling3_0`, `sound: off`):

| duration | std | pro | 4k |
|---|---|---|---|
| 3 s | **4.5** | — | — |
| 5 s | **7.5** | 8.75 | 30 |
| 8 s | **12** | — | — |

`sound: on` at 5 s std costs **10** instead of 7.5.

The rate is linear: **1.5 credits/second** at std, 1.75 at pro, and **6 at 4k**.

**4k is four times pro for the same clip.** A B-roll cut that is on screen for
three seconds inside a 1080p delivery cannot justify that. Use `std` for B-roll,
`pro` only for a hero shot that holds the frame.

### What a 60-credit ceiling actually buys

| plan shape | cost |
|---|---|
| 8 × 5 s std silent | 60 |
| 5 × 8 s std silent | 60 |
| 30 × 2k stills | 60 |
| **10 stills + 5 × 5 s video** | **57.5** ← the shape to aim for |

The mixed shape is the recommendation, for the reason below.

---

## The workflow that makes the budget go further

**Iterate on stills, then generate video once.**

A 2k still is **2 credits**. A 5-second std clip is **7.5**. So exploring a look
costs 3.75× more in video than in stills, and video iterations are where budgets
die — you spend five generations discovering what you wanted instead of
producing it.

```
1. Generate 3-4 stills exploring the shot          2 credits each
2. Pick one                                        free
3. Feed it to Kling as start_image                 7.5 credits, already art-directed
```

That converts most of the iteration cost to image rates and means the one video
generation starts from a frame you have already approved.

For a **looping plate**, pass the same still as `start_image` *and* `end_image`.
Identical endpoints make the loop *compatible*, not seamless — velocity can still
mismatch — so watch three cycles before accepting it.

---

## Prompting Nano Banana Pro

Google's own structure, six parts:

**Subject · Composition · Action · Location · Style · (Editing instruction)**

```
A single desk lamp throwing a warm pool of light across a dark plaster wall.
Extreme close-up, shallow depth of field at f/1.8, the lamp just out of frame
left. Nothing else in shot. Photoreal, 35mm, warm tungsten, heavy falloff into
shadow. 16:9.
```

**Do:**
- Use cinematographer vocabulary — focal length, aperture, angle, light quality.
  It responds to `low-angle`, `f/1.8`, `golden hour backlighting`, `macro`.
- State aspect ratio and resolution in the prompt as well as the parameter.
- State text **exactly** as it should appear, in quotes, when you want text.
- Give each reference image a **role** when passing several.
- Prefer a focused short prompt over a long one.

**Don't:**
- Stack competing styles or viewpoints — "cinematic photoreal anime watercolour"
  produces mush. Conflicts beat length.
- Repeat yourself for emphasis. It does not increase weight; it adds noise.
- Trust small text or data in a generated diagram. Google explicitly warns to
  verify factual accuracy — **read the rendered text before you place it**.
- Expect character consistency to survive heavy editing.

---

## Prompting Kling 3.0

The failure everyone makes: **prompting a video model like an image model.** A
list of visual attributes gives Kling nothing to animate. It generates *motion*,
so the prompt must say how the shot moves.

Structure:

**Camera movement · Scene · Subject action · Light/mood · Time**

```
Slow dolly push toward a fireplace in a dark room. Flames rise and settle,
throwing moving light across a stone hearth. Warm amber key from the fire only,
deep shadow beyond. Grain, soft highlight bloom. No people. Static frame edges.
```

**Do:**
- Use real camera terms: `dolly push`, `whip-pan`, `tracking shot`, `crash zoom`,
  `snap focus`, `macro close-up`, `POV`, `profile shot`. It understands them.
- Describe **how the scene evolves**, not just what is in it.
- Add tactile detail — grain, lens flare, reflection, fabric sheen, condensation,
  smoke. These are what read as physically real.
- Keep single-shot B-roll prompts to roughly **20–50 words**. Longer prompts are
  for multi-shot or dialogue work, where 100–250 is normal.
- For **image-to-video**, treat the start image as an anchor and describe only
  the *change*: what moves, how the camera drifts, how the light shifts. Do not
  re-describe the picture you already supplied.
- Name subjects consistently if there is more than one. Pronouns confuse it.

**Don't:**
- Write `moves`, `goes`, `changes` — generic verbs produce artifacts.
- Compress several shots into one paragraph. Label them separately.
- Ask for on-screen text. That is Nano Banana's job, or your typography layer's.
- Generate people doing ordinary things. Stock is better, free and instant, and
  generated humans still read as generated.
- Leave `sound: on`. Silent B-roll, every time.

**Parameter surface is small.** There is no negative prompt, no seed, no CFG —
`duration`, `mode`, `sound` and the two image roles are all there is. Everything
else lives in the prompt text, so the prompt has to carry it.

---

## From a requirement to a prompt

This is the part that decides whether generation helps or wastes money. Do it in
three steps, in order, and never skip the first.

### Step 1 — triage the cue. Most are not generations.

A script's visual cues are not all the same kind of job. Sorting them first is
where most of the budget is saved:

| The cue asks for | Where it belongs | Cost |
|---|---|---|
| On-screen words, a title card, a term appearing | **Palmier `add_texts`** | free |
| A list, a label, a definition, a comparison in text | **Palmier typography** | free |
| "Talking head", "stay on face" | **nothing — hold the shot** | free |
| Their own output, screen recording, before/after | **their footage** | free |
| A real-world object, place or texture | **free stock first** | free |
| A thing that must be *specifically* this, and does not exist | **Higgsfield** | credits |

Real examples from a script in this project:

- `Words appear one by one: SHOT. CAMERA. FRAME. PEOPLE.` → **typography**.
  Generating text-in-image here would be slower, cost credits, and look worse
  than a clean type animation.
- `Cut to black. THE VIDEO MODEL ISN'T THE DIRECTOR.` → **typography**.
- `Talking head. Keep the eight words visible somewhere cleanly.` → **hold the
  shot** plus a persistent text layer.
- `two characters rigidly facing each other / a prop changing position` →
  **generation**, because it must demonstrate a specific failure that no stock
  clip contains.

**If the cue is text, it is never a generation.** Nano Banana renders text well
for a *poster*; it is the wrong tool for a caption in your own video, where the
typography layer already has your font, your accent colour and your animation.

### Step 2 — write the requirement before the prompt

State what must be **true in the frame** for the spoken line to land. One
sentence, no adjectives about mood. This is what you check the output against
later, and it is what goes in the `rationale` column of the plan.

> Line: *"A prop disappears in the next shot."*
> Requirement: two frames of the same room from the same angle, where one clearly
> visible object is present in the first and absent in the second, with
> everything else unchanged.

Notice that the requirement dictates the *technique* — it needs two shots that
match, which means one generation and one edit of it, not two independent
generations that will not match.

### Step 3 — translate to the model

**Nano Banana Pro** — Subject · Composition · Action · Location · Style:

```
A modern living room interior with a blue ceramic vase on the coffee table.
Eye-level medium-wide shot, 35mm, shallow depth of field. Late afternoon light
from a window camera-left. Photoreal, neutral colour, no people. 16:9.
```

Then for the second frame, pass the first as `image_references` and give an
**editing instruction**, not a fresh description:

```
Same room, same camera position, same light. Remove the blue vase from the
coffee table. Change nothing else.
```

**Kling 3.0** — Camera · Scene · Action · Light · Time. Describe the *motion*:

```
Slow dolly push into the living room. The camera drifts forward past the coffee
table; dust moves in the window light. Late afternoon key from camera-left,
soft shadow falloff. Grain, gentle highlight bloom. No people.
```

### The consistency techniques that matter here

**One master still, then crops.** When a cue asks for the *same scene at several
shot sizes* — a very common teaching device — do **not** generate five shots.
Generate **one 4k still** (4 credits) and crop it to wide / medium / close /
detail in Palmier. That is cheaper than five 2k generations (10 credits) and it
is the only way the five shots will actually match, which is the entire point of
the sequence.

**Chain with `start_image`.** For a sequence that must stay in one world,
generate the establishing still once, then use it as `start_image` for each
video beat. The model is anchored to a frame you approved rather than
re-inventing the space.

**Edit, don't regenerate.** To change one thing in a frame, pass the original as
`image_references` and instruct the change. Regenerating from a modified text
prompt gives you a different room.

### Prompt hygiene, both models

- **Say what is in frame, not what it means.** "A prop changing position between
  shots" is a requirement; the prompt is "a blue vase on the left of the table"
  and then "a blue vase on the right of the table".
- **Name the negative explicitly.** These models have no negative-prompt
  parameter, so exclusions go in the text: `no people`, `no text`, `no logos`,
  `no camera movement`.
- **Lock what must not vary** across a set: camera height, focal length, light
  direction, time of day, colour palette. Repeat those words verbatim in every
  prompt of the set. Paraphrasing them is what makes a set drift.
- **One idea per generation.** Two competing subjects in one prompt produces
  neither.
- **Match your own footage.** Your A-roll has a look — state the equivalent in
  the prompt (`warm tungsten key`, `shallow depth of field`, `35mm`) so the cut
  does not jolt.

### Verify against the requirement, not against taste

When the generation lands, check it against the sentence you wrote in step 2.
"Does the vase actually disappear, with the rest of the frame unchanged?" — not
"is this a nice image". A beautiful shot that does not carry the argument is a
failed generation, and re-rolling it costs the same as the first attempt.

---

## Rules for this pipeline

1. **Free stock and existing footage first.** State which source was searched and
   why it lacked the shot before spending anything. `broll-direction` has the
   evidence hierarchy; generated sits near the bottom of it.
2. **Preflight every generation** with `get_cost: true` and add it to the running
   total *before* submitting.
3. **Silent, std, 16:9** unless there is a stated reason otherwise.
4. **Batch independent requests.** `generate_image_batch` and
   `generate_video_batch` take 2–12 independent prompts. Use `count` only for
   variants of the *same* prompt. This is what makes an approved plan fast.
5. **Never `use_unlim: true` on your own initiative** — only when the user asks.
   (Checked on this account: `unlim.available` is false, so it is moot for now.)
6. **Archive every asset** with provider, model, prompt, resolution, duration,
   credits and job id, next to the media. That is the provenance record and the
   audit trail for `broll-plan.md`.
7. **Stop at the ceiling.** If the plan needs more, say how much is left, what it
   is, why it matters and what the video loses without it. Do not quietly trim
   the plan to fit, and do not spend past it.
