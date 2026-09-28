# Runbook — raw footage to master

Read `SKILL.md` for the reasoning. This is the sequence.

```bash
PIPE=~/Developer/video-pipeline
PY=$PIPE/.venv/bin/python
ALIGN=$PIPE/.venv-align/bin/python
export FFMPEG=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg
export FFPROBE=/opt/homebrew/opt/ffmpeg-full/bin/ffprobe

P=/path/to/project            # working dir
FOOTAGE="$P/raw.mov"
SCRIPT="$P/script/script.md"
mkdir -p "$P"/edit/{cache,renders,qc} "$P"/assets/{broll,environments}
```

---

## 1 · Measure

```bash
$PY $PIPE/preflight.py "$FOOTAGE" --json "$P/edit/preflight.json"
```

Once per shoot setup, not per video:

```bash
$PY $PIPE/skills/frame-design/scripts/analyze_framing.py "$FOOTAGE" \
    --frames 60 --json "$P/edit/framing.json" --heatmap "$P/edit/qc/occupancy.png"
$PY $PIPE/skills/greenscreen-comp/scripts/analyze_key.py "$FOOTAGE" --frames 16
```

Also check the two things that cap quality before you start:

```bash
$FFPROBE -v error -select_streams v:0 -show_entries stream=bit_rate \
         -of default=nw=1:nk=1 "$FOOTAGE"            # under ~2 Mbps at 1080p is a problem
$FFMPEG -hide_banner -i "$FOOTAGE" -af "highpass=f=8000,volumedetect" -f null - 2>&1 | grep mean
```

## 2 · Transcribe and align

```bash
$PY $PIPE/transcribe.py "$FOOTAGE" --out-dir "$P/edit/cache"
W=$(ls -t "$P/edit/cache"/words_*.json | head -1)
$ALIGN $PIPE/align_words.py --media "$FOOTAGE" --transcript "$W" \
       -o "$P/edit/cache/aligned.json" --report
```

Sanity: gaps ≥0.4s should be within a few of what `silencedetect` reports.
If it says 2 and silencedetect says 33, the alignment did not run.

## 3 · Sections from the script

```bash
$PY $PIPE/sections.py --script "$SCRIPT" \
    --transcript "$P/edit/cache/aligned.json" --fps 60 -o "$P/edit/sections.json"
```

Note any `NOT LOCATED`. Note the `[B-ROLL]` cues and their frames.

## 4 · Take selection

```bash
$PY $PIPE/skills/retake-dedup/scripts/align_retakes.py \
    --script "$SCRIPT" --transcript "$P/edit/cache/aligned.json" \
    -o "$P/edit/edl_takes.json" --report
```

Read the report. Put every REVIEW flag to the user before continuing.

---

## 5 · Build in Palmier

All of the following are MCP calls, not shell.

**Project and media**

```
manage_project  action=create  name="EP-NN Title"  fps=60  aspectRatio=16:9  quality=1080p
import_media    source={"path":"<FOOTAGE>"}                folder="A-roll"
import_media    source={"path":"<environment.png>"}        folder="Environments"
import_media    source={"path":"<assets/broll>"}           folder="B-roll"     # a directory imports recursively
```

**Place the surviving ranges.** Convert `edl_takes.json` ranges to entries —
`startFrame` is the running sum of prior durations in project frames,
`source` is `[startSeconds, endSeconds]` from the take list.

```
add_clips  entries=[{mediaRef, startFrame, source:[s,e]}, ...]
```

**Key every host clip**

```
apply_effect  clipIds=[...]  effects=[{type:"key.chroma",
              params:{keyHue:0.30, tolerance:0.34, softness:0.11, spill:0.84}}]
```

Verify at five points across the runtime with `inspect_timeline`, including the
darkest part of the screen.

**Background underneath**

```
add_clips      entries=[{mediaRef:<env>, startFrame:0, endFrame:<total>}]
manage_tracks  reorder=[{trackId:<env>, to:<below host>}]
apply_layout   layout="full" fit="fill" slots=[{slot:"main", clipIds:[<env>], anchorY:0.42}]
set_keyframes  clipId=<env> property="scale" keyframes=[[0,1,1.19],[<total>,1.07,1.27]]   # slow parallax
```

**Grade — measure, don't eyeball**

```
inspect_color  clipId=<a host clip>  reference=<env mediaRef>
```

Read the gap. Then grade the environment down so the speaker is the brightest
thing, and grade the host for life. Ignore the "raise blacks" hint on a keyed
clip — the transparent area is dragging that number.

```
apply_color  clipIds=[<env>]   exposure=-0.42 contrast=1.02 saturation=0.82 highlights=-0.15
apply_color  clipIds=[<hosts>] contrast=1.12 saturation=1.06 vibrance=0.12 exposure=0.10
             temperature=6600 highlights=-0.18 shadowsLum=0.02
             hueCurves={"targets":[{"targetHue":120,"satScale":0},
                                   {"targetHue":150,"satScale":0},
                                   {"targetHue":30,"satScale":1.02}]}
apply_effect clipIds=[<hosts>] effects=[{type:"detail.clarity",params:{clarity:0.28,dehaze:0.12}},
                                        {type:"blur.sharpen",params:{amount:0.55}},
                                        {type:"blur.noiseReduction",params:{amount:0.22}}]
```

**Cut craft**

```
get_transcript  granularity="segments"        # find stutters the selector missed
remove_words    words=[[start,end]]           # ripples — re-read before the next call
remove_silence                                # optional, if pauses remain
set_clip_properties clipIds=[<emphasis>] transform={width:1.14,height:1.14,centerY:0.535}
set_clip_properties clipIds=[<out>] fadeOutFrames=9    # only at real section boundaries
set_clip_properties clipIds=[<in>]  fadeInFrames=9
```

