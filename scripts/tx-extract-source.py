#!/usr/bin/env python3
"""tx-extract-source.py ── TX _lex から物語執筆に必要な情報だけを compact に抜き出す。
250KB の _lex 全読を避け、エージェントが数 KB で済むようにする。

  python scripts/tx-extract-source.py <CODE>

出力（stdout・プレーンテキスト）：
  TITLE / 問題の核心(data-explanation) / 各記述(ox-stmt)＋正誤＋論点コア / PART A 問題文要旨
"""
import sys, re, glob, os, html


def find_lex(code):
    f = f'outputs/ux/000_TX/001_刑法/{code}_lex.html'
    if os.path.exists(f):
        return f
    cand = glob.glob(f'outputs/ux/000_TX/*/{code}_lex.html')
    if not cand:
        raise SystemExit(f'not found: {code}_lex.html')
    return cand[0]


def strip(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def main(code):
    h = open(find_lex(code), encoding='utf-8').read()
    out = []
    m = re.search(r'<title>(.*?)</title>', h)
    out.append(f'TITLE: {strip(m.group(1)) if m else code}')
    de = re.search(r'data-explanation="([^"]+)"', h)
    if de:
        out.append('\n【問題の核心（解説の要旨）】\n' + html.unescape(de.group(1)))
    # 各記述：ox-stmt ＋ verdict（記述記号・正誤・論点コア）
    stmts = re.findall(r'<span class="ox-stmt">(.*?)</span>', h, re.S)
    verd = re.findall(r'<tr data-stmt="([^"]*)"[^>]*>.*?<td[^>]*>([○×])</td><td>(.*?)</td>', h, re.S)
    out.append('\n【各記述と正誤・論点のコア】')
    if verd:
        for i, (sym, ox, core) in enumerate(verd):
            stxt = strip(stmts[i]) if i < len(stmts) else ''
            out.append(f'  ［{sym}］{ox}　記述: {stxt}')
            out.append(f'        論点のコア: {strip(core)}')
    else:
        for i, s in enumerate(stmts):
            out.append(f'  ({i+1}) {strip(s)}')
    # PART A の問題文（.problem-text を結合・先頭 1200 字）
    pts = re.findall(r'class="problem-text"[^>]*>(.*?)</div>', h, re.S)
    if pts:
        joined = ' / '.join(strip(p) for p in pts if strip(p))
        out.append('\n【PART A 問題文（要旨・先頭のみ）】\n' + joined[:1200])
    print('\n'.join(out))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: python scripts/tx-extract-source.py <CODE>'); sys.exit(2)
    main(sys.argv[1])
