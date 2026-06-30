#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX _lex 全件 restyle（正典 <style>/engine を全インライン _lex へ載せ替え・内容不変）。

`tx-lex-recanon.py` は「接ぎ木（旧 Annex C JS／band-aid／>2 scripts）を含むファイルだけ」を
修復するため、既にクリーンな _lex はスキップされ、**正典の書式変更が波及しない**
（docs / 引継ぎの「注意3」で指摘された restyle 不在問題）。

本スクリプトは RX の `rx-restyle.py` と同じ役割の TX 版＝**接ぎ木かどうかに関係なく
全インライン `_lex` の土台（<style> と末尾エンジン <script>）を最新 canonical へ載せ替える**。
変換そのものは `tx-lex-recanon.py` の検証済み `recanon()` を**そのまま再利用**する
（パレットバグ修正 a83e20c9 を含む単一情報源。ロジック重複ゼロ）。

保全されるもの（recanon と同じ）:
  - 本文（HEADER / PART A / ox-grid / inline カード本文 / PART B / 参考条文判例 /
    SVG / 物語解説 / 解法ナビの問題固有データ）
  - per-file の AI 選定パレット（2つ目の :root{ --accent ... }）
  - per-file の <title>
  - 2本目の解法ナビ <script>（solve-nav）

載せ替えられるもの:
  - <style> の CSS 全体（パレット :root を除く＝デザイン源）
  - 末尾の canonical 単一エンジン <script>

対象外（スキップ）:
  - `.tx-inline-card` を持たない _lex（旧デザイン・ox-grid のみ等）
    → 構造が違うため recanon の前提を満たさない。別途扱う。

注意（既知の限界）:
  - Google Fonts の `<link href=...>`（font-family そのもの）は <style> の外なので
    本ツールは載せ替えない。font-family を変える書式変更時は別途リンク行を伝播する。

使い方:
  python -X utf8 scripts/tx-lex-restyle.py outputs/ux/000_TX/001_刑法            # dry-run（既定）
  python -X utf8 scripts/tx-lex-restyle.py outputs/ux/000_TX/001_刑法 --apply    # 実反映
  python -X utf8 scripts/tx-lex-restyle.py outputs/ux/000_TX/001_刑法/刑TX360_lex.html

検証は呼び出し側で全対象に validate-tx-core.py ＋ check-tx-lex-engine.py を必ず通すこと。
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]


def _load_recanon():
    """ハイフン入りファイル名 tx-lex-recanon.py をモジュールとして読み込む。"""
    path = ROOT / "scripts" / "tx-lex-recanon.py"
    spec = importlib.util.spec_from_file_location("tx_lex_recanon", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RC = _load_recanon()


def is_inline(text: str) -> bool:
    return ('class="tx-inline-card' in text) or ("class='tx-inline-card" in text)


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
    ap.add_argument("--show-unchanged", action="store_true", help="no-op ファイルも一覧表示")
    args = ap.parse_args()

    canon = RC.CANON.read_text(encoding="utf-8")
    files = collect(args.paths)

    inline = noninline = changed = unchanged = errors = 0
    changed_list = []

    for f in files:
        text = f.read_text(encoding="utf-8")
        if not is_inline(text):
            noninline += 1
            continue
        inline += 1
        try:
            new = RC.recanon(text, canon)
        except Exception as e:  # palette 不在など
            errors += 1
            print(f"  [ERR] {f.name}: {e}")
            continue
        rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
        if new == text:
            unchanged += 1
            if args.show_unchanged:
                print(f"  [=]  no-op: {rel}")
            continue
        changed += 1
        changed_list.append((rel, len(text), len(new)))
        if args.apply:
            f.write_text(new, encoding="utf-8")
            print(f"  [w]  restyled: {rel}  ({len(text):,} -> {len(new):,} bytes)")
        else:
            print(f"  [.]  would change: {rel}  ({len(text):,} -> {len(new):,} bytes)")

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(
        f"\n[{mode}] inline={inline} / changed={changed} / unchanged(no-op)={unchanged}"
        f" / non-inline-skip={noninline} / errors={errors}"
    )
    if not args.apply and changed:
        print("-> reflect with --apply, then run validate-tx-core.py + check-tx-lex-engine.py on changed files.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
