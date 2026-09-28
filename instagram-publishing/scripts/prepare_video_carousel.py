#!/usr/bin/env python3
"""Fit original vertical clips into a 4:5 video carousel and add licensed music.

Usage: python3 prepare_video_carousel.py /absolute/path/package.json
The source is shown whole in the centre; the side fill is a blurred copy.
"""
import json
import subprocess
import sys
from pathlib import Path


def probe(file):
    data = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", str(file)]))
    return float(data["format"]["duration"])


def main():
    cfg_file = Path(sys.argv[1]).resolve()
    cfg = json.loads(cfg_file.read_text())
    base = cfg_file.parent
    source = [(base / p).resolve() for p in cfg["sourceVideos"]]
    if not 2 <= len(source) <= 20:
        raise ValueError("A carousel needs 2–20 videos")
    music = (base / cfg["music"]).resolve()
    out = (base / cfg["outputDir"]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    for i, file in enumerate(source, 1):
        duration = probe(file)
        fade = min(0.35, duration / 10)
        target = out / f"slide_{i:02}.mp4"
        visual = ("[0:v]split=2[original][copy];"
                  "[copy]scale=1080:1350:force_original_aspect_ratio=increase:flags=lanczos,"
                  "crop=1080:1350,boxblur=30:10,eq=brightness=-0.25[back];"
                  "[original]scale=-2:1350:flags=lanczos[front];"
                  "[back][front]overlay=(W-w)/2:0:shortest=1,format=yuv420p[v];")
        audio = (f"[1:a]atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,"
                 f"afade=t=in:d={fade:.3f},afade=t=out:st={duration-fade:.3f}:d={fade:.3f},"
                 "loudnorm=I=-16:TP=-1.5:LRA=9[a]")
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-i", str(file),
            "-ss", str(cfg.get("musicOffsetSeconds", 0)), "-i", str(music),
            "-filter_complex", visual + audio, "-map", "[v]", "-map", "[a]",
            "-r", "30", "-t", f"{duration:.3f}", "-c:v", "libx264", "-preset", "medium",
            "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(target)], check=True)
        print(target)


if __name__ == "__main__":
    main()
