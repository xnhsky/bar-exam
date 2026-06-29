#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Summarize dirty worktree changes into Lexia/bar-exam review buckets."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "lexia-change-summary/v1"
DEFAULT_UNTRACKED_FILES = "all"
GROUP_ORDER = [
    "ROOT_TOOLING",
    "GENERATION_TOOLING",
    "GENERATED_SYNC_HTML",
    "QUARANTINED_OUTPUT",
    "CANONICAL",
    "DOCS",
    "INPUTS",
    "WORK",
    "LOCAL_CONFIG",
    "OTHER",
]
FAIL_PRESETS = {
    "root-tooling-only": [group for group in GROUP_ORDER if group != "ROOT_TOOLING"],
    "tooling-only": [group for group in GROUP_ORDER if group not in {"ROOT_TOOLING", "GENERATION_TOOLING"}],
    "sync-ready": ["QUARANTINED_OUTPUT", "WORK", "LOCAL_CONFIG", "OTHER"],
}


@dataclass(frozen=True)
class Change:
    status: str
    path: str
    original_path: str = ""


def run_git_status(untracked_files: str = DEFAULT_UNTRACKED_FILES) -> bytes:
    proc = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", f"--untracked-files={untracked_files}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.stdout


def parse_porcelain_z(data: bytes) -> list[Change]:
    text = data.decode("utf-8", errors="replace")
    parts = [part for part in text.split("\0") if part]
    changes: list[Change] = []
    i = 0
    while i < len(parts):
        record = parts[i]
        status = record[:2]
        path = record[3:] if len(record) >= 4 else ""
        original_path = ""
        if "R" in status or "C" in status:
            i += 1
            if i < len(parts):
                original_path = parts[i]
        if path:
            changes.append(Change(status=status, path=path.replace("\\", "/"), original_path=original_path.replace("\\", "/")))
        i += 1
    return changes


def category_for_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    name = Path(normalized).name
    if normalized == "README.md":
        return "ROOT_TOOLING"
    if normalized.startswith("scripts/"):
        if normalized.startswith("scripts/lex/") or name.startswith(("build_", "build-", "tx-build-", "validate-")):
            return "GENERATION_TOOLING"
        return "ROOT_TOOLING"
    if normalized.startswith(("outputs/", "references/")):
        if "/_failed/" in normalized:
            return "QUARANTINED_OUTPUT"
        if normalized.lower().endswith(".html"):
            return "GENERATED_SYNC_HTML"
        return "OTHER"
    if normalized.startswith("canonical/"):
        return "CANONICAL"
    if normalized.startswith("docs/"):
        return "DOCS"
    if normalized.startswith("inputs/"):
        return "INPUTS"
    if normalized.startswith("work/"):
        return "WORK"
    if normalized.startswith((".claude/", ".codex/", ".agents/")):
        return "LOCAL_CONFIG"
    return "OTHER"


def grouped_changes(changes: list[Change]) -> dict[str, list[Change]]:
    groups = {group: [] for group in GROUP_ORDER}
    for change in sorted(changes, key=lambda item: (GROUP_ORDER.index(category_for_path(item.path)), item.path)):
        groups[category_for_path(change.path)].append(change)
    return {group: items for group, items in groups.items() if items}


def ordered_groups(groups: list[str]) -> list[str]:
    selected = set(groups)
    return [group for group in GROUP_ORDER if group in selected]


def ordered_presets(presets: list[str]) -> list[str]:
    selected = set(presets)
    return [preset for preset in FAIL_PRESETS if preset in selected]


def expand_fail_groups(groups: list[str] | None = None, presets: list[str] | None = None) -> list[str]:
    expanded = list(groups or [])
    for preset in ordered_presets(presets or []):
        expanded.extend(FAIL_PRESETS[preset])
    return ordered_groups(expanded)


