#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx-lex-sysmap-center.py — 体系マップSVGの「ラベル見出し中央化＋本文初行字下げ」を
決定論・冪等・CRLF保存で全 v13 LOOP-CARD へ適用する（ユーザー訂正 2026-07-04 の正典化）。

体系マップの各カテゴリ箱（職権/濫用/権利妨害 等）は色帯ヘッダーが左寄せ・本文も字下げ無しだった。
① ヘッダー統合中央化：category(font-size 18) と sublabel(font-size 16) の隣接ペアを
   1つの <text x="0" text-anchor="middle"> ＋ <tspan> に統合＝箱幅に依らず確実に中央。
   サブラベルの無い単独 category(256型) は単独で中央化。
② 本文初行字下げ：各箱の本文初行（y="58" fill="#493730" font-size="14.5"）の本文頭へ
   全角スペースを1つ挿入（x座標に依存せず・箱幅が違っても効く・二重挿入しない）。

SVG座標・本文は他を一切変えない。冪等（再実行で無変化）。CRLF を保存する。
  適用: python scripts/tx-lex-sysmap-center.py --apply
  点検: python scripts/tx-lex-sysmap-center.py
"""
import sys, glob, io, os, re

PAIR = re.compile(
    r'<text x="-?\d+" y="23"[^>]*font-size="18">([^<]*)</text>\s*'
    r'<text x="-?\d+" y="23"[^>]*font-size="16">([^<]*)</text>')

LONE = re.compile(r'<text x="-?\d+" y="23"([^>]*?)font-size="18">([^<]*)</text>')

BODY = re.compile(r'(<text x="-?\d+" y="58" fill="#493730" font-size="14\.5">)(　?)([^<]*)(</text>)')


def merge_pair(m):
    return ('<text x="0" y="23" text-anchor="middle" fill="#fff" font-weight="700" font-size="16">'
            '<tspan font-weight="800" font-size="18">' + m.group(1) + '</tspan>　' + m.group(2) + '</text>')


def center_lone(m):
    attrs = m.group(1)
    if 'text-anchor' in attrs:      # 既に中央化済み → 触らない（冪等）
        return m.group(0)
    return '<text x="0" y="23" text-anchor="middle"' + attrs + 'font-size="18">' + m.group(2) + '</text>'


def indent_body(m):
    if m.group(2) == '　':      # 既に字下げ済み → 触らない（冪等）
        return m.group(0)
    return m.group(1) + '　' + m.group(3) + m.group(4)


def fix(text):
    n = {}
    text, n['pair'] = PAIR.subn(merge_pair, text)
    text, n['lone'] = LONE.subn(center_lone, text)
    text, n['body'] = BODY.subn(indent_body, text)
    return text, n


def main():
    apply = '--apply' in sys.argv
    files = sorted(f for f in glob.glob('outputs/ux/000_TX/**/*_lex.html', recursive=True))
    changed = 0
    for f in files:
        with io.open(f, 'r', encoding='utf-8', newline='') as fh:
            raw = fh.read()
        crlf = '\r\n' in raw
        src = raw.replace('\r\n', '\n')
        if 'class="tx-sysmap"' not in src and 'tx-sysmap-svg' not in src:
            continue
        # ---- 420 の旧字下げ（x=-184 の x シフト方式）を素の -198 へ戻し、全角スペース方式へ統一 ----
        src2 = src.replace('<text x="-184" y="58" fill="#493730" font-size="14.5">',
                           '<text x="-198" y="58" fill="#493730" font-size="14.5">')
        new, n = fix(src2)
        if new == src:
            continue
        changed += 1
        tag = os.path.basename(f).replace('_lex.html', '')
        print(f"[{'APPLIED' if apply else 'WOULD-FIX'}] {tag}: pair={n['pair']} lone={n['lone']} body={n['body']}")
        if apply:
            out = new.replace('\n', '\r\n') if crlf else new
            with io.open(f, 'w', encoding='utf-8', newline='') as fh:
                fh.write(out)
    print(f"\n{'applied' if apply else 'would-fix'} files: {changed}")


if __name__ == '__main__':
    main()
