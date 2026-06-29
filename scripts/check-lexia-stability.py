#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check whether Lexia sync HTML files stay unchanged during a short observation window."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "lexia-file-stability/v1"


def resolve_path(path_arg: str) -> Path:
    path = Path(path_arg)
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def write_text_if_changed(path: Path, text: str) -> bool:
    try:
        if path.exists() and path.read_text(encoding="utf-8") == text:
            return False
    except OSError:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def iter_html_files(roots: list[Path]) -> tuple[list[Path], list[str]]:
    errors: list[str] = []
    files_by_path: dict[Path, Path] = {}
    for root in roots:
        if not root.exists():
            errors.append(f"{display_path(root)}: root missing")
            continue
        candidates = [root] if root.is_file() else root.rglob("*.html")
        for path in candidates:
            if path.is_file() and path.suffix.lower() == ".html":
                files_by_path[path.resolve()] = path
    files = sorted(files_by_path.values(), key=display_path)
    return files, errors


def file_info(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        return None, f"{display_path(path)}: cannot read file: {exc}"
    return {
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }, None


def snapshot(roots: list[Path]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    files, errors = iter_html_files(roots)
    result: dict[str, dict[str, Any]] = {}
    for path in files:
        info, error = file_info(path)
        if error:
            errors.append(error)
            continue
        assert info is not None
        result[display_path(path)] = info
    return result, errors


def diff_snapshots(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    before_paths = set(before)
    after_paths = set(after)
    common = before_paths & after_paths
    return {
        "added": sorted(after_paths - before_paths),
        "removed": sorted(before_paths - after_paths),
        "changed": sorted(path for path in common if before[path] != after[path]),
    }


def build_payload(
    roots: list[Path],
    settle_seconds: float,
    before: dict[str, dict[str, Any]],
    after: dict[str, dict[str, Any]],
    diff: dict[str, list[str]],
    errors: list[str],
    attempt: int = 1,
    attempts: int = 1,
) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "roots": [display_path(root) for root in roots],
        "settleSeconds": settle_seconds,
        "attempt": attempt,
        "attempts": attempts,
        "stable": not errors and not any(diff.values()),
        "beforeCount": len(before),
        "afterCount": len(after),
        "errorCount": len(errors),
        "changedCount": len(diff["changed"]),
        "addedCount": len(diff["added"]),
        "removedCount": len(diff["removed"]),
        "errors": errors,
        "changed": diff["changed"],
        "added": diff["added"],
        "removed": diff["removed"],
    }


def run_check(roots: list[Path], settle_seconds: float, attempt: int = 1, attempts: int = 1) -> dict[str, Any]:
    before, before_errors = snapshot(roots)
    if settle_seconds > 0:
        time.sleep(settle_seconds)
    after, after_errors = snapshot(roots)
    diff = diff_snapshots(before, after)
    return build_payload(roots, settle_seconds, before, after, diff, before_errors + after_errors, attempt, attempts)


def run_until_stable(
    roots: list[Path],
    settle_seconds: float,
    attempts: int = 1,
    retry_delay_seconds: float = 1.0,
) -> dict[str, Any]:
    payload: dict[str, Any] | None = None
    for attempt in range(1, attempts + 1):
        payload = run_check(roots, settle_seconds, attempt=attempt, attempts=attempts)
        if payload["stable"] or attempt == attempts:
            return payload
        if retry_delay_seconds > 0:
            time.sleep(retry_delay_seconds)
    assert payload is not None
    return payload


def print_summary(payload: dict[str, Any]) -> None:
    print("=== Lexia file stability check ===")
    print(f"roots={', '.join(payload['roots'])}")
    print(f"settleSeconds={payload['settleSeconds']}")
    if payload.get("attempts", 1) > 1:
        print(f"attempt={payload['attempt']} / {payload['attempts']}")
    print(f"before={payload['beforeCount']} / after={payload['afterCount']}")
    if payload["errors"]:
        for error in payload["errors"][:12]:
            print(f"  ERROR {error}")
    for label in ("added", "removed", "changed"):
        paths = payload[label]
        if paths:
            print(f"  {label.upper()} {len(paths)}")
            for path in paths[:12]:
                print(f"    {path}")
    print("\n=== summary ===")
    print("STABLE" if payload["stable"] else "CHANGED")


def main() -> int:
    ap = argparse.ArgumentParser(description="Check whether outputs/references HTML files are stable")
    ap.add_argument("roots", nargs="*", default=["outputs", "references"], help="HTML roots to observe")
    ap.add_argument("--settle-seconds", type=float, default=2.0, help="seconds between two snapshots")
    ap.add_argument("--attempts", type=int, default=1, help="retry until stable, up to this many attempts")
    ap.add_argument("--retry-delay-seconds", type=float, default=1.0, help="seconds to wait between unstable attempts")
    ap.add_argument("--json", help="write stable JSON report")
    args = ap.parse_args()

    if args.settle_seconds < 0:
        print("[ERROR] --settle-seconds must be >= 0")
        return 2
    if args.attempts < 1:
        print("[ERROR] --attempts must be >= 1")
        return 2
    if args.retry_delay_seconds < 0:
        print("[ERROR] --retry-delay-seconds must be >= 0")
        return 2
    roots = [resolve_path(root) for root in args.roots]
    payload = run_until_stable(roots, args.settle_seconds, args.attempts, args.retry_delay_seconds)
    if args.json:
        out = resolve_path(args.json)
        write_text_if_changed(out, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        print(f"json={display_path(out)}")
    print_summary(payload)
    return 0 if payload["stable"] else 1


if __name__ == "__main__":
    sys.exit(main())
