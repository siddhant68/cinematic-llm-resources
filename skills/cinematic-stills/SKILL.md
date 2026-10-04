---
name: cinematic-stills
description: >
  Make cinematic, mature, non-AI-looking images for a film from a script, using a proven pipeline: Pinterest casting and
  scene research (computer use and the built-in browser), ChatGPT breakdowns of each reference, our character rebuilt inside
  that world, then angle grids and timed storyboards ready for Seedance/Kling. Use it whenever someone asks to generate images,
  stills, characters, a cast, a reference character, start frames, end-face stills, scene images, a character sheet, an angle
  grid, a contact sheet or a storyboard for a movie, film, short, reel or scene, or hands over a script (with or without a
  reference character image) and wants visuals. Also use it when a previous still looked plastic, generic, AI-perfect, off-model or
  bland, or when someone asks how to make AI images look like a real film. It stops at the stage asked for: images (stage 4),
  grid (stage 5) or storyboard (stage 6).
---

# Cinematic stills: script → real cast → real worlds → grids → storyboards

**Goal:** every still should look like a frame from a prestige film, not an AI render:
- real skin, a specific face, one motivated light, a real lens;
- wardrobe that is modest and true to its era;
- a world with weather and wear;
- the same person and the same light in every image.

This skill joins two sources:
- what reels 007–010, HOLD STILL, the wind film and Violet taught us: tested templates in `references/proven_templates.md`;
- a repeatable casting-and-research process (below).

## The process, and where each step lives

| # | Step | Stage | Main reference |
|---|---|---|---|
| 1 | Find a **reference character** on Pinterest: human features, real skin, nose, eyes, lips, no AI perfection. **Skip if you already have a reference image.** | 1 | `pinterest_research.md`, T4/T5 |
| 2 | Find **cinematic scene photos** that match the script. Search exhaustively and keep varying the keywords, because this defines the film's look | 2 | `pinterest_research.md` |
| 3 | **Analyse each pin in ChatGPT** (computer use) | 3 | T1/T2/T3 |
| 4 | **The reference character + the breakdown prompt → a new image** of our character in that Pinterest world | 4 | T8–T13, `realism_and_audit.md` |
| 5 | **A grid** of that image from different angles | 5 | T7 |
| 6 | **A storyboard** for the video models | 6 | T14–T16, `grids_and_storyboards.md` |
| 7 | Sometimes only steps 1–4 are wanted: **stop there** | (stop rules) | |

## Stop rules: deliver exactly what was asked
- **"Images" or "stills"** → stages 0–4, then stop and show them.
- **"Grid", "character sheet" or "angles"** → stages 0–5. If the stills already exist, start at 5.
- **"Storyboard" or "board"** → stages 0–6. If the stills already exist, start at 6.
- **"Just the character"** → stages 0–1, plus its angle sheet.
- **Not stated** → do stages 0–4, show them, and ask whether to continue.

**Checkpoints** (show the creator a contact board made with `scripts/make_board.py`, then wait):
- **CP1:** the identity image plus its lookalike board;
- **CP2:** the pin shortlist, with a one-line *why* for each pin;
- **CP3:** the stills;
- **CP4:** the grid or board.

If the creator says "autopilot", keep going, but still log every verdict. Images cost nothing beyond the plan, so redo freely. **Video generation is not part of this skill and needs the creator's go.**

