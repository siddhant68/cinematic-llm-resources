---
name: broll-direction
description: Decide where B-roll belongs in a talking-head edit, how long to hold it, and where to source it for free before spending generation credits. Use whenever B-roll, cutaways, stock footage, or supporting visuals are being planned or placed, whenever a user asks what should go on screen while they talk, and whenever an edit needs visual variety or a cut needs covering. Also use before generating any video with Kling, Veo, Sora or similar, to check whether a free clip would do the job.
---

# B-Roll Direction

B-roll has two jobs: **cover a cut** and **show what words can't**. Anything
placed for a third reason ("it's been a while since we cut away") makes the video
worse.

## Placement

Work from the transcript, not the timeline. For each kept range, ask what the
viewer needs to *see* to believe or follow the sentence. Most sentences need
nothing. The ones that do are usually:

- **Concrete nouns.** A place, an object, a screen, a person. If the script names
  a thing, showing it costs the viewer nothing and gains specificity.
- **Numbers and comparisons.** Anything a viewer would otherwise have to hold in
  working memory. This is often better as a graphic than as footage.
- **Process or sequence.** "First X, then Y" is much clearer shown than said.
- **Joins that don't cut cleanly.** A cutaway over an awkward picture join is
  free — it removes a visible problem and adds variety at the same time.

Rules that hold up:

**Never leave the same framing on screen longer than 10–15 seconds** without some
variation. For short-form, 5–7 seconds. This is the strongest single predictor of
whether a talking head holds attention.

**Hold each B-roll shot 2–5 seconds.** Under 2s the viewer registers a flash but
not an image. Over 5s, the audio outpaces the picture and the viewer starts
wondering when you're coming back.

**Land it on the word, not near it.** The shot should arrive on or slightly
*before* the word it illustrates — 0–300ms early. Arriving after the word has
passed makes the edit feel like it's chasing the script.

**Come out on an L-cut.** Audio continues under the B-roll and the picture
returns to the speaker mid-sentence. Cutting picture and audio back together
announces the B-roll as a segment.

**Duck B-roll audio to near silence** under narration, or strip it. Native audio
at full level under a voiceover is the most common amateur mistake.

**There is no correct cuts-per-minute or A-roll ratio.** 60/40 is a rough sanity
check, not a target. If a video is 70%
B-roll, the talking head has stopped being the video. If it's 95% A-roll and runs
long, it will feel static. Neither number tells you where a specific shot goes.

## Evidence hierarchy — before you search anything

For a channel about your own work, generic stock is the *weakest* option, not the
default. Ask what would actually make the viewer believe the sentence, and work
down this list only as far as you have to:

1. **Your own output** — the thing you actually made. Unbeatable.
2. **Your own screen recording** — the tool, the prompt, the terminal, the result.
3. **A before/after comparison** — the single most persuasive format there is.
4. **A diagram, annotation, or animated explanation** — when the idea is structural.
5. **A script, prompt, storyboard, or asset close-up** — concrete artefacts.
6. **Licensed stock** — when you need a real-world referent you don't have.
7. **Generated B-roll** — when the shot is specific to your script and unfindable.
8. **Generic decorative stock** — last resort, and usually a sign the sentence
   didn't need a visual.

Footage of robots, glowing circuits, people typing, or floating holographic
interfaces makes technical work look *less* credible, not more. If the honest
answer is "nothing" — stay on the face. A visually quiet moment is a legitimate
editorial choice.

Each planned insert should produce a manifest entry so the decision is auditable
and the asset's rights are recorded:

```json
{
  "script_claim": "The sun direction stays consistent across generations",
  "output_start": 188.4, "output_end": 194.2,
  "editorial_purpose": "evidence",
  "preferred_asset_type": "existing_project_clip",
  "search_queries": [], "candidate_assets": [],
  "selected_asset": null, "license": null,
  "crop_plan": null, "fallback": "annotated still",
  "confidence": 0.88
}
```

## Sourcing — free first

Generation credits are worth spending on shots that can't be found, not on
"person typing at a laptop." Search in this order and stop at the first hit.

| Source | Best for | License | Attribution | API |
|---|---|---|---|---|
| **Pexels** | Broadest general B-roll, people, business, tech | Pexels License | No | Yes, free key |
| **Pixabay** | Abstract, motion graphics, particles, 4K loops | Pixabay Content License | No | Yes, free key |
| **Coverr** | Background loops, ambient, real + AI clips | Coverr License | No | No |
| **Mixkit** | Curated cinematic; smaller library | Mixkit Free License — **check per clip** | No | No |
| **Videvo / Videezy** | Motion graphics, effects, fills gaps | Mixed — **some require credit** | Sometimes | Partial |
| **Dareful** | Nature, aerial, 4K scenic | CC-BY | Yes | No |

Both Pexels and Pixabay offer free API keys and are the only two worth wiring up
programmatically. See `references/free-sources.md` for endpoints and query
patterns.

**License cautions that actually bite:** free libraries rarely guarantee model or
property releases, so a recognisable face or logo is a risk in anything
commercial. Pixabay carries AI-generated content mixed in with camera footage —
check the label if that matters. Mixkit's free licence has per-clip restrictions,
so read the individual clip page rather than the site headline. Videvo and
Videezy mix attribution-required clips into free results.

**Download 4K even when delivering 1080p.** It buys reframing, punch-ins and
stabilisation crops with no quality cost.

## When to generate instead

Reach for Kling / Veo / Sora only when the shot is:

- Specific to your script in a way stock can't be ("the exact diagram I'm
  describing")
- Stylistically matched to a look no library has
- Abstract or conceptual, where generation is genuinely strong
- A **background plate**, where seamless looping matters and Kling 3.0 Omni's
  first/last-frame control gives you something stock can't

Do not generate: people doing ordinary things, cities, nature, offices, hands on
keyboards, generic tech. Stock is better, free, and instant, and generated humans
still read as generated.

Before any generation call, state which free source you searched and why it
didn't have the shot. This one habit is what keeps credit spend sane.

## Matching B-roll to the edit

Stock footage arrives in mismatched formats and will look pasted in unless it's
conformed:

- **Frame rate.** Match the timeline. Conforming 24 → 30 introduces judder;
  prefer clips already at your rate when the choice exists.
- **Grade.** Apply the project's look to B-roll too. Ungraded stock next to
  graded A-roll is instantly visible.
- **Motion.** A static talking head next to a fast drone push feels jarring. Slow
  the B-roll or add a slight push to the A-roll so they share energy.
- **Grain.** If the A-roll is noisy and the stock is clean, add a little grain to
  the stock. Mismatched noise floors read as two different videos.

## Rights manifest

"It came from a free site" is not a licence record. For every downloaded or
generated asset, store: source URL, asset page, licence name **and a snapshot of
the licence text as of the download date**, creator, download date, whether
commercial use is permitted, attribution requirement, and any prohibited uses.
For generated assets add provider, model version, prompt, seed and credit cost.

Two reasons this is not bureaucracy. Licences change — a snapshot at download
time is what you can actually rely on later. And free libraries rarely guarantee
model or property releases, so a recognisable face, logo, artwork or private
property can carry rights the footage licence says nothing about. For anything
running as paid media, move that specific shot to a library that documents its
releases.
