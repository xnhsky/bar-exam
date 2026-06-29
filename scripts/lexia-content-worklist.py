#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 HTML 内容改善セッション向け worklist を作る。

check-lexia-sync-contract.py の判定を再利用し、Lexia 同期で気になる対象を
JX/TX/RX コード単位にまとめる。read-only。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_SCRIPT = ROOT / "scripts" / "check-lexia-sync-contract.py"
DEFAULT_ROOTS = ("outputs", "references")
CONTENT_PREFLIGHT_CMD = r"python scripts\check-lexia-preflight.py --allow-untracked-sync-artifacts"
SCHEMA_VERSION = "lexia-content-worklist/v1"
ITEM_JSON_FIELDS = (
    "target",
    "severity",
    "kind",
    "category",
    "path",
    "message",
    "action",
    "validators",
)
FAIL_LEVELS = {
    "error": {"ERROR"},
    "warn": {"ERROR", "WARN"},
    "todo": {"ERROR", "WARN", "TODO"},
    "any": {"ERROR", "WARN", "TODO"},
}


@dataclass
class WorkItem:
    target: str
    severity: str
    kind: str
    category: str
    path: str
    message: str
    action: str
    validators: list[str]


def write_text_if_changed(path: Path, text: str) -> bool:
    try:
        if path.exists() and path.read_text(encoding="utf-8") == text:
            return False
    except OSError:
        pass
    path.write_text(text, encoding="utf-8")
    return True


