#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8 テンプレの pre_part_a 領域 (4 lines / 194-237 bytes) を {{PRE_PART_A}} 化する（Phase 4-9）。

pre_part_a は check_template_sync.py の diff-allowed 領域、8 templates が 8 variants で
完全 1:1 対応。各 variant は HTML コメント内の form 名文字列のみが可変。本パッチは
TEMPLATE_TO_TYPE 表 + FORM_NAMES_BY_TYPE 表で各 template に対応する variant の OLD を
構築し（β variant 別 OLD dispatch、Phase 4-6 TOC と同形）、共通 NEW = {{PRE_PART_A}}
に置換する。

byte-identical 復元の前提:
  - render.py 側 render_pre_part_a(instruction_type) が同じ instruction_type → form 名
    対応で pre_part_a HTML を組み立てる (Phase 4-9 Commit 2 で実装、全 15 件で
    byte-identical 検証済)
  - 本スクリプトの FORM_NAMES_BY_TYPE と render.py の PRE_PART_A_FORM_NAMES_BY_TYPE が
    同一の対応表であることが必須

dry-run:
  python scripts/upgrade_templates_pre_part_a_slot.py --dry-run
apply:
  python scripts/upgrade_templates_pre_part_a_slot.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"

# 8 templates → instruction_type の対応
TEMPLATE_TO_TYPE: dict[str, str] = {
    "KTX_template.html":          "ox-grid-5",
    "KTX_template_ox4.html":      "ox-grid-4",
    "KTX_template_msel5.html":    "multi-select-5",
    "KTX_template_sc5.html":      "single-choice-5",
    "KTX_template_comb5.html":    "combination-5",
    "KTX_template_fillin.html":   "fill-in",
    "KTX_template_ox3comb8.html": "ox-grid-3-combination-8",
    "KTX_template_fillin8.html":  "fillin8",
}

# instruction_type → form 名（render.py PRE_PART_A_FORM_NAMES_BY_TYPE と同期）
# fillin8 のコロン「：」は全角 (U+FF1A) — template と byte-identical 保証のため変更厳禁
FORM_NAMES_BY_TYPE: dict[str, str] = {
    "ox-grid-5":               "ox-grid-5 形式",
    "ox-grid-4":               "ox-grid-4 形式",
    "ox-grid-3-combination-8": "ox-grid-3 + combination-8 形式",
    "multi-select-5":          "multi-select-5 形式",
    "single-choice-5":         "single-choice-5 形式",
    "combination-5":           "combination-5 形式",
    "fill-in":                 "fill-in 形式",
    "fillin8":                 "fillin8 形式：8 blanks 表示 + 5 options 単一選択",
}

NEW: str = '{{PRE_PART_A}}'


def build_old(instr_type: str) -> str:
    """指定 instruction_type 用の OLD pre_part_a 文字列を構築。"""
    form_name = FORM_NAMES_BY_TYPE[instr_type]
    return (
        '\n'
        '  <!-- ============================================================\n'
        f'       PART A ── 問題情報（{form_name}）\n'
        '       ============================================================ -->'
    )


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    results: list[tuple[str, str, str, int]] = []
    for fname, instr_type in TEMPLATE_TO_TYPE.items():
        fp = TEMPLATES_DIR / fname
        original = fp.read_text(encoding="utf-8")
        old = build_old(instr_type)
        if NEW in original and old not in original:
            results.append((fname, instr_type, "ALREADY", 0))
            continue
        if old not in original:
            results.append((fname, instr_type, "MISS", 0))
            continue
        patched = original.replace(old, NEW, 1)
        size_delta = len(patched.encode("utf-8")) - len(original.encode("utf-8"))
        if not dry_run:
            fp.write_text(patched, encoding="utf-8")
        results.append((fname, instr_type, "OK", size_delta))

    width = max(len(f) for f in TEMPLATE_TO_TYPE)
    type_w = max(len(t) for t in TEMPLATE_TO_TYPE.values())
    mode = "[DRY-RUN]" if dry_run else "[APPLY]"
    print(f"=== upgrade_templates_pre_part_a_slot.py {mode} ===")
    print(f"  NEW: {len(NEW)} chars, {NEW.count(chr(10))} newlines")
    print(f"  variants: {len(set(TEMPLATE_TO_TYPE.values()))} unique instruction_types, "
          f"{len({build_old(t) for t in TEMPLATE_TO_TYPE.values()})} unique OLDs")
    print()
    ok = sum(1 for _, _, s, _ in results if s == "OK")
    already = sum(1 for _, _, s, _ in results if s == "ALREADY")
    miss = sum(1 for _, _, s, _ in results if s == "MISS")
    for fname, instr_type, status, delta in results:
        sign = "+" if delta >= 0 else ""
        print(f"  {status:<8}  {fname:<{width}}  ({instr_type:<{type_w}})  bytes delta {sign}{delta}")
    print()
    print(f"  Summary: OK={ok}  ALREADY={already}  MISS={miss}  /  {len(TEMPLATE_TO_TYPE)} templates")
    if miss:
        print("  FAIL: at least one template did not match its expected variant OLD.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
