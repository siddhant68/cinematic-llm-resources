---
name: ltx-video
description: Generate video locally with LTX-2.5 in ComfyUI on this Mac, from a prompt plus optional reference images. Use whenever the user wants a video generated, a clip made, a shot rendered, an image animated, a text-to-video or image-to-video generation, b-roll or a sample clip produced locally, or says things like "generate a video", "make me a clip", "animate this image", "render this shot", or hands over a prompt and reference stills with a duration. Also use when a previous generation looked wrong (black, glitchy, seams, silent audio, warped motion) and needs diagnosing, or when someone asks what settings, resolution or clip length this machine can handle. Produces a verified mp4 with synchronized audio, plus the exact parameters used.
---

# LTX-2.5 video generation

Runs a 22B audio-video model locally on Apple Silicon. Everything here is
measured on this machine, not estimated.

The generator is `ltxgen.py`. It builds the ComfyUI workflow, queues it, waits,
verifies the output actually contains a picture, and reseeds automatically if it
does not. You should almost never hand-build a workflow.

## Preflight, every time

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8188/
```

If that is not `200`, start ComfyUI **via start.sh and nothing else**:

```bash
~/Documents/Applications/ComfyUI/start.sh
```

`start.sh` carries `--use-pytorch-cross-attention`. Without that flag the model
returns NaN at some seeds and writes a completely black mp4 while reporting
success. This is not optional. See `references/troubleshooting.md`.

Also check swap before a long batch:

```bash
sysctl -n vm.swapusage
```

Judge on **free pages and ComfyUI's own footprint**, not on the swap number alone
(macOS swap `used` is sticky and never shrinks). See `references/troubleshooting.md`.

**At 0.7 MP and above, restart before every render, not just before a batch.** A
768x960 two-stage clip exhausted a freshly restarted machine on its own: 4.9 GB
free at the start, 0.0 GB by the refine stage, which then ran 2-3x slower than it
should. A machine in swap once turned an 8 minute render into 74, and it degrades
gradually rather than failing, so it reads as the model being slow.

## What to get from the user

Ask only for what is missing. Infer the rest and say what you inferred.

| Need | Default if unstated |
|---|---|
| The prompt, or the idea to build one from | required |
| Duration in seconds | 4 |
| Reference images, and where each belongs in time | none |
| Resolution | 1280x704 |
| Fast draft or final quality | final (two-stage) |

If they give you an *idea* rather than a prompt, write the prompt. That is the
part of this job with the most leverage. Read `references/prompt-craft.md` first.

## Where your own judgement matters

Four places. The rest is mechanical.

**Writing the prompt.** A one-line idea becomes 120-160 words across six concerns:
shot and lens, scene, action in chronological order, subject detail, camera move,
audio. This is where a mediocre idea becomes a good clip. Do not just pad the
user's sentence; direct the shot.

**Choosing what to put on screen.** If the user asks for something the model is
bad at (fast fight choreography, several characters interacting, hands doing
detailed work, readable text), say so and offer the version of their idea that
plays to its strengths. A slow push-in on one subject under one light source will
beat an ambitious action shot every time. Do not silently narrow their request:
offer the trade and let them choose.

**Deciding whether references help.** A reference forces the frame it is placed at
to *become* that image. Character sheets, turnarounds, mood boards and empty
location plates are useless and will wreck the frame. What works is an actual film
still of the scene. If the user's images are not that, offer to write
image-generation prompts for proper keyframes instead.

**Always check the reference's aspect ratio before generating** (`sips -g
pixelWidth -g pixelHeight`) and pick a matching output resolution. A mismatched
reference is centre-cropped with no warning. Also check whether the reference's
*framing* supports the requested action: a close-up portrait cannot become a
walking wide shot in five seconds. Both cases are in `references/parameters.md`.

**Reading the result.** Run `clipcheck.py`, then actually look at the clip. Report
what is wrong with it rather than presenting it as finished.

## Generate

```bash
cd ~/Documents/Applications/ComfyUI
./venv/bin/python ltxgen.py --prompt "..." --seconds 6 --out shotname
```

With reference keyframes, `path:frame`, negative indices allowed:

```bash
./venv/bin/python ltxgen.py --prompt "..." --seconds 8 \
  --ref open.png:0 --ref close.png:-1 --out duel
