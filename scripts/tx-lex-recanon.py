#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX360 inline _lex 正典化（接ぎ木修復・内容保持）。

codex 等が「既存 _lex を v12 インラインへ手で更新」した結果生じる接ぎ木
（旧 Annex C JS 流用＋後付けパッチ `tx-inline-v1211-upgrade-js`＋不足 CSS）を、
本文（問題固有内容）を温存したまま土台だけ canonical/GENESIS-CORE.html へ載せ替える。
RX の rx-recanon.py / rx-restyle.py と同じ「内容不変・構造正典化」の一族。

やること（決定論的・冪等）:
  1. <style> を canonical のものへ差し替え。ただし AI 選定パレット（2つ目の :root{}）は元のまま。
     → 不足していた toast / result / inline 系 CSS が canonical 品質で揃う。
  2. <script> を「canonical 単一エンジン ＋ 元の解法ナビ(solve-nav)」の最大 2 本へ再構成。
     → 旧 Annex C JS と band-aid を物理削除し、inline カードを正典エンジンが自前配線する。
  3. 本文の `.tx-inline-explain` に初期 hidden を付与（canonical 契約・G40）。
  本文（HEADER / PART A / ox-grid / inline カード本文 / PART B / 参考条文判例 / SVG /
  物語解説 / 解法ナビの問題固有データ）は一切触らない。

対象は `.tx-inline-card` を持つ v12 inline _lex のうち G41 接ぎ木を含むファイルのみ。
既に正典（360-365 等）や旧デザイン _lex はスキップ（冪等）。

  python scripts/tx-lex-recanon.py outputs/ux/000_TX/001_刑法/刑TX366_lex.html   # dry-run（既定）
  python scripts/tx-lex-recanon.py outputs/ux/000_TX --apply                      # 配下を一括修復
  python scripts/tx-lex-recanon.py outputs/ux --apply

検証は呼び出し側で `validate-tx-core.py` ＋ `check-tx-lex-engine.py` を必ず通すこと。
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
CANON = ROOT / "canonical" / "GENESIS-CORE.html"

BAND_AID = "tx-inline-v1211-upgrade-js"
ENGINE_SIG = "hydrateInlinePartBDetails"  # canonical 単一エンジンの固有関数


def split_style(text: str):
    """(pre[..<style>], style_inner, after[</style>..]) を返す。"""
    s_open = text.index("<style>") + len("<style>")
    s_close = text.index("</style>")
    return text[:s_open], text[s_open:s_close], text[s_close:]


def palette_root(style_inner: str) -> str:
    """style 内の2つ目の :root{...}（AI 選定パレット）ブロック。"""
    roots = list(re.finditer(r":root\{[^}]*\}", style_inner, re.S))
    if len(roots) < 2:
        raise ValueError(f"パレット :root が見つからない (count={len(roots)})")
    return roots[1].group(0)


def extract_scripts(text: str):
    return [m.group(0) for m in re.finditer(r"<script\b.*?</script>", text, re.S)]


def is_target(text: str) -> bool:
    """v12 inline かつ接ぎ木（band-aid or 旧エンジン）を含むファイルだけ対象。"""
    if 'class="tx-inline-card' not in text and "class='tx-inline-card" not in text:
        return False
    grafted = (BAND_AID in text) or (ENGINE_SIG not in text) or (len(extract_scripts(text)) > 2)
    return grafted


def recanon(text: str, canon: str) -> str:
    pre, style_src, _ = split_style(text)
    _, style_canon, _ = split_style(canon)

    # 1) style を canonical へ。パレット :root だけ元を保存。
    pal = palette_root(style_src)
    croots = list(re.finditer(r":root\{[^}]*\}", style_canon, re.S))
    style_new = style_canon[:croots[1].start()] + pal + style_canon[croots[1].end():]

    # 本文 = </style> 〜 最初の <script> 直前
    s_close = text.index("</style>")
    first_script = text.index("<script", s_close)
    body = text[s_close:first_script]
    tail = text[text.rindex("</script>") + len("</script>"):]

    # 2) scripts 再構成: canonical エンジン ＋ 元の解法ナビ
    engine = extract_scripts(canon)[0]
    src_scripts = extract_scripts(text)
    solvenav = [s for s in src_scripts if "solve-nav" in s and ENGINE_SIG not in s]

    # 3) 本文契約: .tx-inline-explain を初期 hidden（冪等）
    body = re.sub(r'<div class="tx-inline-explain">',
                  '<div class="tx-inline-explain" hidden>', body)

    new = pre + style_new + body + engine
    for sn in solvenav:
        new += "\n" + sn
    return new + tail


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
    ap.add_argument("paths", nargs="+", help="_lex.html ファイル or ディレクトリ")
    ap.add_argument("--apply", action="store_true", help="実際に上書きする（既定 dry-run）")
    args = ap.parse_args()

    canon = CANON.read_text(encoding="utf-8")
    files = collect(args.paths)
    targeted = skipped = fixed = errors = 0

    for f in files:
        text = f.read_text(encoding="utf-8")
        if not is_target(text):
            skipped += 1
            continue
        targeted += 1
        try:
            new = recanon(text, canon)
        except Exception as e:
            errors += 1
            print(f"  ❌ {f.name}: {e}")
            continue
        rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
        if args.apply:
            f.write_text(new, encoding="utf-8")
            fixed += 1
            print(f"  ✏️  修復: {rel}  ({len(text):,} → {len(new):,} bytes)")
        else:
            print(f"  • 対象: {rel}  ({len(text):,} → {len(new):,} bytes 予定)")

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"\n[{mode}] 接ぎ木対象={targeted} / 修復={fixed} / 非対象スキップ={skipped} / エラー={errors}")
    if not args.apply and targeted:
        print("→ 上書きするには --apply。修復後は validate-tx-core.py と check-tx-lex-engine.py を通すこと。")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
