#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate a Lexia preflight bundle directory produced by check-lexia-preflight.py --bundle-dir."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SYNC_MANIFEST = "lexia-sync-manifest.json"
RX_MANIFEST = "rx-coverage.json"
WORKLIST_MARKDOWN = "lexia-content-worklist.md"
WORKLIST_MANIFEST = "lexia-content-worklist.json"
STABILITY_MANIFEST = "lexia-file-stability.json"
CHANGE_SUMMARY_MANIFEST = "lexia-change-summary.json"
MANIFEST_DIFF = "lexia-manifest-diff.json"
GENERATED_VALIDATORS_MANIFEST = "generated-validators.json"
PROMPTS_DIR = "lexia-content-prompts"
BUNDLE_INDEX = "bundle-index.json"
INDEX_SCHEMA_VERSION = "lexia-preflight-bundle-index/v5"
STABILITY_SCHEMA_VERSION = "lexia-file-stability/v1"
CHANGE_SUMMARY_SCHEMA_VERSION = "lexia-change-summary/v1"
MANIFEST_DIFF_SCHEMA_VERSION = "lexia-manifest-diff/v1"
GENERATED_VALIDATORS_SCHEMA_VERSION = "generated-validators/v1"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
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


def read_json(path: Path) -> tuple[Any | None, list[str]]:
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
    path.write_text(text, encoding="utf-8")
    return True


