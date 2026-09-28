#!/usr/bin/env python3
"""Run non-destructive technical QC on a rendered video with ffmpeg/ffprobe."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def probe(path: Path, ffprobe: str) -> dict[str, Any]:
    result = run([
        ffprobe, "-v", "error", "-show_entries",
        "format=duration,format_name,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json", str(path),
    ])
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed")
    return json.loads(result.stdout)


def video_events(path: Path, ffmpeg: str) -> dict[str, list[dict[str, float]]]:
    result = run([
        ffmpeg, "-hide_banner", "-nostats", "-i", str(path),
        "-map", "0:v:0", "-vf",
        "blackdetect=d=0.20:pix_th=0.02,freezedetect=n=-50dB:d=2.0",
        "-an", "-f", "null", "-",
    ])
    blacks = [
        {"start_sec": float(a), "end_sec": float(b), "duration_sec": float(c)}
        for a, b, c in re.findall(
            r"black_start:([0-9.]+) black_end:([0-9.]+) black_duration:([0-9.]+)",
            result.stderr,
        )
    ]
    starts = [float(x) for x in re.findall(r"freeze_start: ([0-9.]+)", result.stderr)]
    ends = [float(x) for x in re.findall(r"freeze_end: ([0-9.]+)", result.stderr)]
    freezes = []
    for i, start in enumerate(starts):
        item = {"start_sec": start}
        if i < len(ends):
            item["end_sec"] = ends[i]
            item["duration_sec"] = ends[i] - start
        freezes.append(item)
    return {"black_events": blacks, "freeze_events": freezes}


def audio_events(path: Path, ffmpeg: str) -> dict[str, Any]:
    result = run([
        ffmpeg, "-hide_banner", "-nostats", "-i", str(path),
        "-map", "0:a:0", "-af",
        "silencedetect=n=-50dB:d=2.0,loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
        "-vn", "-f", "null", "-",
    ])
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", result.stderr)]
    ends = [(float(a), float(b)) for a, b in re.findall(r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", result.stderr)]
    silences = []
    for i, start in enumerate(starts):
        item: dict[str, float] = {"start_sec": start}
        if i < len(ends):
            item.update({"end_sec": ends[i][0], "duration_sec": ends[i][1]})
        silences.append(item)
    blocks = re.findall(r"\{\s*\"input_i\".*?\}", result.stderr, flags=re.S)
    loud = {}
    if blocks:
        raw = json.loads(blocks[-1])
        for key, value in raw.items():
            try:
                loud[key] = float(value)
            except (TypeError, ValueError):
                loud[key] = value
    return {"silence_events": silences, "loudness": loud}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg") or "ffmpeg")
    parser.add_argument("--ffprobe", default=shutil.which("ffprobe") or "ffprobe")
    parser.add_argument("--expected-width", type=int, default=1920)
    parser.add_argument("--expected-height", type=int, default=1080)
    parser.add_argument("--json", type=Path, dest="json_path")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if not args.media.exists():
        print(f"error: media not found: {args.media}", file=sys.stderr)
        return 2

    try:
        info = probe(args.media, args.ffprobe)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    streams = info.get("streams", [])
    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    report: dict[str, Any] = {
        "media": str(args.media.resolve()),
        "probe": info,
        "black_events": [],
        "freeze_events": [],
        "silence_events": [],
        "loudness": {},
        "errors": [],
        "warnings": [],
    }

    if not video_streams:
        report["errors"].append("No video stream found.")
    else:
        v = video_streams[0]
        if (v.get("width"), v.get("height")) != (args.expected_width, args.expected_height):
            report["warnings"].append(
                f"Frame size is {v.get('width')}x{v.get('height')}, expected {args.expected_width}x{args.expected_height}."
            )
        events = video_events(args.media, args.ffmpeg)
        report.update(events)
        if events["black_events"]:
            report["warnings"].append(f"Detected {len(events['black_events'])} black event(s); inspect timecodes.")
        if events["freeze_events"]:
            report["warnings"].append(f"Detected {len(events['freeze_events'])} freeze event(s); inspect timecodes.")

    if not audio_streams:
        report["errors"].append("No audio stream found.")
    else:
        audio = audio_events(args.media, args.ffmpeg)
        report.update(audio)
        if audio["silence_events"]:
            report["warnings"].append(f"Detected {len(audio['silence_events'])} silence event(s) of at least 2 seconds.")
        li = audio["loudness"].get("input_i")
        tp = audio["loudness"].get("input_tp")
        if isinstance(li, (int, float)) and (li < -18 or li > -12):
            report["warnings"].append(f"Integrated loudness is {li:.1f} LUFS; review against the channel house target.")
        if isinstance(tp, (int, float)) and tp > -1.0:
            report["warnings"].append(f"True peak is {tp:.1f} dBTP, above the -1 dBTP house ceiling.")

    text = json.dumps(report, indent=2)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(text + "\n", encoding="utf-8")
    print(text)

    if report["errors"]:
        return 1
    if args.strict and report["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
