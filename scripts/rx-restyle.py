#!/usr/bin/env python3
"""既存 RX（AXIOM 構造済み）の <head> を最新 canonical/AXIOM.html へ揃える（冪等・非破壊）.

AXIOM 正典の意匠を更新したら（例：v2.0 で TX デザインシステムへ整合）、本スクリプトで
全 RX の `<head>`（フォント link＋`<style>` 一式）だけを最新正典へ差し替える。**body（本文）は
一切触らない**ため内容・クイズ・構造は完全保持。per-file の `<title>` は維持する。

前提：対象は AXIOM 構造済みファイル（`rx-recanon.py` 適用後＝AXIOM-RECANON マーカー保有）。
冪等：既に最新 head と同一なら no-op（差し替えても同じ内容）。
"""
from __future__ import annotations
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
RX_DIR = REPO / "outputs/ux/001_RX"
AXIOM = REPO / "canonical/AXIOM.html"
HEAD_RE = re.compile(r"<head>.*?</head>", re.S)
TITLE_RE = re.compile(r"<title>.*?</title>", re.S)


def main() -> int:
    axiom = AXIOM.read_text(encoding="utf-8")
    m = HEAD_RE.search(axiom)
    if not m:
        print("ERROR: AXIOM に <head> が無い")
        return 2
    axiom_head = m.group(0)

    ok = nohead = unchanged = 0
    for f in sorted(RX_DIR.rglob("*.html")):
        raw = f.read_text(encoding="utf-8")
        if not HEAD_RE.search(raw):
            nohead += 1
            continue
        tm = TITLE_RE.search(raw)
        title = tm.group(0) if tm else "<title>論点</title>"
        new_head = TITLE_RE.sub(lambda _m: title, axiom_head, count=1)
        out = HEAD_RE.sub(lambda _m: new_head, raw, count=1)
        if out == raw:
            unchanged += 1
            continue
        f.write_text(out, encoding="utf-8")
        ok += 1
    print(f"restyled={ok} unchanged={unchanged} no-head={nohead}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
