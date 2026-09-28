#!/usr/bin/env python3
"""Validate a tutorial B-roll plan without contacting external services."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VISUAL_FORMS = {
    "owned_broll", "screen_recording", "still_image", "licensed_stock_video",
    "licensed_stock_still", "motion_graphic", "generated_video",
    "generated_still", "host_only", "host_over_content", "intentional_hold",
}
JOBS = {"evidence", "demonstration", "orientation", "emotion", "analogy", "comparison", "pacing_breath", "payoff"}
HOST = {"off", "on", "host_over_content", "framed_pip", "cutout"}
TEXTURES = {"clean_digital", "natural_proof", "subtle_filmic", "technical_system", "archival_documentary", "hypothetical_idea", "failure_warning", "generated_harmonized"}
RIGHTS = {"owned", "verified", "conditional", "unresolved", "rejected", "generated_pending", "generated_verified"}
GEN_TOOLS = {"ltx_comfyui", "higgsfield"}


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

    gate = data.get("planning_gate")
    if not isinstance(gate, dict):
        add(errors, "planning_gate", "Planning gate must be an object.")
        gate = {}
    for key in ("shown_to_user", "paid_generation_approved"):
        if not isinstance(gate.get(key), bool):
            add(errors, f"planning_gate.{key}", "Expected a boolean.")
    if gate.get("paid_generation_approved") and not gate.get("shown_to_user"):
        add(errors, "planning_gate", "Paid generation cannot be approved before the plan is shown.")

    budget = data.get("budget")
    if not isinstance(budget, dict):
        add(errors, "budget", "Budget must be an object.")
        budget = {}
    for key in ("broll_credit_cap", "thumbnail_credit_cap", "planned_broll_spend", "planned_thumbnail_spend"):
        value = budget.get(key)
        if not number(value) or value < 0:
            add(errors, f"budget.{key}", "Expected a non-negative number.")
    reserve = budget.get("reserve_fraction")
    if not number(reserve) or not 0 <= reserve < 1:
        add(errors, "budget.reserve_fraction", "Expected a number from 0 to less than 1.")
    else:
        bcap = budget.get("broll_credit_cap", 0)
        tcap = budget.get("thumbnail_credit_cap", 0)
        bspend = budget.get("planned_broll_spend", 0)
        tspend = budget.get("planned_thumbnail_spend", 0)
        if all(number(x) for x in (bcap, bspend)) and bspend > bcap * (1 - reserve):
            add(errors, "budget.planned_broll_spend", "Planned B-roll spend consumes the reserved contingency.")
        if all(number(x) for x in (tcap, tspend)) and tspend > tcap * (1 - reserve):
            add(errors, "budget.planned_thumbnail_spend", "Planned thumbnail spend consumes the reserved contingency.")

    items = data.get("items")
    if not isinstance(items, list) or not items:
        add(errors, "items", "At least one B-roll plan item is required.")
        items = []

    ids: set[str] = set()
    calculated_higgsfield = 0.0
    for index, item in enumerate(items):
        path = f"items[{index}]"
        if not isinstance(item, dict):
            add(errors, path, "Item must be an object.")
            continue
        item_id = str(item.get("id", "")).strip()
        if not item_id:
            add(errors, f"{path}.id", "ID is required.")
        elif item_id in ids:
            add(errors, f"{path}.id", "ID must be unique.")
        ids.add(item_id)
        for key in ("beat_id", "section_id", "spoken_line", "audience_question"):
            if not str(item.get(key, "")).strip():
                add(errors, f"{path}.{key}", "Non-empty value is required.")
        if item.get("information_job") not in JOBS:
            add(errors, f"{path}.information_job", f"Expected one of {sorted(JOBS)}.")
        form = item.get("visual_form")
        if form not in VISUAL_FORMS:
            add(errors, f"{path}.visual_form", f"Expected one of {sorted(VISUAL_FORMS)}.")
        if item.get("host_visibility") not in HOST:
            add(errors, f"{path}.host_visibility", f"Expected one of {sorted(HOST)}.")

        placement = item.get("placement")
        if not isinstance(placement, dict):
            add(errors, f"{path}.placement", "Placement object is required.")
        else:
            start = placement.get("start_sec")
            end = placement.get("end_sec")
            if not number(start) or start < 0:
                add(errors, f"{path}.placement.start_sec", "Expected a non-negative number.")
            if not number(end) or not number(start) or end <= start:
                add(errors, f"{path}.placement.end_sec", "End must be after start.")

        texture = item.get("texture")
        if not isinstance(texture, dict):
            add(errors, f"{path}.texture", "Texture object is required.")
        else:
            if texture.get("profile") not in TEXTURES:
                add(errors, f"{path}.texture.profile", f"Expected one of {sorted(TEXTURES)}.")
            intensity = texture.get("intensity")
            if not number(intensity) or not 0 <= intensity <= 3:
                add(errors, f"{path}.texture.intensity", "Expected a value from 0 to 3.")
            if form == "screen_recording" and number(intensity) and intensity > 0:
                add(warnings, f"{path}.texture.intensity", "Screen recordings should usually use clean texture intensity 0.")

        for bridge_key in ("entry_bridge", "exit_bridge"):
            bridge = item.get(bridge_key)
            if not isinstance(bridge, dict) or not str(bridge.get("type", "")).strip() or not str(bridge.get("reason", "")).strip():
                add(errors, f"{path}.{bridge_key}", "Bridge type and reason are required.")

        rights = item.get("rights_status")
        if rights not in RIGHTS:
            add(errors, f"{path}.rights_status", f"Expected one of {sorted(RIGHTS)}.")
        if rights in {"unresolved", "rejected"} and item.get("selected_source_id"):
            add(errors, f"{path}.selected_source_id", "An unresolved or rejected asset cannot be selected.")

        confidence = item.get("confidence")
        if not number(confidence) or not 0 <= confidence <= 1:
            add(errors, f"{path}.confidence", "Expected a number from 0 to 1.")
        if confidence is not None and number(confidence) and confidence < 0.70 and item.get("review_required") is not True:
            add(errors, f"{path}.review_required", "Low-confidence items must require review.")

        generation = item.get("generation")
        is_generated = form in {"generated_video", "generated_still"}
        if is_generated and not isinstance(generation, dict):
            add(errors, f"{path}.generation", "Generated visual requires a generation object.")
        if isinstance(generation, dict):
            tool = generation.get("tool")
            if tool not in GEN_TOOLS:
                add(errors, f"{path}.generation.tool", f"Expected one of {sorted(GEN_TOOLS)}.")
            if not str(generation.get("prompt_id", "")).strip():
                add(errors, f"{path}.generation.prompt_id", "Prompt ID is required.")
            if generation.get("illustrative_only") is not True:
                add(warnings, f"{path}.generation.illustrative_only", "Generated B-roll should normally be marked illustrative.")
            if tool == "higgsfield":
                estimate = generation.get("estimated_credits")
                if not number(estimate) or estimate < 0:
                    add(errors, f"{path}.generation.estimated_credits", "A current non-negative credit estimate is required.")
                else:
                    calculated_higgsfield += float(estimate)
                if not str(generation.get("estimate_checked_at", "")).strip():
                    add(errors, f"{path}.generation.estimate_checked_at", "Record when the estimate was checked.")
                if generation.get("approval_required") is not True:
                    add(errors, f"{path}.generation.approval_required", "Higgsfield generation must require approval.")
            if tool == "ltx_comfyui" and not str(generation.get("checkpoint_license_url", "")).strip():
                add(errors, f"{path}.generation.checkpoint_license_url", "Record the exact checkpoint license URL.")
            if not str(generation.get("fallback", "")).strip():
                add(errors, f"{path}.generation.fallback", "A non-generation fallback is required.")

    planned = budget.get("planned_broll_spend")
    if number(planned) and abs(float(planned) - calculated_higgsfield) > 0.01:
        add(errors, "budget.planned_broll_spend", f"Expected {calculated_higgsfield:g} from item estimates.")

    if items:
        generated_count = sum(1 for item in items if isinstance(item, dict) and item.get("visual_form") in {"generated_video", "generated_still"})
        if generated_count / len(items) > 0.40:
            add(warnings, "items", "More than 40% of planned visuals are generated; confirm owned evidence, screen capture, and graphics were exhausted first.")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output.")
    args = parser.parse_args()
    try:
        data = json.loads(args.plan.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: file not found: {args.plan}", file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read plan: {exc}", file=sys.stderr)
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