## Tools
- **Pinterest:** a browser session signed in to Pinterest (we used Claude's built-in browser). Always add `&filter_genai=true` ("Less AI"). Harvest with `scripts/pinterest_harvest.js`.
- **ChatGPT image (GPT Image 2):** the **desktop app via computer use**, in Chat mode, one fresh chat per image. **Read `references/chatgpt_app_operation.md` before the first message.** It covers pasting images through the clipboard, `pbcopy` for text, the editor-tab trap, saving files, and the 99% stall.
- **Scripts** (run with any Python that has Pillow):
  - `contact_sheet.py`
  - `fetch_originals.py`
  - `make_board.py`
  - `split_grid.py`
  - `to_9x16.sh`
- **Work folder:** `<project>/stills/`:
  - `00_plan/`
  - `01_cast/`
  - `02_pinterest/<group>/` plus `sources.json`
  - `03_breakdowns/`
  - `04_stills/`
  - `05_grids/`
  - `06_boards/`
  - `prompts/`
  - `LOG.md` (each run, what was attached, the output file, and KEEP / PARTIAL / REJECT with the reason)

---

## Stage 0 · Read the script and plan the stills (about 10 min)
Write `00_plan/STILL_PLAN.md`:
1. **Cast:** each recurring character. Age, role, era, wardrobe per scene, and permanent marks (fill these in at stage 1). Who must stay consistent, and who can be a soft background figure.
2. **World rules** (fixed for the whole film):
   - each place;
   - **one light direction per place** (e.g. "lamp at frame LEFT, moonlight from the window at frame RIGHT");
   - the time of day and weather;
   - the wind direction;
   - the palette and grade;
   - the era.
3. **Still list:** one row per image the film needs. For each:
   - id;
   - beat;
   - framing and lens (wide 24–35 mm, medium 50 mm, face 85–100 mm);
   - staging, using screen directions;
   - eyeline (a named point, never "the lens");
   - the expression **START → END** as muscles;
   - what must **NOT** be in frame yet;
   - its job (start frame, END-face reference, board panel, or plate).

   Typical film needs:
   - identity + angle sheet per character;
   - one empty place plate per location;
   - a start frame per clip;
   - an END face per emotional beat;
   - the reveal frames.
4. **Format:** vertical 9:16 unless told otherwise. ChatGPT returns 2:3 or 9:16, so crop start frames with `to_9x16.sh`.
5. **Rules for real events or adaptations:**
   - no real names in ChatGPT;
   - composite faces only;
   - no logos;
   - violence shown by its effect.

## Stage 1 · The reference character (skip if one is supplied)
**The identity rule.** A Pinterest face is a **trait source, not our actor**.
- Harvest real faces, note their traits, then **build our own character from text** (T4) with no pin attached. That built image becomes the "reference character" used in stage 4.
- Never regenerate a pin's actual face: it is a real stranger, ChatGPT may refuse, and on reel 010 the creator chose to blend traits into an original face.

1. **Harvest** 2–3 casting searches per character ("street casting portrait woman freckles natural light", "<trait> portrait 35mm film", "candid <emotion> portrait film"). Make contact sheets and keep **3–4 pins, each for a different trait**:
   - nose and lips;
   - eyes and face shape;
   - hair;
   - wardrobe and wind.
2. **Break each pin down** with T1 (one fresh chat each, up to three in parallel). Save the answers to `03_breakdowns/`.
3. **Build from text only** with T4 as the model. Write:
   - the trait blend;
   - **our own marks**: a scar, a mole, one brow higher, a lopsided smile;
   - skin as texture;
   - worn and specific wardrobe;
   - a real scene with a named key light;
   - the camera and lens;
   - the avoid line.

   Make two takes in fresh chats and pick the most specific, most frontal face.
4. **Lookalike check:** the identity image beside its pins (`make_board.py --fit contain`). It must share traits only, never a whole face, and resemble no actor or real person.
5. **Angle sheet** with T7 (identity attached, 1:1).

→ **CP1.**

**If a reference image is supplied:**
- use it as the identity;
- run T5 if it must move to our world and outfit, or to gain marks and real skin;
- run T6 for small fixes;
- then make the angle sheet.

## Stage 2 · Scene references on Pinterest (exhaustive, about 25 min)
This search defines the film's look, so it is never one query. Follow `references/pinterest_research.md`:
- **4–8 searches per scene**, built from subject + setting + light/time + medium words ("film still", "35mm film", "documentary photography"). Change one axis per search, and rephrase whenever results are AI-glossy, stock or the wrong era.
- **Search for:**
  - each **place**;
  - the **light**;
  - each key **framing** (an over-the-shoulder, a lone figure in a vast landscape);
  - each **expression beat**;
  - the **wardrobe and props**.
- **Keep 1–2 world pins plus 1 light pin per beat**, and 1 expression pin per emotional beat. Reject AI renders, text and watermarks, celebrities and actors, and catalogue shots.
- Log everything in `sources.json` (fill in `why`).
- **Research, don't just obey:** when the script leaves a look open (a dress, a room, the era), look at the options and recommend one with a reason, the way the 1950s strapped sundress was chosen for HOLD STILL.

→ **CP2.**

## Stage 3 · Break the references down in ChatGPT (about 20 min)
One fresh chat per pin: paste the pin as an image, then the template.

| Pin | Template |
|---|---|
| a world, light or mood | **T1** |
| a room or costume, and any film or show still | **T2** (never the face) |
| an expression | **T3** (muscles plus a transferable paragraph) |

Save each answer to `03_breakdowns/<slot>.md`, then **mine it**:
- the concrete nouns and positions;
- the light: direction, colour and hardness;
- the lens, the depth of field and the grade;
- the costume construction;
- the muscle actions.

Those phrases, not the pin, go into stage 4.

## Stage 4 · Rebuild: our character inside the Pinterest world (about 25 min)
**What to attach:** the **identity image** (plus the angle sheet, the place plate, and the previous still when framing must match), in the order the prompt numbers them. **Never attach a pin.**

**Writing the prompt** (structure of T8; the nine layers are in `references/realism_and_audit.md`):
1. "Use the [woman] in the attached photo exactly as she is: same face, [marks], skin, hair and clothes."
2. "Photoreal vertical 9:16 film still, [framing]".
3. The **staging** in screen directions.
4. The **world**, in the breakdown's concrete nouns.
5. The **light, lens and grade** from the light breakdown, matching the film's fixed direction.
6. The **expression as muscles**, from T3.
7. **What must NOT be in frame.**
8. "Real skin with visible pores, no retouching. Natural analogue film grade, fine 35 mm grain."
9. The avoid line, then `Aspect ratio: 9:16 (vertical).`

**Which template to model on:**

| Still | Template |
|---|---|
| establishing wide | T9 |
| reaction or END face | T10, T13 |
| reveal or reverse angle | T11 |
| several references, full figure | T12 |

**Order of work:**
1. Make **empty place plates** first (text only, no people), so every later still shares the room.
2. Make the stills **in story order**. For a sequence of close shots, attach the previous still as the framing reference.

**Audit every image** with the checklist in `references/realism_and_audit.md`:
- face and marks;
- skin;
- hands;
- eyeline;
- light direction;
- wardrobe;
- world drift;
- nothing that must not show yet;
- no text;
- it reads at phone size.

Fix with T6 ("keep everything, change only…") or a fresh run. Log the verdicts.

→ **CP3.** Stop here if only images were asked for.

## Stage 5 · Angle grid (about 5 min per still)
- **Which prompt:**
  - **T7**, our plain six-view prompt (it held faces best for us);
  - for nine named angles (MCU / MS / OS / WS / HA / LA / profile / 3/4 / back), ask for them by name, but **remove any label line** if a panel will feed video;
  - for an editorial contact sheet, **state your film's look** instead of a default flash look.
- **Settings:** the still attached, aspect **1:1**.
- Check that the face, marks, wardrobe and light hold in **every** panel. Wide panels lose face detail; that's a known limit.
- Cut panels with `split_grid.py --crop916`. If a panel will be a video start frame and its face is weak, regenerate that angle as a full stage 4 still instead.

→ **CP4**, or stop.

## Stage 6 · Storyboard for video (about 10 min per clip)
Read `references/grids_and_storyboards.md`. Video models read a multi-panel board as a **cut list**.

| The clip should be | Make |
|---|---|
| several shots, with cuts wanted | a **timed board**: a 3×3 or our T14 (2×3), or T15 when key panels already exist as approved stills. For video input, prefer an **exact board** from the approved stills (`make_board.py`), with panel 1 = the start frame |
| one continuous take | a **detail grid** (T16): "These four panels are NOT separate shots", the same framing as the start frame in every panel, the END state of hand and prop actions drawn |

**Timing:** about one beat per 4 s. Each action is cause → action → settle; a face change needs at least 3 s. Never pack nine actions into 15 s.

**Fixed across every panel:**
- faces and wardrobe;
- the place;
- one light direction;
- the wind;
- "what must not appear before panel N";
- no text other than labels.

→ **CP4.**

**Hand-off to video**, per clip:
- the start frame (9:16);
- the identity image(s);
- the angle sheet(s);
- the board or grid;
- the END-face still(s).

Prompt-writing belongs to the `ai-performance-director` and `cinematic-sequence-director` skills.

---

## Rights and hygiene
- **Pins and show stills are references only:** never attached for generation, never uploaded to Higgsfield, never published.
- **No real names in ChatGPT**, and no real-person likeness.
- **Modest, era-true wardrobe** unless the script says otherwise.

## What good looks like (proven outputs to compare against)
- **Reel 010** (the desert woman and the dust storm): `reel-010/` in this repository.
- **HOLD STILL** (the flower farm, the red car, the yellow sundress).
- **Violet** (the lamplit stone chamber, two characters): our two-character interior; the same pipeline, a different world.
