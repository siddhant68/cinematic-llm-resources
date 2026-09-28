---
name: audio-post
description: Clean, shape and master a dialogue track — noise, rumble, sibilance, clipping, room tone, compression, ducking and loudness. Use whenever audio quality is being worked on or complained about, whenever a user mentions noise, hiss, hum, echo, mic quality, levels, loudness, LUFS, ducking, music beds, breaths, mouth clicks, or says the audio sounds "thin", "harsh", "muddy", "quiet" or "amateur" — and always before delivering any video, because a polished picture with untreated audio still reads as amateur.
---

# Audio Post

Viewers forgive a soft image and leave over bad audio. This is the highest
return-per-minute stage in the whole pipeline, and the one most likely to be
skipped because its problems are less visible than a bad cut.

## Measure first

```bash
python scripts/analyze_audio.py dialogue.wav --platform youtube
python scripts/analyze_audio.py video.mp4 --json          # machine-readable
python scripts/analyze_audio.py video.mp4 --emit-chain    # just the -af string
```

Reports integrated loudness, loudness range, true peak, noise floor, SNR,
clipping, rumble and sibilance ratios, and a room-tone candidate — then
prescribes a chain with values derived from those measurements rather than
presets.

The prescription is a **starting point**. Every number in it is defensible from
the measurement; none of it is a substitute for listening.

## Chain order is the whole skill

Order matters more than parameter choice, because each stage changes what the
next one sees. The failure mode is universal: people reach for compression and
loudness first because those are the audible wins, and in doing so they bake in
and then amplify every problem underneath.

```
1. REPAIR      declip, declick, DC offset
2. SUBTRACT    high-pass, notch out specific resonances
3. DENOISE     afftdn / arnndn
4. DE-ESS      before dynamics
5. DYNAMICS    compressor
6. TONE        additive EQ, presence
7. CEILING     limiter
8. LOUDNESS    two-pass loudnorm
```

Why this order and not another:

- **Repair before anything.** A compressor cannot rebuild a flat-topped wave; it
  will just make the distortion louder and more even.
- **High-pass early.** Nothing useful for a speaking voice lives below ~75Hz.
  Rumble there is invisible on a waveform but consumes headroom that every later
  stage fights for.
- **Denoise before compression, never after.** Compression raises quiet passages,
  which means it raises the noise floor. Denoise afterwards and you are removing
  noise you already amplified, at a much worse signal-to-noise ratio.
- **De-ess before compression.** A sibilant peak triggers the compressor, so the
  whole word ducks on every "s". De-essing first stops the pumping.
- **Additive EQ after compression.** Boost before and the compressor just removes
  the boost.
- **Loudness last, and only once.** Anything after it invalidates the measurement.

## Denoise is a trade, not a free win

`afftdn=nr=12:nf=-40:tn=1` is a reasonable starting point when SNR is below 25 dB.
`nr` is the reduction in dB; `nf` should be near the measured noise floor;
`tn=1` tracks a drifting floor.

**Over-denoising is worse than the noise.** Past roughly `nr=15` you get the
underwater, phasey artefact that is instantly recognisable as processed audio.
Viewers tolerate a quiet hiss; they do not tolerate a voice that sounds like it is
coming through a wall. If SNR is above 40 dB, skip denoise entirely — applying it
anyway costs presence for no gain.

`arnndn` (RNN-based) often outperforms `afftdn` on speech but requires an external
model file. Worth setting up if the room is genuinely noisy; unnecessary
otherwise.

The real fix is upstream: a closer mic, a quieter room, or a lav instead of a
shotgun. No filter recovers what was never captured.

## Room tone is the thing that gets missed

When you delete a pause or a retake, you do not just remove speech — you remove
the room. Splicing two segments directly creates a moment of **absolute digital
silence** between them, and the ear hears that as a hole. It is the single most
common reason cut dialogue sounds edited.

The fix: capture a few seconds of the empty room and lay it under the whole
dialogue track at the measured noise floor, so removed pauses are filled rather
than blank.

```bash
# the analyzer reports a room-tone candidate span; extract and loop it
ffmpeg -i dialogue.wav -ss 7.02 -t 1.2 -y roomtone.wav
ffmpeg -i dialogue_cut.wav -stream_loop -1 -i roomtone.wav -filter_complex \
  "[1:a]volume=-3dB[rt];[0:a][rt]amix=inputs=2:duration=first:normalize=0" \
  -y dialogue_with_tone.wav
```

Better still: record 5–10 seconds of silence deliberately at the start of every
shoot, before you speak. It costs nothing and makes both room tone and noise-floor
measurement exact instead of inferred.

## Fades and crossfades — replacing the fixed 30ms rule

A tiny fade prevents the click that a hard splice produces. A blanket 30ms on
every edit softens consonants and smears speech onsets.

Choose per boundary:

| Situation | Treatment |
|---|---|
| Mid-phrase splice, continuous ambience | 10–20ms equal-power crossfade |
| Boundary between separate takes | 20–30ms crossfade, plus room tone underneath |
| Removed pause | room tone across the gap, no crossfade |
| A deliberate silent beat before a key line | **no fade, no tone reduction — leave it** |
| Hard cut to a new section | 5–10ms is enough; the cut is the point |

