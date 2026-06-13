#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jx-indent-bodytext.py — JX 本文の段落字下げ（一字下げ）を適用する。

方式：CSS `text-indent:1em` を **クラス無しの本文 <p>**（解説・規範プロセ・模範答案・採点講評等）
にだけ適用する（`.step`/`.arrow`/`.judgment-text`/`.subtitle`/`.closing` 等のクラス付き <p> は
フロー矢印・規範ボックス・見出し系なので字下げ対象外）。本文テキストは原則不改変。

唯一の本文改変：模範答案などの `<p>　`（先頭 全角スペースによる旧来の字下げ）を `<p>` に正規化する。
これを残すと CSS の text-indent と二重字下げになるため、CSS 方式へ一本化する。

冪等：字下げ CSS マーカーが既にあれば CSS 注入を skip（先頭全角スペース除去は再実行しても無害）。
"""

import re
import sys
from pathlib import Path

INDENT_CSS = """
/* ==========================================
   本文の字下げ（段落一字下げ・クラス無し <p> のみ／矢印・規範ボックス等は対象外）
   ========================================== */
.container p:not([class]){ text-indent:1em; }
@media print{ .container p:not([class]){ text-indent:1em; } }
"""

MARKER = '.container p:not([class])'


def apply_indent(path: Path):
    s = path.read_text(encoding='utf-8')
    log = []

    # 1) 先頭 全角スペース字下げ（クラス無し <p>　）を除去して CSS に一本化
    n_space = len(re.findall(r'<p>　', s))
    if n_space:
        s = s.replace('<p>　', '<p>')
        log.append(f'先頭全角スペース除去 {n_space} 件')

    # 2) 字下げ CSS を </style> 直前へ注入（冪等）
    if MARKER in s:
        log.append('CSS: 既存 skip')
    else:
        idx = s.find('</style>')
        if idx == -1:
            raise ValueError('</style> not found')
        s = s[:idx] + INDENT_CSS + s[idx:]
        log.append('CSS: text-indent 注入')

    path.write_text(s, encoding='utf-8')
    return log


def main(argv):
    if len(argv) < 2:
        print('usage: jx-indent-bodytext.py <file.html> [file2.html ...]')
        return 2
    rc = 0
    for f in argv[1:]:
        p = Path(f)
        try:
            log = apply_indent(p)
            print(f'[OK] {p.name}: ' + ' / '.join(log))
        except Exception as e:
            rc = 1
            print(f'[ERROR] {p.name}: {e}')
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv))
