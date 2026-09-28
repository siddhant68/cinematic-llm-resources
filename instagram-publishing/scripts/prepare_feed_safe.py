#!/usr/bin/env python3
"""Keep an entire portrait Reel visible in Instagram's 4:5 feed preview.

The output stays 1080x1920 for the Reel player. Its source picture sits inside
the centre 1080x1350 area, over a dark blurred copy of the frame. Audio is
copied without changing levels or timing.

Usage:
    python3 prepare_feed_safe.py source.mp4 output.mp4
"""

import argparse
import json
import subprocess
from pathlib import Path


def video_size(file: Path) -> tuple[int, int]:
    result = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "json", str(file),
    ])
    stream = json.loads(result)["streams"][0]
    return stream["width"], stream["height"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--quality", type=int, default=18,
                        help="H.264 CRF; lower means higher quality (default: 18)")
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if source == output:
        parser.error("Source and output must be different files")
    if not source.is_file():
        parser.error(f"Source does not exist: {source}")
    width, height = video_size(source)
    if abs(width / height - 9 / 16) > 0.01:
        parser.error(f"Expected a 9:16 source; got {width}x{height}")
    if not 0 <= args.quality <= 51:
        parser.error("Quality must be between 0 and 51")
    output.parent.mkdir(parents=True, exist_ok=True)

    graph = (
        "[0:v]split=2[front][back];"
        "[back]scale=1080:1920:flags=lanczos,boxblur=40:10,"
        "eq=brightness=-0.22[blur];"
        "[front]scale=760:1350:flags=lanczos[picture];"
        "[blur][picture]overlay=(W-w)/2:(H-h)/2:shortest=1,"
        "format=yuv420p[v]"
    )
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
        "-filter_complex", graph, "-map", "[v]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "medium", "-crf", str(args.quality),
        "-c:a", "copy", "-movflags", "+faststart", str(output),
    ], check=True)
    print(output)


if __name__ == "__main__":
    main()
