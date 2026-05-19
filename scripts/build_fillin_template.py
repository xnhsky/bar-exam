#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_fillin_template.py — KTX_template_msel5.html から KTX_template_fillin.html を生成。

戦略 (slotmap §6.6 §2.1):
  - msel5 を読み込み、差分許容セクション (toc/pre_part_a/part_a/a2/part_b/basis) のみ
    fillin 用に in-place 置換
  - 同期義務セクション (head/css/body_pre_toc/marker_legend/part_c_d/footer_spec/js)
    は msel5 から byte-identical 維持 (CP1/CP4 担保)
  - 後ろから置換していくことで前方インデックスを破壊しない

Usage:
    python scripts/build_fillin_template.py
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "templates" / "KTX_template_msel5.html"
DST = ROOT / "templates" / "KTX_template_fillin.html"


def find_line(lines, pattern, start=0):
    p = re.compile(pattern)
    for i in range(start, len(lines)):
        if p.search(lines[i]):
            return i
    return -1


# ============================================================
# 差分許容セクションの fillin 用置換テキスト (改行 = 別行)
# ============================================================

FILLIN_TOC = '''    <div class="toc-row">
      <a href="#part-a">問題文</a>
      <a href="#answer-area">解答</a>
      <a href="#choice-1">A</a>
      <a href="#choice-2">B</a>
      <a href="#choice-3">C</a>
      <a href="#choice-4">D</a>
      <a href="#choice-5">E</a>
      <a href="#basis">共通根拠</a>
      <a href="#c-1">体系</a>
      <a href="#c-7">三層記憶</a>
      <a href="#part-d">⚔ARENA</a>
    </div>'''

# pre_part_a: msel5 では marker_legend_close+1 〜 part_a_title (= 4 行)
# msel5 構造: 空行 / <!-- ====== / PART A ... / ====== --> の 4 行
FILLIN_PRE_PART_A = '''
  <!-- ============================================================
       PART A ── 問題情報（fill-in 形式）
       ============================================================ -->'''

FILLIN_PART_A = '''  <div class="part-title">PART A ── 問題情報</div>

  <section class="section" id="part-a">
    <nav class="sec-nav"><a href="#answer-area">↓解答</a><a href="#choice-1">↓空欄A</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>A-1 問題文</h2>

    <p style="font-weight:600;">{{INSTRUCTION}}</p>

    <h3 style="background:transparent; border-left:none; padding:8px 0 4px 0; margin:20px 0 8px 0; border-bottom:2px dotted var(--border-mid); color:var(--accent); font-family:var(--font-display);">【空欄】</h3>

    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_A_LABEL}}</span>{{CHOICE_A_STEM}}</div>
    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_B_LABEL}}</span>{{CHOICE_B_STEM}}</div>
    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_C_LABEL}}</span>{{CHOICE_C_STEM}}</div>
    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_D_LABEL}}</span>{{CHOICE_D_STEM}}</div>
    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_E_LABEL}}</span>{{CHOICE_E_STEM}}</div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>
'''

FILLIN_A2 = '''  <section class="section" id="answer-area">
    <nav class="sec-nav"><a href="#part-a">↑A-1</a><a href="#choice-1">↓空欄A</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>A-2 解答</h2>

    <div class="answer-area"
         data-correct-value="{{ANSWER}}"
         data-answer-type="fill-in"
         data-explanation="{{ANSWER_EXPLANATION}}">
      <h3>各空欄に該当する候補番号を確認</h3>
      <p class="answer-instruction">各空欄に入る候補を確認したら「解答を表示」を押してください。</p>

      <div class="answer-row">
        <button class="answer-slot" type="button" data-num="A" data-value="A">A</button>
        <button class="answer-slot" type="button" data-num="B" data-value="B">B</button>
        <button class="answer-slot" type="button" data-num="C" data-value="C">C</button>
        <button class="answer-slot" type="button" data-num="D" data-value="D">D</button>
        <button class="answer-slot" type="button" data-num="E" data-value="E">E</button>
      </div>

      <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>
      <div id="answer-feedback" hidden></div>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>'''

