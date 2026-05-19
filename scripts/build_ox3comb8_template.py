#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_ox3comb8_template.py — KTX_template_comb5.html から KTX_template_ox3comb8.html を生成。

戦略 (slotmap §6.7 §2.1):
  - comb5 を読み込み、差分許容セクション (toc/pre_part_a/part_a/a2/part_b/basis) のみ
    ox3comb8 用に in-place 置換
  - 同期義務セクション (head/css/body_pre_toc/marker_legend/part_c_d/footer_spec/js)
    は comb5 から byte-identical 維持 (CP1/CP4 担保)

Usage:
    python scripts/build_ox3comb8_template.py
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "templates" / "KTX_template_comb5.html"
DST = ROOT / "templates" / "KTX_template_ox3comb8.html"


def find_line(lines, pattern, start=0):
    p = re.compile(pattern)
    for i in range(start, len(lines)):
        if p.search(lines[i]):
            return i
    return -1


# toc: 3 records (ア,イ,ウ) + 1-5 で十分 (8 全部は省略可)
OX3COMB8_TOC = '''    <div class="toc-row">
      <a href="#part-a">問題文</a>
      <a href="#answer-area">解答</a>
      <a href="#choice-1">ア</a>
      <a href="#choice-2">イ</a>
      <a href="#choice-3">ウ</a>
      <a href="#basis">共通根拠</a>
      <a href="#c-1">体系</a>
      <a href="#c-7">三層記憶</a>
      <a href="#part-d">⚔ARENA</a>
    </div>'''

# pre_part_a: marker_legend_close+1 〜 part_a_title (= 4 行: 空行 + 3行コメント)
OX3COMB8_PRE_PART_A = '''
  <!-- ============================================================
       PART A ── 問題情報（ox-grid-3 + combination-8 形式）
       ============================================================ -->'''

# part_a: 3 records (ア,イ,ウ) + 8 combinations (1-8)
OX3COMB8_PART_A = '''  <div class="part-title">PART A ── 問題情報</div>

  <section class="section" id="part-a">
    <nav class="sec-nav"><a href="#answer-area">↓解答</a><a href="#choice-1">↓記述ア</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>A-1 問題文</h2>

    <p style="font-weight:600;">{{INSTRUCTION}}</p>

    <h3 style="background:transparent; border-left:none; padding:8px 0 4px 0; margin:20px 0 8px 0; border-bottom:2px dotted var(--border-mid); color:var(--accent); font-family:var(--font-display);">【記述】</h3>

    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_A_LABEL}}</span>{{CHOICE_A_STEM}}</div>
    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_B_LABEL}}</span>{{CHOICE_B_STEM}}</div>
    <div class="problem-text"><span class="choice-num-inline">{{CHOICE_C_LABEL}}</span>{{CHOICE_C_STEM}}</div>

    <h3 style="background:transparent; border-left:none; padding:8px 0 4px 0; margin:20px 0 8px 0; border-bottom:2px dotted var(--border-mid); color:var(--accent); font-family:var(--font-display);">【組合せ】</h3>

    <section class="combinations-section" id="part-a-combinations">
      <div class="combo-block">
        <span class="combo-label">{{COMBO_1_LABEL}}</span>
        <span class="combo-set">{{COMBO_1_SET}}</span>
      </div>
      <div class="combo-block">
        <span class="combo-label">{{COMBO_2_LABEL}}</span>
        <span class="combo-set">{{COMBO_2_SET}}</span>
      </div>
      <div class="combo-block">
        <span class="combo-label">{{COMBO_3_LABEL}}</span>
        <span class="combo-set">{{COMBO_3_SET}}</span>
      </div>
      <div class="combo-block">
        <span class="combo-label">{{COMBO_4_LABEL}}</span>
        <span class="combo-set">{{COMBO_4_SET}}</span>
      </div>
      <div class="combo-block">
        <span class="combo-label">{{COMBO_5_LABEL}}</span>
        <span class="combo-set">{{COMBO_5_SET}}</span>
      </div>
      <div class="combo-block">
        <span class="combo-label">{{COMBO_6_LABEL}}</span>
        <span class="combo-set">{{COMBO_6_SET}}</span>
      </div>
      <div class="combo-block">
        <span class="combo-label">{{COMBO_7_LABEL}}</span>
        <span class="combo-set">{{COMBO_7_SET}}</span>
      </div>
      <div class="combo-block">
        <span class="combo-label">{{COMBO_8_LABEL}}</span>
        <span class="combo-set">{{COMBO_8_SET}}</span>
      </div>
    </section>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>'''