def load_contract_module():
    spec = importlib.util.spec_from_file_location("check_lexia_sync_contract", CONTRACT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CONTRACT_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def code_sort_key(contract, code: str):
    key = contract.code_key(code)
    return key if key is not None else ("", "", 10**9, None)


def target_from_path_or_message(contract, path: str, message: str = "") -> str:
    for text in (path, message):
        key = contract.code_key(text)
        if key is not None:
            prefix, typ, num, suffix = key
            if typ == "RX":
                return f"{prefix}JX{num:03d}" if suffix is not None else f"{prefix}{typ}{num:03d}"
            return f"{prefix}{typ}{num:03d}"
    return path or "GLOBAL"


def action_for(kind: str, message: str) -> str:
    if "ARIADNE 欠落" in message:
        return "対応 ARIADNE を生成/復元し、data-athena-code と data-rx を確認"
    if "TREE 欠落" in message:
        return "対応 TREE を生成/復元し、JX 本体との baseCode 一致を確認"
    if "data-rx" in message and "重複" in message:
        return "ARIADNE 想起カードの data-rx 割当を確認し、必要なら対応 RX へ振り分け"
    if "RX" in message and ("不在" in message or "dangling" in message):
        return "ARIADNE data-rx と RX 実ファイルの対応を修正"
    if "本文不足" in message:
        return "本文生成漏れ/テンプレート崩れを確認して再生成または補修"
    if "title" in message or "ID" in message or "code" in message or "fileName" in message:
        return "title/code/fileName/header/footer の一致を修正"
    if kind == "QUARANTINED":
        return "隔離理由を確認し、正規出力は生成パイプラインから再生成"
    return "対象 HTML を確認し、Lexia 同期メタと本文品質を補修"


def validators_for(item_target: str, category: str, path: str, message: str = "") -> list[str]:
    validators = []
    win_path = path.replace("/", "\\")
    if category == "JX" and path.endswith(".html"):
        validators.append(f"python scripts\\validate-jx.py {win_path}")
    if category == "ARIADNE" and path.endswith(".html"):
        validators.append(f"python scripts\\validate-ariadne.py {win_path}")
    if category == "TREE" and path.endswith(".html"):
        validators.append(f"python scripts\\validate-tree.py {win_path}")
    parts = path.split("/")
    if category == "JX" and len(parts) >= 4 and parts[:2] == ["outputs", "001_JX"]:
        subject_dir = parts[2]
        if "ARIADNE 欠落" in message:
            expected = f"outputs\\ux\\001_ARIADNE\\{subject_dir}\\{item_target}_ARIADNE.html"
            validators.append(f"python scripts\\validate-ariadne.py {expected}")
        if "TREE 欠落" in message:
            expected = f"outputs\\ux\\003_TREE\\{subject_dir}\\{item_target}_TREE.html"
            validators.append(f"python scripts\\validate-tree.py {expected}")
    validators.append(CONTENT_PREFLIGHT_CMD)
    return validators


def inferred_validators_for_target(contract, item_target: str, path: str) -> list[str]:
    key = contract.code_key(item_target)
    if key is None:
        return [CONTENT_PREFLIGHT_CMD]
    parts = path.split("/")
    subject_dir = ""
    if len(parts) >= 3 and parts[0] == "outputs" and parts[1] in {"000_TX", "001_JX"}:
        subject_dir = parts[2]
    elif len(parts) >= 4 and parts[:2] == ["outputs", "ux"]:
        subject_dir = parts[3]

    prefix, typ, num, _suffix = key
    code = f"{prefix}{typ}{num:03d}"
    validators = []
    if subject_dir and typ == "JX":
        validators.extend([
            f"python scripts\\validate-jx.py outputs\\001_JX\\{subject_dir}\\{code}.html",
            f"python scripts\\validate-ariadne.py outputs\\ux\\001_ARIADNE\\{subject_dir}\\{code}_ARIADNE.html",
            f"python scripts\\validate-tree.py outputs\\ux\\003_TREE\\{subject_dir}\\{code}_TREE.html",
        ])
    elif subject_dir and typ == "TX":
        validators.extend([
            f"python scripts\\validate-tx.py outputs\\000_TX\\{subject_dir}\\{code}.html",
            f"python scripts\\validate-tx-core.py outputs\\ux\\000_TX\\{subject_dir}\\{code}_lex.html",
        ])
    validators.append(CONTENT_PREFLIGHT_CMD)
    return validators


def collect_contract_items(contract, roots: Iterable[str]) -> list[WorkItem]:
    files = contract.collect_files(roots)
    entries = []
    per_file = []
    for path in files:
        entry, errors, warnings = contract.audit_entry(path)
        if entry:
            entries.append(entry)
        per_file.append((path, entry, errors, warnings))

    items: list[WorkItem] = []
    for path, entry, errors, warnings in per_file:
        rel = contract.relpath(path)
        target = entry.baseCode if entry else target_from_path_or_message(contract, rel)
        category = entry.category if entry else "UNCLASSIFIED"
        for msg in errors:
            items.append(WorkItem(
                target=target,
                severity="ERROR",
                kind="FILE",
                category=category,
                path=rel,
                message=msg,
                action=action_for("FILE", msg),
                validators=validators_for(target, category, rel, msg),
            ))
        for msg in warnings:
            items.append(WorkItem(
                target=target,
                severity="WARN",
                kind="FILE",
                category=category,
                path=rel,
                message=msg,
                action=action_for("FILE", msg),
                validators=validators_for(target, category, rel, msg),
            ))

    by_category: dict[str, set[str]] = defaultdict(set)
    by_target_path: dict[tuple[str, str], str] = {}
    for e in entries:
        by_category[e.category].add(e.baseCode)
        by_target_path[(e.category, e.baseCode)] = e.sourcePath

    def add_global(target: str, category: str, message: str) -> None:
        path = by_target_path.get((category, target), "")
        items.append(WorkItem(
            target=target,
            severity="WARN",
            kind="MISSING",
            category=category,
            path=path,
            message=message,
            action=action_for("MISSING", message),
            validators=validators_for(target, category, path, message),
        ))

    official_tx = by_category["TX_OFFICIAL"]
    lexia_tx = by_category["TX_LEXIA"]
    for target in sorted(official_tx - lexia_tx, key=lambda c: code_sort_key(contract, c)):
        add_global(target, "TX_OFFICIAL", "TX _lex 欠落")
    for target in sorted(lexia_tx - official_tx, key=lambda c: code_sort_key(contract, c)):
        add_global(target, "TX_LEXIA", "TX 公式 HTML 欠落")

    jx = by_category["JX"]
    ariadne = by_category["ARIADNE"]
    tree = by_category["TREE"]
    rx_bases = by_category["RX"]
    for target in sorted(jx - ariadne, key=lambda c: code_sort_key(contract, c)):
        add_global(target, "JX", "JX 対応 ARIADNE 欠落")
    for target in sorted(jx - tree, key=lambda c: code_sort_key(contract, c)):
        add_global(target, "JX", "JX 対応 TREE 欠落")
    for target in sorted(ariadne - jx, key=lambda c: code_sort_key(contract, c)):
        add_global(target, "ARIADNE", "JX 本体が無い ARIADNE")
    for target in sorted(tree - jx, key=lambda c: code_sort_key(contract, c)):
        add_global(target, "TREE", "JX 本体が無い TREE")
    for target in sorted(rx_bases - jx, key=lambda c: code_sort_key(contract, c)):
        add_global(target, "RX", "JX 本体が無い RX")
    return items


def collect_failed_items(contract) -> list[WorkItem]:
    items: list[WorkItem] = []
    outputs = ROOT / "outputs"
    if not outputs.is_dir():
        return items
    for path in sorted(outputs.rglob("*.html")):
        if "_failed" not in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        target = target_from_path_or_message(contract, rel)
        items.append(WorkItem(
            target=target,
            severity="TODO",
            kind="QUARANTINED",
            category="FAILED",
            path=rel,
            message="隔離済み HTML が残っている",
            action=action_for("QUARANTINED", ""),
            validators=inferred_validators_for_target(contract, target, rel),
        ))
    return items


def dedupe(items: list[WorkItem]) -> list[WorkItem]:
    seen = set()
    out = []
    for item in items:
        key = (item.target, item.severity, item.kind, item.category, item.path, item.message)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def priority_key(contract, item: WorkItem):
    sev = {"ERROR": 0, "WARN": 1, "TODO": 2}.get(item.severity, 9)
    return (sev, code_sort_key(contract, item.target), item.kind, item.category, item.path, item.message)


def is_preflight_cmd(command: str) -> bool:
    return command.startswith(r"python scripts\check-lexia-preflight.py")


def filter_targets(items: list[WorkItem], targets: Iterable[str]) -> list[WorkItem]:
    wanted = {t.strip() for t in targets if t.strip()}
    if not wanted:
        return items
    return [item for item in items if item.target in wanted]


def failing_items(items: list[WorkItem], fail_on: str | None) -> list[WorkItem]:
    if not fail_on:
        return []
    levels = FAIL_LEVELS[fail_on]
    return [item for item in items if item.severity in levels]


def item_to_json(item: WorkItem) -> dict[str, object]:
    raw = asdict(item)
    return {field: raw[field] for field in ITEM_JSON_FIELDS}


def items_json(items: Iterable[WorkItem]) -> list[dict[str, object]]:
    return [item_to_json(item) for item in items]


def normalized_target_filter(targets: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(t.strip() for t in targets if t.strip()))


def build_worklist_payload(
    contract,
    roots: Iterable[str],
    items: list[WorkItem],
    target_filter: Iterable[str] = (),
    include_failed: bool = True,
) -> dict[str, object]:
    counts = Counter(item.severity for item in items)
    targets = sorted({item.target for item in items}, key=lambda c: code_sort_key(contract, c))
    categories = Counter(item.category for item in items)
    kinds = Counter(item.kind for item in items)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "roots": list(roots),
        "filters": {
            "target": normalized_target_filter(target_filter),
            "includeFailed": include_failed,
        },
        "targets": len(targets),
        "counts": {severity: counts.get(severity, 0) for severity in ("ERROR", "WARN", "TODO")},
        "categories": {key: categories[key] for key in sorted(categories)},
        "kinds": {key: kinds[key] for key in sorted(kinds)},
        "items": items_json(items),
    }


