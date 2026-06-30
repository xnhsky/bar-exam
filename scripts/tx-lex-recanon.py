#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX-LEX の土台正典化ゲート。

本文・問題文を編集せず、Lexia/SM2 の土台として必要な機械可読 payload
（inline 型の `.ox-pool-explain`）だけを冪等に補完する。既存の
`scripts/tx-sm2-payload-backfill.py` と同じ抽出規則を使うため、dry-run では
対象確認、`--apply` では変更を書き込む。
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKFILL = ROOT / "scripts" / "tx-sm2-payload-backfill.py"


def load_backfill():
    spec = importlib.util.spec_from_file_location("tx_sm2_payload_backfill", BACKFILL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {BACKFILL}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def iter_targets(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if not p.is_absolute():
            p = ROOT / p
        if p.is_dir():
            out.extend(sorted(p.rglob("*_lex.html")))
        elif p.is_file() and p.name.endswith("_lex.html"):
            out.append(p)
        else:
            print(f"WARN skip non-target: {raw}")
    # de-dup while preserving order
    seen = set()
    uniq = []
    for p in out:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            uniq.append(p)
    return uniq


def main() -> int:
    ap = argparse.ArgumentParser(description="TX-LEX の本文不変・土台正典化（dry-run 既定）")
    ap.add_argument("paths", nargs="+", help="対象ディレクトリまたは *_lex.html")
    ap.add_argument("--apply", action="store_true", help="変更を書き込む（既定は対象確認のみ）")
    args = ap.parse_args()

    bf = load_backfill()
    targets = iter_targets(args.paths)
    if not targets:
        print("ERROR: 対象 *_lex.html がありません", file=sys.stderr)
        return 2

    total_changed = 0
    inline = 0
    skipped = 0
    print("=== tx-lex-recanon ===")
    print(f"mode={'apply' if args.apply else 'dry-run'} targets={len(targets)}")
    for path in targets:
        src = path.read_text(encoding="utf-8", errors="replace")
        if 'answer-area inline-prototype-mode' in src or 'inline-prototype-mode answer-area' in src:
            inline += 1
        changed, msgs = bf.process(path, dry_run=not args.apply)
        total_changed += changed
        if changed == 0:
            skipped += 1
        for msg in msgs:
            print(msg)
    print(f"summary: targets={len(targets)} inline={inline} changed={total_changed} unchanged_or_skipped={skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
