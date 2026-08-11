#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ariadne-loop-mode.py — ARIADNE v1.5.0 LOOP-MODE の既存一括伝播（決定論・冪等・本文不変）。

目的（正典改定の背景）
  ARIADNE 1 本は本文 約2万字（周回層 約1.15万字＋深掘り 約0.85万字）あり、
  2周目・3周目も同じ物量を通る設計だった＝「周回教材なのに周回ごとに減量する仕組みが無い」。
  v1.5.0 LOOP-MODE は `.wrap[data-loop="1|2|3"]` の段階フェードでこれを解く。

やること（3ブロック＋版スタンプ）
  1. CSS  : <style> 末尾へ `ARIADNE-LOOPMODE:BEGIN〜END`
  2. UI   : <main class="sheet"> 直後へ `ARIADNE-LOOPMODE-UI:BEGIN〜END`（周回モード切替＋案内文）
  3. JS   : 末尾 </script> 直前へ `ARIADNE-LOOPMODE-JS:BEGIN〜END`
  4. `<div class="wrap">` → `<div class="wrap" data-loop="1">`
  5. 版スタンプ `ARIADNE v1.4.0 ARENA-PURE` → `ARIADNE v1.5.0 LOOP-MODE`

単一情報源＝canonical/ARIADNE.html（3ブロックはそこから逐語抽出する）。
LLM 手編集の接ぎ木を避けるための決定論ツール（docs/canonical-revision-migration-playbook.md）。
本文（問題固有テキスト）は 1 文字も触らない。改行様式はファイルごとの優勢な様式に合わせる。

使い方:
  python scripts/ariadne-loop-mode.py --check            # 全出力を検査（書き換えなし）
  python scripts/ariadne-loop-mode.py --apply            # 全出力へ適用
  python scripts/ariadne-loop-mode.py --apply <file...>  # 個別適用
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "canonical" / "ARIADNE.html"
DEFAULT_GLOB = "outputs/ux/001_ARIADNE/**/*_ARIADNE.html"

OLD_VERSIONS = ("ARIADNE v1.4.0 ARENA-PURE",)
NEW_VERSION = "ARIADNE v1.5.0 LOOP-MODE"

CSS_BEGIN = "/* ===== ARIADNE-LOOPMODE:BEGIN"
CSS_END = "/* ===== ARIADNE-LOOPMODE:END ===== */"
UI_BEGIN = "<!-- ARIADNE-LOOPMODE-UI:BEGIN"
UI_END = "<!-- ARIADNE-LOOPMODE-UI:END -->"
JS_BEGIN = "/* ==== ARIADNE-LOOPMODE-JS:BEGIN"
JS_END = "/* ==== ARIADNE-LOOPMODE-JS:END ==== */"


def slice_block(text: str, begin: str, end: str, what: str) -> str:
    i = text.find(begin)
    j = text.find(end)
    if i < 0 or j < 0 or j < i:
        raise SystemExit(f"[ERROR] canonical から {what} ブロックを抽出できない（{begin} … {end}）")
    return text[i:j + len(end)]


def load_blocks() -> tuple[str, str, str]:
    if not CANONICAL.is_file():
        raise SystemExit(f"[ERROR] canonical not found: {CANONICAL}")
    with open(CANONICAL, encoding="utf-8", newline="") as fh:
        text = fh.read().replace("\r\n", "\n").replace("\r", "\n")
    return (
        slice_block(text, CSS_BEGIN, CSS_END, "CSS"),
        slice_block(text, UI_BEGIN, UI_END, "UI"),
        slice_block(text, JS_BEGIN, JS_END, "JS"),
    )


def dominant_newline(raw: str) -> str:
    crlf = raw.count("\r\n")
    lf_only = raw.count("\n") - crlf
    return "\r\n" if crlf > lf_only else "\n"


