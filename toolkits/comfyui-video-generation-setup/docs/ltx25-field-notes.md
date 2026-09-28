# LTX-2.5 on a Mac — Field Notes

Running a 22-billion-parameter AI video model locally on an **M5 Pro with 48 GB
of memory**. What works, what it costs, and the two bugs that will waste your
time if nobody warns you.

Tested 2 September 2026. Every number here comes from a real render that was
checked afterwards to confirm it actually produced a picture.

---

## The short answer

**Yes, your Mac can run it.** Comfortably. A 2-second clip at 864x480 takes
about 2.5 minutes, an 8-second clip takes about 9 minutes, and you never come
close to running out of memory.

The catch is that it does **not** work out of the box. Two separate bugs stand
between "installed" and "working", and neither one gives you an error message.

---

## The interesting bits, one line each

**Memory and resource use**

- The whole 22B model runs in about **32 GB of your 48 GB** — you never get near the limit.
- Memory barely moves: every setting tested used between **30.1 and 32.2 GB**, a spread of just 2 GB.
- Even the heaviest render left **16 GB of RAM completely unused**.
- Going from the smallest picture (608x352) to the largest (1280x736) — about **twice as wide and twice as tall, so 4.4x the pixels** — changed memory by only **6%** but changed render time by **196%**. You budget minutes, never gigabytes.
- Peak memory is basically just the model weights sitting there; everything else is rounding error.
- `ps` lies about memory on Mac — it reported **2 GB when the real figure was 24 GB** (use `vmmap` instead).

**Speed**

- Apple's GPU has no int8 math, so ComfyUI quietly ran the model **on the CPU** instead — 498% CPU, GPU doing nothing, one step taking over 4 minutes.
- One patch moved the work back to the GPU: CPU fell to **7%**, step time became 8.4 seconds — roughly a **71x speedup**.
- Bigger pictures cost almost exactly in proportion to pixel count — **there is no sweet spot hiding in the middle**.
- Longer clips are cheaper than bigger ones: **3x the length costs 2.6x, 3x the pixels costs 2.9x**.
- Budget about **one minute of computer time per second of finished video**.

**Things that are surprisingly cheap**

- Three reference images cost only **+24% time and zero extra memory**.
- Long detailed prompts are **completely free** — the model pads every prompt to 1024 tokens regardless, so a paragraph costs the same as three words.
- One reference image at the start still influenced the final frame (0.76 similarity) — you may not need three.

**Things that are surprisingly expensive**

- Moving the text encoder onto the GPU made it **4x slower**, not faster — the CPU is genuinely the better place for it.
- `--highvram` does **nothing at all** on Apple Silicon; the setting is overwritten immediately after it is read.

**Bugs that fail silently**

- The default attention setting produces **completely black videos at random seeds** — no error, no warning, the log says "success".
- **16 of our 37 renders were blank** before we found the cause.
- Fixing it costs **19% more time** and is non-negotiable.
- The audio encoder threw away otherwise-finished renders because ComfyUI handed it the entire soundtrack as one chunk.
- FLAC accepted the broken audio silently while AAC refused it — that mismatch is what revealed the real problem.
- **Two entire rounds of benchmarking produced sensible-looking numbers from completely black videos.** A render time tells you nothing about whether it worked.

---

## What to actually do on an M5 Pro 48 GB

### Pick the right model file

Use the **distilled int8** version (21.5 GB). The full-precision version is
42 GB and will not fit alongside everything else. You are not missing much —
distilled needs only 8 steps instead of 30+.

### Pick your resolution by what you are doing

| You are... | Use | 2-second clip takes |
|---|---|---|
| Checking if the motion works | 608x352 | ~1.8 min |
| Normal working / judging a shot | **864x480** | **~2.5 min** |
| Rendering something final | 1280x736 | ~5.2 min |

Going below 608x352 saves almost nothing. 720p works fine — it is just slow
enough that you would not want to iterate at it.

