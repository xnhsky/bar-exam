#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx-lex-v131-author.py ── v13.1.0 の問題固有スロット（規範核バッジ＋印付き原文）を authored データから一括鋳造。

前提：先に `tx-lex-verdict-redesign.py` で土台（CSS＋エンジン＋帰结箱除去）を注入済みの _lex に対して実行する。
入力 JSON（問題ごとに執筆）: { "1": {"kihan": "…規範核1文…", "mark": "…印付き原文HTML…"}, "2": {...}, ... }
  - kihan: 体系マップ記述札の ✍規範核バッジ本文（転用可能な規範核・11〜14字）。
  - mark : 正誤表の印付き記述原文（<span class='tx-stmt-x'>…×…</span><span class='tx-stmt-fix'>→正解</span> 等・
           属性は二重引用/内側 class は単引用）。

やること（本文の他部分は不変）:
  1. 各体系マップ記述札ノード（<a href="#stmt-N"><g transform="translate(X,392)">…</g></a>）を高さ92→118へ拡張し、
     1行目ノート y58→52・記述N y82→110 へ寄せ、✍規範核バッジ（.nb-badge＋.nb-badge-text）を挿入。
     バッジ色はノード枠 stroke の暗色（既知3色マップ＋汎用暗色化）。
  2. svg.tx-sysmap-svg の viewBox 下端を 532 へ詰める（帰结箱除去分）。
  3. 各正誤表行 <tr data-stmt="N" …> に data-brief-mark="…mark…" を付与。
版スタンプ（v13.1.0）は別途 tx-lex-v13-stamp.py が実体判定で行う。

使い方: python -X utf8 scripts/tx-lex-v131-author.py <lex.html> <data.json>
"""
import sys
import re
import json

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ノード枠 stroke 色 → バッジ暗色（359/371 と同一）
DARK = {"#5a86a8": "#3f6a8c", "#b0635c": "#8f4a44", "#c99a3a": "#9a7328"}


def darken(hexc):
    if hexc.lower() in DARK:
        return DARK[hexc.lower()]
    try:
        r = int(hexc[1:3], 16); g = int(hexc[3:5], 16); b = int(hexc[5:7], 16)
        f = 0.68
        return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))
    except Exception:
        return "#6a4a44"


def extract_synorig(html, n):
    """記述 n のカードの syn-orig（印付き記述原文＝検証済み）を抽出し、属性用に単引用化して返す。"""
    m = re.search(r'<article class="tx-inline-card"[^>]*data-stmt="' + re.escape(n) + r'"[^>]*>(.*?)</article>', html, re.DOTALL)
    if not m:
        return ""
    sm = re.search(r'<p class="syn-orig"><span class="syn-tag[^>]*>[^<]*</span>(.*?)</p>', m.group(1), re.DOTALL)
    if not sm:
        return ""
    return sm.group(1).strip().replace('"', "'")


def process(html, data):
    stats = {"nodes": 0, "rows": 0}
    # 1) ノード加工
    node_re = re.compile(r'(<a href="#stmt-([^"]+)"><g transform="translate\(\d+,392\)">)(.*?)(</g></a>)', re.DOTALL)

    def fix_node(m):
        head, n, body, tail = m.group(1), m.group(2), m.group(3), m.group(4)
        if n not in data or "nb-badge" in body:
            return m.group(0)
        kihan = data[n].get("kihan", "").strip()
        if not kihan:
            return m.group(0)
        stroke = "#b0635c"
        sm = re.search(r'stroke="(#[0-9a-fA-F]{6})" stroke-width="2"/>', body)
        if sm:
            stroke = sm.group(1)
        badge_fill = darken(stroke)
        b = body.replace('height="92"', 'height="118"')
        b = b.replace('<text x="-118" y="58"', '<text x="-118" y="52"')
        badge = ('<rect class="nb-badge" x="-118" y="64" width="228" height="30" rx="9" fill="%s"/>\n'
                 '<text class="nb-badge-text" x="-104" y="84" fill="#fff" font-weight="800" font-size="13">✍ %s</text>\n'
                 % (badge_fill, kihan))
        b = re.sub(r'(<text x="118" y=")82(")', r'\g<1>110\g<2>', b)
        b = badge + '<text x="118" y="110"'.join(b.split('<text x="118" y="110"')) if False else b
        # 記述N テキスト行の直前にバッジを差し込む
        b = re.sub(r'(<text x="118" y="110" text-anchor="end")', badge + r'\1', b, count=1)
        stats["nodes"] += 1
        return head + b + tail

    html = node_re.sub(fix_node, html)
    # 2) viewBox
    html = re.sub(r'(tx-sysmap-svg" viewBox="0 0 1500 )\d+(")', r'\g<1>532\g<2>', html, count=1)
    # 3) 正誤表行に data-brief-mark
    for n, d in data.items():
        mark = d.get("mark", "").strip() or extract_synorig(html, n)
        if not mark:
            continue
        pat = re.compile(r'(<tr data-stmt="%s")( data-verdict="[ox]")(?![^>]*data-brief-mark)' % re.escape(n))
        html, cnt = pat.subn(lambda mm: mm.group(1) + mm.group(2) + ' data-brief-mark="' + mark + '"', html, count=1)
        stats["rows"] += cnt
    return html, stats


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: tx-lex-v131-author.py <lex.html> <data.json>")
    path, datapath = sys.argv[1], sys.argv[2]
    with open(path, encoding="utf-8") as f:
        html = f.read()
    with open(datapath, encoding="utf-8") as f:
        data = json.load(f)
    data = {str(k): v for k, v in data.items()}
    new, stats = process(html, data)
    if new != html:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(new)
    print("[OK] %s  規範核バッジ=%d  印付き原文行=%d" % (path.split("/")[-1], stats["nodes"], stats["rows"]))


if __name__ == "__main__":
    main()
