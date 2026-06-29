#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare two Lexia sync manifests and classify sync-relevant drift."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_CHECKER = ROOT / "scripts" / "check-lexia-manifest.py"
SCHEMA_VERSION = "lexia-manifest-diff/v1"
ENTRY_CHANGE_FIELDS = (
    "sourcePath",
    "fileName",
    "code",
    "baseCode",
    "title",
    "subject",
    "subjectDir",
    "category",
    "bytes",
    "textLength",
    "stableSha256",
    "generated",
)


def load_manifest_checker():
    spec = importlib.util.spec_from_file_location("check_lexia_manifest", MANIFEST_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MANIFEST_CHECKER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def resolve_path(path_arg: str) -> Path:
    path = Path(path_arg)
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def read_manifest(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except OSError as exc:
        return None, [f"{display_path(path)}: cannot read JSON: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"{display_path(path)}: invalid JSON: {exc}"]


def write_text_if_changed(path: Path, text: str) -> bool:
    try:
        if path.exists() and path.read_text(encoding="utf-8") == text:
            return False
    except OSError:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def entries_by_path(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = payload.get("entries") if isinstance(payload.get("entries"), list) else []
    return {
        entry["sourcePath"]: entry
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("sourcePath"), str)
    }


def entry_code(entry: dict[str, Any]) -> str:
    value = entry.get("code")
    return value if isinstance(value, str) else ""


def entry_category(entry: dict[str, Any]) -> str:
    value = entry.get("category")
    return value if isinstance(value, str) else ""


def changed_fields(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    fields = [field for field in ENTRY_CHANGE_FIELDS if before.get(field) != after.get(field)]
    extra_fields = sorted((set(before) | set(after)) - set(ENTRY_CHANGE_FIELDS))
    fields.extend(field for field in extra_fields if before.get(field) != after.get(field))
    return fields


def classify_change(before: dict[str, Any], after: dict[str, Any], fields: list[str]) -> str:
    field_set = set(fields)
    before_hash = before.get("stableSha256")
    after_hash = after.get("stableSha256")
    if field_set == {"generated"}:
        return "generatedOnly"
    if isinstance(before_hash, str) and isinstance(after_hash, str):
        if before_hash != after_hash:
            return "contentChanged"
        if "generated" in field_set and field_set <= {"generated", "bytes", "textLength"}:
            return "generatedOnly"
        if field_set <= {"generated", "bytes", "textLength"}:
            return "sizeOnly"
        return "metadataOnly"
    if field_set <= {"generated", "bytes", "textLength"}:
        return "sizeOnly"
    return "metadataOnly"


def change_item(path: str, before: dict[str, Any], after: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    item: dict[str, Any] = {
        "sourcePath": path,
        "category": entry_category(after) or entry_category(before),
        "code": entry_code(after) or entry_code(before),
        "changedFields": fields,
    }
    for field in ("bytes", "textLength", "stableSha256", "generated"):
        if field in fields:
            item[f"before{field[0].upper()}{field[1:]}"] = before.get(field)
            item[f"after{field[0].upper()}{field[1:]}"] = after.get(field)
    return item


def build_diff_payload(before_path: Path, before: dict[str, Any], after_path: Path, after: dict[str, Any]) -> dict[str, Any]:
    before_entries = entries_by_path(before)
    after_entries = entries_by_path(after)
    paths = sorted(set(before_entries) | set(after_entries))
    groups: dict[str, list[Any]] = {
        "added": [],
        "removed": [],
        "generatedOnly": [],
        "contentChanged": [],
        "sizeOnly": [],
        "metadataOnly": [],
    }
    unchanged = 0
    for path in paths:
        if path not in before_entries:
            entry = after_entries[path]
            groups["added"].append({"sourcePath": path, "category": entry_category(entry), "code": entry_code(entry)})
            continue
        if path not in after_entries:
            entry = before_entries[path]
            groups["removed"].append({"sourcePath": path, "category": entry_category(entry), "code": entry_code(entry)})
            continue
        before_entry = before_entries[path]
        after_entry = after_entries[path]
        if before_entry == after_entry:
            unchanged += 1
            continue
        fields = changed_fields(before_entry, after_entry)
        group = classify_change(before_entry, after_entry, fields)
        groups[group].append(change_item(path, before_entry, after_entry, fields))

    counts = {
        "beforeEntries": len(before_entries),
        "afterEntries": len(after_entries),
        "unchanged": unchanged,
        **{group: len(items) for group, items in groups.items()},
    }
    counts["changedTotal"] = sum(counts[group] for group in groups)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "before": display_path(before_path),
        "after": display_path(after_path),
        "counts": counts,
        **groups,
    }


def validate_manifest_payload(checker, contract, path: Path, payload: Any) -> list[str]:
    errors = checker.validate_manifest(contract, payload)
    return [f"{display_path(path)}: {error}" for error in errors]


def print_group(name: str, items: list[Any], limit: int) -> None:
    if not items:
        return
    print(f"\n## {name} ({len(items)})")
    for item in items[:limit]:
        if isinstance(item, dict):
            fields = item.get("changedFields")
            suffix = f" [{', '.join(fields)}]" if isinstance(fields, list) and fields else ""
            print(f"  {item.get('category', '')} {item.get('code', '')} {item.get('sourcePath', '')}{suffix}")
        else:
            print(f"  {item}")
    remaining = len(items) - min(len(items), limit)
    if remaining > 0:
        print(f"  ... and {remaining} more")


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare two Lexia sync manifests")
    ap.add_argument("before", help="older lexia-sync-manifest.json")
    ap.add_argument("after", help="newer lexia-sync-manifest.json")
    ap.add_argument("--json", dest="json_path", help="write stable diff JSON")
    ap.add_argument("--limit", type=int, default=20, help="max items per group in stdout")
    ap.add_argument("--fail-on-content-change", action="store_true", help="exit 1 when stableSha256 changed")
    args = ap.parse_args()

    before_path = resolve_path(args.before)
    after_path = resolve_path(args.after)
    before_payload, before_errors = read_manifest(before_path)
    after_payload, after_errors = read_manifest(after_path)
    errors = before_errors + after_errors
    if not errors:
        checker = load_manifest_checker()
        contract = checker.load_contract_module()
        errors.extend(validate_manifest_payload(checker, contract, before_path, before_payload))
        errors.extend(validate_manifest_payload(checker, contract, after_path, after_payload))
    if errors:
        print("=== Lexia manifest diff ===")
        for error in errors:
            print(f"  ERROR {error}")
        print("\n=== summary ===")
        print(f"ERROR={len(errors)}")
        return 2

    assert isinstance(before_payload, dict)
    assert isinstance(after_payload, dict)
    payload = build_diff_payload(before_path, before_payload, after_path, after_payload)
    if args.json_path:
        out = resolve_path(args.json_path)
        write_text_if_changed(out, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        print(f"json={display_path(out)}")

    counts = payload["counts"]
    print("=== Lexia manifest diff ===")
    print(f"before={payload['before']}")
    print(f"after={payload['after']}")
    print(
        "counts: "
        + ", ".join(
            f"{key}={counts[key]}"
            for key in (
                "beforeEntries",
                "afterEntries",
                "unchanged",
                "added",
                "removed",
                "generatedOnly",
                "contentChanged",
                "sizeOnly",
                "metadataOnly",
            )
        )
    )
    for group in ("added", "removed", "contentChanged", "generatedOnly", "sizeOnly", "metadataOnly"):
        print_group(group, payload[group], args.limit)

    print("\n=== summary ===")
    if args.fail_on_content_change and counts["contentChanged"]:
        print(f"ERROR=1 contentChanged={counts['contentChanged']}")
        return 1
    print("ERROR=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
