#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8 テンプレの a2 領域全体を {{A2_FRAME}} 化する（Phase 4-13、パターン E 応用 1 例目）。

a2 は check_template_sync.py の diff-allowed 領域、8 templates × 8 variants
（ox-grid 2 種 + slot-row 6 種）。本パッチは scripts/render.py の
render_a2(instruction_type) が返す literal （{{ANSWER}} 等 slot placeholder を
保持した完成形）を OLD として各 template から検出し、共通 NEW = {{A2_FRAME}}
に置換する。

β variant 別 OLD dispatch（Phase 4-6 TOC / Phase 4-9 pre_part_a / Phase 4-11
basis_secnav / Phase 4-12 part_a と同形）。OLD の生成元が render.py 単一であるため、
二重管理リスクなし。

byte-identical 復元の前提:
  - render.py 側 render_a2(instruction_type) が同じ instruction_type → literal
    対応で a2 HTML を組み立てる (Phase 4-13 Commit 2 で実装、全 8 templates で
    byte-identical 検証済)
  - 本スクリプトは render.py の render_a2 を直接 import して OLD を生成（
    対応表は持たず、render.py が source of truth）

dry-run:
  python scripts/upgrade_templates_a2_slot.py --dry-run
apply:
  python scripts/upgrade_templates_a2_slot.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"
sys.path.insert(0, str(ROOT / "scripts"))

from render import render_a2  # noqa: E402


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

NEW: str = "{{A2_FRAME}}"


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    results: list[tuple[str, str, str, int]] = []
    for fname, instr_type in TEMPLATE_TO_TYPE.items():
        fp = TEMPLATES_DIR / fname
        original = fp.read_text(encoding="utf-8")
        old = render_a2(instr_type)
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
    print(f"=== upgrade_templates_a2_slot.py {mode} ===")
    print(f"  NEW: {len(NEW)} chars, {NEW.count(chr(10))} newlines")
    print(f"  variants: {len(set(TEMPLATE_TO_TYPE.values()))} unique instruction_types")
    print()
    ok = sum(1 for _, _, s, _ in results if s == "OK")
    already = sum(1 for _, _, s, _ in results if s == "ALREADY")
    miss = sum(1 for _, _, s, _ in results if s == "MISS")
    total_delta = sum(d for _, _, _, d in results)
    for fname, instr_type, status, delta in results:
        sign = "+" if delta >= 0 else ""
        print(f"  {status:<8}  {fname:<{width}}  ({instr_type:<{type_w}})  bytes delta {sign}{delta}")
    print()
    print(f"  Summary: OK={ok}  ALREADY={already}  MISS={miss}  /  {len(TEMPLATE_TO_TYPE)} templates")
    print(f"  Total bytes delta: {'+' if total_delta >= 0 else ''}{total_delta}")
    if miss:
        print("  FAIL: at least one template did not match its expected variant OLD.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
