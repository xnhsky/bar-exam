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

# PART B basis スタブ（Phase 3-2 で導入）。
# basis フィールドが None / 未指定 / cards 空 の場合、{{BASIS_CARDS}} slot に
# このリテラルが注入され、既存 14 件 byte-identical を維持する。
# テンプレ patch スクリプト upgrade_templates_basis_slot.py と対応。
BASIS_STUB: str = '    <!-- TODO: Phase 2 で JSON schema 拡張、本実装 -->'


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
# PART B basis 描画関数（Phase 3-3）
# ============================================================================
# basis フィールドが None / 未指定 / cards 空 の場合は BASIS_STUB を返却。
# dict が与えられた場合は schema 準拠の構造化 basis-card HTML を組み立てて返却する。
# {{BASIS_CARDS}} slot は template の <h2> 行と <div class="back-to-top"> 行の間に
# 単独行で配置されているため、戻り値は「先頭 blank line + cards 連結（card 間 blank
# line 区切り）+ 末尾改行なし」のフォーマットで組み立てる。

# freq enum → freq-badge 星数マッピング
_BASIS_FREQ_STARS: dict[str, str] = {
    "high": "★★★",
    "mid":  "★★",
    "low":  "★",
}

# kind → デフォルト icon マッピング（icon フィールド省略時に補完）
_BASIS_DEFAULT_ICON: dict[str, str] = {
    "statute": "📜",
    "case":    "⚖",
}


def _render_basis_back_links(back_links: list[dict]) -> str:
    """back_links[{href, label}] を <div class="ref-backlinks">...</div> に変換。"""
    chips = "".join(
        f'<a class="rb-chip" href="{escape(bl.get("href", ""))}">{escape(bl.get("label", ""))}</a>'
        for bl in back_links
    )
    return f'        <div class="ref-backlinks">{chips}</div>'


def _render_basis_card(card: dict) -> str:
    """単一 Basis_Card（kind=statute / kind=case）を HTML に変換。"""
    kind = card.get("kind", "")
    card_id = card.get("id", "")
    icon = card.get("icon") or _BASIS_DEFAULT_ICON.get(kind, "")
    title_html = card.get("title_html", "")
    title_suffix_html = card.get("title_suffix_html", "")
    freq = card.get("freq", "high")
    stars = _BASIS_FREQ_STARS.get(freq, "")

    header_inner = (
        f'{icon} {title_html}{title_suffix_html}'
        f'<span class="freq-badge freq-{freq}">{stars}</span>'
    )

    body_lines: list[str] = []
    if kind == "statute":
        for para in card.get("paragraphs", []):
            para_num = escape(para.get("para_num", ""))
            body_html = para.get("body_html", "")
            body_lines.append(
                f'        <p class="hanging">'
                f'<span class="para-num">{para_num}</span>'
                f'<span class="hang-body">{body_html}</span></p>'
            )
    elif kind == "case":
        facts_html = card.get("facts_html", "")
        judgment_html = card.get("judgment_html", "")
        body_lines.append(
            f'        <p class="hanging"><strong>【事案】</strong>'
            f'<span class="hang-body">{facts_html}</span></p>'
        )
        body_lines.append(
            f'        <p class="judgment-text hanging"><strong>【判旨】</strong>'
            f'<span class="hang-body">{judgment_html}</span></p>'
        )

    note_html = card.get("note_html")
    if note_html:
        body_lines.append('        <div class="note">')
        body_lines.append(f'          {note_html}')
        body_lines.append('        </div>')

    back_links = card.get("back_links") or []
    if back_links:
        body_lines.append(_render_basis_back_links(back_links))

    card_class = f'basis-card {kind}-card'
    parts = [
        f'    <div class="{card_class}" id="{escape(card_id)}">',
        f'      <div class="basis-card-header">{header_inner}</div>',
        f'      <div class="basis-card-body">',
    ]
    parts.extend(body_lines)
    parts.append('      </div>')
    parts.append('    </div>')
    return "\n".join(parts)


