#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 13B 補助: KTX_template.html に施した fb-* polish CSS を残り 7 templates に伝播する。

3 つの edit を逐次適用：
  edit-1: .basis-card-body .note + .note::before （fb-4 grid + .note-body）
  edit-2: .para-num 直後に fb-1/fb-2/fb-3/priority-badge polish ブロックを挿入
  edit-3: .basis-card-body > p.hanging > .hang-body に text-indent:1em 追加 + fb-5 selector ブロック挿入

byte-level diff で副作用ゼロを担保。
"""
from __future__ import annotations
from pathlib import Path

TARGETS = [
    "KTX_template_comb5.html",
    "KTX_template_fillin.html",
    "KTX_template_fillin8.html",
    "KTX_template_msel5.html",
    "KTX_template_ox3comb8.html",
    "KTX_template_ox4.html",
    "KTX_template_sc5.html",
]

EDIT_1_OLD = """.basis-card-body .note{
  position:relative;
  background:#e7f1ff;
  border:1px solid rgba(21,101,192,.30);
  border-radius:8px;
  padding:18px 32px 14px;
  margin:14px 0 12px;
  font-family:var(--font-note); font-weight:500;
  line-height:1.95; letter-spacing:.03em;
  box-shadow:
    0 2px 6px rgba(0,0,0,.06),
    inset 0 0 0 1px rgba(255,255,255,.6);
}
.basis-card-body .note::before{
  content:'ℹ NOTE'; display:inline-block;
  background:linear-gradient(135deg,#0d47a1,#1565c0);
  color:#fff; padding:3px 10px 2px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.72rem; font-weight:700; letter-spacing:.14em;
  margin:0 8px 10px 0;
  vertical-align:2px;
  box-shadow:0 1px 2px rgba(0,0,0,.18);
}"""

EDIT_1_NEW = """.basis-card-body .note{
  position:relative;
  background:#e7f1ff;
  border:1px solid rgba(21,101,192,.30);
  border-radius:8px;
  padding:18px 32px 14px;
  margin:14px 0 12px;
  font-family:var(--font-note); font-weight:500;
  line-height:1.95; letter-spacing:.03em;
  box-shadow:
    0 2px 6px rgba(0,0,0,.06),
    inset 0 0 0 1px rgba(255,255,255,.6);
  /* fb-4 (Phase 13B): badge を 1 列目、body を 2 列目に固定 → 2 行目以降が badge 右側に揃う */
  display:grid;
  grid-template-columns:max-content 1fr;
  column-gap:12px;
  align-items:start;
}
.basis-card-body .note::before{
  content:'ℹ NOTE'; display:inline-flex;
  align-items:center;
  background:linear-gradient(135deg,#0d47a1,#1565c0);
  color:#fff; padding:3px 10px 2px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.72rem; font-weight:700; letter-spacing:.14em;
  margin:6px 0 0 0;
  box-shadow:0 1px 2px rgba(0,0,0,.18);
}
.basis-card-body .note .note-body{
  display:block;
  text-indent:1em;
}"""

EDIT_2_OLD = """.para-num{
  display:inline-block;
  background:var(--accent-3); color:var(--accent);
  padding:2px 10px; border-radius:3px;
  font-family:var(--font-statute);
  font-weight:700; font-size:.96em;
  margin-right:8px;
  border:1px solid var(--border-mid);
  letter-spacing:.04em;
}

/* === §15 強調マーカー === */"""

EDIT_2_NEW = """.para-num{
  display:inline-block;
  background:var(--accent-3); color:var(--accent);
  padding:2px 10px; border-radius:3px;
  font-family:var(--font-statute);
  font-weight:700; font-size:.96em;
  margin-right:8px;
  border:1px solid var(--border-mid);
  letter-spacing:.04em;
}

/* === §14-bis fb-3 case-scene カード化（PART A 4 場面の時系列構造・Phase 13B） === */
.case-description{ margin:18px 0 24px; }
.case-scene{
  background:linear-gradient(180deg, var(--accent-3) 0%, var(--paper) 100%);
  border:1px solid rgba(var(--accent-rgb),.18);
  border-left:5px solid var(--accent);
  border-radius:10px;
  padding:16px 22px 18px;
  margin:12px 0;
  box-shadow:0 1px 4px rgba(var(--accent-rgb),.06);
}
.case-scene-label{
  display:flex; align-items:center; gap:14px;
  padding-bottom:10px; margin-bottom:10px;
  border-bottom:1.5px dashed rgba(var(--accent-rgb),.30);
}
.case-scene-num{
  display:inline-flex; align-items:center; justify-content:center;
  width:36px; height:36px;
  border-radius:50%;
  background:var(--accent); color:#fff;
  font-family:var(--font-display);
  font-size:1.20rem; font-weight:800;
  flex-shrink:0;
  box-shadow:0 2px 6px rgba(var(--accent-rgb),.30);
}
.case-scene-title{
  font-family:var(--font-soft);
  font-size:1.02rem; font-weight:700;
  color:var(--bg-dark);
  letter-spacing:.03em; line-height:1.5;
}
.case-paragraph{
  margin:0; line-height:1.95;
  font-weight:550;
  text-indent:1em;
}

/* === §14-bis fb-1 / fb-2 / priority-badge polish (Phase 13B) === */
/* fb-1: 条文/判例 header の freq-badge を右寄せ・spacing 補強 */
.basis-card .basis-card-header{
  display:flex;
  align-items:center;
  flex-wrap:wrap;
  gap:14px;
  justify-content:space-between;
}
.basis-card .basis-card-header .freq-badge{
  margin-left:auto;
  padding:4px 12px;
  font-size:.85rem;
  letter-spacing:.05em;
}
/* fb-2: body の細字補強（500 → 550）。読解時の太さ感を上げる */
.basis-card-body p,
.sub-card.explanation p,
.sub-card.professor p,
.prof-analogy p,
.theory-detail-grid dd,
#c-4 .interpretation-body,
.basis-card-body .note{
  font-weight:550;
}
/* priority-badge 拡大（C-2 三層構造記憶の ①②③ を視認しやすく） */
.memory-list .priority-badge{
  font-size:1.40rem !important;
  font-family:var(--font-display);
  font-weight:800;
  width:42px; height:42px;
  display:inline-flex; align-items:center; justify-content:center;
  border-radius:50%;
  background:var(--accent); color:#fff;
  flex-shrink:0;
  box-shadow:0 2px 6px rgba(var(--accent-rgb),.30);
  line-height:1;
}

/* === §15 強調マーカー === */"""

EDIT_3_OLD = """.basis-card-body > p.hanging > .hang-body{
  display:block;
}

/* === §24-bis basis-card-body font-weight 改訂 (v8.11.0) === */"""

EDIT_3_NEW = """.basis-card-body > p.hanging > .hang-body{
  display:block;
  /* fb-5 (Phase 13B): 条文・判例本文の hang-body にも国語的字下げを適用 */
  text-indent:1em;
}

/* === §24-5-bis fb-5 字下げ補強（Phase 13B・base p{} で未カバーの個別 selector） === */
.mem-body p,
.key-phrase-box,
.interpretation-body,
.arena-intro,
.theory-detail-grid dd{
  text-indent:1em;
}

/* === §24-bis basis-card-body font-weight 改訂 (v8.11.0) === */"""


def main():
    root = Path(__file__).resolve().parent.parent
    tmpl_dir = root / "templates"
    edits = [
        (EDIT_1_OLD, EDIT_1_NEW, "edit-1 (.note fb-4)"),
        (EDIT_2_OLD, EDIT_2_NEW, "edit-2 (case-scene + fb-1/fb-2/priority-badge)"),
        (EDIT_3_OLD, EDIT_3_NEW, "edit-3 (hang-body + fb-5 selectors)"),
    ]
    for name in TARGETS:
        path = tmpl_dir / name
        text = path.read_text(encoding="utf-8")
        for old, new, label in edits:
            count = text.count(old)
            if count != 1:
                raise RuntimeError(f"{name}: {label} の old_string が {count} 件（期待 1）")
            text = text.replace(old, new, 1)
        path.write_text(text, encoding="utf-8", newline="")
        print(f"OK: {name}")


if __name__ == "__main__":
    main()
