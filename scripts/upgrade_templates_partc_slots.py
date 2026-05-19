#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8 テンプレの PART C スタブを slot 化する（Phase 2）。

各 <section class="section" id="c-N">...</section> の内部 4 行（nav, h2, TODO comment,
back-to-top）を 1 行の {{CN_SLOT}} に置換。template が同期義務セクション (part_c_d)
内なので 8 本同一パッチで check_template_sync 維持。
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

# (section_id, slot_name, prev_link, next_link, sec_icon, title)
SECTIONS = [
    ("c-1", "C1_SYSTEMATIC",  "basis",   "c-2",     "❀", "C-1 体系・記憶"),
    ("c-2", "C2_COMPARISON",  "c-1",     "c-3",     "❀", "C-2 概念比較・全肢俯瞰"),
    ("c-3", "C3_CONNECTIONS", "c-2",     "c-4",     "❀", "C-3 関連の深い科目との接続"),
    ("c-4", "C4_DOCTRINES",   "c-3",     "c-5",     "⚔", "C-4 学説対立"),
    ("c-5", "C5_FLOWCHART",   "c-4",     "c-6",     "🗺", "C-5 総合フローチャート"),
    ("c-6", "C6_RELATED",     "c-5",     "c-7",     "📚", "C-6 関連問題・出題傾向"),
    ("c-7", "C7_MEMORY",      "c-6",     "part-d",  "🧠", "C-7 三層構造記憶"),
]


def build_old(section_id, prev_link, next_link, sec_icon, title):
    """既存スタブの 6 行ブロック（section open〜close）。"""
    # c-1 は prev へのリンクが #basis、矢印は ↑共通根拠
    # c-2〜c-7 は prev へ ←C-N
    # next は ↓C-N（c-7 は PART D→）
    prev_label = "↑共通根拠" if prev_link == "basis" else f"←C-{prev_link.split('-')[1]}"
    next_label = "PART D→" if next_link == "part-d" else f"↓C-{next_link.split('-')[1]}"
    return (
        f'  <section class="section" id="{section_id}">\n'
        f'    <nav class="sec-nav"><a href="#{prev_link}">{prev_label}</a><a href="#{next_link}">{next_label}</a></nav>\n'
        f'    <h2 class="section-title"><span class="sec-icon">{sec_icon}</span>{title}</h2>\n'
        f'    <!-- TODO: Phase 2 で JSON schema 拡張、本実装 -->\n'
        f'    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>\n'
        f'  </section>'
    )


def build_new(section_id, slot_name):
    """slot 化後の 3 行ブロック（section open + slot + close）。"""
    return (
        f'  <section class="section" id="{section_id}">\n'
        f'{{{{{slot_name}}}}}\n'
        f'  </section>'
    )


def main() -> int:
    for fname in TEMPLATES:
        fp = TEMPLATES_DIR / fname
        h = fp.read_text(encoding="utf-8")
        applied = 0
        for section_id, slot_name, prev_link, next_link, sec_icon, title in SECTIONS:
            old = build_old(section_id, prev_link, next_link, sec_icon, title)
            new = build_new(section_id, slot_name)
            if old in h:
                h = h.replace(old, new, 1)
                applied += 1
            elif new in h:
                # Already patched
                pass
            else:
                print(f"  MISS {fname}: section {section_id} stub not found")
                return 1
        if applied:
            fp.write_text(h, encoding="utf-8")
            print(f"  OK   {fname}: {applied}/{len(SECTIONS)} sections slot 化")
        else:
            print(f"  SKIP {fname} (already slotified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