def render_basis(data: dict | None) -> str:
    """basis フィールドを {{BASIS_CARDS}} slot 値に変換する。

    None / 未指定 / cards 空 → BASIS_STUB（byte-identical 維持）
    dict → 構造化 basis-card HTML（先頭 blank line + cards 連結、末尾改行なし）
    """
    if not data:
        return BASIS_STUB
    cards = data.get("cards") or []
    if not cards:
        return BASIS_STUB
    rendered = [_render_basis_card(c) for c in cards]
    # 各 card 間は blank line 区切り、戻り値の先頭にも blank line（h2 と最初の card を区切る）。
    # 末尾改行は template 側の `{{BASIS_CARDS}}\n` が供給するため付けない。
    return "\n" + "\n\n".join(rendered)


# ============================================================================
# PART A 【見解】描画関数（Phase 4-1）
# ============================================================================
# views フィールドが None / 未指定 / 空 の場合は空文字列を返却 → {{VIEWS_BLOCK}}
# slot が空に置換され、template 側の `\n{{VIEWS_BLOCK}}\n` が `\n\n` となり、
# 【見解】H3 + section ごと出力から消える（gold 300 と一致）。
# list[3] の場合は 18 行ブロック相当の HTML を返却し、329 等の byte-identical を維持。
# {{VIEWS_BLOCK}} slot は sc5 template 単独に配置（他 7 templates には placeholder なし）。

_VIEWS_H3_STYLE = (
    'background:transparent; border-left:none; padding:8px 0 4px 0;'
    ' margin:20px 0 8px 0; border-bottom:2px dotted var(--border-mid);'
    ' color:var(--accent); font-family:var(--font-display);'
)


def render_views_block(views: list | None) -> str:
    """views フィールドを {{VIEWS_BLOCK}} slot 値に変換する。

    None / 未指定 / 空 → ""（views 関連 HTML を完全に出力しない）
    list[3 (A/B/C)] → 【見解】H3 + views-section の HTML
    """
    if not views:
        return ""
    views_by_label: dict[str, dict] = {}
    for v in views:
        lbl = v.get("label")
        if lbl in ("A", "B", "C"):
            views_by_label[lbl] = v
    view_blocks: list[str] = []
    for letter in ("A", "B", "C"):
        v = views_by_label.get(letter, {})
        label = str(v.get("label", ""))
        body = str(v.get("body", ""))
        view_blocks.append(
            '      <div class="view-block">\n'
            f'        <span class="view-label">{label}</span>\n'
            f'        <p class="view-body">{body}</p>\n'
            '      </div>'
        )
    blocks_html = "\n".join(view_blocks)
    # 戻り値は 17 \n を含み leading/trailing \n 付き（line 2060-2077 相当の 18 行）。
    # template 側の `\n{{VIEWS_BLOCK}}\n` が calc {{CASE_BODY}} 行末と【記述】行頭の
    # 境界 \n を 1 つずつ提供する（合計 19 \n で原 region と byte-identical）。
    return (
        '\n'
        '    <h3 style="' + _VIEWS_H3_STYLE + '">【見解】</h3>\n'
        '\n'
        '    <section class="views-section" id="part-a-views">\n'
        f'{blocks_html}\n'
        '    </section>\n'
    )


# ============================================================================
# footer-spec feature-tag 列描画関数（Phase 4-2）
# ============================================================================
# 8 templates の <p class="footer-meta"> 内 23 行 <span class="feature-tag"> を
# {{FOOTER_FEATURE_TAGS}} 集約 slot に置換。
# 末尾 1 行は OVERRIDE_PATTERN を取り、それより手前 22 行は仕様固定（v8.11.7 時点）。
# byte-identical 復元のため irregular indent パターン (6/0/0/0/0/6/0/6...6) を逐語温存。

# 末尾 OVERRIDE_PATTERN を除く 22 固定 feature-tag（v8.11.7 時点）。
# spec 上昇に伴う増減はこのリストを編集する（8 templates の手修正不要）。
FOOTER_FEATURE_TAGS_DEFAULT: list[str] = [
    "TX v8.11.7",
    "spoiler-safe",
    "a2-two-stage-reveal",
    "a2-multi-ox-support",
    "spoiler-leak-eradication",
    "spoiler-strong-elimination",
    "ox-grid-fa-unification",
    "spoiler-footer-purge",
    "multi-answer-css",
    "ktx301-canon",
    "ktx-template-canon",
    "embedded-canon",
    "readability-layer",
    "hanging-grid",
    "basis-order-v2",
    "a2-feedback-canon",
    "rbchip-patched",
    "k302-immune",
    "p2p3-unified",
    "p1-absolute",
    "jp-prefix-naming",
    "content-independence",
]

