#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate a Lexia sync manifest JSON produced by check-lexia-sync-contract.py."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
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
CONTRACT_SCRIPT = ROOT / "scripts" / "check-lexia-sync-contract.py"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TOP_LEVEL_FIELDS = (
    "schemaVersion",
    "roots",
    "html",
    "classified",
    "categories",
    "errorCount",
    "warningCount",
    "entries",
)


def load_contract_module():
    spec = importlib.util.spec_from_file_location("check_lexia_sync_contract", CONTRACT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CONTRACT_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def resolve_path(path_arg: str) -> Path:
    path = Path(path_arg)
    return path if path.is_absolute() else ROOT / path


def require_type(errors: list[str], value: Any, typ: type | tuple[type, ...], label: str) -> bool:
    if isinstance(value, typ):
        return True
    type_name = getattr(typ, "__name__", " / ".join(t.__name__ for t in typ))
    errors.append(f"{label}: expected {type_name}, got {type(value).__name__}")
    return False


def validate_entry(contract, entry: Any, index: int) -> list[str]:
    errors: list[str] = []
    label = f"entries[{index}]"
    if not isinstance(entry, dict):
        return [f"{label}: expected object, got {type(entry).__name__}"]
    keys = list(entry.keys())
    expected_keys = list(contract.ENTRY_JSON_FIELDS)
    if keys != expected_keys:
        errors.append(f"{label}: field order/keys mismatch: {keys}")
    positive_integer_fields = {"bytes", "textLength"}
    for field in expected_keys:
        if field not in entry:
            continue
        if field in positive_integer_fields:
            if not isinstance(entry[field], int) or entry[field] <= 0:
                errors.append(f"{label}.{field}: expected positive integer")
        elif field == "stableSha256":
            if not isinstance(entry[field], str) or not SHA256_RE.fullmatch(entry[field]):
                errors.append(f"{label}.{field}: expected lowercase sha256 hex")
        else:
            if not isinstance(entry[field], str) or not entry[field].strip():
                errors.append(f"{label}.{field}: expected non-empty string")

    source_path = entry.get("sourcePath", "")
    file_name = entry.get("fileName", "")
    category = entry.get("category", "")
    generated = entry.get("generated", "")
    if isinstance(source_path, str):
        path_syntax_ok = True
        if "\\" in source_path:
            errors.append(f"{label}.sourcePath: must use forward slashes")
            path_syntax_ok = False
        if source_path.startswith("/") or ":" in source_path:
            errors.append(f"{label}.sourcePath: must be repo-relative")
            path_syntax_ok = False
        if any(part in {"", ".", ".."} for part in source_path.split("/")):
            errors.append(f"{label}.sourcePath: must not contain empty/current/parent path segments")
            path_syntax_ok = False
        if isinstance(file_name, str) and source_path.rsplit("/", 1)[-1] != file_name:
            errors.append(f"{label}.fileName: does not match sourcePath basename")
        if path_syntax_ok:
            expected_meta, _warnings = contract.classify(ROOT / source_path)
            if expected_meta is None:
                errors.append(f"{label}.sourcePath: cannot derive Lexia category/code from path")
            else:
                for field in ("category", "code", "baseCode", "subject", "subjectDir"):
                    if entry.get(field) != expected_meta[field]:
                        errors.append(
                            f"{label}.{field}: does not match sourcePath-derived value "
                            f"{expected_meta[field]!r}"
                        )
    if isinstance(category, str) and category not in contract.MIN_BYTES:
        errors.append(f"{label}.category: unknown category {category}")
    if isinstance(generated, str) and not contract.valid_generated_stamp(generated):
        errors.append(f"{label}.generated: invalid data-generated {generated}")
    return errors


def validate_manifest(contract, payload: Any) -> list[str]:
    errors: list[str] = []
    valid_roots: list[str] = []
    if isinstance(payload, list):
        return ["manifest object expected; got entries array. Use --json-format manifest when generating."]
    if not isinstance(payload, dict):
        return [f"manifest object expected; got {type(payload).__name__}"]

    keys = list(payload.keys())
    if keys != list(TOP_LEVEL_FIELDS):
        errors.append(f"top-level field order/keys mismatch: {keys}")
    if payload.get("schemaVersion") != contract.SCHEMA_VERSION:
        errors.append(f"schemaVersion mismatch: {payload.get('schemaVersion')!r}")
    if not require_type(errors, payload.get("roots"), list, "roots"):
        roots = []
    else:
        roots = payload["roots"]
        valid_roots = [root for root in roots if isinstance(root, str) and root]
        if not roots or len(valid_roots) != len(roots):
            errors.append("roots: expected non-empty string list")
    for field in ("html", "classified", "errorCount", "warningCount"):
        if not isinstance(payload.get(field), int) or payload.get(field) < 0:
            errors.append(f"{field}: expected non-negative integer")
    if not require_type(errors, payload.get("categories"), dict, "categories"):
        categories = {}
    else:
        categories = payload["categories"]
        for key, value in categories.items():
            if not isinstance(key, str) or not isinstance(value, int) or value < 0:
                errors.append(f"categories.{key}: expected non-negative integer")
    if not require_type(errors, payload.get("entries"), list, "entries"):
        entries = []
    else:
        entries = payload["entries"]

    for index, entry in enumerate(entries):
        errors.extend(validate_entry(contract, entry, index))

    source_path_items = [
        (index, entry.get("sourcePath"))
        for index, entry in enumerate(entries)
        if isinstance(entry, dict)
    ]
    string_source_path_items = [
        (index, source_path)
        for index, source_path in source_path_items
        if isinstance(source_path, str)
    ]
    string_source_paths = [source_path for _index, source_path in string_source_path_items]
    if valid_roots:
        root_prefixes = tuple(root.rstrip("/") + "/" for root in valid_roots)
        for index, source_path in string_source_path_items:
            if not source_path.startswith(root_prefixes):
                errors.append(f"entries[{index}].sourcePath: outside manifest roots: {source_path}")
    for index, source_path in string_source_path_items:
        if not source_path.lower().endswith((".html", ".htm")):
            errors.append(f"entries[{index}].sourcePath: expected .html/.htm file")
    if len(string_source_paths) == len(source_path_items) and string_source_paths != sorted(string_source_paths):
        errors.append("entries: sourcePath order is not stable-sorted")
    duplicates = [path for path, count in Counter(string_source_paths).items() if count > 1]
    if duplicates:
        errors.append("entries: duplicate sourcePath: " + ", ".join(sorted(duplicates)[:12]))
    file_names = [
        entry.get("fileName")
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("fileName"), str)
    ]
    duplicate_names = [name for name, count in Counter(file_names).items() if count > 1]
    if duplicate_names:
        errors.append("entries: duplicate fileName: " + ", ".join(sorted(duplicate_names)[:12]))
    ids = [
        (entry.get("category"), entry.get("code"))
        for entry in entries
        if (
            isinstance(entry, dict)
            and isinstance(entry.get("category"), str)
            and isinstance(entry.get("code"), str)
        )
    ]
    duplicate_ids = [key for key, count in Counter(ids).items() if count > 1]
    if duplicate_ids:
        errors.append(
            "entries: duplicate category+code: "
            + ", ".join(f"{category}:{code}" for category, code in sorted(duplicate_ids)[:12])
        )

    if isinstance(payload.get("classified"), int) and payload["classified"] != len(entries):
        errors.append(f"classified mismatch: {payload['classified']} != entries {len(entries)}")
    if isinstance(payload.get("html"), int) and payload["html"] < len(entries):
        errors.append(f"html count cannot be smaller than entries: {payload['html']} < {len(entries)}")
    actual_categories = Counter(
        entry.get("category")
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("category"), str)
    )
    if isinstance(payload.get("categories"), dict):
        expected_categories = {key: payload["categories"][key] for key in sorted(payload["categories"])}
        actual = {key: actual_categories[key] for key in sorted(actual_categories)}
        if expected_categories != actual:
            errors.append(f"categories mismatch: {expected_categories} != {actual}")
    return errors


