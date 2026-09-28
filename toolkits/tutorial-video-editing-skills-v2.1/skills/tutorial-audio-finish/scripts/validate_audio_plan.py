#!/usr/bin/env python3
"""Validate a tutorial audio plan and its rights gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

KINDS = {"music", "sfx", "natural_sound"}
LICENSE = {"verified", "conditional", "unresolved", "rejected", "owned"}
DENSITY = {"none", "light", "medium", "dense"}
DIFFICULTY = {"low", "medium", "high"}
STATES = {"off", "intro", "under_dialogue_sparse", "under_dialogue_energy", "transition_lift", "broll_feature", "reveal", "recap", "outro"}


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

    dialogue = data.get("dialogue")
    if not isinstance(dialogue, dict):
        add(errors, "dialogue", "Dialogue object is required.")
        dialogue = {}
    if not str(dialogue.get("source_id", "")).strip():
        add(errors, "dialogue.source_id", "Dialogue source ID is required.")
    for key in ("target_house_lufs_min", "target_house_lufs_max", "true_peak_ceiling_dbtp"):
        if not number(dialogue.get(key)):
            add(errors, f"dialogue.{key}", "Expected a number.")
    if number(dialogue.get("target_house_lufs_min")) and number(dialogue.get("target_house_lufs_max")) and dialogue["target_house_lufs_min"] >= dialogue["target_house_lufs_max"]:
        add(errors, "dialogue", "Minimum LUFS must be lower than maximum LUFS.")

    sources = data.get("sources")
    if not isinstance(sources, list):
        add(errors, "sources", "Sources must be a list.")
        sources = []
    source_ids: set[str] = set()
    source_map: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        path = f"sources[{index}]"
        if not isinstance(source, dict):
            add(errors, path, "Source must be an object.")
            continue
        sid = str(source.get("id", "")).strip()
        if not sid:
            add(errors, f"{path}.id", "ID is required.")
        elif sid in source_ids:
            add(errors, f"{path}.id", "ID must be unique.")
        source_ids.add(sid)
        source_map[sid] = source
        if source.get("kind") not in KINDS:
            add(errors, f"{path}.kind", f"Expected one of {sorted(KINDS)}.")
        if not str(source.get("local_path", "")).strip():
            add(errors, f"{path}.local_path", "Local path is required.")
        status = source.get("license_status")
        if status not in LICENSE:
            add(errors, f"{path}.license_status", f"Expected one of {sorted(LICENSE)}.")
        if status in {"unresolved", "rejected"}:
            add(errors, f"{path}.license_status", "Unresolved or rejected audio cannot enter an approved plan.")
        if source.get("attribution_required") is True and not str(source.get("attribution_text", "")).strip():
            add(errors, f"{path}.attribution_text", "Attribution text is required.")

    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        add(errors, "sections", "At least one section is required.")
        sections = []
    section_ids: set[str] = set()
    previous_end = -1.0
    for index, section in enumerate(sections):
        path = f"sections[{index}]"
        if not isinstance(section, dict):
            add(errors, path, "Section must be an object.")
            continue
        sid = str(section.get("id", "")).strip()
        if not sid:
            add(errors, f"{path}.id", "ID is required.")
        elif sid in section_ids:
            add(errors, f"{path}.id", "ID must be unique.")
        section_ids.add(sid)
        start = section.get("start_sec")
        end = section.get("end_sec")
        if not number(start) or start < 0:
            add(errors, f"{path}.start_sec", "Expected a non-negative number.")
        if not number(end) or not number(start) or end <= start:
            add(errors, f"{path}.end_sec", "End must be after start.")
        if number(start) and start < previous_end:
            add(errors, f"{path}.start_sec", "Sections must not overlap.")
        if number(end):
            previous_end = float(end)
        energy = section.get("energy")
        if not number(energy) or not 0 <= energy <= 4:
            add(errors, f"{path}.energy", "Expected a value from 0 to 4.")
        if section.get("dialogue_density") not in DENSITY:
            add(errors, f"{path}.dialogue_density", f"Expected one of {sorted(DENSITY)}.")
        if section.get("conceptual_difficulty") not in DIFFICULTY:
            add(errors, f"{path}.conceptual_difficulty", f"Expected one of {sorted(DIFFICULTY)}.")
        if section.get("music_state") not in STATES:
            add(errors, f"{path}.music_state", f"Expected one of {sorted(STATES)}.")

    cues = data.get("music_cues")
    if not isinstance(cues, list):
        add(errors, "music_cues", "Music cues must be a list.")
        cues = []
    cue_ids: set[str] = set()
    for index, cue in enumerate(cues):
        path = f"music_cues[{index}]"
        if not isinstance(cue, dict):
            add(errors, path, "Cue must be an object.")
            continue
        cid = str(cue.get("id", "")).strip()
        if not cid:
            add(errors, f"{path}.id", "ID is required.")
        elif cid in cue_ids:
            add(errors, f"{path}.id", "ID must be unique.")
        cue_ids.add(cid)
        if cue.get("section_id") not in section_ids:
            add(errors, f"{path}.section_id", "Unknown section ID.")
        source_id = cue.get("source_id")
        if source_id not in source_map:
            add(errors, f"{path}.source_id", "Unknown source ID.")
        elif source_map[source_id].get("kind") != "music":
            add(errors, f"{path}.source_id", "Music cue must reference a music source.")
        if cue.get("state") not in STATES:
            add(errors, f"{path}.state", f"Expected one of {sorted(STATES)}.")
        if cue.get("dialogue_density") not in DENSITY:
            add(errors, f"{path}.dialogue_density", f"Expected one of {sorted(DENSITY)}.")
        start = cue.get("start_sec")
        end = cue.get("end_sec")
        if not number(start) or start < 0:
            add(errors, f"{path}.start_sec", "Expected a non-negative number.")
        if not number(end) or not number(start) or end <= start:
            add(errors, f"{path}.end_sec", "End must be after start.")
        if not str(cue.get("purpose", "")).strip():
            add(errors, f"{path}.purpose", "Purpose is required.")
        level = cue.get("relative_to_dialogue_db")
        if not number(level):
            add(errors, f"{path}.relative_to_dialogue_db", "Expected a number.")
        elif cue.get("dialogue_density") == "dense" and level > -18:
            add(warnings, f"{path}.relative_to_dialogue_db", "Music may be too prominent for dense dialogue.")
        duck = cue.get("duck_db")
        if not number(duck) or duck < 0:
            add(errors, f"{path}.duck_db", "Expected a non-negative number.")
        for key in ("entry", "exit"):
            if not str(cue.get(key, "")).strip():
                add(errors, f"{path}.{key}", "Automation instruction is required.")

    sfx = data.get("sfx_cues")
    if not isinstance(sfx, list):
        add(errors, "sfx_cues", "SFX cues must be a list.")
        sfx = []
    if len(sfx) > max(4, len(sections) * 4):
        add(warnings, "sfx_cues", "SFX count is high for the number of sections.")
    for index, cue in enumerate(sfx):
        path = f"sfx_cues[{index}]"
        if not isinstance(cue, dict):
            add(errors, path, "Cue must be an object.")
            continue
        for key in ("id", "source_id", "linked_visual_event", "purpose"):
            if not str(cue.get(key, "")).strip():
                add(errors, f"{path}.{key}", "Non-empty value is required.")
        source_id = cue.get("source_id")
        if source_id in source_map and source_map[source_id].get("kind") != "sfx":
            add(errors, f"{path}.source_id", "SFX cue must reference an SFX source.")
        elif source_id not in source_map:
            add(errors, f"{path}.source_id", "Unknown source ID.")
        if not number(cue.get("time_sec")) or cue.get("time_sec", -1) < 0:
            add(errors, f"{path}.time_sec", "Expected a non-negative number.")
        if not number(cue.get("gain_db")):
            add(errors, f"{path}.gain_db", "Expected a number.")

    if not str(data.get("rights_manifest", "")).strip():
        add(errors, "rights_manifest", "Rights manifest path is required.")
    gate = data.get("review_gate")
    if not isinstance(gate, dict):
        add(errors, "review_gate", "Review gate must be an object.")
    else:
        for key in ("plan_shown", "rights_reviewed", "lookdev_audio_reviewed"):
            if not isinstance(gate.get(key), bool):
                add(errors, f"review_gate.{key}", "Expected a boolean.")

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
