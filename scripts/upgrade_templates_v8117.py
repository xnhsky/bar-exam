#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
templates/KTX_template*.html の footer-spec を v8.11.7 化:
 - <span class="feature-tag">TX v8.11.6</span> → TX v8.11.7
 - <span class="feature-tag">p1-absolute</span>・ 直後に
   jp-prefix-naming / content-independence を追補

8 本すべて byte-identical な footer-spec を持つ前提（check_template_sync.py
の sync_required footer_spec を維持）。
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

OLD_VER = '<span class="feature-tag">TX v8.11.6</span>'
NEW_VER = '<span class="feature-tag">TX v8.11.7</span>'

P1_LINE = '<span class="feature-tag">p1-absolute</span>・\n      '
INSERT = (
    P1_LINE
    + '<span class="feature-tag">jp-prefix-naming</span>・\n      '
    + '<span class="feature-tag">content-independence</span>・\n      '
)


def main() -> int:
    for fname in TEMPLATES:
        fp = TEMPLATES_DIR / fname
        h = fp.read_text(encoding="utf-8")

        ok_ver = OLD_VER in h
        ok_p1 = "jp-prefix-naming" not in h and P1_LINE in h

        if not ok_ver and not ok_p1:
            print(f"  SKIP {fname} (already up to date)")
            continue

        if ok_ver:
            h = h.replace(OLD_VER, NEW_VER, 1)
        if ok_p1:
            h = h.replace(P1_LINE, INSERT, 1)

        fp.write_text(h, encoding="utf-8")
        print(f"  OK   {fname}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
