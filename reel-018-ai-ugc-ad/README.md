# Reel 018 · AI UGC ad + the prompt behind it

A 30-second AI UGC ad (a woman recommending a hair oil on a South Delhi rooftop), and everything you need to make your own: the full video prompt, the 9-line blueprint, the ChatGPT image prompts, and the edit grade.

> **Spec ad.** Not affiliated with Mamaearth. The creator is AI-generated and is not a real customer; her testimonial lines are scripted. Everything in the ad was generated, nothing was filmed.

## What is here
| file | what it is |
|---|---|
| [prompts/01_video_prompt_seedance.txt](prompts/01_video_prompt_seedance.txt) | The full Seedance 2.5 prompt, in my own wording: look, scene, two reference photos, camera, cuts, a timeline pinned to seconds, performance, voice lock, sound, no-list. |
| [prompts/02_prompt_blueprint.md](prompts/02_prompt_blueprint.md) | The same prompt as 9 reusable lines. Swap your person and product. |
| [prompts/03_ad_script_and_timing.md](prompts/03_ad_script_and_timing.md) | The six beats, the lines, and where the model really cut. |
| [prompts/image_prompts/](prompts/image_prompts/) | ChatGPT image prompts: her face from text only, the rooftop selfie, the flat oily-hair edit, and the three party-hair reveal stills. |
| [edit/take_the_shine_off.md](edit/take_the_shine_off.md) | The ffmpeg chain that takes the AI shine off the footage. |
| [images/](images/) | The creator still used as `@image1`, the reveal stills, the identity take, a contact sheet of the ad and the cover. |

## The recipe in four lines
1. Make her from text only in ChatGPT, then put her in a lived-in place (prompts 01 and 02).
2. Take one clean photo of your product (a packshot on white works). It is `@image2`.
3. Paste the video prompt into Seedance 2.5 in reference mode, 9:16, 30 s, sound on. 480p costs 90 credits.
4. In the edit: cut in the payoff stills, take the shine off, add your disclosure.

## Notes
- The product photo used for the ad is not included: bring your own, and only use a real brand's name or pack with permission.
- Model results vary with the references. These are the exact texts used for this ad, in my wording; adapt freely.
- The reel: [instagram.com/cinematic_llm/reel/DePiQb8BNrA](https://www.instagram.com/cinematic_llm/reel/DePiQb8BNrA/) on [@cinematic_llm](https://www.instagram.com/cinematic_llm/).
