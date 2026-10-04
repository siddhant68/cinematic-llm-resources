# Genjutsu recast: assets checklist and prompt template

Written 2026-10-04. Built from two sources: a study of the 50 most popular Higgsfield Genjutsu community videos that have both a prompt and images (24 studied frame by frame; notes from that study are summarised below), and our own five jobs for the film "Trial by Combat" (our run log). Use it for the common job: recast the people and the place in an existing video.

## How Genjutsu divides the work

| Input | What it decides |
|---|---|
| Reference video | Length, cuts, camera, framing, every movement. Words cannot change these. |
| Images | Who is in it: faces, hair, build, outfits, the place. |
| Prompt | Which person or thing in the video becomes which image, and what must stay. |

## Assets checklist

**The video**
- Cut the exact motion you want. Ours were 4 to 6 seconds each.
- Keep cuts few. One prompt handled three shots, but every cut is a chance for an identity mix-up.
- A soft, low-resolution source is fine. The output size comes from the resolution setting.
- The result keeps the source audio. Mute it if the source has speech or music.

**The cast, per person**
- One image for the face: several views of the same face on one sheet worked for us (six expressions).
- One image for the body and outfit: a turnaround sheet (front, three-quarter, side, back).
- Dress the person in these images. Whatever they wear there appears in the video.
- Bare hands in the image if the scene needs bare hands; props in the image tend to appear in the result.

**The place**
- One image of the new location, lit the way you want the scene lit.

**Before you submit**
- Count the attachments against the prompt. A prompt can name an image that is not attached, and nothing warns you.
- Order the images the way the prompt numbers them: face, body, face, body, place.

## The template

Replace everything in [brackets]. Delete the SHOT BY SHOT block if the clip has no cuts.

```
REFS: <<<video_1>>> the source, the only thing that controls motion, camera, cuts and timing · <<<image_1>>> the face of PERSON A · <<<image_2>>> PERSON A full body, build and clothes · <<<image_3>>> the face of PERSON B · <<<image_4>>> PERSON B full body, build and clothes · <<<image_5>>> the place.

Recast <<<video_1>>> as [one line: the new scene]. Replace [the two people] completely (head, hair, face, skin, build and clothing), [the people around them], [the surroundings] and every piece of text. Keep everything else identical to the source: the same shots in the same order, the same cuts, the same timing, the same framing and camera, and the same movement of every body exactly as filmed.

PERSON A is [how this person looks in the SOURCE: hair, clothes, position]. They become the person in <<<image_1>>> and <<<image_2>>>: exactly that face, [their hair, in words], [their build], wearing exactly the clothes in <<<image_2>>>: [the outfit, in words]. Keep the same face in every shot, from every angle.

PERSON B is [how this person looks in the SOURCE]. They become the person in <<<image_3>>> and <<<image_4>>>: exactly that face, [hair], [build], [outfit]. They have no [the source trait that must disappear, e.g. blonde hair] at all.

Each reference sheet shows ONE single person several times. Use the sheets only to learn the face, body and clothes. Never reproduce a grid, panels, a studio backdrop or more than one copy of either person. Take every expression and head movement from <<<video_1>>>, not from the sheets.

SHOT BY SHOT
Shot 1, [framing]: [who is in it, where they stand, what they do].
Shot 2, [framing]: [who is on the left, who is on the right].

[Anything to remove or swap on the bodies: gloves, phones, logos on clothes.]

Replace [the room, ring or street] with <<<image_5>>>: keep [what stays where it is] but make it [the new materials], [the new floor], [what stands behind], [the light]. Remove all writing, logos, banners and watermarks. No modern objects.

No face morphing, no change of identity between shots, no blending of the two people, no extra people, no merged or duplicated bodies, no flickering, no distorted hands.
```

A filled example is our real prompt for the close exchange: `8_genjutsu_prompt_clip3_close_exchange_two_shots.txt`.

## What each block is for

1. **REFS** tells the model the job of every attachment. In the top videos, images still win over mislabelled tags, so keep the numbering honest.
2. **Replace only, keep everything else identical** is the framing the top recasts share: the word "replace" is in 70% of the 9,169 community prompts we counted.
3. **Name people by the source.** "The blonde man in black trunks" tells the model which body to recast. Then point to the images.
4. **Say the outfit in words as well.** In close-ups the source shows bare skin or the wrong clothes; the words back up the image.
5. **Shot by shot** when the clip cuts: which person each shot shows, and who is left and right after a reverse angle.
6. **The place** as a swap list: what stays where it is, what it becomes.
7. **The guard line** names the failures you fear. Keep it short.

## Do not write

- A duration, "slow", "fast" or a frame rate. The reference video decides (a prompt asking for a slow 6 seconds got 13 fast seconds).
- A new pose or staging that fights the source. The source pose wins.
- A colour or attribute that contradicts your image. The word can override the image.
- Character, show or real-person names.

## What still went wrong for us (three clips, one take each, 720p)

- One clip swapped the two fighters: each kept his own look, but they traded places and moves.
- The crouching photographers in a wide shot kept their cameras although the prompt said "holding nothing".
- One fighter's cropped hair came out fuller in one clip.
- Every clip repeats one frame about once a second.
- Two earlier jobs ended with the status `ip_detected` and were refunded: their images were flagged as protected characters. The fighters in the film are original characters.

## Cost we measured (October 2026, Higgsfield credits)

480p: 3 credits per second. 720p: 7 credits per second. The number of images did not change the price. Our three 720p clips (16 seconds) cost 112 credits.
