#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12 役割タイポグラフィの割当てを正典どおりに戻す決定論ツール（2026-08-19・LEX-442・§v13u-3）。

背景（実機指摘：刑訴TX054「フォントの割り当てが正典どおりでない」）:
  `spec/jx-v3.2-master.md` 第6項の 12 役割マトリクスに対し、TX v13 の実装には
  **12 役割の外にある第2フォント系統 `--ed-serif` / `--ed-sans` / `--ed-quote`** が存在し
  （§6-7 禁則「独自フォントの新設」）、①本文・⑤引用を上書きしていた。加えて
  ④条文は飾り要素にしか当たらず、⑥答案が解説カード全域へ過剰適用、⑦KEY は参照 0 だった。

  実測（computed style・刑訴TX054）と是正:

  | # | 役割 | 変数 | 是正前 | 是正後 |
  |---|---|---|---|---|
  | ① | 本文 | --font-body    | body が --ed-sans（Zen Kaku Gothic Antique） | --font-body |
  | ④ | 条文 | --font-statute | 条文本文＝Shippori Antique（答案書体）      | --font-statute |
  | ⑤ | 引用 | --font-quote   | .syn-orig 等が --ed-quote（Noto Serif JP）  | --font-quote（游明朝） |
  | ⑥ | 答案 | --font-answer  | 解説カード全域                              | 答案圧縮・模範答案のみ |
  | ⑦ | KEY  | --font-keyword | 参照 0（.key-phrase-box は --font-impact）  | --font-keyword |
  | ⑨ | 注釈 | --font-note    | --ed-sans（同一スタックの別名）             | --font-note |

  `--ed-serif` は `--font-display` と、`--ed-sans` は `--font-note` と、`--ed-quote` は
  `--font-statute` とスタックが完全一致する別名だったため、①⑨は見た目が変わらない衛生是正、
  ⑤⑥⑦④が実際に誌面へ効く是正である。

設計方針（bar-exam の決定論的 recanon 哲学）:
  - 単一情報源：置換表 `SUBS` は正典 `canonical/GENESIS-CARD.html` の実文字列と 1:1 対応。
  - 冪等：既に是正済みの箇所は無変更（置換前文字列が無いだけ）。
  - 改行様式保存：`newline=''` で読み書きし全体正規化しない。
  - 本文不変：CSS 宣言の font-family だけを差し替え、DOM も本文テキストも触らない。
  - 併用：BASIS 条文カード本文への ④ 適用は `scripts/tx-basis-statute-font.py`（CSS 区画の追加）。

使い方:
  python -X utf8 scripts/tx-font-roles-recanon.py --check <file...>   # 検出のみ（exit 1 で残存）
  python -X utf8 scripts/tx-font-roles-recanon.py --apply <file...>   # 是正（書き込み）
  python -X utf8 scripts/tx-font-roles-recanon.py --check --all       # outputs 配下を全走査
