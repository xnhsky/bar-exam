#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""変換漏れの旧様式(h5)判例カードを cx-sec 統一形式へ変換（card-return 無しにも対応）。

ariadne-case-unify は card-return 前提で、card-return を持たない h5 カードを取りこぼした。
本スクリプトは div 深さでカード境界を取り、h5 節を百選スキーム(事件情報/事案/判旨/解説/射程/百選/
本問での使い方)の cx-sec へ変換＋統合する。cx-sec/hy-sec 既済カードは対象外。冪等・内容不変・LF保持。

usage: python scripts/ariadne-convert-residual.py [--apply] [files...]
"""
import re, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER = ["事件情報", "事案", "判旨", "解説", "射程", "百選", "本問での使い方"]
ROLE = {"事件情報": "cr-jouhou", "事案": "cr-jian", "判旨": "cr-hanshi",
        "解説": "cr-kaisetsu", "射程": "cr-shatei", "百選": "cr-jouhou",
        "本問での使い方": "cr-honmon"}

def target_of(label):
    l = label
    if "事件情報" in l or "審級" in l or l.startswith("事実"):
        return "事件情報"
    if "本問" in l and "射程" in l:
        return "本問での使い方"
    if l.startswith("判旨") or l.startswith("規範") or l.startswith("決定要旨") or l.startswith("判決要旨") or "事案・判旨" in l:
        return "判旨"
    if l.startswith("事案"):
        return "事案"
    if "答案" in l or "本問" in l:
        return "本問での使い方"
    if "射程" in l:
        return "射程"
    return "解説"

H5 = re.compile(r'<h5 class="kd-label[^"]*">(.*?)</h5>', re.S)

def find_close(html, start):
    depth, i = 1, start
    while depth > 0:
        nd = html.find("<div", i); nc = html.find("</div>", i)
        if nc < 0:
            return -1
        if 0 <= nd < nc:
            depth += 1; i = nd + 4
        else:
            depth -= 1
            if depth == 0:
                return nc
            i = nc + 6
    return -1

def convert_body(inner, hy):
    parts = H5.split(inner)
    buckets = {}
    meta = parts[0].strip()
    # meta（先頭のプレーン段落＝裁判所/判決日/出典 等）を 事件情報 へ
    if meta and re.search(r'<(p|table|blockquote)', meta):
        buckets.setdefault("事件情報", []).append(meta)
    i = 1
    while i + 1 <= len(parts) - 1:
        lab = re.sub(r"<[^>]+>", "", parts[i]).strip()
        cont = parts[i + 1].strip()
        buckets.setdefault(target_of(lab), []).append(cont)
        i += 2
    if hy and "百選" not in buckets:
        buckets["百選"] = [f"<p>刑法百選{hy}（第8版）</p>"]
    out = []
    for tgt in ORDER:
        if tgt in buckets:
            out.append(f'<div class="cx-sec {ROLE[tgt]}"><span class="cx-lab">{tgt}</span><div class="cx-body">{chr(10).join(buckets[tgt])}</div></div>')
    return "\n".join(out)

def transform(html):
    n = 0
    out = []
    pos = 0
    for m in re.finditer(r'<div class="basis-card case-card"([^>]*)>', html):
        if m.start() < pos:
            continue
        attrs = m.group(1)
        cstart = m.end()
        cclose = find_close(html, cstart)
        if cclose < 0:
            continue
        card_inner = html[cstart:cclose]
        if "cx-sec" in card_inner or "hy-sec" in card_inner or '<h5 class="kd-label' not in card_inner:
            continue  # 既済 or h5 無し
        bo = card_inner.find('<div class="basis-card-body">')
        if bo < 0:
            continue
        bo_end = bo + len('<div class="basis-card-body">')
        bclose = find_close(card_inner, bo_end)
        if bclose < 0:
            continue
        body_inner = card_inner[bo_end:bclose]
        hy_m = re.search(r'data-hyakusen="刑法百選([^"]+)"', attrs)
        new_body = convert_body(body_inner, hy_m.group(1) if hy_m else None)
        new_card_inner = card_inner[:bo_end] + "\n" + new_body + "\n" + card_inner[bclose:]
        out.append(html[pos:cstart]); out.append(new_card_inner)
        pos = cclose
        n += 1
    out.append(html[pos:])
    return "".join(out), n

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
            print(f"  {'[WROTE]' if apply else '[DIFF]'} {Path(f).name}  {n}カード")
    print(f"\n{tot} 旧様式カードを変換 ({'APPLY' if apply else 'DRY-RUN'})")

if __name__ == "__main__":
    main()
