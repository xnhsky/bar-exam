#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix-choice-num-indent.py — 丸囲い番号バッジ（.choice-num-inline）の字下げ継承バグを恒久修正。

原因：.choice-num-inline は display:inline-block で、CSS 継承プロパティである
text-indent を親段落（.case-paragraph / .problem-text-body ＝ text-indent:1em）
から受け継ぐ。円形バッジは幅 24px なので 1em の字下げで中の数字（①②③④）が
右へ押し出され、円からはみ出す/切れる。
恒久対処：ベース .choice-num-inline 規則に text-indent:0 を必ず持たせる。

対象：.choice-num-inline{...border-radius:50%...} のベース規則のみ（パレット
上書き規則 .choice-num-inline{background:... !important} は対象外）。冪等。
使い方： python scripts/fix-choice-num-indent.py <files...>   （--check で検査のみ・exit1=未修正あり）
"""
import re, sys, glob, os

# ベース規則＝ border-radius:50% を含む .choice-num-inline{...} ブロック
BASE_RE = re.compile(r'\.choice-num-inline\s*\{[^}]*?border-radius:\s*50%[^}]*?\}', re.S)


def needs_fix(css):
    m = BASE_RE.search(css)
    if not m:
        return False  # バッジ定義が無いファイルは対象外
    return 'text-indent' not in m.group(0)


def patch(css):
    def repl(m):
        block = m.group(0)
        if 'text-indent' in block:
            return block
        # 閉じ } の直前に text-indent:0; を挿入
        return block[:-1].rstrip() + ' text-indent:0; }'
    return BASE_RE.sub(repl, css, count=1)


def main():
    check = '--check' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    files = []
    for a in args:
        files.extend(glob.glob(a, recursive=True))
    files = sorted(set(files))
    fixed = bad = 0
    for f in files:
        # newline='' で CRLF/LF を保存（改行変換をしない＝バッジ規則1行だけの最小 diff）
        with open(f, encoding='utf-8', newline='') as fh:
            css = fh.read()
        if not needs_fix(css):
            continue
        bad += 1
        if check:
            print('[NEEDS-FIX] ' + f)
            continue
        with open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(patch(css))
        fixed += 1
    if check:
        print('\n未修正 %d / %d 走査' % (bad, len(files)))
        return 1 if bad else 0
    print('修正 %d / %d 走査' % (fixed, len(files)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
