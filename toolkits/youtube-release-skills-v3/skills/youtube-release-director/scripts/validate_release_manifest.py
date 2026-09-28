#!/usr/bin/env python3
"""Validate a YouTube release manifest without contacting YouTube."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_PRIVACY = {"private", "unlisted", "public"}
THUMBNAIL_EXTENSIONS = {".jpg", ".jpeg", ".png"}
CAPTION_EXTENSIONS = {".srt", ".vtt", ".sbv", ".sub", ".ttml"}


def add(items: list[dict[str, str]], path: str, message: str) -> None:
    items.append({"path": path, "message": message})


def resolve(base: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    return path if path.is_absolute() else base / path


def probe_duration(path: Path) -> float | None:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode:
        return None
    try:
        return float(result.stdout.strip())
    except ValueError:
        return None


def probe_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode:
        return None
    try:
        streams = json.loads(result.stdout).get("streams", [])
        if not streams:
            return None
        return int(streams[0]["width"]), int(streams[0]["height"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def parse_rfc3339(value: str) -> datetime | None:
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def chapter_lines(chapters: list[dict[str, Any]]) -> list[str]:
    lines = []
    for chapter in chapters:
        start = int(chapter["start_sec"])
        hours, rem = divmod(start, 3600)
        minutes, seconds = divmod(rem, 60)
        stamp = f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"
        lines.append(f"{stamp} {chapter['title']}")
    return lines


def validate(data: dict[str, Any], base: Path, allow_missing: bool) -> tuple[list[dict[str, str]], list[dict[str, str]], float | None]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if data.get("schema_version") != "1.0":
        add(errors, "schema_version", "Expected schema_version '1.0'.")

    video = resolve(base, data.get("video_file"))
    duration = None
    if video is None:
        add(errors, "video_file", "A video_file path is required.")
    elif not video.exists():
        add(warnings if allow_missing else errors, "video_file", f"File not found: {video}")
    else:
        duration = probe_duration(video)
        if duration is None:
            add(warnings, "video_file", "Could not read duration with ffprobe.")

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        add(errors, "metadata", "Metadata must be an object.")
        metadata = {}
    title = metadata.get("title")
    if not isinstance(title, str) or not title.strip():
        add(errors, "metadata.title", "Title is required.")
    elif "\n" in title or len(title) > 100:
        add(errors, "metadata.title", "Title must be one line and no more than 100 characters.")
    elif len(title.strip()) < 15:
        add(warnings, "metadata.title", "Title is unusually short; verify that the promise is specific.")

    description_path = resolve(base, metadata.get("description_file"))
    description = ""
    if description_path is None:
        add(errors, "metadata.description_file", "Description file is required.")
    elif not description_path.exists():
        add(warnings if allow_missing else errors, "metadata.description_file", f"File not found: {description_path}")
    else:
        description = description_path.read_text(encoding="utf-8")
        if not description.strip():
            add(errors, "metadata.description_file", "Description file is empty.")
        if len(description) > 5000:
            add(errors, "metadata.description_file", "Description exceeds 5000 characters.")

    tags = metadata.get("tags", [])
    if not isinstance(tags, list) or any(not isinstance(tag, str) or not tag.strip() for tag in tags):
        add(errors, "metadata.tags", "Tags must be a list of non-empty strings.")
    elif sum(len(tag) for tag in tags) > 450:
        add(warnings, "metadata.tags", "Tag text is large; tags are secondary and should not be stuffed.")

    status = data.get("status")
    if not isinstance(status, dict):
        add(errors, "status", "Status must be an object.")
        status = {}
    privacy = status.get("privacy_status")
    if privacy not in ALLOWED_PRIVACY:
        add(errors, "status.privacy_status", f"Expected one of {sorted(ALLOWED_PRIVACY)}.")
    if privacy != "private":
        add(warnings, "status.privacy_status", "Private-first upload is recommended.")

    publish_at = status.get("publish_at")
    if publish_at is not None:
        if not isinstance(publish_at, str) or parse_rfc3339(publish_at) is None:
            add(errors, "status.publish_at", "Expected a timezone-aware RFC 3339 timestamp or null.")
        else:
            parsed = parse_rfc3339(publish_at)
            if parsed and parsed <= datetime.now(timezone.utc):
                add(errors, "status.publish_at", "Scheduled time must be in the future.")
            if privacy != "private":
                add(errors, "status.publish_at", "Scheduled publishing requires privacy_status 'private'.")

    for key in ("self_declared_made_for_kids", "contains_synthetic_media", "embeddable", "public_stats_viewable"):
        if not isinstance(status.get(key), bool):
            add(errors, f"status.{key}", "Expected a boolean.")

    chapters = data.get("chapters")
    if not isinstance(chapters, list) or len(chapters) < 3:
        add(errors, "chapters", "Manual chapters require at least three entries.")
        chapters = []
    previous = None
    valid_chapters: list[dict[str, Any]] = []
    for index, chapter in enumerate(chapters):
        path = f"chapters[{index}]"
        if not isinstance(chapter, dict):
            add(errors, path, "Chapter must be an object.")
            continue
        start = chapter.get("start_sec")
        title_value = chapter.get("title")
        if not isinstance(start, (int, float)) or isinstance(start, bool) or start < 0:
            add(errors, f"{path}.start_sec", "Start must be a non-negative number.")
            continue
        if not isinstance(title_value, str) or not title_value.strip():
            add(errors, f"{path}.title", "Chapter title is required.")
        if index == 0 and start != 0:
            add(errors, f"{path}.start_sec", "The first chapter must start at 0 seconds.")
        if previous is not None:
            if start <= previous:
                add(errors, f"{path}.start_sec", "Chapter starts must be strictly ascending.")
            elif start - previous < 10:
                add(errors, f"{path}.start_sec", "Each chapter must last at least 10 seconds.")
        previous = float(start)
        valid_chapters.append({"start_sec": start, "title": title_value})
    if duration is not None and valid_chapters and valid_chapters[-1]["start_sec"] >= duration:
        add(errors, "chapters", "The final chapter starts at or after the video duration.")
    if description and valid_chapters:
        for line in chapter_lines(valid_chapters):
            if line not in description:
                add(warnings, "metadata.description_file", f"Description does not contain chapter line: {line}")

    assets = data.get("assets")
    if not isinstance(assets, dict):
        add(errors, "assets", "Assets must be an object.")
        assets = {}
    primary_thumbnail = resolve(base, assets.get("primary_thumbnail"))
    if primary_thumbnail is None:
        add(errors, "assets.primary_thumbnail", "Primary thumbnail is required.")
    elif primary_thumbnail.suffix.lower() not in THUMBNAIL_EXTENSIONS:
        add(errors, "assets.primary_thumbnail", "Thumbnail must be JPEG or PNG.")
    elif not primary_thumbnail.exists():
        add(warnings if allow_missing else errors, "assets.primary_thumbnail", f"File not found: {primary_thumbnail}")
    elif primary_thumbnail.stat().st_size > 2 * 1024 * 1024:
        add(errors, "assets.primary_thumbnail", "Thumbnail is larger than 2 MB.")

    variants = assets.get("thumbnail_variants", [])
    if not isinstance(variants, list) or len(variants) > 3:
        add(errors, "assets.thumbnail_variants", "Expected a list with at most three thumbnail variants.")
        variants = []
    for index, variant in enumerate(variants):
        path = f"assets.thumbnail_variants[{index}]"
        variant_file = resolve(base, variant)
        if variant_file is None:
            add(errors, path, "Thumbnail path is required.")
        elif variant_file.suffix.lower() not in THUMBNAIL_EXTENSIONS:
            add(errors, path, "Thumbnail must be JPEG or PNG.")
        elif not variant_file.exists():
            add(warnings if allow_missing else errors, path, f"File not found: {variant_file}")
        else:
            if variant_file.stat().st_size > 2 * 1024 * 1024:
                add(errors, path, "Thumbnail is larger than 2 MB.")
            dimensions = probe_dimensions(variant_file)
            if dimensions is None:
                add(warnings, path, "Could not inspect thumbnail dimensions with ffprobe.")
            else:
                width, height = dimensions
                ratio = width / height if height else 0
                if width < 640:
                    add(warnings, path, f"Thumbnail width is {width}px; verify current YouTube minimum and display quality.")
                if abs(ratio - (16 / 9)) > 0.03:
                    add(warnings, path, f"Thumbnail is {width}x{height}, not close to 16:9.")
                if width < 1280:
                    add(warnings, path, f"Thumbnail is {width}x{height}; use a higher-resolution 16:9 source when available.")

    captions = assets.get("captions", [])
    if not isinstance(captions, list):
        add(errors, "assets.captions", "Captions must be a list.")
        captions = []
    for index, caption in enumerate(captions):
        path = f"assets.captions[{index}]"
        if not isinstance(caption, dict):
            add(errors, path, "Caption entry must be an object.")
            continue
        cap_file = resolve(base, caption.get("file"))
        if cap_file is None:
            add(errors, f"{path}.file", "Caption file is required.")
        elif cap_file.suffix.lower() not in CAPTION_EXTENSIONS:
            add(warnings, f"{path}.file", "Verify that YouTube accepts this caption format.")
        elif not cap_file.exists():
            add(warnings if allow_missing else errors, f"{path}.file", f"File not found: {cap_file}")
        elif cap_file.stat().st_size > 100 * 1024 * 1024:
            add(errors, f"{path}.file", "Caption file is larger than 100 MB.")
        if not isinstance(caption.get("language"), str) or not caption.get("language"):
            add(errors, f"{path}.language", "Caption language is required.")

    playlists = data.get("playlist_ids", [])
    if not isinstance(playlists, list) or any(not isinstance(item, str) or not item.strip() for item in playlists):
        add(errors, "playlist_ids", "Playlist IDs must be a list of non-empty strings.")

    packaging_plan = resolve(base, data.get("packaging_plan_file"))
    if packaging_plan is None:
        add(warnings, "packaging_plan_file", "Packaging plan is not declared.")
    elif not packaging_plan.exists():
        add(warnings if allow_missing else errors, "packaging_plan_file", f"File not found: {packaging_plan}")

    post_publish = data.get("post_publish", {})
    if post_publish and not isinstance(post_publish, dict):
        add(errors, "post_publish", "Post-publish configuration must be an object.")
        post_publish = {}
    if isinstance(post_publish, dict):
        comment_path = resolve(base, post_publish.get("top_level_comment_file"))
        if post_publish.get("pin_comment") is True and comment_path is None:
            add(errors, "post_publish.top_level_comment_file", "Pinned-comment plan requires a top-level comment file.")
        if comment_path is not None:
            if not comment_path.exists():
                add(warnings if allow_missing else errors, "post_publish.top_level_comment_file", f"File not found: {comment_path}")
            else:
                comment_text = comment_path.read_text(encoding="utf-8").strip()
                if not comment_text:
                    add(errors, "post_publish.top_level_comment_file", "Comment file is empty.")
                elif len(comment_text) > 2000:
                    add(warnings, "post_publish.top_level_comment_file", "Pinned comment is very long; keep the main action visible without expansion.")
        community_path = resolve(base, post_publish.get("community_post_file"))
        if post_publish.get("community_post_enabled") is True and community_path is None:
            add(errors, "post_publish.community_post_file", "Enabled community post requires a copy file.")
        if community_path is not None and not community_path.exists():
            add(warnings if allow_missing else errors, "post_publish.community_post_file", f"File not found: {community_path}")

    studio_tasks = data.get("studio_tasks", {})
    if not isinstance(studio_tasks, dict):
        add(errors, "studio_tasks", "Studio tasks must be an object.")
        studio_tasks = {}
    end_screen = studio_tasks.get("end_screen", {})
    if isinstance(end_screen, dict) and end_screen.get("enabled") is True:
        offset = end_screen.get("start_offset_from_end_sec")
        elements = end_screen.get("elements", [])
        if not isinstance(offset, (int, float)) or isinstance(offset, bool) or not 5 <= offset <= 20:
            add(errors, "studio_tasks.end_screen.start_offset_from_end_sec", "End-screen offset must be between 5 and 20 seconds.")
        if not isinstance(elements, list) or not 1 <= len(elements) <= 4:
            add(errors, "studio_tasks.end_screen.elements", "A standard 16:9 end screen should declare one to four elements.")
        if duration is not None and duration < 25:
            add(errors, "studio_tasks.end_screen", "End screens require an eligible video of at least 25 seconds.")
    elif end_screen and not isinstance(end_screen, dict):
        add(errors, "studio_tasks.end_screen", "End screen must be an object.")

    cards = studio_tasks.get("cards", [])
    if cards and not isinstance(cards, list):
        add(errors, "studio_tasks.cards", "Cards must be a list.")
    elif isinstance(cards, list) and len(cards) > 5:
        add(errors, "studio_tasks.cards", "YouTube supports at most five cards on a video.")

    ab_test = studio_tasks.get("ab_test", {})
    if isinstance(ab_test, dict) and ab_test.get("enabled") is True:
        mode = ab_test.get("mode", "title_and_thumbnail")
        if mode not in {"title_only", "thumbnail_only", "title_and_thumbnail"}:
            add(errors, "studio_tasks.ab_test.mode", "Expected title_only, thumbnail_only, or title_and_thumbnail.")
        title_variants = ab_test.get("title_variants", [])
        thumbnail_variants = ab_test.get("thumbnail_variants", [])
        if mode in {"title_only", "title_and_thumbnail"}:
            if not isinstance(title_variants, list) or not 2 <= len(title_variants) <= 3:
                add(errors, "studio_tasks.ab_test.title_variants", "Title testing requires two or three title variants.")
            elif len(set(title_variants)) != len(title_variants):
                add(warnings, "studio_tasks.ab_test.title_variants", "Title variants are duplicated or insufficiently distinct.")
        if mode in {"thumbnail_only", "title_and_thumbnail"}:
            if not isinstance(thumbnail_variants, list) or not 2 <= len(thumbnail_variants) <= 3:
                add(errors, "studio_tasks.ab_test.thumbnail_variants", "Thumbnail testing requires two or three thumbnail variants.")
        if status.get("self_declared_made_for_kids") is True:
            add(errors, "studio_tasks.ab_test", "Native A/B testing is not available for Made for Kids videos.")
        if status.get("intended_final_privacy") == "private":
            add(errors, "studio_tasks.ab_test", "Native A/B testing cannot run while the intended final state remains private.")
    elif ab_test and not isinstance(ab_test, dict):
        add(errors, "studio_tasks.ab_test", "A/B test must be an object.")

    provenance = data.get("production_provenance")
    if not isinstance(provenance, dict):
        add(errors, "production_provenance", "Production provenance object is required.")
        provenance = {}
    for key in (
        "rights_ledger",
        "visual_download_receipts",
        "audio_rights_manifest",
        "audio_download_receipts",
        "generated_assets_log",
        "thumbnail_generation_spend",
    ):
        prov_path = resolve(base, provenance.get(key))
        if prov_path is None:
            add(errors, f"production_provenance.{key}", "File path is required.")
        elif not prov_path.exists():
            add(warnings if allow_missing else errors, f"production_provenance.{key}", f"File not found: {prov_path}")

    thumb_gen = data.get("thumbnail_generation")
    if not isinstance(thumb_gen, dict):
        add(errors, "thumbnail_generation", "Thumbnail generation object is required.")
        thumb_gen = {}
    tool = thumb_gen.get("tool")
    if tool not in {"none", "higgsfield", "other"}:
        add(errors, "thumbnail_generation.tool", "Expected none, higgsfield, or other.")
    for key in ("credit_cap", "planned_spend", "actual_spend"):
        value = thumb_gen.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            add(errors, f"thumbnail_generation.{key}", "Expected a non-negative number.")
    reserve = thumb_gen.get("reserve_fraction")
    if not isinstance(reserve, (int, float)) or isinstance(reserve, bool) or not 0 <= reserve < 1:
        add(errors, "thumbnail_generation.reserve_fraction", "Expected a number from 0 to less than 1.")
    cap = thumb_gen.get("credit_cap")
    planned = thumb_gen.get("planned_spend")
    actual = thumb_gen.get("actual_spend")
    if isinstance(cap, (int, float)) and not isinstance(cap, bool) and isinstance(reserve, (int, float)) and not isinstance(reserve, bool):
        if isinstance(planned, (int, float)) and not isinstance(planned, bool) and planned > cap * (1 - reserve):
            add(errors, "thumbnail_generation.planned_spend", "Planned spend consumes the reserved contingency.")
        if isinstance(actual, (int, float)) and not isinstance(actual, bool) and actual > cap:
            add(errors, "thumbnail_generation.actual_spend", "Actual spend exceeds the thumbnail credit cap.")
    if tool == "higgsfield":
        if cap == 0:
            add(errors, "thumbnail_generation.credit_cap", "Higgsfield thumbnail generation requires a positive dedicated cap.")
        if thumb_gen.get("approval_recorded") is not True:
            add(errors, "thumbnail_generation.approval_recorded", "Approval must be recorded before paid thumbnail generation.")
    elif (planned or actual) and tool == "none":
        add(errors, "thumbnail_generation.tool", "Non-zero spend requires a generation tool.")

    gate = data.get("release_gate")
    required_gate_fields = {
        "master_reviewed",
        "metadata_reviewed",
        "packaging_reviewed",
        "rights_cleared",
        "captions_reviewed",
        "disclosures_reviewed",
        "thumbnail_reviewed_on_mobile",
        "thumbnail_variants_reviewed",
        "chapters_verified",
        "production_provenance_reviewed",
        "thumbnail_spend_reviewed",
        "pinned_comment_reviewed",
        "launch_plan_reviewed",
        "private_upload_approved",
        "publish_approved",
    }
    if not isinstance(gate, dict) or not gate:
        add(errors, "release_gate", "Release gate object is required.")
    else:
        missing_gate_fields = sorted(required_gate_fields - set(gate))
        for key in missing_gate_fields:
            add(errors, f"release_gate.{key}", "Required release-gate field is missing.")
        for key, value in gate.items():
            if not isinstance(value, bool):
                add(errors, f"release_gate.{key}", "Expected a boolean.")
        package_fields = required_gate_fields - {"private_upload_approved", "publish_approved"}
        package_pending = sorted(key for key in package_fields if gate.get(key) is not True)
        if package_pending:
            add(warnings, "release_gate", "Release package review is incomplete: " + ", ".join(package_pending))
        if gate.get("private_upload_approved") is not True:
            add(warnings, "release_gate.private_upload_approved", "Private upload has not been approved.")
        if gate.get("publish_approved") is not True:
            add(warnings, "release_gate.publish_approved", "Public/unlisted/scheduled release has not been approved.")

    if re.search(r"https?://\S+\s+https?://", description):
        add(warnings, "metadata.description_file", "Description may contain adjacent unlabelled links; review readability.")

    return errors, warnings, duration


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--allow-missing-assets", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Return failure when warnings exist.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output.")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"error: manifest not found: {args.manifest}", file=sys.stderr)
        return 2
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("error: manifest root must be an object", file=sys.stderr)
        return 2

    errors, warnings, duration = validate(data, args.manifest.parent, args.allow_missing_assets)
    result = {
        "manifest": str(args.manifest.resolve()),
        "duration_sec": duration,
        "errors": errors,
        "warnings": warnings,
        "valid": not errors and (not args.strict or not warnings),
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Manifest: {result['manifest']}")
        print(f"Errors: {len(errors)}; warnings: {len(warnings)}")
        for item in errors:
            print(f"ERROR {item['path']}: {item['message']}")
        for item in warnings:
            print(f"WARN  {item['path']}: {item['message']}")
        print("PASS" if result["valid"] else "FAIL")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
