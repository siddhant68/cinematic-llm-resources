#!/usr/bin/env python3
"""Build a deterministic YouTube thumbnail from a JSON layout."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


def color(value: str | None, default: str = "#00000000") -> tuple[int, int, int, int]:
    value = value or default
    value = value.lstrip("#")
    if len(value) == 6:
        value += "FF"
    if len(value) != 8:
        raise ValueError(f"Invalid color: {value}")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4, 6))


def fit_image(image: Image.Image, width: int, height: int, mode: str) -> Image.Image:
    image = image.convert("RGBA")
    if mode == "stretch":
        return image.resize((width, height), Image.Resampling.LANCZOS)
    scale = max(width / image.width, height / image.height) if mode == "cover" else min(width / image.width, height / image.height)
    new_size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    resized = image.resize(new_size, Image.Resampling.LANCZOS)
    if mode == "cover":
        left = max(0, (resized.width - width) // 2)
        top = max(0, (resized.height - height) // 2)
        return resized.crop((left, top, left + width, top + height))
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.alpha_composite(resized, ((width - resized.width) // 2, (height - resized.height) // 2))
    return canvas


def find_font(path: str | None, size: int) -> tuple[ImageFont.FreeTypeFont, str]:
    candidates = [
        path,
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size), candidate
    raise FileNotFoundError("No usable TrueType font found. Set font_path in the layout JSON.")


def draw_gradient(width: int, height: int, start: tuple[int, int, int, int], end: tuple[int, int, int, int], direction: str) -> Image.Image:
    gradient = Image.new("RGBA", (width, height))
    pixels = gradient.load()
    horizontal = direction in {"left_to_right", "right_to_left"}
    reverse = direction in {"right_to_left", "bottom_to_top"}
    total = width - 1 if horizontal else height - 1
    total = max(1, total)
    for primary in range(width if horizontal else height):
        t = primary / total
        if reverse:
            t = 1 - t
        rgba = tuple(round(start[i] * (1 - t) + end[i] * t) for i in range(4))
        if horizontal:
            for y in range(height):
                pixels[primary, y] = rgba
        else:
            for x in range(width):
                pixels[x, primary] = rgba
    return gradient


def text_block(draw: ImageDraw.ImageDraw, layer: dict[str, Any], scale: float = 1.0) -> str:
    font_size = round(int(layer.get("font_size", 180)) * scale)
    font, selected = find_font(layer.get("font_path"), max(1, font_size))
    text = str(layer.get("text", ""))
    x = round(float(layer.get("x", 0)) * scale)
    y = round(float(layer.get("y", 0)) * scale)
    max_width = round(float(layer.get("max_width", 100000)) * scale)
    spacing_factor = float(layer.get("line_spacing", 1.0))
    align = str(layer.get("align", "left"))
    stroke_width = round(int(layer.get("stroke_width", 0)) * scale)
    fill = color(layer.get("fill"), "#FFFFFFFF")
    stroke_fill = color(layer.get("stroke_fill"), "#000000FF")

    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            bbox = draw.textbbox((0, 0), candidate, font=font, stroke_width=stroke_width)
            if bbox[2] - bbox[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)

    ascent, descent = font.getmetrics()
    line_height = max(1, round((ascent + descent) * spacing_factor))
    for index, line in enumerate(lines):
        line_y = y + index * line_height
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=stroke_width)
        line_width = bbox[2] - bbox[0]
        if align == "center":
            line_x = x + (max_width - line_width) // 2
        elif align == "right":
            line_x = x + max_width - line_width
        else:
            line_x = x
        draw.text((line_x, line_y), line, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
    return selected


def load_layout(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Layout JSON root must be an object")
    return value


def save_upload(master: Image.Image, path: Path, max_bytes: int) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".png":
        master.convert("RGBA").save(path, format="PNG", optimize=True)
        if path.stat().st_size > max_bytes:
            raise ValueError("PNG upload derivative exceeds max size; use JPEG or simplify the image")
        return path.stat().st_size
    if suffix not in {".jpg", ".jpeg"}:
        raise ValueError("Upload output must be .jpg, .jpeg, or .png")
    rgb = master.convert("RGB")
    for quality in range(95, 49, -3):
        rgb.save(path, format="JPEG", quality=quality, optimize=True, progressive=True, subsampling=0)
        if path.stat().st_size <= max_bytes:
            return path.stat().st_size
    raise ValueError("Unable to compress upload derivative below max size without dropping below quality 50")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--upload", type=Path, required=True)
    parser.add_argument("--max-upload-bytes", type=int, default=2 * 1024 * 1024)
    args = parser.parse_args()

    layout = load_layout(args.layout)
    canvas_spec = layout.get("canvas", {})
    width = int(canvas_spec.get("width", 3840))
    height = int(canvas_spec.get("height", 2160))
    if width < 640 or height < 360 or abs(width / height - 16 / 9) > 0.02:
        raise ValueError("Canvas must be a 16:9 thumbnail with width at least 640")

    canvas = Image.new("RGBA", (width, height), color(canvas_spec.get("background_color"), "#111111FF"))
    background = layout.get("background")
    if isinstance(background, dict) and background.get("path"):
        bg_path = (args.layout.parent / str(background["path"])).resolve()
        bg = fit_image(Image.open(bg_path), width, height, str(background.get("fit", "cover")))
        blur = float(background.get("blur_radius", 0))
        if blur > 0:
            bg = bg.filter(ImageFilter.GaussianBlur(blur))
        brightness = float(background.get("brightness", 1.0))
        if brightness != 1.0:
            bg = ImageEnhance.Brightness(bg).enhance(brightness)
        canvas.alpha_composite(bg)

    used_fonts: set[str] = set()
    for layer in layout.get("layers", []):
        if not isinstance(layer, dict):
            continue
        layer_type = layer.get("type")
        if layer_type == "gradient":
            overlay = draw_gradient(
                width, height,
                color(layer.get("start_color"), "#00000000"),
                color(layer.get("end_color"), "#00000000"),
                str(layer.get("direction", "left_to_right")),
            )
            canvas.alpha_composite(overlay)
        elif layer_type == "rect":
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            x = int(layer.get("x", 0)); y = int(layer.get("y", 0))
            w = int(layer.get("width", 0)); h = int(layer.get("height", 0))
            radius = int(layer.get("radius", 0))
            draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=color(layer.get("fill"), "#00000080"))
            canvas.alpha_composite(overlay)
        elif layer_type == "image":
            image_path = (args.layout.parent / str(layer.get("path"))).resolve()
            source = Image.open(image_path)
            w = int(layer.get("width", source.width)); h = int(layer.get("height", source.height))
            fitted = fit_image(source, w, h, str(layer.get("fit", "contain")))
            opacity = float(layer.get("opacity", 1.0))
            if opacity < 1.0:
                alpha = fitted.getchannel("A").point(lambda p: round(p * max(0.0, min(1.0, opacity))))
                fitted.putalpha(alpha)
            canvas.alpha_composite(fitted, (int(layer.get("x", 0)), int(layer.get("y", 0))))
        elif layer_type == "text":
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            selected = text_block(ImageDraw.Draw(overlay), layer)
            used_fonts.add(selected)
            canvas.alpha_composite(overlay)
        else:
            raise ValueError(f"Unsupported layer type: {layer_type}")

    args.master.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.master, format="PNG", optimize=True)
    upload_bytes = save_upload(canvas, args.upload, args.max_upload_bytes)
    print(json.dumps({
        "master": str(args.master),
        "upload": str(args.upload),
        "upload_bytes": upload_bytes,
        "fonts": sorted(used_fonts),
        "canvas": [width, height],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
