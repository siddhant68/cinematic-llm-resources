#!/usr/bin/env python3
"""Validate a tutorial-video style profile for hierarchy, readability, and restraint."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
REQUIRED_ROLES = {"episode_title", "section_title", "hero_claim", "memory_anchor", "step_label", "comparison_label", "screen_callout", "recap", "captions"}
ALLOWED_ISOLATION = {"mask_first", "chroma_key", "none"}


def validate(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if data.get("schema_version") not in {"1.0", "1.1"}:
        errors.append("schema_version must be '1.0' or '1.1'")

    canvas = data.get("canvas", {})
    for key in ("width", "height", "safe_margin_fraction"):
        if key not in canvas:
            errors.append(f"canvas.{key} is required")
    margin = canvas.get("safe_margin_fraction")
    if isinstance(margin, (int, float)) and not 0.03 <= margin <= 0.12:
        warnings.append("canvas.safe_margin_fraction is outside the usual 0.03-0.12 range")
    if canvas.get("end_screen_reserved") is not True:
        warnings.append("canvas.end_screen_reserved should be true for a YouTube tutorial")

    fonts = data.get("fonts", {})
    if not fonts.get("primary"):
        errors.append("fonts.primary is required")
    named = [x for x in (fonts.get("primary"), fonts.get("secondary")) if x]
    if len(named) > 2:
        errors.append("use no more than two named type families")

    colors = data.get("colors", {})
    for key in ("background", "surface", "text_on_dark", "text_on_light", "accent"):
        value = colors.get(key)
        if not value:
            errors.append(f"colors.{key} is required")
        elif not HEX.match(str(value)):
            errors.append(f"colors.{key} must be a six-digit hex color")

    typography = data.get("typography", {})
    missing = REQUIRED_ROLES - set(typography)
    for role in sorted(missing):
        errors.append(f"typography.{role} is required")
    captions = typography.get("captions", {})
    if captions.get("max_lines", 0) > 2:
        warnings.append("captions use more than two lines")
    chars = captions.get("max_chars_per_line")
    if isinstance(chars, (int, float)) and chars > 46:
        warnings.append("caption lines exceed 46 characters; verify phone readability")
    hero = typography.get("hero_claim", {})
    if hero.get("max_words", 0) > 10:
        warnings.append("hero_claim allows more than 10 words")
    anchors = typography.get("memory_anchor", {})
    if anchors.get("max_words", 0) > 8:
        warnings.append("memory_anchor allows more than 8 words")

    layouts = data.get("layouts", {})
    pip = layouts.get("host_pip", {})
    width = pip.get("width_fraction")
    if not isinstance(width, (int, float)):
        errors.append("layouts.host_pip.width_fraction is required")
    elif not 0.15 <= width <= 0.32:
        warnings.append("host PIP width is outside the usual 0.15-0.32 range")
    if pip.get("glow_strength", 0) > 0.2:
        warnings.append("host PIP glow is strong; confirm this is an approved channel style")

    cutout = layouts.get("host_cutout", {})
    if not isinstance(cutout, dict) or not cutout:
        errors.append("layouts.host_cutout is required")
    else:
        cutout_width = cutout.get("width_fraction")
        if not isinstance(cutout_width, (int, float)):
            errors.append("layouts.host_cutout.width_fraction must be numeric")
        elif not 0.20 <= cutout_width <= 0.45:
            warnings.append("host cutout width is outside the usual 0.20-0.45 range")
        if cutout.get("isolation_method") not in ALLOWED_ISOLATION:
            errors.append(f"layouts.host_cutout.isolation_method must be one of {sorted(ALLOWED_ISOLATION)}")
        if cutout.get("isolation_method") != "mask_first":
            warnings.append("host cutout is not configured for the requested mask-first workflow")
        if cutout.get("spill_suppression") is not True:
            warnings.append("host cutout does not require spill suppression")
        if cutout.get("preserve_hair_and_hands") is not True:
            warnings.append("host cutout does not explicitly preserve hair and hands")
        if cutout.get("fallback") != "framed_pip":
            warnings.append("host cutout should fall back to framed_pip when the matte fails")
        feather = cutout.get("edge_feather_px_1080")
        if isinstance(feather, (int, float)) and feather > 4:
            warnings.append("host cutout edge feather may create a visible halo")

    screen = data.get("screen_focus", {})
    if not isinstance(screen, dict):
        errors.append("screen_focus must be an object")
    else:
        if screen.get("texture_profile") != "clean_digital":
            warnings.append("screen recordings should normally use clean_digital texture")
        if screen.get("max_simultaneous_callouts", 0) > 2:
            warnings.append("more than two simultaneous screen callouts may overload the frame")

    motion = data.get("motion", {})
    families = motion.get("transition_families", [])
    if not isinstance(families, list):
        errors.append("motion.transition_families must be a list")
    elif len(families) > 4:
        warnings.append("more than four transition families will make the episode visually noisy")
    if "hard_cut" not in families:
        warnings.append("hard_cut is absent from the transition family")
    if not ({"j_cut", "l_cut"} & set(families)):
        warnings.append("neither J-cut nor L-cut is included")
    share = motion.get("decorative_transition_share_max")
    if isinstance(share, (int, float)) and share > 0.25:
        warnings.append("decorative transition share is high")

    palette = data.get("audio", {}).get("sfx_palette", [])
    if not isinstance(palette, list):
        errors.append("audio.sfx_palette must be a list")
    elif len(palette) > 4:
        warnings.append("SFX palette has more than four recurring identities")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.profile.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("error: profile root must be an object", file=sys.stderr)
        return 2
    errors, warnings = validate(data)
    valid = not errors and (not args.strict or not warnings)
    if args.json:
        print(json.dumps({"valid": valid, "errors": errors, "warnings": warnings}, indent=2))
    else:
        for item in errors:
            print(f"ERROR {item}")
        for item in warnings:
            print(f"WARN  {item}")
        print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
