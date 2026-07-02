#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX _lex: 正誤表（テーゼ版パネル）を体系マップ(.tx-sysmap)の上へ＋問題文ゼブラを伝播。

canonical/GENESIS-CORE.html の確定仕様に既存 _lex を決定論的・冪等に合わせる：

  1. 露出面は「テーゼ版クローン」パネル `.tx-inline-answer-table-panel`。その挿入位置を
     `.tx-sysmap` の直前へ変える（露出順: 正誤表 → 体系マップ → 肢カード）。
  2. 元の5点表は inline モードで final-answer 内に隠したまま（answer-key/データ源）。
     `moveStatementVerdictTableToTop` は元表を持ち上げない版へ正規化（過去の誤った
     「元表を体系マップ上へ引き出す」改修を revert し、二重表示を解消する）。
  3. 記述カードのゼブラ（交互背景）CSS を注入。
  4. 旧 `.tx-verdict-hoisted` CSS を撤去し、パネル余白 CSS へ。

本文（問題固有内容）は触らない。冪等（何度流しても最終状態は同じ）。

  python scripts/tx-lex-verdict-hoist.py outputs/ux/000_TX/001_刑法/刑TX355_lex.html          # dry-run
  python scripts/tx-lex-verdict-hoist.py outputs/ux/000_TX/001_刑法 --apply                    # フォルダ一括
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

# --- mover: 誤った「体系マップ上へ引き出す」版 → 元の「final-answer 内に隠す」版 ---
WRONG_MOVER = """  function moveStatementVerdictTableToTop(){
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

GOOD_MOVER = """  function moveStatementVerdictTableToTop(){
    var fa = document.querySelector('.final-answer');
    if (!fa) return null;
    var table = fa.querySelector('.statement-verdict-table');
    if (!table) return null;
    // 元の5点表は inline モードでは final-answer 内に隠して置く（answer-key/データ源）。
    // 露出面は下の renderInlineAnswerTablePanel が作る「テーゼ版クローン」。
    if (fa.firstElementChild !== table) fa.insertBefore(table, fa.firstElementChild);
    return table;
  }"""

# --- panel 挿入位置: story 前 → sysmap 前 ---
OLD_PANEL = """      panel.hidden = true;
      panel.setAttribute('hidden', '');
      var story = document.querySelector('.tx-inline-story-panel');
      if (story && story.parentNode) {
        story.parentNode.insertBefore(panel, story);
      } else {
        var anchor = document.querySelector('.solve-nav') || document.querySelector('.tx-inline-judge-list, .tx-inline-list') || document.querySelector('.tx-inline-reveal-panel') || document.querySelector('.answer-area.inline-prototype-mode');
        if (anchor && anchor.parentNode) anchor.parentNode.insertBefore(panel, anchor.nextSibling);
      }"""

NEW_PANEL = """      panel.hidden = true;
      panel.setAttribute('hidden', '');
      // 正誤表（テーゼ版）は体系マップ(.tx-sysmap)の直前へ置く（露出順: 正誤表 → 体系マップ → 肢カード）。
      var sysmap = document.querySelector('.tx-sysmap');
      var story = document.querySelector('.tx-inline-story-panel');
      if (sysmap && sysmap.parentNode) {
        sysmap.parentNode.insertBefore(panel, sysmap);
      } else if (story && story.parentNode) {
        story.parentNode.insertBefore(panel, story);
      } else {
        var anchor = document.querySelector('.solve-nav') || document.querySelector('.tx-inline-judge-list, .tx-inline-list') || document.querySelector('.tx-inline-reveal-panel') || document.querySelector('.answer-area.inline-prototype-mode');
        if (anchor && anchor.parentNode) anchor.parentNode.insertBefore(panel, anchor.nextSibling);
      }"""

OLD_CSS = """/* === 正誤表を体系マップの上へ持ち上げたとき（露出順: 正誤表 → 体系マップ → 肢カード）の体裁 ===
   final-answer から出るため、単独ブロックとして上下余白を確保する。 */
.statement-verdict-table.tx-verdict-hoisted{ margin:6px 0 22px; }"""

NEW_CSS = """/* === 正誤表（テーゼ版パネル）を体系マップの上に置いたときの体裁 === */
.tx-inline-answer-table-panel{ margin:6px 0 22px; }"""

ZEBRA_MARK = "問題文原文の交互背景（ゼブラ）"
ZEBRA_BLOCK = """
/* === 問題文原文の交互背景（ゼブラ）: 記述カードを1つおきに淡く染め、記述の切れ目を目で追える ===
   pale bg + dark text を維持（WCAG）。偶数カードだけ暖色クリームへ。テクスチャ線は踏襲。 */
.tx-inline-judge-list .tx-inline-card:nth-child(even){
  background:
    linear-gradient(180deg,rgba(250,240,226,.96) 0%,rgba(247,235,220,.98) 100%),
    repeating-linear-gradient(0deg,rgba(80,55,35,.032) 0,rgba(80,55,35,.032) 1px,transparent 1px,transparent 7px);
}
"""


def process(path: Path, apply: bool) -> str:
    html = path.read_text(encoding="utf-8")
    orig = html
    notes = []

    if WRONG_MOVER in html:
        html = html.replace(WRONG_MOVER, GOOD_MOVER, 1); notes.append("mover=revert")
    elif GOOD_MOVER in html:
        notes.append("mover=既済")
    else:
        notes.append("mover=対象外")

    if NEW_PANEL in html:
        notes.append("panel=既済")
    elif OLD_PANEL in html:
        html = html.replace(OLD_PANEL, NEW_PANEL, 1); notes.append("panel=更新")
    else:
        notes.append("panel=未検出")

    if OLD_CSS in html:
        html = html.replace(OLD_CSS, NEW_CSS, 1); notes.append("css=是正")
    elif NEW_CSS in html:
        notes.append("css=既済")
    else:
        # 旧 hoisted CSS が無い（＝別経路）。NEW_CSS を </style> 前へ注入。
        idx = html.rfind("</style>")
        if idx != -1:
            html = html[:idx] + NEW_CSS + "\n" + html[idx:]; notes.append("css=注入")

    if ZEBRA_MARK not in html:
        idx = html.rfind("</style>")
        if idx != -1:
            html = html[:idx] + ZEBRA_BLOCK + html[idx:]; notes.append("zebra=注入")
    else:
        notes.append("zebra=既済")

    changed = html != orig
    if changed and apply:
        path.write_text(html, encoding="utf-8")
    tag = "APPLIED " if (changed and apply) else ("WOULD   " if changed else "skip    ")
    return tag + f"{path.name}  [{', '.join(notes)}]"


def collect(args):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    files = collect(a.paths)
    if not files:
        print("対象なし"); return 1
    for f in files:
        print(process(f, a.apply))
    if not a.apply:
        print("\n(dry-run。--apply で書き込み)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
