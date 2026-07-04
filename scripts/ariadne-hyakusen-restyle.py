#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ARIADNE 判例百選プロファイル＆条文判例カードの重厚化リスタイル（冪等・本文不変・LF保持）。

STEP7以降の deep-dive（判例 完全プロファイル／条文 完全プロファイル）の質感を上げる：
- 判例百選プロファイル：役割別カラー＋食み出しラベルタブ＋本文1字下げ。
  各 <p class="hanging"><strong>【label】</strong> に共有クラス hy-sec ＋役割クラス r-* を付与。
- 条文判例カード：影・ヘッダ・条文ブロックの食み出しラベルで重厚感。
CSS は marker で括った1ブロックを <style> 末尾に注入（既存なら置換＝冪等）。

usage: python scripts/ariadne-hyakusen-restyle.py [--apply] [files...]
  files 省略時は canonical/ARIADNE.html ＋ outputs/ux/001_ARIADNE/**/*_ARIADNE.html
"""
import re, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "/* === HYAKUSEN-PROFILE-RESTYLE v1 (auto) BEGIN === */"
END = "/* === HYAKUSEN-PROFILE-RESTYLE v1 (auto) END === */"

# 【label】→役割クラス
ROLE = {
    "事件情報": "r-jouhou", "事案": "r-jian", "判旨": "r-hanshi",
    "解説": "r-kaisetsu", "射程": "r-shatei", "百選": "r-hyakusen",
    "本問での使い方": "r-honmon",
}
ZMARU = '"Zen Maru Gothic","Hiragino Maru Gothic ProN","Yu Gothic Medium",sans-serif'

CSS = f"""{BEGIN}
/* 判例百選プロファイル＝役割別カラー＋食み出しラベルタブ＋本文1字下げ（重厚化）*/
.basis-card.case-card .basis-card-body p.hy-sec{{
  position:relative; text-indent:0; margin:22px 0 13px; padding:16px 17px 13px;
  background:var(--hp-bg); border:1px solid var(--hp-line); border-left:4px solid var(--hp);
  border-radius:10px; box-shadow:0 2px 7px rgba(46,73,83,.07);
}}
.basis-card.case-card .basis-card-body p.hy-sec:first-of-type{{margin-top:9px}}
.basis-card.case-card .basis-card-body p.hy-sec > strong:first-child{{
  position:absolute; top:-12px; left:14px; display:inline-block;
  background:var(--hp); color:#fff; border:none; font-family:{ZMARU};
  font-size:.73em; font-weight:800; padding:3px 12px 4px; border-radius:7px;
  letter-spacing:.07em; text-indent:.07em !important; vertical-align:baseline;
  box-shadow:0 2px 6px rgba(46,73,83,.22);
}}
.basis-card.case-card .basis-card-body p.hy-sec > .hang-body{{display:block; text-indent:1em}}
.basis-card.case-card .basis-card-body p.r-jouhou{{--hp:#5b6470;--hp-bg:#eef0f2;--hp-line:#d5dae0}}
.basis-card.case-card .basis-card-body p.r-jian{{--hp:#3f6ea5;--hp-bg:#eef3fa;--hp-line:#cdddef}}
.basis-card.case-card .basis-card-body p.r-hanshi{{--hp:#c1566a;--hp-bg:#fdf1f3;--hp-line:#f2ccd4}}
.basis-card.case-card .basis-card-body p.r-kaisetsu{{--hp:#4d8a5c;--hp-bg:#eef6ef;--hp-line:#cfe6d3}}
.basis-card.case-card .basis-card-body p.r-shatei{{--hp:#8b6a9a;--hp-bg:#f4eff7;--hp-line:#ddd0e5}}
.basis-card.case-card .basis-card-body p.r-hyakusen{{--hp:#a4762a;--hp-bg:#faf4e6;--hp-line:#ecddb9}}
.basis-card.case-card .basis-card-body p.r-honmon{{--hp:#4E8597;--hp-bg:#eaf4f4;--hp-line:#c6e0e0}}
.basis-card.case-card .basis-card-body p.r-hanshi > .hang-body .judgment-text{{color:#43242c}}
.basis-card.case-card .basis-card-body p.r-hyakusen{{padding:11px 17px 9px}}
.basis-card.case-card .basis-card-body p.r-hyakusen > .hang-body{{display:inline; text-indent:0; font-family:{ZMARU}; font-weight:700}}
/* 条文判例カード＝影・ヘッダ・条文/判旨ラベルで重厚感 */
.athena-graft .basis-card{{box-shadow:0 3px 12px rgba(46,73,83,.11)}}
.athena-graft .basis-card.statute-card .basis-card-header{{background:linear-gradient(180deg,#eef6f6,#dfeeed)}}
.athena-graft .basis-card.case-card .basis-card-header{{background:linear-gradient(180deg,#fdc9c9,#f7bdbd)}}
.athena-graft blockquote.statute{{position:relative; margin-top:22px; padding-top:19px; box-shadow:0 2px 6px rgba(46,73,83,.06)}}
.athena-graft blockquote.statute::before{{content:"\\1F4DC 条文"; position:absolute; top:-11px; left:14px; font-family:{ZMARU}; font-size:.69rem; font-weight:800; letter-spacing:.06em; text-indent:.06em; color:#fff; background:#6b7280; padding:3px 11px; border-radius:6px; box-shadow:0 2px 5px rgba(0,0,0,.16)}}
.athena-graft blockquote.case{{box-shadow:0 2px 7px rgba(215,138,138,.14)}}
{END}"""

def add_roles(html):
    def rep(m):
        label = m.group(2)
        role = ROLE.get(label)
        if not role:
            return m.group(0)
        return f'<p class="hanging hy-sec {role}"><strong>【{label}】</strong>'
    # class="hanging" 丁度のものだけ（既に hy-sec 付きは触らない＝冪等）
    return re.sub(r'<p class="hanging"(><strong>【([^】]+)】</strong>)',
                  lambda m: rep(m) if ROLE.get(m.group(2)) else m.group(0),
                  html)

def inject_css(html):
    block = CSS
    if BEGIN in html and END in html:
        return re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: block, html, flags=re.S)
    i = html.rfind("</style>")
    if i < 0:
        return html
    return html[:i] + block + "\n" + html[i:]

def process(path, apply):
    raw = Path(path).read_bytes().decode("utf-8")
    new = inject_css(add_roles(raw))
    changed = new != raw
    nrole = new.count("hy-sec") - raw.count("hy-sec")
    if changed and apply:
        Path(path).write_bytes(new.encode("utf-8"))
    return changed, nrole

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
        c, nr = process(f, apply)
        ch += 1 if c else 0
        if c:
            print(f"  {'[WROTE]' if apply else '[DIFF]'} {Path(f).name}  +{nr} hy-sec")
    print(f"\n{ch} files {'updated' if apply else 'would change'} ({'APPLY' if apply else 'DRY-RUN'})")

if __name__ == "__main__":
    main()