def replace_or_insert(text: str, block: str, begin: str, end: str, anchor: str, after: bool,
                      nl: str, last: bool = False) -> tuple[str, str]:
    """既存ブロックがあれば差し替え、無ければ anchor の前/後へ挿入。戻り値 (新text, 動作)。"""
    body = block.replace("\n", nl)
    i = text.find(begin)
    if i >= 0:
        j = text.find(end, i)
        if j < 0:
            raise SystemExit(f"[ERROR] 既存ブロックの終端 {end} が見つからない")
        new = text[:i] + body + text[j + len(end):]
        return new, ("unchanged" if new == text else "updated")
    pos = text.rfind(anchor) if last else text.find(anchor)
    if pos < 0:
        raise SystemExit(f"[ERROR] 挿入位置 {anchor!r} が見つからない")
    if after:
        at = pos + len(anchor)
        return text[:at] + nl + body + text[at:], "inserted"
    return text[:pos] + body + nl + text[pos:], "inserted"


def process(path: Path, blocks: tuple[str, str, str], apply: bool) -> tuple[str, list[str]]:
    css, ui, js = blocks
    with open(path, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    nl = dominant_newline(raw)
    text = raw
    actions: list[str] = []

    text, act = replace_or_insert(text, css, CSS_BEGIN, CSS_END, "</style>", after=False, nl=nl, last=True)
    actions.append(f"css:{act}")
    text, act = replace_or_insert(text, ui, UI_BEGIN, UI_END, '<main class="sheet">', after=True, nl=nl)
    actions.append(f"ui:{act}")
    text, act = replace_or_insert(text, js, JS_BEGIN, JS_END, "</script>", after=False, nl=nl, last=True)
    actions.append(f"js:{act}")

    # data-loop 既定値（JS 不動作でも 1周目＝全表示のフォールバック）
    if 'class="wrap" data-loop=' not in text:
        text2 = text.replace('<div class="wrap">', '<div class="wrap" data-loop="1">', 1)
        if text2 != text:
            actions.append("wrap:set")
            text = text2
        else:
            actions.append("wrap:MISSING")

    # 版スタンプ
    stamped = 0
    for old in OLD_VERSIONS:
        stamped += text.count(old)
        text = text.replace(old, NEW_VERSION)
    text = re.sub(r"ARIADNE v1\.4\.0(?! LOOP-MODE)(?![ ]ARENA)", NEW_VERSION, text)
    if stamped:
        actions.append(f"stamp:{stamped}")

    changed = text != raw
    if changed and apply:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    return ("changed" if changed else "ok"), actions


def main() -> int:
    ap = argparse.ArgumentParser(description="ARIADNE v1.5.0 LOOP-MODE 一括伝播（冪等）")
    ap.add_argument("paths", nargs="*", help="対象 HTML（省略時は ARIADNE 出力全件）")
    ap.add_argument("--apply", action="store_true", help="書き込む（既定は dry-run）")
    ap.add_argument("--check", action="store_true", help="未適用ファイルの一覧だけ出す（exit 1）")
    args = ap.parse_args()

    blocks = load_blocks()
    if args.paths:
        targets = [Path(p) if Path(p).is_absolute() else ROOT / p for p in args.paths]
    else:
        targets = sorted(ROOT.glob(DEFAULT_GLOB))
    targets = [p for p in targets if p.is_file()]
    if not targets:
        print("[ERROR] 対象ファイルなし")
        return 2

    pending: list[Path] = []
    for path in targets:
        state, actions = process(path, blocks, apply=args.apply and not args.check)
        rel = path.relative_to(ROOT).as_posix()
        if state == "changed":
            pending.append(path)
            verb = "APPLIED" if (args.apply and not args.check) else "PENDING"
            print(f"[{verb}] {rel}  ({', '.join(actions)})")
    print(f"\n=== loop-mode: 対象 {len(targets)} / 変更 {len(pending)} / 既適用 {len(targets) - len(pending)} ===")
    if args.check and pending:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
