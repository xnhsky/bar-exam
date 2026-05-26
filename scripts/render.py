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
# v9.2.0 DEEP-DIVE spec version 分岐フラグ
# ============================================================================
# 既定値は v9.1.0 互換（既存 8 templates 経路を破壊しない）。
# 問題 JSON の "spec_version" フィールドが "v9.2.0" の場合のみ v9.2.0 経路に切替。
# 切替は build_slot_dict() 内で動的に判定（per-problem）。
#
# TASK12-13-HANDOFF § 4 に対応：
#   INCLUDE_TREE_MINDMAP / INCLUDE_RADIAL_MINDMAP /
#   INCLUDE_BRANCHING_FLOWCHART / INCLUDE_THEORY_DEEP_DIVE /
#   PROFESSOR_DENSITY_LEVEL / PALETTE_DERIVATIVES

DEFAULT_SPEC_VERSION = "v9.1.0"


def get_render_flags(spec_version: str) -> dict[str, object]:
    """spec バージョンから render 分岐フラグ群を導出。

    既存 8 templates は v8.11.7/v9.0.0/v9.1.0 共通の slot 集合を持ち、
    v9.2.0 専用 slot (MINDMAP_TREE / MINDMAP_RADIAL_V92 / FLOW_SVG_V92 /
    THEORY_DEEP_DIVE / PALETTE_DERIVATIVES_ROOT) は参照していない。
    したがって v9.2.0 用 slot 値を空文字で供給しても render() の未置換検出に
    影響せず、既存 byte-identical を維持できる。
    """
    if spec_version == "v9.4.0":
        # v9.4.0 COMPLETE-BASELINE: v9.1.0 構造美 + v9.2.0 加算 6 件 + v9.3.0 加算 1 件
        # v9.2.0 加算機能は全て ON、v9.4.0 独自の v9.1.0 baseline 機能（hero-extra,
        # choice-summary, sub-card.basis-link, mindmap-section v94）も ON。
        return {
            "INCLUDE_TREE_MINDMAP": True,
            "INCLUDE_RADIAL_MINDMAP": True,
            "INCLUDE_BRANCHING_FLOWCHART": True,
            "INCLUDE_THEORY_DEEP_DIVE": True,
            "PROFESSOR_DENSITY_LEVEL": "v2",
            "PALETTE_DERIVATIVES": True,
            "INCLUDE_V94_HERO_EXTRA": True,
            "INCLUDE_V94_CHOICE_SUMMARY": True,
            "INCLUDE_V94_SUB_CARD_BASIS_LINK": True,
            "INCLUDE_V94_MINDMAP_SECTION": True,
        }
    if spec_version == "v9.2.0":
        return {
            "INCLUDE_TREE_MINDMAP": True,
            "INCLUDE_RADIAL_MINDMAP": True,
            "INCLUDE_BRANCHING_FLOWCHART": True,
            "INCLUDE_THEORY_DEEP_DIVE": True,
            "PROFESSOR_DENSITY_LEVEL": "v2",
            "PALETTE_DERIVATIVES": True,
        }
    # v9.1.0 / v9.0.0 / v8.11.7 共通：v9.2.0 拡張は全 OFF
    return {
        "INCLUDE_TREE_MINDMAP": False,
        "INCLUDE_RADIAL_MINDMAP": True,  # v9.1.0 の旧 §22-quad は radial として残存（mindmap-section）
        "INCLUDE_BRANCHING_FLOWCHART": False,
        "INCLUDE_THEORY_DEEP_DIVE": False,
        "PROFESSOR_DENSITY_LEVEL": "v1",
        "PALETTE_DERIVATIVES": False,
    }


# ============================================================================
# v9.2.0 派生色 :root override 値（TASK02 § 1 / TASK11 § 2 / § 3）
# ============================================================================
# P1/P2/P3 各々で 10 個（相対 7 + 絶対 3）。絶対派生 3 個は全 pattern で同値。
# S88 検証対象。

V92_PALETTE_DERIVATIVES = {
    "P1": {
        # 相対派生 7 個
        "--accent-light":   "#a83553",
        "--accent-darker":  "#6f1830",
        "--mid-warm":       "#e0664f",
        "--mid-cool":       "#b04466",
        "--accent-soft-2":  "#f9e0e5",
        "--mid-soft":       "#fad8e1",
        "--surface-tint":   "#fef9fb",
        # 絶対派生 3 個（パターン非依存）
        "--neutral-cream":  "#f4ede0",
        "--contrast-warm":  "#d97a4f",
        "--contrast-cool":  "#6a8aa8",
    },
    "P2": {
        "--accent-light":   "#5b8062",
        "--accent-darker":  "#34503a",
        "--mid-warm":       "#99ad75",
        "--mid-cool":       "#7ea58e",
        "--accent-soft-2":  "#e7eee0",
        "--mid-soft":       "#d5dfd0",
        "--surface-tint":   "#f9fbf7",
        "--neutral-cream":  "#f4ede0",
        "--contrast-warm":  "#d97a4f",
        "--contrast-cool":  "#6a8aa8",
    },
    "P3": {
        "--accent-light":   "#7560a8",
        "--accent-darker":  "#3e2a5c",
        "--mid-warm":       "#b890c4",
        "--mid-cool":       "#8a92c4",
        "--accent-soft-2":  "#ebe1f3",
        "--mid-soft":       "#ddd1ee",
        "--surface-tint":   "#faf8fd",
        "--neutral-cream":  "#f4ede0",
        "--contrast-warm":  "#d97a4f",
        "--contrast-cool":  "#6a8aa8",
    },
}


# ============================================================================
# v9.2.0 footer-spec 33-tag canonical（TASK11 § 5-2）
# ============================================================================
# 既存 22 tag (FOOTER_FEATURE_TAGS_DEFAULT) を v9.2.0 用に拡張。
# 末尾は OVERRIDE_PATTERN + palette-strategy: [戦略名] の 2 件。

FOOTER_FEATURE_TAGS_V92: list[str] = [
    "TX v9.2.0 DEEP-DIVE",
    "genkei-skeleton",
    "design-byte-lock",
    "content-independence",
    "ktx301-canon",
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
    "spoiler-safe",
    "multi-answer-css",
    "a2-two-stage-reveal",
    "a2-multi-ox-support",
    "spoiler-leak-eradication",
    "spoiler-strong-elimination",
    "ox-grid-fa-unification",
    "host-injection-safe",
    "tree-mindmap",
    "radial-mindmap",
    "branching-flowchart",
    "theory-deep-dive",
    "professor-density-v2",
    "meta-explanation-blocked",
    "palette-derivatives",
    "single-document-self-sufficient-deep",
]  # 31 件（OVERRIDE_PATTERN + palette-strategy 行はレンダリング時に追加で 33 件）


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
    spec_version: str = "v9.1.0",
    palette_strategy: str | None = None,
) -> str:
    """{{FOOTER_FEATURE_TAGS}} slot 値を組み立てる。

    Args:
        override_pattern: 末尾 feature-tag に注入する pattern 文字列（例: "P1"）。
        extra_tags: per-problem 拡張 tag。
                    指定時は override_pattern 行のさらに後ろに、各 indent=6 で追加。
        spec_version: "v9.2.0" の場合は FOOTER_FEATURE_TAGS_V92 を使用（31+2=33 件）。
                      それ以外は既存 22+1+extra の v8.11.7/v9.1.0 互換。
        palette_strategy: v9.2.0 のみ。"palette-strategy: [戦略名]" を末尾に追加。

    戻り値は \\n 区切りで連結したもの。末尾 \\n は含まない
    （template 側の `{{FOOTER_FEATURE_TAGS}}\\n` が末尾改行を供給する）。
    """
    if spec_version in ("v9.2.0", "v9.4.0"):
        # v9.2.0 DEEP-DIVE: 31 固定 + override_pattern + palette-strategy = 33 tag
        # v9.4.0 COMPLETE-BASELINE: 同じ 33 tag に v9.4.0 識別 tag を 5 件追加 = 38 tag
        base = list(FOOTER_FEATURE_TAGS_V92) + [override_pattern]
        if palette_strategy:
            base.append(f"palette-strategy: {palette_strategy}")
        else:
            base.append("palette-strategy: 同系統調和")  # 既定戦略
        if spec_version == "v9.4.0":
            # v9.4.0 識別タグ群（v9.1.0 baseline 機能の有効化を明示）
            # v9.2.0 DEEP-DIVE tag を v9.4.0 COMPLETE-BASELINE tag に差し替える
            base[0] = "TX v9.4.0 COMPLETE-BASELINE"
            base.append("v94-hero-extra")
            base.append("v94-choice-summary")
            base.append("v94-sub-card-basis-link")
            base.append("v94-mindmap-section")
        if extra_tags:
            base.extend(extra_tags)
        tags = base
    else:
        tags = list(FOOTER_FEATURE_TAGS_DEFAULT) + [override_pattern]
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
# v9.2.0 派生色 :root override 出力（S88 対応）
# ============================================================================

def render_palette_derivatives_root(pattern: str) -> str:
    """v9.2.0 派生色 10 個を含む :root{} ブロックを生成。

    Args:
        pattern: "P1" / "P2" / "P3" のいずれか（OVERRIDE_PATTERN ベース）。
                 未知の値は P1 にフォールバック。

    戻り値：CSS テキスト（<style> 内に挿入する用）。
    v9.1.0 以下ファイル生成時は呼ばれない（build_slot_dict で空文字を返す）。
    """
    palette_key = pattern if pattern in V92_PALETTE_DERIVATIVES else "P1"
    derivs = V92_PALETTE_DERIVATIVES[palette_key]
    lines = ["  /* === v9.2.0 派生色 10 個（" + palette_key + " override・S88） === */", ":root{"]
    for var, val in derivs.items():
        # 整列：var 名は最大 17 字相当、val は 7 字 hex
        lines.append(f"  {var}: {val};")
    lines.append("}")
    return "\n".join(lines)


# ============================================================================
# v9.2.0 SVG auto-layout 補完層（Phase 13A）
# ============================================================================
# 「座標フィールドなし」JSON（例: 305.json）に対し、構造データから x/y/cx/cy/
# lines/viewbox を自動算出して inject する。座標が JSON に明示されていれば
# それを優先（後方互換）。render_mindmap_tree / render_mindmap_radial_v92 /
# render_flowchart_v2 の冒頭で 1 行呼ぶだけで動作。


def auto_layout_tree(tree: dict) -> dict:
    """mindmap_tree 用 auto-layout。
    入力 JSON に座標がなければ階層位置から x/y を生成し、parent_idx から lines を組み立てる。
    """
    if not tree:
        return tree
    out = dict(tree)  # 浅いコピー

    l0 = list(out.get("l0_nodes", []))
    l1 = list(out.get("l1_nodes", []))
    l2 = list(out.get("l2_nodes", []))
    l3 = list(out.get("l3_nodes", []))

    # viewbox 自動選択（"auto" or 未指定の場合）
    vb = out.get("viewbox", "auto")
    if vb == "auto" or not vb:
        max_per_layer = max(len(l0), len(l1), len(l2), len(l3), 1)
        depth = sum(1 for layer in (l0, l1, l2, l3) if layer)
        if depth >= 5:
            vb = "0 0 1100 800"
        elif max_per_layer >= 9:
            vb = "0 0 1300 600"
        elif max_per_layer >= 6:
            vb = "0 0 1100 700"
        else:
            vb = "0 0 1100 600"
    out["viewbox"] = vb

    # viewbox 幅・高さ抽出
    parts = vb.split()
    w = int(parts[2]) if len(parts) >= 4 else 1100
    h = int(parts[3]) if len(parts) >= 4 else 600

    # 階層 y 座標（上から下へ 13% / 35% / 57% / 79%）
    layer_y = [int(h * 0.13), int(h * 0.35), int(h * 0.57), int(h * 0.79)]

    def assign_xy(layer_nodes, layer_idx):
        n = len(layer_nodes)
        if n == 0:
            return []
        gap = w / (n + 1)
        out_nodes = []
        for i, node in enumerate(layer_nodes):
            new_node = dict(node)
            if "x" not in new_node:
                new_node["x"] = int(gap * (i + 1))
            if "y" not in new_node:
                new_node["y"] = layer_y[layer_idx]
            out_nodes.append(new_node)
        return out_nodes

    out["l0_nodes"] = assign_xy(l0, 0)
    out["l1_nodes"] = assign_xy(l1, 1)
    out["l2_nodes"] = assign_xy(l2, 2)
    out["l3_nodes"] = assign_xy(l3, 3)

    # 接続線生成（parent_idx から）
    if "lines" not in out:
        new_lines: list[dict] = []
        # L0 → L1
        for child in out["l1_nodes"]:
            pidx = child.get("parent_idx")
            if pidx is not None and pidx < len(out["l0_nodes"]):
                p = out["l0_nodes"][pidx]
                new_lines.append({"x1": p["x"], "y1": p["y"] + 20, "x2": child["x"], "y2": child["y"] - 15})
        # L1 → L2
        for child in out["l2_nodes"]:
            pidx = child.get("parent_idx")
            if pidx is not None and pidx < len(out["l1_nodes"]):
                p = out["l1_nodes"][pidx]
                new_lines.append({"x1": p["x"], "y1": p["y"] + 15, "x2": child["x"], "y2": child["y"] - 15})
        # L2 → L3
        for child in out["l3_nodes"]:
            pidx = child.get("parent_idx")
            if pidx is not None and pidx < len(out["l2_nodes"]):
                p = out["l2_nodes"][pidx]
                new_lines.append({"x1": p["x"], "y1": p["y"] + 15, "x2": child["x"], "y2": child["y"] - 15})
        out["lines"] = new_lines

    # issue_box の auto-layout（active な L3 ノード右側）
    issue = out.get("issue_box")
    if issue and ("x" not in issue or "y" not in issue):
        issue = dict(issue)
        active_l3 = next((n for n in out["l3_nodes"] if n.get("active")), None)
        if active_l3:
            issue["x"] = min(active_l3["x"] + 200, w - 100)
            issue["y"] = active_l3["y"]
            if "arrow" not in issue:
                issue["arrow"] = {
                    "x1": issue["x"] - 80, "y1": issue["y"],
                    "x2": active_l3["x"] + 60, "y2": active_l3["y"],
                }
        else:
            issue["x"] = w - 150
            issue["y"] = 100
        out["issue_box"] = issue

    return out


