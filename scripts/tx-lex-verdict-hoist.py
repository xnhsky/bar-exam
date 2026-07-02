#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX _lex: 正誤表を体系マップ(.tx-sysmap)の上へ持ち上げ＋問題文原文の交互背景（ゼブラ）を伝播。

canonical/GENESIS-CORE.html で確定した2点の意匠変更を、既存の現行エンジン _lex
（`moveStatementVerdictTableToTop` を持つ v12.2.x）へ決定論的・冪等に載せる：

  1. エンジンJS `moveStatementVerdictTableToTop` を、正誤表を `.tx-sysmap` の直前へ
     持ち上げる版へ差し替える（体系マップの無い問題は従来どおり final-answer 冒頭）。
  2. `<style>` 末尾に (a) 記述カードのゼブラ (b) 持ち上げ表の余白 の2規則を注入。

本文（問題固有内容）は一切触らない。RX の rx-restyle / tx-lex-restyle と同じ
「構造・意匠だけ正典へ同期、内容不変」の一族。

  python scripts/tx-lex-verdict-hoist.py outputs/ux/000_TX/001_刑法/刑TX355_lex.html   # dry-run
  python scripts/tx-lex-verdict-hoist.py 刑TX355_lex.html 刑TX356_lex.html --apply
  python scripts/tx-lex-verdict-hoist.py outputs/ux/000_TX/001_刑法 --apply             # フォルダ一括
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]

OLD_MOVER = """  function moveStatementVerdictTableToTop(){
    var fa = document.querySelector('.final-answer');
    if (!fa) return null;
    var table = fa.querySelector('.statement-verdict-table');
    if (!table) return null;
    if (fa.firstElementChild !== table) fa.insertBefore(table, fa.firstElementChild);
    return table;
  }"""

NEW_MOVER = """  function moveStatementVerdictTableToTop(){
    var fa = document.querySelector('.final-answer');
    if (!fa) return null;
    // 一度持ち上げると fa 外へ出るため、2回目以降は文書全体から拾う（冪等）。
    var table = fa.querySelector('.statement-verdict-table')
             || document.querySelector('.statement-verdict-table');
    if (!table) return null;
    // 正誤表は体系マップ(.tx-sysmap)の直前へ持ち上げる（露出順: 正誤表 → 体系マップ → 肢カード）。
    // 体系マップの無い問題（各肢マトリクス型）は従来どおり final-answer 冒頭に置く。
    var partA = document.getElementById('part-a');
    var sysmap = partA ? partA.querySelector('.tx-sysmap') : null;
    if (sysmap && sysmap.parentNode) {
      if (table.nextElementSibling !== sysmap || table.parentNode !== sysmap.parentNode) {
        sysmap.parentNode.insertBefore(table, sysmap);
      }
      table.classList.add('tx-verdict-hoisted');
    } else if (fa.firstElementChild !== table) {
      fa.insertBefore(table, fa.firstElementChild);
    }
    return table;
  }"""

CSS_MARK = "問題文原文の交互背景（ゼブラ）"
CSS_BLOCK = """
/* === 問題文原文の交互背景（ゼブラ）: 記述カードを1つおきに淡く染め、記述の切れ目を目で追える ===
   pale bg + dark text を維持（WCAG）。偶数カードだけ暖色クリームへ。テクスチャ線は踏襲。 */
.tx-inline-judge-list .tx-inline-card:nth-child(even){
  background:
    linear-gradient(180deg,rgba(250,240,226,.96) 0%,rgba(247,235,220,.98) 100%),
    repeating-linear-gradient(0deg,rgba(80,55,35,.032) 0,rgba(80,55,35,.032) 1px,transparent 1px,transparent 7px);
}
/* === 正誤表を体系マップの上へ持ち上げたとき（露出順: 正誤表 → 体系マップ → 肢カード）の体裁 === */
.statement-verdict-table.tx-verdict-hoisted{ margin:6px 0 22px; }
</style>"""


def process(path: Path, apply: bool) -> str:
    html = path.read_text(encoding="utf-8")
    orig = html
    notes = []

    # 1. エンジンJSの差し替え
    if NEW_MOVER in html:
        notes.append("mover=既済")
    elif OLD_MOVER in html:
        html = html.replace(OLD_MOVER, NEW_MOVER, 1)
        notes.append("mover=更新")
    else:
        notes.append("mover=対象外(旧エンジン/未検出)")

    # 2. CSS注入（最後の </style> の直前へ、未注入なら）
    if CSS_MARK in html:
        notes.append("css=既済")
    else:
        idx = html.rfind("</style>")
        if idx == -1:
            notes.append("css=</style>無しでスキップ")
        else:
            html = html[:idx] + CSS_BLOCK[1:] + html[idx + len("</style>"):]
            notes.append("css=注入")

    changed = html != orig
    if changed and apply:
        path.write_text(html, encoding="utf-8")
    return ("APPLIED " if (changed and apply) else ("WOULD   " if changed else "skip    ")) + \
        f"{path.name}  [{', '.join(notes)}]"


def collect(args) -> list[Path]:
    out = []
    for a in args:
        p = Path(a)
        if not p.is_absolute():
            cand = ROOT / a
            p = cand if cand.exists() else p
        if p.is_dir():
            out.extend(sorted(p.glob("*_lex.html")))
        elif p.exists():
            out.append(p)
        else:
            print(f"[WARN] 見つからない: {a}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--apply", action="store_true", help="実際に書き込む（既定は dry-run）")
    a = ap.parse_args()
    files = collect(a.paths)
    if not files:
        print("対象ファイルなし")
        return 1
    for f in files:
        print(process(f, a.apply))
    if not a.apply:
        print("\n(dry-run。--apply で書き込み)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
