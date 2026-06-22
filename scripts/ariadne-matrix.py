#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARIADNE 骨子（.bone）マトリクスの視覚的可読性を上げる（記載方式は不変）。
- bsec を金アクセントバー付きの箱に（GOAL=金テーマと連動）
- 各第N 見出し .b1 を独立ヘッダー化（display:block＋下罫線）
- b1 ブロック化で pre-wrap に出る余分な改行（見出し直後の \\n）を除去
冪等：強化版CSSが既にあればスキップ。LF/CRLF 保存。
"""
import re, sys, pathlib, glob

OLD_CSS = (
    '.bone .bsec,.kp-model .bsec{white-space:pre-wrap; background:#f3f2f5; '
    'border:1px solid #e6e3ec; border-radius:9px; padding:8px 13px 9px; margin:11px 0 0}\n'
    '.bone .bsec:first-child,.kp-model .bsec:first-child{margin-top:0}'
)
NEW_CSS = (
    '.bone .bsec,.kp-model .bsec{white-space:pre-wrap; background:#f6f5f8; '
    'border:1px solid #e7e4ec; border-left:4px solid var(--gd-line); border-radius:9px; '
    'padding:11px 16px 12px; margin:13px 0 0}\n'
    '.bone .bsec:first-child,.kp-model .bsec:first-child{margin-top:0}\n'
    '.bone .b1,.kp-model .b1{display:block; padding-bottom:6px; margin-bottom:7px; '
    'border-bottom:1px solid var(--gd-line); font-size:.97rem; letter-spacing:.01em}'
)

# b1 見出し閉じ直後の改行1個を除去（b1 内容にタグは無い＝[^<]*）
B1_NL_RE = re.compile(r'(<span class="b1">[^<]*</span>)\n')


def process(path: pathlib.Path):
    with open(path, encoding='utf-8', newline='') as fh:
        txt = fh.read()
    nl = '\r\n' if '\r\n' in txt else '\n'
    changed = []
    if NEW_CSS.split('\n')[0] not in txt:
        old = OLD_CSS.replace('\n', nl)
        new = NEW_CSS.replace('\n', nl)
        if old in txt:
            txt = txt.replace(old, new, 1)
            changed.append('css')
    # 見出し直後の改行除去。b1 は静的HTMLでは bone 内にしか存在しない（モデルは実行時生成）
    # ため、bsec 入れ子で div スコープが壊れる問題を避けて全体に適用する。
    pat = re.compile(r'(<span class="b1">[^<]*</span>)' + re.escape(nl))
    new_txt = pat.sub(r'\1', txt)
    if new_txt != txt:
        changed.append('nl')
        txt = new_txt
    if changed:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(txt)
    return changed


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    files = []
    for a in args:
        files += glob.glob(a)
    for fp in files:
        if not fp.endswith('.html'):
            continue
        c = process(pathlib.Path(fp))
        print(f"{pathlib.Path(fp).name}: {','.join(c) if c else 'no-change'}")


if __name__ == '__main__':
    main()
