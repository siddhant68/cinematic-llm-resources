#!/usr/bin/env python3
"""Measure stream properties, loudness, true peak, and long silences with ffmpeg.

This script analyzes only. It never rewrites the source.
"""

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
        "format=duration:stream=index,codec_type,codec_name,sample_rate,channels,channel_layout",
        "-of", "json", str(path),
    ])
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed")
    return json.loads(result.stdout)


def loudness(path: Path, ffmpeg: str) -> dict[str, Any]:
    result = run([
        ffmpeg, "-hide_banner", "-nostats", "-i", str(path),
        "-map", "0:a:0", "-af",
        "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
        "-f", "null", "-",
    ])
    if result.returncode and "Output file is empty" not in result.stderr:
        raise RuntimeError(result.stderr.strip() or "ffmpeg loudness analysis failed")
    blocks = re.findall(r"\{\s*\"input_i\".*?\}", result.stderr, flags=re.S)
    if not blocks:
        return {}
    raw = json.loads(blocks[-1])
    out: dict[str, Any] = {}
    for key, value in raw.items():
        try:
            out[key] = float(value)
        except (TypeError, ValueError):
            out[key] = value
    return out


def silences(path: Path, ffmpeg: str, threshold_db: float, min_duration: float) -> list[dict[str, float]]:
    result = run([
        ffmpeg, "-hide_banner", "-nostats", "-i", str(path),
        "-map", "0:a:0", "-af", f"silencedetect=n={threshold_db}dB:d={min_duration}",
        "-f", "null", "-",
    ])
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", result.stderr)]
    ends = [(float(a), float(b)) for a, b in re.findall(r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", result.stderr)]
    events: list[dict[str, float]] = []
    for i, start in enumerate(starts):
        if i < len(ends):
            end, duration = ends[i]
            events.append({"start_sec": start, "end_sec": end, "duration_sec": duration})
        else:
            events.append({"start_sec": start})
    return events


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg") or "ffmpeg")
    parser.add_argument("--ffprobe", default=shutil.which("ffprobe") or "ffprobe")
    parser.add_argument("--silence-threshold-db", type=float, default=-50.0)
    parser.add_argument("--silence-min-sec", type=float, default=1.2)
    parser.add_argument("--json", type=Path, dest="json_path")
    args = parser.parse_args()

    if not args.media.exists():
        print(f"error: media not found: {args.media}", file=sys.stderr)
        return 2

    try:
        info = probe(args.media, args.ffprobe)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    audio_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    report: dict[str, Any] = {
        "media": str(args.media.resolve()),
        "duration_sec": float(info.get("format", {}).get("duration", 0) or 0),
        "audio_streams": audio_streams,
        "loudness": {},
        "long_silences": [],
        "warnings": [],
    }

    if not audio_streams:
        report["warnings"].append("No audio stream found.")
    else:
        try:
            report["loudness"] = loudness(args.media, args.ffmpeg)
            report["long_silences"] = silences(
                args.media, args.ffmpeg, args.silence_threshold_db, args.silence_min_sec
            )
        except RuntimeError as exc:
            report["warnings"].append(str(exc))

    li = report["loudness"].get("input_i")
    tp = report["loudness"].get("input_tp")
    if isinstance(li, (int, float)) and (li < -18 or li > -12):
        report["warnings"].append(
            f"Integrated loudness is {li:.1f} LUFS; compare with the channel house range of about -16 to -14 LUFS."
        )
    if isinstance(tp, (int, float)) and tp > -1.0:
        report["warnings"].append(f"True peak is {tp:.1f} dBTP, above the -1 dBTP house ceiling.")

    text = json.dumps(report, indent=2)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
