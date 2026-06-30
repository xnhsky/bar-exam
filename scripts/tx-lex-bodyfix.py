#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX _lex 本文の v12.2.0 小正規化（凡例＋判例 is-case）。決定論的・冪等・本文意味不変。

(1) 凡例（marker-legend）:
    - 「論」項の説明を「論点」→「論文と重複」（論マーカー＝論文試験と被る所の意味で合意）。
    - 「条/条文」「判/裁判例」項を区切りごと削除（実運用で未使用との合意）。
(2) 条文判例ボックスの型整合（条文=ブルー系/判例=ピンク系）:
    - .tx-law-item.is-support のうち code が「判例」のものを is-case へ改める
      （判例は必ず is-case=ピンク系。生成時に is-support 青で出た誤タグ＝5件の是正）。

restyle/answerbox とは独立（本文の別箇所）。どの順でも可。

  python -X utf8 scripts/tx-lex-bodyfix.py outputs/ux/000_TX/001_刑法            # dry-run
  python -X utf8 scripts/tx-lex-bodyfix.py outputs/ux/000_TX/001_刑法 --apply    # 反映
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

# 論ラベルは file ごとに不揃い（357件「論点」＋5件「論文関連」）。現ラベル不問で「論文と重複」へ統一。
# 既に「論文と重複」なら lookahead でスキップ（冪等）。
RON_RE = re.compile(r'(<span class="lg-sample lg-ron">論</span>)(?!論文と重複</span>)[^<]*(</span>)')
# 凡例は2系統（標準＝判「裁判例」／変種5件＝判「判例」）。判ラベルは [^<]* で両対応。
STATUTE_CASE_LEGEND_RE = re.compile(
    r'\s*<span class="lg-divider">\|</span>\s*'
    r'<span class="lg-item"><span class="statute-emphasis[^"]*">条</span>条文</span>\s*'
    r'<span class="lg-item"><span class="case-emphasis[^"]*">判</span>[^<]*</span>'
)
# is-support だが code=判例 のカードを is-case へ（属性順・空白に寛容に、code 直後まで含めて確実に同定）。
CASE_RETAG_RE = re.compile(
    r'(<div class="tx-law-item )is-support(">\s*<span class="tx-mini-law-title">'
    r'<span class="tx-mini-law-code">判例</span>)'
)


def fix(text: str):
    changes = []
    new = text

    new, n = RON_RE.subn(r'\1論文と重複\2', new)
    if n:
        changes.append(f"凡例-論ラベル={n}")

    new, n = STATUTE_CASE_LEGEND_RE.subn("", new)
    if n:
        changes.append(f"凡例-条判削除={n}")

    new, n = CASE_RETAG_RE.subn(r'\1is-case\2', new)
    if n:
        changes.append(f"判例is-case化={n}")

    return new, changes


def collect(paths):
    files = []
    for p in paths:
        ap = Path(p)
        ap = ap if ap.is_absolute() else ROOT / ap
        if ap.is_file() and ap.suffix == ".html":
            files.append(ap)
        elif ap.is_dir():
            files.extend(sorted(ap.rglob("*_lex.html")))
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    files = collect(args.paths)
    scanned = changed = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        if "marker-legend" not in text and "tx-law-item" not in text:
            continue
        scanned += 1
        new, changes = fix(text)
        if not changes:
            continue
        changed += 1
        rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
        tag = "[w]" if args.apply else "[.]"
        print(f"  {tag}  {rel}  ({', '.join(changes)})")
        if args.apply:
            f.write_text(new, encoding="utf-8")

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"\n[{mode}] scanned={scanned} / changed={changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
