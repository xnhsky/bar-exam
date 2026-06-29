#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate an RX coverage manifest JSON produced by check-rx-coverage.py."""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
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
RX_COVERAGE_SCRIPT = ROOT / "scripts" / "check-rx-coverage.py"
CONTRACT_SCRIPT = ROOT / "scripts" / "check-lexia-sync-contract.py"
TOP_LEVEL_FIELDS = (
    "schemaVersion",
    "filter",
    "strict",
    "supplementCap",
    "fail",
    "counts",
    "subjects",
    "skippedSubjects",
)
COUNT_FIELDS = (
    "jx",
    "present",
    "referenced",
    "uncovered",
    "unreachable",
    "safetynet",
    "dangling",
    "ok",
    "ari_missing",
)
SUBJECT_FIELDS = (
    "subject",
    "jx",
    "present",
    "referenced",
    "uncovered",
    "unreachable",
    "safetynet",
    "dangling",
    "ok",
    "ari_missing",
    "danglingDetail",
    "unreachableDetail",
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_rx_module():
    return load_module("check_rx_coverage", RX_COVERAGE_SCRIPT)


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


def validate_count_map(errors: list[str], counts: Any, label: str) -> None:
    if not require_type(errors, counts, dict, label):
        return
    keys = list(counts.keys())
    if keys != list(COUNT_FIELDS):
        errors.append(f"{label}: field order/keys mismatch: {keys}")
    for field in COUNT_FIELDS:
        if field not in counts:
            continue
        value = counts[field]
        if not isinstance(value, int) or value < 0:
            errors.append(f"{label}.{field}: expected non-negative integer")
    validate_count_invariants(errors, counts, label)


def validate_count_invariants(errors: list[str], counts: dict[str, Any], label: str) -> None:
    if not all(isinstance(counts.get(field), int) for field in COUNT_FIELDS):
        return
    if counts["uncovered"] != counts["unreachable"] + counts["safetynet"]:
        errors.append(
            f"{label}.uncovered: expected unreachable+safetynet "
            f"{counts['unreachable'] + counts['safetynet']}, got {counts['uncovered']}"
        )
    if counts["present"] - counts["uncovered"] != counts["referenced"] - counts["dangling"]:
        errors.append(
            f"{label}: present/referenced/uncovered/dangling counts are inconsistent"
        )
    if counts["ok"] > counts["jx"]:
        errors.append(f"{label}.ok: cannot exceed jx")
    if counts["ari_missing"] > counts["jx"]:
        errors.append(f"{label}.ari_missing: cannot exceed jx")


def validate_dangling_detail(detail: Any, subject_index: int, detail_index: int) -> list[str]:
    label = f"subjects[{subject_index}].danglingDetail[{detail_index}]"
    if not isinstance(detail, dict):
        return [f"{label}: expected object, got {type(detail).__name__}"]
    errors: list[str] = []
    if list(detail.keys()) != ["jx", "rx"]:
        errors.append(f"{label}: field order/keys mismatch: {list(detail.keys())}")
    if not isinstance(detail.get("jx"), str) or not detail.get("jx"):
        errors.append(f"{label}.jx: expected non-empty string")
    rx = detail.get("rx")
    if not isinstance(rx, list) or not all(isinstance(code, str) and code for code in rx):
        errors.append(f"{label}.rx: expected non-empty string list")
    return errors


def validate_unreachable_detail(detail: Any, subject_index: int, detail_index: int) -> list[str]:
    label = f"subjects[{subject_index}].unreachableDetail[{detail_index}]"
    if not isinstance(detail, dict):
        return [f"{label}: expected object, got {type(detail).__name__}"]
    errors: list[str] = []
    if list(detail.keys()) != ["jx", "rx"]:
        errors.append(f"{label}: field order/keys mismatch: {list(detail.keys())}")
    if not isinstance(detail.get("jx"), str) or not detail.get("jx"):
        errors.append(f"{label}.jx: expected non-empty string")
    rx = detail.get("rx")
    if not isinstance(rx, list):
        errors.append(f"{label}.rx: expected list")
        return errors
    for rx_index, item in enumerate(rx):
        item_label = f"{label}.rx[{rx_index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_label}: expected object, got {type(item).__name__}")
            continue
        if list(item.keys()) != ["code", "reason"]:
            errors.append(f"{item_label}: field order/keys mismatch: {list(item.keys())}")
        if not isinstance(item.get("code"), str) or not item.get("code"):
            errors.append(f"{item_label}.code: expected non-empty string")
        if not isinstance(item.get("reason"), str) or not item.get("reason"):
            errors.append(f"{item_label}.reason: expected non-empty string")
    return errors


