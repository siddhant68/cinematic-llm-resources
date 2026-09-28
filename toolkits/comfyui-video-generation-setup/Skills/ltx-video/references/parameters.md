# ltxgen parameters

Run from the ComfyUI folder with its venv python:

```bash
cd ~/Documents/Applications/ComfyUI
./venv/bin/python ltxgen.py [flags]
```

## Content

| Flag | Default | Notes |
|---|---|---|
| `--prompt TEXT` | required | One flowing paragraph. See `prompt-craft.md`. |
| `--prompt-file PATH` | | Same, read from a file. Easier for long prompts. |
| `--negative TEXT` | a default that is **not evaluated** | See "Negative prompts do nothing at CFG 1" below. Changing it has no effect at default settings. |
| `--out NAME` | `clip` | Filename prefix. Output lands in `output/video/NAME_00001_.mp4`. |

## Shape

| Flag | Default | Options and guidance |
|---|---|---|
| `--seconds N` | `4` | Any number. Converted to frames as `round(N*fps)+1`, then snapped so `(frames-1) % 8 == 0`. 4 s = 97 frames, 6 s = 145, 8 s = 193. |
| `--fps N` | `24` | 24 is cinematic and what everything here is measured at. 30 works. Higher costs proportionally more. |
| `--res WxH` | `1280x704` | Auto-snapped: multiples of 32 for single-stage, **64 for two-stage** because the base pass runs at half size. It tells you when it snaps. |

**Landscape 16:9-ish** (two-stage legal):

| Res | MP | Use |
|---|---|---|
| `640x352` | 0.22 | fast draft |
| `864x480` | 0.41 | everyday working size |
| `1152x640` | 0.74 | good middle |
| `1280x704` | 0.90 | delivery, the default |
| `1920x1088` | 2.09 | slow, only if you need it |

**Portrait and square are fully supported.** Nothing restricts you to landscape;
the only rule is the multiple-of-64 grid for two-stage.

| Res | Ratio | Use |
|---|---|---|
| `576x1024` | 9:16 | vertical / Shorts |
| `768x960` | 4:5 | portrait reference, social |
| `704x704` | 1:1 | square |
| `960x768` | 5:4 | mild landscape |

**Match the output aspect to your reference image.** See the crop warning below.

## Quality

| Flag | Default | Guidance |
|---|---|---|
| `--stages 1\|2` | `2` | **2** = base pass at half resolution, latent 2x upscale, 3-step refine. This is what the official template does and it is visibly better. **1** = single pass, roughly a third of the time. Use 1 for drafts and iteration, 2 for anything you show someone. |
| `--sampler NAME` | `euler_ancestral` | What the official template uses. Little reason to change. |
| `--video-cfg N` | `1.0` | The distilled model is trained for CFG 1. Raising it causes flicker and drift rather than more adherence. |
| `--audio-cfg N` | `1.0` | Same. |

### Negative prompts do nothing at CFG 1

`LTXVDualCFGGuider` falls back to single-CFG when `video_cfg == audio_cfg`
(`comfy_extras/nodes_lt.py:1077`) without setting `disable_cfg1_optimization`.
ComfyUI then drops the unconditional pass entirely because the scale is 1.0
(`comfy/samplers.py:610`). The negative conditioning is never evaluated.

Both default to 1.0, so **the default negative prompt has no effect**, and neither
does anything you pass to `--negative`. This is correct for a CFG-distilled model
and the right trade; it just means the negative is not the lever.

To make it live you have to leave the distilled operating point, e.g.
`--video-cfg 2.0 --audio-cfg 1.0`, which costs a second model pass per step and
tends to add flicker on this model. Fix artifacts in the positive prompt instead.
| `--no-audio` | off | Skips the audio branch. Slightly faster. Audio is genuinely good, so keep it unless the clip is going under music. |

## References

| Flag | Default | Guidance |
|---|---|---|
| `--ref PATH[:FRAME]` | none | Repeatable. `:0` first frame, `:-1` last frame, `:48` a specific frame. Frame index snaps down to a multiple of 8. Files are copied into `input/` automatically. |
| `--ref-strength N` | `1.0` | 1.0 pins the frame hard to the image. Lower (0.7-0.9) gives the model room to blend, useful for a mid-clip reference that would otherwise cause a visible jump. |

**A reference makes that frame become that image.** Give it an actual film still of
the scene. Character turnarounds, mood boards and empty location plates will be
reproduced literally and ruin the frame.

### A mismatched reference is silently centre-cropped