def build_payload(
    changes: list[Change],
    untracked_files: str = DEFAULT_UNTRACKED_FILES,
    fail_groups: list[str] | None = None,
    fail_presets: list[str] | None = None,
) -> dict[str, Any]:
    groups = grouped_changes(changes)
    fail_presets = ordered_presets(fail_presets or [])
    fail_groups = expand_fail_groups(fail_groups, fail_presets)
    group_counts = {group: len(items) for group, items in groups.items()}
    fail_items = [
        {
            "group": group,
            "status": item.status,
            "path": item.path,
            **({"originalPath": item.original_path} if item.original_path else {}),
        }
        for group in fail_groups
        for item in groups.get(group, [])
    ]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "untrackedFiles": untracked_files,
        "total": len(changes),
        "failPresets": fail_presets,
        "failGroups": fail_groups,
        "failCount": len(fail_items),
        "failItems": fail_items,
        "groups": [
            {
                "group": group,
                "count": len(items),
                "items": [
                    {
                        "status": item.status,
                        "path": item.path,
                        **({"originalPath": item.original_path} if item.original_path else {}),
                    }
                    for item in items
                ],
            }
            for group, items in groups.items()
        ],
    }


def validate_payload(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["expected object payload"]
    errors: list[str] = []
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SCHEMA_VERSION!r}")
    if "generatedAt" in payload:
        errors.append("generatedAt must not be present")
    untracked_files = payload.get("untrackedFiles")
    if untracked_files is not None and untracked_files not in {"all", "normal", "no"}:
        errors.append("untrackedFiles must be one of: all, normal, no")
    fail_groups = payload.get("failGroups", [])
    if not isinstance(fail_groups, list) or not all(isinstance(item, str) and item in GROUP_ORDER for item in fail_groups):
        errors.append("failGroups must be an array of known groups")
        fail_groups = []
    fail_presets = payload.get("failPresets", [])
    if not isinstance(fail_presets, list) or not all(isinstance(item, str) and item in FAIL_PRESETS for item in fail_presets):
        errors.append("failPresets must be an array of known presets")
    fail_count = payload.get("failCount", 0)
    if not isinstance(fail_count, int) or fail_count < 0:
        errors.append("failCount must be a non-negative integer")
        fail_count = 0
    fail_items = payload.get("failItems", [])
    if not isinstance(fail_items, list):
        errors.append("failItems must be an array when present")
        fail_items = []
    for item_index, item in enumerate(fail_items):
        if not isinstance(item, dict):
            errors.append(f"failItems[{item_index}] must be an object")
            continue
        group = item.get("group")
        if not isinstance(group, str) or group not in GROUP_ORDER:
            errors.append(f"failItems[{item_index}].group is unknown")
        elif fail_groups and group not in fail_groups:
            errors.append(f"failItems[{item_index}].group must be one of failGroups")
        if not isinstance(item.get("status"), str) or len(item["status"]) != 2:
            errors.append(f"failItems[{item_index}].status must be a two-character string")
        if not isinstance(item.get("path"), str) or not item["path"]:
            errors.append(f"failItems[{item_index}].path must be a non-empty string")
        original = item.get("originalPath")
        if original is not None and (not isinstance(original, str) or not original):
            errors.append(f"failItems[{item_index}].originalPath must be a non-empty string")
    total = payload.get("total")
    if not isinstance(total, int) or total < 0:
        errors.append("total must be a non-negative integer")
        total = 0
    groups = payload.get("groups")
    if not isinstance(groups, list):
        errors.append("groups must be an array")
        groups = []
    seen: set[str] = set()
    counted = 0
    for index, group in enumerate(groups):
        if not isinstance(group, dict):
            errors.append(f"groups[{index}] must be an object")
            continue
        name = group.get("group")
        if not isinstance(name, str) or name not in GROUP_ORDER:
            errors.append(f"groups[{index}].group is unknown")
        elif name in seen:
            errors.append(f"duplicate group {name}")
        else:
            seen.add(name)
        count = group.get("count")
        items = group.get("items")
        if not isinstance(items, list):
            errors.append(f"groups[{index}].items must be an array")
            items = []
        if not isinstance(count, int) or count < 0:
            errors.append(f"groups[{index}].count must be a non-negative integer")
        elif count != len(items):
            errors.append(f"groups[{index}].count must match items length")
        counted += len(items)
        for item_index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"groups[{index}].items[{item_index}] must be an object")
                continue
            if not isinstance(item.get("status"), str) or len(item["status"]) != 2:
                errors.append(f"groups[{index}].items[{item_index}].status must be a two-character string")
            if not isinstance(item.get("path"), str) or not item["path"]:
                errors.append(f"groups[{index}].items[{item_index}].path must be a non-empty string")
            original = item.get("originalPath")
            if original is not None and (not isinstance(original, str) or not original):
                errors.append(f"groups[{index}].items[{item_index}].originalPath must be a non-empty string")
    if counted != total:
        errors.append("total must match grouped item count")
    group_counts = {
        group.get("group"): group.get("count", 0)
        for group in groups
        if isinstance(group, dict) and isinstance(group.get("group"), str) and isinstance(group.get("count"), int)
    }
    expected_fail_count = sum(group_counts.get(group, 0) for group in fail_groups)
    if fail_count != expected_fail_count:
        errors.append("failCount must match selected failGroups")
    if "failItems" in payload and len(fail_items) != fail_count:
        errors.append("failItems length must match failCount")
    return errors


