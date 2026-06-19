# -*- coding: utf-8 -*-
"""ARIADNE peek（「自分で答えてから開く」トグル）改善・冪等

ユーザー要望（2026-06-19）：
  ① 各手（.step）で peek が ○× の前にあると開き忘れる → **各手の末尾（○×の後）へ移動**。
     順序変更は実行時 JS（document 委譲で Lexia iframe でも動く）で行い、静的HTMLは安全に温存。
  ② peek が背景と同系色（lilac soft）で目立たない → **ゴールド（ヒント系）で目立たせる**。

canonical/ARIADNE.html ＋ 既存 ARIADNE 全ファイルに適用。マーカー KP-PEEK-MOVE で冪等。
使い方：python scripts/ariadne-peek-tweak.py [file ...]（無引数で canonical＋全ARIADNE）
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANON = ROOT / "canonical/ARIADNE.html"
ARIADNE_DIR = ROOT / "outputs/004_JX_EX/ARIADNE"
MARKER = "KP-PEEK-MOVE"

# ② 目立つ配色（ゴールド＝spec §5 ヒント・ゴール）。難易度別ベース（ローズ/ブルー/バイオレット）に
#    対して補色的に映える。
NEW_PEEK = ('details.peek{margin:13px 0 4px; border-radius:11px; background:#fffdf6; '
            'border:1.5px solid var(--gd-line); box-shadow:0 2px 8px rgba(200,160,40,.16)}')
NEW_SUMMARY = ('details.peek > summary{cursor:pointer; list-style:none; padding:11px 15px; '
               'font-family:var(--f-soft); font-weight:800; font-size:.9rem; color:#5a4400; '
               'display:flex; align-items:center; gap:8px; '
               'background:linear-gradient(135deg,#ffd45e,#f2af2b); border-radius:10px}')
NEW_HINT = ('details.peek > summary .hint{margin-left:auto; font-weight:600; '
            'font-size:.72rem; color:#7a5810}')

# ① peek を各手の末尾へ移す実行時 JS
#    ただし末尾化は「想起型（自分で答え/挙げ・立ち止まる石）」のみ。
#    「なぜ〜／理由」型（順序・前提のオリエン）は元位置（.do 直後＝冒頭）に残す。
MOVE_JS = (
    f'\n/* ==== {MARKER} ==== peek を末尾へ（想起型「自分で答え/挙げ・立ち止まる石」のみ。'
    '前提・理由「なぜ〜」型は元位置=冒頭のまま） */\n'
    '(function(){var RE=/自分で(答え|挙げ)|立ち止まる石/;function mv(){var s=document.querySelectorAll(".step");'
    'for(var i=0;i<s.length;i++){var p=s[i].querySelectorAll(":scope > details.peek");'
    'for(var j=0;j<p.length;j++){var sm=p[j].querySelector("summary");'
    'if(sm&&RE.test(sm.textContent||""))s[i].appendChild(p[j]);}}}'
    'if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mv);else mv();})();\n'
)
# 既注入ブロックの差し替え用（コメント開始〜IIFE終端 })();）
OLD_BLOCK_RE = re.compile(r'\n?/\* ==== ' + MARKER + r' ====.*?\}\)\(\);\n?', re.S)


def apply_to(path):
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        # 既適用 → 移動JSブロックだけ最新（想起型のみ末尾）へ差し替え（CSSは触らない）
        new = OLD_BLOCK_RE.sub(lambda m: MOVE_JS, html, count=1)
        if new != html:
            path.write_text(new, encoding="utf-8")
            return "updated(想起型のみ末尾)"
        return "skip(変化なし)"
    if 'details.peek' not in html or '</script>' not in html:
        return "skip(構造不一致)"
    # ② 配色（基底ルールを置換）
    html = re.sub(r'details\.peek\{[^}]*\}', NEW_PEEK, html, count=1)
    html = re.sub(r'details\.peek > summary\{[^}]*\}', NEW_SUMMARY, html, count=1)
    html = re.sub(r'details\.peek > summary \.hint\{[^}]*\}', NEW_HINT, html, count=1)
    # ① 末尾移動 JS（</script> 直前）
    html = html.replace('</script>', MOVE_JS + '</script>', 1)
    path.write_text(html, encoding="utf-8")
    return "applied"


def main():
    args = [pathlib.Path(a) for a in sys.argv[1:]]
    targets = args if args else ([CANON] + sorted(ARIADNE_DIR.glob("*/*_ARIADNE.html")))
    for p in targets:
        print(f"  {p.name}: {apply_to(p)}")


if __name__ == "__main__":
    main()
