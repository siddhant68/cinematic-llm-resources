# Grids and storyboards: which kind, and how video models read them

Four different things get called a "grid". Pick by their job.

| Kind | What it is | Made with | Goes into video as |
|---|---|---|---|
| **Angle sheet** (character sheet) | One instant, six or nine camera positions | ChatGPT: our T7 (six views), or a nine-angle variant. Square 1:1 output | An **identity reference** (Image 2 or 3). Never as a board, because its panels are not story beats |
| **Timed storyboard** (shot map) | The story beat by beat, each panel a shot, with timecode, title and one action line | ChatGPT: a 3×3 board or our T14/T15 (2×3). Use a 9:16 sheet when the panels are vertical | A **cut list**: Seedance makes about **one hard cut per panel boundary** (take 1 of the wind film: a 6-panel board gave exactly 5 cuts). Use it when you *want* those cuts |
| **Detail grid** | 2×2 moments **inside one continuous shot**, the same framing in every panel | ChatGPT: our T16 ("These four panels are NOT separate shots") | Adds **no cuts**. Makes hand and prop actions readable. Use it for one-take clips |
| **Exact board** | Approved stills placed side by side, real pixels | `scripts/make_board.py` (Pillow, no labels) | A shot map where **panel 1 is exactly the start frame**. The safest board for video |

## Rules that came from real takes
1. **Board panel 1 must equal the clip's start frame exactly**, or the model opens on the panel and ignores the start image. That happened on a stylised 3D test: it opened on the grid's top-left panel.
2. **For a one-take, every panel must share the start frame's framing.** On Violet clip 3, the grid's panels were wider than the start frame; the clip opened at the grid's framing and caused a jump cut in the edit.
3. **Everything in a panel leaks,** not only what you meant it for. The sky, light, faces, eyelines and even a panel's mood get copied. Audit every panel in every respect. The "use it for X only" line does not stop the leak.
4. **A still of fast motion becomes frozen motion.** A bouquet frozen mid-air made petals park in the sky. Describe speed in the video prompt, not in a frozen panel.
5. **An eyeline in a reference is copied.** Check where every pair of eyes points before uploading.
6. **Labels:** with ChatGPT boards, add "labels are notes only, no text ever appears" to the video prompt. That line worked: no panel text leaked. Prefer exact boards (no text) for anything going straight into a model.
7. **Panel size:** a 6-panel board gives each moment about 470 px; a 2×2 gives about twice the detail. Use a big board for the order of events and a 2×2 for the hard moments.
8. **Draw the END state** of a hand or prop action (the hand coming away, the poppy visible), not just the action.

## Timing a storyboard (so the video isn't rushed)
- About **one beat per 4 s**. Every action is cause → action → settle. A face change needs at least 3 s; a laugh needs 2.5 s plus a settle; a shot needs at least 3.5 s if you cut.
- A 15 s / 9-panel board (1.5 s each) is a **planning** board. For one Seedance clip, merge it into 4–6 beats. Never pack 9 actions into 15 s; that is what made our early clips rushed and mugged.
- Write the panels with **the action never resetting** between them; only the camera and the framing change (T14).
- **Fix across all panels:** faces, outfits, the place, **one light direction**, the wind direction, and "what must not appear before panel N".

## Angle-grid tips
- Upload the image, use a **1:1** aspect ratio, and paste the prompt.
- Wide panels lose face detail. Cut a panel for a start frame only if its face holds up at full size; otherwise regenerate that angle as its own still (Stage 4, with the identity and the sheet attached).
- Cut panels with `scripts/split_grid.py sheet.png --rows R --cols C --out-dir … --crop916`.

## Handing off to video
For each clip, pass:
- the **start frame** (9:16 crop);
- the **identity image(s)**;
- the **angle sheet(s)**;
- the **board** (an exact board for cuts, or a T16 detail grid for one-takes);
- the **END-face still(s)**.

The order of the media list = the image numbering in the video prompt. Prompt-writing then belongs to the `ai-performance-director` and `cinematic-sequence-director` skills.
