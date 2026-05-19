#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
templates/KTX_template*.html の 3 箇所のハードコード「刑TX」「刑法」を
{{JP_PREFIX}} / {{SUBJECT_LABEL}} に置換する。

対象:
  1. <title>刑TX{{PROBLEM_ID}} - ...        (HEAD)
  2. <div class="doc-header">刑TX{{PROBLEM_ID}}</div>  (body_pre_toc)
  3. <p><strong>刑TX{{PROBLEM_ID}}</strong>・刑法（...） (footer_spec)

8 本 byte-identical な前提（check_template_sync.py の sync_required を維持）。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"

TEMPLATES = [
    "KTX_template.html",
    "KTX_template_ox4.html",
    "KTX_template_msel5.html",
    "KTX_template_sc5.html",
    "KTX_template_comb5.html",
    "KTX_template_fillin.html",
    "KTX_template_ox3comb8.html",
    "KTX_template_fillin8.html",
]

REPLACEMENTS = [
    # (old, new) のリスト。各 template に対して順次 replace する。
    ("<title>刑TX{{PROBLEM_ID}}", "<title>{{JP_PREFIX}}{{PROBLEM_ID}}"),
    (
        '<div class="doc-header">刑TX{{PROBLEM_ID}}</div>',
        '<div class="doc-header">{{JP_PREFIX}}{{PROBLEM_ID}}</div>',
    ),
    (
        "<p><strong>刑TX{{PROBLEM_ID}}</strong>・刑法（",
        "<p><strong>{{JP_PREFIX}}{{PROBLEM_ID}}</strong>・{{SUBJECT_LABEL}}（",
    ),
]


def main() -> int:
    for fname in TEMPLATES:
        fp = TEMPLATES_DIR / fname
        h = fp.read_text(encoding="utf-8")
        applied = 0
        for old, new in REPLACEMENTS:
            if old in h:
                h = h.replace(old, new, 1)
                applied += 1
        if applied:
            fp.write_text(h, encoding="utf-8")
            print(f"  OK   {fname}: {applied}/{len(REPLACEMENTS)} 置換")
        else:
            print(f"  SKIP {fname} (already up to date)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
