#!/usr/bin/env python3
"""Extract exact video frames for thumbnail review using FFmpeg."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def safe_name(value: str) -> str:
    return value.replace(":", "-").replace(".", "_")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("--timecode", action="append", required=True, help="HH:MM:SS.mmm or seconds")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--prefix", default="frame")
    args = parser.parse_args()

    if not args.video.is_file():
        raise SystemExit(f"Video not found: {args.video}")
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required but was not found on PATH")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for index, timecode in enumerate(args.timecode, start=1):
        output = args.out_dir / f"{args.prefix}-{index:02d}-{safe_name(timecode)}.png"
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", timecode, "-i", str(args.video), "-frames:v", "1",
            "-fps_mode", "passthrough", str(output),
        ]
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        if result.returncode != 0:
            raise SystemExit(f"ffmpeg failed at {timecode}: {result.stderr.strip()}")
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
