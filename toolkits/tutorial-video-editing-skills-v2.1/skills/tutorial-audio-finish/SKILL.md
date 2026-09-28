---
name: tutorial-audio-finish
description: Plan and finish professional tutorial audio from a production microphone, camera scratch tracks, music, natural sound, and SFX. Use when an agent must repair dialogue edits, create room-tone continuity, design J/L-cut audio overlaps, determine section tempo and music energy, find and document licensed music or sound effects, build scene-level music ducking and automation, prevent dialogue masking, mix B-roll natural sound, create audio_plan.json, or measure final loudness, true peak, silence, and delivery defects.
---

# Tutorial Audio Finish

Dialogue is the hierarchy anchor. Music, natural sound, and SFX support clarity, rhythm, emotion, and transitions without competing with speech.

## Required inputs

- `EPISODE_BRIEF.json`
- story-cut audio spine and source inventory
- `edit_blueprint.json`
- approved B-roll and motion-graphics plans
- final or provisional section timecodes
- target platform and delivery format
- allowed music/SFX sources and rights policy

Read:

- `references/audio-chain.md`
- `references/audio-edit-continuity.md`
- `references/music-tempo-and-licensing.md`
- `references/session-proven-audio.md` when music is ducked under dialogue, section cards receive a recurring signature, or an AAC master is delivered

## Required outputs

Before downloading or mixing, produce:

```text
planning/audio_plan.json
planning/music_direction.md
assets/audio_rights_manifest.json
assets/audio_download_receipts.json
```

Validate:

```bash
python scripts/validate_audio_plan.py planning/audio_plan.json
```

Download only reviewed, rights-verified audio entries:

```bash
python scripts/download_approved_audio.py assets/audio_rights_manifest.json --dry-run
python scripts/download_approved_audio.py assets/audio_rights_manifest.json
assets/audio_download_receipts.json
```

Measure source or render:

```bash
python scripts/analyze_audio.py master.mp4 --json review/audio_analysis.json
```

## 1. Build one dialogue spine

- Choose the production microphone as the primary dialogue source.
- Synchronize and retain camera scratch audio only as reference or emergency repair.
- Cut dialogue for intended meaning and performance, not merely silence length.
- Preserve breaths and pauses that support phrasing.
- Patch edit holes with matched room tone.
- Use short, content-appropriate crossfades at every dialogue edit.
- Match clip and phrase gain before compression.

Do not gate speech so aggressively that room tone opens and closes between words.

## 2. Design audio continuity at cuts

Use:

- J-cut: next sentence or sound begins before the next picture
- L-cut: current dialogue continues over B-roll, screen, reaction, or the next view
- room-tone bridge: keep ambience continuous through a visual change
- natural-sound bridge: lead or trail a real action across the edit
- music phrase bridge: move sections on a musical phrase only when it supports the argument
- intentional silence: remove music before a critical claim or payoff

A cut should not feel abrupt merely because picture and audio change on the same frame. Stagger them when continuity improves.

## 3. Create an energy map

For every section, rate:

- dialogue density
- conceptual difficulty
- emotional energy
- visual motion
- proof/demo intensity
- need for concentration or breathing room

Then choose one music state:

- `off`
- `intro`
- `under_dialogue_sparse`
- `under_dialogue_energy`
- `transition_lift`
- `broll_feature`
- `reveal`
- `recap`
- `outro`

Do not keep one loop at one level beneath the whole episode.

## 4. Select music by function

Write the music brief before searching:

- intended emotion and section role
- acceptable BPM range, pulse, and arrangement density
- instruments and frequency density to avoid
- whether vocals are prohibited
- required loop/edit points
- desired start, development, and ending behavior

For dense technical explanation, prefer sparse instrumental arrangement with limited energy in the speech band and no competing vocal. For result montages or non-dialogue B-roll, music can become more present. Return it under dialogue before the next phrase.

Tempo should support speech cadence and section energy, not force cuts onto every beat. A tutorial can use a steady bed under explanation and phrase-level lifts at major transitions.

## 5. Source music and SFX legally

Use verified commercial-use sources. YouTube Audio Library is the preferred starting point for YouTube music and SFX because licensing and attribution requirements are shown in the library. Mixkit and Pixabay can be considered only after checking the exact asset and current license.

Record for every asset:

- source page and direct download URL
- creator and track/effect title
- exact license and license URL
- date checked
- attribution requirement and exact text
- editing/monetization restrictions
- local path and SHA-256
- approval status and explicit `approved_for_download` gate
- download receipt, local SHA-256, and final timeline ranges

Use `download_approved_audio.py` only with a direct HTTPS file URL taken from the verified source page. Download to quarantine first; listen for embedded watermarks, vocals, clipping, or unexpected third-party material before approving the asset.

Do not download from random converter sites, another YouTube video, streaming services, films, or social media. Do not assume that `royalty-free` means no conditions.

## 6. Plan music automation by scene

For each cue, specify:

- start and end
- music source ID
- state and purpose
- dialogue density
- target relative level
- fade/phrase alignment
- ducking amount or automation shape
- natural-sound relationship
- transition into and out of the cue