The last row matters. A pause before an important line is doing editorial work.
Processing it away because a rule said "fade every boundary" removes the emphasis
you built.

`acrossfade=d=0.02:c1=tri:c2=tri` for equal-power; `afade` for single-sided.

## Ducking under B-roll and music

Use sidechain compression keyed off the dialogue rather than static volume
automation — it responds to the actual speech and needs no keyframes.

```bash
ffmpeg -i dialogue.wav -i music.wav -filter_complex \
  "[1:a][0:a]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400:makeup=1[duck];
   [0:a][duck]amix=inputs=2:normalize=0" -y mixed.wav
```

`release` is the parameter that decides whether it sounds professional. Too short
(under 200ms) and the music pumps audibly between words. 300–500ms lets it recover
between sentences rather than between syllables.

Targets: music sits **15–20 dB below** dialogue under speech; B-roll native audio
usually belongs at **−25 dB or muted entirely**. Native audio at full level under
narration is the most common amateur mistake in the whole pipeline.

## Breaths

Do not delete every breath. Breath is how speech sounds human, and a track with
all breaths removed sounds unnervingly synthetic — the same uncanny quality as
AI-generated narration.

Reduce rather than remove: attenuate loud breaths 6–10 dB, remove only the ones
that are genuinely distracting (a gasp, a breath directly into the mic). Leave
the rest.

## Loudness targets

Two-pass `loudnorm` — measure, then apply the measurement. Single-pass guesses and
gets the range wrong.

| Destination | Integrated | True peak |
|---|---|---|
| YouTube, Instagram, TikTok | −14 LUFS | −1 dBTP |
| Podcast | −16 LUFS | −1 dBTP |
| Broadcast (EBU R128) | −23 LUFS | −2 dBTP |

**Do not master louder than the platform target.** Platforms normalise: going to
−9 LUFS means YouTube turns you down by 5 dB, and you have permanently crushed the
dynamics you sacrificed to get there. You end up quieter *and* flatter than if you
had hit the target.

Declare the target explicitly in the project rather than relying on a default —
ffmpeg's `loudnorm` default is `I=-24`, which is a broadcast value and wrong for
YouTube.

## Filter names that are easy to get wrong

Two verified against this ffmpeg build, both of which cost time if assumed:

- **The de-esser is `deesser`, not `adeesser`.** The `a`-prefixed name is
  frequently cited and does not exist. Check with
  `ffmpeg -h filter=deesser` before writing a chain around it.
- **Clipping is detected via `Peak count`, not `Flat factor`.** On a hard-clipped
  file, `astats` reported `Flat factor: 0.00` while `Peak count: 240` — 240
  samples pinned at full scale. Flat factor is not a clipping indicator; peak
  count relative to a hot peak is.

Confirm availability before building a chain: some builds omit filters, and a
missing filter fails the whole graph rather than degrading gracefully.

```bash
for f in afftdn arnndn deesser acompressor alimiter sidechaincompress loudnorm; do
  ffmpeg -hide_banner -h filter=$f >/dev/null 2>&1 && echo "OK $f" || echo "-- $f MISSING"
done
```

## Measure the source, not your extraction

Feed the analyzer the **original file**. Pre-extracting audio changes the answer:
`-ac 1` on a dual-mono source applies roughly 3 dB of downmix attenuation, which
shifted a real measurement from −33.8 to −36.9 LUFS and moved the estimated noise
floor by 15 dB.

Check whether your two channels are actually different before touching them:

```bash
ffmpeg -i in.mp4 -af "pan=mono|c0=c0" -f s16le - | ...   # left
ffmpeg -i in.mp4 -af "pan=mono|c0=c1" -f s16le - | ...   # right
```

If they correlate at ~1.0 the file is dual mono and either channel is the whole
signal. If they differ materially, **pick one — do not downmix**, because summing
partially cancels and changes the noise floor.

## Trust the loudness numbers more than the SNR

Loudness, loudness range and true peak come from a proper EBU R128 pass and are
reliable to a fraction of a LU. **Noise floor and SNR are estimates** derived from
the quietest passage the tool can find, and they move with the material. Read SNR
as a band — clean / marginal / noisy — not as a precise figure, and never gate an
irreversible decision on it alone.

## QC before delivery

Re-measure the output and check:

- Integrated loudness within **±0.5 LU** of target; true peak at or below ceiling.
- **No sample at full scale** — re-run the analyzer and confirm peak count is low.
- No audible pump on sibilance or under music.
- **No absolute-silence gaps** — `silencedetect` at a very low threshold should
  find none if room tone was applied.
- Consistency across cut boundaries: sample a few splices and confirm the noise
  floor does not step up and down between segments. A changing floor is more
  noticeable than a high one.
- **Listen on headphones and on a phone speaker.** They fail differently:
  headphones expose noise and artefacts, phone speakers expose thin low-mids and
  lost intelligibility. Most of your audience is on the second one.

The last check is not automatable and is the one that catches what the numbers
miss.