def auto_layout_radial(radial: dict) -> dict:
    """mindmap_radial 用 auto-layout。
    branches は V92_RADIAL_BRANCH_POSITIONS の既定座標を順序に従って使用。
    sub_nodes は branch から放射方向にオフセット配置。
    """
    import math
    if not radial:
        return radial
    out = dict(radial)

    branches = list(out.get("branches", []))
    new_branches = []
    cx_center, cy_center = 550, 450

    for i, branch in enumerate(branches):
        new_branch = dict(branch)
        # 主要枝の座標
        if "x" not in new_branch or "y" not in new_branch:
            if i < len(V92_RADIAL_BRANCH_POSITIONS):
                _, _, bx, by = V92_RADIAL_BRANCH_POSITIONS[i]
            else:
                bx, by = 550, 450
            new_branch.setdefault("x", bx)
            new_branch.setdefault("y", by)

        # sub_nodes の座標（branch から放射方向に外側へ）
        new_sub_nodes = []
        sub_nodes = branch.get("sub_nodes", [])
        if sub_nodes:
            dx = new_branch["x"] - cx_center
            dy = new_branch["y"] - cy_center
            dist = max(math.sqrt(dx * dx + dy * dy), 1.0)
            ux, uy = dx / dist, dy / dist
            tx, ty = -uy, ux
            base_x = new_branch["x"] + int(ux * 90)
            base_y = new_branch["y"] + int(uy * 90)
            n = len(sub_nodes)
            for j, sub in enumerate(sub_nodes):
                new_sub = dict(sub)
                if "x" not in new_sub or "y" not in new_sub:
                    offset = (j - (n - 1) / 2.0) * 40
                    new_sub["x"] = base_x + int(tx * offset)
                    new_sub["y"] = base_y + int(ty * offset)
                new_sub_nodes.append(new_sub)
        new_branch["sub_nodes"] = new_sub_nodes
        new_branches.append(new_branch)

    out["branches"] = new_branches

    issue = out.get("issue_branch")
    if issue and ("x" not in issue or "y" not in issue):
        issue = dict(issue)
        issue.setdefault("x", 200)
        issue.setdefault("y", 450)
        out["issue_branch"] = issue

    return out


def auto_layout_flowchart(flow: dict) -> dict:
    """flowchart_v2 用 auto-layout。
    decisions[] から cy を自動算出、yn_pos / chips / end_success / end_fails の座標も補完。
    """
    if not flow:
        return flow
    out = dict(flow)

    decisions = list(out.get("decisions", []))
    n_dec = len(decisions)

    # viewbox 自動選択
    vb = out.get("viewbox", "auto")
    if vb == "auto" or not vb:
        if n_dec <= 3:
            vb = "0 0 900 600"
        elif n_dec <= 5:
            vb = "0 0 900 800"
        else:
            vb = "0 0 900 1000"
    out["viewbox"] = vb

    # decisions の cy 自動算出
    new_decisions = []
    for i, dec in enumerate(decisions):
        new_dec = dict(dec)
        if "cy" not in new_dec:
            new_dec["cy"] = 200 + i * 150
        if "yn_pos" not in new_dec:
            cy = new_dec["cy"]
            new_dec["yn_pos"] = {
                "yes_x": 540, "yes_y": cy,
                "no_x": 360, "no_y": cy,
            }
        new_decisions.append(new_dec)
    out["decisions"] = new_decisions

    # chips の座標
    new_chips = []
    for chip in out.get("chips", []):
        new_chip = dict(chip)
        if "cx" not in new_chip or "cy" not in new_chip:
            didx = new_chip.get("on_decision_idx", 0)
            branch = new_chip.get("branch", "no")
            if didx < len(new_decisions):
                cy = new_decisions[didx]["cy"]
                new_chip.setdefault("cx", 580 if branch == "yes" else 320)
                new_chip.setdefault("cy", cy + 50)
            else:
                new_chip.setdefault("cx", 450)
                new_chip.setdefault("cy", 700)
        new_chips.append(new_chip)
    out["chips"] = new_chips

    # 終端ノードの座標
    last_y = new_decisions[-1]["cy"] + 150 if new_decisions else 500
    if "end_success" not in out:
        out["end_success"] = {"cx": 450, "cy": last_y}
    elif "cx" not in out["end_success"] or "cy" not in out["end_success"]:
        es = dict(out["end_success"])
        es.setdefault("cx", 450)
        es.setdefault("cy", last_y)
        out["end_success"] = es

    fail_labels = out.get("end_fail_labels", [])
    end_fails = list(out.get("end_fails", []))
    if not end_fails and fail_labels:
        for i, _ in enumerate(fail_labels):
            end_fails.append({
                "cx": 200 + i * 250 if i < 3 else 200,
                "cy": last_y if i < 3 else last_y + 80,
            })
    elif end_fails:
        new_end_fails = []
        for i, ef in enumerate(end_fails):
            new_ef = dict(ef)
            new_ef.setdefault("cx", 200 + i * 250 if i < 3 else 200)
            new_ef.setdefault("cy", last_y if i < 3 else last_y + 80)
            new_end_fails.append(new_ef)
        end_fails = new_end_fails
    out["end_fails"] = end_fails

    return out


# ============================================================================
# v9.2.0 §22-tree ツリー型体系図 SVG section 描画（S85 対応）
# ============================================================================

def render_mindmap_tree(problem: dict) -> str:
    """problem.mindmap_tree フィールドから <section id="mindmap-tree"> を生成。

    期待する problem JSON フィールド（spec_version="v9.2.0" のみ）：
        mindmap_tree:
          viewbox: "0 0 1100 600" 等（4 パターン）
          aria_label: 体系図の説明文
          legend: 凡例テキスト
          l0_nodes: [{x, y, label}]
          l1_nodes: [{x, y, label, parent_idx}]
          l2_nodes: [{x, y, label, parent_idx}]
          l3_nodes: [{x, y, label, parent_idx, active: bool}]
          issue_box: {x, y, title, body, target_idx}
          caption: 図キャプション

    未定義の場合は空文字を返す（v9.1.0 以下 + v9.2.0 で tree を持たない問題は無害）。
    """
    tree = problem.get("mindmap_tree")
    if not tree:
        return ""
    tree = auto_layout_tree(tree)  # Phase 13A: 座標未指定なら auto-layout

    viewbox = tree.get("viewbox", "0 0 1100 600")
    aria_label = escape(tree.get("aria_label", "[本問テーマ] の体系的位置づけ"))
    legend = escape(tree.get("legend", "凡例"))
    caption = escape(tree.get("caption", "図：体系的位置づけ"))

    # SVG ノード群を組み立て
    svg_parts: list[str] = []

    # 凡例
    svg_parts.append(f'      <g transform="translate(20, 14)"><text class="tx-legend">{legend}</text></g>')

    # L0 ノード
    for node in tree.get("l0_nodes", []):
        x, y, label = node["x"], node["y"], escape(node["label"])
        svg_parts.append(
            f'      <g transform="translate({x}, {y})">'
            f'<rect class="l0-fill" x="-80" y="-20" width="160" height="40" rx="10"/>'
            f'<text class="tx-l0" text-anchor="middle" y="5">{label}</text></g>'
        )

    # L1/L2/L3 ノード
    for cls_short, level in (("l1", "l1"), ("l2", "l2"), ("l3", "l3")):
        for node in tree.get(f"{level}_nodes", []):
            x, y, label = node["x"], node["y"], escape(node["label"])
            fill_class = f"{level}-active" if node.get("active") else f"{level}-fill"
            tx_class = f"tx-{level}"
            svg_parts.append(
                f'      <g transform="translate({x}, {y})">'
                f'<rect class="{fill_class}" x="-60" y="-15" width="120" height="30" rx="6"/>'
                f'<text class="{tx_class}" text-anchor="middle" y="4">{label}</text></g>'
            )

    # 接続線（簡易版：parent_idx を持つノードは parent と結線）
    # 実装は問題側で line データを渡す方が柔軟。ここでは省略可（problem JSON に lines 配列があれば描画）
    for line in tree.get("lines", []):
        svg_parts.append(
            f'      <line class="connect" x1="{line["x1"]}" y1="{line["y1"]}" '
            f'x2="{line["x2"]}" y2="{line["y2"]}"/>'
        )

    # 本問の論点枠
    issue = tree.get("issue_box")
    if issue:
        ix, iy = issue["x"], issue["y"]
        title = escape(issue.get("title", "本問の論点"))
        body = escape(issue.get("body", ""))
        svg_parts.append(
            f'      <g transform="translate({ix}, {iy})">'
            f'<rect class="issue-fill" x="-80" y="-25" width="160" height="50" rx="12"/>'
            f'<text class="tx-issue-ttl" text-anchor="middle" y="-4">{title}</text>'
            f'<text class="tx-issue-body" text-anchor="middle" y="14">{body}</text></g>'
        )

        # 破線矢印（issue_box → l3-active）
        arrow = issue.get("arrow")
        if arrow:
            svg_parts.append(
                f'      <line class="issue-arrow" x1="{arrow["x1"]}" y1="{arrow["y1"]}" '
                f'x2="{arrow["x2"]}" y2="{arrow["y2"]}" marker-end="url(#issueArr)"/>'
            )

    svg_body = "\n".join(svg_parts) if svg_parts else "      <!-- 構造ノード未指定 -->"

    return f'''  <section class="section" id="mindmap-tree">
    <nav class="sec-nav"><a href="#basis">↑参考</a><a href="#mindmap-radial">↓マインドマップ放射</a></nav>
    <h2 class="section-title"><span class="sec-icon">🌳</span>体系ツリー</h2>

    <div class="figure-wrap">
      <svg class="tree-svg" viewBox="{viewbox}"
           xmlns="http://www.w3.org/2000/svg"
           role="img" aria-label="{aria_label}">
        <defs>
          <marker id="issueArr" viewBox="0 0 10 10" refX="9" refY="5"
                  markerWidth="6" markerHeight="6" orient="auto">
            <path d="M2 1L8 5L2 9" fill="none" stroke="var(--mid-warm)"
                  stroke-width="1.4" stroke-linecap="round"/>
          </marker>
        </defs>

{svg_body}
      </svg>
      <p class="figure-caption">{caption}</p>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>'''


# ============================================================================
# v9.2.0 §22-radial 放射状マインドマップ SVG section 描画（S86 対応）
# ============================================================================

V92_RADIAL_BRANCH_POSITIONS = [
    # (idx, default_label, x, y) — 8 主要枝の標準配置
    (0, "保護法益",     550, 180),
    (1, "構成要件①",   780, 260),
    (2, "構成要件②",   900, 450),
    (3, "構成要件③",   780, 640),
    (4, "構成要件④",   550, 720),
    (5, "法定刑",       320, 640),
    # idx=6 は本問の論点（暖色独立）
    (7, "特別法均衡",   320, 260),
]


