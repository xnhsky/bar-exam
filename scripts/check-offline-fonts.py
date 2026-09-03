#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""オフライン同梱フォントの被覆検査（read-only・2026-08-26・LEX-443）。

build-offline-fonts.py が作った woff2 が、corpus の文字を本当に持っているかを検査する。
サブセット指定に入れても**元フォントがその字を持っていなければ収録されない**
（例：Zen Old Mincho の収録は 7,815 字で JIS 第2水準の一部を欠く）。欠けた字は
その 1 文字だけ端末フォントで描かれる＝豆腐にはならないが書体が混ざるので、
どの書体が何字欠くかを出荷前に把握しておく。

判定は 3 層に分ける（そうしないと実害と無害が混ざって読めない）：
  1. **corpus 実使用の本文文字の欠落** … 誌面に実害が出る。ERROR（終了コード 1）。
  2. 安全網（JIS 第1水準ほか）だけの欠落 … 今後その字を使ったときだけ出る。助言。
  3. 記号・絵文字（✍ ⚖ ☑ ▸ …）／欧文書体の和文欠落 … 実害なし。数えない。
     絵文字は CSS `content:` の装飾で、オンラインでも Apple Color Emoji で描かれている。
     Source Code Pro・EB Garamond 等の欧文書体は和文を持たないのが正常。

  python scripts/check-offline-fonts.py dist/lexia-offline-fonts
  python scripts/check-offline-fonts.py dist/lexia-offline-fonts --show 40
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
CHARSET = ROOT / "docs" / "data" / "lexia-offline-charset.txt"


def is_text_char(ch: str) -> bool:
    """誌面の「文字」か（＝欠落が実害になりうるか）。記号・絵文字は対象外。"""
    cp = ord(ch)
    return (
        0x3041 <= cp <= 0x3096          # ひらがな（結合記号・古字は除く）
        or 0x30A1 <= cp <= 0x30FA       # カタカナ
        or ch in "ーゝゞヽヾ"
        or 0x4E00 <= cp <= 0x9FFF       # CJK 統合漢字
        or 0x3400 <= cp <= 0x4DBF       # 拡張A
        or 0xF900 <= cp <= 0xFAFF       # 互換漢字
        or 0x20 <= cp <= 0x7E           # ASCII
        or 0xFF10 <= cp <= 0xFF19       # 全角数字
        or 0xFF21 <= cp <= 0xFF5A       # 全角英字
        or ch in "　、。・「」『』（）〔〕【】〈〉《》〜…々〆"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle", nargs="?", default="dist/lexia-offline-fonts")
    ap.add_argument("--charset", default=str(CHARSET))
    ap.add_argument("--show", type=int, default=20, help="欠落文字の表示数")
    ap.add_argument("--max-missing", type=int, default=50,
                    help="1 face あたり許容する corpus 欠落字数（既定 50）。"
                         "これを超えたらサブセット事故を疑って ERROR にする")
    a = ap.parse_args()

    from fontTools.ttLib import TTFont

    d = Path(a.bundle)
    if not d.is_absolute():
        d = ROOT / d
    cs = Path(a.charset)
    if not cs.is_absolute():
        cs = ROOT / cs
    corpus_cs = cs.with_suffix(".corpus.txt")
    if not cs.exists() or not corpus_cs.exists():
        print(f"[ERROR] 文字集合が無い: {cs} / {corpus_cs}\n"
              "  先に python scripts/lexia-font-charset.py を実行する")
        return 2

    want = {c for c in cs.read_text(encoding="utf-8").strip("\n") if is_text_char(c)}
    corpus = {c for c in corpus_cs.read_text(encoding="utf-8").strip("\n") if is_text_char(c)}
    net_only = want - corpus

    files = sorted(d.glob("*.woff2"))
    if not files:
        print(f"[ERROR] woff2 が無い: {d}")
        return 2

    print(f"=== オフライン同梱フォント被覆検査 / {len(files)} face ===")
    print(f"本文文字 {len(want)} 字（corpus 実使用 {len(corpus)} ／ 安全網のみ {len(net_only)}）\n")

    jp_rows: list[tuple[int, int, str, set[str]]] = []
    latin = 0
    total = 0
    for f in files:
        font = TTFont(str(f))
        have = {chr(cp) for cp in font.getBestCmap()}
        font.close()
        total += f.stat().st_size
        if "あ" not in have:            # 欧文書体（和文を持たないのが正常）
            latin += 1
            continue
        jp_rows.append((len(corpus - have), len((net_only - have)), f.name, corpus - have))

    jp_rows.sort(reverse=True)
    harmful = [r for r in jp_rows if r[0]]
    for n, netn, name, missing in jp_rows:
        if not n and not netn:
            continue
        tag = "[実害 corpus" if n else "[助言 安全網のみ"
        sample = "".join(sorted(missing or set())[: a.show])
        detail = f" corpus欠落: {sample}…" if n else ""
        print(f"  {tag} {n:4d} / 安全網 {netn:4d}] {name}{detail}")

    print(f"\n和文 {len(jp_rows)} face / 欧文 {latin} face（和文欠落は正常）"
          f" / バンドル合計 {total / 1024 / 1024:.2f} MB")
    over = [r for r in harmful if r[0] > a.max_missing]
    if over:
        print(f"[NG] corpus 欠落が {a.max_missing} 字を超える face が {len(over)} 件。"
              "サブセット指定の取り違え（文字集合の渡し忘れ等）を疑う。")
        return 1
    if harmful:
        print(f"[OK] 大きな欠落なし。ただし {len(harmful)} face に少数の欠落あり"
              "（＝元フォントがその字を持っていない。再ビルドしても増えないので、"
              "その字だけ端末フォントで描かれる）。")
        return 0
    print("[OK] すべての和文 face が corpus 実使用の本文文字を完全被覆")
    return 0


if __name__ == "__main__":
    sys.exit(main())