def render_markdown(contract, items: list[WorkItem], generated_at: str = "") -> str:
    counts = Counter(item.severity for item in items)
    grouped: dict[str, list[WorkItem]] = defaultdict(list)
    for item in sorted(items, key=lambda x: priority_key(contract, x)):
        grouped[item.target].append(item)

    lines = [
        "# Lexia Content Worklist",
        "",
        f"- targets: {len(grouped)}",
        f"- ERROR: {counts.get('ERROR', 0)}",
        f"- WARN: {counts.get('WARN', 0)}",
        f"- TODO: {counts.get('TODO', 0)}",
        "",
    ]
    if generated_at:
        lines.insert(2, f"- generated: {generated_at}")
    if not items:
        lines.append("No content work items.")
        lines.append("")
        return "\n".join(lines)

    for target in sorted(grouped, key=lambda c: code_sort_key(contract, c)):
        target_items = grouped[target]
        lines.append(f"## {target}")
        for item in target_items:
            location = f" `{item.path}`" if item.path else ""
            lines.append(f"- **{item.severity} / {item.kind} / {item.category}**{location}: {item.message}")
            lines.append(f"  - action: {item.action}")
        validators = []
        for item in target_items:
            validators.extend(item.validators)
        validators = list(dict.fromkeys(validators))
        preflight = [v for v in validators if is_preflight_cmd(v)]
        validators = [v for v in validators if not is_preflight_cmd(v)] + preflight
        if validators:
            lines.append("  - validators:")
            for cmd in validators:
                lines.append(f"    - `{cmd}`")
        lines.append("")
    return "\n".join(lines)