"""
from __future__ import annotations

import glob
import io
import sys

# (差し替え前, 差し替え後, 役割の説明)
SUBS = [
    ("background:#F1EAF1; font-family:var(--ed-sans);",
     "background:#F1EAF1; font-family:var(--font-body);",
     "① body を --ed-sans 上書きから --font-body へ"),
    (".problem-text,.sub-card.original>p,.orig-gist{ font-family:var(--ed-quote); }",
     ".problem-text,.sub-card.original>p,.orig-gist{ font-family:var(--font-quote); }",
     "⑤ 問題文・記述原文は引用書体（游明朝）"),
    (".tx-inline-stmt{ margin:0; font-family:var(--ed-quote); font-weight:560;",
     ".tx-inline-stmt{ margin:0; font-family:var(--font-quote); font-weight:560;",
     "⑤ 提示文は引用書体"),
    ("font-family:var(--ed-quote,var(--font-quote,serif)); font-weight:540; font-size:.97em;",
     "font-family:var(--font-quote,serif); font-weight:540; font-size:.97em;",
     "⑤ 正誤表の記述原文マーク"),
    (".tx-verdict-brief .tx-vb-orig{ font-family:var(--ed-quote,var(--font-quote,serif)); font-weight:540; }",
     ".tx-verdict-brief .tx-vb-orig{ font-family:var(--font-quote,serif); font-weight:540; }",
     "⑤ 正誤表の記述原文"),
    ("font-family:var(--ed-quote); background:var(--ed-tint2); border:1px solid var(--ed-line2);",
     "font-family:var(--font-quote); background:var(--ed-tint2); border:1px solid var(--ed-line2);",
     "⑤ .syn-orig（記述原文）は引用書体"),
    ("line-height:1.95; font-family:var(--ed-quote); font-weight:540;",
     "line-height:1.95; font-family:var(--font-statute); font-weight:540;",
     "④ ミニ条文カード本文は条文書体"),
    ("font-family:var(--ed-sans); font-weight:500; color:rgba(255,255,255,.92); letter-spacing:.04em;",
     "font-family:var(--font-note); font-weight:500; color:rgba(255,255,255,.92); letter-spacing:.04em;",
     "⑨ ヘッダーのバッジ・タグ"),
    ("font-family:var(--ed-sans); font-size:.84em; font-weight:700;",
     "font-family:var(--font-note); font-size:.84em; font-weight:700;",
     "⑨ kd-label"),
    ("""  font-family:var(--font-impact);
  font-size:.98rem;
  font-weight:900;
  line-height:1.95;""",
     """  font-family:var(--font-keyword);
  font-size:.98rem;
  font-weight:900;
  line-height:1.95;""",
     "⑦ KEY フレーズ箱は Kaisei Decol"),
    ('font-family:var(--font-impact),"Source Code Pro",monospace;',
     "font-family:var(--font-mono);",
     "⑪ KEY ラベル ::before は等幅（spec 6-6-8）"),
    ("""  display:inline-block;
  font-family:var(--font-impact);
  font-weight:900;
  color:var(--accent);""",
     """  display:inline-block;
  font-family:var(--font-keyword);
  font-weight:900;
  color:var(--accent);""",
     "⑦ .kp-strong は Kaisei Decol"),
    ("""  border-radius:16px;
  font-family:var(--font-answer);
  line-height:1.94;""",
     """  border-radius:16px;
  font-family:var(--font-body);
  line-height:1.94;""",
     "⑥ 解説カードの地の文は本文書体（答案書体は答案圧縮・模範答案のみ）"),
    ("""  min-width:0;
  color:#3b3346;
  font-family:var(--font-answer);""",
     """  min-width:0;
  color:#3b3346;
  font-family:var(--font-body);""",
     "⑥ 5点フロー本文は本文書体"),
    ("""  background:linear-gradient(180deg,rgba(255,255,255,.96) 0%,rgba(250,248,245,.96) 100%);
  font-family:var(--font-answer);""",
     """  background:linear-gradient(180deg,rgba(255,255,255,.96) 0%,rgba(250,248,245,.96) 100%);
  font-family:var(--font-body);""",
     "⑥ 詳説パネルは本文書体"),
]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def process(path: str, apply: bool) -> int:
    raw = io.open(path, "r", encoding="utf-8", newline="").read()
    hits = 0
    # 改行様式は **ファイル単位で決め打ちしない**（CRLF と LF が混在する実ファイルがあり、
    # 「CRLF が 1 つでもあれば全部 CRLF」と見なすと該当箇所を取り逃がす／全行差分になる）。
    # 置換前後とも LF 版・CRLF 版の両方を試し、当たった側の様式をそのまま保つ。
    for before, after, _label in SUBS:
        for nl in ("\n", "\r\n"):
            b = before.replace("\n", nl)
            a = after.replace("\n", nl)
            if b in raw:
                hits += raw.count(b)
                raw = raw.replace(b, a)
    if hits and apply:
        io.open(path, "w", encoding="utf-8", newline="").write(raw)
    return hits


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    if "--all" in sys.argv:
        args = sorted(glob.glob("outputs/ux/000_TX/*/*_lex.html")) + \
               sorted(glob.glob("outputs/000_TX/*/*.html"))
    if not args:
        print(__doc__)
        return 2
    files = total = 0
    for path in args:
        n = process(path, apply)
        if n:
            files += 1
            total += n
            if not apply:
                print(f"  [要是正 {n:2d}] {path}")
    verb = "是正" if apply else "要是正"
    print(f"\n==== 走査 {len(args)} ファイル / {verb} {files} ファイル・{total} 箇所 ====")
    return 1 if (not apply and files) else 0


if __name__ == "__main__":
    sys.exit(main())
