# Reel 014 · HOLD STILL

The prompts, images and rules behind the AI short film **HOLD STILL**, and behind the tutorial made from it: *How to control over-acting in AI characters*.

A woman waits in a flower field by a red car. He arrives late with wildflowers from the lane. She plans to stay cross, but the wind won't let her. The film is 38 seconds with no dialogue, made from three Seedance 2.5 clips on Higgsfield. Three other clips failed on the way, and each one taught a rule. Everything here is real: the exact prompts we sent, the images we attached, and what came back.

All characters, places and images are AI generated. Results will vary with models and references.

The tutorial, [How to control over-acting in AI characters](https://www.instagram.com/cinematic_llm/reel/DeHjJCTBT1m/), and [the film](https://www.instagram.com/cinematic_llm/reel/DeHjZLvhbza/) are on Instagram.

## The six generations

| # | Clip | Higgsfield job | Settings | Credits | In the film? | Prompt |
|---|---|---|---|---|---|---|
| 1 | Alone at the car | 6b1f7119 | 7 s, 720p | 49 | yes | `prompts/1_…` |
| 2 | He brings flowers, first attempt: **overacting** | 448b68f4 | 13 s, 720p | 91 | no | `prompts/2_…` |
| 3 | He brings flowers, the restrained redo (**acting**) | cf2f7ab9 | 16 s, 720p, one take | 112 | yes | `prompts/3_…` |
| 4 | An eyeline miss | fd1333c8 | 13 s, 720p | 91 | no | `prompts/4_…` |
| 5 | The wind takes the flowers, take 1: a six-panel shot map | a34b90ef | 20 s, 480p | 60 | no | `prompts/5_…` |
| 6 | The wind takes the flowers, take 2: one take | 29b200e0 | 20 s, 480p | 60 | yes, from 4.04 s | `prompts/6_…` |

All six used Seedance 2.5 in `omni_reference` mode with audio on. Price per second: 7 credits at 720p, 3 at 480p. The three clips in the film cost 221 credits; all six cost 463.

## What is in the folders

- `prompts/`: the six video prompts exactly as sent, with the verdict in the file name, plus two reusable files: the performance block with its ban list, and the prompt skeleton.
- `chatgpt_prompts/`: the ChatGPT image prompts, in the order we used them: identity, angle sheet, car, start frames, her surprise and her laugh, the boards and grids, and the three hair edits that fixed the plastic hair (`19`–`21`).
- `images/`: the generated references and start frames, named for what they did.
- `clip_frames/`: three frames from each of the six generations, so you can see each result without opening a video.

## The rules, with their evidence

1. **Write the feeling in her body, not her face.** The first prompt named six faces in 13 seconds: an eye-roll, a raised brow, a sideways pout, narrowed eyes, a sucked-in cheek and a nose scrunch. The model played every one at full size (`clip_frames/2_…`). The redo wrote posture, arms, where she looks and her breath, and allowed one small face change at about a third of its full size (`prompts/7_…`).
2. **Ban the mugging faces by name.** The redo's constraint list is in `prompts/7_…`.
3. **Big emotion needs a cause on screen.** After the redo her performance was controlled but less expressive. In the wind clip the gust causes her surprise and his empty hand causes her laugh; both are big and both read as real (`clip_frames/6_…`).
4. **Hair: long, heavy, and moved by a physical cause.** A short curl bob froze into one shape even though the prompt said "steady wind". We regenerated the identity, start frame and angle sheet with longer, looser, heavier hair (`chatgpt_prompts/19`–`21`, `images/01` vs `03`), named gusts at set seconds (1.5, 7 and 12 s in `prompts/3_…`), and wrote a `THE AIR:` line in every time block (`prompts/6_…`).
5. **Name the eyeline by screen direction.** `prompts/4_…` says her eyes "settle on the lens, on him". She looked at the audience (`clip_frames/4_…`). `prompts/3_…` says "up and to frame right, straight into his eyes".
6. **A multi-panel board is a cut list.** The six-panel board (`images/18`) gave exactly five cuts, one at each panel edge (3.0, 5.4, 8.7, 12.0 and 15.4 s). A 2×2 grid labelled "four moments inside one continuous shot" (`images/21`) added none.
7. **One beat per 4 seconds.** Take 1 packed seven beats into 20 seconds and felt rushed. Take 2 had five and landed. Cut beats, never squeeze them.
8. **Say how things break.** "Bursts apart" flew away as one bunch (`clip_frames/5_…`). "Torn apart in their hands, never as one bunch" worked (`prompts/6_…`).
9. **Big framing changes become cuts.** Take 2 asked for no cuts and got three (4.04, 7.9 and 14.8 s). A single slow move in one direction stays one take (the redo, `prompts/3_…`).
10. **In the edit:** a dissolve only where time passes (clip 1 to clip 2), drop the repeated action (the first 4 s of the wind clip re-staged the hand-off), and cut on the motive (into the gust). Every clip plays at real speed.

## Honest notes

- The overacting vs acting pair is **not a one-variable test**. Same face, same story, same place, but the prompt, the hair and the camera all changed between them: two shots with a cut became one continuous take.
- Clip 1 asked for a camera that "does not move, zoom or cut" and Seedance cut at 1.8 s anyway.
- Prompts are shown exactly as sent, including their flaws.
- The film is 24 fps, as the clips were. Music: "Morning Garden" by folk_acoustic (Pixabay).

## Skills

The three skills we use for this work are in [`../skills/`](../skills/): [AI Performance Director](../skills/ai-performance-director/SKILL.md), [Cinematic Sequence Director](../skills/cinematic-sequence-director/SKILL.md) and [Cinematic Stills](../skills/cinematic-stills/SKILL.md).

Made for [@cinematic_llm](https://www.instagram.com/cinematic_llm/).
