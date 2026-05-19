#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_fillin8_template.py — KTX_template_comb5.html から KTX_template_fillin8.html を生成。

戦略 (slotmap §6.6b §3.1):
  - comb5 を読み込み、差分許容セクション (toc/pre_part_a/part_a/a2/part_b/basis) のみ
    fillin8 用に in-place 置換
  - 同期義務セクションは comb5 から byte-identical 維持 (CP1/CP5 担保)
  - KEIS の本質的形式 (8 blanks 表示 + 5 options 単一選択) に合わせ、
    answer 機構は comb5 と同じ single-choice (1〜5) を流用

Usage:
    python scripts/build_fillin8_template.py
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "templates" / "KTX_template_comb5.html"
DST = ROOT / "templates" / "KTX_template_fillin8.html"


def find_line(lines, pattern, start=0):
    p = re.compile(pattern)
    for i in range(start, len(lines)):
        if p.search(lines[i]):
            return i
    return -1


# toc: 肢 1-5 + 共通リンク
FILLIN8_TOC = '''    <div class="toc-row">
      <a href="#part-a">問題文</a>
      <a href="#answer-area">解答</a>
      <a href="#choice-1">肢1</a>
      <a href="#choice-2">肢2</a>
      <a href="#choice-3">肢3</a>
      <a href="#choice-4">肢4</a>
      <a href="#choice-5">肢5</a>
      <a href="#basis">共通根拠</a>
      <a href="#c-1">体系</a>
      <a href="#c-7">三層記憶</a>
      <a href="#part-d">⚔ARENA</a>
    </div>'''

FILLIN8_PRE_PART_A = '''
  <!-- ============================================================
       PART A ── 問題情報（fillin8 形式：8 blanks 表示 + 5 options 単一選択）
       ============================================================ -->'''

# part_a: 問題本文は {{INSTRUCTION}} 内に 8 blanks (①〜⑧) を embed、
# 候補一覧 (a〜i) も instruction に embed、
# 5 選択肢の主張は CHOICE_A〜E_STEM に格納
FILLIN8_PART_A = '''  <div class="part-title">PART A ── 問題情報</div>

  <section class="section" id="part-a">
    <nav class="sec-nav"><a href="#answer-area">↓解答</a><a href="#choice-1">↓肢1</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>A-1 問題文</h2>

    <p style="font-weight:600;">{{INSTRUCTION}}</p>

    <h3 style="background:transparent; border-left:none; padding:8px 0 4px 0; margin:20px 0 8px 0; border-bottom:2px dotted var(--border-mid); color:var(--accent); font-family:var(--font-display);">【選択肢】</h3>

    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_A_LABEL}}</span>{{CHOICE_A_STEM}}</div>
    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_B_LABEL}}</span>{{CHOICE_B_STEM}}</div>
    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_C_LABEL}}</span>{{CHOICE_C_STEM}}</div>
    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_D_LABEL}}</span>{{CHOICE_D_STEM}}</div>
    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_E_LABEL}}</span>{{CHOICE_E_STEM}}</div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>'''

# a2: comb5 と同じ single-choice 1-5
FILLIN8_A2 = '''  <section class="section" id="answer-area">
    <nav class="sec-nav"><a href="#part-a">↑A-1</a><a href="#choice-1">↓肢1</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>A-2 解答</h2>

    <div class="answer-area"
         data-correct-value="{{ANSWER}}"
         data-answer-type="single"
         data-explanation="{{ANSWER_EXPLANATION}}">
      <h3>正しい組合せを選択</h3>
      <p class="answer-instruction">選択肢を選んで「解答を表示」を押してください。</p>

      <div class="answer-row">
        <button class="answer-slot" type="button" data-num="1" data-value="1">1</button>
        <button class="answer-slot" type="button" data-num="2" data-value="2">2</button>
        <button class="answer-slot" type="button" data-num="3" data-value="3">3</button>
        <button class="answer-slot" type="button" data-num="4" data-value="4">4</button>
        <button class="answer-slot" type="button" data-num="5" data-value="5">5</button>
      </div>

      <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>
      <div id="answer-feedback" hidden></div>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>'''

