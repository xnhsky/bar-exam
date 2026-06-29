#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate a Lexia content worklist JSON produced by lexia-content-worklist.py."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
WORKLIST_SCRIPT = ROOT / "scripts" / "lexia-content-worklist.py"
CONTRACT_SCRIPT = ROOT / "scripts" / "check-lexia-sync-contract.py"
TOP_LEVEL_FIELDS = (
    "schemaVersion",
    "roots",
    "filters",
    "targets",
    "counts",
    "categories",
    "kinds",
    "items",
)
SEVERITIES = ("ERROR", "WARN", "TODO")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_worklist_module():
    return load_module("lexia_content_worklist", WORKLIST_SCRIPT)


def load_contract_module():
    return load_module("check_lexia_sync_contract", CONTRACT_SCRIPT)


def resolve_path(path_arg: str) -> Path:
    path = Path(path_arg)
    return path if path.is_absolute() else ROOT / path


def require_type(errors: list[str], value: Any, typ: type | tuple[type, ...], label: str) -> bool:
    if isinstance(value, typ):
        return True
    type_name = getattr(typ, "__name__", " / ".join(t.__name__ for t in typ))
    errors.append(f"{label}: expected {type_name}, got {type(value).__name__}")
    return False


def validate_item(worklist, item: Any, index: int) -> list[str]:
    errors: list[str] = []
    label = f"items[{index}]"
    if not isinstance(item, dict):
        return [f"{label}: expected object, got {type(item).__name__}"]
    keys = list(item.keys())
    expected_keys = list(worklist.ITEM_JSON_FIELDS)
    if keys != expected_keys:
        errors.append(f"{label}: field order/keys mismatch: {keys}")
    for field in expected_keys:
        if field not in item:
            continue
        value = item[field]
        if field == "validators":
            if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
                errors.append(f"{label}.{field}: expected non-empty string list")
            elif value[-1] != worklist.CONTENT_PREFLIGHT_CMD:
                errors.append(f"{label}.{field}: final validator must be content preflight")
        elif field == "path":
            if not isinstance(value, str):
                errors.append(f"{label}.{field}: expected string")
        else:
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}.{field}: expected non-empty string")
    severity = item.get("severity")
    if isinstance(severity, str) and severity not in SEVERITIES:
        errors.append(f"{label}.severity: unknown severity {severity}")
    path = item.get("path")
    if isinstance(path, str) and path:
        if "\\" in path:
            errors.append(f"{label}.path: must use forward slashes")
        if path.startswith("/") or ":" in path:
            errors.append(f"{label}.path: must be repo-relative")
        if any(part in {"", ".", ".."} for part in path.split("/")):
            errors.append(f"{label}.path: must not contain empty/current/parent path segments")
    return errors


def validate_worklist(worklist, contract, payload: Any) -> list[str]:
    errors: list[str] = []
    if isinstance(payload, list):
        return ["worklist manifest object expected; got items array. Use --json-format manifest when generating."]
    if not isinstance(payload, dict):
        return [f"worklist manifest object expected; got {type(payload).__name__}"]

    keys = list(payload.keys())
    if keys != list(TOP_LEVEL_FIELDS):
        errors.append(f"top-level field order/keys mismatch: {keys}")
    if payload.get("schemaVersion") != worklist.SCHEMA_VERSION:
        errors.append(f"schemaVersion mismatch: {payload.get('schemaVersion')!r}")

    roots = payload.get("roots")
    if require_type(errors, roots, list, "roots"):
        if not roots or not all(isinstance(root, str) and root for root in roots):
            errors.append("roots: expected non-empty string list")
    else:
        roots = []

    filters = payload.get("filters")
    if require_type(errors, filters, dict, "filters"):
        target_filter = filters.get("target")
        if not isinstance(target_filter, list) or not all(isinstance(target, str) and target.strip() for target in target_filter):
            errors.append("filters.target: expected non-empty string list")
        if not isinstance(filters.get("includeFailed"), bool):
            errors.append("filters.includeFailed: expected boolean")

    if not isinstance(payload.get("targets"), int) or payload.get("targets") < 0:
        errors.append("targets: expected non-negative integer")

    if require_type(errors, payload.get("items"), list, "items"):
        items = payload["items"]
    else:
        items = []

    for index, item in enumerate(items):
        errors.extend(validate_item(worklist, item, index))

    for field in ("counts", "categories", "kinds"):
        value = payload.get(field)
        if not require_type(errors, value, dict, field):
            continue
        for key, count in value.items():
            if not isinstance(key, str) or not isinstance(count, int) or count < 0:
                errors.append(f"{field}.{key}: expected non-negative integer")

    valid_items = [item for item in items if isinstance(item, dict)]
    target_values = [item.get("target") for item in valid_items if isinstance(item.get("target"), str)]
    if isinstance(payload.get("targets"), int) and payload["targets"] != len(set(target_values)):
        errors.append(f"targets mismatch: {payload['targets']} != unique targets {len(set(target_values))}")

    actual_counts = Counter(item.get("severity") for item in valid_items if isinstance(item.get("severity"), str))
    if isinstance(payload.get("counts"), dict):
        expected_counts = {severity: payload["counts"].get(severity, 0) for severity in SEVERITIES}
        actual = {severity: actual_counts.get(severity, 0) for severity in SEVERITIES}
        if expected_counts != actual:
            errors.append(f"counts mismatch: {expected_counts} != {actual}")

    for field in ("category", "kind"):
        top_field = "categories" if field == "category" else "kinds"
        actual_counts = Counter(item.get(field) for item in valid_items if isinstance(item.get(field), str))
        if isinstance(payload.get(top_field), dict):
            expected = {key: payload[top_field][key] for key in sorted(payload[top_field])}
            actual = {key: actual_counts[key] for key in sorted(actual_counts)}
            if expected != actual:
                errors.append(f"{top_field} mismatch: {expected} != {actual}")

    if valid_items:
        sorted_items = sorted(
            valid_items,
            key=lambda item: worklist.priority_key(
                contract,
                worklist.WorkItem(
                    target=item.get("target", ""),
                    severity=item.get("severity", ""),
                    kind=item.get("kind", ""),
                    category=item.get("category", ""),
                    path=item.get("path", ""),
                    message=item.get("message", ""),
                    action=item.get("action", ""),
                    validators=item.get("validators", []) if isinstance(item.get("validators"), list) else [],
                ),
            ),
        )
        if valid_items != sorted_items:
            errors.append("items: order is not stable-sorted")
    return errors