def render_mindmap_radial_v92(problem: dict) -> str:
    """problem.mindmap_radial フィールドから <section id="mindmap-radial"> を生成（v9.2.0）。

    期待 JSON フィールド：
        mindmap_radial:
          center_label: 中心法理（例「詐欺罪体系」）
          aria_label: SVG aria-label
          legend: 凡例テキスト
          branches: [{label, x, y, sub_nodes: [{type:'statute'|'case'|'elem', label, x, y}]}]
                    7 件（保護法益／構成要件①〜④／法定刑／特別法均衡）
          issue_branch: {label, body, x, y}
          correct: 正解表示（例「正解：4（イウ）」）
          caption: 図キャプション
    """
    radial = problem.get("mindmap_radial")
    if not radial:
        return ""
    radial = auto_layout_radial(radial)  # Phase 13A: 座標未指定なら auto-layout

    center = escape(radial.get("center_label", "[中心法理]"))
    aria_label = escape(radial.get("aria_label", "[本問テーマ] の体系（8 主要枝）"))
    legend = escape(radial.get("legend", "凡例"))
    caption = escape(radial.get("caption", "図：本問テーマの体系"))
    correct = escape(radial.get("correct", ""))

    svg_parts: list[str] = []

    # 凡例
    svg_parts.append(f'      <g transform="translate(20, 16)"><text class="tx-legend">{legend}</text></g>')

    # 中心ノード
    svg_parts.append(
        '      <g transform="translate(550, 450)">'
        '<ellipse rx="120" ry="60" fill="url(#centerGrad)" stroke="var(--accent)" stroke-width="1.5"/>'
        f'<text class="tx-center" text-anchor="middle" y="7">{center}</text></g>'
    )

    # 7 主要枝 + サブノード
    branches = radial.get("branches", [])
    for i, branch in enumerate(branches[:7]):
        bx = branch.get("x", V92_RADIAL_BRANCH_POSITIONS[i][2] if i < len(V92_RADIAL_BRANCH_POSITIONS) else 550)
        by = branch.get("y", V92_RADIAL_BRANCH_POSITIONS[i][3] if i < len(V92_RADIAL_BRANCH_POSITIONS) else 450)
        blabel = escape(branch.get("label", f"[枝{i+1}]"))
        svg_parts.append(
            f'      <g transform="translate({bx}, {by})">'
            f'<rect class="branch-fill" x="-100" y="-30" width="200" height="60" rx="8"/>'
            f'<text class="tx-branch" text-anchor="middle" y="6">{blabel}</text></g>'
        )
        # 中心 → 主要枝 line-main
        svg_parts.append(
            f'      <line class="line-main" x1="550" y1="450" x2="{bx}" y2="{by}"/>'
        )
        # サブノード
        for sub in branch.get("sub_nodes", []):
            sx, sy = sub.get("x", bx), sub.get("y", by - 50)
            stype = sub.get("type", "elem")
            slabel = escape(sub.get("label", "[sub]"))
            cls_map = {"statute": ("sub-statute", "tx-statute"), "case": ("sub-case", "tx-case"), "elem": ("sub-elem", "tx-elem")}
            rect_cls, text_cls = cls_map.get(stype, cls_map["elem"])
            svg_parts.append(
                f'      <g transform="translate({sx}, {sy})">'
                f'<rect class="{rect_cls}" x="-70" y="-17" width="140" height="34" rx="4"/>'
                f'<text class="{text_cls}" text-anchor="middle" y="5">{slabel}</text></g>'
            )
            svg_parts.append(
                f'      <line class="line-sub" x1="{bx}" y1="{by}" x2="{sx}" y2="{sy}"/>'
            )

    # 本問の論点枝
    issue = radial.get("issue_branch")
    if issue:
        ix, iy = issue.get("x", 200), issue.get("y", 450)
        ititle = escape(issue.get("label", "本問の論点"))
        ibody = escape(issue.get("body", ""))
        svg_parts.append(
            f'      <g transform="translate({ix}, {iy})">'
            f'<rect class="issue-branch-fill" x="-110" y="-35" width="220" height="70" rx="12"/>'
            f'<text class="tx-issue" text-anchor="middle" y="-6">{ititle}</text>'
            f'<text class="tx-issue-body" text-anchor="middle" y="14">{ibody}</text></g>'
        )
        # 中心 → 本問の論点枝 line-issue（強調）
        svg_parts.append(
            f'      <line class="line-issue" x1="550" y1="450" x2="{ix}" y2="{iy}"/>'
        )

    # 正解表示
    if correct:
        svg_parts.append(
            f'      <g transform="translate(550, 870)">'
            f'<text class="tx-correct" text-anchor="middle">{correct}</text></g>'
        )

    svg_body = "\n".join(svg_parts)

    return f'''  <section class="section" id="mindmap-radial">
    <nav class="sec-nav"><a href="#mindmap-tree">↑マインドマップツリー</a><a href="#c-1">↓C-1</a></nav>
    <h2 class="section-title"><span class="sec-icon">🧭</span>論点マインドマップ</h2>

    <div class="figure-wrap">
      <svg class="radial-svg" viewBox="0 0 1200 1000"
           xmlns="http://www.w3.org/2000/svg"
           role="img" aria-label="{aria_label}">
        <defs>
          <linearGradient id="centerGrad" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0" stop-color="var(--accent)"/>
            <stop offset="1" stop-color="var(--accent-darker)"/>
          </linearGradient>
        </defs>

{svg_body}
      </svg>
      <p class="figure-caption">{caption}</p>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>'''


# ============================================================================
# v9.2.0 §22-flowchart-v2 分岐型フローチャート SVG 描画（S87 対応）
# ============================================================================

def render_flowchart_v2(problem: dict) -> str:
    """problem.flowchart_v2 フィールドから flow-svg ブロックを生成（v9.2.0）。

    既存 § C-5 stub と置換すべき SVG ブロック（<svg>...</svg> + figure-caption）。
    既存 render_c5_flowchart の戻り値と排他的に使用される（spec_version 分岐）。

    期待 JSON フィールド：
        flowchart_v2:
          aria_label: SVG aria-label
          viewbox: "0 0 900 800" 等（3 パターン）
          legend: 凡例
          start_label: START ノードのラベル（既定 "START"）
          decisions: [{cy, label, yn_pos: {yes_x, yes_y, no_x, no_y}}]
          chips: [{cx, cy, label}]
          end_success: {cx, cy}
          end_fails: [{cx, cy}]
          caption: 図キャプション
    """
    flow = problem.get("flowchart_v2")
    if not flow:
        return ""
    flow = auto_layout_flowchart(flow)  # Phase 13A: 座標未指定なら auto-layout

    aria_label = escape(flow.get("aria_label", "[本問テーマ] の成否判定フロー"))
    viewbox = flow.get("viewbox", "0 0 900 800")
    legend = escape(flow.get("legend", "凡例"))
    caption = escape(flow.get("caption", "図：成否判定フロー"))
    start_label = escape(flow.get("start_label", "START"))

    svg_parts: list[str] = []

    # 凡例
    svg_parts.append(f'        <g transform="translate(20, 14)"><text>{legend}</text></g>')

    # START
    svg_parts.append(
        '        <g transform="translate(450, 65)">'
        '<rect class="flow-start" x="-75" y="-25" width="150" height="50" rx="10"/>'
        f'<text class="tx-start" text-anchor="middle" y="6">{start_label}</text></g>'
    )

    # Decisions
    prev_y = 90
    for decision in flow.get("decisions", []):
        cy = decision["cy"]
        label = escape(decision["label"])
        svg_parts.append(
            f'        <g transform="translate(450, {cy})">'
            f'<polygon class="flow-decision" points="-90,0 0,-60 90,0 0,60"/>'
            f'<text class="tx-decision" text-anchor="middle" y="6">{label}</text></g>'
        )
        # 接続線（前ノード → Decision）
        svg_parts.append(
            f'        <line class="flow-line" x1="450" y1="{prev_y}" x2="450" y2="{cy - 60}" marker-end="url(#flowArr)"/>'
        )
        prev_y = cy + 60

    # Yes/No ラベルは decisions 内 yn_pos を直接 text 出力（簡略実装）
    for decision in flow.get("decisions", []):
        yn = decision.get("yn_pos", {})
        if yn.get("yes_x") is not None:
            svg_parts.append(
                f'        <text class="tx-yn" x="{yn["yes_x"]}" y="{yn["yes_y"]}">Yes</text>'
            )
        if yn.get("no_x") is not None:
            svg_parts.append(
                f'        <text class="tx-yn" x="{yn["no_x"]}" y="{yn["no_y"]}">No</text>'
            )

    # 肢マーカー
    for chip in flow.get("chips", []):
        svg_parts.append(
            f'        <g transform="translate({chip["cx"]}, {chip["cy"]})">'
            f'<rect class="flow-chip" x="-30" y="-11" width="60" height="22" rx="11"/>'
            f'<text class="tx-chip" text-anchor="middle" y="4">{escape(chip["label"])}</text></g>'
        )

    # 終端：成立（end_success_label が指定されていればそれを表示・既定「成立」）
    end_success = flow.get("end_success")
    if end_success:
        es_label = escape(flow.get("end_success_label", "成立"))
        svg_parts.append(
            f'        <g transform="translate({end_success["cx"]}, {end_success["cy"]})">'
            f'<rect class="flow-end-success" x="-80" y="-25" width="160" height="50" rx="10"/>'
            f'<text class="tx-end" text-anchor="middle" y="6">{es_label}</text></g>'
        )

    # 終端：不成立（複数可・end_fail_labels が指定されていればラベルを順次適用）
    end_fails = flow.get("end_fails", [])
    fail_labels = flow.get("end_fail_labels", [])
    for i, end_fail in enumerate(end_fails):
        label = escape(fail_labels[i]) if i < len(fail_labels) else "不成立"
        svg_parts.append(
            f'        <g transform="translate({end_fail["cx"]}, {end_fail["cy"]})">'
            f'<rect class="flow-end-fail" x="-80" y="-25" width="160" height="50" rx="10"/>'
            f'<text class="tx-end" text-anchor="middle" y="6">{label}</text></g>'
        )

    svg_body = "\n".join(svg_parts)

    return f'''      <svg class="flow-svg" viewBox="{viewbox}"
           xmlns="http://www.w3.org/2000/svg"
           role="img" aria-label="{aria_label}">
        <defs>
          <marker id="flowArr" viewBox="0 0 10 10" refX="9" refY="5"
                  markerWidth="6" markerHeight="6" orient="auto">
            <path d="M2 1L8 5L2 9" fill="none" stroke="var(--bg-dark)"
                  stroke-width="1.4" stroke-linecap="round"/>
          </marker>
        </defs>

{svg_body}
      </svg>
      <p class="figure-caption">{caption}</p>'''


# ============================================================================
# v9.2.0 §17-ter 学説対立 deep-dive 描画（S89 対応）
# ============================================================================

def render_theory_deep_dive(problem: dict) -> str:
    """problem.theory_deep_dive フィールドから theory-detail-grid + statute-interpretation を生成。

    期待 JSON フィールド：
        theory_deep_dive:
          is_theory_selection: True（学説問題型）/False
          major: {name, conclusion, basis, why_adopted, response_to_criticism}
          minor: {name, conclusion, basis, why_not_adopted, practical_problem}
          statute: {num, text, interpretation}
          axis_fig: {svg, caption} 任意

    is_theory_selection=True の場合、c-4 section に data-question-type 属性追加（呼出側）。
    """
    theory = problem.get("theory_deep_dive")
    if not theory:
        return ""

    major = theory.get("major", {})
    minor = theory.get("minor", {})
    statute = theory.get("statute", {})

    grid_html = f'''<div class="theory-detail-grid">
      <div class="sub-card theory-major">
        <h3 class="theory-heading">
          <span class="theory-badge">通説/判例</span>{escape(major.get("name", "[学説名]"))}
        </h3>
        <dl class="theory-dl">
          <dt>結論</dt>
          <dd>{escape(major.get("conclusion", ""))}</dd>
          <dt>論拠</dt>
          <dd>{escape(major.get("basis", ""))}</dd>
          <dt class="why-adopted">判例が採用する理由</dt>
          <dd>{escape(major.get("why_adopted", ""))}</dd>
          <dt>批判への応答</dt>
          <dd>{escape(major.get("response_to_criticism", ""))}</dd>
        </dl>
      </div>
      <div class="sub-card theory-minor">
        <h3 class="theory-heading">
          <span class="theory-badge">少数説</span>{escape(minor.get("name", "[学説名]"))}
        </h3>
        <dl class="theory-dl">
          <dt>結論</dt>
          <dd>{escape(minor.get("conclusion", ""))}</dd>
          <dt>論拠</dt>
          <dd>{escape(minor.get("basis", ""))}</dd>
          <dt class="why-not-adopted">判例が採用しない理由</dt>
          <dd>{escape(minor.get("why_not_adopted", ""))}</dd>
          <dt>実務上の問題点</dt>
          <dd>{escape(minor.get("practical_problem", ""))}</dd>
        </dl>
      </div>
    </div>'''

    axis_html = ""
    axis_fig = theory.get("axis_fig")
    if axis_fig and axis_fig.get("svg"):
        # SVG は事前にレンダー済の文字列を期待
        axis_html = f'''
    <div class="theory-axis-fig">
{axis_fig["svg"]}
      <p class="figure-caption">{escape(axis_fig.get("caption", "図：学説対立の 2 軸分析"))}</p>
    </div>'''

    statute_html = ""
    if statute:
        statute_html = f'''
    <blockquote class="statute-interpretation">
      <p class="statute-cite"><span class="statute-num">{escape(statute.get("num", ""))}</span> {escape(statute.get("text", ""))}</p>
      <p class="interpretation-body">{escape(statute.get("interpretation", ""))}</p>
    </blockquote>'''

    return f"    {grid_html}{axis_html}{statute_html}"


# ============================================================================
# v9.2.0 教授解説密度 v2 prof-heading 描画（S91 対応）
# ============================================================================

def render_c5_flowchart_v92(problem: dict) -> str:
    """v9.2.0 専用：c-5 section 全体 inner content（nav + h2 + key-phrase + flow-svg + 鉄則 + back-to-top）を生成。

    既存 render_c5_flowchart の v9.2.0 版置換。flowchart_v2 フィールドから flow-svg を生成。
    """
    flow_svg_block = render_flowchart_v2(problem)
    if not flow_svg_block:
        # flowchart_v2 未定義 → stub 維持
        return PART_C_STUBS["C5_FLOWCHART"]

    # key-phrase（任意）
    flow_data = problem.get("flowchart_v2", {})
    intro = flow_data.get("intro_key_phrase_html", "")
    rules = flow_data.get("rules", {})

    parts = [
        '    <nav class="sec-nav"><a href="#c-4">←C-4</a><a href="#c-6">C-6→</a></nav>',
        '    <h2 class="section-title"><span class="sec-icon">🗺</span>C-5 総合フローチャート</h2>',
    ]
    if intro:
        parts.append("")
        parts.append(f'    <div class="key-phrase-box">\n      {intro}\n    </div>')
    parts.append("")
    parts.append('    <div class="figure-wrap">')
    # flow_svg_block は既に "      <svg ...>...\n      <p class=\"figure-caption\">...</p>" 形式
    parts.append(flow_svg_block)
    parts.append('    </div>')

    if rules.get("items"):
        parts.append("")
        if rules.get("title"):
            parts.append(f'    <h3>{escape(rules["title"])}</h3>')
        parts.append('    <ul class="lead-list">')
        for item in rules["items"]:
            parts.append(f'      <li>{item}</li>')
        parts.append('    </ul>')

    parts.extend(["", _BACK_TO_TOP])
    return "\n".join(parts)


