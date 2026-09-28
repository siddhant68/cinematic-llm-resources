# ComfyUI + LTX-2.5 on Apple Silicon (M5 Pro, 48 GB)

## What this is

ComfyUI 0.34.0, Python 3.12, PyTorch 2.13 on MPS, running LTX-2.5 22B distilled
from the official `comfy-int8-convrot` weights.

    ./start.sh                 # launch on http://127.0.0.1:8188
    ./download-ltx25.sh        # re-download the model set (needs `hf auth login`)

## IMPORTANT #1: always launch with --use-pytorch-cross-attention

`start.sh` already does this. Do not remove it, and do not launch `main.py`
directly without it.

ComfyUI's default sub-quadratic attention returns **NaN on MPS at some seeds**.
The NaN propagates through the VAE and you get a **fully black MP4 with a silent
audio track** - no error, no warning, exit status `success`. It is seed-dependent,
so it looks random and intermittent.

16 of the 37 renders made while setting this up were black before the cause was
found. Verified: seed 2001 at 864x480 is pure black on the default and correct
with the flag, same server and graph, back to back.

Costs about 19% time. Non-negotiable.

**How to spot it:** decode the output and check pixel standard deviation. A real
render is ~55-80; a NaN render is exactly 0.00. Black video also compresses to a
suspiciously tiny file.

    # quick check of the newest render
    ./venv/bin/python - <<'EOF'
    import av, numpy as np, glob
    p=sorted(glob.glob("output/video/*.mp4"))[-1]
    c=av.open(p); fr=[f.to_ndarray(format="rgb24").astype(float) for f in c.decode(video=0)]
    print(p, "pixel std:", round(float(np.mean([a.std() for a in fr])),2))
    EOF

## IMPORTANT #2: local patch to comfy/

This install carries a 3-part local patch, saved as `mps-int8-emulate.patch`.
**A `git pull` will likely clobber it. Re-apply it after any ComfyUI update**
or LTX-2.5 becomes ~10x slower and pegs the CPU instead of using the GPU.

    git apply mps-int8-emulate.patch     # after updating
    git diff --stat                      # should show 2 files, ~31 insertions

### The problem it fixes

LTX-2.5's official ComfyUI weights are INT8 (`int8-convrot`). ComfyUI executes
INT8 linears with `torch._int_mm`, which **has no Metal kernel**. With
`PYTORCH_ENABLE_MPS_FALLBACK=1` set, PyTorch silently runs it on the CPU
instead of erroring, so every quantized linear round-trips MPS -> CPU -> MPS.

Symptom: ~500% CPU, idle GPU, and a single sampling step not finishing in
minutes. The give-away line is:

    UserWarning: The operator 'aten::_int_mm' is not currently supported on the
    MPS backend and will fall back to run on the CPU.

### The fix

ComfyUI already has an "emulated" path for quantized formats the device can't
execute natively (it dequantizes to bf16 and does a normal on-device matmul).
`pick_operations()` used it for nvfp4/mxfp8/fp8 but had **no capability check
for int8 at all**, so int8 always took the native path.

1. `comfy/model_management.py` - new `supports_int8_compute()`, returns False on MPS.
2. `comfy/ops.py` - `pick_operations()` adds `int8_tensorwise`, `convrot_w4a4`,
   `asym_w4a8_int8` to `disabled` when int8 isn't supported.