def comparable_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "roots": payload.get("roots"),
        "filters": payload.get("filters"),
        "targets": payload.get("targets"),
        "counts": payload.get("counts"),
        "categories": payload.get("categories"),
        "kinds": payload.get("kinds"),
        "items": payload.get("items"),
    }


def current_payload(worklist, contract, roots: list[str], filters: dict[str, Any]) -> dict[str, Any]:
    items = worklist.collect_contract_items(contract, roots)
    include_failed = filters.get("includeFailed", True) if isinstance(filters, dict) else True
    target_filter = filters.get("target", []) if isinstance(filters, dict) else []
    if include_failed:
        items.extend(worklist.collect_failed_items(contract))
    items = worklist.dedupe(items)
    if isinstance(target_filter, list):
        items = worklist.filter_targets(items, [target for target in target_filter if isinstance(target, str)])
    items = sorted(items, key=lambda item: worklist.priority_key(contract, item))
    return comparable_payload(worklist.build_worklist_payload(
        contract,
        roots,
        items,
        target_filter=target_filter if isinstance(target_filter, list) else [],
        include_failed=include_failed,
    ))


def summarize_changed_items(expected: dict[str, Any], actual: dict[str, Any], limit: int = 12) -> list[str]:
    expected_items = expected.get("items") if isinstance(expected.get("items"), list) else []
    actual_items = actual.get("items") if isinstance(actual.get("items"), list) else []

    def item_key(item: Any) -> tuple[str, str, str, str, str, str] | None:
        if not isinstance(item, dict):
            return None
        vals = tuple(str(item.get(field, "")) for field in ("target", "severity", "kind", "category", "path", "message"))
        return vals

    expected_by_key = {key: item for item in expected_items if (key := item_key(item)) is not None}
    actual_by_key = {key: item for item in actual_items if (key := item_key(item)) is not None}
    keys = sorted(set(expected_by_key) | set(actual_by_key))
    changes = []
    for key in keys:
        label = " / ".join(part for part in key if part)
        if key not in expected_by_key:
            changes.append(f"+ {label}")
        elif key not in actual_by_key:
            changes.append(f"- {label}")
        elif expected_by_key[key] != actual_by_key[key]:
            changes.append(f"~ {label}")
    if len(changes) > limit:
        return changes[:limit] + [f"... (+{len(changes) - limit})"]
    return changes


def validate_against_current(worklist, contract, payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["cannot verify current worklist without a manifest object"]
    roots = payload.get("roots")
    if not isinstance(roots, list) or not all(isinstance(root, str) and root for root in roots):
        return ["cannot verify current worklist without valid roots"]
    filters = payload.get("filters")
    if not isinstance(filters, dict):
        return ["cannot verify current worklist without valid filters"]
    expected = comparable_payload(payload)
    actual = current_payload(worklist, contract, roots, filters)
    errors = []
    for field in ("roots", "filters", "targets", "counts", "categories", "kinds"):
        if expected.get(field) != actual.get(field):
            errors.append(f"current {field} mismatch: manifest={expected.get(field)!r} current={actual.get(field)!r}")
    if expected.get("items") != actual.get("items"):
        errors.append("current items mismatch:")
        errors.extend("  " + change for change in summarize_changed_items(expected, actual))
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a Lexia content worklist manifest JSON")
    ap.add_argument("worklist", help="worklist JSON path produced with --json-format manifest")
    ap.add_argument("--verify-current", action="store_true", help="worklist items が現在の outputs/references と一致するかも検証")
    args = ap.parse_args()

    path = resolve_path(args.worklist)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"[ERROR] cannot read worklist: {exc}")
        return 2
    except json.JSONDecodeError as exc:
        print(f"[ERROR] invalid JSON: {exc}")
        return 2

    worklist = load_worklist_module()
    contract = load_contract_module()
    errors = validate_worklist(worklist, contract, payload)
    if args.verify_current and not errors:
        errors.extend(validate_against_current(worklist, contract, payload))
    print("=== Lexia content worklist schema check ===")
    print(f"path={contract.display_path(path)}")
    if errors:
        for msg in errors:
            print(f"  ERROR {msg}")
        print("\n=== summary ===")
        print(f"ERROR={len(errors)}")
        return 1
    print("\n=== summary ===")
    print("ERROR=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
