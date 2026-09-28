#!/usr/bin/env python3
"""Validate a YouTube analytics snapshot and compute cautious derived indicators."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("snapshot root must be an object")
    return value


def number(value: Any, name: str, issues: list[str], allow_null: bool = False) -> float | None:
    if value is None and allow_null:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        issues.append(f"{name} must be numeric" + (" or null" if allow_null else ""))
        return None
    if value < 0:
        issues.append(f"{name} cannot be negative")
    return float(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    data = read_object(args.snapshot)
    issues: list[str] = []
    warnings: list[str] = []
    if data.get("schema_version") != "1.0":
        issues.append("schema_version must be 1.0")
    if not str(data.get("video_id", "")).strip():
        issues.append("video_id is required")
    metrics = data.get("metrics")
    if not isinstance(metrics, dict):
        issues.append("metrics must be an object")
        metrics = {}

    impressions = number(metrics.get("impressions"), "metrics.impressions", issues) or 0.0
    views = number(metrics.get("views"), "metrics.views", issues) or 0.0
    views_from_impressions = number(metrics.get("views_from_impressions"), "metrics.views_from_impressions", issues) or 0.0
    ctr = number(metrics.get("impressions_ctr"), "metrics.impressions_ctr", issues, allow_null=True)
    watch_hours = number(metrics.get("watch_time_hours"), "metrics.watch_time_hours", issues) or 0.0
    avd = number(metrics.get("average_view_duration_seconds"), "metrics.average_view_duration_seconds", issues) or 0.0

    if ctr is not None and ctr > 1:
        warnings.append("impressions_ctr is greater than 1; ensure rates are stored as fractions rather than percentages")
    calculated_ctr = views_from_impressions / impressions if impressions > 0 else None
    average_watch_seconds_from_totals = watch_hours * 3600 / views if views > 0 else None
    if ctr is not None and calculated_ctr is not None and abs(ctr - calculated_ctr) > 0.02:
        warnings.append("reported CTR differs materially from views_from_impressions / impressions; check scope and traffic-source definitions")
    if average_watch_seconds_from_totals is not None and avd > 0 and abs(average_watch_seconds_from_totals - avd) / avd > 0.25:
        warnings.append("watch-time-derived AVD differs materially from reported AVD; check metric windows and included views")
    if impressions < 100:
        warnings.append("impression sample is very small; avoid packaging conclusions")

    release_integrity = data.get("release_integrity", {})
    operational_blockers = []
    if isinstance(release_integrity, dict):
        for key in ("hd_processed", "chapters_visible", "captions_visible"):
            if release_integrity.get(key) is False:
                operational_blockers.append(key)
        restrictions = release_integrity.get("restrictions", [])
        if isinstance(restrictions, list) and restrictions:
            operational_blockers.append("restrictions")

    derived = {
        "snapshot": str(args.snapshot),
        "valid": not issues,
        "issues": issues,
        "warnings": warnings,
        "derived": {
            "calculated_ctr": calculated_ctr,
            "average_watch_seconds_from_totals": average_watch_seconds_from_totals,
            "operational_blockers": operational_blockers,
            "minimum_recommendation": "fix_release_integrity" if operational_blockers else ("hold_for_more_data" if impressions < 100 else "manual_contextual_review_required")
        },
        "interpretation_guardrails": [
            "compare CTR by traffic source and channel baseline",
            "consider impressions, watch time, and retention together",
            "do not infer causality from sequential manual swaps",
            "do not interrupt an active native A/B test without a safety reason"
        ]
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(derived, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(derived, indent=2))
    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