3. `comfy/ops.py` - `MixedPrecisionOps.Linear._forward()` dequantizes a
   still-quantized weight when `_full_precision_mm` is set. This is the one that
   actually matters: `F.linear` on a `QuantizedTensor` gets intercepted by
   `__torch_dispatch__` and routed into the INT8 kernel regardless of the flag,
   so it has to be dequantized before the call.
   (`linear_input_act()` got the same guard - it's a second, fused entry point.)

Weights stay stored as INT8, so the memory saving is preserved. Only a
transient per-layer bf16 copy is materialised during the matmul.

### Measured effect (608x352, 49 frames, 8 steps)

| | before | after |
|---|---|---|
| CPU | ~498% | ~7% |
| `_int_mm` calls | thousands | 0 |
| step time | did not finish 1 step in 4 min | 8.4-8.9 s/it |
| total | - | 162 s |
| peak memory | 24 GB | 30.1 GB |

Worth reporting upstream - this affects every Apple Silicon user of any INT8
ComfyUI checkpoint, not just LTX-2.5.

## Model set (models/, ~42 GB)

    diffusion_models/ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors   21.5 GB
    text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors           15.4 GB
    text_encoders/gemma4_e2b_it_int8_convrot.safetensors      5.2 GB  (prompt enhancer, optional)
    vae/ltx-2.5-video-vae-bf16.safetensors                     1.5 GB
    vae/ltx-2.5-audio-vae-bf16.safetensors                     0.4 GB
    latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors  1.0 GB
    model_patches/ltx-2.5-duration-head-bf16.safetensors       small (Auto Duration)

`Lightricks/LTX-2.5` is a gated repo: accept the licence on the model page AND
use a real access token (a browser/OAuth `hf auth login` session does NOT carry
gated-repo file access).

## Old models

`extra_model_paths.yaml` read-throughs to the older ComfyUI Desktop install at
`../ComfySid/ComfyUI/models` (~104 GB). Deliberately not `is_default`, so new
downloads land here. Delete that file to unlink; nothing is written back.

## Workflows

- Official templates: browse Templates > Video > LTX-2.5 (t2v / i2v / flf2v).
  Defaults are 1280x720 / 121 frames / two-stage - heavy for this machine.
- `ltx25_smoketest_api.json` - flat API-format graph, 608x352 / 49 frames /
  single stage. Queue with:

      curl -s -X POST http://127.0.0.1:8188/prompt -H 'Content-Type: application/json' \
        -d "{\"prompt\": $(cat ltx25_smoketest_api.json)}"

---

# Measured scaling (revision 2 - verified)

All numbers below re-measured with `--use-pytorch-cross-attention`, and every run
decoded and checked (frame count, pixel std, audio RMS) before its timing was
accepted. Revision 1 of these numbers was partly measured on black renders.

22B distilled int8-convrot, 8 steps, euler_ancestral, CFG 1, single stage,
tiled VAE decode, audio on, one fixed seed per sweep.

## Resolution (49 frames, 2s @ 24fps)

| Resolution | MP   | Time  | Peak RAM |
|---|---|---|---|
| 608x352    | 0.21 | 106 s | 30.1 GB |
| 736x416    | 0.31 | 117 s | 30.1 GB |
| 864x480    | 0.41 | 154 s | 32.1 GB |
| 1056x608   | 0.64 | 232 s | 31.7 GB |
| 1280x736   | 0.94 | 314 s | 32.0 GB |

Time tracks pixels almost linearly (slightly sub-linear). No knee.

## Clip length (864x480)

| Clip | Frames | Time  | vs 2s | Peak RAM |
|---|---|---|---|---|
| 2 s  | 49     | 154 s | 1.00x | 32.1 GB |
| 4 s  | 97     | 262 s | 1.70x | 31.9 GB |
| 6 s  | 145    | 403 s | 2.61x | 32.1 GB |

## Reference images (864x480, 49f, guides at 0/24/48)

| References | Time  | vs none | Peak RAM | Guide fidelity |
|---|---|---|---|---|
| none       | 158 s | 1.00x   | 32.2 GB  | +0.25 (unrelated) |
| 1 image    | 174 s | 1.10x   | 32.0 GB  | +0.998 |
| 3 images   | 196 s | 1.24x   | 32.0 GB  | +0.996 .. +0.999 |

Guide fidelity = correlation between each guided frame and its reference image,
which confirms the guides actually landed rather than being silently ignored.

## Text encoder placement - tested and rejected

| Placement                | Encode | Peak RAM |
|---|---|---|
| CPU (ComfyUI default)    | 21.1 s | 32.9 GB |
| GPU, CPU offload         | 46.0 s | 30.5 GB |
| GPU pinned (--gpu-only)  | 81.1 s | 44.3 GB |

Leave it on the CPU. Also note `--highvram` does nothing on Apple Silicon:
`vram_state` is overwritten to SHARED after that flag is read.

## Budget guidance

- Iterate at 608x352, judge at 864x480, finish at 1280x736.
- Prefer longer clips over wider ones (3x length = 2.61x; 3x pixels ~= 2.9x).
- Prompts and references are cheap; both beat one resolution step.
- Memory is never the constraint: ten configs spanned 30.1-32.2 GB of 48.

Times assume the model is resident and text conditioning cached; a prompt change
adds ~21 s of CPU text encoding.
