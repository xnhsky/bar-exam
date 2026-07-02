#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TXLEX v12.2.2 体系マップ戻りリンク挿入（deterministic, idempotent）.

gold 361/367 と同じく、各 inline カードの詳説 </details> 直後に
`<div class="tx-sysmap-back"><a href="#tx-sysmap">↑ 体系マップに戻る</a></div>`
を1つずつ挿入する。既に直後にある場合はスキップ（冪等）。newline 保全。

前提: ファイルに .tx-sysmap（体系マップ）が存在すること（存在しなければ何もしない）。

Usage: python -X utf8 scripts/tx-lex-v1222-backlink.py <file> [...]
"""
import io, re, sys

BACK = '\n<div class="tx-sysmap-back"><a href="#tx-sysmap">↑ 体系マップに戻る</a></div>'
DETAIL_CLOSE = "</details>"
PAT = re.compile(r'<details class="tx-inline-detail">.*?</details>', re.S)


def read(p):
    return io.open(p, encoding="utf-8", newline="").read()


def write(p, t):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def main():
    for path in sys.argv[1:]:
        h = read(path)
        if 'class="tx-sysmap"' not in h:
            print("[SKIP] %s (no tx-sysmap)" % path); continue
        added = 0
        out = []
        last = 0
        for m in PAT.finditer(h):
            end = m.end()
            out.append(h[last:end])
            tail = h[end:end + 80]
            if "tx-sysmap-back" not in tail:
                out.append(BACK)
                added += 1
            last = end
        out.append(h[last:])
        if added:
            write(path, "".join(out))
        print("[OK] %s back-links added: %d" % (path, added))


if __name__ == "__main__":
    main()