Starting point under ordinary dialogue: keep the music roughly 18-24 dB below perceived dialogue, then adjust by ear and spectrum. Lower it further or remove it during dense knowledge, quiet voices, names, numbers, code, and caveats. Raise it during non-dialogue B-roll or montage only to the level the visual can support.

Use sidechain/ducking as a helper, not a replacement for intentional automation. Avoid audible pumping.

## 7. Use natural sound deliberately

Feature real clicks, typing, movement, ambience, or result audio when it increases presence or proof. Fade it under narration and mute embedded stock music unless cleared.

Natural sound can create stronger transitions than designed SFX. Do not replace every real event with a synthetic whoosh.

## 8. Build a restrained SFX palette

Choose no more than four recurring families, such as:

- soft UI tick
- subdued whoosh for a meaningful spatial move
- low soft impact for a claim or reveal
- short riser for one major transition

Every SFX must name a visible event or structural event. No whoosh on ordinary camera cuts. No riser before every section. Keep accents below dialogue and check on small speakers.

## 9. Dialogue processing order

Use only what the source needs:

1. source gain and phrase matching
2. clip repair and room tone
3. conservative noise/voice isolation
4. corrective EQ
5. moderate compression
6. de-essing when required
7. dialogue bus control
8. music/SFX automation
9. final bus limiting and measurement

Heavy denoise, over-compression, or aggressive de-essing can make limited-camera audio feel more artificial. Compare against the source.

## 10. Look-development and full mix

The sample must include dense instruction, a view change, B-roll natural sound, music automation, one SFX, and a quiet or music-free important moment.

After approval, mix one section at a time. Listen on headphones, laptop speakers, and a phone. Check intelligibility at low playback volume.

## Proven implementation notes

- Treat every supplied asset pack as **unresolved** until its exact source page, license, and local SHA-256 are recorded. A familiar filename alone is not provenance. A local copy of a verified item can be used once its item page and license are recorded in the rights manifest.
- Read embedded music metadata before estimating tempo. When `TBP` (tempo BPM) is present, record it and start source time 00:00:00.000 on the intended visual event; at 120 BPM, for example, beats are 0.500 seconds apart. This makes a repeatable beat grid without forcing dialogue edits to the grid.
- Resolve timing references before applying a cue sheet. If the provisional picture render duration and section map differ, use the current render for review samples and explicitly conform any out-of-range future cues to the delivery timeline.
- In this ffmpeg build, `sidechaincompress` requires `makeup` from 1 to 64; use `makeup=1` when no gain compensation is wanted. `loudnorm` may increase the working sample rate, so explicitly `aresample=48000` (and encode `-ar 48000`) for a 48 kHz delivery.
- Detect actual chapter cards from rendered evidence before adding holds; a stale section map can name cards which are not present in the exported picture. Insert a complete A/V card clip at each verified position, rather than stretching the surrounding render, so burned captions and every following dialogue frame remain synchronized.
- Use a distinct short sting for chapter cards, separate from the ordinary music bed. Record whether it is licensed or generated/owned. Do not add transition effects to ordinary B-roll cuts.
- Record music source gain and post-duck listening target separately. A value such as `-17 dB` before a 5:1 sidechain is not the perceived music level under dialogue; document attack and release too.
- Measure a representative **ducked music stem** and compare its integrated loudness with the same dialogue range. One completed mix passed programme loudness QC while its bed was effectively inaudible because -26 to -29 dB source gain was followed by a low-threshold 5:1 sidechain. The repaired opening measured the ducked bed 19.19 LU below dialogue using gentler 2.5:1 ducking. Use roughly 15-20 LU below dialogue as a listening starting range, then judge the actual programme; never infer gain reduction from the ratio control alone.
- When a chapter transition is meant to have a recurring audible signature, tie one restrained SFX family to every verified chapter card and record its pre-roll. Do not let the general rule against ordinary-cut whooshes accidentally remove the explicitly designed chapter signature.

## 11. Delivery checks

Measure integrated loudness, loudness range, true peak, channels, sample rate, and long silences. The bundle uses about -16 to -14 LUFS integrated and no higher than -1 dBTP as a practical house range, not a substitute for listening or platform-specific requirements.

When the final delivery uses AAC, leave practical encode headroom and measure the encoded file rather than trusting the pre-encode bus. A limiter ceiling around -1.5 dBTP may be needed to keep the delivered file at or below -1 dBTP; adjust from the measured result rather than treating that number as universal.

One completed AAC delivery consumed roughly 0.7 dB of headroom after a -1.5 dBTP bus target. If the encoded file overshoots, lower the bus target (that delivery passed with -2.3 dBTP), rerun the two-pass render, and preserve both measurements. Treat these figures as an encoder-specific starting point, not a universal preset.

Flag:

- clipped words or peaks
- pumping room tone
- sudden level changes
- music masking speech
- SFX spikes
- phase/correlation problems
- accidental silence
- mismatched stereo/mono routing
- unlicensed or unattributed assets

## Non-negotiable rules

- Dialogue always wins.
- No music or SFX without a rights record.
- No one-level music loop through the full lesson.
- No automatic beat-cutting that damages speech rhythm.
- No SFX without a linked event.
- No final mix approval from meters alone.