def inject_theory_into_c4(c4_html: str, theory_html: str) -> str:
    """C4_DOCTRINES 内の back-to-top の直前に theory-detail-grid を挿入する（v9.2.0）。"""
    if not theory_html:
        return c4_html
    # _BACK_TO_TOP は固定文字列 — その直前に theory を挿入
    if _BACK_TO_TOP in c4_html:
        return c4_html.replace(_BACK_TO_TOP, theory_html + "\n" + _BACK_TO_TOP)
    # back-to-top が見つからない場合（stub 等）：末尾に append
    return c4_html + "\n" + theory_html


def render_professor_density_v2(prof: dict) -> str:
    """professor-density-v2 構造の 4 prof-heading を生成。

    期待 JSON フィールド（choices[*].professor 内）：
        point: {list: [str, str, str], locus: str}
        process: {steps: [str, str, str, str]}
        image: {scene: str, bridge: str, contrast: str}
        application: {major: str, minor: str, conclusion: str}

    既存の summary/note 構造（v9.1.0）とは並存可能（呼出側で spec_version 判定）。
    """
    if not prof:
        return ""

    point = prof.get("point", {})
    process = prof.get("process", {})
    image = prof.get("image", {})
    application = prof.get("application", {})

    point_list_items = "\n          ".join(
        f"<li>{escape(item)}</li>" for item in point.get("list", [])
    )
    process_step_items = "\n          ".join(
        f"<li>{escape(step)}</li>" for step in process.get("steps", [])
    )

    return f'''      <div class="prof-heading prof-point">
        <h4>ポイント</h4>
        <ul class="point-list">
          {point_list_items}
        </ul>
        <p class="point-locus">{escape(point.get("locus", ""))}</p>
      </div>
      <div class="prof-heading prof-process">
        <h4>考え方の道筋</h4>
        <ol class="process-steps">
          {process_step_items}
        </ol>
      </div>
      <div class="prof-heading prof-image">
        <h4>イメージで掴む</h4>
        <div class="image-scene">
          <h5 class="img-sub">具体場面</h5>
          <p>{escape(image.get("scene", ""))}</p>
        </div>
        <div class="image-bridge">
          <h5 class="img-sub">規範への接続</h5>
          <p>{escape(image.get("bridge", ""))}</p>
        </div>
        <div class="image-contrast">
          <h5 class="img-sub">反対結論との対比</h5>
          <p>{escape(image.get("contrast", ""))}</p>
        </div>
      </div>
      <div class="prof-heading prof-application">
        <h4>あてはめ</h4>
        <div class="syllogism">
          <div class="syl-major">
            <h5 class="img-sub">大前提（規範）</h5>
            <p>{escape(application.get("major", ""))}</p>
          </div>
          <div class="syl-minor">
            <h5 class="img-sub">小前提（事実）</h5>
            <p>{escape(application.get("minor", ""))}</p>
          </div>
          <div class="syl-conclusion">
            <h5 class="img-sub">結論</h5>
            <p>{escape(application.get("conclusion", ""))}</p>
          </div>
        </div>
      </div>'''


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
# pre_part_a 描画関数（Phase 4-9・A+C 組合せ・Phase 4-6 TOC 同形）
# ============================================================================
# 8 templates の diff-allowed 領域 pre_part_a (4 lines / 194-237 bytes、8 templates ×
# 8 variants で完全 1:1 対応) を集約 slot 化。各 variant は HTML コメント内の form 名
# 文字列のみが可変、固定の前後コメント枠 (universal) と組み合わせて出力。
#
# 設計判断（BACKLOG §2-1、ユーザ採択）:
# - schema 変更なし、JSON 改修なし（既存 problem.instruction_type から派生）
# - 未対応 instruction_type は RuntimeError raise（Phase 4-6 TOC 同方針、silent
#   fallback 不採用）
# - broken intermediate state なし（diff-allowed 領域、旧 slot 不在）

PRE_PART_A_FORM_NAMES_BY_TYPE: dict[str, str] = {
    "ox-grid-5":               "ox-grid-5 形式",
    "ox-grid-4":               "ox-grid-4 形式",
    "ox-grid-3-combination-8": "ox-grid-3 + combination-8 形式",
    "multi-select-5":          "multi-select-5 形式",
    "single-choice-5":         "single-choice-5 形式",
    "combination-5":           "combination-5 形式",
    "fill-in":                 "fill-in 形式",
    "fillin8":                 "fillin8 形式：8 blanks 表示 + 5 options 単一選択",
}


def render_pre_part_a(instruction_type: str) -> str:
    """{{PRE_PART_A}} slot 値を返す（instruction_type 派生）。未対応 type で RuntimeError。"""
    if instruction_type not in PRE_PART_A_FORM_NAMES_BY_TYPE:
        raise RuntimeError(
            f"unknown instruction_type {instruction_type!r} for pre_part_a. "
            f"valid: {sorted(PRE_PART_A_FORM_NAMES_BY_TYPE)}"
        )
    form_name = PRE_PART_A_FORM_NAMES_BY_TYPE[instruction_type]
    return (
        '\n'
        '  <!-- ============================================================\n'
        f'       PART A ── 問題情報（{form_name}）\n'
        '       ============================================================ -->'
    )


# ============================================================================
# head 領域描画関数（Phase 4-10・C refined・Phase 4-8 body_pre_toc 同形）
# ============================================================================
# 8 templates の sync-required head 領域 (867 bytes / 9 lines) を集約 slot 化。
# universal な HTML 構造 (DOCTYPE / html / head / meta / link) + <title> 行内に
# 4 個の動的値 (JP_PREFIX/PROBLEM_ID/CRIME/SOURCE_ID) を含むため、Phase 4-8
# body_pre_toc と同形の Python .format() 名前付き placeholder 拡張を採択。
#
# 設計判断（BACKLOG §2-1、Phase 4-8 同方針）:
# - schema 変更なし、JSON 改修なし（既存 4 slot 値を流用）
# - 旧 4 slot ({{JP_PREFIX}}/{{PROBLEM_ID}}/{{CRIME}}/{{SOURCE_ID}}) は据え置き
#   （body_pre_toc / footer-spec で他参照あり削除不可）
# - escape 旧仕様踏襲（Phase 4-7/4-8 と同一）
# - broken intermediate state なし（旧 slot 据え置きのため）
# - font URL に `{`/`}` リテラル不在を確認 → `.format()` 安全

HEAD_TEMPLATE: str = (
    '<!DOCTYPE html>\n'
    '<html lang="ja">\n'
    '<head>\n'
    '<meta charset="UTF-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    '<title>{jp_prefix}{problem_id} - {crime}（{source_id}）</title>\n'
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@400;500;700;800&family=Shippori+Antique&family=Zen+Old+Mincho:wght@400;500;700;900&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Zen+Maru+Gothic:wght@400;500;700&family=Noto+Serif+JP:wght@400;500;700&family=Noto+Sans+JP:wght@400;500;700&family=Kaisei+Decol:wght@400;500;700&family=Kosugi+Maru&family=Source+Code+Pro:wght@400;600;700&family=M+PLUS+Rounded+1c:wght@500;700;800&family=M+PLUS+1p:wght@500;700;800;900&display=swap" rel="stylesheet">'
)


def render_head(problem: dict) -> str:
    """{{HEAD}} slot 値を返す（Python .format() で 4 動的値を埋込）。"""
    subject = problem.get("subject", "KEI")
    jp_prefix = SUBJECT_TO_JP[subject] + "TX"
    return HEAD_TEMPLATE.format(
        jp_prefix=jp_prefix,
        problem_id=str(problem.get("id", "")),
        crime=str(problem.get("crime", "")),
        source_id=str(problem.get("source", "")),
    )


# ============================================================================
# basis 領域 sec-nav 描画関数（Phase 4-11・A+C 組合せ・Phase 4-6/4-9 機械的踏襲）
# ============================================================================
# basis section の第 2 行 <nav class="sec-nav"> 内の back-link 1 つだけが
# instruction_type 別に可変。universal 枠 (nav wrapper + C-1 link) は固定。
# A+C 組合せの 3 例目、Phase 4-6 TOC / Phase 4-9 pre_part_a と完全同形の
# dispatch ロジックを機械的踏襲。
#
# 設計判断（BACKLOG §2-1、Phase 4-6/4-9 同方針）:
# - schema 変更なし、JSON 改修なし（既存 problem.instruction_type から派生）
# - 未対応 instruction_type で RuntimeError raise（silent fallback 不採用）
# - broken intermediate state なし（diff-allowed 領域、旧 slot 不在）

BASIS_SECNAV_LINKS_BY_TYPE: dict[str, str] = {
    "ox-grid-5":               '<a href="#choice-5">↑記述オ</a>',
    "ox-grid-4":               '<a href="#choice-4">↑記述エ</a>',
    "ox-grid-3-combination-8": '<a href="#choice-3">↑記述ウ</a>',
    "multi-select-5":          '<a href="#choice-5">↑記述5</a>',
    "single-choice-5":         '<a href="#choice-5">↑記述5</a>',
    "combination-5":           '<a href="#choice-5">↑記述オ</a>',
    "fill-in":                 '<a href="#choice-5">↑空欄E</a>',
    "fillin8":                 '<a href="#choice-5">↑肢5</a>',
}


def render_basis_secnav(instruction_type: str) -> str:
    """{{BASIS_SECNAV}} slot 値を返す（instruction_type 派生）。未対応 type で RuntimeError。"""
    if instruction_type not in BASIS_SECNAV_LINKS_BY_TYPE:
        raise RuntimeError(
            f"unknown instruction_type {instruction_type!r} for basis sec-nav. "
            f"valid: {sorted(BASIS_SECNAV_LINKS_BY_TYPE)}"
        )
    back_link = BASIS_SECNAV_LINKS_BY_TYPE[instruction_type]
    return f'    <nav class="sec-nav">{back_link}<a href="#c-1">↓C-1</a></nav>'


# ============================================================================
# part_a 領域描画関数（Phase 4-12・パターン E 新規確立: A+C + 局所 D）
# ============================================================================
# 8 templates の diff-allowed part_a 領域（avg 1,515 bytes / 19〜52 lines、
# 8 templates × 8 variants）を集約 slot 化。
#
# 5 つの可変軸（BACKLOG §1-2）:
#   1. sec_nav_back  (dict 派生)        — A-1 nav 内 back-link
#   2. h3_title      (dict 派生)        — 記述 H3 見出し（【記述】/【空欄】/【選択肢】）
#   3. choice_lines  (件数別関数生成)   — problem-text の件数 (3/4/5)
#   4. combo_section (件数別関数生成・D 局所) — 【組合せ】section (0/5/8 件)
#   5. middle_line   (2 値分岐)         — sc5 のみ {{VIEWS_BLOCK}} 行
#
# 軸 1/2/3/5 は A+C 組合せ、軸 4 のみ件数可変のため局所 D（配列駆動）を併用。
# A/B/C/D 単独でも、A+C 組合せでも捕捉できない新形態 → パターン E として新規確立。
#
# 設計判断（BACKLOG §2-1）:
# - schema 変更なし、JSON 改修なし（既存 problem.instruction_type から派生）
# - 未対応 instruction_type は RuntimeError raise（Phase 4-6/4-9/4-11 同方針）
# - broken intermediate state なし（diff-allowed 領域、旧 slot 不在）
# - PART_A_FRAME_TEMPLATE は Python .format() 名前付き placeholder、6 引数
#   {{INSTRUCTION}} 等 slot 参照は {{{{INSTRUCTION}}}} 形式でエスケープ

PART_A_H3_STYLE: str = (
    'background:transparent; border-left:none; padding:8px 0 4px 0;'
    ' margin:20px 0 8px 0; border-bottom:2px dotted var(--border-mid);'
    ' color:var(--accent); font-family:var(--font-display);'
)

# instruction_type → 5 軸の値（軸 5 has_views_block は bool、他は派生用 raw 値）
PART_A_AXES_BY_TYPE: dict[str, dict] = {
    "ox-grid-5": {
        "sec_nav_back":    '<a href="#choice-1">↓記述ア</a>',
        "h3_title":        "【記述】",
        "choice_count":    5,
        "combo_count":     0,
        "has_views_block": False,
    },
    "ox-grid-4": {
        "sec_nav_back":    '<a href="#choice-1">↓記述ア</a>',
        "h3_title":        "【記述】",
        "choice_count":    4,
        "combo_count":     0,
        "has_views_block": False,
    },
    "ox-grid-3-combination-8": {
        "sec_nav_back":    '<a href="#choice-1">↓記述ア</a>',
        "h3_title":        "【記述】",
        "choice_count":    3,
        "combo_count":     8,
        "has_views_block": False,
    },
    "multi-select-5": {
        "sec_nav_back":    '<a href="#choice-1">↓記述1</a>',
        "h3_title":        "【記述】",
        "choice_count":    5,
        "combo_count":     0,
        "has_views_block": False,
    },
    "single-choice-5": {
        "sec_nav_back":    '<a href="#choice-1">↓記述1</a>',
        "h3_title":        "【記述】",
        "choice_count":    5,
        "combo_count":     0,
        "has_views_block": True,  # sc5 のみ {{VIEWS_BLOCK}} 行を含む（Phase 4-1）
    },
    "combination-5": {
        "sec_nav_back":    '<a href="#choice-1">↓記述ア</a>',
        "h3_title":        "【記述】",
        "choice_count":    5,
        "combo_count":     5,
        "has_views_block": False,
    },
    "fill-in": {
        "sec_nav_back":    '<a href="#choice-1">↓空欄A</a>',
        "h3_title":        "【空欄】",
        "choice_count":    5,
        "combo_count":     0,
        "has_views_block": False,
    },
    "fillin8": {
        "sec_nav_back":    '<a href="#choice-1">↓肢1</a>',
        "h3_title":        "【選択肢】",
        "choice_count":    5,
        "combo_count":     0,
        "has_views_block": False,
    },
}

