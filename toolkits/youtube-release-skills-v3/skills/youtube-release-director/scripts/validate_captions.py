#!/usr/bin/env python3
"""Validate SRT or WebVTT caption timing and readability heuristics."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

TIME = re.compile(r"(?:(\d+):)?(\d{2}):(\d{2})[,.](\d{3})")


def seconds(value: str) -> float:
    match = TIME.fullmatch(value.strip())
    if not match:
        raise ValueError(f"invalid timestamp: {value}")
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2))
    sec = int(match.group(3))
    millis = int(match.group(4))
    return hours * 3600 + minutes * 60 + sec + millis / 1000


def parse(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    if text.lstrip().startswith("WEBVTT"):
        text = text.lstrip()[len("WEBVTT"):].lstrip("\n")
    blocks = re.split(r"\n\s*\n", text.strip())
    cues = []
    for block in blocks:
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        timing_index = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing_index is None:
            continue
        timing = lines[timing_index].split("-->")
        if len(timing) != 2:
            raise ValueError(f"invalid cue timing: {lines[timing_index]}")
        start_text = timing[0].strip().split()[0]
        end_text = timing[1].strip().split()[0]
        cue_text = lines[timing_index + 1:]
        cues.append({"start": seconds(start_text), "end": seconds(end_text), "lines": cue_text})
    if not cues:
        raise ValueError("no timed caption cues found")
    return cues


def validate(cues: list[dict[str, Any]], max_chars: int, max_lines: int, video_duration: float | None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    previous_end = -1.0
    for index, cue in enumerate(cues, start=1):
        start = cue["start"]
        end = cue["end"]
        lines = cue["lines"]
        if start < 0 or end <= start:
            errors.append(f"cue {index}: expected 0 <= start < end")
        if start < previous_end - 0.02:
            errors.append(f"cue {index}: overlaps the previous cue")
        previous_end = max(previous_end, end)
        duration = end - start
        if duration < 0.45:
            warnings.append(f"cue {index}: duration {duration:.2f}s is very short")
        if duration > 7.0:
            warnings.append(f"cue {index}: duration {duration:.2f}s is unusually long")
        if not lines:
            errors.append(f"cue {index}: no text")
        if len(lines) > max_lines:
            warnings.append(f"cue {index}: {len(lines)} lines exceeds target {max_lines}")
        for line_number, line in enumerate(lines, start=1):
            plain = re.sub(r"<[^>]+>", "", line)
            if len(plain) > max_chars:
                warnings.append(
                    f"cue {index} line {line_number}: {len(plain)} characters exceeds target {max_chars}"
                )
        words = len(" ".join(lines).split())
        if duration > 0 and words / duration > 4.2:
            warnings.append(f"cue {index}: reading speed is {words / duration:.1f} words per second")
        if video_duration is not None and end > video_duration + 0.1:
            errors.append(f"cue {index}: ends after video duration")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captions", type=Path)
    parser.add_argument("--max-chars-per-line", type=int, default=42)
    parser.add_argument("--max-lines", type=int, default=2)
    parser.add_argument("--video-duration", type=float)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.captions.is_file():
        print(f"error: caption file not found: {args.captions}", file=sys.stderr)
        return 2
    try:
        cues = parse(args.captions)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    errors, warnings = validate(cues, args.max_chars_per_line, args.max_lines, args.video_duration)
    valid = not errors and (not args.strict or not warnings)
    result = {"cues": len(cues), "errors": errors, "warnings": warnings, "valid": valid}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for item in errors:
            print(f"ERROR {item}")
        for item in warnings:
            print(f"WARN  {item}")
        print(f"Summary: {len(cues)} cues, {len(errors)} error(s), {len(warnings)} warning(s)")
        print("PASS" if valid else "FAIL")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