`LTXVAddGuide` resizes the reference to the output dimensions with `crop="center"`
(`comfy_extras/nodes_lt.py:307`). There is no resize stage in `ltxgen.py` and **no
warning anywhere** when the aspect ratios differ.

Feed a 4:5 portrait into the default `1280x704` and you get a 16:9 band taken
through the middle of the image: the top of the head gone, the shot opening on a
cropped face. The render succeeds, `clipcheck` reports ok, and nothing tells you.

**So: check the reference's aspect ratio first and pick a matching output size.**

```bash
sips -g pixelWidth -g pixelHeight ref.png
```

Then choose the nearest resolution on the 64 grid with the same ratio. A 1122x1402
reference is 4:5, so `768x960` (768 = 64x12, 960 = 64x15) fits exactly.

If you must change the framing, crop the image deliberately to the target ratio
yourself so you control what is lost.

### Identity drift

A single reference at frame 0 pins the opening and then loosens. Measured on a 5
second clip, correlation to the reference went 0.90 at frame 0, 0.53 by frame 36,
and the face was visibly a different person by frame 120.

For a held identity, put a reference at **both ends** (`:0` and `:-1`). Untested at
the time of writing whether that fully fixes it, but it is the obvious lever and
costs about 10% more time.

Cost: 1 reference ~+10% time, 3 references ~+24%, no extra memory. Cheap.

## Finishing

Both run after the VAE decode, in this order, and neither touches the sampler.

| Flag | Default | Guidance |
|---|---|---|
| `--interpolate N` | `1` | RIFE optical-flow interpolation, 2-4x. Emits `(frames-1)*N + 1` frames and multiplies fps by the same factor, so **duration and audio sync are unchanged** — this buys smoothness, not slow motion. |
| `--upscale N` | `1.0` | Pixel upscale, e.g. `2.0`. Runs a 4x model then resamples down to N times the render size; upscale-then-downsample resolves more real detail than asking a scaler for the intermediate factor. |
| `--upscale-model NAME` | `fast` | `fast` = 4x-UltraSharp (RRDBNet CNN). `quality` = 4x-UltraSharpV2 (DAT transformer). Or an explicit filename. |
| `--upscale-chunk N` | `16` | Frames per upscale pass. Lower it if the stage pushes the machine into swap. |

**Use `fast` unless you have a reason not to.** This is per-frame work, so the
architecture difference compounds: UltraSharpV2 is a DAT transformer with 2116
tensors against the CNN's 702, and on MPS that is minutes per clip. `quality` is
for a hero shot or a single still, not a reel.

The stage-2 latent upsampler is not this. That is a refinement pass *inside* the
sampler; these are the separate finishing legs between a render and delivery.

Pick the render size for the model and the final size for the destination. A
vertical reel wants `--res 576x1024 --upscale 1.875`, which lands on exactly
1080x1920. Interpolation to 48fps is what makes a slow push-in stop stuttering.

Cost is roughly linear in output pixels and frames. Interpolation runs before the
upscale so RIFE works on the smaller frames; that is cheaper in peak memory but
means interpolated frames get upscaled too.

| Flag | Default | Guidance |
|---|---|---|
| `--lora NAME[:STRENGTH]` | none | Patches the transformer, repeatable. Applies to both stages. Strength defaults to 1.0. |

## Control

| Flag | Default | Guidance |
|---|---|---|
| `--seed N` | random | Set it to reproduce a shot exactly, or to A/B a settings change. |
| `--retries N` | `2` | Reseeds and retries when a render comes back black. Set 0 when you are deliberately testing a specific seed. |
| `--batch FILE` | | JSON list of `{out, prompt}` plus optional `seconds`, `res`, `seed`, `stages`, `fps`, `negative`, `ref_strength`, `refs`. Per-item values override the command line. |
| `--dry-run` | off | Prints resolved resolution, frames and seed without generating. Use it to sanity-check a batch. |

## Environment

`LTXGEN_HOST` overrides the ComfyUI address, default `http://127.0.0.1:8188`.

## Batch file example

```json
[
  {"out": "wide_establishing", "prompt": "...", "seconds": 6},
  {"out": "closeup_hands",     "prompt": "...", "seconds": 3, "res": "864x480", "stages": 1},
  {"out": "final_shot",        "prompt": "...", "seconds": 8, "seed": 4242,
   "refs": ["/path/open.png:0", "/path/close.png:-1"]}
]
```

## What each clip leaves behind

- `output/video/NAME_00001_.mp4` the clip
- `output/video/NAME_00001_.params.json` every parameter used, for exact reproduction