# .format() 名前付き placeholder。{{INSTRUCTION}} 等の slot 参照は {{{{...}}}}
# でエスケープ（.format() 通過後に {{INSTRUCTION}} 形式で残り、main render の
# slot 置換に渡される）。
PART_A_FRAME_TEMPLATE: str = (
    '  <div class="part-title">PART A ── 問題情報</div>\n'
    '\n'
    '  <section class="section" id="part-a">\n'
    '    <nav class="sec-nav"><a href="#answer-area">↓解答</a>{sec_nav_back}</nav>\n'
    '    <h2 class="section-title"><span class="sec-icon">❀</span>A-1 問題文</h2>\n'
    '\n'
    '    <p style="font-weight:600;">{{{{INSTRUCTION}}}}</p>\n'
    '\n'
    '    {{{{CASE_BODY}}}}\n'
    '{middle_line}'
    '    <h3 style="{h3_style}">{h3_title}</h3>\n'
    '\n'
    '{choice_lines}'
    '{combo_section}'
    '\n'
    '    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>\n'
    '  </section>'
)


def _build_part_a_choice_lines(n: int) -> str:
    """N 件 (3/4/5) の problem-text 行を生成（{{CHOICE_X_LABEL}}/{{CHOICE_X_STEM}} は raw 保持）。"""
    letters = "ABCDE"[:n]
    return "".join(
        f'    <div class="problem-text"><span class="choice-num-inline">'
        f'{{{{CHOICE_{ltr}_LABEL}}}}</span>{{{{CHOICE_{ltr}_STEM}}}}</div>\n'
        for ltr in letters
    )


def _build_part_a_combo_section(n: int) -> str:
    """N 件 (0/5/8) の【組合せ】section を生成（D 局所配列駆動）。N=0 で空文字列。"""
    if n == 0:
        return ""
    blocks: list[str] = []
    for i in range(1, n + 1):
        blocks.append(
            '      <div class="combo-block">\n'
            f'        <span class="combo-label">{{{{COMBO_{i}_LABEL}}}}</span>\n'
            f'        <span class="combo-set">{{{{COMBO_{i}_SET}}}}</span>\n'
            '      </div>'
        )
    return (
        '\n'
        f'    <h3 style="{PART_A_H3_STYLE}">【組合せ】</h3>\n'
        '\n'
        '    <section class="combinations-section" id="part-a-combinations">\n'
        + "\n".join(blocks) + '\n'
        '    </section>\n'
    )


def render_part_a(instruction_type: str) -> str:
    """{{PART_A_FRAME}} slot 値を返す（パターン E: A+C dispatch + 局所 D 配列駆動）。

    軸 1/2/3/5 は dict 派生、軸 4 (combo_section) のみ件数別の関数生成。
    未対応 instruction_type で RuntimeError。
    """
    if instruction_type not in PART_A_AXES_BY_TYPE:
        raise RuntimeError(
            f"unknown instruction_type {instruction_type!r} for part_a. "
            f"valid: {sorted(PART_A_AXES_BY_TYPE)}"
        )
    axes = PART_A_AXES_BY_TYPE[instruction_type]
    middle_line = "{{VIEWS_BLOCK}}\n" if axes["has_views_block"] else "\n"
    choice_lines = _build_part_a_choice_lines(axes["choice_count"])
    combo_section = _build_part_a_combo_section(axes["combo_count"])
    return PART_A_FRAME_TEMPLATE.format(
        sec_nav_back=axes["sec_nav_back"],
        middle_line=middle_line,
        h3_style=PART_A_H3_STYLE,
        h3_title=axes["h3_title"],
        choice_lines=choice_lines,
        combo_section=combo_section,
    )


# ============================================================================
# a2 領域描画関数（Phase 4-13・パターン E 応用 1 例目: A+C + 局所 D + UI 種別 dispatch）
# ============================================================================
# 8 templates の diff-allowed a2 領域（avg 1,643 bytes / 25〜60 lines、8 templates ×
# 8 variants）を集約 slot 化。
#
# 6 つの可変軸（BACKLOG §1-2）:
#   1. sec_nav_back            (dict 派生)        — A-2 nav 内 back-link
#   2. data_answer_type        (dict 派生)        — answer-area attribute 値
#   3. h3_title                (dict 派生)        — answer-area H3 見出し
#   4. answer_instruction      (dict 派生)        — answer-instruction 文言
#   5. selection_counter_line  (2 値分岐)         — msel5 のみ 1 行 in
#   6. ui_block                (件数別関数生成・D 局所 + UI 種別 dispatch)
#                                                  — answer UI 構造（ox-grid / slot-row）
#                                                    × 件数 (4/5/8) × ラベル系 (digit / A〜E)
#
# 軸 1〜5 は A+C 組合せ、軸 6 のみ件数・block 種別・ラベル可変のため局所 D（配列駆動）
# + UI 種別 dispatch（2 builder の切替）を併用。Phase 4-12 part_a で確立した
# パターン E の応用 1 例目。
#
# 設計判断（BACKLOG §2-1）:
# - schema 変更なし、JSON 改修なし（既存 problem.instruction_type から派生）
# - 未対応 instruction_type は RuntimeError raise（Phase 4-6/4-9/4-11/4-12 同方針）
# - broken intermediate state なし（diff-allowed 領域、旧 slot 不在）
# - A2_FRAME_TEMPLATE は Python .format() 名前付き placeholder、6 引数
#   {{ANSWER}} 等 slot 参照は {{{{ANSWER}}}} 形式でエスケープ
#   answer_instruction 値内の {{SELECTION_COUNT}} は値として渡るため二重エスケープ不要

# instruction_type → 6 軸の値（軸 5 has_selection_counter は bool、他は派生用 raw 値）
A2_AXES_BY_TYPE: dict[str, dict] = {
    "ox-grid-5": {
        "sec_nav_back":           '<a href="#choice-1">↓記述ア</a>',
        "data_answer_type":       "ox-grid",
        "h3_title":               "各記述の正誤を判定",
        "answer_instruction":     "各記述に「1（正）」または「2（誤）」を選んで「解答を表示」を押してください。",
        "has_selection_counter":  False,
        "ui_kind":                "ox-grid",
        "ui_count":               5,
        "ui_labels":              None,  # ox-grid モードでは未使用
    },
    "ox-grid-4": {
        "sec_nav_back":           '<a href="#choice-1">↓記述ア</a>',
        "data_answer_type":       "ox-grid",
        "h3_title":               "各記述の正誤を判定",
        "answer_instruction":     "各記述に「1（正）」または「2（誤）」を選んで「解答を表示」を押してください。",
        "has_selection_counter":  False,
        "ui_kind":                "ox-grid",
        "ui_count":               4,
        "ui_labels":              None,
    },
    "ox-grid-3-combination-8": {
        "sec_nav_back":           '<a href="#choice-1">↓記述ア</a>',
        "data_answer_type":       "ox3comb8",
        "h3_title":               "正しい組合せを選択",
        "answer_instruction":     "選択肢を選んで「解答を表示」を押してください。",
        "has_selection_counter":  False,
        "ui_kind":                "slot-row",
        "ui_count":               8,
        "ui_labels":              ["1", "2", "3", "4", "5", "6", "7", "8"],
    },
    "multi-select-5": {
        "sec_nav_back":           '<a href="#choice-1">↓記述1</a>',
        "data_answer_type":       "multi",
        "h3_title":               "該当する選択肢を選択",
        "answer_instruction":     "選択肢を{{SELECTION_COUNT}}個選んで「解答を表示」を押してください。",
        "has_selection_counter":  True,  # msel5 のみ <p class="selection-counter"> 行を含む
        "ui_kind":                "slot-row",
        "ui_count":               5,
        "ui_labels":              ["1", "2", "3", "4", "5"],
    },
    "single-choice-5": {
        "sec_nav_back":           '<a href="#choice-1">↓記述1</a>',
        "data_answer_type":       "single",
        "h3_title":               "該当する選択肢を選択",
        "answer_instruction":     "選択肢を選んで「解答を表示」を押してください。",
        "has_selection_counter":  False,
        "ui_kind":                "slot-row",
        "ui_count":               5,
        "ui_labels":              ["1", "2", "3", "4", "5"],
    },
    "combination-5": {
        "sec_nav_back":           '<a href="#choice-1">↓記述ア</a>',
        "data_answer_type":       "single",
        "h3_title":               "正しい記述の組合せを選択",
        "answer_instruction":     "選択肢を選んで「解答を表示」を押してください。",
        "has_selection_counter":  False,
        "ui_kind":                "slot-row",
        "ui_count":               5,
        "ui_labels":              ["1", "2", "3", "4", "5"],
    },
    "fill-in": {
        "sec_nav_back":           '<a href="#choice-1">↓空欄A</a>',
        "data_answer_type":       "fill-in",
        "h3_title":               "各空欄に該当する候補番号を確認",
        "answer_instruction":     "各空欄に入る候補を確認したら「解答を表示」を押してください。",
        "has_selection_counter":  False,
        "ui_kind":                "slot-row",
        "ui_count":               5,
        "ui_labels":              ["A", "B", "C", "D", "E"],
    },
    "fillin8": {
        "sec_nav_back":           '<a href="#choice-1">↓肢1</a>',
        "data_answer_type":       "single",
        "h3_title":               "正しい組合せを選択",
        "answer_instruction":     "選択肢を選んで「解答を表示」を押してください。",
        "has_selection_counter":  False,
        "ui_kind":                "slot-row",
        "ui_count":               5,
        "ui_labels":              ["1", "2", "3", "4", "5"],
    },
}

# .format() 名前付き placeholder。{{ANSWER}} 等の slot 参照は {{{{...}}}}
# でエスケープ（.format() 通過後に {{ANSWER}} 形式で残り、main render の
# slot 置換に渡される）。
A2_FRAME_TEMPLATE: str = (
    '  <section class="section" id="answer-area">\n'
    '    <nav class="sec-nav"><a href="#part-a">↑A-1</a>{sec_nav_back}</nav>\n'
    '    <h2 class="section-title"><span class="sec-icon">❀</span>A-2 解答</h2>\n'
    '\n'
    '    <div class="answer-area"\n'
    '         data-correct-value="{{{{ANSWER}}}}"\n'
    '         data-answer-type="{data_answer_type}"\n'
    '         data-explanation="{{{{ANSWER_EXPLANATION}}}}">\n'
    '      <h3>{h3_title}</h3>\n'
    '      <p class="answer-instruction">{answer_instruction}</p>\n'
    '{selection_counter_line}'
    '\n'
    '{ui_block}\n'
    '\n'
    '      <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>\n'
    '      <div id="answer-feedback" hidden></div>\n'
    '    </div>\n'
    '\n'
    '    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>\n'
    '  </section>'
)


def _build_a2_ox_grid_block(n: int) -> str:
    """N 件 (4/5) の ox-row を生成（{{CHOICE_X_LABEL}}/{{CHOICE_X_STEM}} は raw 保持）。"""
    letters = "ABCDE"[:n]
    rows = "\n".join(
        '        <div class="ox-row">\n'
        f'          <span class="ox-label">{{{{CHOICE_{ltr}_LABEL}}}}</span>\n'
        f'          <p class="ox-stmt">{{{{CHOICE_{ltr}_STEM}}}}</p>\n'
        '          <span class="ox-btn-group">\n'
        '            <button class="ox-btn" type="button" data-value="1">1 正しい</button>\n'
        '            <button class="ox-btn" type="button" data-value="2">2 誤っている</button>\n'
        '          </span>\n'
        '        </div>'
        for ltr in letters
    )
    return f'      <div class="answer-ox-grid">\n{rows}\n      </div>'


def _build_a2_slot_row_block(labels: list[str]) -> str:
    """labels 件分の answer-slot button を生成（labels は ["1",...,"N"] または ["A",...,"E"]）。"""
    buttons = "\n".join(
        f'        <button class="answer-slot" type="button" '
        f'data-num="{lbl}" data-value="{lbl}">{lbl}</button>'
        for lbl in labels
    )
    return f'      <div class="answer-row">\n{buttons}\n      </div>'


def render_a2(instruction_type: str) -> str:
    """{{A2_FRAME}} slot 値を返す（パターン E 応用: A+C dispatch + 局所 D 配列駆動 + UI 種別 dispatch）。

    軸 1〜5 は dict 派生、軸 6 (ui_block) のみ件数・block 種別・ラベル別の関数生成。
    未対応 instruction_type で RuntimeError。
    """
    if instruction_type not in A2_AXES_BY_TYPE:
        raise RuntimeError(
            f"unknown instruction_type {instruction_type!r} for a2. "
            f"valid: {sorted(A2_AXES_BY_TYPE)}"
        )
    axes = A2_AXES_BY_TYPE[instruction_type]

    # 軸 5: selection_counter_line (msel5 のみ 1 行 in)
    if axes["has_selection_counter"]:
        selection_counter_line = (
            '      <p class="selection-counter">選択数: 0 / {{SELECTION_COUNT}}</p>\n'
        )
    else:
        selection_counter_line = ""

    # 軸 6: ui_block (UI 種別 dispatch + 局所 D 配列駆動)
    if axes["ui_kind"] == "ox-grid":
        ui_block = _build_a2_ox_grid_block(axes["ui_count"])
    else:  # slot-row
        ui_block = _build_a2_slot_row_block(axes["ui_labels"])

    return A2_FRAME_TEMPLATE.format(
        sec_nav_back=axes["sec_nav_back"],
        data_answer_type=axes["data_answer_type"],
        h3_title=axes["h3_title"],
        answer_instruction=axes["answer_instruction"],
        selection_counter_line=selection_counter_line,
        ui_block=ui_block,
    )


