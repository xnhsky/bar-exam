#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render.py — テンプレート + JSON → HTML

templates/KTX_template.html の {{SLOT}} を problems/{id}.json の値で置換し、
outputs/tx/刑TX/刑TX{id}.html を生成する。

設計原則:
  - 未定義の {{SLOT}} が 1 つでも残ったら FAIL（黙って素通りさせない）
  - 標準ライブラリのみ依存
  - 失敗時は出力ファイルを書かない

Usage:
    python scripts/render.py <id>

例:
    python scripts/render.py 326
"""

from __future__ import annotations

import json
import re
import sys
from html import escape
from pathlib import Path


# ============================================================================
# パス設定
# ============================================================================

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "templates" / "KTX_template.html"
PROBLEMS_DIR = ROOT / "problems"
OUTPUT_DIR = ROOT / "outputs" / "tx" / "刑TX"  # legacy KEI 用（subject 未指定経路の温存）

# 科目略称 → 出力先ディレクトリ／ファイル名接頭辞 のマッピング
# （CLAUDE.md「出力先」表 + 「JX シリーズ運用ルール」と整合）
SUBJECT_TO_JP: dict[str, str] = {
    "KEI": "刑",
    "KEN": "憲",
    "MIN": "民",
    "SYO": "商",
    "MINS": "民訴",
    "KEIS": "刑訴",
    "GSE": "行政",
}

# 科目略称 → footer-spec 表示用科目ラベル（「○○法」形式）。
# template footer の <p><strong>{{JP_PREFIX}}{{PROBLEM_ID}}</strong>・{{SUBJECT_LABEL}}（...）</p>
# に注入される。
SUBJECT_TO_LABEL: dict[str, str] = {
    "KEI": "刑法",
    "KEN": "憲法",
    "MIN": "民法",
    "SYO": "商法",
    "MINS": "民事訴訟法",
    "KEIS": "刑事訴訟法",
    "GSE": "行政法",
}

# instruction_type → template path のマッピング（slotmap §5.1 §5 / §5.2 §5）
# - "ox-grid-4"      → ox4 派生 template
# - "multi-select-5" → msel5 派生 template
# - それ以外（"ox-grid-5" / 未指定 / 他値）は既存 KTX_template.html を維持
#   （デフォルト経路の防壁、326/327 への regression を防ぐ）
TEMPLATE_PATHS: dict[str, Path] = {
    "ox-grid-4": ROOT / "templates" / "KTX_template_ox4.html",
    "ox-grid-5": TEMPLATE_PATH,
    "multi-select-5": ROOT / "templates" / "KTX_template_msel5.html",
    "single-choice-5": ROOT / "templates" / "KTX_template_sc5.html",
    "combination-5": ROOT / "templates" / "KTX_template_comb5.html",
    "fill-in": ROOT / "templates" / "KTX_template_fillin.html",  # 6 本目 (slotmap §6.6)
    "ox-grid-3-combination-8": ROOT / "templates" / "KTX_template_ox3comb8.html",  # 7 本目 (slotmap §6.7)
    "fillin8": ROOT / "templates" / "KTX_template_fillin8.html",  # 8 本目 (slotmap §6.6b)
}

# combinations の set 要素を結合するときの区切り（slotmap §5.4 §5）
COMBO_SET_SEPARATOR = "・"



# ============================================================================
# PART C スタブ（Phase 2 byte-identical 維持用）
# ============================================================================
# 各 PART C セクションの内部 4 行（nav, h2, TODO comment, back-to-top）。
# part_c フィールドが未指定 / null の場合、これらが slot 値として注入され、
# 既存 14 件の出力と byte-identical を維持する。
# テンプレ patch スクリプト upgrade_templates_partc_slots.py と対応。

PART_C_STUBS: dict[str, str] = {
    "C1_SYSTEMATIC": (
        '    <nav class="sec-nav"><a href="#basis">↑共通根拠</a><a href="#c-2">↓C-2</a></nav>\n'
        '    <h2 class="section-title"><span class="sec-icon">❀</span>C-1 体系・記憶</h2>\n'
        '    <!-- TODO: Phase 2 で JSON schema 拡張、本実装 -->\n'
        '    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>'
    ),
    "C2_COMPARISON": (
        '    <nav class="sec-nav"><a href="#c-1">←C-1</a><a href="#c-3">↓C-3</a></nav>\n'
        '    <h2 class="section-title"><span class="sec-icon">❀</span>C-2 概念比較・全肢俯瞰</h2>\n'
        '    <!-- TODO: Phase 2 で JSON schema 拡張、本実装 -->\n'
        '    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>'
    ),
    "C3_CONNECTIONS": (
        '    <nav class="sec-nav"><a href="#c-2">←C-2</a><a href="#c-4">↓C-4</a></nav>\n'
        '    <h2 class="section-title"><span class="sec-icon">❀</span>C-3 関連の深い科目との接続</h2>\n'
        '    <!-- TODO: Phase 2 で JSON schema 拡張、本実装 -->\n'
        '    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>'
    ),
    "C4_DOCTRINES": (
        '    <nav class="sec-nav"><a href="#c-3">←C-3</a><a href="#c-5">↓C-5</a></nav>\n'
        '    <h2 class="section-title"><span class="sec-icon">⚔</span>C-4 学説対立</h2>\n'
        '    <!-- TODO: Phase 2 で JSON schema 拡張、本実装 -->\n'
        '    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>'
    ),
    "C5_FLOWCHART": (
        '    <nav class="sec-nav"><a href="#c-4">←C-4</a><a href="#c-6">↓C-6</a></nav>\n'
        '    <h2 class="section-title"><span class="sec-icon">🗺</span>C-5 総合フローチャート</h2>\n'
        '    <!-- TODO: Phase 2 で JSON schema 拡張、本実装 -->\n'
        '    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>'
    ),
    "C6_RELATED": (
        '    <nav class="sec-nav"><a href="#c-5">←C-5</a><a href="#c-7">↓C-7</a></nav>\n'
        '    <h2 class="section-title"><span class="sec-icon">📚</span>C-6 関連問題・出題傾向</h2>\n'
        '    <!-- TODO: Phase 2 で JSON schema 拡張、本実装 -->\n'
        '    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>'
    ),
    "C7_MEMORY": (
        '    <nav class="sec-nav"><a href="#c-6">←C-6</a><a href="#part-d">PART D→</a></nav>\n'
        '    <h2 class="section-title"><span class="sec-icon">🧠</span>C-7 三層構造記憶</h2>\n'
        '    <!-- TODO: Phase 2 で JSON schema 拡張、本実装 -->\n'
        '    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>'
    ),
}

# ============================================================================
# PART C 描画関数（Phase 2）
# ============================================================================
# 各 render_c{N}_xxx は part_c.<key> が None / 未指定なら stub を返却し、
# object が与えられた場合は構造化 HTML を組み立てて返却する。
# 全テキストフィールドは escape 適用済。`*_html` フィールドは raw HTML（inline
# strong/br/span/a を許容）として埋め込む（docs/phase2-schema-design.md §9）。

# 共通の back-to-top 末尾
_BACK_TO_TOP = '    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>'


# ============================================================================

def _render_table(table: dict | None, indent: str = "    ") -> str:
    """{title?, headers, rows[{cells, row_key?}]} を cmp-table-wrap HTML に変換。"""
    if not table:
        return ""
    parts = []
    title = table.get("title")
    if title:
        parts.append(f'{indent}<h3>{escape(title)}</h3>')
    parts.append(f'{indent}<div class="cmp-table-wrap">')
    parts.append(f'{indent}  <table>')
    headers = table.get("headers", [])
    if headers:
        ths = "".join(f"<th>{escape(h)}</th>" for h in headers)
        parts.append(f'{indent}    <thead><tr>{ths}</tr></thead>')
    parts.append(f'{indent}    <tbody>')
    for row in table.get("rows", []):
        tr_cls = ' class="row-key"' if row.get("row_key") else ""
        # cells 内は raw HTML 許容（schema 設計に基づく）
        tds = "".join(f"<td>{c}</td>" for c in row.get("cells", []))
        parts.append(f'{indent}      <tr{tr_cls}>{tds}</tr>')
    parts.append(f'{indent}    </tbody>')
    parts.append(f'{indent}  </table>')
    parts.append(f'{indent}</div>')
    return "\n".join(parts)


def render_c1_systematic(data: dict | None) -> str:
    if not data:
        return PART_C_STUBS["C1_SYSTEMATIC"]
    parts = [
        '    <nav class="sec-nav"><a href="#basis">↑共通根拠</a><a href="#c-2">C-2→</a></nav>',
        f'    <h2 class="section-title"><span class="sec-icon">❀</span>C-1 体系的解説{escape(data.get("title_suffix", ""))}</h2>',
        '',
    ]
    if data.get("subheading"):
        parts.append(f'    <h3>{escape(data["subheading"])}</h3>')
    if data.get("intro_key_phrase_html"):
        parts.append(f'    <div class="key-phrase-box">\n      {data["intro_key_phrase_html"]}\n    </div>')
    if data.get("summary_html"):
        parts.append(f'    <p>{data["summary_html"]}</p>')
    table_html = _render_table(data.get("table"))
    if table_html:
        parts.append("")
        parts.append(table_html)
    if data.get("footer_note_html"):
        parts.append(f'    <p style="font-size:.92em;">{data["footer_note_html"]}</p>')
    parts.extend(["", _BACK_TO_TOP])
    return "\n".join(parts)


def render_c2_comparison(data: dict | None) -> str:
    if not data:
        return PART_C_STUBS["C2_COMPARISON"]
    parts = [
        '    <nav class="sec-nav"><a href="#c-1">←C-1</a><a href="#c-3">C-3→</a></nav>',
        '    <h2 class="section-title"><span class="sec-icon">❀</span>C-2 概念比較・全肢俯瞰</h2>',
    ]
    for table in data.get("tables", []):
        parts.append("")
        parts.append(_render_table(table))
    parts.extend(["", _BACK_TO_TOP])
    return "\n".join(parts)


def render_c3_connections(data: dict | None) -> str:
    if not data:
        return PART_C_STUBS["C3_CONNECTIONS"]
    parts = [
        '    <nav class="sec-nav"><a href="#c-2">←C-2</a><a href="#c-4">C-4→</a></nav>',
        '    <h2 class="section-title"><span class="sec-icon">❀</span>C-3 関連の深い科目との接続</h2>',
        '',
        '    <div class="cross-grid">',
    ]
    for card in data.get("cards", []):
        parts.append('      <div class="cross-card">')
        parts.append(
            f'        <h4><span class="cc-label">{escape(card.get("label", ""))}</span>{escape(card.get("title", ""))}</h4>'
        )
        for row in card.get("rows", []):
            key = escape(row.get("key", ""))
            body = row.get("body_html", "")
            parts.append(f'        <div class="cc-row"><span class="cc-key">{key}</span>{body}</div>')
        parts.append('      </div>')
    parts.append('    </div>')
    parts.extend(["", _BACK_TO_TOP])
    return "\n".join(parts)


def render_c4_doctrines(data: dict | None) -> str:
    if not data:
        return PART_C_STUBS["C4_DOCTRINES"]
    parts = [
        '    <nav class="sec-nav"><a href="#c-3">←C-3</a><a href="#c-5">C-5→</a></nav>',
        '    <h2 class="section-title"><span class="sec-icon">⚔</span>C-4 学説対立</h2>',
    ]
    default_headers = ["学説", "結論", "論拠"]
    for topic in data.get("topics", []):
        table_for_render = {
            "title": topic.get("title"),
            "headers": topic.get("headers") or default_headers,
            "rows": topic.get("rows", []),
        }
        parts.append("")
        parts.append(_render_table(table_for_render))
    parts.extend(["", _BACK_TO_TOP])
    return "\n".join(parts)


def render_c5_flowchart(data: dict | None) -> str:
    if not data:
        return PART_C_STUBS["C5_FLOWCHART"]
    parts = [
        '    <nav class="sec-nav"><a href="#c-4">←C-4</a><a href="#c-6">C-6→</a></nav>',
        '    <h2 class="section-title"><span class="sec-icon">🗺</span>C-5 総合フローチャート</h2>',
    ]
    if data.get("intro_key_phrase_html"):
        parts.append("")
        parts.append(f'    <div class="key-phrase-box">\n      {data["intro_key_phrase_html"]}\n    </div>')
    figure = data.get("figure")
    if figure and figure.get("svg_html"):
        parts.append("")
        parts.append('    <div class="figure-wrap">')
        parts.append(f'      {figure["svg_html"]}')
        if figure.get("caption"):
            parts.append(f'      <p class="figure-caption">{escape(figure["caption"])}</p>')
        parts.append('    </div>')
    rules = data.get("rules")
    if rules and rules.get("items"):
        parts.append("")
        if rules.get("title"):
            parts.append(f'    <h3>{escape(rules["title"])}</h3>')
        parts.append('    <ul class="lead-list">')
        for item in rules["items"]:
            parts.append(f'      <li>{item}</li>')
        parts.append('    </ul>')
    parts.extend(["", _BACK_TO_TOP])
    return "\n".join(parts)


def render_c6_related(data: dict | None) -> str:
    if not data:
        return PART_C_STUBS["C6_RELATED"]
    parts = [
        '    <nav class="sec-nav"><a href="#c-5">←C-5</a><a href="#c-7">C-7→</a></nav>',
        '    <h2 class="section-title"><span class="sec-icon">📚</span>C-6 関連問題・出題傾向</h2>',
    ]
    for section_key in ("trends", "related"):
        section = data.get(section_key)
        if not section or not section.get("items"):
            continue
        parts.append("")
        if section.get("title"):
            parts.append(f'    <h3>{escape(section["title"])}</h3>')
        parts.append('    <ul class="lead-list">')
        for item in section["items"]:
            parts.append(f'      <li>{item}</li>')
        parts.append('    </ul>')
    parts.extend(["", _BACK_TO_TOP])
    return "\n".join(parts)


def render_c7_memory(data: dict | None) -> str:
    if not data:
        return PART_C_STUBS["C7_MEMORY"]
    parts = [
        '    <nav class="sec-nav"><a href="#c-6">←C-6</a><a href="#part-d">PART D→</a></nav>',
        '    <h2 class="section-title"><span class="sec-icon">🧠</span>C-7 三層構造記憶</h2>',
    ]
    if data.get("intro_key_phrase_html"):
        parts.append("")
        parts.append(f'    <div class="key-phrase-box">\n      {data["intro_key_phrase_html"]}\n    </div>')
    for layer in data.get("layers", []):
        priority = layer.get("priority", "a")
        parts.append("")
        if layer.get("title"):
            parts.append(f'    <h3>{escape(layer["title"])}</h3>')
        parts.append('    <div class="memory-list">')
        for item in layer.get("items", []):
            badge = escape(item.get("badge", ""))
            title = escape(item.get("title", ""))
            body = item.get("body_html", "")
            parts.append(f'      <div class="memory-item priority-{priority}">')
            parts.append(f'        <span class="priority-badge priority-{priority}">{badge}</span>')
            parts.append('        <div class="mem-body">')
            parts.append(f'          <span class="mem-title">{title}</span>')
            parts.append(f'          {body}')
            if item.get("hint_html"):
                parts.append(f'          <span class="mem-hint">{item["hint_html"]}</span>')
            parts.append('        </div>')
            parts.append('      </div>')
        parts.append('    </div>')
    parts.extend(["", _BACK_TO_TOP])
    return "\n".join(parts)


# ============================================================================
# 選択肢の slot 命名規約
# ============================================================================
# JSON の choices[*].label はアイウエオ。テンプレ側では A/B/C/D/E を使う。
# 例: 「ア」の stem → {{CHOICE_A_STEM}}

LABEL_TO_LETTER: dict[str, str] = {
    # ox-grid 系: カナ → A〜J
    "ア": "A", "イ": "B", "ウ": "C", "エ": "D", "オ": "E",
    "カ": "F", "キ": "G", "ク": "H", "ケ": "I", "コ": "J",
    # multi-select 系: 算用数字 → A〜E（slot 名は共通）
    "1": "A", "2": "B", "3": "C", "4": "D", "5": "E",
    # fill-in 系: 空欄ラベル A〜E (slotmap §6.6、ラベルそのまま maps to letter)
    "A": "A", "B": "B", "C": "C", "D": "D", "E": "E",
}

# 判例引用リストの結合区切り（テンプレ側で複数引用を 1 文字列として埋め込むときの区切り）
CASE_SEPARATOR = "／"


# ============================================================================
# slot 辞書の構築
# ============================================================================

def _format_answer(answer) -> str:
    """answer フィールドを HTML data-correct-value 形式に正規化する。
    - string（"12222" 等、ox-grid 系）→ そのまま
    - list（[1, 4] 等、multi-select 系）→ "1,4" にカンマ連結
      ※ K=1 の単一要素リスト（[3] 等）は末尾カンマで "3," とし、
         validate_structure の auto mode 判定が 'single' に倒れないよう担保 (multi-select-5 を維持)
    - dict（{"A": "5", "B": "7"} 等、fill-in 系）→ "A=5,B=7,C=3,..." に整形
      (slotmap §6.6 §2.4)
    - その他 → str() で文字列化"""
    if isinstance(answer, list):
        joined = ",".join(str(v) for v in answer)
        # K=1 単一要素時は末尾カンマで 'multi' mode を担保 (validate_structure 互換)
        if len(answer) == 1:
            return joined + ","
        return joined
    if isinstance(answer, dict):
        return ",".join(f"{k}={v}" for k, v in answer.items())
    return str(answer) if answer is not None else ""


def build_slot_dict(problem: dict) -> dict[str, str]:
    """problems/{id}.json から slot 名 → 値 の辞書を作る。"""
    answer_raw = problem.get("answer", "")
    answer_str = _format_answer(answer_raw)
    # multi-select 系で利用する選択数 K（answer が list の場合のみ意味あり、
    # ox-grid 系では使われないので空文字でも害なし）
    selection_count = str(len(answer_raw)) if isinstance(answer_raw, list) else ""

    # 科目判定（JSON 内 subject フィールド優先、未指定なら legacy 互換で KEI）。
    # title/doc-header/footer-spec の科目接頭辞・科目ラベルを動的に注入する。
    subject = problem.get("subject", "KEI")
    if subject not in SUBJECT_TO_JP:
        raise RuntimeError(
            f"unknown subject {subject!r}. valid: {sorted(SUBJECT_TO_JP)}"
        )
    jp_prefix = SUBJECT_TO_JP[subject] + "TX"
    subject_label = SUBJECT_TO_LABEL[subject]

    slots: dict[str, str] = {
        "PROBLEM_ID": str(problem["id"]),
        "SOURCE_ID": str(problem.get("source", "")),
        "CRIME": str(problem.get("crime", "")),
        "CHAPTER": str(problem.get("chapter", "")),
        "SECTION": str(problem.get("section", "")),
        "PAGE": str(problem.get("page", "")),
        "POINTS": str(problem.get("points", "")),
        "CORRECT_RATE": str(problem.get("correct_rate", "")),
        "INSTRUCTION": str(problem.get("instruction", "")),
        "ANSWER": answer_str,
        "ANSWER_EXPLANATION": str(problem.get("answer_explanation", "")),
        "OVERRIDE_PATTERN": str(problem.get("override_pattern", "P1")),
        "SELECTION_COUNT": selection_count,
        "JP_PREFIX": jp_prefix,
        "SUBJECT_LABEL": subject_label,
    }

    # 【事例】slot 供給（任意フィールド case.paragraphs を HTML 化）。
    # case 未定義の問題（list-form 系）では空文字列となり、テンプレ上は何も表示されない。
    case_data = problem.get("case")
    if case_data and case_data.get("paragraphs"):
        paragraphs_html = "\n".join(
            f'<p class="case-paragraph">{escape(p)}</p>'
            for p in case_data["paragraphs"]
        )
        slots["CASE_BODY"] = (
            '<div class="case-description">\n'
            + paragraphs_html
            + '\n</div>'
        )
    else:
        slots["CASE_BODY"] = ""

    # PART C slot 供給（Phase 2、任意フィールド part_c.*）。
    # part_c 未定義 / 各サブセクション未定義の場合は PART_C_STUBS が注入され、
    # 既存 14 件は byte-identical 維持。
    part_c = problem.get("part_c") or {}
    slots["C1_SYSTEMATIC"]  = render_c1_systematic(part_c.get("systematic"))
    slots["C2_COMPARISON"]  = render_c2_comparison(part_c.get("comparison"))
    slots["C3_CONNECTIONS"] = render_c3_connections(part_c.get("connections"))
    slots["C4_DOCTRINES"]   = render_c4_doctrines(part_c.get("doctrines"))
    slots["C5_FLOWCHART"]   = render_c5_flowchart(part_c.get("flowchart"))
    slots["C6_RELATED"]     = render_c6_related(part_c.get("related_problems"))
    slots["C7_MEMORY"]      = render_c7_memory(part_c.get("three_layer_memory"))

    # 【見解】slot 供給（slotmap §5.3 §8 固定 3 件方式: A/B/C）
    # views が未指定（ox-grid / multi-select / combination 系）の場合は空文字で埋める。
    # sc5 template 以外には VIEW_*_* placeholder が存在しないため無害。
    views = problem.get("views", [])
    views_by_label: dict[str, dict] = {}
    for v in views:
        lbl = v.get("label")
        if lbl in ("A", "B", "C"):
            views_by_label[lbl] = v
    for letter in ("A", "B", "C"):
        v = views_by_label.get(letter, {})
        slots[f"VIEW_{letter}_LABEL"] = str(v.get("label", ""))
        slots[f"VIEW_{letter}_BODY"] = str(v.get("body", ""))

    # PART D drill-block slot 供給（slotmap §5.5 固定 12 件方式: 01〜12）
    # drill_blocks 未指定（旧問題）の場合は全 slot に空文字。
    drills = problem.get("drill_blocks", [])
    drills_by_num: dict[str, dict] = {}
    for d in drills:
        n = d.get("num", "")
        if isinstance(n, str) and n.isdigit():
            drills_by_num[n] = d
    for i in range(1, 13):
        num_str = f"{i:02d}"
        d = drills_by_num.get(num_str, {})
        correct = d.get("correct", "")
        slots[f"DRILL_{num_str}_TAG"] = str(d.get("tag", ""))
        slots[f"DRILL_{num_str}_QUESTION"] = str(d.get("question", ""))
        slots[f"DRILL_{num_str}_CORRECT"] = str(correct)
        slots[f"DRILL_{num_str}_EXPLANATION"] = str(d.get("explanation", ""))
        # ○× ボタンの data-correct 属性値（"true"/"false"）
        slots[f"DRILL_{num_str}_O_CORRECT"] = "true" if correct == "○" else "false"
        slots[f"DRILL_{num_str}_X_CORRECT"] = "true" if correct == "×" else "false"

    # 【組合せ】slot 供給（slotmap §5.4 §5 固定 5 件、§6.7 で 8 件に拡張）
    # combinations が未指定（ox-grid / multi-select / single-choice 系）の場合は空文字。
    # comb5 / ox3comb8 template 以外には COMBO_*_* placeholder が存在しないため無害。
    combinations = problem.get("combinations", [])
    combos_by_label: dict[str, dict] = {}
    valid_combo_labels = ("1", "2", "3", "4", "5", "6", "7", "8")
    for c in combinations:
        lbl = c.get("label")
        if lbl in valid_combo_labels:
            combos_by_label[lbl] = c
    for num in valid_combo_labels:
        c = combos_by_label.get(num, {})
        slots[f"COMBO_{num}_LABEL"] = str(c.get("label", ""))
        slots[f"COMBO_{num}_SET"] = COMBO_SET_SEPARATOR.join(c.get("set", []))

    # 選択肢 slot の事前 fill (slotmap §6.6: choices < 5 件の場合に未充填 slot が
    # 残らないよう、CHOICE_A〜CHOICE_E の全 slot を空文字で初期化してから上書きする)。
    # ox-grid 系 (5 choice 必須) には影響なし、fill-in 系 (4 空欄等) で活躍。
    for letter in ("A", "B", "C", "D", "E"):
        prefix = f"CHOICE_{letter}"
        slots.setdefault(f"{prefix}_LABEL", "")
        slots.setdefault(f"{prefix}_STEM", "")
        slots.setdefault(f"{prefix}_VERDICT", "")
        slots.setdefault(f"{prefix}_VERDICT_LABEL", "")
        slots.setdefault(f"{prefix}_EXPLANATION", "")
        slots.setdefault(f"{prefix}_CASES", "")
        slots.setdefault(f"{prefix}_PROFESSOR_SUMMARY", "")
        slots.setdefault(f"{prefix}_PROFESSOR_NOTE", "")

    # 選択肢
    for choice in problem.get("choices", []):
        label = choice.get("label")
        letter = LABEL_TO_LETTER.get(label)
        if letter is None:
            continue
        prefix = f"CHOICE_{letter}"

        explanation = choice.get("explanation")
        if explanation is None:
            # null は未抽出のサイン。validate_content.py で fail させるため、
            # render では空文字ではなく明示的なマーカーを入れる。
            explanation = "<!-- EXPLANATION_NOT_EXTRACTED -->"

        slots[f"{prefix}_LABEL"] = label
        slots[f"{prefix}_STEM"] = str(choice.get("stem", ""))
        slots[f"{prefix}_VERDICT"] = str(choice.get("verdict", ""))
        slots[f"{prefix}_VERDICT_LABEL"] = str(choice.get("verdict_label", ""))
        slots[f"{prefix}_EXPLANATION"] = str(explanation)
        slots[f"{prefix}_CASES"] = CASE_SEPARATOR.join(choice.get("case_citations", []))
        # 教授の解説 sub-card (slotmap §5.6、optional)
        professor = choice.get("professor") or {}
        slots[f"{prefix}_PROFESSOR_SUMMARY"] = str(professor.get("summary", ""))
        slots[f"{prefix}_PROFESSOR_NOTE"] = str(professor.get("note", ""))

    return slots


# ============================================================================
# レンダリング
# ============================================================================

SLOT_PATTERN = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)\}\}")


def render(template: str, slots: dict[str, str]) -> str:
    """{{SLOT}} を置換する。未定義 slot が残ったら RuntimeError。"""
    # 順次置換
    out = template
    for key, value in slots.items():
        out = out.replace("{{" + key + "}}", value)

    # 未置換 slot の検出
    remaining = SLOT_PATTERN.findall(out)
    if remaining:
        unique = sorted(set(remaining))
        raise RuntimeError(
            "未定義の slot が残っています: "
            + ", ".join(f"{{{{{s}}}}}" for s in unique)
            + "\n  → problems/{id}.json の不足、または templates/KTX_template.html の slot 名を確認"
        )

    return out


# ============================================================================
# 引数 → (subject, problem_id, json_path) 解決
# ============================================================================

_ARG_RE = re.compile(r"^([A-Z]+)(\d+)$")


def resolve_arg(arg: str) -> tuple[str, str, Path]:
    """CLI 引数を (subject, problem_id, json_path) に解決する。

    後方互換:
        - 数字のみ (例: "326") → subject="KEI", problem_id=arg.zfill(3),
          json_path = problems/{problem_id}.json
    新規 (K-1 案 β):
        - 科目接頭辞 + 数字 (例: "KEN001") → subject=接頭辞, problem_id=数字.zfill(3),
          json_path = problems/{subject}{problem_id}.json
    """
    if arg.isdigit():
        problem_id = arg.zfill(3)
        return "KEI", problem_id, PROBLEMS_DIR / f"{problem_id}.json"

    m = _ARG_RE.match(arg)
    if m:
        subject = m.group(1)
        if subject not in SUBJECT_TO_JP:
            raise ValueError(
                f"unknown subject prefix: '{subject}'. "
                f"valid prefixes: {sorted(SUBJECT_TO_JP)}"
            )
        problem_id = m.group(2).zfill(3)
        return subject, problem_id, PROBLEMS_DIR / f"{subject}{problem_id}.json"

    raise ValueError(
        f"invalid argument: '{arg}'. "
        f"expected '<digits>' (legacy KEI) or '<SUBJECT><digits>' (例: KEN001)"
    )


def get_output_path(subject: str, problem_id: str) -> Path:
    """subject + problem_id から出力 HTML パスを決定する。

    KEI: outputs/tx/刑TX/刑TX{id}.html (legacy、326-330 と一致)
    他:  outputs/tx/{jp}TX/{jp}TX{id}.html
    """
    jp = SUBJECT_TO_JP[subject]
    return ROOT / "outputs" / "tx" / f"{jp}TX" / f"{jp}TX{problem_id}.html"


# ============================================================================
# エントリポイント
# ============================================================================

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    try:
        subject, problem_id, json_path = resolve_arg(argv[1])
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if not json_path.exists():
        print(f"ERROR: problem JSON not found: {json_path}", file=sys.stderr)
        return 2

    problem = json.loads(json_path.read_text(encoding="utf-8"))

    # JSON 内の subject field が指定されていれば、それが CLI 引数推定より優先される
    # （CLI 引数なし経路でも安全に動かすための保険）
    json_subject = problem.get("subject")
    if json_subject and json_subject != subject:
        if json_subject not in SUBJECT_TO_JP:
            print(
                f"ERROR: JSON 'subject'={json_subject!r} は未知。"
                f"valid: {sorted(SUBJECT_TO_JP)}",
                file=sys.stderr,
            )
            return 2
        subject = json_subject

    # instruction_type に応じて template を選択（slotmap §5.1 §5）
    instruction_type = problem.get("instruction_type")
    selected_template_path = TEMPLATE_PATHS.get(instruction_type, TEMPLATE_PATH)
    if instruction_type is None:
        print(
            f"WARN: instruction_type 未指定。デフォルト {TEMPLATE_PATH.name} を使用します。",
            file=sys.stderr,
        )

    if not selected_template_path.exists():
        print(f"ERROR: template not found: {selected_template_path}", file=sys.stderr)
        return 2

    template = selected_template_path.read_text(encoding="utf-8")

    slots = build_slot_dict(problem)

    try:
        rendered = render(template, slots)
    except RuntimeError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1

    output_path = get_output_path(subject, problem_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    print(
        f"OK: {output_path} ({len(rendered):,} bytes) "
        f"(subject={subject}, template={selected_template_path.name}, "
        f"instruction_type={instruction_type or 'unset'})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
