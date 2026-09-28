# Troubleshooting

Every failure here is silent. None of them raise an error, and several report
`success`. Assume nothing from an exit code.

## The output is completely black

**Cause.** ComfyUI's default sub-quadratic attention returns NaN on MPS at some
seeds. The NaN propagates through the decoder and every pixel comes out zero. The
log says success.

**Fix.** Launch with `--use-pytorch-cross-attention`. `start.sh` already does. Do
not run `main.py` directly without it. Costs about 19% time.

**Detect.** Mean pixel standard deviation. A real render is 30-80; a NaN render is
exactly 0.00. A black clip also compresses to about 13 KB against ~600 KB for a
real one.

**Recover.** It is seed-dependent, so re-run with a different seed. `ltxgen.py`
does this automatically via `--retries`.

## Audio is silent but the picture is fine

Same root cause, hitting only the audio branch. Change the seed. The muxer has
been patched to substitute silence and warn rather than aborting the save, so you
get a usable clip with a dead track instead of losing the render.

## A glitch at regular intervals, roughly once a second

**Cause.** Tiled VAE decode chunking in time. A seam appears every
`temporal_size - temporal_overlap` frames. With 32/8 that is every 24 frames, i.e.
once a second at 24fps. It is most visible over motion.

**Fix.** `temporal_size` must exceed the clip length. `ltxgen.py` sets
`max(64, frames + 8)`, so it never chunks. ComfyUI's own decoder defaults to no
temporal chunking; this is only a problem if something sets it low.

**Verify deterministically.** Check the `.params.json` sidecar rather than trying
to detect it in the output. `clipcheck.py` does this.

**Do not trust after-the-fact detection.** A 4 second clip has only three boundary
frames, which is not enough signal. Measured across clips known to contain seams,
prominence ranged 0.7 to 2.6 and overlapped clean clips. `clipcheck` reports the
number as an advisory only.

## Everything is suddenly 5-10x slower

**Cause.** The machine is in swap. It degrades gradually, so it reads as the model
being slow.

**Check both, not just swap.** macOS swap `used` is sticky and cumulative: it does
not shrink when memory is freed, so a high number alone means nothing.

```bash
sysctl -n vm.swapusage      # sticky, high is not proof
vm_stat | head -4           # free pages: this is the real signal
/usr/bin/vmmap -summary $(pgrep -f main.py | head -1) | grep -i "physical footprint"
```

Restart ComfyUI only when **ComfyUI itself** has grown across a sustained batch. If
free pages are healthy and ComfyUI is small, the swap is held by other apps and a
restart costs you a full model reload for nothing.

**Use `vmmap` physical footprint for that judgement, never `ps -o rss`.** RSS
under-reports this process by roughly 10x: a server sitting at 28 GB footprint
reads as 2.5 GB under `ps`, which makes a bloated server look idle and healthy.

**Measured.** One clip took 74 minutes against a normal 8. Sampling degraded from
13.5 s/it to 667 s/it inside a single session. ComfyUI's own footprint never moved,
so nothing leaked in the model.

**Avoid.** Restart ComfyUI between batches, and **between individual renders at
0.7 MP or above**. 90 seconds well spent.

Measured: a 768x960 two-stage render was started on a freshly restarted server with
4.9 GB free. It still reached **0.0 GB free inside that single 6 second clip**, and
the refine stage ran at 98-115 s/it against roughly 40 s/it on a clean machine.
Total 16.9 min against an expected 12.

One render at this size is enough to exhaust the machine on its own. "Restart
between batches" is not conservative enough above about 0.7 MP; restart every time.

Below roughly 0.4 MP (864x480 and smaller) a few renders back to back are fine.

## A render finished suspiciously fast

ComfyUI caches per node by input hash. Changing only the resolution still reuses
cached text conditioning; changing nothing returns the previous result and reports
success. Two runs came back in 5.0 s and 0.13 s this way.

**Fix.** Vary the seed for any cold measurement.

## The model runs but the GPU is idle and the CPU is pegged

**Cause.** LTX-2.5's weights are int8. Metal has no int8 matmul kernel, so
`torch._int_mm` silently falls back to the CPU when `PYTORCH_ENABLE_MPS_FALLBACK=1`
is set, and every quantized layer round-trips off the GPU.

**Fix.** A three-part patch to `comfy/` is already applied in this install and
saved as `mps-int8-emulate.patch`. **A `git pull` will remove it.** Re-apply:

```bash
cd ~/Documents/Applications/ComfyUI && git apply mps-int8-emulate.patch
```

**Symptom if lost.** ~498% CPU, idle GPU, a single sampling step not finishing in
four minutes, versus 8.4 s/it when correct.

## Motion looks warped, or a character changes appearance

Usually the prompt, not the model. Check `prompt-craft.md`: one camera move, one
light source, chronological action, no tag lists. If the subject is fast action or
several interacting characters, the model is being asked for something it does not
do well, and no setting will fix that.

For character consistency across a shot, a reference keyframe at frame 0 is the
strongest lever and costs about 10% more time.

## Where things live

| | |
|---|---|
| ComfyUI | `~/Documents/Applications/ComfyUI` |
| Launcher, carries the attention flag | `start.sh` |
| Generator | `ltxgen.py` |
| The int8 patch | `mps-int8-emulate.patch` |
| Setup and measured results | `README-MAC-SETUP.md` |
| Outputs | `output/video/` |
| Reference images get copied to | `input/` |
