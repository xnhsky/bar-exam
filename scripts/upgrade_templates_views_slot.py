#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KTX_template_sc5.html の【見解】ブロックを {{VIEWS_BLOCK}} slot 化する（Phase 4-1）。

PART A 内の views section は 8 templates 中 sc5 にのみ存在する diff-allowed 領域。
本パッチは sc5 単独で完結し、check_template_sync の sync-required セクションには
触れない（part_a は元々 [8 variants] 許容）。

byte-identical 復元の前提:
  - 329（views 3 件 present）→ render_views_block が原ブロックと同一の文字列を返す
  - 300 / その他 non-sc5（views 未定義）→ render_views_block が "" を返し、
    PART A の【見解】H3 + section ごと出力から消える（gold 300 と一致）

dry-run:
  python scripts/upgrade_templates_views_slot.py --dry-run
apply:
  python scripts/upgrade_templates_views_slot.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "KTX_template_sc5.html"

# 削除対象ブロック: `    {{CASE_BODY}}` 行末から `    <h3 ...>【記述】</h3>` 行頭までの間。
# 含まれる要素:
#   - 直前の空行（CASE_BODY と【見解】H3 の間）
#   - 【見解】H3 行
#   - 空行
#   - <section class="views-section" id="part-a-views"> 開タグ
#   - <div class="view-block"> × 3（VIEW_A/B/C の LABEL/BODY placeholder 入り）
#   - </section> 閉タグ
#   - 直後の空行（</section> と【記述】H3 の間）
# 合計: \n × 2（surrounding blanks）+ 16 lines (H3 + blank + section open + 12 view lines + section close)
OLD = (
    '\n'
    '\n'
    '    <h3 style="background:transparent; border-left:none; padding:8px 0 4px 0; margin:20px 0 8px 0; border-bottom:2px dotted var(--border-mid); color:var(--accent); font-family:var(--font-display);">【見解】</h3>\n'
    '\n'
    '    <section class="views-section" id="part-a-views">\n'
    '      <div class="view-block">\n'
    '        <span class="view-label">{{VIEW_A_LABEL}}</span>\n'
    '        <p class="view-body">{{VIEW_A_BODY}}</p>\n'
    '      </div>\n'
    '      <div class="view-block">\n'
    '        <span class="view-label">{{VIEW_B_LABEL}}</span>\n'
    '        <p class="view-body">{{VIEW_B_BODY}}</p>\n'
    '      </div>\n'
    '      <div class="view-block">\n'
    '        <span class="view-label">{{VIEW_C_LABEL}}</span>\n'
    '        <p class="view-body">{{VIEW_C_BODY}}</p>\n'
    '      </div>\n'
    '    </section>\n'
    '\n'
)

# 置換結果: 単一行 {{VIEWS_BLOCK}} + 行末 newline + 直後の空行を 1 つ復元。
# `    {{CASE_BODY}}` の行末 \n の直後にこの NEW が来て、その直後に
# `    <h3 ...>【記述】</h3>` が続く形に再構成される。
NEW = '\n{{VIEWS_BLOCK}}\n'


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    text = TEMPLATE.read_text(encoding="utf-8")
    if NEW in text and OLD not in text:
        print(f"  ALREADY  {TEMPLATE.name}: slot already present")
        return 0
    if OLD not in text:
        print(f"  MISS     {TEMPLATE.name}: expected views block not found")
        return 1
    new_text = text.replace(OLD, NEW, 1)
    delta = len(new_text.encode("utf-8")) - len(text.encode("utf-8"))
    mode = "[DRY-RUN]" if dry_run else "[APPLY]"
    print(f"=== upgrade_templates_views_slot.py {mode} ===")
    print(f"  OLD: {len(OLD)} chars, {OLD.count(chr(10))} newlines")
    print(f"  NEW: {len(NEW)} chars, {NEW.count(chr(10))} newlines")
    print(f"  OK       {TEMPLATE.name}: bytes delta {delta:+d}")
    if not dry_run:
        TEMPLATE.write_text(new_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
