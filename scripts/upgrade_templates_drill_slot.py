#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8 テンプレの PART D drill 12 件分の literal HTML を {{DRILL_BLOCKS}} 化する（Phase 4-7）。

PART D drill section は check_template_sync.py の part_c_d sync 領域内、8 templates
完全 byte-identical (hash=672cca2605)。本パッチは全 8 同一 OLD 文字列（12 drill-block
分 = 約 96 行）を共通 NEW = {{DRILL_BLOCKS}} に置換するため sync 維持される。

byte-identical 復元の前提:
  - render.py 側 render_drill_blocks(drills) が drill_blocks 配列から同じ HTML を
    再生する（Phase 4-7 Commit 2 で実装、全 15 件で byte-identical 検証済）
  - 戻り値末尾に \\n を含めない（OLD の `    </div>` で終わり、次行は元から
    blank line + arena-scorecard のため、NEW = `{{DRILL_BLOCKS}}` の直後 \\n は
    template 側が持つ）

dry-run:
  python scripts/upgrade_templates_drill_slot.py --dry-run
apply:
  python scripts/upgrade_templates_drill_slot.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"

TEMPLATES = [
    "KTX_template.html",
    "KTX_template_ox4.html",
    "KTX_template_msel5.html",
    "KTX_template_sc5.html",
    "KTX_template_comb5.html",
    "KTX_template_fillin.html",
    "KTX_template_ox3comb8.html",
    "KTX_template_fillin8.html",
]


def build_old_drill_block(num_str: str) -> str:
    """drill-block 1 件分の literal HTML を {{DRILL_NN_*}} placeholder 込みで構築。"""
    return (
        '    <div class="drill-block">\n'
        '      <div class="drill-label">'
        '<span class="drill-num">DRILL&nbsp;' + num_str + '</span>'
        '<span class="drill-tag">{{DRILL_' + num_str + '_TAG}}</span></div>\n'
        '      <div class="self-check-quiz" data-arena="1" '
        'data-correct-value="{{DRILL_' + num_str + '_CORRECT}}" '
        'data-explanation="{{DRILL_' + num_str + '_EXPLANATION}}">\n'
        '        <div class="quiz-question">{{DRILL_' + num_str + '_QUESTION}}</div>\n'
        '        <div class="quiz-buttons">'
        '<button class="quiz-btn" type="button" '
        'data-correct="{{DRILL_' + num_str + '_O_CORRECT}}" data-value="○">○</button>'
        '<button class="quiz-btn" type="button" '
        'data-correct="{{DRILL_' + num_str + '_X_CORRECT}}" data-value="×">×</button></div>\n'
        '        <div class="quiz-answer" hidden>'
        '<span class="quiz-result"></span>{{DRILL_' + num_str + '_EXPLANATION}}</div>\n'
        '      </div>\n'
        '    </div>'
    )


# 12 drill-block × 8 lines / block + 11 blank line separators = 107 lines
OLD: str = "\n\n".join(build_old_drill_block(f"{i:02d}") for i in range(1, 13))
NEW: str = '{{DRILL_BLOCKS}}'


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    results: list[tuple[str, str, int]] = []
    for fname in TEMPLATES:
        fp = TEMPLATES_DIR / fname
        original = fp.read_text(encoding="utf-8")
        if NEW in original and OLD not in original:
            results.append((fname, "ALREADY", 0))
            continue
        if OLD not in original:
            results.append((fname, "MISS", 0))
            continue
        patched = original.replace(OLD, NEW, 1)
        size_delta = len(patched.encode("utf-8")) - len(original.encode("utf-8"))
        if not dry_run:
            fp.write_text(patched, encoding="utf-8")
        results.append((fname, "OK", size_delta))

    width = max(len(f) for f in TEMPLATES)
    mode = "[DRY-RUN]" if dry_run else "[APPLY]"
    print(f"=== upgrade_templates_drill_slot.py {mode} ===")
    print(f"  OLD: {len(OLD)} chars, {OLD.count(chr(10))} newlines")
    print(f"  NEW: {len(NEW)} chars, {NEW.count(chr(10))} newlines")
    print()
    ok = sum(1 for _, s, _ in results if s == "OK")
    already = sum(1 for _, s, _ in results if s == "ALREADY")
    miss = sum(1 for _, s, _ in results if s == "MISS")
    for fname, status, delta in results:
        sign = "+" if delta >= 0 else ""
        print(f"  {status:<8}  {fname:<{width}}  bytes delta {sign}{delta}")
    print()
    print(f"  Summary: OK={ok}  ALREADY={already}  MISS={miss}  /  {len(TEMPLATES)} templates")
    if miss:
        print("  FAIL: at least one template did not match expected OLD drill block sequence.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
