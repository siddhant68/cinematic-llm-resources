# Realism: what makes a still cinematic and mature, and how to audit it

## Why images look AI-made (and the cure for each)
| Tell | Cure (write it into the prompt) |
|---|---|
| Light with no source, flat and frontal (the "built-in flash" look) | Name **one key source, its side, hardness and colour**; a fill; a rim. "Low sun from frame left, warm, raking across her face; soft cool fill from the open sky; a rim through her hair." |
| Skin too perfect (no pores, waxy) | "Visible pores across the nose and cheeks, fine peach fuzz catching the light, uneven tone, faint shadows under the eyes, a little natural shine, slightly dry lips, no makeup beyond balm." Add **our own marks**: a scar in a named place, a mole, one brow higher, a lopsided smile. |
| The model-average face (symmetrical, pretty) | Build from **specific irregular traits** (Pinterest trait notes) written as physical fact, never "beautiful". Add to the avoid line: "a symmetrical model face". |
| The hero pose (centred, frontal, looking into the lens) | Caught mid-action; the eyes on a **named point off the lens** ("just past the lens to frame right"); three-quarter angles. |
| A spotless world | Wear, dust, clutter, weather; props used and not new; "sand-worn edges", "sill dust". |
| Spectacle that nobody has photographed | Ground it in a real place type and physics ("a real haboob, not smoke, a tornado or a creature"). |
| Default grade (teal-orange, HDR, oversaturated) | "Natural analogue film grade, [2–3 named colours], gently lifted blacks, soft highlight roll-off, fine 35 mm grain." |
| Word salad ("8k, masterpiece, hyperrealistic, octane") | Delete it. Describe a photograph someone took. |
| Broken small things (hands, earrings, text) | "Hands anatomically correct, five fingers", and no text anywhere. Check the hands first in the audit. |

## The nine layers of a still prompt, with our wording for each
1. **Identity:** age, face structure, presence ("a woman of about twenty-seven… a long lean face, defined cheekbones, a firm, slightly square jaw").
2. **Skin realism:** see above.
3. **Styling:** materials, cut, colour, wear ("a lightweight, slightly sheer cream shirt with a faint beige check, sleeves pushed to the elbow").
4. **Emotional energy**, written as **muscles, never as a mood word**: "lips closed and relaxed, the left corner lifted a little higher, eyes soft".
5. **Environment:** concrete nouns from the breakdown, with positions ("two old pumps beneath the canopy, an empty two-lane road runs past").
6. **Lighting:** one key, fill and rim, the time of day, and **the same direction in every still of the film**.
7. **Camera:** height, distance, framing, lens feel (24–35 mm for wides, 50 mm for medium shots, 85–100 mm for faces), aperture, focus.
8. **Format:** "Photoreal vertical 9:16 film still", plus `Aspect ratio: 9:16 (vertical).` on its own last line.
9. **Negatives:** the avoid line (below), tuned to this still's specific risks.

**Standard avoid line:** "Avoid a symmetrical model face, plastic, airbrushed or waxy skin, beauty retouching, glamour makeup, anything that looks rendered, broken anatomy, extra fingers, extra people, text, logos, brand names, number plates or watermarks." Then add this still's own risks: "looking into the lens", "a big grin", "a changed neckline", "the storm visible", "a sexualised pose".

## "Mature": the bar
The bar is a frame from a prestige film or a documentary photograph, not an advert, a game render or a fashion campaign:
- restrained, specific emotion;
- one motivated light;
- real wear;
- a composition with negative space or depth;
- modest, era-true wardrobe.

On HOLD STILL the first dress (a short strapless one) was rejected as too short, and the creator asked for researched wardrobe rather than blind obedience (a 1950s strapped knee-length sundress, chosen from a Pinterest sweep). When a creative call is open, research it and recommend with reasons.

The creator also asked for worlds that are "magical", not bland: dreamy, real places with weather and depth (the flower farm under fast clouds beat the plain desert bus stop).

## The expression method (from reel 010, proven)
- **Every face beat is a change between opposite faces:** START → END (calm → afraid, guarded → wounded).
- **Design both faces as stills.** The END face becomes a video reference and is drawn in its board panel.
- **Give every change a trigger the camera can see or hear,** one beat before the face moves.
- **Write the face as muscles, in the order a real face moves:** eyes → brows → breath → mouth → head.
- **Eyes go to a named point off the lens. Never "the lens" for a character.**
- **Banned on AI faces:** tears running down (allow "a tear gathers but does not fall"), open-mouth crying, screaming, a broad grin, a duck-face pout, looking into the lens.

## Identity rules
- **Every still after the identity image is made with the identity image attached** (plus the angle sheet once it exists). Start each prompt: "Use the [woman] in the attached photo exactly as she is: same face, [marks], skin, hair and clothes."
- **Name the permanent marks in every prompt**, so ChatGPT re-draws them: the scar, the mole, the crooked tooth.
- **Lookalike check:** put the identity image beside every trait pin with `scripts/make_board.py --fit contain`. It must share **traits, never a whole face**. It must not resemble any actor or real person. Log the check.
- **Fixed world:** one light direction, one geography (the lamp at frame LEFT, the window at frame RIGHT), and a fixed wind direction. Write it into every still.

## Audit checklist (every image, before it is kept)
1. Face: the same person as the identity image, with the marks present; no age or sharpness drift; no beautification.
2. Skin: pores visible, not waxy.
3. Hands: five fingers each, natural grip on any prop.
4. Eyes: pointing where the spec says, by screen direction; nobody looks into the lens unless the spec says so.
5. Light: from the film's fixed direction; one motivated source.
6. Wardrobe: identical to the identity image (neckline, length, colour, bands, shoes).
7. World: the right place, with no drift (the HOLD STILL background drifted to Tuscany once; fixed with T6).
8. Nothing that must not be in frame yet (the storm, the weapon, the reveal).
9. No text, logos, watermarks, number plates or brand marks.
10. The still reads at phone size: look at it at about 360 px wide.

Fix with **one targeted edit** (template T6: "keep everything, change only…") or regenerate in a fresh chat. **Log the verdict** (KEEP / PARTIAL / REJECT and why) in `<work>/LOG.md`.