def comparable_payload(contract, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "roots": payload.get("roots"),
        "html": payload.get("html"),
        "classified": payload.get("classified"),
        "categories": {key: payload["categories"][key] for key in sorted(payload.get("categories", {}))}
        if isinstance(payload.get("categories"), dict)
        else payload.get("categories"),
        "errorCount": payload.get("errorCount"),
        "warningCount": payload.get("warningCount"),
        "entries": payload.get("entries"),
    }


def current_payload(contract, roots: list[str]) -> dict[str, Any]:
    result = contract.audit_roots(roots, allow_untracked_sync_artifacts=True)
    return {
        "roots": roots,
        "html": len(result.files),
        "classified": len(result.entries),
        "categories": {key: result.category_counts[key] for key in sorted(result.category_counts)},
        "errorCount": result.error_count,
        "warningCount": result.warning_count,
        "entries": contract.entries_json(result.entries),
    }


def summarize_changed_entries(expected: dict[str, Any], actual: dict[str, Any], limit: int = 12) -> list[str]:
    expected_entries = expected.get("entries") if isinstance(expected.get("entries"), list) else []
    actual_entries = actual.get("entries") if isinstance(actual.get("entries"), list) else []
    expected_by_path = {
        entry.get("sourcePath"): entry
        for entry in expected_entries
        if isinstance(entry, dict) and isinstance(entry.get("sourcePath"), str)
    }
    actual_by_path = {
        entry.get("sourcePath"): entry
        for entry in actual_entries
        if isinstance(entry, dict) and isinstance(entry.get("sourcePath"), str)
    }
    paths = sorted(set(expected_by_path) | set(actual_by_path))
    changes = []
    changed_field_sets = []
    for path in paths:
        if path not in expected_by_path:
            changes.append(f"+ {path}")
        elif path not in actual_by_path:
            changes.append(f"- {path}")
        elif expected_by_path[path] != actual_by_path[path]:
            changed_fields = [
                field
                for field in expected_by_path[path]
                if expected_by_path[path].get(field) != actual_by_path[path].get(field)
            ]
            changed_field_sets.append(set(changed_fields))
            changes.append(f"~ {path} ({', '.join(changed_fields)})")
    if changed_field_sets and all(fields == {"generated"} for fields in changed_field_sets):
        changes.insert(
            0,
            "hint: generated-only drift. HTML content appears stable; footer timestamps are changing between manifest generations.",
        )
    size_fields = {"bytes", "textLength"}
    if changed_field_sets and all(fields and fields <= size_fields for fields in changed_field_sets):
        changes.insert(
            0,
            "hint: bytes/textLength-only drift. If another generation/content session is active, rerun after it settles; otherwise regenerate the manifest.",
        )
    if len(changes) > limit:
        return changes[:limit] + [f"... (+{len(changes) - limit})"]
    return changes


