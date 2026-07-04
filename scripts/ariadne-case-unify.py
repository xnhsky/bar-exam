#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""旧型(h5 kd-label)の判例カードを、百選型(hy-sec)と同じ役割別カラー箱＋食み出しタブへ統一。

構成は③(旧型)のまま＝分析節（事案/審級経過/判旨キーワード強調/先例/射程/学説評価/答案）を保持し、
見た目だけ④の役割別カラー箱＋食み出しラベルタブ＋本文1字下げに統一する（非破壊）。
各 <h5 class="kd-label..">LABEL</h5> ＋直後の内容を <div class="cx-sec cr-{role}"> でくくり、
LABEL を食み出しタブ .cx-lab に、内容を .cx-body に入れる。冒頭の裁判所/判決日/出典は「事件情報」箱に。
百選型(hy-sec)カードは対象外（既に箱）。CSS は marker ブロックを <style> 末尾へ注入（冪等）。

usage: python scripts/ariadne-case-unify.py [--apply] [files...]
"""
import re, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "/* === ARIADNE-CASE-UNIFY v1 (auto) BEGIN === */"
END = "/* === ARIADNE-CASE-UNIFY v1 (auto) END === */"
ZMARU = '"Zen Maru Gothic","Hiragino Maru Gothic ProN","Yu Gothic Medium",sans-serif'

CSS = f"""{BEGIN}
/* 旧型case-cardの節を④役割箱に統一（③構成＋④カラー箱＋食み出しタブ＋本文1字下げ）*/
.basis-card.case-card .basis-card-body .cx-sec{{position:relative; margin:22px 0 13px; padding:16px 17px 13px; background:var(--hp-bg,#eef0f2); border:1px solid var(--hp-line,#d5dae0); border-left:4px solid var(--hp,#5b6470); border-radius:10px; box-shadow:0 2px 7px rgba(46,73,83,.07)}}
.basis-card.case-card .basis-card-body .cx-sec:first-child{{margin-top:9px}}
.basis-card.case-card .basis-card-body .cx-sec > .cx-lab{{position:absolute; top:-12px; left:14px; display:inline-block; background:var(--hp,#5b6470); color:#fff; font-family:{ZMARU}; font-size:.73em; font-weight:800; padding:3px 12px 4px; border-radius:7px; letter-spacing:.05em; text-indent:0; box-shadow:0 2px 6px rgba(46,73,83,.22); max-width:calc(100% - 28px); white-space:nowrap; overflow:hidden; text-overflow:ellipsis}}
.basis-card.case-card .basis-card-body .cx-sec > .cx-body{{text-indent:0}}
.basis-card.case-card .basis-card-body .cx-sec > .cx-body > p{{margin:0 0 .6em; text-indent:1em; line-height:1.95}}
.basis-card.case-card .basis-card-body .cx-sec > .cx-body > p:last-child{{margin-bottom:0}}
.basis-card.case-card .basis-card-body .cx-sec.cx-meta > .cx-body > p{{text-indent:0; margin:.15em 0}}
.basis-card.case-card .basis-card-body .cx-sec > .cx-body > .judgment-text{{font-family:var(--f-disp); font-weight:700; text-indent:1em !important}}
.basis-card.case-card .basis-card-body .cx-sec > .cx-body table{{margin:6px 0 3px}}
.basis-card.case-card .basis-card-body .cr-jouhou{{--hp:#5b6470;--hp-bg:#eef0f2;--hp-line:#d5dae0}}
.basis-card.case-card .basis-card-body .cr-jian{{--hp:#3f6ea5;--hp-bg:#eef3fa;--hp-line:#cdddef}}
.basis-card.case-card .basis-card-body .cr-hanshi{{--hp:#c1566a;--hp-bg:#fdf1f3;--hp-line:#f2ccd4}}
.basis-card.case-card .basis-card-body .cr-kaisetsu{{--hp:#4d8a5c;--hp-bg:#eef6ef;--hp-line:#cfe6d3}}
.basis-card.case-card .basis-card-body .cr-shatei{{--hp:#8b6a9a;--hp-bg:#f4eff7;--hp-line:#ddd0e5}}
.basis-card.case-card .basis-card-body .cr-honmon{{--hp:#4E8597;--hp-bg:#eaf4f4;--hp-line:#c6e0e0}}
{END}"""

def role_of(label):
    l = label
    if l.startswith('判旨') or l.startswith('決定要旨') or l.startswith('判決要旨') or l.startswith('規範'):
        return 'cr-hanshi'
    if l.startswith('事案') or l.startswith('事実'):
        return 'cr-jian'
    if '射程' in l:
        return 'cr-shatei'
    if '答案' in l or '本問' in l:
        return 'cr-honmon'
    if (l.startswith('解説') or '学説' in l or '調査官' in l or l.startswith('理由')
            or '意義' in l or '先例' in l or '影響' in l or '評価' in l):
        return 'cr-kaisetsu'
    return 'cr-jouhou'  # 審級経過/補足/体系/出典/その他

H5 = re.compile(r'<h5 class="kd-label[^"]*">(.*?)</h5>', re.S)

def box_body(inner):
    parts = H5.split(inner)  # [meta, lab1, cont1, lab2, cont2, ...]
    out = []
    meta = parts[0].strip()
    if meta:
        out.append(f'<div class="cx-sec cr-jouhou cx-meta"><span class="cx-lab">事件情報</span><div class="cx-body">{meta}</div></div>')
    i = 1
    while i + 1 <= len(parts) - 1:
        lab_html = parts[i]
        cont = parts[i + 1].strip()
        label_txt = re.sub(r'<[^>]+>', '', lab_html).strip()
        out.append(f'<div class="cx-sec {role_of(label_txt)}"><span class="cx-lab">{lab_html}</span><div class="cx-body">{cont}</div></div>')
        i += 2
    return '\n'.join(out)

CARD = re.compile(r'(<div class="basis-card case-card"[^>]*>.*?<div class="card-return">.*?</div></div>)', re.S)

def transform(html):
    cnt = 0
    def rep(m):
        nonlocal cnt
        card = m.group(1)
        if 'hy-sec' in card or 'cx-sec' in card or '<h5 class="kd-label' not in card:
            return card  # 百選型/変換済/h5なし は対象外
        bo = card.find('<div class="basis-card-body">')
        if bo < 0:
            return card
        bo_end = bo + len('<div class="basis-card-body">')
        cr = card.find('<div class="card-return">', bo_end)
        if cr < 0:
            return card
        inner = card[bo_end:cr]
        boxed = box_body(inner)
        cnt += boxed.count('cx-sec ')
        return card[:bo_end] + '\n' + boxed + '\n' + card[cr:]
    return CARD.sub(rep, html), cnt

def inject_css(html):
    if BEGIN in html and END in html:
        return re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: CSS, html, flags=re.S)
    i = html.rfind("</style>")
    return html if i < 0 else html[:i] + CSS + "\n" + html[i:]

def process(path, apply):
    raw = Path(path).read_bytes().decode("utf-8")
    boxed, nsec = transform(raw)
    new = inject_css(boxed)
    changed = new != raw
    if changed and apply:
        Path(path).write_bytes(new.encode("utf-8"))
    return changed, nsec

def main():
    apply = "--apply" in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not files:
        files = [str(ROOT / "canonical/ARIADNE.html")]
        files += sorted(glob.glob(str(ROOT / "outputs/ux/001_ARIADNE/**/*_ARIADNE.html"), recursive=True))
    ch = 0
    for f in files:
        if not Path(f).exists():
            continue
        c, ns = process(f, apply)
        ch += 1 if c else 0
        if c:
            print(f"  {'[WROTE]' if apply else '[DIFF]'} {Path(f).name}  {ns} cx-sec")
    print(f"\n{ch} files {'updated' if apply else 'would change'} ({'APPLY' if apply else 'DRY-RUN'})")

if __name__ == "__main__":
    main()