def file_info(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def prompt_filename_for_target(target: str) -> str:
    safe = re.sub(r"[^\w.-]+", "_", target, flags=re.UNICODE).strip("_") or "target"
    return f"{safe}_content_prompt.md"


class BundleModules:
    def __init__(self) -> None:
        self.sync_checker = load_module("check_lexia_manifest", SCRIPTS / "check-lexia-manifest.py")
        self.rx_checker = load_module("check_rx_coverage_manifest", SCRIPTS / "check-rx-coverage-manifest.py")
        self.worklist_checker = load_module("check_lexia_worklist", SCRIPTS / "check-lexia-worklist.py")
        self.generated_validators = load_module("check_generated_validators", SCRIPTS / "check-generated-validators.py")
        self.change_summary = load_module("lexia_change_summary", SCRIPTS / "lexia-change-summary.py")
        self.contract = self.sync_checker.load_contract_module()
        self.rx = self.rx_checker.load_rx_module()
        self.worklist = self.worklist_checker.load_worklist_module()


def validate_sync_manifest(mods: BundleModules, path: Path, verify_current: bool) -> tuple[Any | None, list[str]]:
    payload, errors = read_json(path)
    if errors:
        return payload, errors
    assert payload is not None
    errors = mods.sync_checker.validate_manifest(mods.contract, payload)
    if verify_current and not errors:
        errors.extend(mods.sync_checker.validate_against_current(mods.contract, payload))
    return payload, [f"{display_path(path)}: {error}" for error in errors]


def validate_rx_manifest(mods: BundleModules, path: Path, verify_current: bool) -> tuple[Any | None, list[str]]:
    payload, errors = read_json(path)
    if errors:
        return payload, errors
    assert payload is not None
    errors = mods.rx_checker.validate_manifest(mods.rx, payload)
    if verify_current and not errors:
        errors.extend(mods.rx_checker.validate_against_current(mods.rx, payload))
    return payload, [f"{display_path(path)}: {error}" for error in errors]


def validate_worklist_manifest(mods: BundleModules, path: Path, verify_current: bool) -> tuple[Any | None, list[str]]:
    payload, errors = read_json(path)
    if errors:
        return payload, errors
    assert payload is not None
    errors = mods.worklist_checker.validate_worklist(mods.worklist, mods.contract, payload)
    if verify_current and not errors:
        errors.extend(mods.worklist_checker.validate_against_current(mods.worklist, mods.contract, payload))
    return payload, [f"{display_path(path)}: {error}" for error in errors]


def validate_stability_manifest(path: Path) -> list[str]:
    if not path.exists():
        return []
    payload, errors = read_json(path)
    if errors:
        return errors
    local_errors: list[str] = []
    if not isinstance(payload, dict):
        return [f"{display_path(path)}: expected object payload"]
    if payload.get("schemaVersion") != STABILITY_SCHEMA_VERSION:
        local_errors.append(f"schemaVersion must be {STABILITY_SCHEMA_VERSION!r}")
    if payload.get("stable") is not True:
        local_errors.append("stable must be true")
    for field in ("beforeCount", "afterCount", "errorCount", "changedCount", "addedCount", "removedCount"):
        value = payload.get(field)
        if not isinstance(value, int) or value < 0:
            local_errors.append(f"{field} must be a non-negative integer")
    for field in ("errorCount", "changedCount", "addedCount", "removedCount"):
        if payload.get(field) != 0:
            local_errors.append(f"{field} must be 0")
    if payload.get("beforeCount") != payload.get("afterCount"):
        local_errors.append("beforeCount and afterCount must match")
    settle = payload.get("settleSeconds")
    if not isinstance(settle, (int, float)) or settle < 0:
        local_errors.append("settleSeconds must be a non-negative number")
    attempt = payload.get("attempt", 1)
    attempts = payload.get("attempts", 1)
    if not isinstance(attempt, int) or attempt < 1:
        local_errors.append("attempt must be a positive integer")
        attempt = 1
    if not isinstance(attempts, int) or attempts < 1:
        local_errors.append("attempts must be a positive integer")
        attempts = 1
    if attempt > attempts:
        local_errors.append("attempt must be <= attempts")
    roots = payload.get("roots")
    if not isinstance(roots, list) or not all(isinstance(item, str) and item for item in roots):
        local_errors.append("roots must be a non-empty string array")
    for field in ("errors", "changed", "added", "removed"):
        value = payload.get(field)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            local_errors.append(f"{field} must be a string array")
    for count_field, list_field in (
        ("errorCount", "errors"),
        ("changedCount", "changed"),
        ("addedCount", "added"),
        ("removedCount", "removed"),
    ):
        if isinstance(payload.get(count_field), int) and isinstance(payload.get(list_field), list):
            if payload[count_field] != len(payload[list_field]):
                local_errors.append(f"{count_field} must match {list_field} length")
    return [f"{display_path(path)}: {error}" for error in local_errors]


def validate_change_summary_manifest(mods: BundleModules, path: Path) -> list[str]:
    if not path.exists():
        return []
    payload, errors = read_json(path)
    if errors:
        return errors
    assert payload is not None
    return [f"{display_path(path)}: {error}" for error in mods.change_summary.validate_payload(payload)]


def validate_manifest_diff(path: Path) -> list[str]:
    if not path.exists():
        return []
    payload, errors = read_json(path)
    if errors:
        return errors
    local_errors: list[str] = []
    if not isinstance(payload, dict):
        return [f"{display_path(path)}: expected object payload"]
    if payload.get("schemaVersion") != MANIFEST_DIFF_SCHEMA_VERSION:
        local_errors.append(f"schemaVersion must be {MANIFEST_DIFF_SCHEMA_VERSION!r}")
    counts = payload.get("counts")
    if not isinstance(counts, dict):
        local_errors.append("counts must be an object")
        counts = {}
    for field in (
        "beforeEntries",
        "afterEntries",
        "unchanged",
        "added",
        "removed",
        "generatedOnly",
        "contentChanged",
        "sizeOnly",
        "metadataOnly",
        "changedTotal",
    ):
        value = counts.get(field)
        if not isinstance(value, int) or value < 0:
            local_errors.append(f"counts.{field} must be a non-negative integer")
    diff_fields = ("added", "removed", "generatedOnly", "contentChanged", "sizeOnly", "metadataOnly")
    for field in diff_fields:
        items = payload.get(field)
        if not isinstance(items, list):
            local_errors.append(f"{field} must be an array")
        elif isinstance(counts.get(field), int) and counts[field] != len(items):
            local_errors.append(f"counts.{field} must match {field} length")
    if all(isinstance(counts.get(field), int) for field in (*diff_fields, "changedTotal")):
        changed_total = sum(counts[field] for field in diff_fields)
        if counts["changedTotal"] != changed_total:
            local_errors.append(f"counts.changedTotal must equal diff group sum {changed_total}")
    return [f"{display_path(path)}: {error}" for error in local_errors]


def validate_generated_validators_manifest(mods: BundleModules, path: Path, verify_current: bool) -> list[str]:
    if not path.exists():
        return []
    payload, errors = read_json(path)
    if errors:
        return errors
    local_errors = mods.generated_validators.validate_payload(payload)
    if verify_current and not local_errors:
        local_errors.extend(mods.generated_validators.validate_against_current(payload))
    return [f"{display_path(path)}: {error}" for error in local_errors]


def worklist_targets(worklist_payload: Any) -> list[str]:
    if not isinstance(worklist_payload, dict):
        return []
    items = worklist_payload.get("items")
    if not isinstance(items, list):
        return []
    return sorted({
        item["target"]
        for item in items
        if isinstance(item, dict) and isinstance(item.get("target"), str) and item["target"].strip()
    })


def validate_worklist_markdown(path: Path, worklist_payload: Any) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{display_path(path)}: cannot read Markdown: {exc}"]
    if not text.startswith("# Lexia Content Worklist\n"):
        errors.append(f"{display_path(path)}: expected '# Lexia Content Worklist' heading")
    if isinstance(worklist_payload, dict) and isinstance(worklist_payload.get("targets"), int):
        needle = f"- targets: {worklist_payload['targets']}"
        if needle not in text:
            errors.append(f"{display_path(path)}: missing target count line {needle!r}")
    return errors


def validate_prompts(prompts_dir: Path, worklist_payload: Any) -> list[str]:
    errors: list[str] = []
    if not prompts_dir.is_dir():
        return [f"{display_path(prompts_dir)}: prompt directory missing"]
    targets = worklist_targets(worklist_payload)
    expected_by_file: dict[str, str] = {}
    for target in targets:
        name = prompt_filename_for_target(target)
        if name in expected_by_file:
            errors.append(f"{display_path(prompts_dir)}: prompt filename collision: {name}")
        expected_by_file[name] = target
    actual_files = {
        path.name: path
        for path in prompts_dir.glob("*_content_prompt.md")
        if path.is_file()
    }
    missing = sorted(set(expected_by_file) - set(actual_files))
    stale = sorted(set(actual_files) - set(expected_by_file))
    if missing:
        errors.append(f"{display_path(prompts_dir)}: missing prompt files: {', '.join(missing[:12])}")
    if stale:
        errors.append(f"{display_path(prompts_dir)}: stale prompt files: {', '.join(stale[:12])}")
    for name, target in sorted(expected_by_file.items()):
        path = actual_files.get(name)
        if not path:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{display_path(path)}: cannot read prompt: {exc}")
            continue
        heading = f"# {target} 内容改善セッション"
        if not text.startswith(heading + "\n"):
            errors.append(f"{display_path(path)}: expected heading {heading!r}")
    return errors


def bundle_files_payload(bundle_dir: Path) -> dict[str, Any]:
    files: dict[str, Any] = {}
    for name in (
        SYNC_MANIFEST,
        RX_MANIFEST,
        WORKLIST_MARKDOWN,
        WORKLIST_MANIFEST,
        STABILITY_MANIFEST,
        CHANGE_SUMMARY_MANIFEST,
        MANIFEST_DIFF,
        GENERATED_VALIDATORS_MANIFEST,
    ):
        path = bundle_dir / name
        if path.is_file():
            files[name] = file_info(path)
    prompts_dir = bundle_dir / PROMPTS_DIR
    prompt_files = {}
    if prompts_dir.is_dir():
        for path in sorted(prompts_dir.glob("*_content_prompt.md"), key=lambda p: p.name):
            if path.is_file():
                prompt_files[f"{PROMPTS_DIR}/{path.name}"] = file_info(path)
    return {
        **files,
        **prompt_files,
    }


def text_density(entry: dict[str, Any]) -> float:
    text_length = entry.get("textLength")
    size = entry.get("bytes")
    if not isinstance(text_length, int) or not isinstance(size, int) or size <= 0:
        return 0.0
    return text_length / size


def int_value(value: Any) -> int:
    return value if isinstance(value, int) else 0


def sync_quality_summary(sync_payload: dict[str, Any], limit: int = 5) -> dict[str, Any]:
    entries = sync_payload.get("entries")
    entries = entries if isinstance(entries, list) else []
    dict_entries = [entry for entry in entries if isinstance(entry, dict)]
    low_text_entries = sorted(
        dict_entries,
        key=lambda entry: (
            entry.get("textLength") if isinstance(entry.get("textLength"), int) else 10**18,
            text_density(entry),
            entry.get("sourcePath") if isinstance(entry.get("sourcePath"), str) else "",
        ),
    )[:limit]
    return {
        "hasTextLength": bool(dict_entries) and all(isinstance(entry.get("textLength"), int) for entry in dict_entries),
        "hasStableSha256": bool(dict_entries) and all(isinstance(entry.get("stableSha256"), str) for entry in dict_entries),
        "lowestTextEntries": [
            {
                "sourcePath": entry.get("sourcePath", ""),
                "category": entry.get("category", ""),
                "code": entry.get("code", ""),
                "textLength": entry.get("textLength", 0),
                "bytes": entry.get("bytes", 0),
                "density": round(text_density(entry), 6),
            }
            for entry in low_text_entries
        ],
    }


def build_index_payload(bundle_dir: Path) -> dict[str, Any]:
    sync_payload, _sync_errors = read_json(bundle_dir / SYNC_MANIFEST)
    rx_payload, _rx_errors = read_json(bundle_dir / RX_MANIFEST)
    worklist_payload, _worklist_errors = read_json(bundle_dir / WORKLIST_MANIFEST)
    stability_payload, _stability_errors = read_json(bundle_dir / STABILITY_MANIFEST)
    change_payload, _change_errors = read_json(bundle_dir / CHANGE_SUMMARY_MANIFEST)
    manifest_diff_payload, _manifest_diff_errors = read_json(bundle_dir / MANIFEST_DIFF)
    generated_validators_payload, _generated_validators_errors = read_json(bundle_dir / GENERATED_VALIDATORS_MANIFEST)
    generated_validators_checked = (bundle_dir / GENERATED_VALIDATORS_MANIFEST).is_file()
    sync_payload = sync_payload if isinstance(sync_payload, dict) else {}
    rx_payload = rx_payload if isinstance(rx_payload, dict) else {}
    worklist_payload = worklist_payload if isinstance(worklist_payload, dict) else {}
    stability_payload = stability_payload if isinstance(stability_payload, dict) else {}
    change_payload = change_payload if isinstance(change_payload, dict) else {}
    manifest_diff_payload = manifest_diff_payload if isinstance(manifest_diff_payload, dict) else {}
    generated_validators_payload = generated_validators_payload if isinstance(generated_validators_payload, dict) else {}
    rx_counts = rx_payload.get("counts") if isinstance(rx_payload.get("counts"), dict) else {}
    worklist_counts = worklist_payload.get("counts") if isinstance(worklist_payload.get("counts"), dict) else {}
    sync_quality = sync_quality_summary(sync_payload)
    generated_warning_items = generated_validators_payload.get("warnings", [])
    generated_warning_items = generated_warning_items if isinstance(generated_warning_items, list) else []
    generated_failure_items = generated_validators_payload.get("failures", [])
    generated_failure_items = generated_failure_items if isinstance(generated_failure_items, list) else []
    generated_warning_count = sum(
        item.get("warnings", 0)
        for item in generated_warning_items
        if isinstance(item, dict) and isinstance(item.get("warnings"), int)
    )
    sync_error_count = int_value(sync_payload.get("errorCount"))
    sync_warning_count = int_value(sync_payload.get("warningCount"))
    rx_dangling = int_value(rx_counts.get("dangling"))
    rx_unreachable = int_value(rx_counts.get("unreachable"))
    worklist_error = int_value(worklist_counts.get("ERROR"))
    worklist_warn = int_value(worklist_counts.get("WARN"))
    worklist_todo = int_value(worklist_counts.get("TODO"))
    change_fail_count = int_value(change_payload.get("failCount"))
    generated_failure_count = len(generated_failure_items)
    gate_details = {
        "syncContract": {
            "errorCount": sync_error_count,
            "warningCount": sync_warning_count,
        },
        "rxReachability": {
            "dangling": rx_dangling,
            "unreachable": rx_unreachable,
        },
        "contentWorklist": {
            "ERROR": worklist_error,
            "WARN": worklist_warn,
            "TODO": worklist_todo,
        },
        "changeSummary": {
            "failCount": change_fail_count,
        },
        "generatedValidators": {
            "checked": generated_validators_checked,
            "failureCount": generated_failure_count,
        },
    }
    gates = {
        "syncContract": sync_error_count == 0 and sync_warning_count == 0,
        "rxReachability": rx_dangling == 0 and rx_unreachable == 0,
        "contentWorklist": worklist_error == 0 and worklist_warn == 0 and worklist_todo == 0,
        "changeSummary": change_fail_count == 0,
        "generatedValidators": generated_validators_checked and generated_failure_count == 0,
        "generatedValidatorWarnings": generated_warning_count,
        "details": gate_details,
    }
    gates["ready"] = all(
        bool(gates[name])
        for name in (
            "syncContract",
            "rxReachability",
            "contentWorklist",
            "changeSummary",
            "generatedValidators",
        )
    )
    return {
        "schemaVersion": INDEX_SCHEMA_VERSION,
        "files": bundle_files_payload(bundle_dir),
        "gates": gates,
        "sync": {
            "schemaVersion": sync_payload.get("schemaVersion", ""),
            "html": sync_payload.get("html", 0),
            "classified": sync_payload.get("classified", 0),
            "errorCount": sync_error_count,
            "warningCount": sync_warning_count,
            "categories": sync_payload.get("categories", {}),
            "hasTextLength": sync_quality["hasTextLength"],
            "hasStableSha256": sync_quality["hasStableSha256"],
            "lowestTextEntries": sync_quality["lowestTextEntries"],
        },
        "rx": {
            "schemaVersion": rx_payload.get("schemaVersion", ""),
            "dangling": rx_dangling,
            "unreachable": rx_unreachable,
            "safetynet": int_value(rx_counts.get("safetynet")),
            "present": int_value(rx_counts.get("present")),
            "referenced": int_value(rx_counts.get("referenced")),
        },
        "worklist": {
            "schemaVersion": worklist_payload.get("schemaVersion", ""),
            "targets": worklist_payload.get("targets", 0),
            "counts": {
                "ERROR": worklist_error,
                "WARN": worklist_warn,
                "TODO": worklist_todo,
            },
            "promptFiles": sorted(
                path.name
                for path in (bundle_dir / PROMPTS_DIR).glob("*_content_prompt.md")
                if path.is_file()
            ) if (bundle_dir / PROMPTS_DIR).is_dir() else [],
        },
        "stability": {
            "schemaVersion": stability_payload.get("schemaVersion", ""),
            "stable": stability_payload.get("stable", None),
            "settleSeconds": stability_payload.get("settleSeconds", 0),
            "attempt": stability_payload.get("attempt", 1),
            "attempts": stability_payload.get("attempts", 1),
            "beforeCount": stability_payload.get("beforeCount", 0),
            "afterCount": stability_payload.get("afterCount", 0),
            "changedCount": stability_payload.get("changedCount", 0),
            "addedCount": stability_payload.get("addedCount", 0),
            "removedCount": stability_payload.get("removedCount", 0),
            "errorCount": stability_payload.get("errorCount", 0),
        },
        "changes": {
            "schemaVersion": change_payload.get("schemaVersion", ""),
            "untrackedFiles": change_payload.get("untrackedFiles", ""),
            "total": change_payload.get("total", 0),
            "failPresets": change_payload.get("failPresets", []),
            "failGroups": change_payload.get("failGroups", []),
            "failCount": change_fail_count,
            "failItems": change_payload.get("failItems", []) if isinstance(change_payload.get("failItems"), list) else [],
            "groups": {
                group.get("group"): group.get("count", 0)
                for group in change_payload.get("groups", [])
                if isinstance(group, dict) and isinstance(group.get("group"), str)
            } if isinstance(change_payload.get("groups"), list) else {},
        },
        "manifestDiff": {
            "schemaVersion": manifest_diff_payload.get("schemaVersion", ""),
            "counts": manifest_diff_payload.get("counts", {}) if isinstance(manifest_diff_payload.get("counts"), dict) else {},
        },
        "generatedValidators": {
            "schemaVersion": generated_validators_payload.get("schemaVersion", ""),
            "checked": generated_validators_checked,
            "targets": generated_validators_payload.get("targets", []) if isinstance(generated_validators_payload.get("targets"), list) else [],
            "planned": generated_validators_payload.get("planned", {}) if isinstance(generated_validators_payload.get("planned"), dict) else {},
            "summary": generated_validators_payload.get("summary", {}) if isinstance(generated_validators_payload.get("summary"), dict) else {},
            "warningCount": generated_warning_count,
            "warningItemCount": len(generated_warning_items),
            "failureCount": generated_failure_count,
            "warningItems": [
                {
                    "kind": item.get("kind", ""),
                    "label": item.get("label", ""),
                    "warnings": item.get("warnings", 0),
                }
                for item in generated_warning_items
                if isinstance(item, dict)
            ],
        },
    }


def write_bundle_index(bundle_dir: Path) -> Path:
    path = bundle_dir / BUNDLE_INDEX
    payload = build_index_payload(bundle_dir)
    write_text_if_changed(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return path


def validate_index(bundle_dir: Path) -> list[str]:
    path = bundle_dir / BUNDLE_INDEX
    payload, errors = read_json(path)
    if errors:
        return errors
    expected = build_index_payload(bundle_dir)
    if payload != expected:
        return [
            f"{display_path(path)}: stale index; run check-lexia-bundle.py "
            f"{display_path(bundle_dir)} --verify-current --write-index"
        ]
    return []


def change_fail_summary(bundle_dir: Path, limit: int = 5) -> dict[str, Any] | None:
    payload, errors = read_json(bundle_dir / CHANGE_SUMMARY_MANIFEST)
    if errors or not isinstance(payload, dict):
        return None
    fail_count = payload.get("failCount", 0)
    if not isinstance(fail_count, int) or fail_count <= 0:
        return None
    fail_items = payload.get("failItems", [])
    fail_items = fail_items if isinstance(fail_items, list) else []
    return {
        "failCount": fail_count,
        "failPresets": payload.get("failPresets", []) if isinstance(payload.get("failPresets"), list) else [],
        "failGroups": payload.get("failGroups", []) if isinstance(payload.get("failGroups"), list) else [],
        "failItems": [
            {
                "group": item.get("group", ""),
                "path": item.get("path", ""),
            }
            for item in fail_items[:limit]
            if isinstance(item, dict)
        ],
    }


def gate_detail_text(name: str, detail: Any) -> str:
    detail = detail if isinstance(detail, dict) else {}
    if name == "syncContract":
        return f"errors={int_value(detail.get('errorCount'))} warnings={int_value(detail.get('warningCount'))}"
    if name == "rxReachability":
        return f"dangling={int_value(detail.get('dangling'))} unreachable={int_value(detail.get('unreachable'))}"
    if name == "contentWorklist":
        return (
            f"ERROR={int_value(detail.get('ERROR'))} "
            f"WARN={int_value(detail.get('WARN'))} "
            f"TODO={int_value(detail.get('TODO'))}"
        )
    if name == "changeSummary":
        return f"failCount={int_value(detail.get('failCount'))}"
    if name == "generatedValidators":
        checked = "true" if detail.get("checked") is True else "false"
        return f"checked={checked} failureCount={int_value(detail.get('failureCount'))}"
    return ""


def not_ready_gates(bundle_dir: Path) -> dict[str, Any]:
    index = build_index_payload(bundle_dir)
    gates = index.get("gates", {})
    gates = gates if isinstance(gates, dict) else {}
    blocking = [
        name
        for name in (
            "syncContract",
            "rxReachability",
            "contentWorklist",
            "changeSummary",
            "generatedValidators",
        )
        if gates.get(name) is not True
    ]
    gate_details = gates.get("details", {})
    gate_details = gate_details if isinstance(gate_details, dict) else {}
    return {
        "ready": gates.get("ready") is True,
        "blocking": blocking,
        "details": [f"{name}: {gate_detail_text(name, gate_details.get(name))}" for name in blocking],
        "generatedValidatorWarnings": int_value(gates.get("generatedValidatorWarnings")),
    }


def validate_bundle(bundle_dir: Path, verify_current: bool = False) -> list[str]:
    errors: list[str] = []
    if not bundle_dir.is_dir():
        return [f"{display_path(bundle_dir)}: bundle directory missing"]
    mods = BundleModules()
    sync_payload, sync_errors = validate_sync_manifest(mods, bundle_dir / SYNC_MANIFEST, verify_current)
    rx_payload, rx_errors = validate_rx_manifest(mods, bundle_dir / RX_MANIFEST, verify_current)
    worklist_payload, worklist_errors = validate_worklist_manifest(mods, bundle_dir / WORKLIST_MANIFEST, verify_current)
    errors.extend(sync_errors)
    errors.extend(rx_errors)
    errors.extend(worklist_errors)
    errors.extend(validate_stability_manifest(bundle_dir / STABILITY_MANIFEST))
    errors.extend(validate_change_summary_manifest(mods, bundle_dir / CHANGE_SUMMARY_MANIFEST))
    errors.extend(validate_manifest_diff(bundle_dir / MANIFEST_DIFF))
    errors.extend(validate_generated_validators_manifest(mods, bundle_dir / GENERATED_VALIDATORS_MANIFEST, verify_current))
    errors.extend(validate_worklist_markdown(bundle_dir / WORKLIST_MARKDOWN, worklist_payload))
    errors.extend(validate_prompts(bundle_dir / PROMPTS_DIR, worklist_payload))
    if sync_payload is None:
        errors.append(f"{display_path(bundle_dir / SYNC_MANIFEST)}: required bundle file missing or unreadable")
    if rx_payload is None:
        errors.append(f"{display_path(bundle_dir / RX_MANIFEST)}: required bundle file missing or unreadable")
    if worklist_payload is None:
        errors.append(f"{display_path(bundle_dir / WORKLIST_MANIFEST)}: required bundle file missing or unreadable")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a Lexia preflight bundle directory")
    ap.add_argument("bundle_dir", help="directory produced by check-lexia-preflight.py --bundle-dir")
    ap.add_argument("--verify-current", action="store_true", help="各 manifest が現在の outputs/references と一致するかも検証")
    ap.add_argument("--verify-index", action="store_true", help=f"{BUNDLE_INDEX} が bundle の現在内容と一致するかも検証")
    ap.add_argument("--write-index", action="store_true", help=f"検証成功時に {BUNDLE_INDEX} も更新する")
    ap.add_argument("--fail-on-change-fail-items", action="store_true", help=f"{CHANGE_SUMMARY_MANIFEST} の failCount が 1 以上なら失敗させる")
    ap.add_argument("--fail-on-not-ready", action="store_true", help=f"{BUNDLE_INDEX} v5 の gates.ready が false なら失敗させる")
    args = ap.parse_args()

    bundle_dir = resolve_path(args.bundle_dir)
    errors = validate_bundle(bundle_dir, verify_current=args.verify_current)
    print("=== Lexia preflight bundle check ===")
    print(f"path={display_path(bundle_dir)}")
    if errors:
        for error in errors:
            print(f"  ERROR {error}")
        print("\n=== summary ===")
        print(f"ERROR={len(errors)}")
        return 1
    if args.write_index:
        index_path = write_bundle_index(bundle_dir)
        print(f"\nindex={display_path(index_path)}")
    if args.verify_index:
        index_errors = validate_index(bundle_dir)
        if index_errors:
            for error in index_errors:
                print(f"  ERROR {error}")
            print("\n=== summary ===")
            print(f"ERROR={len(index_errors)}")
            return 1
    change_summary = change_fail_summary(bundle_dir)
    if change_summary:
        print(
            "\nNOTICE change summary has blocking items: "
            f"failCount={change_summary['failCount']}"
        )
        if change_summary["failPresets"]:
            print("  failPresets=" + ", ".join(change_summary["failPresets"]))
        if change_summary["failGroups"]:
            print("  failGroups=" + ", ".join(change_summary["failGroups"]))
        for item in change_summary["failItems"]:
            print(f"  {item['group']}: {item['path']}")
        remaining = change_summary["failCount"] - len(change_summary["failItems"])
        if remaining > 0:
            print(f"  ... and {remaining} more")
        if args.fail_on_change_fail_items:
            print("\n=== summary ===")
            print("ERROR=1")
            return 1
    readiness = not_ready_gates(bundle_dir)
    if not readiness["ready"]:
        print("\nNOTICE bundle gates are not ready: " + ", ".join(readiness["blocking"]))
        for detail in readiness["details"]:
            print(f"  {detail}")
        if readiness["generatedValidatorWarnings"]:
            print(f"  generatedValidatorWarnings={readiness['generatedValidatorWarnings']}")
        if args.fail_on_not_ready:
            print("\n=== summary ===")
            print("ERROR=1")
            return 1
    print("\n=== summary ===")
    print("ERROR=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
