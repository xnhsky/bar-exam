#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ariadne-ma-restyle.py — ARIADNE 模範答案を「問規当結カード（マイルドライナー）」へ誌面リスキン。

承認デザイン（案B-v2）の CSS を ARIADNE HTML の <style> 末尾へ冪等注入する。
- 問規当結を 5 系統マイルドライナー（AXIOM と同一 hex）で色分け（問=Blue/規=Yellow/当=Violet/結=Green）。
- 各段落カードに「食い出しバッジ（縁なしピル・カードより一段濃い -b 背景）」＋一行ごとの点線ルール。
- 事実=ピンクマーカー／評価語=橙マーカー。
※ CSS のみ注入（本文不変）。各 <p> への役割クラス（r-issue/r-norm/r-apply/r-concl）と
   .fact/.eval/.rule スパンの付与は別途（ファイルごとの内容判断＝LLM）で行う。CSS だけでは
   既存の役割未タグ段落は従来表示のまま（無害）。

使い方:  python scripts/ariadne-ma-restyle.py <file.html> [<file.html> ...]
         python scripts/ariadne-ma-restyle.py --all       # canonical + outputs/ux/000_ARIADNE 全件
冪等（MARK..ENDMARK を毎回置換）。
"""
import sys, os, re, glob

MARK = "/* === MA-ROLE-RESTYLE (模範答案 問規当結カード・2026-06-22) === */"
ENDMARK = "/* === /MA-ROLE-RESTYLE === */"

BLOCK = MARK + r"""
:root{
  --ml-yellow:#FCF3C5;--ml-yellow-b:#EAD879;--ml-yellow-d:#7A6818;--ml-yellow-m:#9C8526;
  --ml-green:#E7F4D9;--ml-green-b:#BFE09C;--ml-green-d:#4E7536;--ml-green-m:#5E8C44;
  --ml-blue:#DFEFF7;--ml-blue-b:#A8D6E8;--ml-blue-d:#2F6A8C;--ml-blue-m:#3F82A6;
  --ml-violet:#EDE6F6;--ml-violet-b:#C7B4E2;--ml-violet-d:#6A4D86;--ml-violet-m:#7E5F9C;
  --ml-pink:#FBE5EE;--ml-pink-b:#F3B0CA;--ml-pink-d:#A84E74;--ml-pink-m:#BC6189;
  --ml-orange:#FCEBD3;--ml-orange-b:#F6CB97;--ml-orange-d:#B06D28;--ml-orange-m:#C17F38;
}
.model-answer{font-family:var(--f-disp);font-size:.97rem;color:#2b2330}
.model-answer .ma-h{font-family:var(--f-disp);font-weight:800;color:#fff;margin:1.5em 0 .7em;padding:6px 14px;
  background:linear-gradient(135deg,var(--a-head),var(--a-foot));border-radius:8px;text-indent:0;display:inline-block;letter-spacing:.05em;font-size:.97rem}
.model-answer .ma-h:first-child{margin-top:.2em}
.model-answer u{text-decoration-color:var(--shu-line);text-decoration-thickness:2px;text-underline-offset:3px}
/* 役割カード共通：問規当結カード＋食い出しバッジ＋一行点線 */
.model-answer p.role{
  --lh:2.15em; position:relative; margin:22px 0; padding:1.5em 15px .6em 18px; line-height:var(--lh);
  text-indent:1em; background:var(--c); border:1px solid var(--cb); border-left:5px solid var(--cm);
  border-radius:11px; box-shadow:inset 0 1px 0 rgba(255,255,255,.55),0 2px 7px rgba(80,60,80,.07);
}
.model-answer p.role::before{
  content:var(--lbl); position:absolute; top:-12px; left:13px; padding:4px 13px 3px;
  font-family:var(--f-soft); font-weight:800; font-size:.68rem; letter-spacing:.1em; color:var(--cd);
  background:var(--cb); border:none; border-radius:9px; box-shadow:0 2px 6px rgba(80,60,80,.13); text-indent:0;
}
.model-answer p.role::after{
  content:""; position:absolute; left:18px; right:13px; top:1.5em; bottom:.5em; pointer-events:none; opacity:.6;
  background:var(--cd);
  -webkit-mask:
    repeating-linear-gradient(to bottom, transparent 0, transparent calc(var(--lh) - 1.1px), #000 calc(var(--lh) - 1.1px), #000 var(--lh)),
    repeating-linear-gradient(to right, #000 0 1.5px, transparent 1.5px 7px);
  -webkit-mask-composite:source-in;
  mask:
    repeating-linear-gradient(to bottom, transparent 0, transparent calc(var(--lh) - 1.1px), #000 calc(var(--lh) - 1.1px), #000 var(--lh)),
    repeating-linear-gradient(to right, #000 0 1.5px, transparent 1.5px 7px);
  mask-composite:intersect;
}
.model-answer p.role > b:first-child{color:var(--cd); font-weight:800}
.r-issue{--c:var(--ml-blue);  --cb:var(--ml-blue-b);  --cm:var(--ml-blue-m);  --cd:var(--ml-blue-d);  --lbl:"❓ 問題提起"}
.r-norm {--c:var(--ml-yellow);--cb:var(--ml-yellow-b);--cm:var(--ml-yellow-m);--cd:var(--ml-yellow-d);--lbl:"🔑 規範"}
.r-apply{--c:var(--ml-violet);--cb:var(--ml-violet-b);--cm:var(--ml-violet-m);--cd:var(--ml-violet-d);--lbl:"✍ あてはめ"}
.r-concl{--c:var(--ml-green); --cb:var(--ml-green-b); --cm:var(--ml-green-m); --cd:var(--ml-green-d); --lbl:"⮕ 結論"}
.model-answer .r-norm b.rule{background:linear-gradient(transparent 56%,rgba(234,216,121,.75) 56%);font-weight:800;color:#5c4e10}
.model-answer .fact{background:linear-gradient(transparent 56%,rgba(243,176,202,.7) 56%);font-weight:700;color:#9a3f63}
.model-answer .eval{background:linear-gradient(transparent 56%,rgba(246,203,151,.72) 56%);font-weight:700;color:#7c4a16}
""" + ENDMARK


def restyle(path):
    html = open(path, encoding='utf-8', newline='').read()
    if MARK in html and ENDMARK in html:
        new = re.sub(re.escape(MARK) + r'.*?' + re.escape(ENDMARK), lambda m: BLOCK, html, count=1, flags=re.S)
        status = 'updated'
    else:
        idx = html.rfind('</style>')
        if idx == -1:
            print(f"[SKIP] <style> 不在: {path}"); return False
        new = html[:idx] + BLOCK + '\n' + html[idx:]
        status = 'injected'
    if new != html:
        open(path, 'w', encoding='utf-8', newline='').write(new)
    print(f"[{status}] {path}")
    return True


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(2)
    if args[0] == '--all':
        files = ['canonical/ARIADNE.html'] + sorted(glob.glob('outputs/ux/000_ARIADNE/**/*_ARIADNE.html', recursive=True))
    else:
        files = args
    n = 0
    for f in files:
        if os.path.isfile(f) and restyle(f):
            n += 1
    print(f"\n=== MA-restyle 完了: {n} ファイル ===")


if __name__ == '__main__':
    main()
