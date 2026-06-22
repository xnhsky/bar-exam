#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARIADNE のバッジ／タブ／ラベルで letter-spacing による右寄り（右側だけ余白）を
TX の作法どおり text-indent＝letter-spacing 同値併記で中央化する。
対象を限定：letter-spacing が非0 で、かつ
  (本体に inline-block を含む＝インラインバッジ) または (セレクタが ::before/::after＝ラベル疑似要素)
のルールのみ。本文・見出し（block テキスト）は対象外（右寄り問題が起きない）。
冪等：text-indent が既に letter-spacing と同値ならスキップ。LF/CRLF 保存。
"""
import re, sys, pathlib, glob

RULE_RE = re.compile(r'([^{}]+)\{([^}]*)\}', re.DOTALL)
LS_RE = re.compile(r'letter-spacing:\s*([^;!]+)(\s*!important)?\s*;')
TI_RE = re.compile(r'text-indent:\s*([^;!]+)(\s*!important)?\s*;')


def fix(path: pathlib.Path):
    with open(path, encoding='utf-8', newline='') as fh:
        txt = fh.read()
    changed = 0

    def repl(m):
        nonlocal changed
        sel, body = m.group(1), m.group(2)
        lsm = LS_RE.search(body)
        if not lsm:
            return m.group(0)
        ls = lsm.group(1).strip()
        if ls in ('0', 'normal', '0px', '0em'):
            return m.group(0)
        is_badge = ('inline-block' in body) or ('::before' in sel) or ('::after' in sel)
        if not is_badge:
            return m.group(0)
        tim = TI_RE.search(body)
        if tim and tim.group(1).strip() == ls:
            return m.group(0)  # 既に一致＝冪等
        if tim:
            new_body = body[:tim.start()] + f'text-indent:{ls};' + body[tim.end():]
        else:
            # letter-spacing 宣言の直後に text-indent を挿入
            ins = lsm.end()
            new_body = body[:ins] + f' text-indent:{ls};' + body[ins:]
        changed += 1
        return sel + '{' + new_body + '}'

    new_txt = RULE_RE.sub(repl, txt)
    if changed:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(new_txt)
    return changed


def main():
    files = []
    for a in sys.argv[1:]:
        if not a.startswith('--'):
            files += glob.glob(a)
    for fp in files:
        if fp.endswith('.html'):
            n = fix(pathlib.Path(fp))
            print(f"{pathlib.Path(fp).name}: {n} rules fixed")


if __name__ == '__main__':
    main()
