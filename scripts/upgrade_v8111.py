#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TX v8.11.0 → v8.11.1 一括アップグレードスクリプト

実施内容：
  1. <div class="final-answer"> に hidden 属性を追加 (S68)
  2. <style> 末尾に §22-quater multi-answer + spoiler-safe CSS を挿入 (S69)
  3. footer-spec に spoiler-safe / multi-answer-css feature-tag を追加 (S51)
  4. fa-summary 内の「正解はN」リテラルを除去 (S70)
  5. TX v8.11.0 → TX v8.11.1 feature-tag 置換
"""
import sys, re, glob, os

CSS_PATCH = '''
/* ============================================================
   §22-quater  multi-answer cells + spoiler-safe reveal
   (v8.11.1 で §22-ter HTML canonical に対応する CSS を正典組込み)
   ============================================================ */

/* §22-ter answer-num-multi セル群 — 多解答型の正答表示 */
.final-answer .answer-num.answer-num-multi{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
  width:auto;
  height:auto;
  background:transparent;
  border-radius:0;
  box-shadow:none;
  margin:6px 0 14px;
  padding:0;
  line-height:1;
}
.final-answer .answer-num-multi .ans-cell{
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  width:62px;
  height:62px;
  border-radius:12px;
  font-family:var(--font-display);
  color:#fff;
  box-shadow:
    0 3px 8px rgba(0,0,0,.20),
    inset 0 1px 0 rgba(255,255,255,.20);
  -webkit-print-color-adjust:exact;
  print-color-adjust:exact;
}
.final-answer .answer-num-multi .ans-cell.ans-correct{
  background:linear-gradient(135deg,var(--recall-correct) 0%,var(--recall-correct-light) 100%);
}
.final-answer .answer-num-multi .ans-cell.ans-incorrect{
  background:linear-gradient(135deg,#7e0024 0%,var(--recall-incorrect) 100%);
}
.final-answer .answer-num-multi .ans-stmt{
  font-size:.92em;
  font-weight:700;
  letter-spacing:.04em;
  margin-bottom:3px;
  opacity:.95;
  text-shadow:0 1px 2px rgba(0,0,0,.30);
}
.final-answer .answer-num-multi .ans-val{
  font-size:1.55em;
  font-weight:800;
  text-shadow:0 1px 2px rgba(0,0,0,.30);
}

/* §22-quater spoiler-safe — 初期は非表示、JS revealFinalAnswer() で開示 */
.final-answer[hidden]{ display:none !important; }
.final-answer.revealed{
  animation:faReveal .4s ease-out;
}
@keyframes faReveal{
  from{ opacity:0; transform:translateY(8px); }
  to  { opacity:1; transform:translateY(0); }
}

'''

NEW_FEATURE_TAGS = (
    '<span class="feature-tag">spoiler-safe</span>・\n'
    '      <span class="feature-tag">multi-answer-css</span>・\n      '
)


def upgrade(fp):
    with open(fp, encoding='utf-8') as f:
        html = f.read()
    changes = []

    # 1. <div class="final-answer"> に hidden 属性追加
    new_html, n = re.subn(
        r'<div class="final-answer">(?![^<]*hidden)',
        '<div class="final-answer" hidden>',
        html
    )
    # ※既存に hidden があれば置換しない正規表現にしたいが簡易版
    if n:
        # 重複防止：すでに hidden 属性のあるものは元に戻すロジック不要、
        # 単純に「<div class="final-answer">」を「<div class="final-answer" hidden>」に置換
        html = new_html.replace(
            '<div class="final-answer" hidden hidden>',
            '<div class="final-answer" hidden>'
        )
        changes.append(f'S68: hidden added ({n} occurrence)')

    # 2. <style> 末尾に CSS パッチ挿入（既に挿入済みかチェック）
    if '@keyframes faReveal' not in html:
        html = html.replace('</style>', CSS_PATCH + '</style>', 1)
        changes.append('S69: CSS patch inserted')

    # 3. footer-spec に feature-tag 追加（既存チェック）
    if 'spoiler-safe' not in html:
        # TX v8.11.0 → TX v8.11.1 置換 + 直後に新タグ追加
        # まずバージョン置換
        html = html.replace(
            '<span class="feature-tag">TX v8.11.0</span>',
            '<span class="feature-tag">TX v8.11.1</span>'
        )
        # ktx301-canon の後に挿入
        html = html.replace(
            '<span class="feature-tag">ktx301-canon</span>・\n      ',
            '<span class="feature-tag">ktx301-canon</span>・\n      ' + NEW_FEATURE_TAGS,
            1
        )
        changes.append('S51: feature-tags added + version bump')

    # 4. fa-summary 内の「正解はN」リテラル除去（句点前まで削除）
    pattern = re.compile(
        r'(<p class="fa-summary">.*?)正解は[0-9XＸア-ン・]{1,15}[。．]',
        re.DOTALL
    )
    new_html, n = pattern.subn(r'\1', html)
    if n:
        html = new_html
        changes.append(f'S70: literal removed ({n} occurrence)')

    # 書き戻し
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(html)
    return changes


def main():
    folder = r'C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam\outputs\000_TX\刑TX'
    files = sorted(glob.glob(os.path.join(folder, '*.html')))
    print(f'Target: {len(files)} files')
    for fp in files:
        changes = upgrade(fp)
        name = os.path.basename(fp)
        if changes:
            print(f'  [OK] {name}: ' + ' / '.join(changes))
        else:
            print(f'  [SKIP] {name}: no changes (already upgraded)')


if __name__ == '__main__':
    main()
