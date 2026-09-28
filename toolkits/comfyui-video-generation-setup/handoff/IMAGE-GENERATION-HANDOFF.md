# Handoff: build a local image generation capability

> **HISTORICAL — this brief was completed on 2026-09-05 and its model list is
> already out of date.** The capability now exists: see
> `../../image_generation_setup/`, the `qwen-image` skill, and
> `../../pipeline/scenegen.py`. In particular the table below predates
> `qwen-image-edit-2511` and its 4-step Lightning LoRA, which are what reference
> and character work actually run on. Do not use this list to decide anything;
> read `../../image_generation_setup/docs/model-research.md` instead.

**For:** a fresh Claude session, on this Mac.
**From:** the session that built the LTX-2.5 video pipeline (`../docs/`).

---

## Your mission

Work out how to produce **high quality still images locally in ComfyUI**, good
enough for two jobs:

1. **B-roll frames for YouTube videos** — cinematic stills that hold up full screen
2. **Reference keyframes for video generation** — images fed to LTX-2.5 locally, or
   to Higgsfield, as the first or last frame of a shot

Then build it, the same way the video side was built: a parameterised script, a QC
tool that catches silent failures, a skill so future sessions do not start over.

**Start by researching.** The image model field moves fast and this brief was
written on 5 September 2026. Do not assume what is here is still the best choice.
Check what currently produces the best photoreal stills that run in ~40 GB of
unified memory, and what the community actually recommends for ComfyUI on Apple
Silicon.

---

## What is already on this machine

**Do not download anything before checking this list.** There is 104 GB of models
already here, at `~/Documents/Applications/comfy-models/`, shared into ComfyUI via
`extra_model_paths.yaml`.

| Model | Size | Where |
|---|---|---|
| `flux1-dev.safetensors` | 23.8 GB | `checkpoints/` |
| `flux1-schnell-fp8.safetensors` | 17.2 GB | `checkpoints/` |
| `flux1-dev-fp8.safetensors` | 17.2 GB | `diffusion_models/` |
| `juggernautXL_ragnarok.safetensors` | 7.1 GB | `checkpoints/` (SDXL) |
| `qwen-image-Q8_0.gguf` | 21.8 GB | `gguf/` |
| `qwen_2.5_vl_7b_fp8_scaled` | 9.4 GB | `text_encoders/` |
| `t5xxl_fp8_e4m3fn` | 4.9 GB | `text_encoders/` |
| `clip_l` | 0.2 GB | `text_encoders/` |
| `qwen_image_vae` | 0.3 GB | `vae/` |
| `Qwen-Image-Lightning-8steps-V1.1` | LoRA | `loras/` |

Flux dev, Flux schnell, SDXL and Qwen-Image are all present. There is a strong
chance you need to download nothing at all. Verify quality empirically before
adding 20 GB of anything.

Also present: 5.8 GB `clip_vision`, 1.7 GB `photomaker` (identity-preserving
portraits), 16 GB `diffusion_models`, 1.6 GB `loras`.

---

## The environment

| | |
|---|---|
| Machine | M5 Pro, 48 GB unified, macOS 26 |
| ComfyUI | `~/Documents/Applications/ComfyUI`, v0.34.0, plain git checkout |
| Python | its own venv at `venv/bin/python` (3.12) |
| Launch | `./start.sh` **only** |
| Models | `~/Documents/Applications/comfy-models/` (shared) |
| Free disk | ~500 GB |

### Two things that will waste your day if you do not know them

**1. The int8 patch.** `patches/mps-int8-emulate.patch` is applied to `comfy/`.
Apple's GPU has no int8 matmul kernel, so ComfyUI silently ran quantized models on
the **CPU** at roughly a tenth of the speed, with no error. Three hunks fix it.
`git pull` removes them. Symptom if lost: ~498% CPU, idle GPU, absurd step times.

```bash
cd ~/Documents/Applications/ComfyUI && git apply mps-int8-emulate.patch
```

This affects **any int8 checkpoint**, not just video. If you pick a quantized image
model, this matters to you.

**2. `--use-pytorch-cross-attention`.** ComfyUI's default sub-quadratic attention
returns NaN on MPS at some seeds. For video that meant black clips. For images,
expect black or corrupt frames. `start.sh` carries the flag. Never launch
`main.py` directly.

---

## Hard-won lessons that transfer directly

### Verify output, never trust exit codes

The single most expensive mistake made on the video side: **two entire rounds of
benchmarking produced clean, plausible, monotonic numbers from renders that were
completely black.** The log said `success` every time.

Build the equivalent check before you build anything else. For images:

- pixel standard deviation (a NaN image is exactly 0.00)
- file size sanity (a blank PNG compresses to almost nothing)
- actually open the file