**B-roll** — place against the script's cues, mute its audio, shot-match it.

```
add_clips           entries=[{mediaRef, startFrame, source:[s,e]}, ...]
set_clip_properties clipIds=[<their audio ids>] volumeDb=-60
apply_effect        clipIds=[<broll>] effects=[{type:"stylize.grain",params:{amount:0.16,size:1.4}},
                                               {type:"blur.sharpen",params:{amount:0.35}}]
apply_color         clipIds=[<broll>] contrast=1.10 saturation=0.92 temperature=6800 highlights=-0.20
manage_tracks       reorder=[{trackId:<broll>, to:<below captions, above host>}]
```

**Audio clean-up**

```
denoise_audio  clipIds=[<audio ids>]  strength=0.55
```

## 6 · Captions and typography — LAST

Only after every ripple edit is done.

```
add_captions  trackIndex=<dialogue A1>  animation="highlightPop" highlightColor="#F2A65A"
              maxWords=4 maximumGapSeconds=0.5 transform={y:0.815}
              style={fontName:"Helvetica", bold:true, fontSize:72, fontCase:"uppercase",
                     tracking:2, shadow:{enabled:true, opacity:0.6, blur:22, offset:{x:0,y:5}}}
add_captions  trackIndex=<dialogue A2>  ...same...      # if dialogue spans two tracks
```

Section labels and hero lines, placed at frames from `sections.json`:

```
add_texts  entries=[{startFrame, endFrame, content:"SECTION NAME", animation:"slideUp",
                     transform:{x:0.07,y:0.155}, style:{...accent...}},
                    {startFrame, endFrame, content:"HERO WORD", animation:"popIn",
                     transform:{x:0.5,y:0.42}, style:{fontSize:200}}]
set_keyframes clipId=<host under hero> property="blur" keyframes=[[0,0],[N,0],[N+28,14]]
```

Then fix layer order — top to bottom: **headline, captions, B-roll, host, environment.**

## 7 · Verify before exporting

```
inspect_timeline  startFrame=0 endFrame=<total> maxFrames=9
```

Look at it. Check the montage, the labels, the hero beat, the section boundaries.

## 8 · Export and master

```
export_project  mode="video" codec="ProRes" resolution="1080p" outputPath=".../v1_prores.mov"
```

Then loudness — this part is ffmpeg's, Palmier has no LUFS target:

```bash
SRC="$P/edit/renders/v1_prores.mov"
CHAIN='adeclick,highpass=f=110:poles=2,equalizer=f=240:t=q:w=1.3:g=-3,equalizer=f=3200:t=q:w=1.5:g=3.5,equalizer=f=6000:t=q:w=1.8:g=2,deesser=i=0.4,acompressor=threshold=-24dB:ratio=3.2:attack=6:release=160:makeup=3,alimiter=limit=0.89:level=disabled'

M=$($FFMPEG -hide_banner -i "$SRC" -af "${CHAIN},loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | tail -14)
I=$(echo "$M"|grep input_i|grep -oE '\-?[0-9.]+');   TP=$(echo "$M"|grep input_tp|grep -oE '\-?[0-9.]+')
LRA=$(echo "$M"|grep input_lra|grep -oE '\-?[0-9.]+'); TH=$(echo "$M"|grep input_thresh|grep -oE '\-?[0-9.]+')
OFF=$(echo "$M"|grep target_offset|grep -oE '\-?[0-9.]+')

$FFMPEG -hide_banner -loglevel error -i "$SRC" \
  -af "${CHAIN},loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=${I}:measured_TP=${TP}:measured_LRA=${LRA}:measured_thresh=${TH}:offset=${OFF}:linear=true" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -profile:v high -level 4.2 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -r 60 \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$P/edit/renders/master.mp4" -y
```

Braces on `${OFF}` are not optional — in zsh, `$OFF:linear` is parsed as the
lowercase modifier `:l` and eats the flag.

## 9 · QC

```bash
$PY $PIPE/skills/qc-review/scripts/qc_review.py "$P/edit/renders/master.mp4" \
    --target-lufs -14 --json "$P/edit/qc/qc.json"
```

Exit 1 means defects. Fix the cause, re-render, re-check. Cap at three passes.
**Then watch it.**

## 10 · Hand off

```
export_project  mode="fcpxml" fcpxmlTarget="fcp" outputPath=".../episode.fcpxml"
```

Load `youtube-episode` with the master, the script, and the remaining budget.

---

## Traps, all of them found the hard way

| Symptom | Cause |
|---|---|
| Caption filters don't exist | Slim Homebrew `ffmpeg`; use `ffmpeg-full` |
| Cuts land in the wrong place | Whisper's own word timings; run `align_words.py` |
| Output runs long, captions drift | Cut points not snapped to the frame grid |
| Captions have holes | Generated before a ripple edit; regenerate |
| Whole lines uncaptioned | Dialogue split across A1/A2; caption both |
| Green in the hair | Spill, not the matte — and 1.0 over-corrects to magenta |
| Everything turns green in a filtergraph | `blend` in yuv multiplies chroma; convert to `gbrp` first |
| Master over true-peak spec | Normalised to −1.0; AAC overshoots, use −1.5 |
| Grade looks flat/faded | Under-graded; push then pull back |
| Composite reads as pasted-on | Background brighter than the subject; measure with `inspect_color` |
| B-roll blocks up | Below ~0.06 bits/pixel/frame; grain masks it, 4K downscale avoids it |