# 23 行（22 固定 + OVERRIDE_PATTERN）の indent 量。v8.11.7 baseline 由来。
# 整理したくなる irregular 配列だが、byte-identical 復元のため逐語温存。
FOOTER_TAG_INDENTS: list[int] = [
    6, 0, 0, 0, 0,
    6, 0,
    6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
    6,  # OVERRIDE_PATTERN 行
]


def render_footer_feature_tags(
    override_pattern: str,
    extra_tags: list[str] | None = None,
) -> str:
    """{{FOOTER_FEATURE_TAGS}} slot 値を組み立てる。

    Args:
        override_pattern: 末尾 feature-tag に注入する pattern 文字列（例: "P1"）。
        extra_tags: per-problem 拡張 tag（v8.11.7 では未使用、将来 hook）。
                    指定時は override_pattern 行のさらに後ろに、各 indent=6 で追加。

    戻り値は (22 + 1 + len(extra_tags)) 行を \\n 区切りで連結したもの。末尾 \\n は含まない
    （template 側の `{{FOOTER_FEATURE_TAGS}}\\n` が末尾改行を供給する）。
    """
    tags: list[str] = list(FOOTER_FEATURE_TAGS_DEFAULT) + [override_pattern]
    if extra_tags:
        tags.extend(extra_tags)
    indents: list[int] = list(FOOTER_TAG_INDENTS)
    while len(indents) < len(tags):
        indents.append(6)  # extras default to indent 6
    lines: list[str] = []
    last = len(tags) - 1
    for i, (indent, tag) in enumerate(zip(indents, tags)):
        sep = "・" if i < last else ""
        lines.append(" " * indent + f'<span class="feature-tag">{tag}</span>' + sep)
    return "\n".join(lines)


# ============================================================================
# marker-legend 描画関数（Phase 4-5）
# ============================================================================
# 8 templates の sync-required 領域 marker-legend block を集約 slot 化。
# universal content (subject / instruction_type 無関係) のため引数なし固定。
# spec bump で legend 内容が変わる際は MARKER_LEGEND_DEFAULT のみ修正することで
# 8 templates を一括追従可能。per-problem 拡張 hook は Phase 4-5 完了後に判断
# (BACKLOG §6-4)。

MARKER_LEGEND_DEFAULT: str = (
    '  <div class="marker-legend" aria-label="マーカー凡例">\n'
    '    <span class="lg-title">凡例</span>\n'
    '    <span class="lg-item"><span class="lg-sample lg-ron">論</span>論文関連</span>\n'
    '    <span class="lg-divider">|</span>\n'
    '    <span class="lg-item"><span class="exam-mark freq-high">高</span>短答頻出</span>\n'
    '    <span class="lg-item"><span class="exam-mark freq-mid">中</span>標準</span>\n'
    '    <span class="lg-item"><span class="exam-mark freq-low">低</span>関連</span>\n'
    '    <span class="lg-divider">|</span>\n'
    '    <span class="lg-item"><span class="statute-emphasis freq-high">条</span>条文</span>\n'
    '    <span class="lg-item"><span class="case-emphasis freq-high">判</span>判例</span>\n'
    '  </div>'
)


def render_marker_legend() -> str:
    """{{MARKER_LEGEND}} slot 値を返す（universal、引数なし固定）。"""
    return MARKER_LEGEND_DEFAULT


# ============================================================================
# TOC 描画関数（Phase 4-6・thin schema 派生）
# ============================================================================
# 8 templates の diff-allowed `toc` 領域（6 variants）を集約 slot 化。
# 既存 problem.instruction_type から choice ラベル系列を派生し、universal 部分
# （先頭 3 行 + 末尾 5 行）と組み合わせて完全な TOC を生成する。
# 未対応 instruction_type は RuntimeError（silent fallback 不採用、新 type 追加時の
# 失敗を早期検出）。
#
# - schema 変更なし、JSON 改修なし
# - 14 protected + 300 すべて byte-identical 維持（各問題の instruction_type に
#   対応する既存 variant と一致する TOC が再生される）

