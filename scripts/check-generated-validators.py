#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ARIADNE/RX/TREE の個別バリデータを outputs/ux 横断で実行する read-only ゲート。"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TARGETS = ("ariadne", "rx", "tree")
RX_FILE_RE = re.compile(r"^(.+RX\d{3})_(\d+)\.html$")
SCHEMA_VERSION = "generated-validators/v1"
TOP_LEVEL_FIELDS = (
    "schemaVersion",
    "root",
    "targets",
    "planned",
    "summary",
    "warnings",
    "failures",
)
SUMMARY_FIELDS = ("items", "failures", "errors", "warnings")
RESULT_FIELDS = ("kind", "label", "command", "returnCode", "errors", "warnings", "warningLines")


@dataclass(frozen=True)
class PlanItem:
    kind: str
    label: str
    command: list[str]


@dataclass
class ResultCounts:
    items: int = 0
    failures: int = 0
    warnings: int = 0
    errors: int = 0


@dataclass(frozen=True)
class ValidationResult:
    kind: str
    label: str
    command: str
    return_code: int
    errors: int
    warnings: int
    warning_lines: list[str]


def repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def resolve_scan_root(root: str) -> Path:
    p = Path(root)
    return (p if p.is_absolute() else ROOT / p).resolve()


def write_text_if_changed(path: Path, text: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def require_type(errors: list[str], value: object, typ: type | tuple[type, ...], label: str) -> bool:
    if isinstance(value, typ):
        return True
    type_name = " / ".join(t.__name__ for t in typ) if isinstance(typ, tuple) else typ.__name__
    errors.append(f"{label}: expected {type_name}, got {type(value).__name__}")
    return False


def find_ariadne_files(scan_root: Path) -> list[Path]:
    return sorted(p for p in scan_root.rglob("*_ARIADNE.html") if p.is_file())


def find_tree_files(scan_root: Path) -> list[Path]:
    return sorted(p for p in scan_root.rglob("*_TREE.html") if p.is_file())


def find_rx_groups(scan_root: Path) -> list[tuple[Path, str]]:
    grouped: dict[tuple[Path, str], list[int]] = defaultdict(list)
    for path in scan_root.rglob("*.html"):
        if not path.is_file():
            continue
        m = RX_FILE_RE.fullmatch(path.name)
        if not m:
            continue
        grouped[(path.parent, m.group(1))].append(int(m.group(2)))
    return sorted(grouped)


def build_plan(scan_root: Path, targets: list[str]) -> list[PlanItem]:
    plan: list[PlanItem] = []
    if "ariadne" in targets:
        for path in find_ariadne_files(scan_root):
            plan.append(PlanItem(
                "ariadne",
                repo_rel(path),
                [sys.executable, str(SCRIPTS / "validate-ariadne.py"), str(path)],
            ))
    if "rx" in targets:
        for directory, basename in find_rx_groups(scan_root):
            plan.append(PlanItem(
                "rx",
                f"{repo_rel(directory)}/{basename}_*.html",
                [sys.executable, str(SCRIPTS / "validate-rx.py"), str(directory), basename],
            ))
    if "tree" in targets:
        for path in find_tree_files(scan_root):
            plan.append(PlanItem(
                "tree",
                repo_rel(path),
                [sys.executable, str(SCRIPTS / "validate-tree.py"), str(path)],
            ))
    return plan


def parse_counts(kind: str, output: str, returncode: int) -> tuple[int, int]:
    patterns = {
        "ariadne": r"ARIADNE 検証: PASS \d+ / WARN (\d+) / ERROR (\d+)",
        "rx": r"ERROR=(\d+), WARNING=(\d+)",
        "tree": r"ERROR=(\d+)\s+WARNING=(\d+)",
    }
    m = re.search(patterns[kind], output)
    if not m:
        return (1 if returncode else 0), 0
    if kind == "ariadne":
        return int(m.group(2)), int(m.group(1))
    return int(m.group(1)), int(m.group(2))


def warning_lines(output: str) -> list[str]:
    return [
        line.strip()
        for line in output.splitlines()
        if line.lstrip().startswith(("[WARN]", "[WARN ]"))
    ]


def display_cmd(command: list[str]) -> str:
    parts: list[str] = []
    for part in command:
        if part == sys.executable:
            parts.append("python")
            continue
        p = Path(part)
        if p.is_absolute():
            parts.append(repo_rel(p))
        else:
            parts.append(part)
    return " ".join(parts)


def run_item(item: PlanItem, verbose: bool, show_warnings: bool) -> ValidationResult:
    completed = subprocess.run(
        item.command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    errors, warnings = parse_counts(item.kind, output, completed.returncode)
    lines = warning_lines(output)
    if show_warnings and warnings and completed.returncode == 0 and not verbose:
        suffix = ""
        if lines:
            suffix = f" :: {lines[0]}"
            if len(lines) > 1:
                suffix += f" (+{len(lines) - 1} more)"
        print(f"[WARN] {item.kind}: {item.label} warnings={warnings}{suffix}")
    if verbose or completed.returncode != 0:
        print(f"\n--- {item.kind}: {item.label} ---")
        print(f"$ {display_cmd(item.command)}")
        if output:
            print(output, end="" if output.endswith("\n") else "\n")
        print("[PASS]" if completed.returncode == 0 else f"[FAIL] exit {completed.returncode}")
    return ValidationResult(
        kind=item.kind,
        label=item.label,
        command=display_cmd(item.command),
        return_code=completed.returncode,
        errors=errors,
        warnings=warnings,
        warning_lines=lines,
    )


def summarize_plan(plan: list[PlanItem]) -> dict[str, int]:
    counts = {target: 0 for target in TARGETS}
    for item in plan:
        counts[item.kind] += 1
    return counts


def result_to_dict(result: ValidationResult) -> dict[str, object]:
    return {
        "kind": result.kind,
        "label": result.label,
        "command": result.command,
        "returnCode": result.return_code,
        "errors": result.errors,
        "warnings": result.warnings,
        "warningLines": result.warning_lines,
    }


def counts_to_dict(counts: ResultCounts) -> dict[str, int]:
    return {
        "items": counts.items,
        "failures": counts.failures,
        "errors": counts.errors,
        "warnings": counts.warnings,
    }


def validate_result_item(item: object, label: str) -> list[str]:
    if not isinstance(item, dict):
        return [f"{label}: expected object, got {type(item).__name__}"]
    errors: list[str] = []
    if list(item.keys()) != list(RESULT_FIELDS):
        errors.append(f"{label}: field order/keys mismatch: {list(item.keys())}")
    kind = item.get("kind")
    if not isinstance(kind, str) or kind not in TARGETS:
        errors.append(f"{label}.kind: unknown target")
    for field in ("label", "command"):
        value = item.get(field)
        if not isinstance(value, str) or not value:
            errors.append(f"{label}.{field}: expected non-empty string")
    for field in ("returnCode", "errors", "warnings"):
        value = item.get(field)
        if not isinstance(value, int) or value < 0:
            errors.append(f"{label}.{field}: expected non-negative integer")
    lines = item.get("warningLines")
    if not isinstance(lines, list) or not all(isinstance(line, str) for line in lines):
        errors.append(f"{label}.warningLines: expected string array")
    return errors


def validate_payload(payload: object) -> list[str]:
    errors: list[str] = []
    if isinstance(payload, list):
        return ["generated validators manifest object expected; got array."]
    if not isinstance(payload, dict):
        return [f"generated validators manifest object expected; got {type(payload).__name__}"]
    if list(payload.keys()) != list(TOP_LEVEL_FIELDS):
        errors.append(f"top-level field order/keys mismatch: {list(payload.keys())}")
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"schemaVersion mismatch: {payload.get('schemaVersion')!r}")
    if not isinstance(payload.get("root"), str) or not payload["root"]:
        errors.append("root: expected non-empty string")
    targets = payload.get("targets")
    if require_type(errors, targets, list, "targets"):
        if not targets or not all(isinstance(target, str) and target in TARGETS for target in targets):
            errors.append("targets: expected non-empty known target list")
        elif targets != [target for target in TARGETS if target in targets]:
            errors.append("targets: order is not stable-sorted")
    else:
        targets = []
    planned = payload.get("planned")
    if require_type(errors, planned, dict, "planned"):
        if isinstance(targets, list):
            if list(planned.keys()) != list(targets):
                errors.append(f"planned: keys must match targets: {list(planned.keys())}")
        for key, value in planned.items():
            if not isinstance(key, str) or key not in TARGETS:
                errors.append(f"planned.{key}: unknown target")
            if not isinstance(value, int) or value < 0:
                errors.append(f"planned.{key}: expected non-negative integer")
    else:
        planned = {}
    summary = payload.get("summary")
    if require_type(errors, summary, dict, "summary"):
        if isinstance(targets, list):
            if list(summary.keys()) != list(targets):
                errors.append(f"summary: keys must match targets: {list(summary.keys())}")
        for key, counts in summary.items():
            if not isinstance(key, str) or key not in TARGETS:
                errors.append(f"summary.{key}: unknown target")
            if not isinstance(counts, dict):
                errors.append(f"summary.{key}: expected object")
                continue
            if list(counts.keys()) != list(SUMMARY_FIELDS):
                errors.append(f"summary.{key}: field order/keys mismatch: {list(counts.keys())}")
            for field in SUMMARY_FIELDS:
                value = counts.get(field)
                if not isinstance(value, int) or value < 0:
                    errors.append(f"summary.{key}.{field}: expected non-negative integer")
            planned_count = planned.get(key) if isinstance(planned, dict) else None
            if isinstance(planned_count, int) and isinstance(counts.get("items"), int) and counts["items"] != planned_count:
                errors.append(f"summary.{key}.items must match planned.{key}")
    else:
        summary = {}
    warnings = payload.get("warnings")
    if require_type(errors, warnings, list, "warnings"):
        for index, item in enumerate(warnings):
            errors.extend(validate_result_item(item, f"warnings[{index}]"))
    else:
        warnings = []
    failures = payload.get("failures")
    if require_type(errors, failures, list, "failures"):
        for index, item in enumerate(failures):
            errors.extend(validate_result_item(item, f"failures[{index}]"))
    else:
        failures = []
    warning_totals = {target: 0 for target in TARGETS}
    error_totals = {target: 0 for target in TARGETS}
    failure_totals = {target: 0 for target in TARGETS}
    for item in warnings if isinstance(warnings, list) else []:
        if isinstance(item, dict) and isinstance(item.get("kind"), str) and item["kind"] in TARGETS:
            warning_totals[item["kind"]] += item.get("warnings") if isinstance(item.get("warnings"), int) else 0
    for item in failures if isinstance(failures, list) else []:
        if isinstance(item, dict) and isinstance(item.get("kind"), str) and item["kind"] in TARGETS:
            failure_totals[item["kind"]] += 1
            error_totals[item["kind"]] += item.get("errors") if isinstance(item.get("errors"), int) else 0
    if isinstance(summary, dict):
        for target, counts in summary.items():
            if not isinstance(counts, dict) or target not in TARGETS:
                continue
            if isinstance(counts.get("warnings"), int) and counts["warnings"] != warning_totals[target]:
                errors.append(f"summary.{target}.warnings must match warning item total")
            if isinstance(counts.get("failures"), int) and counts["failures"] != failure_totals[target]:
                errors.append(f"summary.{target}.failures must match failures length")
            if isinstance(counts.get("errors"), int) and counts["errors"] != error_totals[target]:
                errors.append(f"summary.{target}.errors must match failure error total")
    return errors


def build_payload(scan_root: Path, targets: list[str], plan: list[PlanItem], results: list[ValidationResult]) -> dict[str, object]:
    summary = {target: ResultCounts() for target in TARGETS}
    for result in results:
        counts = summary[result.kind]
        counts.items += 1
        counts.errors += result.errors
        counts.warnings += result.warnings
        if result.return_code != 0:
            counts.failures += 1
    planned = summarize_plan(plan)
    selected_targets = [target for target in TARGETS if target in targets]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "root": repo_rel(scan_root),
        "targets": selected_targets,
        "planned": {target: planned[target] for target in selected_targets},
        "summary": {target: counts_to_dict(summary[target]) for target in selected_targets},
        "warnings": [result_to_dict(result) for result in results if result.warnings],
        "failures": [result_to_dict(result) for result in results if result.return_code != 0],
    }