# ============================================================================
# part_b 領域描画関数（Phase 4-14・パターン E 応用 2 例目: A+C + 局所 D）
# ============================================================================
# 8 templates の diff-allowed part_b 領域（最大規模、avg 5,530 bytes / 174-108 lines、
# 8 templates × 6 variants）を集約 slot 化。
#
# 3 つの可変軸（BACKLOG §1-2）:
#   1. noun         (dict 派生)       — 記述名詞（記述 / 空欄 / 肢、3 値）
#   2. labels       (dict 派生)       — ラベル系列（カナ ア-オ / 1-5 / A-E、6 系列）
#   3. count        (件数別関数生成・D 局所) — choice-section の繰返し回数 (= len(labels))
#
# 軸 1〜2 は A+C 組合せ、軸 3 のみ件数可変のため局所 D（配列駆動）を併用。
# Phase 4-12 part_a で確立したパターン E の応用 2 例目。Phase 4-13 a2 で必要だった
# UI 種別 dispatch（ox-grid / slot-row 2 builder 切替）は不要 — 全 variants が同一の
# choice-section 構造を共有するため builder は 1 つ。
#
# 設計判断（BACKLOG §2-1）:
# - schema 変更なし、JSON 改修なし（既存 problem.instruction_type から派生）
# - 未対応 instruction_type は RuntimeError raise（Phase 4-6/4-9/4-11/4-12/4-13 同方針）
# - broken intermediate state なし（diff-allowed 領域、旧 slot 不在）
# - PART_B_FRAME_TEMPLATE は Python .format() 名前付き placeholder、2 引数
# - {{CHOICE_X_*}} 等 slot 参照は {{{{...}}}} 形式でエスケープ

# instruction_type → 2 軸の値（noun: str / labels: list[str]、count は len(labels)）
PART_B_AXES_BY_TYPE: dict[str, dict] = {
    "ox-grid-5":               {"noun": "記述", "labels": ["ア", "イ", "ウ", "エ", "オ"]},
    "ox-grid-4":               {"noun": "記述", "labels": ["ア", "イ", "ウ", "エ"]},
    "ox-grid-3-combination-8": {"noun": "記述", "labels": ["ア", "イ", "ウ"]},
    "multi-select-5":          {"noun": "記述", "labels": ["1", "2", "3", "4", "5"]},
    "single-choice-5":         {"noun": "記述", "labels": ["1", "2", "3", "4", "5"]},
    "combination-5":           {"noun": "記述", "labels": ["ア", "イ", "ウ", "エ", "オ"]},
    "fill-in":                 {"noun": "空欄", "labels": ["A", "B", "C", "D", "E"]},
    "fillin8":                 {"noun": "肢",   "labels": ["1", "2", "3", "4", "5"]},
}

# .format() 名前付き placeholder。{{CHOICE_X_*}} 等の slot 参照は {{{{...}}}} で
# エスケープ（.format() 通過後に {{CHOICE_X_*}} 形式で残り、main render の slot 置換に渡される）。
# {first_label} / {last_label} は labels[0] / labels[-1] の単純連結。
PART_B_FRAME_TEMPLATE: str = (
    '\n'
    '  <!-- ============================================================\n'
    '       PART B ── {noun}別解説（{first_label}〜{last_label}）\n'
    '       ============================================================ -->\n'
    '  <div class="part-title">PART B ── {noun}別解説（{first_label}〜{last_label}）</div>\n'
    '\n'
    '{choice_blocks}'
    '  <!-- ============================================================\n'
    '       A-3 共通根拠条文・判例（スタブ）\n'
    '       ============================================================ -->'
)


def _build_part_b_choice_block(
    idx: int,
    noun: str,
    labels: list[str],
) -> str:
    """choice-section 1 件分の HTML（32 lines + trailing blank line）を生成する。

    Args:
        idx: 0-indexed の section 番号（0 〜 len(labels)-1）。
        noun: "記述" / "空欄" / "肢" のいずれか。
        labels: ラベル系列全体。nav の前後リンクと終端判定に使う。

    nav 規則:
        - 1 件目 (idx == 0):           "↑A-2" 固定 + 次 label
        - 中間 (0 < idx < N-1):        前 label + 次 label
        - 最終 (idx == N-1):           前 label + "↓共通根拠" 固定

    parity 規則: 1-indexed で奇数 → odd、偶数 → even。
    slot 名 letter: "ABCDE"[idx]。
    """
    n = len(labels)
    s = idx + 1  # 1-indexed section 番号
    label = labels[idx]
    letter = "ABCDE"[idx]
    parity = "odd" if s % 2 == 1 else "even"

    # nav back link
    if idx == 0:
        back = '<a href="#answer-area">↑A-2</a>'
    else:
        prev_label = labels[idx - 1]
        back = f'<a href="#choice-{s - 1}">←{noun}{prev_label}</a>'

    # nav forward link
    if idx == n - 1:
        forward = '<a href="#basis">↓共通根拠</a>'
    else:
        next_label = labels[idx + 1]
        forward = f'<a href="#choice-{s + 1}">{noun}{next_label}→</a>'

    return (
        f'  <!-- =============== {noun}{label} =============== -->\n'
        f'  <section class="choice-section {parity}" id="choice-{s}">\n'
        f'    <nav class="sec-nav">{back}{forward}</nav>\n'
        '\n'
        '    <div class="choice-header-block">\n'
        f'      <div class="choice-big-badge">{{{{CHOICE_{letter}_LABEL}}}}</div>\n'
        f'      <span class="verdict" data-verdict-label="{{{{CHOICE_{letter}_VERDICT_LABEL}}}}">{{{{CHOICE_{letter}_VERDICT_LABEL}}}}</span>\n'
        '    </div>\n'
        '\n'
        '    <div class="sub-card original">\n'
        f'      <span class="label">{noun}原文</span>\n'
        f'      <p>{{{{CHOICE_{letter}_STEM}}}}</p>\n'
        '    </div>\n'
        '\n'
        '    <div class="sub-card explanation">\n'
        '      <h4>📖 解説原文</h4>\n'
        f'      <p>{{{{CHOICE_{letter}_EXPLANATION}}}}</p>\n'
        '    </div>\n'
        '\n'
        '    <div class="sub-card basis-link">\n'
        '      <h4>📚 根拠判例</h4>\n'
        f'      <p>{{{{CHOICE_{letter}_CASES}}}}</p>\n'
        '    </div>\n'
        '\n'
        '    <div class="sub-card professor">\n'
        '      <h4>👨‍🏫 教授の解説</h4>\n'
        f'      <p class="prof-summary">{{{{CHOICE_{letter}_PROFESSOR_SUMMARY}}}}</p>\n'
        f'      <p class="prof-note">{{{{CHOICE_{letter}_PROFESSOR_NOTE}}}}</p>\n'
        '    </div>\n'
        '\n'
        '    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>\n'
        '  </section>\n'
        '\n'  # trailing blank line (separator to next section or A-3 preamble)
    )


def render_part_b(instruction_type: str) -> str:
    """{{PART_B_FRAME}} slot 値を返す（パターン E 応用: A+C dispatch + 局所 D 配列駆動）。

    軸 1〜2 は dict 派生、軸 3 (choice_blocks) のみ件数別の関数生成。
    未対応 instruction_type で RuntimeError。
    """
    if instruction_type not in PART_B_AXES_BY_TYPE:
        raise RuntimeError(
            f"unknown instruction_type {instruction_type!r} for part_b. "
            f"valid: {sorted(PART_B_AXES_BY_TYPE)}"
        )
    axes = PART_B_AXES_BY_TYPE[instruction_type]
    noun = axes["noun"]
    labels = axes["labels"]

    choice_blocks = "".join(
        _build_part_b_choice_block(idx, noun, labels) for idx in range(len(labels))
    )

    return PART_B_FRAME_TEMPLATE.format(
        noun=noun,
        first_label=labels[0],
        last_label=labels[-1],
        choice_blocks=choice_blocks,
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

    # pre_part_a slot 供給（Phase 4-9 で集約 slot 化、Phase 4-6 TOC 同形・A+C 組合せ 2 例目）。
    # problem.instruction_type から PRE_PART_A_FORM_NAMES_BY_TYPE を参照し、form 名を埋込。
    # 未対応 type は render_pre_part_a() 内で RuntimeError。
    slots["PRE_PART_A"] = render_pre_part_a(problem.get("instruction_type", ""))

    # head slot 供給（Phase 4-10 で集約 slot 化、Phase 4-8 body_pre_toc 同形・C refined 3 例目）。
    # 旧 4 slot ({{JP_PREFIX}}/{{PROBLEM_ID}}/{{CRIME}}/{{SOURCE_ID}}) は据え置き、本 slot
    # は経路の重複となるが許容（body_pre_toc/footer-spec で他参照あり）。
    slots["HEAD"] = render_head(problem)

    # basis sec-nav slot 供給（Phase 4-11 で集約 slot 化、A+C 組合せ 3 例目・Phase 4-6/4-9 機械的踏襲）。
    # basis section 第 2 行の <nav class="sec-nav"> 全体を {{BASIS_SECNAV}} に集約。
    # 未対応 type は render_basis_secnav() 内で RuntimeError。
    slots["BASIS_SECNAV"] = render_basis_secnav(problem.get("instruction_type", ""))

    # part_a 領域 slot 供給（Phase 4-12 で集約 slot 化、パターン E 新規確立: A+C + 局所 D）。
    # PART A 全体 (part-title から </section> まで、21〜52 lines) を {{PART_A_FRAME}} に集約。
    # 5 軸のうち軸 4 (combo_section) のみ件数可変なため局所 D を併用。
    # 未対応 type は render_part_a() 内で RuntimeError。
    # Commit 3 (templates 置換) 完了前は templates 内に {{PART_A_FRAME}} placeholder が
    # 存在しないため、本値は無害に未使用となる（broken intermediate state なし）。
    slots["PART_A_FRAME"] = render_part_a(problem.get("instruction_type", ""))

    # a2 領域 slot 供給（Phase 4-13 で集約 slot 化、パターン E 応用 1 例目: A+C + 局所 D + UI 種別 dispatch）。
    # A-2 解答エリア全体 (<section id="answer-area"> から </section> まで、25〜60 lines) を {{A2_FRAME}} に集約。
    # 6 軸のうち軸 6 (ui_block) のみ件数・block 種別・ラベル可変なため局所 D + UI 種別 dispatch を併用。
    # 未対応 type は render_a2() 内で RuntimeError。
    # Commit 3 (templates 置換) 完了前は templates 内に {{A2_FRAME}} placeholder が
    # 存在しないため、本値は無害に未使用となる（broken intermediate state なし）。
    slots["A2_FRAME"] = render_a2(problem.get("instruction_type", ""))

    # part_b 領域 slot 供給（Phase 4-14 で集約 slot 化、パターン E 応用 2 例目: A+C + 局所 D）。
    # PART B 全体（part-title 〜 全 choice-section 〜 A-3 preamble、108〜174 lines）を {{PART_B_FRAME}} に集約。
    # 3 軸のうち軸 3 (choice_blocks の N 回ループ) のみ件数可変なため局所 D（配列駆動）を併用。
    # Phase 4-13 a2 で必要だった UI 種別 dispatch（2 builder 切替）は不要 — 全 variants が
    # 同一の choice-section 構造を共有するため builder は 1 つ。
    # 未対応 type は render_part_b() 内で RuntimeError。
    # Commit 3 (templates 置換) 完了前は templates 内に {{PART_B_FRAME}} placeholder が
    # 存在しないため、本値は無害に未使用となる（broken intermediate state なし）。
    slots["PART_B_FRAME"] = render_part_b(problem.get("instruction_type", ""))

    # spec_version 判定（v9.2.0 DEEP-DIVE 対応・既定は v9.1.0 互換）
    spec_version = str(problem.get("spec_version", DEFAULT_SPEC_VERSION))
    flags = get_render_flags(spec_version)
    palette_strategy = problem.get("palette_strategy")
    if isinstance(problem.get("footer"), dict):
        palette_strategy = palette_strategy or problem["footer"].get("palette_strategy")

    # footer-spec feature-tag 列 slot 供給（Phase 4-2 で集約 slot 化）。
    # v9.1.0 以下：FOOTER_FEATURE_TAGS_DEFAULT (22 固定) + override_pattern = 23 行
    # v9.2.0：FOOTER_FEATURE_TAGS_V92 (31 固定) + override_pattern + palette-strategy = 33 行
    slots["FOOTER_FEATURE_TAGS"] = render_footer_feature_tags(
        slots["OVERRIDE_PATTERN"],
        extra_tags=problem.get("footer", {}).get("extra_tags") if isinstance(problem.get("footer"), dict) else None,
        spec_version=spec_version,
        palette_strategy=palette_strategy,
    )

    # v9.2.0 専用 slot 供給。
    # templates 拡張方針（Phase 12D 案 A）：8 templates にインライン slot 配置
    #   `</style>{{PALETTE_DERIVATIVES_ROOT}}`
    #   `  </section>{{MINDMAP_TREE}}{{MINDMAP_RADIAL_V92}}`
    # populated 時のみ slot 値の先頭に `\n` を付け、インライン直後に正しい改行で
    # 続く HTML を出力する。v9.1.0 以下では空文字 → byte-identical 維持。
    # v9.2.0 / v9.4.0 共通：v9.2.0 加算機能 6 件（tree-mindmap / radial-mindmap-v92 /
    # branching-flowchart / theory-deep-dive / palette-derivatives / density-v2）を全 ON。
    # v9.4.0 はこれに加えて v9.1.0 baseline 機能（hero-extra / choice-summary /
    # sub-card.basis-link / mindmap-section）を build_slot_dict() 末尾で post-process。
    if spec_version in ("v9.2.0", "v9.4.0"):
        if flags["PALETTE_DERIVATIVES"]:
            palette_root = render_palette_derivatives_root(slots["OVERRIDE_PATTERN"])
            slots["PALETTE_DERIVATIVES_ROOT"] = "\n" + palette_root if palette_root else ""
        else:
            slots["PALETTE_DERIVATIVES_ROOT"] = ""

        if flags["INCLUDE_TREE_MINDMAP"]:
            tree = render_mindmap_tree(problem)
            slots["MINDMAP_TREE"] = "\n\n" + tree if tree else ""
        else:
            slots["MINDMAP_TREE"] = ""

        if flags["INCLUDE_RADIAL_MINDMAP"]:
            radial = render_mindmap_radial_v92(problem)
            slots["MINDMAP_RADIAL_V92"] = "\n\n" + radial if radial else ""
        else:
            slots["MINDMAP_RADIAL_V92"] = ""

        # FLOW_SVG_V92 slot は将来用に保持（現状 templates では参照されない）
        slots["FLOW_SVG_V92"] = (
            render_flowchart_v2(problem) if flags["INCLUDE_BRANCHING_FLOWCHART"] else ""
        )
        # THEORY_DEEP_DIVE slot も将来用（C4_DOCTRINES への inject_theory_into_c4 で実際に注入）
        slots["THEORY_DEEP_DIVE"] = (
            render_theory_deep_dive(problem) if flags["INCLUDE_THEORY_DEEP_DIVE"] else ""
        )

        # v9.2.0/v9.4.0 C-4 への theory-detail-grid 注入（back-to-top の直前に挿入）
        if flags["INCLUDE_THEORY_DEEP_DIVE"] and problem.get("theory_deep_dive"):
            slots["C4_DOCTRINES"] = inject_theory_into_c4(
                slots["C4_DOCTRINES"], render_theory_deep_dive(problem)
            )

        # v9.2.0/v9.4.0 C-5 を分岐型 flow-svg に置換（flowchart_v2 が定義されている場合のみ）
        if flags["INCLUDE_BRANCHING_FLOWCHART"] and problem.get("flowchart_v2"):
            slots["C5_FLOWCHART"] = render_c5_flowchart_v92(problem)

    else:
        # v9.1.0 以下：v9.2.0 専用 slot は空（インライン挿入位置に何も入らない・
        # byte-identical 維持）。
        slots["PALETTE_DERIVATIVES_ROOT"] = ""
        slots["MINDMAP_TREE"] = ""
        slots["MINDMAP_RADIAL_V92"] = ""
        slots["FLOW_SVG_V92"] = ""
        slots["THEORY_DEEP_DIVE"] = ""

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
        # v9.2.0 density-v2 統合（Phase 13A）：
        # spec_version=v9.2.0 かつ professor.point が定義されている場合のみ density-v2 HTML
        # を生成。それ以外（v9.1.0 以下 / v9.2.0 で density-v2 未指定）は既存 summary/note
        # 経路を維持。PART_B_FRAME 内 `<p class="prof-summary">{{...}}</p>` への注入だが、
        # HTML parser は内部 <div> を検知して <p> を自動的に閉じるため、S91 検査（BeautifulSoup）
        # の `.prof-heading.prof-point` セレクタは到達可能。v9.1.0 baseline は byte-identical 維持。
        if spec_version in ("v9.2.0", "v9.4.0") and professor.get("point"):
            slots[f"{prefix}_PROFESSOR_SUMMARY"] = render_professor_density_v2(professor)
            slots[f"{prefix}_PROFESSOR_NOTE"] = ""
        else:
            slots[f"{prefix}_PROFESSOR_SUMMARY"] = str(professor.get("summary", ""))
            slots[f"{prefix}_PROFESSOR_NOTE"] = str(professor.get("note", ""))

    # v9.4.0 COMPLETE-BASELINE 拡張（Phase Y-4-bis-impl Commit 1）
    # spec_version="v9.4.0" の時のみ以下を上書き:
    #   - BODY_PRE_TOC: header-top (exam-badge) + theme-tags + 難度・愛称付き exam-meta
    #   - PART_B_FRAME: choice-summary / sub-card.basis-link を post-process 注入
    # 既存 slot 群（HEAD/A2_FRAME/PART_A_FRAME 等）は無改変。
    # v9.4.0 以外（v9.1.0/v9.2.0 等）では本ブロックは起動せず、既存出力と byte-identical。
    if spec_version == "v9.4.0":
        slots["BODY_PRE_TOC"] = render_body_pre_toc_v94(problem)
        slots["PART_B_FRAME"] = inject_v94_choice_extras(slots["PART_B_FRAME"], problem)

    return slots


# ============================================================================
# レンダリング
# ============================================================================

SLOT_PATTERN = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)\}\}")


