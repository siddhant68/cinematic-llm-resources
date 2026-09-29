# Reel 010 — Dust Wall

One woman, one desert fuel stop at dusk, one dust storm. Twenty-five seconds from a single Seedance 2.5 generation, built in six beats so you feel her fear before you see the storm. The [Instagram film](https://www.instagram.com/cinematic_llm/), its tutorial, and a Wan 3.0 vs Seedance 2.5 comparison show how it was made.

## The six beats

| Beat | Feeling | Shot |
|---|---|---|
| 1 Establish | calm, small | wide, still |
| 2 Connect | we care about her | medium, slow push-in |
| 3 Disrupt | something is wrong | only the world changes |
| 4 React | fear, before we know why | close-up |
| 5 Reveal | the storm | wide reverse angle |
| 6 Escape | keep moving | fast tracking shot |

## Use the resources

1. Read the [director map](prompts/0_director_map_six_beats.md).
2. Break down reference photos with the [breakdown prompt](prompts/1_breakdown_prompt_attach_one_pinterest_photo.txt), one photo per fresh ChatGPT chat. Use the output as notes on light, place and traits, never as a face source.
3. Build the character from text only with the [character prompt](prompts/2_character_prompt_text_only_no_photo.txt), then her [angle sheet](prompts/3_angle_sheet_prompt_attach_her_image.txt).
4. Make the beat stills with her image attached: [establish](prompts/4_still_establish_attach_her_image.txt), [react](prompts/5_still_react_attach_her_image.txt), [reveal](prompts/6_still_reveal_attach_her_image.txt), [escape](prompts/7_still_escape_attach_her_image.txt).
5. Draw the six-panel [storyboard](prompts/8_storyboard_prompt_attach_her_the_place_and_the_storm.txt) with her, the establishing still and the reveal still attached.
6. Generate the scene with the [Seedance 2.5 video prompt](prompts/9_seedance_2_5_video_prompt_25s_attach_5_images.txt): omni-reference, 25 s, 9:16, 480p, sound on, five reference images in this order: her, her angle sheet, the establishing still, the reveal still, the storyboard. The [same prompt for Wan 3.0](prompts/9b_same_prompt_for_wan_3_0_20s.txt) (20 s) is included for comparison.

The [images](images/) are the original ChatGPT results and the [stills](stills/) are one frame per beat from the film. No Pinterest reference photos are included.

## What happened in this test

Seedance 2.5: one take, no retries, 75 credits. All six beats landed in order, her eyes stayed closed in Connect and opened into fear in React as asked, and the storm stayed hidden until 16 s. The last half second fades into the dust. The film is posted at its native 480p.

Wan 3.0 with the same prompt: one take, 35 credits. It kept all six beats and her face, but her eyes were open where the prompt asked closed, the reveal came early, and it copied a storyboard panel label into the frame. That is why the Seedance prompt adds one line telling the model the storyboard's labels never appear in the video.

These outcomes describe this run, not a guarantee for another model or reference set.