# a2: 1-8 の 8 answer-slot (single-choice、答えは 1-8 のいずれか)
# data-answer-type="ox3comb8" を新設 (slotmap §6.7 §2.4)、validate_structure で
# 専用 mode 識別する
OX3COMB8_A2 = '''  <section class="section" id="answer-area">
    <nav class="sec-nav"><a href="#part-a">↑A-1</a><a href="#choice-1">↓記述ア</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>A-2 解答</h2>

    <div class="answer-area"
         data-correct-value="{{ANSWER}}"
         data-answer-type="ox3comb8"
         data-explanation="{{ANSWER_EXPLANATION}}">
      <h3>正しい組合せを選択</h3>
      <p class="answer-instruction">選択肢を選んで「解答を表示」を押してください。</p>

      <div class="answer-row">
        <button class="answer-slot" type="button" data-num="1" data-value="1">1</button>
        <button class="answer-slot" type="button" data-num="2" data-value="2">2</button>
        <button class="answer-slot" type="button" data-num="3" data-value="3">3</button>
        <button class="answer-slot" type="button" data-num="4" data-value="4">4</button>
        <button class="answer-slot" type="button" data-num="5" data-value="5">5</button>
        <button class="answer-slot" type="button" data-num="6" data-value="6">6</button>
        <button class="answer-slot" type="button" data-num="7" data-value="7">7</button>
        <button class="answer-slot" type="button" data-num="8" data-value="8">8</button>
      </div>

      <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>
      <div id="answer-feedback" hidden></div>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>'''

# part_b: 3 choice-sections (ア,イ,ウ) + 末尾に A-3 共通根拠コメント
OX3COMB8_PART_B = '''
  <!-- ============================================================
       PART B ── 記述別解説（ア〜ウ）
       ============================================================ -->
  <div class="part-title">PART B ── 記述別解説（ア〜ウ）</div>

  <!-- =============== 記述ア =============== -->
  <section class="choice-section odd" id="choice-1">
    <nav class="sec-nav"><a href="#answer-area">↑A-2</a><a href="#choice-2">記述イ→</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_A_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_A_VERDICT_LABEL}}">{{CHOICE_A_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">記述原文</span>
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

  <!-- =============== 記述イ =============== -->
  <section class="choice-section even" id="choice-2">
    <nav class="sec-nav"><a href="#choice-1">←記述ア</a><a href="#choice-3">記述ウ→</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_B_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_B_VERDICT_LABEL}}">{{CHOICE_B_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">記述原文</span>
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

  <!-- =============== 記述ウ =============== -->
  <section class="choice-section odd" id="choice-3">
    <nav class="sec-nav"><a href="#choice-2">←記述イ</a><a href="#basis">↓共通根拠</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">{{CHOICE_C_LABEL}}</div>
      <span class="verdict" data-verdict-label="{{CHOICE_C_VERDICT_LABEL}}">{{CHOICE_C_VERDICT_LABEL}}</span>
    </div>

    <div class="sub-card original">
      <span class="label">記述原文</span>
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

  <!-- ============================================================
       A-3 共通根拠条文・判例（スタブ）
       ============================================================ -->'''

# basis: comb5 と同じ構造、sec-nav の back-link を記述ウ に変更
OX3COMB8_BASIS = '''  <section class="section" id="basis">
    <nav class="sec-nav"><a href="#choice-3">↑記述ウ</a><a href="#c-1">↓C-1</a></nav>
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
        (basis_section, basis_close + 1, OX3COMB8_BASIS.split("\n")),
        (answer_area_close + 1, basis_section, OX3COMB8_PART_B.split("\n")),
        (answer_area_section, answer_area_close + 1, OX3COMB8_A2.split("\n")),
        (part_a_title, answer_area_section, OX3COMB8_PART_A.split("\n")),
        (marker_legend_close + 1, part_a_title, OX3COMB8_PRE_PART_A.split("\n")),
        (toc_open, toc_close + 1, OX3COMB8_TOC.split("\n")),
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
