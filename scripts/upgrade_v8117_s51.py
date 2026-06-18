#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v8.11.7 S51 タグ追補:
 - <span class="feature-tag">TX v8.11.6</span> → TX v8.11.7
 - <span class="feature-tag">p1-absolute</span>・ 直後に
   jp-prefix-naming / content-independence を追補

対象: outputs/000_TX/001_刑法/*.html （_quarantine 配下を除く）
"""
import glob, os, sys, re

ROOT = r'C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam'
TARGET_DIR = os.path.join(ROOT, 'outputs', 'tx', '刑TX')

OLD_VER = '<span class="feature-tag">TX v8.11.6</span>'
NEW_VER = '<span class="feature-tag">TX v8.11.7</span>'

# p1-absolute の行末（"・\n      "）直後に 2 タグを追加
P1_LINE = '<span class="feature-tag">p1-absolute</span>・\n      '
INSERT_TAGS = (
    P1_LINE
    + '<span class="feature-tag">jp-prefix-naming</span>・\n      '
    + '<span class="feature-tag">content-independence</span>・\n      '
)


def main():
    files = sorted(
        f for f in glob.glob(os.path.join(TARGET_DIR, '*.html'))
        if '_quarantine' not in f
    )
    print(f'Targets: {len(files)} file(s)')
    for fp in files:
        name = os.path.basename(fp)
        with open(fp, encoding='utf-8') as f:
            h = f.read()

        changed = False
        if OLD_VER in h:
            h = h.replace(OLD_VER, NEW_VER, 1)
            changed = True

        if 'jp-prefix-naming' not in h:
            if P1_LINE in h:
                h = h.replace(P1_LINE, INSERT_TAGS, 1)
                changed = True
            else:
                print(f'  WARN {name}: p1-absolute anchor not found, skipping insert')

        if changed:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(h)
            print(f'  OK   {name}')
        else:
            print(f'  SKIP {name} (already up to date)')


if __name__ == '__main__':
    main()