def validate_subject(subject: Any, index: int) -> list[str]:
    label = f"subjects[{index}]"
    if not isinstance(subject, dict):
        return [f"{label}: expected object, got {type(subject).__name__}"]
    errors: list[str] = []
    if list(subject.keys()) != list(SUBJECT_FIELDS):
        errors.append(f"{label}: field order/keys mismatch: {list(subject.keys())}")
    if not isinstance(subject.get("subject"), str) or not subject.get("subject"):
        errors.append(f"{label}.subject: expected non-empty string")
    for field in COUNT_FIELDS:
        if field not in subject:
            continue
        value = subject[field]
        if not isinstance(value, int) or value < 0:
            errors.append(f"{label}.{field}: expected non-negative integer")
    validate_count_invariants(errors, subject, label)
    details = subject.get("danglingDetail")
    if require_type(errors, details, list, f"{label}.danglingDetail"):
        for detail_index, detail in enumerate(details):
            errors.extend(validate_dangling_detail(detail, index, detail_index))
        detail_count = sum(
            len(detail.get("rx", []))
            for detail in details
            if isinstance(detail, dict) and isinstance(detail.get("rx"), list)
        )
        if isinstance(subject.get("dangling"), int) and subject["dangling"] != detail_count:
            errors.append(f"{label}.dangling: detail count mismatch {subject['dangling']} != {detail_count}")
    details = subject.get("unreachableDetail")
    if require_type(errors, details, list, f"{label}.unreachableDetail"):
        for detail_index, detail in enumerate(details):
            errors.extend(validate_unreachable_detail(detail, index, detail_index))
        detail_count = sum(
            len(detail.get("rx", []))
            for detail in details
            if isinstance(detail, dict) and isinstance(detail.get("rx"), list)
        )
        if isinstance(subject.get("unreachable"), int) and subject["unreachable"] != detail_count:
            errors.append(f"{label}.unreachable: detail count mismatch {subject['unreachable']} != {detail_count}")
    return errors


def validate_manifest(rx, payload: Any) -> list[str]:
    errors: list[str] = []
    if isinstance(payload, list):
        return ["RX coverage manifest object expected; got array."]
    if not isinstance(payload, dict):
        return [f"RX coverage manifest object expected; got {type(payload).__name__}"]

    keys = list(payload.keys())
    if keys != list(TOP_LEVEL_FIELDS):
        errors.append(f"top-level field order/keys mismatch: {keys}")
    if payload.get("schemaVersion") != rx.SCHEMA_VERSION:
        errors.append(f"schemaVersion mismatch: {payload.get('schemaVersion')!r}")
    if not isinstance(payload.get("filter"), str):
        errors.append("filter: expected string")
    if not isinstance(payload.get("strict"), bool):
        errors.append("strict: expected boolean")
    if payload.get("supplementCap") != rx.SUPPLEMENT_CAP:
        errors.append(f"supplementCap mismatch: {payload.get('supplementCap')!r}")
    if not isinstance(payload.get("fail"), bool):
        errors.append("fail: expected boolean")

    validate_count_map(errors, payload.get("counts"), "counts")
    subjects = payload.get("subjects")
    if require_type(errors, subjects, list, "subjects"):
        for index, subject in enumerate(subjects):
            errors.extend(validate_subject(subject, index))
    else:
        subjects = []

    skipped = payload.get("skippedSubjects")
    if require_type(errors, skipped, list, "skippedSubjects"):
        if not all(isinstance(subject, str) and subject for subject in skipped):
            errors.append("skippedSubjects: expected non-empty string list")
        if skipped != sorted(skipped):
            errors.append("skippedSubjects: order is not stable-sorted")

    valid_subjects = [subject for subject in subjects if isinstance(subject, dict)]
    subject_names = [subject.get("subject") for subject in valid_subjects if isinstance(subject.get("subject"), str)]
    if subject_names != sorted(subject_names):
        errors.append("subjects: order is not stable-sorted")

    if isinstance(payload.get("counts"), dict):
        actual = {field: 0 for field in COUNT_FIELDS}
        for subject in valid_subjects:
            for field in COUNT_FIELDS:
                if isinstance(subject.get(field), int):
                    actual[field] += subject[field]
        expected = {field: payload["counts"].get(field) for field in COUNT_FIELDS}
        if all(isinstance(expected[field], int) for field in COUNT_FIELDS) and expected != actual:
            errors.append(f"counts mismatch: {expected} != {actual}")

    if isinstance(payload.get("fail"), bool) and isinstance(payload.get("counts"), dict) and isinstance(payload.get("strict"), bool):
        counts = payload["counts"]
        if all(isinstance(counts.get(field), int) for field in ("dangling", "unreachable")):
            actual_fail = counts["dangling"] > 0 or (payload["strict"] and counts["unreachable"] > 0)
            if payload["fail"] != actual_fail:
                errors.append(f"fail mismatch: {payload['fail']} != {actual_fail}")
    return errors


