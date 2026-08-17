#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BASIS カードの「役割フォント割当て」を正す決定論ツール（2026-08-17・LEX-441）。

📚BASIS の各アイテムは種別（条文／判例 `is-case`／学説 `is-theory`）で枠色・見出し色が変わり、
**本文の役割フォント**も種別に対応する：

  - 判例（`is-case`）の判旨本文 … `judgment-text` ＝ `--font-judgment`（Zen Old Mincho 700）
  - 条文・学説の本文         … 役割クラス無し（親 `.tx-inline-explain` の `--font-answer` を継承）

この対応が崩れると、判旨が答案書体で出たり（判旨フォントが当たらない）、学説が判旨書体で出たり、
判例カードが条文の枠色（ブルー）で出たりする。1 ファイル検証（validate-tx-core G1〜G76）は
種別と本文クラスの対応を見ていないため、これまで機械検出されなかった。

修復する 3 型（いずれも本文テキストは 1 文字も変えない）:
  A: `is-case` の `<p class="hanging">` に judgment-text が無い
       → `<span class="hang-body">` に `judgment-text` を足す（正例＝刑訴TX302_lex）。
         hang-body が無い段落は `<p>` 側のクラスに足す。
  B: 種別なし（＝条文枠）なのに honbun が `<p class="judgment-text">` を持つ
       → アイテムの class に `is-case` を足す（中身が判旨なのに条文カードで出ていた）。
  C: `is-theory` の `<p class="judgment-text">`
       → `judgment-text` を外す（学説は判旨ではない。正例＝theory/hanging・theory/素の p）。

設計方針（bar-exam の決定論的 recanon 哲学）:
  - 生テキスト編集：`.tx-basis-honbun` は入れ子 div を持たない（corpus 5,882 箇所で実証）ので
    `<div class="tx-basis-honbun">(.*?)</div>` で厳密に切り出せる。該当箇所だけ差し替える。
  - 改行様式保存：CRLF/LF 混在ファイルでも全体正規化しない（`newline=''` で読み書き）。
  - 冪等：直っているファイルは無変更。
  - 単一情報源：判定は `scripts/tx_basis_roles.py` を検出ゲート（validate-tx-core G77）と共用。

使い方:
  python -X utf8 scripts/tx-basis-role-fix.py --check <file...>   # 検出のみ（exit 1 で残存を通知）
  python -X utf8 scripts/tx-basis-role-fix.py <file...>           # 修復（書き込み）
"""
from __future__ import annotations

import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tx_basis_roles as roles  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def process(path: str, apply: bool) -> tuple[int, int]:
    raw = io.open(path, "r", encoding="utf-8", newline="").read()
    findings = roles.find_issues(raw)
    if not findings:
        return 0, 0
    new_raw, fixed = roles.apply_fixes(raw, findings)
    print(f"### {path}  (役割割当ての逸脱 {len(findings)} 件 / 修正 {len(fixed)} 件)")
    for f in findings:
        mark = "[修正]" if f in fixed else "[未修正]"
        print(f"  {mark} {f.kind}: {f.detail}")
    if apply and fixed and new_raw != raw:
        io.open(path, "w", encoding="utf-8", newline="").write(new_raw)
    return len(findings), len(fixed)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_only = "--check" in sys.argv
    if not args:
        print(__doc__)
        return 2
    total = fixed = 0
    for path in args:
        t, f = process(path, apply=not check_only)
        total += t
        fixed += f
    tail = " [CHECK-ONLY]" if check_only else ""
    print(f"\n==== 走査 {len(args)} ファイル / 逸脱 {total} 件 / 修正 {fixed} 件{tail} ====")
    if check_only:
        return 1 if total else 0
    return 1 if total != fixed else 0


if __name__ == "__main__":
    sys.exit(main())