def render(template: str, slots: dict[str, str]) -> str:
    """{{SLOT}} を置換する。未定義 slot が残ったら RuntimeError。

    Phase 4-12 で meta-slot ({{PART_A_FRAME}} 等の、展開後に nested {{X}} を含む slot)
    対応のため**多段置換**に変更。1 pass の置換結果に対して再び全 slot を適用し、
    置換が収束する (出力が変化しなくなる) まで繰り返す。

    Phase 4-11 まで:
      - すべての slot 値が nested {{X}} を含まなかったため、1 pass で必ず収束
      - 多段化しても結果は完全同一 (14 protected + 300 全件 byte-identical 維持)

    Phase 4-12 以降:
      - meta-slot の展開結果 ({{INSTRUCTION}} / {{CASE_BODY}} / {{CHOICE_X_LABEL}} /
        {{COMBO_N_LABEL}} 等の nested 参照) が 2 pass 目で解決される

    安全ガード: MAX_PASSES (5) を超えても収束しない場合は循環参照と判断し
    RuntimeError raise。
    """
    out = template
    MAX_PASSES = 5
    for _ in range(MAX_PASSES):
        prev = out
        for key, value in slots.items():
            out = out.replace("{{" + key + "}}", value)
        if out == prev:
            break
    else:
        raise RuntimeError(
            f"slot 置換が {MAX_PASSES} pass 内に収束しません。"
            "slot 値内の循環参照を確認してください。"
        )

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


# ============================================================================
# v9.4.0 COMPLETE-BASELINE 拡張関数群（Phase Y-4-bis-impl Commit 1）
# ============================================================================
# 既存関数を一切改変せず、v9.4.0 専用の追加機能を「post-process injection」で
# 実装する。spec_version!="v9.4.0" では起動しないため、v9.1.0/v9.2.0/v9.3.0
# ファイルの byte-identical を完全に維持する。
#
# 「過ちを繰り返さない」5 原則準拠：
# (原則 2) 既存関数は無改変・新規関数として追加のみ
# (原則 3) JSON schema は v9.1.0 流儀（structured）・{title, body} 単純化禁止
# (原則 5) 検査先行 (S95-S97) は validate-tx.py 側で既に追加済


# パターン愛称完全形（v9.1.0 baseline で確認・313 で出力されていた）
V94_PATTERN_NICKNAMES: dict[str, str] = {
    "P1": "P1 ローズシャンブル",
    "P2": "P2 セージブラリー",
    "P3": "P3 ラベンダードーン",
}

# 科目絵文字（v9.1.0 baseline で確認・313 のヒーロー部 exam-badge 由来）
V94_SUBJECT_EMOJI: dict[str, str] = {
    "KEI":   "📚 刑法",
    "KEN":   "📚 憲法",
    "MIN":   "📚 民法",
    "SYO":   "📚 商法",
    "MINS":  "📚 民訴",
    "KEIS":  "📚 刑訴",
    "GSE":   "📚 行政法",
}


# 難度判定（正答率 → 星表記）
def difficulty_stars(correct_rate_value) -> str:
    """correct_rate (数値 or '50%' 等) → '★★☆' 等の難度文字列。

    >=70: ★☆☆（易）/ 40-69: ★★☆（中）/ <40: ★★★（難）
    """
    if isinstance(correct_rate_value, str):
        m = re.search(r"(\d+)", correct_rate_value)
        if not m:
            return "★★☆"
        rate = int(m.group(1))
    elif isinstance(correct_rate_value, (int, float)):
        rate = int(correct_rate_value)
    else:
        return "★★☆"
    rate = max(0, min(100, rate))
    if rate >= 70:
        return "★☆☆"
    elif rate >= 40:
        return "★★☆"
    else:
        return "★★★"


# v9.4.0 BODY_PRE_TOC テンプレ（v9.1.0 baseline 構造）
# 既存 BODY_PRE_TOC_TEMPLATE は無改変。spec_version="v9.4.0" の時のみ本テンプレを使用。
BODY_PRE_TOC_TEMPLATE_V94: str = (
    '</head>\n'
    '<body id="top">\n'
    '<div class="container">\n'
    '\n'
    '  <!-- HEADER -->\n'
    '  <header class="header">\n'
    '    <div class="doc-header">{jp_prefix}{problem_id}</div>\n'
    '{header_top}'
    '    <h1>No.{problem_id} ── {crime}（{source_id}）</h1>\n'
    '{theme_tags}'
    '    <div class="exam-meta">\n'
    '      <span><strong>正答率:</strong>{correct_rate}</span>\n'
    '      <span><strong>難度:</strong>{difficulty}</span>\n'
    '      <span><strong>パターン:</strong>{pattern_nickname}</span>\n'
    '    </div>'
)


def render_exam_badges_html(problem: dict) -> str:
    """v9.4.0 exam-badge 4 件（subject/exam/year/source）の HTML を返す。

    JSON フィールド `exam_badges[]` が指定されていればそれを優先、
    未指定なら subject + exam + year + source から自動構築する。
    """
    explicit_badges = problem.get("exam_badges")
    if explicit_badges and isinstance(explicit_badges, list):
        badges = explicit_badges
    else:
        subject = problem.get("subject", "KEI")
        subject_label = V94_SUBJECT_EMOJI.get(subject, f"📚 {subject}")
        exam = problem.get("exam", "")
        year = problem.get("year", "")
        source = problem.get("source", "")
        badges = [subject_label]
        if exam:
            badges.append(f"📝 {exam}")
        if year:
            badges.append(f"📅 {year}")
        if source:
            badges.append(f"🔢 {source}")
    if not badges:
        return ""
    inner = "\n".join(f'      <span class="exam-badge">{escape(b)}</span>' for b in badges)
    return (
        '    <div class="header-top">\n'
        + inner + "\n"
        '    </div>\n'
    )


def render_theme_tags_html(problem: dict) -> str:
    """v9.4.0 theme-tags の HTML を返す。

    JSON フィールド `theme_tags[]` (list of string) が指定されていれば
    `<div class="theme-tags"><span class="theme-tag">...</span></div>` を返す。
    未指定なら空文字（既存出力に影響なし）。
    """
    tags = problem.get("theme_tags") or []
    if not tags:
        return ""
    inner = "\n".join(f'      <span class="theme-tag">{escape(t)}</span>' for t in tags)
    return (
        '    <div class="theme-tags">\n'
        + inner + "\n"
        '    </div>\n'
    )


def render_body_pre_toc_v94(problem: dict) -> str:
    """v9.4.0 専用 BODY_PRE_TOC を返す。spec_version="v9.4.0" の時のみ呼ばれる。

    既存 render_body_pre_toc() は無改変。本関数は build_slot_dict() の末尾分岐で
    spec_version="v9.4.0" の場合に呼ばれ、slots["BODY_PRE_TOC"] を上書きする。
    """
    subject = problem.get("subject", "KEI")
    jp_prefix = SUBJECT_TO_JP[subject] + "TX"
    override_pattern = str(problem.get("override_pattern", "P1"))
    pattern_nickname = V94_PATTERN_NICKNAMES.get(override_pattern, override_pattern)
    difficulty = problem.get("difficulty") or difficulty_stars(problem.get("correct_rate", ""))
    return BODY_PRE_TOC_TEMPLATE_V94.format(
        jp_prefix=jp_prefix,
        problem_id=str(problem.get("id", "")),
        crime=str(problem.get("crime", "")),
        source_id=str(problem.get("source", "")),
        correct_rate=str(problem.get("correct_rate", "")),
        difficulty=str(difficulty),
        pattern_nickname=pattern_nickname,
        header_top=render_exam_badges_html(problem),
        theme_tags=render_theme_tags_html(problem),
    )


def render_choice_summary_html(choice: dict) -> str:
    """v9.4.0 choice-summary の HTML を返す（choice.summary_html がある時のみ）。

    313 では `<div class="choice-summary">…</div>` が各 choice-section の
    choice-header-block 内に配置されていた。本関数は inject_v94_choice_extras 経由で
    既存 PART_B_FRAME 出力に post-process injection される。
    """
    summary_html = choice.get("summary_html")
    if not summary_html:
        return ""
    return f'    <div class="choice-summary">{summary_html}</div>'


