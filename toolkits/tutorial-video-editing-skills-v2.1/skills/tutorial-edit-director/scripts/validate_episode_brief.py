#!/usr/bin/env python3
"""Validate the input contract for a tutorial-video editing session."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROLES = {"face_camera", "side_camera", "screen_capture", "dialogue_audio", "owned_broll", "background", "graphic", "music", "sfx", "thumbnail_reference", "other"}
RIGHTS = {"owned", "owned_or_licensed", "licensed", "public_domain", "unresolved"}
MASTER_EDITORS = {"davinci", "palmier"}
ROUGH_EDITORS = {"none", "palmier"}
HANDOFFS = {"resolve_direct", "palmier_to_resolve", "palmier_only"}


def add(items: list[dict[str, str]], path: str, message: str) -> None:
    items.append({"path": path, "message": message})


def number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def path_exists(base: Path, value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    path = Path(value)
    if not path.is_absolute():
        path = base / path
    return path.exists()


def validate(data: dict[str, Any], base: Path, allow_missing: bool) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if data.get("schema_version") not in {"1.0", "1.1"}:
        add(errors, "schema_version", "Expected '1.0' or '1.1'.")

    project = data.get("project")
    if not isinstance(project, dict):
        add(errors, "project", "Project must be an object.")
        project = {}
    for key in ("id", "working_title", "audience", "viewer_outcome"):
        if not str(project.get(key, "")).strip() or str(project.get(key, "")).strip() == "replace-me":
            add(errors, f"project.{key}", "Replace the placeholder with a real value.")
    master = project.get("master_editor")
    rough = project.get("rough_cut_editor")
    handoff = project.get("handoff_mode")
    if master not in MASTER_EDITORS:
        add(errors, "project.master_editor", f"Expected one of {sorted(MASTER_EDITORS)}.")
    if rough not in ROUGH_EDITORS:
        add(errors, "project.rough_cut_editor", f"Expected one of {sorted(ROUGH_EDITORS)}.")
    if handoff not in HANDOFFS:
        add(errors, "project.handoff_mode", f"Expected one of {sorted(HANDOFFS)}.")
    if handoff == "resolve_direct" and master != "davinci":
        add(errors, "project.handoff_mode", "resolve_direct requires davinci as master editor.")
    if handoff == "palmier_to_resolve" and not (master == "davinci" and rough == "palmier"):
        add(errors, "project.handoff_mode", "palmier_to_resolve requires Palmier rough cut and DaVinci master.")
    if handoff == "palmier_only" and master != "palmier":
        add(errors, "project.handoff_mode", "palmier_only requires Palmier as master editor.")
    for key in ("preserve_original_aroll", "never_use_intermediate_aroll_render"):
        if project.get(key) is not True:
            add(errors, f"project.{key}", "Must be true for this workflow.")
    target = project.get("target")
    if not isinstance(target, dict):
        add(errors, "project.target", "Target must be an object.")
        target = {}
    for key in ("width", "height", "fps"):
        value = target.get(key)
        if not number(value) or value <= 0:
            add(errors, f"project.target.{key}", "Expected a positive number.")

    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        add(errors, "scripts", "Scripts must be an object.")
        scripts = {}
    for key in ("full_script", "teleprompter_script"):
        value = scripts.get(key)
        if not isinstance(value, str) or not value.strip():
            add(errors, f"scripts.{key}", "Path is required.")
        elif not path_exists(base, value):
            add(warnings if allow_missing else errors, f"scripts.{key}", f"File not found relative to brief: {value}")
    transcript = scripts.get("transcript")
    if transcript and not path_exists(base, transcript):
        add(warnings if allow_missing else errors, "scripts.transcript", f"File not found relative to brief: {transcript}")

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        add(errors, "sources", "At least one source is required.")
        sources = []
    ids: set[str] = set()
    roles: set[str] = set()
    source_map: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        path = f"sources[{index}]"
        if not isinstance(source, dict):
            add(errors, path, "Source must be an object.")
            continue
        sid = str(source.get("id", "")).strip()
        if not sid:
            add(errors, f"{path}.id", "ID is required.")
        elif sid in ids:
            add(errors, f"{path}.id", "ID must be unique.")
        ids.add(sid)
        source_map[sid] = source
        role = source.get("role")
        if role not in ROLES:
            add(errors, f"{path}.role", f"Expected one of {sorted(ROLES)}.")
        else:
            roles.add(role)
        value = source.get("path")
        if not isinstance(value, str) or not value.strip():
            add(errors, f"{path}.path", "Path is required.")
        elif not path_exists(base, value):
            add(warnings if allow_missing else errors, f"{path}.path", f"File not found relative to brief: {value}")
        rights = source.get("rights_status")
        if rights not in RIGHTS:
            add(errors, f"{path}.rights_status", f"Expected one of {sorted(RIGHTS)}.")
        if not str(source.get("usage_notes", "")).strip():
            add(warnings, f"{path}.usage_notes", "Describe how this source should be used.")
        if role == "owned_broll" and not source.get("intended_beats"):
            add(warnings, f"{path}.intended_beats", "Map owned B-roll to an intended beat or section.")

    for required_role in ("face_camera", "dialogue_audio"):
        if required_role not in roles:
            add(errors, "sources", f"Missing required source role: {required_role}")

    background = data.get("background_replacement")
    if not isinstance(background, dict):
        add(errors, "background_replacement", "Background replacement must be an object.")
        background = {}
    if background.get("enabled") is True:
        if background.get("method") != "mask_first":
            add(warnings, "background_replacement.method", "This project requested mask_first because global chroma keying previously failed.")
        source_ids = background.get("source_ids", [])
        if not isinstance(source_ids, list) or not source_ids:
            add(errors, "background_replacement.source_ids", "At least one presenter source is required.")
        else:
            for sid in source_ids:
                if sid not in source_map:
                    add(errors, "background_replacement.source_ids", f"Unknown source ID: {sid}")
        replacement = background.get("replacement_source_id")
        if replacement not in source_map:
            add(errors, "background_replacement.replacement_source_id", "Unknown replacement source ID.")
        elif source_map[replacement].get("role") != "background":
            add(errors, "background_replacement.replacement_source_id", "Replacement source must have role 'background'.")
        if background.get("fallback_to_framed_pip_on_bad_matte") is not True:
            add(warnings, "background_replacement.fallback_to_framed_pip_on_bad_matte", "A clean framed PIP fallback is recommended.")

    generation = data.get("generation")
    if not isinstance(generation, dict):
        add(errors, "generation", "Generation must be an object.")
        generation = {}
    ltx = generation.get("ltx_comfyui", {})
    if not isinstance(ltx, dict):
        add(errors, "generation.ltx_comfyui", "Expected an object.")
        ltx = {}
    if ltx.get("enabled") is True:
        checkpoint = str(ltx.get("checkpoint_name", "")).strip()
        license_url = str(ltx.get("checkpoint_license_url", "")).strip()
        maximum = ltx.get("max_generations")
        if checkpoint in {"", "replace-me"}:
            add(errors, "generation.ltx_comfyui.checkpoint_name", "Record the exact checkpoint.")
        if license_url in {"", "replace-me"}:
            add(errors, "generation.ltx_comfyui.checkpoint_license_url", "Record the exact checkpoint license URL.")
        if not number(maximum) or maximum < 0:
            add(errors, "generation.ltx_comfyui.max_generations", "Expected a non-negative number.")
    higgs = generation.get("higgsfield", {})
    if not isinstance(higgs, dict):
        add(errors, "generation.higgsfield", "Expected an object.")
        higgs = {}
    for key in ("broll_credit_cap", "thumbnail_credit_cap", "max_attempts_per_asset"):
        value = higgs.get(key)
        if not number(value) or value < 0:
            add(errors, f"generation.higgsfield.{key}", "Expected a non-negative number.")
    reserve = higgs.get("reserve_fraction")
    if not number(reserve) or not 0 <= reserve < 1:
        add(errors, "generation.higgsfield.reserve_fraction", "Expected a number from 0 to less than 1.")
    if higgs.get("enabled") is True:
        if higgs.get("require_current_cost_estimate") is not True:
            add(errors, "generation.higgsfield.require_current_cost_estimate", "Must be true.")
        if higgs.get("require_approval_before_submit") is not True:
            add(errors, "generation.higgsfield.require_approval_before_submit", "Must be true.")

    audio = data.get("audio")
    if not isinstance(audio, dict):
        add(errors, "audio", "Audio must be an object.")
    elif audio.get("dialogue_priority") is not True:
        add(errors, "audio.dialogue_priority", "Dialogue priority must be true.")

    approvals = data.get("approvals")
    if not isinstance(approvals, dict) or not approvals:
        add(errors, "approvals", "Approvals object is required.")
    else:
        for key, value in approvals.items():
            if not isinstance(value, bool):
                add(errors, f"approvals.{key}", "Expected a boolean.")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path)
    parser.add_argument("--allow-missing-files", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.brief.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("error: brief root must be an object", file=sys.stderr)
        return 2
    errors, warnings = validate(data, args.brief.parent, args.allow_missing_files)
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
