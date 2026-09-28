#!/usr/bin/env python3
"""Download only approved, rights-verified music, SFX, or natural sound.

The manifest must contain direct HTTPS download URLs selected from the original
asset page. This helper does not scrape sites, bypass authentication, or infer
licensing from a filename or search result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_KINDS = {"music", "sfx", "natural_sound"}
ALLOWED_STATUS = {"verified", "conditional", "owned"}


def safe_target(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    resolved_root = root.resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise ValueError(f"output path escapes download root: {relative}")
    return candidate


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_https(value: Any) -> bool:
    return isinstance(value, str) and urllib.parse.urlparse(value).scheme == "https"


def validate_entry(entry: dict[str, Any], index: int) -> list[str]:
    prefix = f"assets[{index}]"
    errors: list[str] = []
    for key in (
        "asset_id",
        "kind",
        "title",
        "creator",
        "source_page_url",
        "direct_download_url",
        "license_name",
        "license_url",
        "license_checked_at",
        "local_path",
        "license_status",
    ):
        if not str(entry.get(key, "")).strip():
            errors.append(f"{prefix}.{key} is required")
    if entry.get("kind") not in ALLOWED_KINDS:
        errors.append(f"{prefix}.kind must be one of {sorted(ALLOWED_KINDS)}")
    for key in ("source_page_url", "direct_download_url", "license_url"):
        value = entry.get(key)
        if value and not is_https(value):
            errors.append(f"{prefix}.{key} must use https")
    if entry.get("commercial_use") is not True:
        errors.append(f"{prefix}.commercial_use must be true")
    if entry.get("modification_allowed") is not True:
        errors.append(f"{prefix}.modification_allowed must be true for editing/mixing")
    status = entry.get("license_status")
    if status not in ALLOWED_STATUS:
        errors.append(f"{prefix}.license_status must be verified, conditional, or owned")
    if status == "conditional" and not str(entry.get("restrictions", "")).strip():
        errors.append(f"{prefix}.restrictions is required for a conditional license")
    if entry.get("attribution_required") is True and not str(entry.get("attribution_text", "")).strip():
        errors.append(f"{prefix}.attribution_text is required")
    return errors


def download(url: str, target: Path, max_bytes: int, timeout: float) -> tuple[int, str | None]:
    request = urllib.request.Request(url, headers={"User-Agent": "TutorialAudioDownloader/1.0"})
    target.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        declared = response.headers.get("Content-Length")
        if declared:
            try:
                declared_bytes = int(declared)
            except ValueError:
                declared_bytes = None
            if declared_bytes is not None and declared_bytes > max_bytes:
                raise ValueError(f"declared file size {declared} exceeds limit {max_bytes}")
        content_type = response.headers.get("Content-Type")
        fd, temp_name = tempfile.mkstemp(prefix="audio-", dir=str(target.parent))
        count = 0
        try:
            with os.fdopen(fd, "wb") as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > max_bytes:
                        raise ValueError(f"download exceeds limit {max_bytes}")
                    handle.write(chunk)
            os.replace(temp_name, target)
        except Exception:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
            raise
    return count, content_type


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--max-mb", type=float, default=250.0)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--receipts", type=Path, default=None)
    args = parser.parse_args()

    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read manifest: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
        print("error: manifest must contain an assets list", file=sys.stderr)
        return 2

    root_value = data.get("download_root", "assets/audio_quarantine")
    root = Path(root_value)
    if not root.is_absolute():
        root = args.manifest.parent / root
    receipts_path = args.receipts or args.manifest.parent / "audio_download_receipts.json"
    receipts: list[dict[str, Any]] = []
    failures = 0
    selected = 0

    for index, raw in enumerate(data["assets"]):
        if not isinstance(raw, dict):
            print(f"ERROR assets[{index}] must be an object")
            failures += 1
            continue
        if raw.get("approved_for_download") is not True:
            continue
        selected += 1
        errors = validate_entry(raw, index)
        if errors:
            for error in errors:
                print(f"ERROR {error}")
            failures += 1
            continue
        try:
            target = safe_target(root, str(raw["local_path"]))
        except ValueError as exc:
            print(f"ERROR assets[{index}]: {exc}")
            failures += 1
            continue

        record: dict[str, Any] = {
            "asset_id": raw["asset_id"],
            "kind": raw["kind"],
            "source_page_url": raw["source_page_url"],
            "direct_download_url": raw["direct_download_url"],
            "license_name": raw["license_name"],
            "license_url": raw["license_url"],
            "license_checked_at": raw["license_checked_at"],
            "attribution_required": bool(raw.get("attribution_required", False)),
            "attribution_text": raw.get("attribution_text", ""),
            "target": str(target),
            "dry_run": args.dry_run,
        }
        if args.dry_run:
            record["status"] = "would_download"
            receipts.append(record)
            print(f"WOULD DOWNLOAD {raw['asset_id']} -> {target}")
            continue
        if target.exists() and not args.overwrite:
            record.update(
                {"status": "skipped_existing", "bytes": target.stat().st_size, "sha256": sha256(target)}
            )
            receipts.append(record)
            print(f"SKIP existing {raw['asset_id']} -> {target}")
            continue
        try:
            count, content_type = download(
                str(raw["direct_download_url"]), target, int(args.max_mb * 1024 * 1024), args.timeout
            )
            record.update(
                {
                    "status": "downloaded",
                    "bytes": count,
                    "content_type": content_type,
                    "sha256": sha256(target),
                    "downloaded_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            receipts.append(record)
            print(f"DOWNLOADED {raw['asset_id']} -> {target} ({count} bytes)")
        except (OSError, ValueError, urllib.error.URLError) as exc:
            record.update({"status": "failed", "error": str(exc)})
            receipts.append(record)
            failures += 1
            print(f"ERROR {raw['asset_id']}: {exc}", file=sys.stderr)

    receipts_path.parent.mkdir(parents=True, exist_ok=True)
    receipts_path.write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "receipts": receipts}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"Selected: {selected}; failures: {failures}; receipts: {receipts_path}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