`../scripts/clipcheck.py` is the video version. Steal its structure.

### Your monitoring tools lie on Apple Silicon

- `ps -o rss` under-reports by ~10x. A process at 28 GB reads as 2.5 GB. Use
  `vmmap -summary <pid> | grep "Physical footprint"`.
- macOS swap `used` is sticky and never shrinks. A high number alone means nothing.
  Cross-check with `vm_stat` free pages.
- `pgrep -af` does not print command lines on macOS. Use `ps -o command=`.

Each of those produced a wrong conclusion before being caught.

### ComfyUI's cache will invalidate your benchmarks

It caches per node by input hash. Change only the resolution and it reuses cached
conditioning; change nothing and it returns the previous result reporting success.
Two runs came back in 5.0 s and 0.13 s this way. **Vary the seed for any cold
measurement.**

### Restart between renders, not just between batches

At 0.7 MP and above a single render can exhaust the machine. One clip took 74
minutes instead of 8 because the machine was in swap, and it degrades gradually so
it reads as the model being slow.

### Tiled decode leaves seams

Setting `temporal_size` below the frame count put a visible glitch every 24 frames.
For images the equivalent risk is **spatial** tiling: check for seams at tile
boundaries if you use `VAEDecodeTiled` on large canvases. ComfyUI's default is no
tiling; only enable it if you actually need the memory.

### Do not build a detector you cannot calibrate

An automatic seam detector was attempted and abandoned: on clips known to contain
seams the signal ranged 0.7x to 2.6x and overlapped clean clips. It shipped as an
*advisory* with an explicit "not proof" caveat, and the real control became a
deterministic settings check. Prefer preventing a failure to detecting it.

---

## What LTX-2.5 needs from your images

This is the part that determines whether your output is actually useful downstream.

**A reference forces that frame to become that image.** It is a keyframe, not a
style hint.

| Works | Does not work |
|---|---|
| An actual film still of the scene | Character turnarounds |
| Full scene, correct framing | Mood boards |
| Matching aspect ratio | Empty location plates |
| Consistent lighting across a set | Anything on flat grey |

**Aspect ratio is critical.** `LTXVAddGuide` centre-crops a mismatched reference
with **no warning** (`comfy_extras/nodes_lt.py:307`, `crop="center"`). Feed a 4:5
portrait into a 16:9 render and the top of the head is silently cut off. So:

- Generate at the **exact aspect** the video will use
- LTX needs width and height divisible by 32, or **64** for its two-stage pipeline
- Useful targets: `1280x704`, `768x960`, `1152x640`, `576x1024`, `704x704`
- Generating at 2x those and downscaling is fine and gives cleaner detail

**Framing matters as much as content.** A perfectly good close-up portrait is the
wrong reference for "walking through a garden", because frame 0 becomes that
close-up and five seconds is not enough to pull back to a wide. When a set of
keyframes is wanted, ask what shot size each one needs.

**Consistency across a set beats quality within one image.** If frame A and frame C
disagree on lighting or costume, the video between them visibly morphs. Generate a
set in one session with fixed settings.

**Identity drifts.** A single reference at frame 0 pins the opening and loosens:
measured correlation went 0.90 at frame 0 to a visibly different face by frame 120.
Two references, first and last, is the mitigation. Your images will be judged on
whether a face survives that.

---

## Suggested shape for what you build

Mirror the video side; it works and it is documented.

```
ltxgen.py   ->  imggen.py      parameterised: prompt, model, size, seed,
                               steps, batch, refs; verifies; writes a
                               .params.json sidecar for reproducibility
clipcheck.py -> imgcheck.py    black/NaN, size sanity, optional seam scan
ltx-video/  ->  a skill        SKILL.md + references/ + scripts/
```

Install the skill at `~/Developer/video-pipeline/skills/<name>` and symlink it into
`~/.claude/skills/`. All 18 existing skills follow that pattern.

Worth deciding early and writing down: which model for which job. Photoreal
cinematic b-roll, stylised, and character-consistent keyframes may not want the
same checkpoint.

---

## Read these before starting

| File | Why |
|---|---|
| `../docs/how-to-generate-video.md` | how the video side is driven; mirror its shape |
| `../docs/comfyui-setup-and-benchmarks.md` | install, patch, every measured number |
| `../docs/ltx25-field-notes.md` | the failures and how they were found |
| `../Skills/ltx-video/references/troubleshooting.md` | every silent failure mode |
| `../Skills/ltx-video/references/parameters.md` | the CLI shape to mirror |
| `../scripts/ltxgen.py` | working reference implementation |

---

## Tone note

The video work went wrong repeatedly, and the value came from saying so plainly and
measuring again. Several published numbers had to be retracted. If something does
not reproduce, say it did not reproduce. Do not present an unverified render as
finished.
