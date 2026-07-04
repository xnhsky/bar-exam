#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ARIADNE 深掘り層（条文/判例/学説＝athena-graft）の配色・意匠を TX_lex(刑TX420_lex) に合わせる。

構成（節・分析の詳しさ）は一切変えず、見た目だけ TX_lex のデザインへ：
- 条文カード=ブルー系淡カード／判例カード=ピンク系淡カード（サブトル border＋グラデ地）。
- 役割ラベルを「重い食み出し色箱」→「TX_lex のパステル薄チップ（インライン・左罫）」に。各節は薄チップ＋区切り線。
- ★★★ 重要度バッジ=violet。緑/紫マーカー・xref ピル=TX_lex。graft-h/blockquote も TX_lex 系。
CSS marker ブロックを <style> 末尾へ注入（冪等・本文不変・LF保持）。body 変換なし＝色/意匠のみ。

usage: python scripts/ariadne-txlex-theme.py [--apply] [files...]
"""
import re, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "/* === ARIADNE-TXLEX-THEME v1 (auto) BEGIN === */"
END = "/* === ARIADNE-TXLEX-THEME v1 (auto) END === */"

CSS = BEGIN + r"""
/* 条文/判例/学説カードを TX_lex(刑TX420_lex) の配色・意匠に合わせる（構成は維持・色/意匠のみ）*/
/* --- セクション見出し graft-h = BASIS ブルー系 --- */
.athena-graft .graft-h{color:#33507e; background:linear-gradient(90deg,rgba(91,118,173,.13),transparent); border-left:4px solid #5b76ad}
.athena-graft .graft-h.gh-case{color:#8a3f57; background:linear-gradient(90deg,rgba(156,75,103,.13),transparent); border-left-color:#c77e97}
/* --- 条文カード = ブルー系サブトル --- */
.athena-graft .basis-card.statute-card{background:linear-gradient(180deg,#fff,#f4f7fc); border:1px solid rgba(96,120,170,.4); border-left:4px solid #5b76ad; box-shadow:0 4px 11px -6px rgba(70,90,140,.36)}
.athena-graft .basis-card.statute-card .basis-card-header{background:linear-gradient(180deg,rgba(226,234,246,.75),rgba(226,234,246,0)); color:#274a73; border-bottom:1px solid rgba(96,120,170,.2)}
/* --- 判例カード = ピンク系サブトル --- */
.athena-graft .basis-card.case-card{background:linear-gradient(180deg,#fff,#fbf1f4); border:1px solid rgba(156,75,103,.42); border-left:4px solid #c77e97; box-shadow:0 4px 11px -6px rgba(140,80,100,.30)}
.athena-graft .basis-card.case-card .basis-card-header{background:linear-gradient(180deg,rgba(246,226,234,.75),rgba(246,226,234,0)); color:#8a3f57; border-bottom:1px solid rgba(156,75,103,.2)}
/* --- 重要度バッジ = violet --- */
.athena-graft .freq-badge,.athena-graft .freq-badge.freq-high{background:#8E6E9A; color:#fff; border:2px solid #2B1F30}
.athena-graft .freq-badge.freq-mid{background:#B79CC2; color:#463A50; border:none}
.athena-graft .freq-badge.freq-low{background:#E6DAE8; color:#463A50; border:none}
/* --- 節を TX_lex チップ意匠に：重い色箱を解除し薄チップ＋区切り線 --- */
.athena-graft .basis-card-body .cx-sec,
.athena-graft .basis-card-body p.hy-sec{background:none !important; border:none !important; box-shadow:none !important; border-radius:0 !important; margin:0 !important; padding:11px 3px 9px !important; border-top:1px dashed rgba(120,110,130,.24) !important}
.athena-graft .basis-card-body .cx-sec:first-child,
.athena-graft .basis-card-body p.hy-sec:first-of-type{border-top:none !important; padding-top:5px !important}
/* ラベル＝パステル薄チップ（食み出し解除・インライン化）*/
.athena-graft .basis-card-body .cx-sec > .cx-lab,
.athena-graft .basis-card-body p.hy-sec > strong:first-child{position:static !important; top:auto !important; left:auto !important; display:inline-block !important; margin:0 0 6px 0 !important; padding:2px 11px 3px !important; border-radius:4px !important; border:1px solid var(--cl-line,#D6C9DC) !important; border-left:3px solid var(--cl-bd,#8E6E9A) !important; background:var(--cl-bg,#EDE2EF) !important; color:var(--cl-fg,#4A3D54) !important; font-family:"Zen Kaku Gothic Antique","Yu Gothic","Hiragino Sans",sans-serif !important; font-size:.8em !important; font-weight:700 !important; letter-spacing:.05em !important; text-indent:.05em !important; box-shadow:none !important; max-width:none !important; white-space:normal !important}
.athena-graft .basis-card-body .cx-sec > .cx-body{display:block; text-indent:0}
.athena-graft .basis-card-body p.hy-sec > .hang-body{display:block; text-indent:1em}
.athena-graft .basis-card-body .cx-sec > .cx-body > p{text-indent:1em}
.athena-graft .basis-card-body .cx-sec > .cx-body > .judgment-text{text-indent:1em !important}
/* 役割 → TX_lex 6色パステルパレット（cx-* と hy r-* 双方）*/
.athena-graft .cr-jian,.athena-graft p.r-jian{--cl-bg:#e3f6fb;--cl-bd:#6fbdd0;--cl-fg:#1f5d70;--cl-line:#c4e8f0}
.athena-graft .cr-hanshi,.athena-graft p.r-hanshi{--cl-bg:#fde7ee;--cl-bd:#dd8ba6;--cl-fg:#9a3f5f;--cl-line:#f4cdda}
.athena-graft .cr-kaisetsu,.athena-graft p.r-kaisetsu{--cl-bg:#eef6d4;--cl-bd:#9bb85a;--cl-fg:#51631c;--cl-line:#dbe8b8}
.athena-graft .cr-shatei,.athena-graft p.r-shatei{--cl-bg:#f6ece4;--cl-bd:#cda890;--cl-fg:#7a5240;--cl-line:#e8d8cb}
.athena-graft .cr-honmon,.athena-graft p.r-honmon{--cl-bg:#fdeede;--cl-bd:#e0a575;--cl-fg:#8a4f24;--cl-line:#f5dcc2}
.athena-graft .cr-jouhou,.athena-graft p.r-jouhou,.athena-graft p.r-hyakusen{--cl-bg:#ece9fb;--cl-bd:#9b9ae6;--cl-fg:#494690;--cl-line:#dcd9f4}
/* 旧 h5 kd-label（doctrine/term カード等 未cx化）も TX_lex 役割色に */
.athena-graft h5.kd-label.r-youken{background:#e3f6fb;border-left-color:#6fbdd0;color:#1f5d70}
.athena-graft h5.kd-label.r-hogo{background:#eef6d4;border-left-color:#9bb85a;color:#51631c}
.athena-graft h5.kd-label.r-shushi{background:#ece9fb;border-left-color:#9b9ae6;color:#494690}
.athena-graft h5.kd-label.r-shatei{background:#f6ece4;border-left-color:#cda890;color:#7a5240}
.athena-graft h5.kd-label.r-ate{background:#fdeede;border-left-color:#e0a575;color:#8a4f24}
.athena-graft h5.kd-label.r-chui{background:#fde7e0;border-left-color:#ef9277;color:#9a4528}
/* マーカー = TX_lex（黄/緑/青の蛍光）*/
.athena-graft .hl-super{background:linear-gradient(transparent 55%,rgba(255,213,79,.55) 55%)}
.athena-graft .hl-high{background:linear-gradient(transparent 60%,rgba(174,213,129,.55) 60%)}
.athena-graft .hl-std{background:linear-gradient(transparent 70%,rgba(144,202,249,.50) 70%)}
/* 判旨内キーワード強調（strong）＝緑マーカー（スクショの緑）*/
.athena-graft .judgment-text strong,.athena-graft .cx-sec.cr-hanshi .cx-body strong{background:linear-gradient(transparent 58%,rgba(174,213,129,.6) 58%) !important; color:#2f4d1c; padding:0 1px}
/* xref ピル＝violet アクセント */
.athena-graft a.xref,.athena-graft a.xref.auto{color:#494690; background:rgba(142,110,154,.13); border-bottom:1.5px solid rgba(142,110,154,.5)}
.athena-graft a.xref:hover,.athena-graft a.xref.auto:hover{color:#fff; background:#8E6E9A}
/* --- 学説カード（doctrine-card）＝ラベンダー系（TX_lex violet accent）--- */
.athena-graft .graft-h.gh-doc{color:#494690; background:linear-gradient(90deg,rgba(155,154,230,.15),transparent); border-left-color:#9b9ae6}
.athena-graft .basis-card.doctrine-card{background:linear-gradient(180deg,#fff,#f5f4fc); border:1px solid rgba(139,138,210,.4); border-left:4px solid #9b9ae6; box-shadow:0 4px 11px -6px rgba(90,88,150,.3)}
.athena-graft .basis-card.doctrine-card .basis-card-header{background:linear-gradient(180deg,rgba(236,233,251,.78),rgba(236,233,251,0)); color:#494690; border-bottom:1px solid rgba(139,138,210,.2)}
.athena-graft .basis-card.doctrine-card table th{background:#ece9fb; color:#494690; border-color:rgba(139,138,210,.4)}
.athena-graft .basis-card.doctrine-card table td{border-color:rgba(139,138,210,.3)}
.athena-graft .basis-card.doctrine-card table tr:nth-child(even) td{background:#f7f6fd}
/* --- 学説対立 gakusetsu ＝ラベンダー枠／採用説=green（TX_lex hl-high 系）--- */
.athena-graft .gakusetsu .gk{background:linear-gradient(180deg,#fff,#f7f6fd); border:1px solid rgba(139,138,210,.35); border-left:4px solid #9b9ae6; border-radius:10px}
.athena-graft .gakusetsu .gk .gh{color:#494690}
.athena-graft .gakusetsu .gk.adopt{border-left-color:#9bb85a; background:#f4f8e8}
.athena-graft .gakusetsu .gk.adopt .gh{color:#51631c}
/* --- 用語カード（term-card）＝スレート系（深掘り層の統一）--- */
.athena-graft .basis-card.term-card{background:linear-gradient(180deg,#fff,#f6f7f9); border:1px solid rgba(120,128,145,.38); border-left:4px solid #8891a5}
.athena-graft .basis-card.term-card .basis-card-header{background:linear-gradient(180deg,rgba(233,236,241,.75),rgba(233,236,241,0)); color:#3f4655; border-bottom:1px solid rgba(120,128,145,.2)}
/* --- doctrine/term カード内の h5 節（cx化してない）も薄チップ寄りに（既存 kd-label 色は上書き済）--- */
/* blockquote statute/case を TX_lex 系に */
.athena-graft blockquote.statute{background:linear-gradient(180deg,#fff,#f4f7fc); border:1px solid rgba(96,120,170,.35); border-left:4px solid #5b76ad}
.athena-graft blockquote.statute::before{background:#5b76ad}
.athena-graft blockquote.case{background:#fff; border:1px solid rgba(156,75,103,.42); border-top:2px solid #c77e97}
.athena-graft blockquote.case::before{background:#9c4b67}
/* key-box = TX_lex ブルー基調（微調整）*/
.athena-graft .key-box{background:linear-gradient(180deg,#f3f6fc,#e8eef8); border:1px solid rgba(96,120,170,.35)}
.athena-graft .key-box::before{color:#33507e}
/* cx-sec 内 判旨は chip があるので blockquote.case の ⚖判旨 バッジは隠す（二重ラベル回避）*/
.athena-graft .cx-sec blockquote.case{margin-top:2px; padding-top:11px; border-top:1px solid rgba(156,75,103,.28)}
.athena-graft .cx-sec blockquote.case::before{display:none}
.athena-graft .cx-sec blockquote.case p{text-indent:1em}
/* 判旨内キーワード（strong）に緑マーカーが乗るよう色は継承（xref はピル）*/
.athena-graft .judgment-text strong a.xref,.athena-graft .judgment-text strong a.xref.auto{background:rgba(142,110,154,.16)}
/* ===== 重厚感・質感レイヤー（深い影＋内側ハイライト＋チップ立体＋本文1字下げ徹底）===== */
.athena-graft .basis-card{box-shadow:0 8px 19px -10px rgba(70,60,90,.42), inset 0 1px 0 rgba(255,255,255,.8) !important; border-radius:12px}
.athena-graft .basis-card.statute-card{box-shadow:0 8px 19px -10px rgba(70,90,140,.44), inset 0 1px 0 rgba(255,255,255,.85) !important}
.athena-graft .basis-card.case-card{box-shadow:0 8px 19px -10px rgba(140,80,100,.4), inset 0 1px 0 rgba(255,255,255,.85) !important}
.athena-graft .basis-card.doctrine-card{box-shadow:0 8px 19px -10px rgba(90,88,150,.4), inset 0 1px 0 rgba(255,255,255,.85) !important}
.athena-graft .basis-card-header{text-shadow:0 1px 0 rgba(255,255,255,.55)}
/* 役割チップに立体（drop＋内側ハイライト・TXLEXチップ規則より高詳細度で上書き）*/
.athena-graft .basis-card-body .cx-sec > .cx-lab,.athena-graft .basis-card-body p.hy-sec > strong:first-child,.athena-graft h5.kd-label{box-shadow:0 2px 4px -1px rgba(70,60,90,.22), inset 0 1px 0 rgba(255,255,255,.6) !important}
/* 学説テーブルに質感（th グラデ＋罫線立体）*/
.athena-graft .basis-card.doctrine-card table th{background-image:linear-gradient(180deg,rgba(255,255,255,.5),rgba(255,255,255,0)); box-shadow:inset 0 1px 0 rgba(255,255,255,.6)}
/* graft-h をリッチな見出しに */
.athena-graft .graft-h{border-radius:0 9px 9px 0; box-shadow:0 3px 9px -6px rgba(70,60,90,.45); padding:9px 15px; font-size:1rem; text-shadow:0 1px 0 rgba(255,255,255,.5)}
/* 本文書き出し1字下げ徹底（ラベル/メタ/表は除く）*/
.athena-graft .basis-card-body .cx-sec > .cx-body > p,
.athena-graft .basis-card-body .cx-sec > .cx-body > .judgment-text{text-indent:1em !important}
.athena-graft .basis-card-body .cx-sec.cx-meta > .cx-body > p{text-indent:0 !important}
.athena-graft .basis-card-body p.hy-sec > .hang-body{text-indent:1em !important}
.athena-graft .basis-card-body p.r-hyakusen > .hang-body{text-indent:0 !important}
.athena-graft .basis-card-body .cx-sec blockquote.case p,.athena-graft blockquote.case p{text-indent:1em !important}
.athena-graft .basis-card.statute-card .basis-card-body > p:not(.hanging){text-indent:1em}
/* 条文プロファイル以降の取りこぼし：statute内のプレーン条文段落・issueカードのnote も1字下げ */
.athena-graft blockquote.statute > p:not(.stat-para){text-indent:1em !important}
.athena-graft .card > p.note,.athena-graft .card > .note > p{text-indent:1em}
.athena-graft .basis-card-body .cx-sec > .cx-body > blockquote.statute > p:not(.stat-para){text-indent:1em !important}
""" + END

def inject_css(html):
    if BEGIN in html and END in html:
        return re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: CSS, html, flags=re.S)
    i = html.rfind("</style>")
    return html if i < 0 else html[:i] + CSS + "\n" + html[i:]

def process(path, apply):
    raw = Path(path).read_bytes().decode("utf-8")
    new = inject_css(raw)
    changed = new != raw
    if changed and apply:
        Path(path).write_bytes(new.encode("utf-8"))
    return changed

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
        if process(f, apply):
            ch += 1
            print(f"  {'[WROTE]' if apply else '[DIFF]'} {Path(f).name}")
    print(f"\n{ch} files {'updated' if apply else 'would change'} ({'APPLY' if apply else 'DRY-RUN'})")

if __name__ == "__main__":
    main()
