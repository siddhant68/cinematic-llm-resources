#!/usr/bin/env python3
"""Check a JSON MCP client configuration for a DaVinci Resolve server entry."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def walk_servers(data: Any) -> list[tuple[str, dict[str, Any]]]:
    found: list[tuple[str, dict[str, Any]]] = []
    if not isinstance(data, dict):
        return found
    for key in ("mcpServers", "servers"):
        value = data.get(key)
        if isinstance(value, dict):
            for name, config in value.items():
                if isinstance(config, dict):
                    found.append((str(name), config))
    for key, value in data.items():
        if key not in {"mcpServers", "servers"} and isinstance(value, dict):
            for name, config in walk_servers(value):
                found.append((f"{key}.{name}", config))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()

    if not args.config.exists():
        print(f"error: config not found: {args.config}", file=sys.stderr)
        return 2
    try:
        data = json.loads(args.config.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read JSON: {exc}", file=sys.stderr)
        return 2

    candidates = []
    for name, config in walk_servers(data):
        text = json.dumps(config).lower()
        if "davinci" in name.lower() or "resolve" in name.lower() or "davinci" in text or "resolve" in text:
            candidates.append((name, config))

    if not candidates:
        print("FAIL: no plausible DaVinci Resolve MCP server entry found.")
        return 1

    print(f"PASS: found {len(candidates)} plausible DaVinci Resolve MCP server entry or entries.")
    for name, config in candidates:
        command = config.get("command", "<not declared>")
        args_value = config.get("args", [])
        print(f"- {name}: command={command!r}, args={args_value!r}")
    print("NOTE: this validates configuration shape only; run a read-only Resolve preflight to prove connectivity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
