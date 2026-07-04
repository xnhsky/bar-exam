#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""判例カード(cx-sec型)の節構成を判例百選スキームへ統一（内容・キーワード強調は保持）。

hy-sec型(百選)＝事件情報/事案/判旨/解説/射程/百選/本問での使い方 に節構成を揃える。
cx-sec型カードの各節を上記ターゲットへリラベル＆同一ターゲットは内容統合し、正規順に並べ替え。
百選案件(data-hyakusen)は【百選】番号節を付加。判旨は元のまま(=paraphrase＋キーワード強調を温存)。
射程・本問での使い方は独立節として温存(試験重要)。hy-sec型カードは対象外(既に統一済)。
本文・キーワード強調・table/blockquote 等は不変。冪等・LF保持。

usage: python scripts/ariadne-unify-case-structure.py [--apply] [files...]
"""
import re, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ターゲット節（正規順）＋役割クラス
ORDER = ["事件情報", "事案", "判旨", "解説", "射程", "百選", "本問での使い方"]
ROLE = {"事件情報": "cr-jouhou", "事案": "cr-jian", "判旨": "cr-hanshi",
        "解説": "cr-kaisetsu", "射程": "cr-shatei", "百選": "cr-jouhou",
        "本問での使い方": "cr-honmon"}

def target_of(label):
    l = label
    if "事件情報" in l or "審級" in l or l.startswith("事実"):
        return "事件情報"
    if "本問" in l and "射程" in l:
        return "本問での使い方"   # 本問への射程＝問題固有適用
    if l.startswith("判旨") or l.startswith("規範") or l.startswith("決定要旨") or l.startswith("判決要旨") or "事案・判旨" in l:
        return "判旨"
    if l.startswith("事案"):
        return "事案"
    if "答案" in l or "本問" in l:
        return "本問での使い方"
    if "射程" in l:
        return "射程"
    return "解説"   # 学説評価/意義/先例との関係/理由/影響/位置/その他 → 解説に統合

CXSEC = re.compile(r'<div class="cx-sec[^"]*">\s*<span class="cx-lab">(.*?)</span>\s*<div class="cx-body">(.*?)</div>\s*</div>', re.S)
CARD = re.compile(r'(<div class="basis-card case-card"([^>]*)>)(.*?)(<div class="card-return">.*?</div></div>)', re.S)

def unify_card(open_tag, attrs, body, tail):
    if "cx-sec" not in body or "hy-sec" in body:
        return open_tag + body + tail  # 対象外
    secs = CXSEC.findall(body)
    if not secs:
        return open_tag + body + tail
    # ターゲット別に内容を統合（順序維持）
    buckets = {}
    for lab_html, content in secs:
        lab = re.sub(r"<[^>]+>", "", lab_html).strip()
        tgt = target_of(lab)
        buckets.setdefault(tgt, []).append(content.strip())
    # 百選番号
    hy = re.search(r'data-hyakusen="刑法百選([^"]+)"', attrs)
    if hy and "百選" not in buckets:
        buckets["百選"] = [f'<p>刑法百選{hy.group(1)}（第8版）</p>']
    # 正規順に cx-sec を再生成
    out = []
    for tgt in ORDER:
        if tgt not in buckets:
            continue
        merged = "\n".join(buckets[tgt])
        out.append(f'<div class="cx-sec {ROLE[tgt]}"><span class="cx-lab">{tgt}</span><div class="cx-body">{merged}</div></div>')
    # 元の basis-card-body 開始タグを維持
    bo = body.find('<div class="basis-card-body">')
    if bo < 0:
        return open_tag + body + tail
    bo_end = bo + len('<div class="basis-card-body">')
    new_body = body[:bo_end] + "\n" + "\n".join(out) + "\n"
    return open_tag + new_body + tail

def transform(html):
    n = 0
    def rep(m):
        nonlocal n
        res = unify_card(m.group(1), m.group(2), m.group(3), m.group(4))
        if res != m.group(0):
            n += 1
        return res
    return CARD.sub(rep, html), n

def process(path, apply):
    raw = Path(path).read_bytes().decode("utf-8")
    new, n = transform(raw)
    changed = new != raw
    if changed and apply:
        Path(path).write_bytes(new.encode("utf-8"))
    return changed, n

def main():
    apply = "--apply" in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not files:
        files = sorted(glob.glob(str(ROOT / "outputs/ux/001_ARIADNE/**/*_ARIADNE.html"), recursive=True))
        files.append(str(ROOT / "canonical/ARIADNE.html"))
    tot = 0
    for f in files:
        if not Path(f).exists():
            continue
        c, n = process(f, apply)
        tot += n
        if c:
            print(f"  {'[WROTE]' if apply else '[DIFF]'} {Path(f).name}  {n}カード統一")
    print(f"\n{tot} カード統一 ({'APPLY' if apply else 'DRY-RUN'})")

if __name__ == "__main__":
    main()
