#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ARIADNE v1.1.0 canonical guard.

Run validate-ariadne.py over the active skeleton and generated ARIADNE files.
Warnings are allowed by validate-ariadne.py; any ERROR exits non-zero.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-ariadne.py"
DEFAULT_GLOB = "outputs/ux/001_ARIADNE/**/*_ARIADNE.html"
CANONICAL_VERSION = "ARIADNE v1.1.0 MATRIX-THREAD"


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def collect_files(include_canonical: bool, patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    if include_canonical:
        canonical = ROOT / "canonical" / "ARIADNE.html"
        if canonical.exists():
            files.append(canonical)
    for pattern in patterns:
        base_pattern = pattern.replace("\\", "/")
        matched = sorted(ROOT.glob(base_pattern))
        files.extend(p for p in matched if p.is_file())
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in files:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(path)
    return unique


def run_validator(path: Path, verbose: bool) -> int:
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if verbose or completed.returncode != 0:
        print(f"\n--- {rel(path)} ---")
        if completed.stdout:
            print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
        if completed.stderr:
            print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n")
    else:
        summary = ""
        for line in completed.stdout.splitlines():
            if line.startswith("=== ARIADNE"):
                summary = line
        print(f"[OK] {rel(path)}" + (f" :: {summary}" if summary else ""))
    return completed.returncode


def check_canonical_version() -> int:
    canonical = ROOT / "canonical" / "ARIADNE.html"
    if not canonical.exists():
        print("[ERROR] canonical/ARIADNE.html not found")
        return 1
    text = canonical.read_text(encoding="utf-8", errors="replace")
    if CANONICAL_VERSION not in text:
        print(f"[ERROR] canonical/ARIADNE.html version marker missing: {CANONICAL_VERSION}")
        return 1
    print(f"[OK] canonical/ARIADNE.html version marker: {CANONICAL_VERSION}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="ARIADNE canonical/preflight guard")
    ap.add_argument(
        "patterns",
        nargs="*",
        default=[DEFAULT_GLOB],
        help="ROOT-relative glob(s) to validate",
    )
    ap.add_argument("--no-canonical", action="store_true", help="do not validate canonical/ARIADNE.html")
    ap.add_argument("--verbose", action="store_true", help="print full validator output for passing files")
    args = ap.parse_args()

    files = collect_files(not args.no_canonical, args.patterns)
    if not files:
        print("[ERROR] ARIADNE validation target not found")
        return 2

    print("=== ARIADNE canonical guard ===")
    print(f"targets={len(files)}")
    failures = check_canonical_version() if not args.no_canonical else 0
    for path in files:
        rc = run_validator(path, args.verbose)
        if rc != 0:
            failures += 1

    print("\n=== summary ===")
    print(f"files={len(files)}  FAIL={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
