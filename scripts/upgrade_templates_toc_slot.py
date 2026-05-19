#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8 テンプレの toc-row block を {{TOC_ROW}} 化する（Phase 4-6・thin schema 派生）。

8 templates の diff-allowed `toc` 領域は 6 variants の重複を持つ。本パッチは
TEMPLATE_TO_TYPE 表 + LABELS_BY_TYPE 表で各 template に対応する variant の OLD
文字列を構築し（β variant 別 OLD dispatch）、共通 NEW = {{TOC_ROW}} に置換する。

byte-identical 復元の前提:
  - render.py 側 render_toc(instruction_type) が同じ instruction_type → labels
    対応で TOC HTML を組み立てる。本スクリプトの LABELS_BY_TYPE と render.py の
    TOC_CHOICE_LABELS_BY_TYPE が同一の対応表であることが必須。
  - 戻り値末尾に \\n を含めない（OLD の `    </div>` で終わり、次行は元から
    別 HTML 要素（`  </header>` 等）のため、NEW = `{{TOC_ROW}}` の直後 \\n は
    template 側が持つ）。

dry-run:
  python scripts/upgrade_templates_toc_slot.py --dry-run
apply:
  python scripts/upgrade_templates_toc_slot.py
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

# instruction_type → choice ラベル系列（render.py TOC_CHOICE_LABELS_BY_TYPE と同期）
LABELS_BY_TYPE: dict[str, list[str]] = {
    "ox-grid-5":               ["ア", "イ", "ウ", "エ", "オ"],
    "ox-grid-4":               ["ア", "イ", "ウ", "エ"],
    "ox-grid-3-combination-8": ["ア", "イ", "ウ"],
    "multi-select-5":          ["1", "2", "3", "4", "5"],
    "single-choice-5":         ["1", "2", "3", "4", "5"],
    "combination-5":           ["ア", "イ", "ウ", "エ", "オ"],
    "fill-in":                 ["A", "B", "C", "D", "E"],
    "fillin8":                 ["肢1", "肢2", "肢3", "肢4", "肢5"],
}

TOC_HEAD: str = (
    '    <div class="toc-row">\n'
    '      <a href="#part-a">問題文</a>\n'
    '      <a href="#answer-area">解答</a>\n'
)

TOC_TAIL: str = (
    '      <a href="#basis">共通根拠</a>\n'
    '      <a href="#c-1">体系</a>\n'
    '      <a href="#c-7">三層記憶</a>\n'
    '      <a href="#part-d">⚔ARENA</a>\n'
    '    </div>'
)

NEW: str = '{{TOC_ROW}}'


def build_old(instr_type: str) -> str:
    """指定 instruction_type 用の OLD TOC 文字列を構築。"""
    labels = LABELS_BY_TYPE[instr_type]
    choice_lines = "".join(
        f'      <a href="#choice-{i}">{lab}</a>\n'
        for i, lab in enumerate(labels, start=1)
    )
    return TOC_HEAD + choice_lines + TOC_TAIL


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    results: list[tuple[str, str, str, int]] = []  # (fname, instr_type, status, bytes_delta)
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
    print(f"=== upgrade_templates_toc_slot.py {mode} ===")
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