def current_payload(root: str, targets: list[str]) -> dict[str, object]:
    scan_root = resolve_scan_root(root)
    plan = build_plan(scan_root, targets)
    results = [run_item(item, verbose=False, show_warnings=False) for item in plan]
    return build_payload(scan_root, targets, plan, results)


def comparable_payload(payload: dict[str, object]) -> dict[str, object]:
    return {
        "root": payload.get("root"),
        "targets": payload.get("targets"),
        "planned": payload.get("planned"),
        "summary": payload.get("summary"),
        "warnings": payload.get("warnings"),
        "failures": payload.get("failures"),
    }


def validate_against_current(payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return ["cannot verify current generated validators without a manifest object"]
    root = payload.get("root")
    targets = payload.get("targets")
    if not isinstance(root, str) or not root:
        return ["cannot verify current generated validators without a valid root"]
    if not isinstance(targets, list) or not all(isinstance(target, str) and target in TARGETS for target in targets):
        return ["cannot verify current generated validators without valid targets"]
    current = comparable_payload(current_payload(root, targets))
    expected = comparable_payload(payload)
    errors = []
    for field in ("planned", "summary", "warnings", "failures"):
        if current.get(field) != expected.get(field):
            errors.append(f"current {field} mismatch")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="ARIADNE/RX/TREE 個別バリデータ横断ゲート")
    ap.add_argument("root", nargs="?", default="outputs/ux", help="走査ルート（既定: outputs/ux）")
    ap.add_argument("--target", action="append", choices=TARGETS, help="対象を絞る（複数回指定可）")
    ap.add_argument("--limit", type=int, help="先頭 N 件だけ実行する（動作確認用）")
    ap.add_argument("--list", action="store_true", help="実行せず、対象だけ表示する")
    ap.add_argument("--json", dest="json_path", help="検証結果を schemaVersion 付き JSON で保存")
    ap.add_argument("--fail-on-warning", action="store_true", help="WARNING が 1 件でもあれば終了コード 1 にする")
    ap.add_argument("--show-warnings", action="store_true", help="WARNING が出たファイル/グループを一行で表示する")
    ap.add_argument("--verbose", action="store_true", help="PASS した個別バリデータの出力も表示する")
    args = ap.parse_args()

    if args.limit is not None and args.limit < 1:
        print("[ERROR] --limit は 1 以上で指定してください")
        return 2

    scan_root = resolve_scan_root(args.root)
    if not scan_root.exists():
        print(f"[ERROR] 走査ルートが存在しない: {args.root}")
        return 2
    targets = args.target or list(TARGETS)
    plan = build_plan(scan_root, targets)
    if args.limit is not None:
        plan = plan[: args.limit]

    counts = summarize_plan(plan)
    print("=== generated validators ===")
    print(f"root={repo_rel(scan_root)}")
    print("targets=" + ", ".join(f"{target}={counts[target]}" for target in TARGETS if target in targets))

    if args.list:
        for item in plan:
            print(f"- {item.kind}: {item.label}")
        return 0

    totals = {target: ResultCounts() for target in TARGETS}
    results: list[ValidationResult] = []
    for item in plan:
        result = run_item(item, args.verbose, args.show_warnings)
        results.append(result)
        totals[item.kind].items += 1
        totals[item.kind].errors += result.errors
        totals[item.kind].warnings += result.warnings
        if result.return_code != 0:
            totals[item.kind].failures += 1

    if args.json_path:
        out = Path(args.json_path)
        if not out.is_absolute():
            out = ROOT / out
        payload = build_payload(scan_root, targets, plan, results)
        write_text_if_changed(out, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        print(f"json={repo_rel(out)}")

    print("\n=== summary ===")
    failures = 0
    warnings = 0
    for target in TARGETS:
        if target not in targets:
            continue
        result = totals[target]
        failures += result.failures
        warnings += result.warnings
        print(
            f"{target}: items={result.items} failures={result.failures} "
            f"errors={result.errors} warnings={result.warnings}"
        )
    if failures:
        print(f"FAIL={failures}")
        return 1
    if args.fail_on_warning and warnings:
        print(f"FAIL-WARN={warnings}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
