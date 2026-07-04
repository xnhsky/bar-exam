#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tx-lex-sysmap-gold-sync.py — v13 体系マップ系 _lex を gold(刑TX359) 基準へ決定論同期する。

背景：v13 移行（放火357-367 / 偽造368-385 クラスタ）で、gold 359 に施した3つの
表示修正がクラスタへ伝播せず、以下の欠落が残った（接ぎ木ではなく欠落）。
  ① 体系マップSVGの狭幅つぶれ（min-width/overflow-x 規則欠落）→ 文字がボックスからはみ出る
  ② 肢カードのゼブラ交互背景CSS欠落 → 問題文が交互背景にならない
  ③ 正誤表を体系マップ直前（＝冒頭）へ挿すJS分岐欠落 → ストーリー解説の下に正誤表が落ちる
     （reveal/browse 双方の insert アンカーが gold と異なる）

本スクリプトは gold 359 と同一のテキストを、gold と同じ位置へ、欠落時のみ挿入する
（冪等・本文/問題固有データ不変）。アンカー不一致のファイルは触らず報告する。
"""
import sys, glob, io, os

STRIPE_SELECTOR = ".tx-inline-judge-list .tx-inline-card:nth-of-type(even)"
SVG_SELECTOR    = ".tx-sysmap-figure svg.tx-sysmap-svg"

CSS_ANCHOR = ".radial-svg ellipse{ fill:var(--accent-darker)!important; }"

STRIPE_RULE = """/* === 問題文原文の交互背景（ゼブラ）: 記述カードを1つおきに淡く染め、記述の切れ目を目で追える ===
   pale bg + dark text を維持（WCAG）。偶数カードだけ暖色クリームへ。テクスチャ線は踏襲。 */
.tx-inline-judge-list .tx-inline-card:nth-of-type(even){
  background:
    linear-gradient(180deg,rgba(250,240,226,.96) 0%,rgba(247,235,220,.98) 100%),
    repeating-linear-gradient(0deg,rgba(80,55,35,.032) 0,rgba(80,55,35,.032) 1px,transparent 1px,transparent 7px);
}"""

SVG_RULES = """.tx-sysmap-figure{ margin-top:14px; overflow-x:auto; }
.tx-sysmap-figure svg.tx-sysmap-svg{ width:100%; height:auto; display:block; min-width:640px; }"""

# --- JS Fix A: getInlineAnswerTablePanel は正誤表を体系マップ直前へ挿す ---
JS_A_OLD = """      panel.setAttribute('hidden', '');
      var story = document.querySelector('.tx-inline-story-panel');
      if (story && story.parentNode) {
        story.parentNode.insertBefore(panel, story);
      } else {"""
JS_A_NEW = """      panel.setAttribute('hidden', '');
      // 正誤表（テーゼ版）は体系マップ(.tx-sysmap)の直前へ置く（露出順: 正誤表 → 体系マップ → 肢カード）。
      var sysmap = document.querySelector('.tx-sysmap');
      var story = document.querySelector('.tx-inline-story-panel');
      if (sysmap && sysmap.parentNode) {
        sysmap.parentNode.insertBefore(panel, sysmap);
      } else if (story && story.parentNode) {
        story.parentNode.insertBefore(panel, story);
      } else {"""

# --- JS Fix B: getInlineStoryPanel は肢カード列の直後へ挿す（reviewPanel基準を廃す） ---
JS_B_OLD = """      panel.setAttribute('hidden', '');
      var reviewPanel = document.querySelector('.tx-inline-answer-table-panel');
      if (reviewPanel && reviewPanel.parentNode) {
        reviewPanel.parentNode.insertBefore(panel, reviewPanel.nextSibling);
      } else {"""
JS_B_NEW = """      panel.setAttribute('hidden', '');
      var judge = document.querySelector('.tx-inline-judge-list, .tx-inline-list');
      if (judge && judge.parentNode) {
        judge.parentNode.insertBefore(panel, judge.nextSibling);
      } else {"""


def fix(text):
    """returns (new_text, changes:list, skips:list)"""
    changes, skips = [], []
    has_sysmap = 'class="tx-sysmap"' in text

    # --- CSS: 欠落規則を gold 位置（radial-svg ellipse アンカー直後）へ挿入 ---
    missing = []
    if STRIPE_SELECTOR not in text:
        missing.append(STRIPE_RULE)
        changes.append('css:stripe')
    if has_sysmap and SVG_SELECTOR not in text:
        missing.append(SVG_RULES)
        changes.append('css:svg')
    if missing:
        if CSS_ANCHOR in text:
            block = CSS_ANCHOR + "\n" + "\n".join(missing)
            text = text.replace(CSS_ANCHOR, block, 1)
        else:
            skips.append('css-anchor-missing')
            # revert change tags we can't apply
            changes = [c for c in changes if not c.startswith('css')]

    # --- JS A ---
    if JS_A_OLD in text:
        text = text.replace(JS_A_OLD, JS_A_NEW, 1)
        changes.append('js:tablePanel->sysmap')
    elif 'sysmap.parentNode.insertBefore(panel, sysmap)' not in text and has_sysmap:
        skips.append('jsA-anchor-missing')

    # --- JS B ---
    if JS_B_OLD in text:
        text = text.replace(JS_B_OLD, JS_B_NEW, 1)
        changes.append('js:storyPanel->judge')

    return text, changes, skips


def main():
    apply = '--apply' in sys.argv
    files = sorted(f for f in glob.glob('outputs/ux/000_TX/**/*_lex.html', recursive=True))
    changed_n = 0
    for f in files:
        # 改行コードを保存（Windows 生成の CRLF を維持し、無関係な全行 diff を防ぐ）
        with io.open(f, 'r', encoding='utf-8', newline='') as fh:
            raw = fh.read()
        is_crlf = '\r\n' in raw
        src = raw.replace('\r\n', '\n')
        # v13 inline エンジンを持つファイルのみ対象（旧版は無関係なので触らない）
        if 'getInlineAnswerTablePanel' not in src:
            continue
        new, changes, skips = fix(src)
        if not changes and not skips:
            continue
        tag = os.path.basename(f)
        if changes:
            changed_n += 1
            status = 'APPLIED' if apply else 'WOULD-FIX'
            print(f"[{status}] {tag}: {', '.join(changes)}" + (f"  ⚠skip={skips}" if skips else ""))
            if apply and new != src:
                out = new.replace('\n', '\r\n') if is_crlf else new
                with io.open(f, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(out)
        elif skips:
            print(f"[SKIP] {tag}: {skips}")
    print(f"\n{'applied' if apply else 'would-fix'} files: {changed_n}")


if __name__ == '__main__':
    main()
