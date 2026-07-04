#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""百選型 hy-sec カードの節を cx-sec 形式へ変換し、全判例カードの markup を1本化。

hy-sec: <p class="hanging hy-sec r-*"><strong>【label】</strong><span class="hang-body">content</span></p>
   → cx: <div class="cx-sec cr-*"><span class="cx-lab">label</span><div class="cx-body"><p>content</p></div></div>
判旨の judgment-text は <p class="judgment-text"> にする。役割 r-*→cr-*（r-hyakusen→cr-jouhou）。
これで③(旧cx統一)と④(百選hy)が同一 markup になり見た目が完全一致。内容不変・冪等・LF保持。
※Lexia 側は cx-sec を構造抽出できるよう別途更新が必要（このスクリプトは ARIADNE のみ）。

usage: python scripts/ariadne-hy-to-cx.py [--apply] [files...]
"""
import re, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RMAP = {"r-jouhou": "cr-jouhou", "r-jian": "cr-jian", "r-hanshi": "cr-hanshi",
        "r-kaisetsu": "cr-kaisetsu", "r-shatei": "cr-shatei",
        "r-hyakusen": "cr-jouhou", "r-honmon": "cr-honmon"}

HYSEC = re.compile(
    r'<p class="hanging hy-sec (r-[a-z]+)"><strong>【([^】]+)】</strong><span class="([^"]*hang-body[^"]*)">(.*?)</span></p>',
    re.S)

def conv(m):
    role, label, spancls, content = m.group(1), m.group(2), m.group(3), m.group(4).strip()
    cr = RMAP.get(role, "cr-jouhou")
    if "judgment-text" in spancls:            # hang-body 自体が判旨
        body = '<p class="judgment-text">' + content + "</p>"
    else:
        jt = re.match(r'^<span class="judgment-text">(.*?)</span>$', content, re.S)
        body = ('<p class="judgment-text">' + jt.group(1).strip() + "</p>") if jt else ("<p>" + content + "</p>")
    return f'<div class="cx-sec {cr}"><span class="cx-lab">{label}</span><div class="cx-body">{body}</div></div>'

def process(path, apply):
    raw = Path(path).read_bytes().decode("utf-8")
    new, n = HYSEC.subn(conv, raw)
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
            print(f"  {'[WROTE]' if apply else '[DIFF]'} {Path(f).name}  {n}節変換")
    print(f"\n{tot} 節を hy-sec→cx-sec 変換 ({'APPLY' if apply else 'DRY-RUN'})")

if __name__ == "__main__":
    main()