TOC_CHOICE_LABELS_BY_TYPE: dict[str, list[str]] = {
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


def render_toc(instruction_type: str) -> str:
    """{{TOC_ROW}} slot 値を返す（instruction_type 派生）。

    未対応 type は RuntimeError raise（silent fallback で誤った TOC が出力される事故を
    防ぐため。新 instruction_type 追加時は TOC_CHOICE_LABELS_BY_TYPE 辞書に 1 行追加）。
    """
    if instruction_type not in TOC_CHOICE_LABELS_BY_TYPE:
        raise RuntimeError(
            f"unknown instruction_type {instruction_type!r} for TOC. "
            f"valid: {sorted(TOC_CHOICE_LABELS_BY_TYPE)}"
        )
    labels = TOC_CHOICE_LABELS_BY_TYPE[instruction_type]
    choice_lines = "".join(
        f'      <a href="#choice-{i}">{lab}</a>\n'
        for i, lab in enumerate(labels, start=1)
    )
    return TOC_HEAD + choice_lines + TOC_TAIL


# ============================================================================
# PART D drill 構造化レンダリング関数（Phase 4-7）
# ============================================================================
# 8 templates の PART D drill 12 件分の固定 slot 方式（旧 DRILL_NN_* 60 個）を、
# 構造化レンダリング方式（{{DRILL_BLOCKS}} 1 slot）に置換するための関数。
# Phase 3-3 basis structured rendering と同種パターン。
#
# 設計判断（BACKLOG §2-1）:
# - schema 変更なし（既存 drill_blocks 配列フィールド流用）
# - escape 旧仕様踏襲（escape なし、byte-identical 優先）
#   ※ BACKLOG §6-6: 将来 HTML attribute-unsafe 文字が出現したときに個別対処
#   ※ Phase 4-7 commit 2 着手前 grep 検証で全 720 field-values で 0 件確認済
# - num は JSON drill["num"] をそのまま使用（"01" 等 0 埋め文字列を期待）
# - correct ("○"/"×") から O_CORRECT / X_CORRECT ("true"/"false") を派生
# - drill_blocks 未指定 / 空 → "" を返却（drill section ごと不出力。ただし
#   template 側の周辺 HTML（arena-counter / arena-scorecard 等）は残る）

def render_drill_blocks(drills: list | None) -> str:
    """{{DRILL_BLOCKS}} slot 値を返す（構造化レンダリング）。

    各 drill を <div class="drill-block">...</div> に変換、間に blank line を挟む。
    旧 60 個の DRILL_NN_* slot 方式と byte-identical な出力を期待する。
    """
    if not drills:
        return ""
    blocks: list[str] = []
    for d in drills:
        num = str(d.get("num", ""))
        tag = str(d.get("tag", ""))
        question = str(d.get("question", ""))
        correct = str(d.get("correct", ""))
        explanation = str(d.get("explanation", ""))
        o_correct = "true" if correct == "○" else "false"
        x_correct = "true" if correct == "×" else "false"
        block = (
            '    <div class="drill-block">\n'
            '      <div class="drill-label">'
            '<span class="drill-num">DRILL&nbsp;' + num + '</span>'
            '<span class="drill-tag">' + tag + '</span></div>\n'
            '      <div class="self-check-quiz" data-arena="1" '
            'data-correct-value="' + correct + '" '
            'data-explanation="' + explanation + '">\n'
            '        <div class="quiz-question">' + question + '</div>\n'
            '        <div class="quiz-buttons">'
            '<button class="quiz-btn" type="button" '
            'data-correct="' + o_correct + '" data-value="○">○</button>'
            '<button class="quiz-btn" type="button" '
            'data-correct="' + x_correct + '" data-value="×">×</button></div>\n'
            '        <div class="quiz-answer" hidden>'
            '<span class="quiz-result"></span>' + explanation + '</div>\n'
            '      </div>\n'
            '    </div>'
        )
        blocks.append(block)
    return "\n\n".join(blocks)


# ============================================================================
# body_pre_toc 描画関数（Phase 4-8）
# ============================================================================
# 8 templates の sync-required 領域 body_pre_toc (393 bytes / 12 lines) を集約 slot 化。
# universal な HTML 構造 + 6 個の動的値 (JP_PREFIX/PROBLEM_ID/CRIME/SOURCE_ID/
# CORRECT_RATE/OVERRIDE_PATTERN) を含むため、Phase 4-5 marker-legend の引数なし固定
# const パターンを Python .format() 名前付き placeholder に拡張。
#
# 設計判断（BACKLOG §2-1 / ユーザ §8 採択回答）:
# - schema 変更なし、JSON 改修なし（既存 6 slot 値を流用）
# - 旧 6 slot ({{JP_PREFIX}} 等) は据え置き（footer-spec 等で他参照あり削除不可）
# - escape 旧仕様踏襲（escape なし、Phase 4-7 と同一）
# - .format(**) 名前参照で insertion order 非依存
# - broken intermediate state なし（旧 slot 据え置きのため Commit 2 直後も render 動作）

BODY_PRE_TOC_TEMPLATE: str = (
    '</head>\n'
    '<body id="top">\n'
    '<div class="container">\n'
    '\n'
    '  <!-- HEADER -->\n'
    '  <header class="header">\n'
    '    <div class="doc-header">{jp_prefix}{problem_id}</div>\n'
    '    <h1>No.{problem_id} ── {crime}（{source_id}）</h1>\n'
    '    <div class="exam-meta">\n'
    '      <span><strong>正答率:</strong>{correct_rate}</span>\n'
    '      <span><strong>パターン:</strong>{override_pattern}</span>\n'
    '    </div>'
)


def render_body_pre_toc(problem: dict) -> str:
    """{{BODY_PRE_TOC}} slot 値を返す（Python .format() で動的値を埋込）。

    旧 6 slot ({{JP_PREFIX}} 等) と同じ値を Python format placeholder 経由で埋込み、
    slot 機構を経由しない完成 HTML を返す。insertion order 非依存。
    escape 旧仕様踏襲（escape なし）。
    """
    subject = problem.get("subject", "KEI")
    jp_prefix = SUBJECT_TO_JP[subject] + "TX"
    return BODY_PRE_TOC_TEMPLATE.format(
        jp_prefix=jp_prefix,
        problem_id=str(problem.get("id", "")),
        crime=str(problem.get("crime", "")),
        source_id=str(problem.get("source", "")),
        correct_rate=str(problem.get("correct_rate", "")),
        override_pattern=str(problem.get("override_pattern", "P1")),
    )


# ============================================================================
# C-7 末尾 final-answer 描画関数（Phase 4-3）
# ============================================================================
# §22-bis 単一解答型 / §22-ter 多解答型 (multi-select-5) の final-answer DOM block
# を構築する。問題に final_answer フィールドが指定されていなければ "" を返却し、
# render_c7_memory() 経由で出力に何も injected されない（既存 14 件 byte-identical
# 維持）。canonical KTX301.html line 3035-3041 の §22-bis 構造に準拠。
#
# - hidden 属性必須 (§22-quater-1 / AP-30 / S68)
# - fa-summary 「正解はN」リテラル禁止は呼出側 (problem.json) の責務 (§22-quater-2)
# - ox-grid 系は AP-40 (v8.11.5) により single 形式に統一 (multi 構造化しない)

def render_final_answer(problem: dict) -> str:
    """problem.final_answer から §22-bis/§22-ter 形式の final-answer block を返す。

    None / 未指定 → ""（block ごと出力しない、byte-identical 維持）
    dict 与えられた場合は instruction_type + answer から mode を派生:
      - multi-select-5: §22-ter (cells per stmt、正解のみ)
      - それ以外:        §22-bis (single answer-num)

    戻り値は末尾改行なしの multi-line 文字列。render_c7_memory() 側で memory-list
    終了と back-to-top の間に blank line 区切りで埋め込む。
    """
    fa = problem.get("final_answer")
    if not fa:
        return ""

    summary_html = fa.get("summary_html", "")
    extra_html = fa.get("extra_html", "")
    instr_type = problem.get("instruction_type", "")
    answer_raw = problem.get("answer", "")

    if instr_type == "multi-select-5" and isinstance(answer_raw, list):
        # §22-ter: 正解と判定された記述 cell のみ列挙 (AP-38)
        cells = "\n".join(
            f'        <div class="ans-cell ans-correct">'
            f'<span class="ans-stmt">{escape(str(n))}</span>'
            f'<span class="ans-val">1</span></div>'
            for n in answer_raw
        )
        answer_block = (
            '      <div class="answer-num answer-num-multi">\n'
            + cells + '\n'
            + '      </div>'
        )
    else:
        # §22-bis: single form (ox-grid 系も AP-40 で single に統一)
        answer_value = _format_answer(answer_raw)
        answer_block = f'      <span class="answer-num">{answer_value}</span>'

    extra_p = f'\n      <p>{extra_html}</p>' if extra_html else ""

    return (
        '    <!-- §22-bis: C-7 末尾配置 final-answer -->\n'
        '    <div class="final-answer" hidden>\n'
        '      <h3>🎯 正解</h3>\n'
        + answer_block + '\n'
        '      <p class="fa-summary">' + summary_html + '</p>'
        + extra_p + '\n'
        '    </div>'
    )


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


def render_c7_memory(data: dict | None, final_answer_html: str = "") -> str:
    """C-7 三層構造記憶セクション。

    final_answer_html が非空なら memory-list 終了と back-to-top の間に挿入する
    (Phase 4-3 § §22-bis/§22-ter)。空文字列なら従来通り出力（byte-identical 維持）。
    """
    if not data:
        if final_answer_html:
            # stub の back-to-top 直前に final-answer + 空行を挿入
            return PART_C_STUBS["C7_MEMORY"].replace(
                "\n" + _BACK_TO_TOP,
                "\n\n" + final_answer_html + "\n" + _BACK_TO_TOP,
                1,
            )
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
    if final_answer_html:
        parts.extend(["", final_answer_html])
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

    # PART B basis slot 供給（Phase 3-3 で structured rendering 導入）。
    # basis 未定義 / null / cards 空 の場合は render_basis() が BASIS_STUB を返し、
    # 既存 14 件 byte-identical を担保する。
    slots["BASIS_CARDS"] = render_basis(problem.get("basis"))

    # PART C slot 供給（Phase 2、任意フィールド part_c.*）。
    # part_c 未定義 / 各サブセクション未定義の場合は PART_C_STUBS が注入され、
    # 既存 14 件は byte-identical 維持。
    # C-7 のみ final-answer (Phase 4-3) と組合せて生成する。
    part_c = problem.get("part_c") or {}
    final_answer_html = render_final_answer(problem)
    slots["C1_SYSTEMATIC"]  = render_c1_systematic(part_c.get("systematic"))
    slots["C2_COMPARISON"]  = render_c2_comparison(part_c.get("comparison"))
    slots["C3_CONNECTIONS"] = render_c3_connections(part_c.get("connections"))
    slots["C4_DOCTRINES"]   = render_c4_doctrines(part_c.get("doctrines"))
    slots["C5_FLOWCHART"]   = render_c5_flowchart(part_c.get("flowchart"))
    slots["C6_RELATED"]     = render_c6_related(part_c.get("related_problems"))
    slots["C7_MEMORY"]      = render_c7_memory(part_c.get("three_layer_memory"), final_answer_html)

    # marker-legend slot 供給（Phase 4-5 で集約 slot 化）。
    # universal content のため problem に依存せず固定値を返却。
    slots["MARKER_LEGEND"] = render_marker_legend()

    # TOC slot 供給（Phase 4-6 で集約 slot 化、thin schema 派生）。
    # problem.instruction_type から TOC_CHOICE_LABELS_BY_TYPE を参照し、
    # universal 部分 (TOC_HEAD + TOC_TAIL) と choice anchor 群を組み立てる。
    # 未対応 type は render_toc() 内で RuntimeError。
    slots["TOC_ROW"] = render_toc(problem.get("instruction_type", ""))

    # body_pre_toc slot 供給（Phase 4-8 で集約 slot 化、案 δ refined: .format() 名前付き placeholder）。
    # 旧 6 slot ({{JP_PREFIX}}/{{PROBLEM_ID}}/{{CRIME}}/{{SOURCE_ID}}/{{CORRECT_RATE}}/
    # {{OVERRIDE_PATTERN}}) は据え置き、本 slot は経路の重複となるが許容（footer-spec 等で
    # 他参照あり旧 slot 削除不可）。
    slots["BODY_PRE_TOC"] = render_body_pre_toc(problem)

    # footer-spec feature-tag 列 slot 供給（Phase 4-2 で集約 slot 化）。
    # FOOTER_FEATURE_TAGS_DEFAULT (22 固定) + override_pattern を 23 行ブロックに
    # 整形して {{FOOTER_FEATURE_TAGS}} に注入する。
    # extra_tags は v8.11.7 では未使用（hook のみ残置）。
    slots["FOOTER_FEATURE_TAGS"] = render_footer_feature_tags(
        slots["OVERRIDE_PATTERN"],
        extra_tags=problem.get("footer", {}).get("extra_tags") if isinstance(problem.get("footer"), dict) else None,
    )

    # 【見解】slot 供給（Phase 4-1 で集約 slot 化）
    # views が未指定/空 の場合は VIEWS_BLOCK = "" → sc5 template の views region
    # （H3 + section）が出力から完全に消える（gold 300 と一致）。
    # views が 3 件 present の場合は原ブロック相当の HTML を返し、329 の byte-identical
    # を維持する。下位互換: VIEW_*_LABEL / VIEW_*_BODY は他処理向けの遺物として
    # 引き続き埋めておく（sc5 template からは placeholder 削除済みのため未参照）。
    views_data = problem.get("views") or []
    slots["VIEWS_BLOCK"] = render_views_block(views_data)
    views_by_label: dict[str, dict] = {}
    for v in views_data:
        lbl = v.get("label")
        if lbl in ("A", "B", "C"):
            views_by_label[lbl] = v
    for letter in ("A", "B", "C"):
        v = views_by_label.get(letter, {})
        slots[f"VIEW_{letter}_LABEL"] = str(v.get("label", ""))
        slots[f"VIEW_{letter}_BODY"] = str(v.get("body", ""))

    # PART D drill-block slot 供給（Phase 4-7 で構造化レンダリングに移行）
    # 旧 60 個の DRILL_NN_* slot 方式を廃止し、{{DRILL_BLOCKS}} 1 slot に集約。
    # drill_blocks 未指定 / 空 → "" を返却（drill 部分が出力から消える、ただし
    # template 側の周辺 HTML（arena-counter / arena-scorecard 等）は残る）。
    slots["DRILL_BLOCKS"] = render_drill_blocks(problem.get("drill_blocks", []))

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
# inject_ref_ids 後処理（Phase 4-4・basis rb-chip back-link 解決）
# ============================================================================
# canonical KTX301 規約 `ref-{target}-{NNN}` で、全 inline <a class="ref-case|ref-stat"
# href="#X"> に id を注入する。NNN は target 別の document order 1-indexed 出現順、
# 3 桁ゼロ埋め。
#
# - schema 不変（既存 basis.cards.back_links[].href を target にする運用）
# - 14 protected ファイルは inline ref-X anchor 0 件 → 注入なし → byte-identical 維持
# - 300.html: 70 inline anchor に id 注入で hash 変化（既存 DIFF=1 内）
# - 呼出経路前提: render.py は main() からのみ呼ばれる。本関数も main() 内で
#   `rendered = render(...); rendered = inject_ref_ids(rendered)` の chain として配線。
#   テスト経路を将来追加する場合は明示的に呼出側で同 chain を組む（render() 自体には
#   後処理を持たせない設計）。
# - 既存 id 付き <a> はマッチしないため idempotent

REF_ANCHOR_PATTERN = re.compile(r'<a class="(ref-case|ref-stat)" href="#([^"]+)">')


def inject_ref_ids(html: str) -> str:
    """全 inline ref-case/ref-stat anchor に id="ref-{target}-{NNN}" を注入する。"""
    counters: dict[str, int] = {}

    def repl(m: "re.Match[str]") -> str:
        cls = m.group(1)
        target = m.group(2)
        counters[target] = counters.get(target, 0) + 1
        n = counters[target]
        return f'<a class="{cls}" id="ref-{target}-{n:03d}" href="#{target}">'

    return REF_ANCHOR_PATTERN.sub(repl, html)


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

    # Phase 4-4: basis rb-chip back-link target を解決するため、inline
    # ref-case / ref-stat anchor に id="ref-{target}-{NNN}" を注入する。
    # 14 protected は inline ref-X anchor 0 件のため不変、300 は 70 個に id 付与で hash 変化。
    rendered = inject_ref_ids(rendered)

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
