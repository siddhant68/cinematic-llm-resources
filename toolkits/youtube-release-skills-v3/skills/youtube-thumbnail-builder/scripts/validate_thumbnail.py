#!/usr/bin/env python3
"""Validate a thumbnail and generate small-size review previews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageOps


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("thumbnail", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--preview-dir", type=Path, required=True)
    parser.add_argument("--max-bytes", type=int, default=2 * 1024 * 1024)
    args = parser.parse_args()

    if not args.thumbnail.is_file():
        raise SystemExit(f"Thumbnail not found: {args.thumbnail}")
    image = Image.open(args.thumbnail).convert("RGB")
    width, height = image.size
    ratio = width / height
    issues: list[str] = []
    warnings: list[str] = []
    if width < 640:
        issues.append("width is below 640 pixels")
    if abs(ratio - 16 / 9) > 0.02:
        issues.append("aspect ratio is not approximately 16:9")
    size = args.thumbnail.stat().st_size
    if size > args.max_bytes:
        issues.append(f"file exceeds {args.max_bytes} bytes")
    if width < 1280:
        warnings.append("source is below 1280 pixels wide")

    args.preview_dir.mkdir(parents=True, exist_ok=True)
    previews = []
    for target in ((640, 360), (320, 180), (160, 90)):
        preview = ImageOps.fit(image, target, method=Image.Resampling.LANCZOS)
        path = args.preview_dir / f"{args.thumbnail.stem}-{target[0]}x{target[1]}.jpg"
        preview.save(path, quality=90, optimize=True)
        previews.append(str(path))
    gray = ImageOps.grayscale(ImageOps.fit(image, (320, 180), method=Image.Resampling.LANCZOS))
    gray_path = args.preview_dir / f"{args.thumbnail.stem}-320x180-grayscale.jpg"
    gray.save(gray_path, quality=90, optimize=True)
    previews.append(str(gray_path))

    report = {
        "thumbnail": str(args.thumbnail),
        "width": width,
        "height": height,
        "aspect_ratio": ratio,
        "file_bytes": size,
        "max_bytes": args.max_bytes,
        "previews": previews,
        "issues": issues,
        "warnings": warnings,
        "valid": not issues,
        "manual_review_required": [
            "promise alignment with title and first minute",
            "readability at 160x90",
            "truthfulness of result and expression",
            "cutout and face quality",
            "asset rights and provenance",
        ],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
