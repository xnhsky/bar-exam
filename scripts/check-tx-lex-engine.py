#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX-LEX G41 engine gate.

`outputs/ux/000_TX` の `_lex` HTML を対象に、Lexia 用 DOM エンジンの最低限契約を一括検査する。
validate-tx-core.py は既存コーパスの移行警告が多いため、必要時だけ --with-validate で併走する。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
VALIDATE = ROOT / "scripts" / "validate-tx-core.py"


def iter_targets(paths: list[str]) -> list[Path]:
    found: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if not p.is_absolute():
            p = ROOT / p
        if p.is_dir():
            found.extend(sorted(p.rglob("*_lex.html")))
        elif p.is_file() and p.name.endswith("_lex.html"):
            found.append(p)
    return found


def rel(p: Path) -> str:
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def g41(path: Path) -> list[str]:
    html = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    errors: list[str] = []
    area = soup.select_one('.answer-area[data-answer-type="ox-grid"]')
    rows = area.select(".ox-row") if area else []
    if area is None:
        errors.append("G41: .answer-area[data-answer-type=ox-grid] が無い")
        return errors
    if not rows:
        errors.append("G41: .answer-area 内の .ox-row が無い")
    cv = area.get("data-correct-value", "")
    if len(cv) != len(rows):
        errors.append(f"G41: data-correct-value 長 {len(cv)} と ox-row 数 {len(rows)} が不一致")
    for idx, row in enumerate(rows, 1):
        stmt = (row.get("data-stmt") or "").strip()
        if not stmt:
            errors.append(f"G41: row {idx} に data-stmt が無い")
        vals = [(b.get("data-value") or "") for b in row.select(".ox-btn")]
        if not vals:
            errors.append(f"G41: stmt {stmt or idx} に .ox-btn が無い")
        elif idx <= len(cv) and cv[idx - 1] not in vals:
            errors.append(f"G41: stmt {stmt or idx} の正解 '{cv[idx-1]}' が選択肢 {vals} に無い")
        if not row.select_one(".ox-stmt"):
            errors.append(f"G41: stmt {stmt or idx} に .ox-stmt が無い")
    if "inline-prototype-mode" in area.get("class", []):
        cards = soup.select(".tx-inline-card[data-stmt]")
        if len(cards) != len(rows):
            errors.append(f"G41: inline card 数 {len(cards)} と ox-row 数 {len(rows)} が不一致")
        for row in rows:
            stmt = (row.get("data-stmt") or "").strip()
            if stmt and not soup.select_one(f'.tx-inline-card[data-stmt="{stmt}"]'):
                errors.append(f"G41: stmt {stmt} に対応する .tx-inline-card が無い")
            if stmt and not row.select_one(":scope > .ox-pool-explain"):
                errors.append(f"G41: inline stmt {stmt} の ox-row 直下に .ox-pool-explain が無い")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="TX-LEX G41 engine gate")
    ap.add_argument("paths", nargs="+", help="対象ルートまたは *_lex.html")
    ap.add_argument("--with-validate", action="store_true", help="validate-tx-core.py も併走する")
    args = ap.parse_args()
    targets = iter_targets(args.paths)
    if not targets:
        print("ERROR: 対象 *_lex.html がありません", file=sys.stderr)
        return 2
    failures = 0
    print("=== check-tx-lex-engine G41 ===")
    print(f"targets={len(targets)}")
    for p in targets:
        errs = g41(p)
        if args.with_validate:
            cp = subprocess.run([sys.executable, str(VALIDATE), str(p)], cwd=ROOT, text=True, capture_output=True)
            if cp.returncode != 0:
                errs.append(f"validate-tx-core exit {cp.returncode}")
                if cp.stdout:
                    print(cp.stdout, end="" if cp.stdout.endswith("\n") else "\n")
                if cp.stderr:
                    print(cp.stderr, end="" if cp.stderr.endswith("\n") else "\n")
        if errs:
            failures += 1
            print(f"[FAIL] {rel(p)}")
            for e in errs[:20]:
                print("  - " + e)
            if len(errs) > 20:
                print(f"  ... {len(errs)-20} more")
        else:
            print(f"[PASS] {rel(p)}")
    print(f"summary: passed={len(targets)-failures} failed={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
