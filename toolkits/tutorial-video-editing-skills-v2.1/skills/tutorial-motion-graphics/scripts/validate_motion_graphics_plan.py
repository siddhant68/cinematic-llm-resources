#!/usr/bin/env python3
"""Validate a tutorial motion-graphics plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROLES = {"episode_title", "section_open", "hero_claim", "memory_anchor", "step_list", "comparison_label", "screen_callout", "data_point", "lower_third", "local_recap", "final_recap", "caption"}
MOTION = {"fade_position", "mask_reveal", "line_draw", "progressive_build", "graphic_match", "static_hold"}
SPEED = {"micro", "standard", "structural"}
WORD_LIMITS = {"section_open": 7, "hero_claim": 8, "memory_anchor": 6, "comparison_label": 6, "screen_callout": 10, "lower_third": 8}


def add(items: list[dict[str, str]], path: str, message: str) -> None:
    items.append({"path": path, "message": message})


def number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate(data: dict[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if data.get("schema_version") != "1.0":
        add(errors, "schema_version", "Expected '1.0'.")
    if not str(data.get("project_id", "")).strip():
        add(errors, "project_id", "Project ID is required.")
    if not str(data.get("style_profile", "")).strip():
        add(errors, "style_profile", "Style profile path is required.")

    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        add(errors, "sections", "At least one section is required.")
        sections = []
    section_ids: set[str] = set()
    section_titles: list[str] = []
    previous_end = -1.0
    for index, section in enumerate(sections):
        path = f"sections[{index}]"
        if not isinstance(section, dict):
            add(errors, path, "Section must be an object.")
            continue
        sid = str(section.get("id", "")).strip()
        title = str(section.get("title", "")).strip()
        if not sid:
            add(errors, f"{path}.id", "ID is required.")
        elif sid in section_ids:
            add(errors, f"{path}.id", "ID must be unique.")
        section_ids.add(sid)
        if not title:
            add(errors, f"{path}.title", "Title is required.")
        else:
            section_titles.append(title)
            words = len(title.split())
            if not 2 <= words <= 7:
                add(warnings, f"{path}.title", "Section titles usually work best at 2-7 words.")
        start = section.get("start_sec")
        end = section.get("end_sec")
        if not number(start) or start < 0:
            add(errors, f"{path}.start_sec", "Expected a non-negative number.")
        if not number(end) or not number(start) or end <= start:
            add(errors, f"{path}.end_sec", "End must be after start.")
        if number(start) and start < previous_end:
            add(errors, f"{path}.start_sec", "Sections must not overlap or move backwards.")
        if number(end):
            previous_end = float(end)
        anchors = section.get("memory_anchors", [])
        if not isinstance(anchors, list) or len(anchors) > 3:
            add(errors, f"{path}.memory_anchors", "Expected a list of zero to three memory anchors.")
        elif any(not isinstance(item, str) or not item.strip() for item in anchors):
            add(errors, f"{path}.memory_anchors", "Every anchor must be a non-empty string.")

    graphics = data.get("graphics")
    if not isinstance(graphics, list):
        add(errors, "graphics", "Graphics must be a list.")
        graphics = []
    graphic_ids: set[str] = set()
    roles_used: set[str] = set()
    for index, graphic in enumerate(graphics):
        path = f"graphics[{index}]"
        if not isinstance(graphic, dict):
            add(errors, path, "Graphic must be an object.")
            continue
        gid = str(graphic.get("id", "")).strip()
        if not gid:
            add(errors, f"{path}.id", "ID is required.")
        elif gid in graphic_ids:
            add(errors, f"{path}.id", "ID must be unique.")
        graphic_ids.add(gid)
        sid = graphic.get("section_id")
        if sid not in section_ids:
            add(errors, f"{path}.section_id", "Unknown section ID.")
        for key in ("beat_id", "template_id", "copy", "information_job", "source_or_evidence", "layout_zone"):
            if not str(graphic.get(key, "")).strip():
                add(errors, f"{path}.{key}", "Non-empty value is required.")
        role = graphic.get("role")
        if role not in ROLES:
            add(errors, f"{path}.role", f"Expected one of {sorted(ROLES)}.")
        else:
            roles_used.add(role)
            limit = WORD_LIMITS.get(role)
            if limit and len(str(graphic.get("copy", "")).split()) > limit:
                add(warnings, f"{path}.copy", f"{role} exceeds the usual {limit}-word limit.")
        start = graphic.get("start_sec")
        end = graphic.get("end_sec")
        if not number(start) or start < 0:
            add(errors, f"{path}.start_sec", "Expected a non-negative number.")
        if not number(end) or not number(start) or end <= start:
            add(errors, f"{path}.end_sec", "End must be after start.")
        hold = graphic.get("minimum_readable_hold_sec")
        if not number(hold) or hold <= 0:
            add(errors, f"{path}.minimum_readable_hold_sec", "Expected a positive number.")
        elif number(start) and number(end) and hold > end - start:
            add(errors, f"{path}.minimum_readable_hold_sec", "Readable hold exceeds total graphic duration.")
        motion = graphic.get("motion")
        if not isinstance(motion, dict):
            add(errors, f"{path}.motion", "Motion object is required.")
        else:
            if motion.get("family") not in MOTION:
                add(errors, f"{path}.motion.family", f"Expected one of {sorted(MOTION)}.")
            if motion.get("speed_class") not in SPEED:
                add(errors, f"{path}.motion.speed_class", f"Expected one of {sorted(SPEED)}.")
        sfx = graphic.get("sfx")
        if isinstance(sfx, dict):
            if not str(sfx.get("cue", "")).strip() or not str(sfx.get("linked_visual_event", "")).strip():
                add(errors, f"{path}.sfx", "SFX requires a cue and linked visible event.")
        elif sfx is not None:
            add(errors, f"{path}.sfx", "SFX must be an object or null.")
        confidence = graphic.get("confidence")
        if not number(confidence) or not 0 <= confidence <= 1:
            add(errors, f"{path}.confidence", "Expected a number from 0 to 1.")
        if number(confidence) and confidence < 0.70 and graphic.get("review_required") is not True:
            add(errors, f"{path}.review_required", "Low-confidence graphics must require review.")

    recap = data.get("final_recap")
    if not isinstance(recap, dict):
        add(errors, "final_recap", "Final recap object is required.")
        recap = {}
    if recap.get("enabled") is not True:
        add(warnings, "final_recap.enabled", "The requested tutorial system expects an enabled final recap.")
    headers = recap.get("section_headers")
    if not isinstance(headers, list):
        add(errors, "final_recap.section_headers", "Expected a list.")
        headers = []
    if headers != section_titles:
        add(errors, "final_recap.section_headers", "Headers must exactly match section titles in order.")
    if not str(recap.get("conclusion", "")).strip():
        add(errors, "final_recap.conclusion", "A concise conclusion is required.")
    if recap.get("reserve_end_screen_space") is not True:
        add(warnings, "final_recap.reserve_end_screen_space", "Reserve space for the YouTube end screen.")
    start = recap.get("start_sec")
    end = recap.get("end_sec")
    if not number(start) or start < 0:
        add(errors, "final_recap.start_sec", "Expected a non-negative number.")
    if not number(end) or not number(start) or end <= start:
        add(errors, "final_recap.end_sec", "End must be after start.")

    if sections and "memory_anchor" not in roles_used:
        add(warnings, "graphics", "No memory-anchor graphic is planned.")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("error: plan root must be an object", file=sys.stderr)
        return 2
    errors, warnings = validate(data)
    valid = not errors and (not args.strict or not warnings)
    result = {"valid": valid, "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for item in errors:
            print(f"ERROR {item['path']}: {item['message']}")
        for item in warnings:
            print(f"WARN  {item['path']}: {item['message']}")
        print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
