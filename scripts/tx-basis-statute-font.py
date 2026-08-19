#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BASIS 条文カードの本文へ条文書体（--font-statute）を当てる CSS 区画を伝播する
（2026-08-19・LEX-442・§v13u-2）。

背景:
  12 役割のうち ④条文 `--font-statute` は `.para-num` / `.ron-mark` / `.statute-emphasis` /
  `.case-emphasis` の 4 箇所にしか当たっておらず、📚BASIS の**条文本文そのもの**は親
  `.tx-inline-explain` の `--font-answer`（Shippori Antique＝答案書体）を継承していた。
  そのため条文カードなのに条文が解説と同じ書体で流れ、号数チップだけが明朝という反転が
  起きる（実機指摘：刑訴TX054 の 60条1項 各号）。

設計方針（bar-exam の決定論的 recanon 哲学）:
  - 単一情報源：区画 `TX-BASIS-STATUTE:BEGIN 〜 :END` を `canonical/GENESIS-CARD.html` から
    **逐語抽出**して差し込む（このスクリプトに CSS を書かない＝正典と二重管理しない）。
  - 挿入位置：`/* TX-VERDICT-CORE2:END */` の直後。同区画を持たない旧世代は第1 `<style>` の
    閉じタグ直前へ落とす（`.tx-basis-honbun` を持たないファイルだけが真の対象外）。
  - 冪等：既に区画があるファイルは、正典と一致していれば無変更／異なれば正典で置き換える。
  - 改行様式保存：CRLF/LF を全体正規化しない（`newline=''` で読み書きし、挿入行だけ局所整形）。
  - 本文不変：CSS 区画の追加だけで、DOM も本文テキストも 1 文字も触らない。

使い方:
  python -X utf8 scripts/tx-basis-statute-font.py --check <file...>   # 検出のみ（exit 1 で残存）
  python -X utf8 scripts/tx-basis-statute-font.py --apply <file...>   # 伝播（書き込み）
  python -X utf8 scripts/tx-basis-statute-font.py --check --all       # outputs 配下を全走査
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys

BEGIN = "/* TX-BASIS-STATUTE:BEGIN"
END = "/* TX-BASIS-STATUTE:END */"
ANCHOR = "/* TX-VERDICT-CORE2:END */"
CANONICAL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "canonical", "GENESIS-CARD.html")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def canonical_block() -> str:
    raw = io.open(CANONICAL, "r", encoding="utf-8", newline="").read()
    i = raw.find(BEGIN)
    j = raw.find(END)
    if i < 0 or j < 0:
        raise SystemExit(f"ERROR: 正典に {BEGIN} 区画がありません: {CANONICAL}")
    return raw[i:j + len(END)]


def newline_of(raw: str) -> str:
    return "\r\n" if "\r\n" in raw else "\n"


def process(path: str, block: str, apply: bool) -> str:
    """戻り値: 'SKIP'（対象外） / 'OK'（既に正典どおり） / 'FIX'（要伝播・適用済み）"""
    raw = io.open(path, "r", encoding="utf-8", newline="").read()
    if "tx-basis-honbun" not in raw:
        return "SKIP"          # BASIS を持たない世代＝当てる先が無い
    nl = newline_of(raw)
    want = block.replace("\r\n", "\n").replace("\n", nl)

    i = raw.find(BEGIN)
    if i >= 0:
        j = raw.find(END, i)
        if j < 0:
            return "SKIP"
        current = raw[i:j + len(END)]
        if current == want:
            return "OK"
        new_raw = raw[:i] + want + raw[j + len(END):]
    else:
        if ANCHOR in raw:
            k = raw.find(ANCHOR) + len(ANCHOR)
        else:
            k = raw.find("</style>")   # 旧世代＝第1 <style> の閉じタグ直前
            if k < 0:
                return "SKIP"
        new_raw = raw[:k] + nl + want + nl + raw[k:] if ANCHOR not in raw else raw[:k] + nl + want + raw[k:]

    if apply:
        io.open(path, "w", encoding="utf-8", newline="").write(new_raw)
    return "FIX"


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    if "--all" in sys.argv:
        args = sorted(glob.glob("outputs/ux/000_TX/*/*_lex.html")) + \
               sorted(glob.glob("outputs/000_TX/*/*.html"))
    if not args:
        print(__doc__)
        return 2

    block = canonical_block()
    counts = {"SKIP": 0, "OK": 0, "FIX": 0}
    for path in args:
        r = process(path, block, apply)
        counts[r] += 1
        if r == "FIX" and not apply:
            print(f"  [要伝播] {path}")
    verb = "伝播" if apply else "要伝播"
    print(f"\n==== 走査 {len(args)} ファイル / {verb} {counts['FIX']} / "
          f"既に正典どおり {counts['OK']} / 対象外（BASIS なし）{counts['SKIP']} ====")
    if not apply and counts["FIX"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