def render_sub_card_basis_link_html(choice: dict) -> str:
    """v9.4.0 sub-card.basis-link の HTML を返す（choice.basis_link_card がある時のみ）。

    313 では各 choice-section に `<div class="sub-card basis-link">` が 1 件配置され、
    本 choice が参照する判例・条文へのリンクを集約していた。

    Schema 想定（structured）:
      choice.basis_link_card: {
        label: "判例・条文への参照",   # heading label
        items: [{href, label, kind}]   # kind = "case" | "statute"
      }
    """
    card = choice.get("basis_link_card")
    if not card or not isinstance(card, dict):
        return ""
    items = card.get("items") or []
    if not items:
        return ""
    label = escape(card.get("label", "📎 参照する条文・判例"))
    parts = [
        '    <div class="sub-card basis-link">',
        f'      <span class="label">{label}</span>',
        '      <ul class="lead-list">',
    ]
    for item in items:
        if not isinstance(item, dict):
            continue
        href = escape(item.get("href", ""))
        item_label = item.get("label", "")
        kind = item.get("kind", "case")
        css_cls = "ref-case" if kind == "case" else "ref-stat"
        parts.append(
            f'        <li><a class="{css_cls}" href="#{href}">{item_label}</a></li>'
        )
    parts.append('      </ul>')
    parts.append('    </div>')
    return "\n".join(parts)


def render_mindmap_section_v94_html(problem: dict) -> str:
    """v9.4.0 mindmap section（v9.1.0 流儀の `<section id="mindmap">`）の HTML を返す。

    JSON フィールド `mindmap_section` が定義されていれば、その内容を section 化。
    Schema 想定（structured）:
      mindmap_section: {
        title: "論点詳細マインドマップ",
        intro_key_phrase_html: "...",   # 任意
        figure: {
          svg_html: "<svg>...</svg>",
          caption: "..."
        },
        legend: "凡例..."   # 任意
      }
    """
    ms = problem.get("mindmap_section")
    if not ms or not isinstance(ms, dict):
        return ""
    title = escape(ms.get("title", "論点詳細マインドマップ"))
    parts = [
        '',
        '  <section class="section" id="mindmap">',
        '    <nav class="sec-nav"><a href="#basis">↑共通根拠</a><a href="#c-1">C-1→</a></nav>',
        f'    <h2 class="section-title"><span class="sec-icon">🧭</span>{title}</h2>',
    ]
    if ms.get("intro_key_phrase_html"):
        parts.append(f'    <div class="key-phrase-box">\n      {ms["intro_key_phrase_html"]}\n    </div>')
    figure = ms.get("figure")
    if figure and figure.get("svg_html"):
        parts.append('    <div class="figure-wrap">')
        parts.append(f'      {figure["svg_html"]}')
        if figure.get("caption"):
            parts.append(f'      <p class="figure-caption">{escape(figure["caption"])}</p>')
        parts.append('    </div>')
    if ms.get("legend"):
        parts.append(f'    <p class="figure-legend">{escape(ms["legend"])}</p>')
    parts.append('    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>')
    parts.append('  </section>')
    return "\n".join(parts)


# choice-section 内 choice-header-block / sub-card 末尾 への post-process 注入
_V94_CHOICE_SECTION_PATTERN = re.compile(
    r'(<section class="choice-section[^"]*" id="choice-(\d+)">)(.*?)(</section>)',
    re.DOTALL,
)
# verdict span の閉じタグ </span> 直後に choice-summary を挿入する
# （入れ子 div を含む choice-header-block 全体の閉じ </div> を regex で正確に
# 検出するのは困難なため、verdict span の閉じ直後を anchor として採用）
_V94_VERDICT_SPAN_PATTERN = re.compile(
    r'(<span class="verdict[^"]*"[^>]*>[^<]*</span>)',
)


def inject_v94_choice_extras(part_b_frame_html: str, problem: dict) -> str:
    """既存 PART_B_FRAME 出力に v9.4.0 専用の choice-summary / sub-card.basis-link を
    post-process で挿入する。

    挿入位置:
      - choice-summary: verdict span の閉じ </span> の直後（choice-header-block 内・
        verdict と同じレベル）。CSS の `.choice-summary { flex:1 1 100%; }` で
        flex-wrap により次行に全幅で配置される。
      - sub-card.basis-link: choice-section 末尾の </section> の直前
    """
    label_to_letter = LABEL_TO_LETTER
    letter_to_label_idx = {v: i + 1 for i, v in enumerate(["A", "B", "C", "D", "E"])}
    choices = problem.get("choices") or []
    # choice id (1-5) → choice dict の map
    choice_by_id: dict[str, dict] = {}
    for c in choices:
        label = c.get("label", "")
        letter = label_to_letter.get(label)
        if letter is None:
            continue
        idx = letter_to_label_idx.get(letter)
        if idx is None:
            continue
        choice_by_id[str(idx)] = c

    def section_repl(m: "re.Match[str]") -> str:
        opening = m.group(1)
        cid = m.group(2)
        body = m.group(3)
        closing = m.group(4)
        c = choice_by_id.get(cid)
        if not c:
            return m.group(0)
        # choice-summary を verdict span の閉じ </span> 直後に挿入
        # （choice-header-block の入れ子 div 構造を regex で正確に追えないため）
        summary_html = render_choice_summary_html(c)
        if summary_html:
            def verdict_repl(vm: "re.Match[str]") -> str:
                return vm.group(0) + "\n" + summary_html
            body = _V94_VERDICT_SPAN_PATTERN.sub(verdict_repl, body, count=1)
        # sub-card.basis-link を choice-section 末尾に挿入
        basis_link_html = render_sub_card_basis_link_html(c)
        if basis_link_html:
            body = body.rstrip() + "\n\n" + basis_link_html + "\n  "
        return opening + body + closing

    return _V94_CHOICE_SECTION_PATTERN.sub(section_repl, part_b_frame_html)


def inject_v94_mindmap_section(rendered_html: str, problem: dict) -> str:
    """basis section と C-1 section の間に v9.4.0 mindmap section を挿入する。

    挿入位置: `<section class="section" id="basis">...</section>` の直後。
    `mindmap_section` フィールド未定義時は no-op。
    """
    section_html = render_mindmap_section_v94_html(problem)
    if not section_html:
        return rendered_html
    # basis section の終了タグを探して、その直後に挿入
    basis_pattern = re.compile(
        r'(<section class="section" id="basis">.*?</section>)',
        re.DOTALL,
    )
    return basis_pattern.sub(lambda m: m.group(1) + "\n" + section_html, rendered_html, count=1)


# v9.4.0 SVG class CSS rules（44 class）
# template には CSS 規則が完全欠落しており、SVG 全形状が既定の黒で描画される
# 重大表示バグ（Phase Y-2 で特定済・v9.2.0 pre-existing）の修正。
# post-process injection 方式で template / 既存ファイルへの影響を完全に避ける。
_V94_SVG_CSS = """
/* === §22-tree / §22-radial / §22-flowchart-v2 SVG class colors (v9.4.0 post-process) === */
/* Tree SVG (§22-tree) */
.tree-svg{ display:block; max-width:100%; height:auto; }
.tree-svg .tx-legend{ font-family:var(--font-mono); font-size:11px; fill:var(--text); }
.tree-svg .l0-fill{ fill:var(--accent); stroke:var(--accent); stroke-width:1.2; }
.tree-svg .l1-fill{ fill:var(--mid); stroke:var(--mid); stroke-width:1; }
.tree-svg .l2-fill{ fill:var(--accent-light); stroke:var(--mid); stroke-width:1; }
.tree-svg .l3-fill{ fill:var(--accent-soft); stroke:var(--mid-cool); stroke-width:.8; }
.tree-svg .l2-active, .tree-svg .l3-active{ fill:var(--mid-warm); stroke:var(--accent); stroke-width:1.5; }
.tree-svg .tx-l0{ font-family:var(--font-display); font-size:13px; font-weight:700; fill:var(--paper); }
.tree-svg .tx-l1{ font-family:var(--font-soft); font-size:12px; font-weight:700; fill:var(--paper); }
.tree-svg .tx-l2{ font-family:var(--font-body); font-size:11px; fill:var(--text); }
.tree-svg .tx-l3{ font-family:var(--font-body); font-size:10px; fill:var(--text); }
.tree-svg .line-main{ stroke:var(--mid); stroke-width:1.6; fill:none; }
.tree-svg .line-sub{ stroke:var(--accent-light); stroke-width:1; fill:none; }
.tree-svg .line-issue, .tree-svg .issue-arrow{ stroke:var(--mid-warm); stroke-width:1.4; fill:none; }
.tree-svg .tx-issue{ fill:var(--mid-warm); stroke:var(--accent); stroke-width:1.2; }
.tree-svg .tx-issue-ttl{ font-family:var(--font-soft); font-size:11px; font-weight:700; fill:var(--bg-dark); }
.tree-svg .tx-issue-body{ font-family:var(--font-body); font-size:10px; fill:var(--text); }

/* Radial SVG (§22-radial) */
.radial-svg{ display:block; max-width:100%; height:auto; }
.radial-svg .tx-legend{ font-family:var(--font-mono); font-size:11px; fill:var(--text); }
.radial-svg .branch-fill{ fill:var(--mid); stroke:var(--accent); stroke-width:1.2; }
.radial-svg .issue-branch-fill{ fill:var(--mid-warm); stroke:var(--accent); stroke-width:1.5; }
.radial-svg .sub-elem{ fill:var(--base); stroke:var(--mid); stroke-width:.8; }
.radial-svg .sub-statute{ fill:var(--accent-light); stroke:var(--mid); stroke-width:.8; }
.radial-svg .sub-case{ fill:var(--accent-soft); stroke:var(--mid-cool); stroke-width:.8; }
.radial-svg .tx-center{ font-family:var(--font-display); font-size:14px; font-weight:700; fill:var(--paper); }
.radial-svg .tx-branch{ font-family:var(--font-soft); font-size:11px; font-weight:700; fill:var(--paper); }
.radial-svg .tx-chip, .radial-svg .tx-elem, .radial-svg .tx-statute, .radial-svg .tx-case{ font-family:var(--font-body); font-size:10px; fill:var(--text); }
.radial-svg .connect{ stroke:var(--mid); stroke-width:1.2; fill:none; }
.radial-svg .tx-issue-ttl{ font-family:var(--font-soft); font-size:11px; font-weight:700; fill:var(--bg-dark); }
.radial-svg .tx-issue-body{ font-family:var(--font-body); font-size:10px; fill:var(--text); }
.radial-svg .tx-correct{ font-family:var(--font-mono); font-size:11px; font-weight:700; fill:var(--accent); }

/* Flow SVG (§22-flowchart-v2) */
.flow-svg{ display:block; max-width:100%; height:auto; }
.flow-svg .tx-legend{ font-family:var(--font-mono); font-size:11px; fill:var(--text); }
.flow-svg .flow-start{ fill:var(--accent); stroke:var(--accent); stroke-width:1.4; }
.flow-svg .flow-decision{ fill:var(--mid); stroke:var(--accent); stroke-width:1.2; }
.flow-svg .flow-end-success{ fill:var(--mid-warm); stroke:var(--accent); stroke-width:1.4; }
.flow-svg .flow-end-fail{ fill:var(--contrast-warm); stroke:var(--bg-dark); stroke-width:1.4; }
.flow-svg .flow-chip{ fill:var(--accent-light); stroke:var(--mid); stroke-width:.8; }
.flow-svg .flow-line{ stroke:var(--mid); stroke-width:1.4; fill:none; }
.flow-svg .tx-start{ font-family:var(--font-display); font-size:12px; font-weight:700; fill:var(--paper); }
.flow-svg .tx-decision{ font-family:var(--font-soft); font-size:11px; font-weight:700; fill:var(--paper); }
.flow-svg .tx-end{ font-family:var(--font-soft); font-size:12px; font-weight:700; fill:var(--paper); }
.flow-svg .tx-chip, .flow-svg .tx-yn{ font-family:var(--font-body); font-size:10px; fill:var(--text); }
"""


def inject_v94_svg_css(rendered_html: str) -> str:
    """v9.4.0 専用: SVG class CSS rules (44 class) を <style> 末尾に注入する。

    Phase Y-2 で特定済の v9.2.0 pre-existing バグ「template の SVG class CSS rule
    完全欠落 → SVG 全形状が既定の黒で描画」を修正する。template / 既存 14 ファイル
    への影響を完全に避けるため、render() 完了後に `</style>` 直前へ post-process
    で注入する経路を選択（原則 1: cascade 後勝ち / 原則 2: 既存無改変 準拠）。

    spec_version!="v9.4.0" では呼ばれないため既存 byte-identical 完全維持。
    """
    return rendered_html.replace("</style>", _V94_SVG_CSS + "\n</style>", 1)


# ============================================================================
# v9.4.0 拡張ここまで
# ============================================================================


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

    # v9.4.0 COMPLETE-BASELINE: mindmap section (v9.1.0 流儀) を basis section の
    # 直後に post-process 注入。spec_version!="v9.4.0" / mindmap_section 未定義時は no-op。
    spec_version_for_post = str(problem.get("spec_version", DEFAULT_SPEC_VERSION))
    if spec_version_for_post == "v9.4.0":
        rendered = inject_v94_mindmap_section(rendered, problem)
        # SVG class CSS rules (44 class) を post-process で <style> 末尾に注入。
        # template の v9.2.0 pre-existing バグ（CSS 規則完全欠落で SVG 黒塗り）の修正。
        rendered = inject_v94_svg_css(rendered)

    output_path = get_output_path(subject, problem_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # newline="" を指定して LF を保持（Windows で CRLF 化を防ぐ・git 差分回避）
    output_path.write_text(rendered, encoding="utf-8", newline="")
    print(
        f"OK: {output_path} ({len(rendered):,} bytes) "
        f"(subject={subject}, template={selected_template_path.name}, "
        f"instruction_type={instruction_type or 'unset'})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