```

Several clips at once, from a JSON file of `{out, prompt, seconds?, res?, seed?, refs?}`:

```bash
./venv/bin/python ltxgen.py --batch clips.json
```

### Finishing is a separate pass, on approved clips only

The upscale is 80%+ of the wall clock and tells you nothing about whether the shot
works. **Do not put it in the render loop.** Render plain, let the user look, then
finish what survived:

```bash
~/Downloads/cinema/pipeline/upscale.py clip.mp4 \
  --to 1080x1920 --model quality --interpolate 2
```

`upscale.py` takes any existing mp4 — including footage this pipeline did not
make — carries the audio through, and has `--dry-run` to print the cost first.
**Always dry-run before starting anything long.** Measured per 512x512 tile:
`fast` 0.76s (RRDBNet CNN), `quality` 3.13s (DAT transformer, 4.1x slower). Cost
tracks tiles, not seconds of footage: a 576x1024 frame is 6 tiles, an 854x480
frame is 2.

`ltxgen`'s own `--upscale` / `--interpolate` still exist for a one-shot final
render, but reach for them only when the shot is already known good:

```bash
# vertical reel: render at 576x1024, deliver exactly 1080x1920 at 48fps
./venv/bin/python ltxgen.py --prompt "..." --res 576x1024 --seconds 5 \
  --ref open.png:0 --ref close.png:-1 --interpolate 2 --upscale 1.875 --out reel_01
```

`--interpolate N` is RIFE; fps is multiplied to match so duration and audio sync
do not change — it is smoothness, not slow motion. `--upscale N` runs a 4x model
then resamples down to N times the render size.

**Match the delivery size to the destination, not the render size.** A vertical
reel is 1080x1920. Rendering at 1280x704 and handing over 864x480 landscape is
the single most common reason local output looks worse than it should.

The upscale runs before interpolation and in `--upscale-chunk` frames at a time
(default 16). It allocates its whole output batch at once: 241 frames at 4x is a
27 GB tensor, which put this machine into 16 GB of swap and never finished. Lower
the chunk if you see swap climbing.

Full flag list with options and when to change each: `references/parameters.md`.

## A character across several shots

When the user has a character reference and wants more than one shot of the same
person, do not run `ltxgen.py` per shot with the same prose. Use the connector:

```bash
~/Downloads/cinema/pipeline/scenegen.py scene.json
```

It generates each shot's keyframe by **editing the same reference image** through
`imggen.py`, at the clip's exact resolution, then renders the clip from those
keyframes. Identity is anchored to a file rather than re-derived from a
description each time, and the keyframe cannot be centre-cropped because it was
made at the right size.

`--skip-video` stops after the stills for approval; `--skip-stills` resumes from
the manifest. See the `qwen-image` skill for how the keyframes are written.

## Verify before delivering

```bash
./venv/bin/python ~/.claude/skills/ltx-video/scripts/clipcheck.py output/video/shotname_00001_.mp4
```

Hard failures are black renders, wrong frame count, and audio that is silent or
inaudible. Healthy values: pixel_std 30-80, loudness -20 to -32 LUFS. It also
prints an advisory periodicity number, which is a hint to go and look, not proof of
anything.

`clipcheck` does not judge whether a shot is any good, and it cannot see identity
drift. Watch the clip.

`ltxgen.py` already verifies and reseeds on a black render, so a clip that reaches
you has passed once. Run `clipcheck` again anyway when delivering a set, and open
the file.

## Deliver

Send the mp4. State the real render time, the resolution and frame count, and
anything visibly wrong. A `.params.json` sidecar is written next to every clip, so
any result can be reproduced exactly.

## Reference files

| File | Read it when |
|---|---|
| `references/parameters.md` | choosing flags, resolutions, durations |
| `references/prompt-craft.md` | writing or fixing a prompt (read before writing one) |
| `references/troubleshooting.md` | anything looks wrong, or before a long batch |
| `scripts/ltxgen.py` | canonical copy also lives in the ComfyUI folder |
| `scripts/clipcheck.py` | QC any mp4 |
| `pipeline/scenegen.py` | a character reference through stills into clips |
| `pipeline/sync.sh` | **run after editing ltxgen.py** — seven copies exist |

## Measured costs on this machine

M5 Pro, 48 GB. Two-stage at 1280x704, verified renders.

| Clip | Time |
|---|---|
| 4 s | ~8 min |
| 8 s | ~16 min |

Single-stage at 864x480 is ~2.5 min for 4 s and is the right choice for drafts.
Memory peaks around 33 GB of 48 for a single render and is not the constraint;
sustained batches are, because the machine ends up in swap.
