#!/usr/bin/env python3
"""Upload a validated YouTube release package through the official Data API.

The script defaults to private upload, records progress in a state file, and
supports resuming post-upload steps with an existing video ID.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import random
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]
RETRIABLE_STATUS = {429, 500, 502, 503, 504}
MAX_VIDEO_BYTES = 256 * 1024 * 1024 * 1024
MAX_THUMBNAIL_BYTES = 2 * 1024 * 1024
MAX_CAPTION_BYTES = 100 * 1024 * 1024


def load_google() -> dict[str, Any]:
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        raise RuntimeError(
            "Google API dependencies are missing. Run: python -m pip install -r assets/requirements.txt"
        ) from exc
    return {
        "Request": Request,
        "Credentials": Credentials,
        "InstalledAppFlow": InstalledAppFlow,
        "build": build,
        "HttpError": HttpError,
        "MediaFileUpload": MediaFileUpload,
    }


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def resolve(base: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    return path if path.is_absolute() else base / path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest_fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def load_state(path: Path, manifest: Path, allow_mismatch: bool) -> dict[str, Any]:
    current_fingerprint = manifest_fingerprint(manifest)
    if path.exists():
        try:
            state = read_json(path)
        except (OSError, json.JSONDecodeError, ValueError):
            state = {}
    else:
        state = {}
    previous_fingerprint = state.get("manifest_sha256")
    if (
        state.get("video_id")
        and previous_fingerprint
        and previous_fingerprint != current_fingerprint
        and not allow_mismatch
    ):
        raise ValueError(
            "state file belongs to a different manifest; use a new --state path or explicitly pass --allow-state-mismatch"
        )
    state.setdefault("schema_version", "1.0")
    state["manifest"] = str(manifest.resolve())
    state["manifest_sha256"] = current_fingerprint
    state.setdefault("completed_steps", [])
    return state


def require_file(path: Path | None, label: str, max_bytes: int | None = None) -> Path:
    if path is None:
        raise ValueError(f"{label} path is missing")
    if not path.is_file():
        raise ValueError(f"{label} file not found: {path}")
    if max_bytes is not None and path.stat().st_size > max_bytes:
        raise ValueError(f"{label} exceeds allowed local size check: {path}")
    return path


def parse_manifest(manifest_path: Path, allow_unapproved: bool, allow_nonprivate: bool, allow_schedule: bool, dry_run: bool = False) -> dict[str, Any]:
    data = read_json(manifest_path)
    if data.get("schema_version") != "1.0":
        raise ValueError("Unsupported release manifest schema_version")
    base = manifest_path.parent

    gate = data.get("release_gate")
    if not isinstance(gate, dict) or not gate:
        raise ValueError("release_gate is missing")
    upload_gate_exemptions = {"publish_approved"}
    if dry_run:
        upload_gate_exemptions.add("private_upload_approved")
    pending = [
        key for key, value in gate.items()
        if key not in upload_gate_exemptions and value is not True
    ]
    if pending and not allow_unapproved:
        raise ValueError(f"release package is not ready for upload: {', '.join(pending)}")
    if not dry_run and gate.get("private_upload_approved") is not True and not allow_unapproved:
        raise ValueError("private upload is not approved: private_upload_approved")

    metadata = data.get("metadata")
    status = data.get("status")
    upload = data.get("upload", {})
    assets = data.get("assets", {})
    if not isinstance(metadata, dict) or not isinstance(status, dict) or not isinstance(assets, dict):
        raise ValueError("metadata, status, and assets must be objects")

    title = str(metadata.get("title", "")).strip()
    if not title or len(title) > 100 or "\n" in title:
        raise ValueError("title is missing, multiline, or longer than 100 characters")
    description_path = require_file(resolve(base, metadata.get("description_file")), "description")
    description = description_path.read_text(encoding="utf-8")
    if not description.strip() or len(description) > 5000:
        raise ValueError("description is empty or longer than 5000 characters")

    privacy = status.get("privacy_status")
    if privacy not in {"private", "unlisted", "public"}:
        raise ValueError("privacy_status must be private, unlisted, or public")
    if privacy != "private" and not allow_nonprivate:
        raise ValueError("non-private upload requires --allow-nonprivate")
    publish_at = status.get("publish_at")
    if publish_at and not allow_schedule:
        raise ValueError("scheduled publication requires --allow-schedule")
    if publish_at and privacy != "private":
        raise ValueError("publish_at requires privacy_status private")
    if (privacy != "private" or publish_at) and gate.get("publish_approved") is not True and not allow_unapproved:
        raise ValueError("public, unlisted, or scheduled release is not approved: publish_approved")

    video = require_file(resolve(base, data.get("video_file")), "video", MAX_VIDEO_BYTES)
    thumbnail = require_file(resolve(base, assets.get("primary_thumbnail")), "thumbnail", MAX_THUMBNAIL_BYTES)
    if thumbnail.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        raise ValueError("primary thumbnail must be JPEG or PNG")

    captions = []
    for index, item in enumerate(assets.get("captions", [])):
        if not isinstance(item, dict):
            raise ValueError(f"caption entry {index} is not an object")
        caption_file = require_file(resolve(base, item.get("file")), f"caption {index}", MAX_CAPTION_BYTES)
        language = str(item.get("language", "")).strip()
        name = str(item.get("name", "")).strip()
        if not language or not name:
            raise ValueError(f"caption entry {index} requires language and name")
        captions.append({**item, "resolved_file": caption_file})

    comment_file = None
    post_publish = data.get("post_publish", {})
    if isinstance(post_publish, dict) and post_publish.get("top_level_comment_file"):
        comment_file = require_file(resolve(base, post_publish.get("top_level_comment_file")), "comment")

    return {
        "raw": data,
        "base": base,
        "video": video,
        "thumbnail": thumbnail,
        "captions": captions,
        "comment_file": comment_file,
        "title": title,
        "description": description,
        "metadata": metadata,
        "status": status,
        "notify_subscribers": bool(upload.get("notify_subscribers", False)) if isinstance(upload, dict) else False,
        "playlist_ids": data.get("playlist_ids", []),
        "post_publish": post_publish if isinstance(post_publish, dict) else {},
    }


def dry_run_summary(parsed: dict[str, Any], skip_assets: bool, post_comment: bool) -> dict[str, Any]:
    status = parsed["status"]
    return {
        "video": str(parsed["video"]),
        "video_bytes": parsed["video"].stat().st_size,
        "video_sha256": file_sha256(parsed["video"]),
        "title": parsed["title"],
        "description_characters": len(parsed["description"]),
        "privacy_status": status.get("privacy_status"),
        "publish_at": status.get("publish_at"),
        "made_for_kids": status.get("self_declared_made_for_kids"),
        "contains_synthetic_media": status.get("contains_synthetic_media"),
        "notify_subscribers": parsed["notify_subscribers"],
        "primary_thumbnail": None if skip_assets else str(parsed["thumbnail"]),
        "captions": [] if skip_assets else [str(item["resolved_file"]) for item in parsed["captions"]],
        "playlist_ids": [] if skip_assets else parsed["playlist_ids"],
        "post_comment": bool(post_comment and not skip_assets and parsed["comment_file"]),
        "studio_only_not_performed": [
            "copyright and restrictions review",
            "monetization and ad suitability",
            "end screen",
            "cards",
            "comment pinning",
            "title and thumbnail A/B test",
        ],
    }


def credentials(google: dict[str, Any], client_secrets: Path, token: Path) -> Any:
    Credentials = google["Credentials"]
    creds = None
    if token.exists():
        creds = Credentials.from_authorized_user_file(str(token), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(google["Request"]())
    if not creds or not creds.valid:
        flow = google["InstalledAppFlow"].from_client_secrets_file(str(client_secrets), SCOPES)
        creds = flow.run_local_server(port=0, prompt="consent")
    token.parent.mkdir(parents=True, exist_ok=True)
    token.write_text(creds.to_json() + "\n", encoding="utf-8")
    try:
        os.chmod(token, 0o600)
    except OSError:
        pass
    return creds


def status_code(exc: Exception) -> int | None:
    response = getattr(exc, "resp", None)
    return getattr(response, "status", None)


def retry_delay(attempt: int) -> float:
    return min(64.0, (2.0 ** attempt) + random.random())


def execute_with_retry(factory: Callable[[], Any], http_error: type[Exception], label: str, attempts: int = 7) -> Any:
    for attempt in range(attempts):
        try:
            return factory().execute()
        except http_error as exc:
            code = status_code(exc)
            if code not in RETRIABLE_STATUS or attempt + 1 >= attempts:
                raise
            delay = retry_delay(attempt)
            print(f"WARN: {label} returned HTTP {code}; retrying after {delay:.1f}s", file=sys.stderr)
            time.sleep(delay)
        except (OSError, socket.timeout) as exc:
            if attempt + 1 >= attempts:
                raise
            delay = retry_delay(attempt)
            print(f"WARN: {label} network error {exc}; retrying after {delay:.1f}s", file=sys.stderr)
            time.sleep(delay)
    raise RuntimeError(f"{label} failed after retries")


def resumable_upload(request: Any, http_error: type[Exception], attempts: int = 10) -> dict[str, Any]:
    retry_count = 0
    while True:
        try:
            progress, response = request.next_chunk()
            if progress:
                print(f"Upload progress: {progress.progress() * 100:.1f}%")
            if response is not None:
                if not isinstance(response, dict) or not response.get("id"):
                    raise RuntimeError(f"Unexpected upload response: {response!r}")
                return response
            retry_count = 0
        except http_error as exc:
            code = status_code(exc)
            if code not in RETRIABLE_STATUS or retry_count >= attempts:
                raise
            delay = retry_delay(retry_count)
            retry_count += 1
            print(f"WARN: upload returned HTTP {code}; retrying after {delay:.1f}s", file=sys.stderr)
            time.sleep(delay)
        except (OSError, socket.timeout) as exc:
            if retry_count >= attempts:
                raise
            delay = retry_delay(retry_count)
            retry_count += 1
            print(f"WARN: upload network error {exc}; retrying after {delay:.1f}s", file=sys.stderr)
            time.sleep(delay)


def add_completed(state: dict[str, Any], step: str) -> None:
    completed = state.setdefault("completed_steps", [])
    if step not in completed:
        completed.append(step)


def upload_video(youtube: Any, google: dict[str, Any], parsed: dict[str, Any]) -> dict[str, Any]:
    metadata = parsed["metadata"]
    status = parsed["status"]
    snippet: dict[str, Any] = {
        "title": parsed["title"],
        "description": parsed["description"],
        "categoryId": str(metadata.get("category_id", "22")),
    }
    tags = metadata.get("tags", [])
    if tags:
        snippet["tags"] = tags
    if metadata.get("default_language"):
        snippet["defaultLanguage"] = metadata["default_language"]

    api_status: dict[str, Any] = {
        "privacyStatus": status["privacy_status"],
        "selfDeclaredMadeForKids": status["self_declared_made_for_kids"],
        "containsSyntheticMedia": status["contains_synthetic_media"],
        "embeddable": status["embeddable"],
        "publicStatsViewable": status["public_stats_viewable"],
    }
    if status.get("publish_at"):
        api_status["publishAt"] = status["publish_at"]

    media = google["MediaFileUpload"](
        str(parsed["video"]),
        mimetype=mimetypes.guess_type(parsed["video"].name)[0] or "application/octet-stream",
        chunksize=8 * 1024 * 1024,
        resumable=True,
    )
    request = youtube.videos().insert(
        part="snippet,status",
        body={"snippet": snippet, "status": api_status},
        media_body=media,
        notifySubscribers=parsed["notify_subscribers"],
    )
    return resumable_upload(request, google["HttpError"])


def upload_thumbnail(youtube: Any, google: dict[str, Any], video_id: str, path: Path) -> Any:
    media = google["MediaFileUpload"](
        str(path),
        mimetype=mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        resumable=False,
    )
    return execute_with_retry(
        lambda: youtube.thumbnails().set(videoId=video_id, media_body=media),
        google["HttpError"],
        "thumbnail upload",
    )


def upload_caption(youtube: Any, google: dict[str, Any], video_id: str, caption: dict[str, Any]) -> Any:
    path = caption["resolved_file"]
    media = google["MediaFileUpload"](
        str(path),
        mimetype=mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        resumable=False,
    )
    body = {
        "snippet": {
            "videoId": video_id,
            "language": caption["language"],
            "name": caption["name"],
            "isDraft": bool(caption.get("is_draft", False)),
        }
    }
    return execute_with_retry(
        lambda: youtube.captions().insert(part="snippet", body=body, media_body=media),
        google["HttpError"],
        f"caption upload {path.name}",
    )


def add_playlist(youtube: Any, google: dict[str, Any], video_id: str, playlist_id: str) -> Any:
    body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {"kind": "youtube#video", "videoId": video_id},
        }
    }
    return execute_with_retry(
        lambda: youtube.playlistItems().insert(part="snippet", body=body),
        google["HttpError"],
        f"playlist insert {playlist_id}",
    )


def post_top_level_comment(youtube: Any, google: dict[str, Any], video_id: str, text: str) -> Any:
    body = {
        "snippet": {
            "videoId": video_id,
            "topLevelComment": {"snippet": {"textOriginal": text}},
        }
    }
    return execute_with_retry(
        lambda: youtube.commentThreads().insert(part="snippet", body=body),
        google["HttpError"],
        "top-level comment",
    )


def readback(youtube: Any, google: dict[str, Any], video_id: str) -> dict[str, Any]:
    response = execute_with_retry(
        lambda: youtube.videos().list(part="snippet,status,contentDetails,processingDetails", id=video_id),
        google["HttpError"],
        "video readback",
    )
    items = response.get("items", []) if isinstance(response, dict) else []
    if not items:
        raise RuntimeError(f"Readback did not return video {video_id}")
    return items[0]


def verify_readback(item: dict[str, Any], parsed: dict[str, Any], video_id: str) -> dict[str, Any]:
    mismatches: list[str] = []
    if item.get("id") != video_id:
        mismatches.append(f"video ID is {item.get('id')!r}, expected {video_id!r}")
    snippet = item.get("snippet", {})
    status = item.get("status", {})
    if snippet.get("title") != parsed["title"]:
        mismatches.append("title differs from the manifest")
    if snippet.get("description") != parsed["description"]:
        mismatches.append("description differs from the manifest")
    expected_privacy = parsed["status"].get("privacy_status")
    if status.get("privacyStatus") != expected_privacy:
        mismatches.append(
            f"privacy is {status.get('privacyStatus')!r}, expected {expected_privacy!r}"
        )
    expected_made_for_kids = parsed["status"].get("self_declared_made_for_kids")
    returned_made_for_kids = status.get("selfDeclaredMadeForKids")
    if returned_made_for_kids is not None and returned_made_for_kids != expected_made_for_kids:
        mismatches.append("made-for-kids declaration differs from the manifest")
    expected_synthetic = parsed["status"].get("contains_synthetic_media")
    returned_synthetic = status.get("containsSyntheticMedia")
    if returned_synthetic is not None and returned_synthetic != expected_synthetic:
        mismatches.append("synthetic-media disclosure differs from the manifest")
    return {
        "verified": not mismatches,
        "mismatches": mismatches,
        "title": snippet.get("title"),
        "privacy_status": status.get("privacyStatus"),
        "processing_status": item.get("processingDetails", {}).get("processingStatus"),
    }


def poll_processing(youtube: Any, google: dict[str, Any], video_id: str, interval: int, attempts: int) -> dict[str, Any]:
    last = {}
    for index in range(attempts):
        last = readback(youtube, google, video_id)
        status = last.get("processingDetails", {}).get("processingStatus")
        print(f"Processing status: {status or 'unknown'}")
        if status in {"succeeded", "failed", "terminated"}:
            return last
        if index + 1 < attempts:
            time.sleep(interval)
    return last


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--client-secrets", type=Path, required=False)
    parser.add_argument("--token", type=Path, default=Path("youtube_token.json"))
    parser.add_argument("--state", type=Path, default=Path("upload_state.json"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-unapproved", action="store_true")
    parser.add_argument("--allow-nonprivate", action="store_true")
    parser.add_argument("--allow-schedule", action="store_true")
    parser.add_argument("--post-comment", action="store_true")
    parser.add_argument("--skip-assets", action="store_true")
    parser.add_argument("--resume-video-id")
    parser.add_argument("--allow-state-mismatch", action="store_true")
    parser.add_argument("--poll-processing", action="store_true")
    parser.add_argument("--poll-interval", type=int, default=20)
    parser.add_argument("--poll-attempts", type=int, default=15)
    args = parser.parse_args()

    if not args.manifest.is_file():
        print(f"error: manifest not found: {args.manifest}", file=sys.stderr)
        return 2
    try:
        parsed = parse_manifest(
            args.manifest,
            args.allow_unapproved,
            args.allow_nonprivate,
            args.allow_schedule,
            args.dry_run,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    summary = dry_run_summary(parsed, args.skip_assets, args.post_comment)
    if args.dry_run:
        print(json.dumps(summary, indent=2))
        return 0

    if args.client_secrets is None or not args.client_secrets.is_file():
        print("error: --client-secrets must point to an OAuth Desktop client JSON file", file=sys.stderr)
        return 2

    try:
        state = load_state(args.state, args.manifest, args.allow_state_mismatch)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.resume_video_id:
        state["video_id"] = args.resume_video_id
        state["resumed_at"] = now_utc()
        write_state(args.state, state)
    video_id = state.get("video_id")

    try:
        google = load_google()
        creds = credentials(google, args.client_secrets, args.token)
        youtube = google["build"]("youtube", "v3", credentials=creds, cache_discovery=False)

        if not video_id:
            response = upload_video(youtube, google, parsed)
            video_id = response["id"]
            state["video_id"] = video_id
            state["uploaded_at"] = now_utc()
            state["upload_response"] = response
            add_completed(state, "video_upload")
            write_state(args.state, state)
            print(f"Uploaded video ID: {video_id}")
        else:
            print(f"Using existing video ID: {video_id}")

        if not args.skip_assets:
            if "thumbnail" not in state["completed_steps"]:
                state["thumbnail_response"] = upload_thumbnail(youtube, google, video_id, parsed["thumbnail"])
                add_completed(state, "thumbnail")
                write_state(args.state, state)

            for index, caption in enumerate(parsed["captions"]):
                step = f"caption:{index}:{caption['language']}"
                if step not in state["completed_steps"]:
                    response = upload_caption(youtube, google, video_id, caption)
                    state.setdefault("caption_responses", []).append(response)
                    add_completed(state, step)
                    write_state(args.state, state)

            for playlist_id in parsed["playlist_ids"]:
                step = f"playlist:{playlist_id}"
                if step not in state["completed_steps"]:
                    response = add_playlist(youtube, google, video_id, playlist_id)
                    state.setdefault("playlist_responses", []).append(response)
                    add_completed(state, step)
                    write_state(args.state, state)

            should_comment = bool(parsed["post_publish"].get("post_comment_via_api", False))
            if args.post_comment and should_comment and parsed["comment_file"] and "top_level_comment" not in state["completed_steps"]:
                text = parsed["comment_file"].read_text(encoding="utf-8").strip()
                if not text:
                    raise ValueError("top-level comment file is empty")
                state["comment_response"] = post_top_level_comment(youtube, google, video_id, text)
                add_completed(state, "top_level_comment")
                write_state(args.state, state)

        if args.poll_processing:
            result = poll_processing(
                youtube,
                google,
                video_id,
                max(1, args.poll_interval),
                max(1, args.poll_attempts),
            )
        else:
            result = readback(youtube, google, video_id)
        verification = verify_readback(result, parsed, video_id)
        state["readback"] = result
        state["readback_verification"] = verification
        state["readback_at"] = now_utc()
        add_completed(state, "readback")
        state.pop("last_error", None)
        write_state(args.state, state)
        if not verification["verified"]:
            raise RuntimeError("readback mismatch: " + "; ".join(verification["mismatches"]))

        output = {
            "video_id": video_id,
            "state_file": str(args.state.resolve()),
            "readback_verification": verification,
            "readback": result,
            "studio_next": "Run youtube-studio-finisher while the video remains private.",
        }
        print(json.dumps(output, indent=2))
        return 0
    except KeyboardInterrupt:
        state["last_error"] = "Interrupted by operator"
        state["failed_at"] = now_utc()
        write_state(args.state, state)
        print("error: interrupted; inspect the state file before retrying", file=sys.stderr)
        return 130
    except Exception as exc:
        state["last_error"] = f"{type(exc).__name__}: {exc}"
        state["failed_at"] = now_utc()
        write_state(args.state, state)
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
