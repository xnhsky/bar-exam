#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""カード面に残る人物記号（§v13z・G80）の corpus 監査。

判定式は `scripts/tx_person_symbols.py`（単一情報源＝validate-tx-core.py G80 と同じ式）。

使い方:
    python -X utf8 scripts/tx-person-symbol-audit.py            # outputs/ux 配下の _lex 全走査
    python -X utf8 scripts/tx-person-symbol-audit.py <path...>  # 個別ファイル
    python -X utf8 scripts/tx-person-symbol-audit.py --md       # docs 用の Markdown 一覧
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import re  # noqa: E402
import tx_person_symbols as ps  # noqa: E402

try:
    from bs4 import BeautifulSoup
except Exception:
    print("beautifulsoup4 が必要です: pip install beautifulsoup4")
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent


def faces_of(soup):
    faces = []
    for card in soup.select(".tx-inline-card[data-stmt]"):
        label = (card.get("data-stmt") or "?").strip()
        for cls, name in (("tx-inline-stmt-text", "記述本文"), ("syn-orig", "記述原文")):
            el = card.select_one("." + cls)
            if el:
                faces.append((name, label, el.get_text(" ", strip=True)))
    for el in soup.select(".ox-stmt"):
        faces.append(("一問一答", "?", el.get_text(" ", strip=True)))
    for tr in soup.select("tr[data-brief-mark]"):
        label = (tr.get("data-stmt") or "?").strip()
        brief = re.sub(r"<[^>]+>", " ", tr.get("data-brief-mark") or "")
        faces.append(("正誤表 原文帯", label, re.sub(r"\s+", " ", brief).strip()))
    return faces


def scan(path: Path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "lxml")
    original = " ".join(el.get_text(" ", strip=True)
                        for el in soup.select(".tx-original-block, .tx-original-lead"))
    defined = ps.role_symbols(original)
    if not defined:
        return {}, []
    return defined, ps.scan_faces(faces_of(soup), defined)


def main():
    args = [a for a in sys.argv[1:] if a != "--md"]
    as_md = "--md" in sys.argv
    if args:
        targets = [Path(a) for a in args]
    else:
        targets = sorted((ROOT / "outputs" / "ux" / "000_TX").glob("*/*_lex.html"))

    rows = []
    for path in targets:
        defined, hits = scan(path)
        if hits:
            rows.append((path, defined, hits))

    total = sum(len(h) for _, _, h in rows)
    if as_md:
        print("# カード面の人物記号 残件一覧（§v13z・G80）\n")
        print(f"- 走査: {len(targets)} ファイル")
        print(f"- 該当: {len(rows)} ファイル／{total} 件")
        print("- 再生成: `python -X utf8 scripts/tx-person-symbol-audit.py --md`\n")
        for path, defined, hits in rows:
            names = "／".join(f"{k}＝{'・'.join(sorted(v))}" for k, v in sorted(defined.items()))
            print(f"## {path.name}（{names}）\n")
            for h in hits:
                print(f"- 記述{h.label}[{h.face}]『{h.symbol}』 … {h.context}")
            print()
    else:
        for path, defined, hits in rows:
            print(f"{path}  {len(hits)} 件  " +
                  "／".join(f"{k}={'・'.join(sorted(v))}" for k, v in sorted(defined.items())))
            for h in hits[:6]:
                print(f"    記述{h.label} [{h.face}] {h.symbol} … {h.context}")
        print(f"\n該当 {len(rows)} ファイル／{total} 件（走査 {len(targets)} ファイル）")
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())