# part_b: msel5 と同じく PART B 見出し + 5 choice-section + A-3 共通根拠コメント (末尾)
FILLIN_PART_B = '''
  <!-- ============================================================
       PART B ── 空欄別解説（A〜E）
       ============================================================ -->
  <div class="part-title">PART B ── 空欄別解説（A〜E）</div>

  <!-- =============== 空欄A =============== -->
  <section class="choice-section odd" id="choice-1">
    <nav class="sec-nav"><a href="#answer-area">↑A-2</a><a href="#choice-2">空欄B→</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_A_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_A_VERDICT_LABEL}}">{{CHOICE_A_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">空欄原文</span>
      <p>{{CHOICE_A_STEM}}</p>
    </div>

    <div class="sub-card explanation">
      <h4>📖 解説原文</h4>
      <p>{{CHOICE_A_EXPLANATION}}</p>
    </div>

    <div class="sub-card basis-link">
      <h4>📚 根拠判例</h4>
      <p>{{CHOICE_A_CASES}}</p>
    </div>

    <div class="sub-card professor">
      <h4>👨‍🏫 教授の解説</h4>
      <p class="prof-summary">{{CHOICE_A_PROFESSOR_SUMMARY}}</p>
      <p class="prof-note">{{CHOICE_A_PROFESSOR_NOTE}}</p>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- =============== 空欄B =============== -->
  <section class="choice-section even" id="choice-2">
    <nav class="sec-nav"><a href="#choice-1">←空欄A</a><a href="#choice-3">空欄C→</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_B_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_B_VERDICT_LABEL}}">{{CHOICE_B_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">空欄原文</span>
      <p>{{CHOICE_B_STEM}}</p>
    </div>

    <div class="sub-card explanation">
      <h4>📖 解説原文</h4>
      <p>{{CHOICE_B_EXPLANATION}}</p>
    </div>

    <div class="sub-card basis-link">
      <h4>📚 根拠判例</h4>
      <p>{{CHOICE_B_CASES}}</p>
    </div>

    <div class="sub-card professor">
      <h4>👨‍🏫 教授の解説</h4>
      <p class="prof-summary">{{CHOICE_B_PROFESSOR_SUMMARY}}</p>
      <p class="prof-note">{{CHOICE_B_PROFESSOR_NOTE}}</p>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- =============== 空欄C =============== -->
  <section class="choice-section odd" id="choice-3">
    <nav class="sec-nav"><a href="#choice-2">←空欄B</a><a href="#choice-4">空欄D→</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_C_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_C_VERDICT_LABEL}}">{{CHOICE_C_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">空欄原文</span>
      <p>{{CHOICE_C_STEM}}</p>
    </div>

    <div class="sub-card explanation">
      <h4>📖 解説原文</h4>
      <p>{{CHOICE_C_EXPLANATION}}</p>
    </div>

    <div class="sub-card basis-link">
      <h4>📚 根拠判例</h4>
      <p>{{CHOICE_C_CASES}}</p>
    </div>

    <div class="sub-card professor">
      <h4>👨‍🏫 教授の解説</h4>
      <p class="prof-summary">{{CHOICE_C_PROFESSOR_SUMMARY}}</p>
      <p class="prof-note">{{CHOICE_C_PROFESSOR_NOTE}}</p>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- =============== 空欄D =============== -->
  <section class="choice-section even" id="choice-4">
    <nav class="sec-nav"><a href="#choice-3">←空欄C</a><a href="#choice-5">空欄E→</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_D_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_D_VERDICT_LABEL}}">{{CHOICE_D_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">空欄原文</span>
      <p>{{CHOICE_D_STEM}}</p>
    </div>

    <div class="sub-card explanation">
      <h4>📖 解説原文</h4>
      <p>{{CHOICE_D_EXPLANATION}}</p>
    </div>

    <div class="sub-card basis-link">
      <h4>📚 根拠判例</h4>
      <p>{{CHOICE_D_CASES}}</p>
    </div>

    <div class="sub-card professor">
      <h4>👨‍🏫 教授の解説</h4>
      <p class="prof-summary">{{CHOICE_D_PROFESSOR_SUMMARY}}</p>
      <p class="prof-note">{{CHOICE_D_PROFESSOR_NOTE}}</p>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- =============== 空欄E =============== -->
  <section class="choice-section odd" id="choice-5">
    <nav class="sec-nav"><a href="#choice-4">←空欄D</a><a href="#basis">↓共通根拠</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_E_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_E_VERDICT_LABEL}}">{{CHOICE_E_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">空欄原文</span>
      <p>{{CHOICE_E_STEM}}</p>
    </div>

    <div class="sub-card explanation">
      <h4>📖 解説原文</h4>
      <p>{{CHOICE_E_EXPLANATION}}</p>
    </div>

    <div class="sub-card basis-link">
      <h4>📚 根拠判例</h4>
      <p>{{CHOICE_E_CASES}}</p>
    </div>

    <div class="sub-card professor">
      <h4>👨‍🏫 教授の解説</h4>
      <p class="prof-summary">{{CHOICE_E_PROFESSOR_SUMMARY}}</p>
      <p class="prof-note">{{CHOICE_E_PROFESSOR_NOTE}}</p>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- ============================================================
       A-3 共通根拠条文・判例（スタブ）
       ============================================================ -->'''