def prompt_scope(contract, target: str, items: list[WorkItem]) -> list[str]:
    paths = [item.path for item in items if item.path]
    subject_dir = ""
    for path in paths:
        parts = path.split("/")
        if len(parts) >= 3 and parts[0] == "outputs" and parts[1] in {"000_TX", "001_JX"}:
            subject_dir = parts[2]
            break
        if len(parts) >= 4 and parts[:2] == ["outputs", "ux"]:
            subject_dir = parts[3]
            break

    key = contract.code_key(target)
    scopes = list(dict.fromkeys(paths))
    if key is None:
        return scopes

    prefix, typ, num, _suffix = key
    code = f"{prefix}{typ}{num:03d}"
    if typ == "JX" and subject_dir:
        scopes.extend([
            f"outputs/001_JX/{subject_dir}/{code}.html",
            f"outputs/ux/001_ARIADNE/{subject_dir}/{code}_ARIADNE.html",
            f"outputs/ux/002_RX/{subject_dir}/{code}/{prefix}RX{num:03d}_*.html",
            f"outputs/ux/003_TREE/{subject_dir}/{code}_TREE.html",
        ])
    elif typ == "TX" and subject_dir:
        scopes.extend([
            f"outputs/000_TX/{subject_dir}/{code}.html",
            f"outputs/ux/000_TX/{subject_dir}/{code}_lex.html",
        ])
    return list(dict.fromkeys(scopes))


def render_prompt(contract, target: str, items: list[WorkItem]) -> str:
    validators = []
    for item in items:
        validators.extend(item.validators)
    validators = list(dict.fromkeys(validators))
    preflight = [v for v in validators if is_preflight_cmd(v)]
    validators = [v for v in validators if not is_preflight_cmd(v)] + preflight
    scopes = prompt_scope(contract, target, items)

    lines = [
        f"# {target} 内容改善セッション",
        "",
        r"作業リポジトリ: `C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam`",
        "",
        "## 制約",
        "",
        "- bar-exam だけ触る。Lexia リポジトリは触らない。",
        "- push/deploy はしない。",
        "- destructive command は使わない。",
        "- scripts/ は原則触らない。生成ファイル内容改善に集中する。",
        "- 同じ target 以外の生成ファイルは編集しない。",
        "",
        "## 対象",
        "",
        f"- target: `{target}`",
    ]
    if scopes:
        lines.append("- 編集候補:")
        for scope in scopes:
            lines.append(f"  - `{scope}`")
    lines.extend([
        "",
        "## 検出事項",
        "",
    ])
    for item in items:
        location = f" `{item.path}`" if item.path else ""
        lines.append(f"- **{item.severity} / {item.kind} / {item.category}**{location}: {item.message}")
        lines.append(f"  - action: {item.action}")
    lines.extend([
        "",
        "## 作業方針",
        "",
        "- title / code / fileName / subject / category / footer / data-athena-code / data-rx を壊さない。",
        "- 既存 HTML のコピーで別問題を作らない。必要なら生成パイプラインから再生成する。",
        "- ARIADNE を触る場合は対応 RX 実ファイルと `data-rx` の整合を確認する。",
        "- TREE を触る場合は JX 本体との baseCode 一致と `validate-tree.py` を確認する。",
        "- 子セッションでは未追跡生成物を許す preflight を使う。親セッション/最終同期では allow なしで再確認する。",
        "",
        "## 必須検証",
        "",
    ])
    for cmd in validators:
        lines.append(f"- `{cmd}`")
    lines.extend([
        "",
        "## 報告フォーマット",
        "",
        "```text",
        "対象:",
        "変更ファイル:",
        "改善内容:",
        "検証結果:",
        "残 WARN / 残課題:",
        "親セッションで確認してほしい点:",
        "```",
        "",
    ])
    return "\n".join(lines)


