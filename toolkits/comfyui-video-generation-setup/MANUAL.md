# Generating video with a fresh Claude session

Everything below works in a brand new session with no context. The skills are
installed and auto-trigger; you do not need to name them.

---

## The short version

Open a session in any folder and say:

> Generate a 6 second video. Prompt: a lone red telephone box on a foggy moor at
> dawn, slow push in. Reference image at /path/to/still.png on the first frame.

That is enough. It will start ComfyUI if needed, write a proper prompt, generate,
verify the output is not black, and send you the clip.

---

## What you can pass

Only the first is required.

| You say | Options | Default if you say nothing |
|---|---|---|
| **the prompt or the idea** | a full paragraph, or one line it expands for you | required |
| **duration** | any length, 8s is the practical ceiling | 4 seconds |
| **reference images** | file paths, and where each sits in time | none |
| **resolution** | `640x352` draft · `864x480` working · `1280x704` delivery · `1920x1088` slow | 1280x704 |
| **draft or final** | "quick draft" = single stage, ~3x faster · "final" = two stage | final |
| **seed** | a number, to reproduce or A/B a shot | random |
| **fps** | 24 or 30 | 24 |
| **audio** | "no audio" to skip it | audio on |
| **how many** | "make me three variations" | one |

### Reference images, the one thing to get right

A reference **forces that frame to become that image**. It is a keyframe, not a
style hint.

- **Works:** an actual film still of the scene you want
- **Does not work:** character turnarounds, mood boards, empty location plates,
  anything on a flat grey background. It will reproduce them literally.

**Two traps worth knowing about:**

A reference whose aspect ratio does not match the output is **silently
centre-cropped**. Feed a portrait into the default widescreen and you lose the top
of the head, with no warning. Say what shape your image is, or just let it check.

A single reference at the start pins the opening and then **drifts**. On a 5 second
test the face was measurably a different person by the end. For a held identity ask
for a reference at both the first and last frame.

Say where each goes: *"this one on the first frame, this one on the last"*. First
and last is the safest pattern. Cost is about +10% for one, +24% for three.

If your images are the wrong kind, ask it to write image-generation prompts for
proper keyframes first. It knows how.

---

## What it costs

M5 Pro, 48 GB, measured.

| Clip | Draft (single stage) | Final (two stage) |
|---|---|---|
| 4 seconds | ~2.5 min | ~8 min |
| 6 seconds | ~4 min | ~12 min |
| 8 seconds | ~5 min | ~16 min |

Iterate at 864x480 single stage. Only spend the two-stage time on something you
will actually show someone.

---

## Multi-clip work

Ask for a reel, a set of samples, or several shots and it switches to the `ltx-reel`
workflow: it plans the shots, shows you the plan **before** spending render time,
generates as a batch, QCs the set, and can assemble and hand off to publishing.

> Make me a four shot reel about deep sea exploration, around 5 seconds each,
> something I can show the team.

---

## Publishing

Once you have a master, say *"publish this to YouTube"* and the `youtube-publish`
skill takes over: title, thumbnail, description, chapters, tags. If you also have a
script, `youtube-episode` does the whole release including Shorts cutdowns.

Generated clips have no dialogue and the audio jumps at every cut, so a reel
usually wants music or voiceover added first. Ask for `episode-edit` if so.

---

## Where to let it be creative, and where to be specific

**Let it write the prompt.** Give it the idea in one line. Turning that into 150
words across shot, scene, chronological action, subject, camera and audio is where
most of the quality comes from, and it has the model's documented preferences
built in.

**Let it plan the shots** for a reel. Varying shot size across a set is the
difference between a reel and five copies of one clip.

**Let it push back.** If you ask for something the model is bad at, it should tell
you before spending 40 minutes. Fast fight choreography, several characters
interacting, hands doing detailed work, readable text on screen. It will offer the
version of your idea that works.

**Be specific about** duration, resolution, which images are references and where
they belong, and anything that has to appear exactly. Those are decisions it cannot
make for you.

---

## When something looks wrong

Just describe it. *"there's a glitch about 2 seconds in"* is enough; it has a
diagnostic path for the known failure modes.

The three that are silent, meaning no error and an exit code of zero:

| Symptom | Cause | Fix |
|---|---|---|
| Completely black video | attention returns NaN at some seeds | change the seed; handled automatically |
| Silent audio, picture fine | same, audio branch only | change the seed |
| A glitch at regular intervals | tiled decode chunking in time | already fixed in the generator |

**Everything gets slow.** Usually swap. One clip once took 74 minutes instead of 8
for this reason, and it degrades gradually so it reads as the model being slow.

```bash
sysctl -n vm.swapusage      # sticky, a high number alone is not proof
vm_stat | head -4           # free pages is the real signal
```

Restart ComfyUI only if ComfyUI itself has grown. macOS swap `used` never shrinks,
so it often reads alarming when nothing is wrong.

**At 1280x704 or 768x960 and above, restart before every render.** One clip at that
size can exhaust the machine by itself: a render begun with 4.9 GB free hit zero
before it finished, and ran about 40% slower than it should have. At 864x480 and
below you can do several back to back without restarting.

---

## Maintenance, the one thing that will bite you

After any ComfyUI update, re-apply the patch:

```bash
cd ~/Documents/Applications/ComfyUI && git apply mps-int8-emulate.patch
```

`git pull` removes it. Without it the model silently runs on the CPU at roughly a
tenth of the speed. Nothing warns you.

Launch with `start.sh`, which carries the flag that prevents black renders. If a
server is already running, what matters is that it has
`--use-pytorch-cross-attention`, not how it was started.

---

## Running it yourself, no session needed

```bash
cd ~/Documents/Applications/ComfyUI

# one clip
./venv/bin/python ltxgen.py --prompt "..." --seconds 6 --out myshot

# with keyframes
./venv/bin/python ltxgen.py --prompt "..." --ref open.png:0 --ref close.png:-1 --out shot2

# a batch
./venv/bin/python ltxgen.py --batch clips.json --stages 2

# check anything before showing it
./venv/bin/python ~/.claude/skills/ltx-video/scripts/clipcheck.py output/video/*.mp4
```

Full flag list: `~/.claude/skills/ltx-video/references/parameters.md`

---

## What is installed where

| | |
|---|---|
| `ltx-video` skill | single clips, all parameters, prompt craft, troubleshooting |
| `ltx-reel` skill | multi-clip productions, assembly, publishing handoff |
| `ltxgen.py` | the generator, in the ComfyUI folder and in the skill |
| `clipcheck.py` | QC any mp4 |
| `README-MAC-SETUP.md` | install notes and all measured benchmarks |
| `mps-int8-emulate.patch` | the performance patch, re-apply after updates |
