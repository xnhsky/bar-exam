#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lexia 同期前の read-only 一括ゲート。

outputs/ と references/ を、Lexia 同期で問題になりやすい順に横断検査する。

  0. test-lexia-sync-contract.py  同期契約チェッカ自体の self-test
  1. check-duplicates.py          title/header/footer の ID 揺れ・重複
  1-bis. check-font-vars.py       var(--font-*) の未定義参照（既定フォント落ち・刑TX003/刑JX013 型）
  2. check-lexia-sync-contract.py fileName/code/title/category/sourcePath/genmeta/data-rx
  3. check-lex-oxgrid-integrity.py TX _lex ○×グリッド健全性(L1矛盾/L2組合せ当否/L3見出し/L4退化)
  4. check-ariadne-canonical.py   ARIADNE v1.2.0 正典レイアウト/スロット契約
  5. check-rx-coverage.py         ARIADNE data-rx から RX 実ファイルへの到達性

生成や修正は行わない。失敗した工程があれば終了コード 1。
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DEFAULT_ROOTS = ("outputs", "references")


@dataclass(frozen=True)
class Step:
    name: str
    command: list[str]


def display_cmd(command: list[str]) -> str:
    rel_parts: list[str] = []
    for part in command:
        if part == sys.executable:
            rel_parts.append("python")
            continue
        try:
            p = Path(part)
            if p.is_absolute():
                rel_parts.append(p.relative_to(ROOT).as_posix())
                continue
        except Exception:
            pass
        rel_parts.append(part)
    return " ".join(rel_parts)


def resolve_roots(roots: list[str]) -> tuple[list[str], list[str]]:
    cmd_roots: list[str] = []
    missing: list[str] = []
    for root in roots:
        p = Path(root)
        abs_path = p if p.is_absolute() else ROOT / p
        if not abs_path.exists():
            missing.append(root)
        try:
            cmd_roots.append(abs_path.resolve().relative_to(ROOT).as_posix())
        except ValueError:
            cmd_roots.append(str(abs_path.resolve()))
    return cmd_roots, missing


def build_steps(args: argparse.Namespace, roots: list[str]) -> list[Step]:
    py_utf8 = [sys.executable, "-X", "utf8"]
    steps: list[Step] = []
    if not args.skip_self_test:
        steps.append(
            Step(
                "sync checker self-test",
                [sys.executable, str(SCRIPTS / "test-lexia-sync-contract.py")],
            )
        )
    steps.extend([
        Step(
            "duplicate/id drift",
            [sys.executable, str(SCRIPTS / "check-duplicates.py"), *roots],
        ),
        Step(
            "font vars defined (刑TX003/刑JX013 型・LEX-388)",
            [sys.executable, str(SCRIPTS / "check-font-vars.py"), *roots],
        ),
        Step(
            "Lexia sync contract",
            [
                *py_utf8,
                str(SCRIPTS / "check-lexia-sync-contract.py"),
                "--summary",
                *roots,
            ],
        ),
    ])
    if args.json:
        steps[-1].command.extend(["--json", args.json])
    if not args.skip_tx_engine:
        steps.append(
            Step(
                "TX360 inline engine integrity (G41)",
                [sys.executable, str(SCRIPTS / "check-tx-lex-engine.py"), *roots],
            )
        )
    if not args.skip_oxgrid:
        steps.append(
            Step(
                "TX _lex ox-grid integrity (L1-L4)",
                [sys.executable, str(SCRIPTS / "check-lex-oxgrid-integrity.py"),
                 *(["--warn-only"] if not args.oxgrid_strict else []), *roots],
            )
        )
    if not args.skip_badge_indent:
        badge_globs = []
        for r in roots:
            badge_globs.append(os.path.join(r, "**", "*.html"))
        steps.append(
            Step(
                "丸囲い番号バッジ字下げ (choice-num-inline text-indent:0)",
                [sys.executable, str(SCRIPTS / "fix-choice-num-indent.py"), "--check", *badge_globs],
            )
        )
    if not args.skip_ariadne:
        steps.append(
            Step(
                "ARIADNE canonical guard",
                [sys.executable, str(SCRIPTS / "check-ariadne-canonical.py")],
            )
        )
    if not args.skip_rx:
        rx_cmd = [
            *py_utf8,
            str(SCRIPTS / "check-rx-coverage.py"),
            "--summary",
        ]
        if not args.no_rx_strict:
            rx_cmd.append("--strict")
        steps.append(Step("ARIADNE -> RX coverage", rx_cmd))
    return steps


def run_step(step: Step) -> int:
    print(f"\n--- {step.name} ---")
    print(f"$ {display_cmd(step.command)}")
    completed = subprocess.run(
        step.command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n")
    if completed.returncode == 0:
        print(f"[PASS] {step.name}")
    else:
        print(f"[FAIL] {step.name}: exit {completed.returncode}")
    return completed.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="Lexia 同期前 read-only 一括ゲート")
    ap.add_argument("roots", nargs="*", default=list(DEFAULT_ROOTS), help="走査ルート（既定: outputs references）")
    ap.add_argument("--keep-going", action="store_true", help="失敗後も残りの検査を続ける")
    ap.add_argument("--skip-self-test", action="store_true", help="同期契約チェッカの self-test を実行しない")
    ap.add_argument("--skip-ariadne", action="store_true", help="ARIADNE 正典横断検証を実行しない")
    ap.add_argument("--skip-tx-engine", action="store_true", help="TX360 inline _lex の canonical エンジン整合(G41)を実行しない")
    ap.add_argument("--skip-oxgrid", action="store_true", help="TX _lex の ox-grid 健全性(L1-L4：矛盾/組合せ当否/退化グリッド)を実行しない")
    ap.add_argument("--skip-badge-indent", action="store_true", help="丸囲い番号バッジ(.choice-num-inline)の字下げ継承ガードを実行しない")
    ap.add_argument("--oxgrid-strict", action="store_true", help="ox-grid 健全性(L1-L4)を hard ERROR にする（既定は移行期の warn-only）")
    ap.add_argument("--skip-rx", action="store_true", help="check-rx-coverage.py を実行しない")
    ap.add_argument("--no-rx-strict", action="store_true", help="RX UNREACHABLE を終了コード 1 にしない")
    ap.add_argument("--json", help="check-lexia-sync-contract.py の導出メタ JSON 出力先")
    args = ap.parse_args()

    roots, missing = resolve_roots(args.roots)
    if missing:
        print("[ERROR] 走査ルートが存在しない: " + ", ".join(missing))
        return 2

    print("=== Lexia preflight ===")
    print("roots=" + ", ".join(Path(r).relative_to(ROOT).as_posix() if Path(r).is_relative_to(ROOT) else r for r in roots))

    failures = 0
    for step in build_steps(args, roots):
        rc = run_step(step)
        if rc != 0:
            failures += 1
            if not args.keep_going:
                print("\n=== summary ===")
                print(f"FAIL={failures} / stopped at: {step.name}")
                return 1

    print("\n=== summary ===")
    if failures:
        print(f"FAIL={failures}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