def comparable_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "filter": payload.get("filter"),
        "strict": payload.get("strict"),
        "supplementCap": payload.get("supplementCap"),
        "fail": payload.get("fail"),
        "counts": payload.get("counts"),
        "subjects": payload.get("subjects"),
        "skippedSubjects": payload.get("skippedSubjects"),
    }


def current_payload(rx, filter_token: str, strict: bool) -> dict[str, Any]:
    grand = {field: 0 for field in COUNT_FIELDS}
    checked, skipped = [], []
    with contextlib.redirect_stdout(io.StringIO()):
        dirs = rx.subject_dirs(filter_token or None)
        for directory in dirs:
            stats = rx.check_subject(directory, summary=True)
            if stats is None:
                skipped.append(directory.name)
                continue
            checked.append(stats)
            for field in COUNT_FIELDS:
                grand[field] += stats.get(field, 0)
    return comparable_payload(rx.build_payload(filter_token or "", strict, checked, skipped, grand))


def summarize_changed_subjects(expected: dict[str, Any], actual: dict[str, Any], limit: int = 12) -> list[str]:
    expected_subjects = expected.get("subjects") if isinstance(expected.get("subjects"), list) else []
    actual_subjects = actual.get("subjects") if isinstance(actual.get("subjects"), list) else []
    expected_by_name = {
        subject.get("subject"): subject
        for subject in expected_subjects
        if isinstance(subject, dict) and isinstance(subject.get("subject"), str)
    }
    actual_by_name = {
        subject.get("subject"): subject
        for subject in actual_subjects
        if isinstance(subject, dict) and isinstance(subject.get("subject"), str)
    }
    changes = []
    for name in sorted(set(expected_by_name) | set(actual_by_name)):
        if name not in expected_by_name:
            changes.append(f"+ {name}")
        elif name not in actual_by_name:
            changes.append(f"- {name}")
        elif expected_by_name[name] != actual_by_name[name]:
            changed_fields = [
                field
                for field in expected_by_name[name]
                if expected_by_name[name].get(field) != actual_by_name[name].get(field)
            ]
            changes.append(f"~ {name} ({', '.join(changed_fields)})")
    if len(changes) > limit:
        return changes[:limit] + [f"... (+{len(changes) - limit})"]
    return changes


def validate_against_current(rx, payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["cannot verify current RX coverage without a manifest object"]
    filter_token = payload.get("filter")
    strict = payload.get("strict")
    if not isinstance(filter_token, str):
        return ["cannot verify current RX coverage without valid filter"]
    if not isinstance(strict, bool):
        return ["cannot verify current RX coverage without valid strict flag"]
    expected = comparable_payload(payload)
    actual = current_payload(rx, filter_token, strict)
    errors = []
    for field in ("filter", "strict", "supplementCap", "fail", "counts", "skippedSubjects"):
        if expected.get(field) != actual.get(field):
            errors.append(f"current {field} mismatch: manifest={expected.get(field)!r} current={actual.get(field)!r}")
    if expected.get("subjects") != actual.get("subjects"):
        errors.append("current subjects mismatch:")
        errors.extend("  " + change for change in summarize_changed_subjects(expected, actual))
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate an RX coverage manifest JSON")
    ap.add_argument("manifest", help="manifest JSON path produced by check-rx-coverage.py --json")
    ap.add_argument("--verify-current", action="store_true", help="RX coverage が現在の outputs/ux と一致するかも検証")
    args = ap.parse_args()

    path = resolve_path(args.manifest)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"[ERROR] cannot read RX coverage manifest: {exc}")
        return 2
    except json.JSONDecodeError as exc:
        print(f"[ERROR] invalid JSON: {exc}")
        return 2

    rx = load_rx_module()
    contract = load_contract_module()
    errors = validate_manifest(rx, payload)
    if args.verify_current and not errors:
        errors.extend(validate_against_current(rx, payload))
    print("=== RX coverage manifest schema check ===")
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