# basis: 元の basis section と同じ構造 (sec-nav の back-link を空欄E に変更)
FILLIN_BASIS = '''  <section class="section" id="basis">
    <nav class="sec-nav"><a href="#choice-5">↑空欄E</a><a href="#c-1">↓C-1</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>A-3 共通根拠条文・判例</h2>
    <!-- TODO: Phase 2 で JSON schema 拡張、本実装 -->
    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>'''


def main():
    if not SRC.exists():
        print(f"ERROR: source not found: {SRC}", file=sys.stderr)
        return 2

    content = SRC.read_text(encoding="utf-8-sig")
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    lines = content.split("\n")

    # 境界 (check_template_sync.py と同じロジック)
    style_open = find_line(lines, r"<style>")
    style_close = find_line(lines, r"</style>")
    toc_open = find_line(lines, r'<div class="toc-row">')
    toc_close = find_line(lines, r"</div>", toc_open + 1)
    marker_legend_open = find_line(lines, r'<div class="marker-legend"')
    marker_legend_close = find_line(lines, r"</div>", marker_legend_open + 1)
    part_a_title = find_line(lines, r'<div class="part-title">PART A')
    answer_area_section = find_line(lines, r'<section[^>]+id="answer-area"')
    answer_area_close = find_line(lines, r"^\s*</section>\s*$", answer_area_section + 1)
    basis_section = find_line(lines, r'<section[^>]+id="basis"')
    basis_close = find_line(lines, r"^\s*</section>\s*$", basis_section + 1)

    # 後ろから置換: basis → part_b → a2 → part_a → pre_part_a → toc
    # (前のインデックスを破壊しない)

    # 1. basis: lines[basis_section : basis_close+1]
    lines[basis_section : basis_close + 1] = FILLIN_BASIS.split("\n")

    # 2. part_b: lines[answer_area_close+1 : basis_section]
    #    (basis_section index は上の置換で変わったが、今回置換するのはそれより前なので OK)
    #    ※ ただし置換に伴うインデックスシフトに注意: basis_section は元の値だが、上の置換後、
    #    新しい basis 位置は別の場所にあるはず。一度 lines を再走査するのが安全。
    # → やはり、後ろから置換するときは元のインデックスを使うが、各置換は独立に実行する。
    #    上で basis を置換した後、part_b の範囲は元のインデックスとは異なる。
    #    解決策: 全置換を「元のスライス→新スライス」の置換ペアとして用意し、後ろから順に適用。
    raise RuntimeError("unreachable")


def main_v2():
    if not SRC.exists():
        print(f"ERROR: source not found: {SRC}", file=sys.stderr)
        return 2

    content = SRC.read_text(encoding="utf-8-sig")
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    lines = content.split("\n")

    style_open = find_line(lines, r"<style>")
    style_close = find_line(lines, r"</style>")
    toc_open = find_line(lines, r'<div class="toc-row">')
    toc_close = find_line(lines, r"</div>", toc_open + 1)
    marker_legend_open = find_line(lines, r'<div class="marker-legend"')
    marker_legend_close = find_line(lines, r"</div>", marker_legend_open + 1)
    part_a_title = find_line(lines, r'<div class="part-title">PART A')
    answer_area_section = find_line(lines, r'<section[^>]+id="answer-area"')
    answer_area_close = find_line(lines, r"^\s*</section>\s*$", answer_area_section + 1)
    basis_section = find_line(lines, r'<section[^>]+id="basis"')
    basis_close = find_line(lines, r"^\s*</section>\s*$", basis_section + 1)

    # 置換ペア (start, end_exclusive, new_lines)
    # 後ろから順に slice 代入することで、前のインデックスは不変
    replacements = [
        # basis: lines[basis_section : basis_close+1]
        (basis_section, basis_close + 1, FILLIN_BASIS.split("\n")),
        # part_b: lines[answer_area_close+1 : basis_section]
        (answer_area_close + 1, basis_section, FILLIN_PART_B.split("\n")),
        # a2: lines[answer_area_section : answer_area_close+1]
        (answer_area_section, answer_area_close + 1, FILLIN_A2.split("\n")),
        # part_a: lines[part_a_title : answer_area_section]
        (part_a_title, answer_area_section, FILLIN_PART_A.split("\n")),
        # pre_part_a: lines[marker_legend_close+1 : part_a_title]
        (marker_legend_close + 1, part_a_title, FILLIN_PRE_PART_A.split("\n")),
        # toc: lines[toc_open : toc_close+1]
        (toc_open, toc_close + 1, FILLIN_TOC.split("\n")),
    ]

    # 後ろから (start が大きい順に) 適用すれば、各 slice は独立
    replacements.sort(key=lambda r: r[0], reverse=True)
    for start, end, newlines in replacements:
        lines[start:end] = newlines

    out = "\n".join(lines)
    DST.write_text(out, encoding="utf-8")
    print(f"OK: {DST} ({len(out):,} chars, {len(lines)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main_v2())
