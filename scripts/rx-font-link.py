#!/usr/bin/env python3
"""RX 論証カードに作り込みフォント（Google Fonts）を読み込ませる（2026-06-20・冪等）.

RX カードは TX(GENESIS)/JX(ATHENA) と同じフォント（Shippori Mincho B1 等）を
font-family に指定しているが、`<head>` に Google Fonts の `<link>` が無いため
iOS など当該フォント非搭載環境では generic serif にフォールバックし、TX/JX のような
作り込み表示にならなかった。本スクリプトは ATHENA と完全同一のフォント link 3 行
（preconnect ×2＋stylesheet）を各 RX の `<head>` 直後へ注入する。

- link を TX/JX と同一 URL にすることでブラウザのフォントキャッシュを共有でき、
  TX/JX を見た後の RX 表示は再ダウンロード不要。
- フォント未読込時もシステムフォント（Hiragino Sans / serif）へフォールバックして動作する
  ため、完全オフラインでも閲覧自体は可能（見た目が素のフォントになるだけ）。
- 冪等：既に fonts.googleapis.com を含むファイルはスキップ。EOL は元ファイルに合わせて保持。
"""
from __future__ import annotations
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
MARKER = b"fonts.googleapis.com"
HEAD_OPEN = b"<head>"
# ATHENA / GENESIS-CORE と完全一致のフォント読込 3 行。
FONT_LINES = [
    '<link rel="preconnect" href="https://fonts.googleapis.com">',
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
    '<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@400;500;700;800'
    "&family=Shippori+Antique&family=Zen+Old+Mincho:wght@400;500;700;900"
    "&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Zen+Maru+Gothic:wght@400;500;700"
    "&family=Noto+Serif+JP:wght@400;500;700&family=Noto+Sans+JP:wght@400;500;700"
    "&family=Kaisei+Decol:wght@400;500;700&family=Kosugi+Maru&family=Source+Code+Pro:wght@400;600;700"
    "&family=M+PLUS+Rounded+1c:wght@500;700;800&family=M+PLUS+1p:wght@500;700;800;900"
    '&display=swap" rel="stylesheet">',
]


def main() -> int:
    applied = skipped = nohead = 0
    for f in sorted((REPO / "outputs/ux/002_RX").rglob("*.html")):
        data = f.read_bytes()
        if MARKER in data:
            skipped += 1
            continue
        idx = data.find(HEAD_OPEN)
        if idx < 0:
            nohead += 1
            continue
        eol = "\r\n" if b"\r\n" in data else "\n"
        insert_at = idx + len(HEAD_OPEN)
        block = (eol + eol.join(FONT_LINES)).encode("utf-8")
        data = data[:insert_at] + block + data[insert_at:]
        f.write_bytes(data)
        applied += 1
    print(f"applied={applied} skipped(has-font)={skipped} no-head={nohead}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
