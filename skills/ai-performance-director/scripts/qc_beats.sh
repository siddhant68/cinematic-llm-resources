#!/bin/bash
# Frame QC for a generated performance clip.
# usage: qc_beats.sh <video.mp4> <outdir> ["name start duration" ...]
# Prints every hard cut (scene score > 0.3), writes a 1 fps sheet, and a 4 fps strip per named beat.
set -e
V=$1; O=$2; shift 2; mkdir -p "$O"
ffprobe -v error -show_entries format=duration:stream=width,height -of compact "$V"
echo "--- cuts (scene score > 0.3):"
ffmpeg -v info -i "$V" -vf "select='gt(scene,0.3)',metadata=print" -f null - 2>&1 | grep -o "pts_time:[0-9.]*" || echo "none"
ffmpeg -v error -y -i "$V" -vf "fps=1,scale=180:-1,tile=10x3" -frames:v 1 "$O/sheet_1fps.jpg"
for spec in "$@"; do
  set -- $spec
  n=$(python3 -c "import math;print(max(1,math.ceil($3*4/2)))")
  ffmpeg -v error -y -ss "$2" -t "$3" -i "$V" -vf "fps=4,scale=160:-1,tile=${n}x2" -frames:v 1 "$O/$1.jpg"
done
echo "written to $O"
