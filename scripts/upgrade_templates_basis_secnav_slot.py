#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8 テンプレの basis section 第 2 行 sec-nav を {{BASIS_SECNAV}} 化する（Phase 4-11）。

basis 領域は check_template_sync.py の diff-allowed 領域、8 templates が 6 variants
(msel5+sc5 / KTX_template+comb5 が同一)。第 2 行の sec-nav 内 back-link 1 つだけが
instruction_type 別に可変。本パッチは TEMPLATE_TO_TYPE 表 + BACK_LINKS_BY_TYPE 表で
各 template に対応する variant の OLD を構築（β variant 別 OLD dispatch、Phase 4-6
TOC / Phase 4-9 pre_part_a と同形）、共通 NEW = {{BASIS_SECNAV}} に置換する。

byte-identical 復元の前提:
  - render.py 側 render_basis_secnav(instruction_type) が同じ instruction_type →
    back-link 対応で sec-nav HTML を組み立てる (Phase 4-11 Commit 2 で実装、全 15 件で
    byte-identical 検証済)
  - 本スクリプトの BACK_LINKS_BY_TYPE と render.py の BASIS_SECNAV_LINKS_BY_TYPE が
    同一の対応表であることが必須

dry-run:
  python scripts/upgrade_templates_basis_secnav_slot.py --dry-run
apply:
  python scripts/upgrade_templates_basis_secnav_slot.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"

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

# instruction_type → back-link 完成 HTML
# (render.py BASIS_SECNAV_LINKS_BY_TYPE と同期)
BACK_LINKS_BY_TYPE: dict[str, str] = {
    "ox-grid-5":               '<a href="#choice-5">↑記述オ</a>',
    "ox-grid-4":               '<a href="#choice-4">↑記述エ</a>',
    "ox-grid-3-combination-8": '<a href="#choice-3">↑記述ウ</a>',
    "multi-select-5":          '<a href="#choice-5">↑記述5</a>',
    "single-choice-5":         '<a href="#choice-5">↑記述5</a>',
    "combination-5":           '<a href="#choice-5">↑記述オ</a>',
    "fill-in":                 '<a href="#choice-5">↑空欄E</a>',
    "fillin8":                 '<a href="#choice-5">↑肢5</a>',
}

NEW: str = '{{BASIS_SECNAV}}'


def build_old(instr_type: str) -> str:
    """指定 instruction_type 用の OLD sec-nav 行を構築。"""
    back_link = BACK_LINKS_BY_TYPE[instr_type]
    return f'    <nav class="sec-nav">{back_link}<a href="#c-1">↓C-1</a></nav>'


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
    print(f"=== upgrade_templates_basis_secnav_slot.py {mode} ===")
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
