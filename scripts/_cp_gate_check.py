#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CP gate health check (inventory phase).

For each problems/*.json, re-render via render.py logic and compare SHA-256
against _phase3_2_pre_patch_baseline.json. Reports PASS / DIFF per file.

This re-renders into a temp buffer (does NOT touch outputs/) so it is safe
to run before any work begins.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import render as R  # noqa: E402


BASELINE_PATH = ROOT / "_phase3_2_pre_patch_baseline.json"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    # Discover problems
    problems_dir = ROOT / "problems"
    cases: list[tuple[str, Path]] = []  # (cli-arg, json_path)
    for jp in sorted(problems_dir.glob("*.json")):
        name = jp.stem
        if name.startswith("_"):
            continue
        if name.isdigit():
            cases.append((name, jp))
        else:
            cases.append((name, jp))

    pass_count = 0
    diff_count = 0
    missing_count = 0
    extra_count = 0
    skip_v92_count = 0
    rendered_keys: set[str] = set()

    for arg, jp in cases:
        try:
            subject, pid, json_path = R.resolve_arg(arg)
        except ValueError as e:
            print(f"  SKIP {arg}: {e}")
            continue
        problem = json.loads(json_path.read_text(encoding="utf-8"))
        # v9.2.0 spec_version files are out-of-scope for baseline comparison by design
        # (新規生成専用・_phase3_2_pre_patch_baseline.json は v9.1.0 までの hash のみ保持)
        spec_version = problem.get("spec_version", "v9.1.0")
        if spec_version == "v9.2.0":
            skip_v92_count += 1
            # SKIP した pid を rendered_keys に add して MISS 誤検出を回避
            # (baseline には旧 v9.1.0 時代の同 pid hash が登録されているため、
            #  rendered_keys に登録せずに skip すると最終 MISS チェックで誤検出される)
            json_subject = problem.get("subject")
            subject_for_skip = (
                json_subject if json_subject and json_subject in R.SUBJECT_TO_JP
                else subject
            )
            jp_prefix = R.SUBJECT_TO_JP[subject_for_skip]
            skip_out_rel = f"tx/{jp_prefix}TX/{jp_prefix}TX{pid}.html"
            rendered_keys.add(skip_out_rel)
            print(f"  {pid}: SKIP_v92 (spec_version=v9.2.0)")
            continue
        json_subject = problem.get("subject")
        if json_subject and json_subject in R.SUBJECT_TO_JP:
            subject = json_subject
        instruction_type = problem.get("instruction_type")
        tpl_path = R.TEMPLATE_PATHS.get(instruction_type, R.TEMPLATE_PATH)
        template = tpl_path.read_text(encoding="utf-8")
        slots = R.build_slot_dict(problem)
        rendered = R.render(template, slots)
        # render.py runs Path.write_text(...) which on Windows converts \n -> \r\n.
        # Reproduce that byte form so the SHA matches the on-disk file the user
        # actually consumes. (The original baseline was captured from CRLF files.)
        rendered_bytes = rendered.replace("\n", "\r\n").encode("utf-8")
        out_rel = f"tx/{R.SUBJECT_TO_JP[subject]}TX/{R.SUBJECT_TO_JP[subject]}TX{pid}.html"
        rendered_keys.add(out_rel)
        expected = baseline.get(out_rel)
        got = sha256_hex(rendered_bytes)
        if expected is None:
            print(f"  EXTRA  {out_rel:<40s}  no baseline entry  ({got[:16]}...)")
            extra_count += 1
        elif expected.lower() == got.lower():
            print(f"  PASS   {out_rel:<40s}  {got[:16]}...")
            pass_count += 1
        else:
            print(f"  DIFF   {out_rel:<40s}  exp {expected[:16]}...  got {got[:16]}...")
            diff_count += 1

    for k in sorted(baseline.keys()):
        if k not in rendered_keys:
            print(f"  MISS   {k:<40s}  baseline entry not rendered")
            missing_count += 1

    print()
    print(f"  Summary: PASS={pass_count}  DIFF={diff_count}  EXTRA={extra_count}  MISS={missing_count}  SKIP_v92={skip_v92_count}  / baseline={len(baseline)}")
    return 0 if (diff_count == 0 and missing_count == 0 and extra_count == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
