#!/usr/bin/env python3
"""誌面ワイド化マイグレーション（2026-06-20・一回限り／冪等・再実行安全）.

Lexia（iPhone/iPad）での閲覧時に「大背景の余白・誌面余白」で本文が窮屈という指摘を受け、
TX/JX/ARIADNE/RX のレイアウト CSS を一括で広げる。各置換は literal 一致で、置換後の文字列は
旧文字列を含まないため何度実行しても安全（idempotent）。

改行保持が重要：成果物 HTML は CRLF（Windows 生成）。テキストモードの read/write は CRLF→LF に
正規化し全行 diff を生む事故があったため、**バイト単位**で読み書きする（置換 literal は全て ASCII
なので UTF-8 多バイト列の途中に出現せず安全）。

対象と方針:
  - TX / JX（canonical: GENESIS-CORE/DEEP/GENESIS/KTX301/ATHENA ＋ outputs 全件）
      コンテンツ幅 1080 -> 1320px / 外周 padding 40->24px・20->16px /
      カード余白 32x36 -> 28x30px / モバイル余白 14->10px・section 18->14px /
      モバイルの表は見切れ防止で横スクロール化（GitHub 方式）
  - ARIADNE（canonical/ARIADNE.html ＋ outputs/ux/000_ARIADNE 全件）
      --maxw 780 -> 1040px / wrap・sheet 余白を微減
  - RX（outputs/ux/001_RX 全件）: カード幅 680 -> 920px
  - TREE（ARBOR）は横スクロール式キャンバスで中央寄せ余白がないため対象外
"""
from __future__ import annotations
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

# (old, new) — old は new に含まれないので冪等。2〜3値 padding は誤マッチ防止に末尾 ; を付与。
REPLACEMENTS: list[tuple[str, str]] = [
    # --- TX / JX 共通：デスクトップ ---
    ("max-width:1080px", "max-width:1320px"),
    ("padding:0 40px 48px 40px", "padding:0 24px 48px 24px"),
    ("padding:0 20px 32px 20px", "padding:0 16px 32px 16px"),
    ("padding:32px 36px;", "padding:28px 30px;"),
    # --- TX / JX 共通：モバイル（iPhone）---
    ("padding:0 14px 32px 14px", "padding:0 10px 28px 10px"),
    ("padding:22px 18px;", "padding:22px 14px;"),
    # --- モバイルの表：見切れ防止で横スクロール（TX 形 / JX 形）---
    ("table, .cmp-table{ font-size:.88em; }",
     "table, .cmp-table{ font-size:.88em; display:block; width:max-content; "
     "max-width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch; }"),
    ("table{font-size:.88em;}",
     "table{font-size:.88em;display:block;width:max-content;max-width:100%;"
     "overflow-x:auto;-webkit-overflow-scrolling:touch;}"),
    # --- ARIADNE（解法ナビ）---
    ("--maxw:780px", "--maxw:1040px"),
    (".wrap{max-width:var(--maxw); margin:0 auto; padding:0 16px 96px}",
     ".wrap{max-width:var(--maxw); margin:0 auto; padding:0 12px 80px}"),
    ("padding:12px 18px 26px;", "padding:12px 14px 26px;"),
    # --- RX 論証カード ---
    ("max-width:680px", "max-width:920px"),
    # 一部の RX は .wrap{max-width:720px} 構造（刑RX047 系）で生成された。720px は現状
    # この RX のみに出現するため全体置換で安全に 920 へ揃える（他テンプレに 720 は無い）。
    ("max-width:720px", "max-width:920px"),
]


def target_files() -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    files += sorted((REPO / "canonical").glob("*.html"))
    files += sorted((REPO / "outputs").rglob("*.html"))
    return files


def main() -> int:
    per_rule = {old: 0 for old, _ in REPLACEMENTS}
    changed_files = 0
    for path in target_files():
        data = path.read_bytes()
        original = data
        for old, new in REPLACEMENTS:
            ob = old.encode("utf-8")
            if ob in data:
                per_rule[old] += data.count(ob)
                data = data.replace(ob, new.encode("utf-8"))
        if data != original:
            path.write_bytes(data)
            changed_files += 1
    print(f"changed files: {changed_files}")
    print("replacements applied (occurrences):")
    for old, _ in REPLACEMENTS:
        label = old if len(old) < 48 else old[:45] + "..."
        print(f"  {per_rule[old]:5d}  {label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
