#!/usr/bin/env python3
"""Validate an editor-neutral tutorial edit blueprint.

Usage:
    python validate_edit_blueprint.py edit_blueprint.json
    python validate_edit_blueprint.py edit_blueprint.json --strict --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SOURCE_KINDS = {
    "face_camera", "side_camera", "screen_capture", "dialogue_audio",
    "broll", "graphic", "music", "sfx",
}
VIEW_MODES = {
    "face", "desk", "screen", "broll", "host_over_content",
    "compare", "graphic", "hold",
}
TRANSITIONS = {
    "none", "hard_cut", "j_cut", "l_cut", "dissolve", "match_cut",
    "graphic_bridge", "motivated_push", "motivated_whip",
}
DECORATIVE = {"dissolve", "graphic_bridge", "motivated_push", "motivated_whip"}


def add(items: list[dict[str, str]], path: str, message: str) -> None:
    items.append({"path": path, "message": message})


def number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate(data: dict[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if data.get("schema_version") != "1.0":
        add(errors, "schema_version", "Expected schema_version '1.0'.")

    project = data.get("project")
    if not isinstance(project, dict):
        add(errors, "project", "Project must be an object.")
        project = {}

    for key in ("id", "editor", "fps", "width", "height", "duration_sec", "audio_spine_source_id"):
        if key not in project:
            add(errors, f"project.{key}", "Required field is missing.")

    fps = project.get("fps")
    duration = project.get("duration_sec")
    if not number(fps) or fps <= 0:
        add(errors, "project.fps", "FPS must be a positive number.")
    if not number(duration) or duration <= 0:
        add(errors, "project.duration_sec", "Duration must be a positive number.")
        duration = 0.0

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        add(errors, "sources", "At least one source is required.")
        sources = []

    source_ids: set[str] = set()
    source_kind: dict[str, str] = {}
    for i, source in enumerate(sources):
        path = f"sources[{i}]"
        if not isinstance(source, dict):
            add(errors, path, "Source must be an object.")
            continue
        sid = source.get("id")
        kind = source.get("kind")
        if not isinstance(sid, str) or not sid.strip():
            add(errors, f"{path}.id", "Source ID must be a non-empty string.")
        elif sid in source_ids:
            add(errors, f"{path}.id", f"Duplicate source ID '{sid}'.")
        else:
            source_ids.add(sid)
            source_kind[sid] = str(kind)
        if kind not in SOURCE_KINDS:
            add(errors, f"{path}.kind", f"Unsupported source kind '{kind}'.")
        if not source.get("path") and not source.get("media_id"):
            add(warnings, path, "Source has neither path nor media_id.")
        if kind == "broll" and source.get("rights_status") not in {"owned", "licensed", "public_domain", "cleared"}:
            add(warnings, f"{path}.rights_status", "B-roll rights status is not recorded as cleared.")

    spine = project.get("audio_spine_source_id")
    if spine and spine not in source_ids:
        add(errors, "project.audio_spine_source_id", f"Unknown source ID '{spine}'.")
    elif spine and source_kind.get(spine) != "dialogue_audio":
        add(warnings, "project.audio_spine_source_id", "Audio spine is not typed as dialogue_audio.")

    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        add(errors, "sections", "At least one section is required.")
        sections = []

    section_ids: set[str] = set()
    section_ranges: dict[str, tuple[float, float]] = {}
    previous_end = -1.0
    for i, section in enumerate(sections):
        path = f"sections[{i}]"
        if not isinstance(section, dict):
            add(errors, path, "Section must be an object.")
            continue
        sid = section.get("id")
        if not isinstance(sid, str) or not sid:
            add(errors, f"{path}.id", "Section ID is required.")
            continue
        if sid in section_ids:
            add(errors, f"{path}.id", f"Duplicate section ID '{sid}'.")
        section_ids.add(sid)
        start, end = section.get("start_sec"), section.get("end_sec")
        if not number(start) or not number(end) or start < 0 or end <= start:
            add(errors, path, "Section range must satisfy 0 <= start < end.")
            continue
        if start < previous_end - 0.001:
            add(errors, path, "Section overlaps or is out of order.")
        previous_end = end
        if duration and end > duration + 0.05:
            add(errors, f"{path}.end_sec", "Section extends past project duration.")
        section_ranges[sid] = (float(start), float(end))
        if not str(section.get("viewer_outcome", "")).strip():
            add(warnings, f"{path}.viewer_outcome", "Viewer outcome is empty.")

    beats = data.get("beats")
    if not isinstance(beats, list) or not beats:
        add(errors, "beats", "At least one beat is required.")
        beats = []

    beat_ids: set[str] = set()
    previous_end = -1.0
    decorated = 0
    transition_count = 0
    for i, beat in enumerate(beats):
        path = f"beats[{i}]"
        if not isinstance(beat, dict):
            add(errors, path, "Beat must be an object.")
            continue
        bid = beat.get("id")
        if not isinstance(bid, str) or not bid:
            add(errors, f"{path}.id", "Beat ID is required.")
        elif bid in beat_ids:
            add(errors, f"{path}.id", f"Duplicate beat ID '{bid}'.")
        else:
            beat_ids.add(bid)

        section_id = beat.get("section_id")
        if section_id not in section_ids:
            add(errors, f"{path}.section_id", f"Unknown section ID '{section_id}'.")

        start, end = beat.get("start_sec"), beat.get("end_sec")
        if not number(start) or not number(end) or start < 0 or end <= start:
            add(errors, path, "Beat range must satisfy 0 <= start < end.")
        else:
            if start < previous_end - 0.001:
                add(errors, path, "Beat overlaps or is out of order.")
            previous_end = end
            if duration and end > duration + 0.05:
                add(errors, f"{path}.end_sec", "Beat extends past project duration.")
            if section_id in section_ranges:
                s0, s1 = section_ranges[section_id]
                if start < s0 - 0.05 or end > s1 + 0.05:
                    add(errors, path, "Beat falls outside its section range.")

        view = beat.get("primary_view")
        if view not in VIEW_MODES:
            add(errors, f"{path}.primary_view", f"Unsupported view mode '{view}'.")

        purpose = str(beat.get("purpose", "")).strip()
        if len(purpose) < 8:
            add(errors, f"{path}.purpose", "State the communication purpose, not only the treatment.")

        visual_ids = beat.get("visual_source_ids")
        if not isinstance(visual_ids, list):
            add(errors, f"{path}.visual_source_ids", "Expected a list of source IDs.")
            visual_ids = []
        for sid in visual_ids:
            if sid not in source_ids:
                add(errors, f"{path}.visual_source_ids", f"Unknown source ID '{sid}'.")

        audio_id = beat.get("audio_source_id")
        if audio_id not in source_ids:
            add(errors, f"{path}.audio_source_id", f"Unknown source ID '{audio_id}'.")

        transition = beat.get("transition_in")
        if not isinstance(transition, dict):
            add(errors, f"{path}.transition_in", "Transition must be an object.")
        else:
            ttype = transition.get("type")
            if ttype not in TRANSITIONS:
                add(errors, f"{path}.transition_in.type", f"Unsupported transition '{ttype}'.")
            if ttype not in {"none", "hard_cut"}:
                transition_count += 1
            if ttype in DECORATIVE:
                decorated += 1
                if len(str(transition.get("reason", "")).strip()) < 8:
                    add(errors, f"{path}.transition_in.reason", "Decorative transition needs a specific reason.")

        confidence = beat.get("confidence")
        if not number(confidence) or not 0 <= confidence <= 1:
            add(errors, f"{path}.confidence", "Confidence must be between 0 and 1.")
        elif confidence < 0.70 and beat.get("review_required") is not True:
            add(errors, f"{path}.review_required", "Low-confidence beat must require review.")

        if view == "host_over_content":
            pip = beat.get("host_pip")
            if not isinstance(pip, dict):
                add(errors, f"{path}.host_pip", "host_over_content requires host_pip settings.")
            else:
                width = pip.get("width_fraction")
                if not number(width) or not 0.15 <= width <= 0.32:
                    add(warnings, f"{path}.host_pip.width_fraction", "Typical 16:9 host PIP width is 0.18-0.28; verify readability and occlusion.")
                if len(str(pip.get("reason", "")).strip()) < 8:
                    add(errors, f"{path}.host_pip.reason", "PIP needs a communication reason.")
            kinds = {source_kind.get(sid) for sid in visual_ids}
            if "face_camera" not in kinds or not ({"screen_capture", "broll", "graphic"} & kinds):
                add(errors, path, "host_over_content needs a face source plus screen, B-roll, or graphic content.")

        text = beat.get("text")
        if isinstance(text, dict):
            copy = str(text.get("copy", ""))
            role = text.get("role")
            if role == "hero_claim" and len(copy.split()) > 8:
                add(warnings, f"{path}.text.copy", "Hero claim is longer than 8 words; test at phone size.")
            if not str(text.get("reason", "")).strip():
                add(errors, f"{path}.text.reason", "On-screen text needs a reason.")

        sfx = beat.get("sfx")
        if isinstance(sfx, dict):
            if not str(sfx.get("linked_visual_event", "")).strip():
                add(errors, f"{path}.sfx.linked_visual_event", "SFX must be tied to a visible event.")
            if not str(sfx.get("reason", "")).strip():
                add(errors, f"{path}.sfx.reason", "SFX needs a reason.")

    if beats and decorated / len(beats) > 0.25:
        add(warnings, "beats", "More than one quarter of beats use decorative transitions; review for mechanical styling.")
    if beats and transition_count / len(beats) > 0.50:
        add(warnings, "beats", "More than half of beats avoid a plain cut; simplify unless the structure demands it.")

    if not data.get("style_profile"):
        add(warnings, "style_profile", "No style profile path is recorded.")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("blueprint", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output.")
    args = parser.parse_args()

    try:
        data = json.loads(args.blueprint.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: file not found: {args.blueprint}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        return 2

    if not isinstance(data, dict):
        print("error: blueprint root must be an object", file=sys.stderr)
        return 2

    errors, warnings = validate(data)
    report = {"valid": not errors and not (args.strict and warnings), "errors": errors, "warnings": warnings}

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for item in errors:
            print(f"ERROR {item['path']}: {item['message']}")
        for item in warnings:
            print(f"WARN  {item['path']}: {item['message']}")
        print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s)")

    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
