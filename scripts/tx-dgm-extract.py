#!/usr/bin/env python3
"""_lex から図解（TX-DGM）執筆に必要な素材を抽出して表示する（読み取り専用）

usage: python scripts/tx-dgm-extract.py <対象_lex.html>

出力：記述（ox-stmt＋pool-gist の正誤・理由）／物語解説の全段落／
各記述カードの GIST・PATH・HOOK・TRAP・BASIS 見出し・既存図解 id。
これだけで「効く論点の選定→レーン/ステップの中身の執筆」ができる。
data-stmt は数字型（1〜5）とカタカナ型（ア〜オ）の両方に対応。
"""
import re, sys, html

def strip(s):
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(re.sub(r'\s+', ' ', s)).strip()

def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    src = open(path, encoding='utf-8').read()

    print("=" * 20, path.split('/')[-1], "=" * 20)

    print("### 記述（ox-grid）")
    for m in re.finditer(r'<div class="ox-row" data-stmt="([^"]+)">(.*?)(?=<div class="ox-row"|\Z)', src, re.S):
        n, seg = m.group(1), m.group(2)[:6000]
        stmt = re.search(r'class="ox-stmt">(.*?)</span>', seg, re.S)
        gist = re.search(r'class="ox-pool-gist">(.*?)</p>', seg, re.S)
        if stmt:
            print(f"  [{n}]", strip(stmt.group(1))[:220])
        if gist:
            print(f"      →", strip(gist.group(1))[:260])
        print()

    print("### 物語解説（fa-narrative）")
    nar = re.search(r'<div class="fa-narrative"(.*?)(?=<div class="fa-crosscheck|<table|<div class="answer-ox-grid")', src, re.S)
    if nar:
        for m in re.finditer(r'<p\b[^>]*>(.*?)</p>|<div class="tx-dgm"[^>]*data-dgm="([^"]*)"', nar.group(1), re.S):
            if m.group(2):
                print(f"  --[既存図解 {m.group(2)}]--")
                continue
            t = strip(m.group(1))
            if t:
                print("  ¶", t[:400])
                print()

    print("\n### 記述カード（article.tx-inline-card）")
    for m in re.finditer(r'<article class="tx-inline-card" data-stmt="([^"]+)"[^>]*>(.*?)</article>', src, re.S):
        n, c = m.group(1), m.group(2)

        def grab(cls, label, limit=400):
            mm = re.search(r'class="[^"]*\b' + cls + r'\b[^"]*"[^>]*>(.*?)</(?:p|div|blockquote|span)>', c, re.S)
            if mm:
                print(f"  [{n}] {label}:", strip(mm.group(1))[:limit])

        grab('syn-lead', 'GIST')
        sp = re.search(r'<div class="syn-path"[^>]*>(.*?)</div>\s*(?=<div|<p|<details)', c, re.S)
        if sp:
            print(f"  [{n}] PATH:", strip(sp.group(1))[:700])
        grab('syn-image', 'HOOK', 250)
        tr = re.search(r'class="[^"]*tx-v13-trap[^"]*"[^>]*>(.*?)(?=<div class="(?!$)|<details)', c, re.S)
        if tr:
            print(f"  [{n}] TRAP:", strip(tr.group(1))[:450])
        for bm in re.finditer(r'class="[^"]*basis-mini-head[^"]*"[^>]*>(.*?)</(?:p|div|span)>', c, re.S):
            print(f"  [{n}] BASIS:", strip(bm.group(1))[:130])
        dg = re.findall(r'data-dgm="([^"]*)"', c)
        if dg:
            print(f"  [{n}] 既存図解:", dg)
        print()

if __name__ == '__main__':
    main()