# part_b: 5 choice-sections (肢 1-5)、最後に A-3 共通根拠コメント
FILLIN8_PART_B = '''
  <!-- ============================================================
       PART B ── 肢別解説（1〜5）
       ============================================================ -->
  <div class="part-title">PART B ── 肢別解説（1〜5）</div>

  <!-- =============== 肢1 =============== -->
  <section class="choice-section odd" id="choice-1">
    <nav class="sec-nav"><a href="#answer-area">↑A-2</a><a href="#choice-2">肢2→</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_A_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_A_VERDICT_LABEL}}">{{CHOICE_A_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">肢原文</span>
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

  <!-- =============== 肢2 =============== -->
  <section class="choice-section even" id="choice-2">
    <nav class="sec-nav"><a href="#choice-1">←肢1</a><a href="#choice-3">肢3→</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_B_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_B_VERDICT_LABEL}}">{{CHOICE_B_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">肢原文</span>
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

  <!-- =============== 肢3 =============== -->
  <section class="choice-section odd" id="choice-3">
    <nav class="sec-nav"><a href="#choice-2">←肢2</a><a href="#choice-4">肢4→</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_C_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_C_VERDICT_LABEL}}">{{CHOICE_C_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">肢原文</span>
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

  <!-- =============== 肢4 =============== -->
  <section class="choice-section even" id="choice-4">
    <nav class="sec-nav"><a href="#choice-3">←肢3</a><a href="#choice-5">肢5→</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_D_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_D_VERDICT_LABEL}}">{{CHOICE_D_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">肢原文</span>
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

  <!-- =============== 肢5 =============== -->
  <section class="choice-section odd" id="choice-5">
    <nav class="sec-nav"><a href="#choice-4">←肢4</a><a href="#basis">↓共通根拠</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_E_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_E_VERDICT_LABEL}}">{{CHOICE_E_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">肢原文</span>
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

FILLIN8_BASIS = '''  <section class="section" id="basis">
    <nav class="sec-nav"><a href="#choice-5">↑肢5</a><a href="#c-1">↓C-1</a></nav>
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

    style_open = find_line(lines, r"<style>")
    toc_open = find_line(lines, r'<div class="toc-row">')
    toc_close = find_line(lines, r"</div>", toc_open + 1)
    marker_legend_open = find_line(lines, r'<div class="marker-legend"')
    marker_legend_close = find_line(lines, r"</div>", marker_legend_open + 1)
    part_a_title = find_line(lines, r'<div class="part-title">PART A')
    answer_area_section = find_line(lines, r'<section[^>]+id="answer-area"')
    answer_area_close = find_line(lines, r"^\s*</section>\s*$", answer_area_section + 1)
    basis_section = find_line(lines, r'<section[^>]+id="basis"')
    basis_close = find_line(lines, r"^\s*</section>\s*$", basis_section + 1)

    replacements = [
        (basis_section, basis_close + 1, FILLIN8_BASIS.split("\n")),
        (answer_area_close + 1, basis_section, FILLIN8_PART_B.split("\n")),
        (answer_area_section, answer_area_close + 1, FILLIN8_A2.split("\n")),
        (part_a_title, answer_area_section, FILLIN8_PART_A.split("\n")),
        (marker_legend_close + 1, part_a_title, FILLIN8_PRE_PART_A.split("\n")),
        (toc_open, toc_close + 1, FILLIN8_TOC.split("\n")),
    ]
    replacements.sort(key=lambda r: r[0], reverse=True)
    for start, end, newlines in replacements:
        lines[start:end] = newlines

    out = "\n".join(lines)
    DST.write_text(out, encoding="utf-8")
    print(f"OK: {DST} ({len(out):,} chars, {len(lines)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
