#!/usr/bin/env python3
"""RX 規範ボックスをレモンイエロー標準化（2026-06-20・冪等）.

RX 論証カードは「規範（暗記対象）」ボックスをユーザー要望でレモンイエローに統一する。
RX はファイルごとに inline CSS が異なる（変数 --norm-bg を使う版／直書きの版）ため、
既存 CSS を書き換えるのではなく **</style> 直前にオーバーライドを追記**して一律に上書きする
（同 specificity の後勝ち。多様な形式に非依存で安全・冪等）。あわせて元データに無かった
「🔑 規範」バッジを ::before で新設する。

冪等：マーカー /* RX-LEMON が既にあればスキップ。EOL は元ファイルに合わせて保持。
"""
from __future__ import annotations
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
MARKER = b"/* RX-LEMON"
BLOCK_LINES = [
    "",
    "/* RX-LEMON 規範ボックス標準色（レモンイエロー）＋規範バッジ（2026-06-20 統一） */",
    ".norm-box{background:#fff7a8;border:2px solid #e8c400;color:#5a4012;position:relative;margin-top:22px;}",
    '.norm-box::before{content:"\U0001F511 規範";position:absolute;top:-13px;left:14px;'
    "background:#ffe24d;color:#5a4012;padding:2px 12px;border-radius:999px;font-size:.78em;"
    "font-weight:700;letter-spacing:.07em;border:1.5px solid #e8c400;box-shadow:0 1px 3px rgba(0,0,0,.12);}",
    "",
]


def main() -> int:
    applied = skipped = nostyle = 0
    for f in sorted((REPO / "outputs/ux/002_RX").rglob("*.html")):
        data = f.read_bytes()
        if MARKER in data:
            skipped += 1
            continue
        idx = data.rfind(b"</style>")
        if idx < 0:
            nostyle += 1
            continue
        eol = "\r\n" if b"\r\n" in data else "\n"
        block = (eol.join(BLOCK_LINES)).encode("utf-8")
        data = data[:idx] + block + data[idx:]
        f.write_bytes(data)
        applied += 1
    print(f"applied={applied} skipped={skipped} no-style={nostyle}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