### How long will my clip take?

At 864x480, roughly:

| Clip length | Time |
|---|---|
| 2 seconds | ~2.5 min |
| 4 seconds | ~4.5 min |
| 6 seconds | ~6.7 min |
| 8 seconds | ~9 min |

Add about 25% if you use reference images. Add 20 seconds the first time you
use a new prompt (the text encoder has to run).

### Spend your effort in the right place

Ranked by what you get per minute of extra render time:

1. **Write a longer, more specific prompt** — costs nothing at all
2. **Add reference images** — costs 24%, and locks character appearance hard
3. **Make the clip longer** — 3x length for 2.6x time
4. **Increase resolution** — the most expensive option, roughly linear in pixels

The cheapest way to improve a shot on this machine is to describe it better and
show the model what you mean, rather than render it larger.

### Frame count rule

Frames must satisfy `(frames - 1)` divisible by 8. At 24fps that means 49
frames = 2s, 97 = 4s, 145 = 6s, 193 = 8s. Width and height must both be
multiples of 32.

---

## Two things you must set up, or nothing works

### 1. Always launch with `--use-pytorch-cross-attention`

Without it you get black videos at random. There is no error message. The log
says the render succeeded. The file is just blank.

    ./start.sh          # already includes the flag

**How to check a render worked:** a real video has visible variation between
pixels; a broken one is mathematically flat. Black video also compresses to a
suspiciously tiny file (13 KB instead of 200 KB).

### 2. Apply the int8 patch after every ComfyUI update

    git apply mps-int8-emulate.patch

`git pull` will remove it, and the model silently drops back to running on the
CPU at roughly a tenth of the speed. Nothing warns you; it just gets slow.

---

## Full measured numbers

All runs: 22B distilled, 8 steps, single stage, audio on, verified afterwards.

### Resolution (2-second clips)

| Resolution | Megapixels | Time | Peak memory |
|---|---|---|---|
| 608x352 | 0.21 | 106 s | 30.1 GB |
| 736x416 | 0.31 | 117 s | 30.1 GB |
| **864x480** | 0.41 | **154 s** | 32.1 GB |
| 1056x608 | 0.64 | 232 s | 31.7 GB |
| 1280x736 | 0.94 | 314 s | 32.0 GB |

### Clip length (at 864x480)

| Length | Frames | Time | vs 2s | Peak memory |
|---|---|---|---|---|
| 2 s | 49 | 154 s | 1.00x | 32.1 GB |
| 4 s | 97 | 262 s | 1.70x | 31.9 GB |
| 6 s | 145 | 403 s | 2.61x | 32.1 GB |

### Reference images (at 864x480, 2s)

| References | Time | vs none | Peak memory | Did the guide land? |
|---|---|---|---|---|
| none | 158 s | 1.00x | 32.2 GB | n/a |
| 1 image | 174 s | 1.10x | 32.0 GB | 0.998 similarity |
| 3 images | 196 s | 1.24x | 32.0 GB | 0.996–0.999 |

### Text encoder placement

| Where it runs | Time | Peak memory |
|---|---|---|
| **CPU (the default — leave it)** | **21 s** | 32.9 GB |
| GPU, offloaded to CPU | 46 s | 30.5 GB |
| GPU, pinned there | 81 s | 44.3 GB |

---

## Real-world example

An 8-second cinematic duel — 864x480, 193 frames, three reference keyframes
guiding the opening, the impact and the closing shot:

- **11 minutes** to render
- All three keyframes hit their marks (0.958–0.983 similarity)
- The model produced **genuine hard cuts** at 3.25 s and 5.50 s rather than one
  continuous camera move, matching the storyboard's shot changes
- Synchronised audio generated alongside the video

---

## What we did not test

Multi-stage upscaling, prompts longer than 1024 tokens, more than three
reference images, and why the attention bug produces NaN in the first place —
only that switching the backend eliminates it entirely.