def write_prompts(contract, items: list[WorkItem], out_dir: Path) -> list[Path]:
    grouped: dict[str, list[WorkItem]] = defaultdict(list)
    for item in sorted(items, key=lambda x: priority_key(contract, x)):
        grouped[item.target].append(item)
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = {path for path in out_dir.glob("*_content_prompt.md") if path.is_file()}
    written = []
    for target in sorted(grouped, key=lambda c: code_sort_key(contract, c)):
        safe = re.sub(r"[^\w.-]+", "_", target, flags=re.UNICODE).strip("_") or "target"
        path = out_dir / f"{safe}_content_prompt.md"
        write_text_if_changed(path, render_prompt(contract, target, grouped[target]))
        written.append(path)
    for stale in sorted(existing - set(written)):
        stale.unlink()
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description="Lexia 生成 HTML 内容改善 worklist を作る")
    ap.add_argument("roots", nargs="*", default=list(DEFAULT_ROOTS), help="走査ルート（既定: outputs references）")
    ap.add_argument("--json", dest="json_path", help="worklist を JSON で保存")
    ap.add_argument(
        "--json-format",
        choices=("items", "manifest"),
        default="items",
        help="--json の出力形式（items: 既存互換 list / manifest: schemaVersion 付き object）",
    )
    ap.add_argument("--markdown", dest="markdown_path", help="worklist を Markdown で保存")
    ap.add_argument("--prompts-dir", help="target ごとの子セッション用プロンプトを保存するディレクトリ")
    ap.add_argument("--target", action="append", default=[], help="指定 target だけ出力（複数回指定可）")
    ap.add_argument("--fail-on", choices=sorted(FAIL_LEVELS), help="指定 severity 以上の item があれば exit 1（error/warn/todo/any）")
    ap.add_argument("--timestamp", action="store_true", help="Markdown に現在時刻の generated 行を入れる（既定は安定出力）")
    ap.add_argument("--generated-at", help="Markdown に固定の generated 行を入れる")
    ap.add_argument("--no-failed", action="store_true", help="outputs/**/_failed/*.html を TODO に含めない")
    ap.add_argument("--quiet", action="store_true", help="Markdown を stdout に出さない")
    args = ap.parse_args()

    if args.json_format != "items" and not args.json_path:
        print("[ERROR] --json-format は --json と一緒に指定してください", file=sys.stderr)
        return 2

    contract = load_contract_module()
    items = collect_contract_items(contract, args.roots)
    if not args.no_failed:
        items.extend(collect_failed_items(contract))
    items = dedupe(items)
    items = filter_targets(items, args.target)
    items = sorted(items, key=lambda x: priority_key(contract, x))

    if args.json_path:
        out = ROOT / args.json_path
        out.parent.mkdir(parents=True, exist_ok=True)
        payload: object
        if args.json_format == "manifest":
            payload = build_worklist_payload(
                contract,
                args.roots,
                items,
                target_filter=args.target,
                include_failed=not args.no_failed,
            )
        else:
            payload = items_json(items)
        write_text_if_changed(out, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    generated_at = args.generated_at or (datetime.now().astimezone().isoformat(timespec="seconds") if args.timestamp else "")
    md = render_markdown(contract, items, generated_at=generated_at)
    if args.markdown_path:
        out = ROOT / args.markdown_path
        out.parent.mkdir(parents=True, exist_ok=True)
        write_text_if_changed(out, md)
    if args.prompts_dir:
        write_prompts(contract, items, ROOT / args.prompts_dir)
    if not args.quiet:
        print(md)
    blockers = failing_items(items, args.fail_on)
    if blockers:
        counts = Counter(item.severity for item in blockers)
        print(
            "worklist gate failed: "
            + ", ".join(f"{severity}={counts[severity]}" for severity in ("ERROR", "WARN", "TODO") if counts.get(severity)),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
