#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ariadne-athena-deep-backfill.py — 既存 ARIADNE への「アテナで詳しく」ジャンプ＋TX書式CSS 後追い（spec §11-3・冪等）

既存 outputs/ux/000_ARIADNE/**/*_ARIADNE.html に対して、機械的に注入する：
  ① TX 参考条文判例書式の CSS ブロック（canonical/ARIADNE.html から抽出＝ドリフト防止）
  ② 深掘り層末尾の「アテナで詳しく」ボタン（.go-athena・postMessage lexia:navigate / 単体は相対リンク）
  ③ ボタンを動かす gotoAthena JS（click 委譲＋keydown）

※ 深掘り層の「中身」を TX 書式カード（A）へアテナ級化するのは問題固有＝機械生成不可。
   それは再生成（バッチ／/new-ariadne）で揃える。本 backfill は B（ジャンプ）を全 ARIADNE に先行配備する保険。

使い方:
  python scripts/ariadne-athena-deep-backfill.py                 # 全科目・dry-run（差分の要約のみ）
  python scripts/ariadne-athena-deep-backfill.py --subject 刑     # 科目フォルダで絞る（接頭辞 or 00N）
  python scripts/ariadne-athena-deep-backfill.py --apply          # 実際に書き込む
"""
import argparse, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARIADNE_DIR = ROOT / "outputs" / "ux" / "000_ARIADNE"
CANON = ROOT / "canonical" / "ARIADNE.html"

XREF_ANCHOR = ".xref{color:var(--a-head); font-weight:700}"
QUIZBTN_LINE = "    var qb = t.closest('.quiz-btn'); if(qb){ onQuizBtn(qb); return; }"
CLICK_OPEN = "  document.addEventListener('click', function(e){\n    var t = e.target; if(!t || !t.closest) return;\n" + QUIZBTN_LINE
CLICK_TAIL = ("    if(a){ var id = decodeURIComponent((a.getAttribute('href')||'').slice(1)); "
              "if(id){ var tgt = document.getElementById(id); if(tgt) openAncestors(tgt); } }\n  });")

GOTO_FN = (
"  function gotoAthena(ga){\n"
"    var code = ga.getAttribute('data-athena-code') || '';\n"
"    var href = ga.getAttribute('data-athena-href') || '';\n"
"    var inFrame = false;\n"
"    try { inFrame = (window.parent && window.parent !== window); } catch(_e){ inFrame = true; }\n"
"    if(inFrame && code){\n"
"      try { window.parent.postMessage({ source:'lexia-quiz', type:'lexia:navigate', targetCode:code }, '*'); return; } catch(_e){}\n"
"    }\n"
"    if(href){ try { window.open(href, '_blank'); } catch(_e){ try { location.href = href; } catch(_e2){} } }\n"
"  }\n")
CLICK_BRANCH = "    var ga = t.closest('.go-athena'); if(ga){ e.preventDefault(); gotoAthena(ga); return; }\n"
KEYDOWN = (
"\n  document.addEventListener('keydown', function(e){\n"
"    if(e.key !== 'Enter' && e.key !== ' ' && e.key !== 'Spacebar') return;\n"
"    var t = e.target; if(!t || !t.closest) return;\n"
"    var ga = t.closest('.go-athena'); if(ga){ e.preventDefault(); gotoAthena(ga); }\n"
"  });")


def extract_css_block():
    """canonical/ARIADNE.html から ATHENA-DEEP CSS ブロックを抽出（.foot 直前まで）。"""
    html = CANON.read_text(encoding="utf-8")
    m = re.search(r"/\* ==== ATHENA-DEEP.*?(?=\n\.foot\{)", html, re.S)
    if not m:
        sys.exit("[FATAL] canonical から ATHENA-DEEP CSS ブロックを抽出できない")
    return m.group(0).rstrip("\n")


def button_html(code, subjdir):
    return (
f'      <a class="go-athena" role="button" tabindex="0" data-athena-code="{code}" '
f'data-athena-href="../../../001_JX/{subjdir}/{code}.html">\n'
'        <span class="ga-ic">📖</span>\n'
'        <span class="ga-tx">アテナ版で詳しく（百科事典）<span class="ga-sub">条文集・判例集・学説一覧・論証集・答案表現集・体系図のフル解説へ</span></span>\n'
f'        <span class="ga-cta">{code} ▶</span>\n'
'      </a>\n'
'      <div class="deep-note">ARIADNE は「次に何をするか」の解法ナビ＋周回。この深掘り層に本問の知識をアテナ級で収め、'
'さらに網羅的事典が要るときだけ上のボタンでアテナ版へ飛ぶ ── という二段構えで役割分担する。</div>')


def process(path, css_block, apply):
    html = path.read_text(encoding="utf-8")
    # 注入済み判定はボタン要素(data-athena-code)で見る（CSS の .go-athena 規則に釣られないため）
    if "data-athena-code" in html and "ATHENA-DEEP" in html:
        return "skip(済)"
    code = path.name.replace("_ARIADNE.html", "")
    subjdir = path.parent.name
    changed = []

    # ① CSS 注入（.xref 行の直後）
    if "ATHENA-DEEP" not in html:
        if XREF_ANCHOR not in html:
            return "skip(.xref アンカー無)"
        html = html.replace(XREF_ANCHOR, XREF_ANCHOR + "\n\n" + css_block, 1)
        changed.append("css")

    # ② ボタン（既存 deep-note を [ボタン＋新note] へ置換）。CSS の .go-athena 規則に釣られないよう
    #    ボタン要素マーカー data-athena-code で判定する。
    if "data-athena-code" not in html:
        new_block = button_html(code, subjdir)
        n = 0
        html, n = re.subn(r'<div class="deep-note">.*?</div>', new_block, html, count=1, flags=re.S)
        if n == 0:
            # deep-note 不在時は deep-dive の閉じ </details> 直前に挿入
            html2, n2 = re.subn(r'(\n\s*</div>\s*\n\s*</details>)', "\n" + new_block + r"\1", html, count=1)
            if n2 == 0:
                return "skip(挿入点無)"
            html = html2
        changed.append("button")

    # ③ JS（gotoAthena 関数＋click 分岐＋keydown）
    if "gotoAthena" not in html:
        if CLICK_OPEN not in html:
            return "skip(click委譲アンカー無)"
        html = html.replace(CLICK_OPEN, GOTO_FN + CLICK_OPEN + "\n" + CLICK_BRANCH.rstrip("\n"), 1)
        if KEYDOWN.strip() not in html:
            html = html.replace(CLICK_TAIL, CLICK_TAIL + KEYDOWN, 1)
        changed.append("js")

    if not changed:
        return "noop"
    if apply:
        path.write_text(html, encoding="utf-8")
    return "+".join(changed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default=None, help="科目フォルダで絞る（接頭辞『刑』や『001』など）")
    ap.add_argument("--apply", action="store_true", help="実書き込み（既定 dry-run）")
    args = ap.parse_args()

    css_block = extract_css_block()
    files = sorted(ARIADNE_DIR.glob("*/*_ARIADNE.html"))
    if args.subject:
        s = args.subject
        files = [f for f in files if s in f.parent.name]
    if not files:
        sys.exit("対象ファイルなし")

    tally = {}
    for f in files:
        r = process(f, css_block, args.apply)
        tally[r] = tally.get(r, 0) + 1
        mark = "APPLIED" if (args.apply and r not in ("noop",) and not r.startswith("skip")) else "would" if not args.apply else "·"
        print(f"  [{mark}] {f.parent.name}/{f.name}: {r}")
    print("\n=== ariadne-athena-deep-backfill " + ("(APPLIED)" if args.apply else "(dry-run)") + " ===")
    for k, v in sorted(tally.items()):
        print(f"  {k}: {v}")
    if not args.apply:
        print("  ※ 反映するには --apply を付けて再実行")


if __name__ == "__main__":
    main()