def validate_against_current(contract, payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["cannot verify current files without a manifest object"]
    roots = payload.get("roots")
    if not isinstance(roots, list) or not all(isinstance(root, str) and root for root in roots):
        return ["cannot verify current files without valid roots"]
    expected = comparable_payload(contract, payload)
    actual = current_payload(contract, roots)
    errors = []
    for field in ("roots", "html", "classified", "categories", "errorCount", "warningCount"):
        if expected.get(field) != actual.get(field):
            errors.append(f"current {field} mismatch: manifest={expected.get(field)!r} current={actual.get(field)!r}")
    if expected.get("entries") != actual.get("entries"):
        errors.append("current entries mismatch:")
        errors.extend("  " + change for change in summarize_changed_entries(expected, actual))
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a Lexia sync manifest JSON")
    ap.add_argument("manifest", help="manifest JSON path produced with --json-format manifest")
    ap.add_argument("--verify-current", action="store_true", help="manifest entries が現在の outputs/references と一致するかも検証")
    args = ap.parse_args()

    path = resolve_path(args.manifest)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"[ERROR] cannot read manifest: {exc}")
        return 2
    except json.JSONDecodeError as exc:
        print(f"[ERROR] invalid JSON: {exc}")
        return 2

    contract = load_contract_module()
    errors = validate_manifest(contract, payload)
    if args.verify_current and not errors:
        errors.extend(validate_against_current(contract, payload))
    print("=== Lexia manifest schema check ===")
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