def write_text_if_changed(path: Path, text: str) -> bool:
    try:
        if path.exists() and path.read_text(encoding="utf-8") == text:
            return False
    except OSError:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def print_summary(payload: dict[str, Any], limit: int) -> None:
    print("=== Lexia change summary ===")
    print(f"total={payload['total']}")
    if payload.get("failPresets"):
        print(f"failPresets={', '.join(payload['failPresets'])}")
    if payload.get("failGroups"):
        print(f"failGroups={', '.join(payload['failGroups'])} / failCount={payload.get('failCount', 0)}")
    if payload.get("failItems"):
        print("\n=== blocking changes ===")
        for item in payload["failItems"][:limit]:
            print(f"  {item['group']}: {item['status']} {item['path']}")
        remaining = len(payload["failItems"]) - min(len(payload["failItems"]), limit)
        if remaining > 0:
            print(f"  ... and {remaining} more")
    for group in payload["groups"]:
        print(f"\n## {group['group']} ({group['count']})")
        for item in group["items"][:limit]:
            print(f"  {item['status']} {item['path']}")
        remaining = group["count"] - min(group["count"], limit)
        if remaining > 0:
            print(f"  ... and {remaining} more")
    print("\n=== suggested buckets ===")
    print("ROOT_TOOLING: scripts/tests/docs for this root-improvement session")
    print("GENERATION_TOOLING: generator/pipeline scripts; keep separate from root audit changes")
    print("GENERATED_SYNC_HTML + QUARANTINED_OUTPUT: generated-content sessions")
    print("CANONICAL/DOCS/INPUTS/WORK/LOCAL_CONFIG: review separately before commit")


def resolve_path(path_arg: str) -> Path:
    path = Path(path_arg)
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize dirty bar-exam changes by review bucket")
    ap.add_argument("--json", help="write stable JSON summary")
    ap.add_argument("--limit", type=int, default=20, help="max paths to print per group")
    ap.add_argument(
        "--untracked-files",
        choices=("all", "normal", "no"),
        default=DEFAULT_UNTRACKED_FILES,
        help="git status untracked expansion mode; default all expands untracked directories to files",
    )
    ap.add_argument(
        "--fail-on-group",
        action="append",
        choices=GROUP_ORDER,
        default=[],
        help="exit 1 when the selected change group has any items; repeatable",
    )
    ap.add_argument(
        "--fail-preset",
        action="append",
        choices=tuple(FAIL_PRESETS),
        default=[],
        help=(
            "shortcut for common fail-on-group sets; root-tooling-only fails on every group except ROOT_TOOLING; "
            "tooling-only permits ROOT_TOOLING and GENERATION_TOOLING; sync-ready fails on quarantine/scratch/local/other changes"
        ),
    )
    args = ap.parse_args()

    if args.limit < 1:
        print("[ERROR] --limit must be >= 1")
        return 2
    changes = parse_porcelain_z(run_git_status(args.untracked_files))
    payload = build_payload(changes, args.untracked_files, args.fail_on_group, args.fail_preset)
    if args.json:
        path = resolve_path(args.json)
        write_text_if_changed(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        print(f"json={path}")
    print_summary(payload, args.limit)
    return 1 if payload["failCount"] else 0


if __name__ == "__main__":
    sys.exit(main())
