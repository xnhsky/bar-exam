#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S51 残課題: feature-tag を後追い追加 + TX v8.11.0 → v8.11.1"""
import re, glob, os

def fix(fp):
    with open(fp, encoding='utf-8') as f:
        html = f.read()
    changes = []

    # version bump
    if 'TX v8.11.0' in html:
        html = html.replace(
            '<span class="feature-tag">TX v8.11.0</span>',
            '<span class="feature-tag">TX v8.11.1</span>'
        )
        changes.append('version bump 8.11.0→8.11.1')

    # spoiler-safe / multi-answer-css 追加 (ktx301-canon 直後)
    if 'spoiler-safe' not in html:
        pattern = re.compile(
            r'(<span class="feature-tag">ktx301-canon</span>・\s*\n\s*)'
        )
        m = pattern.search(html)
        if m:
            indent = re.search(r'\n(\s*)$', m.group(1)).group(1)
            insertion = (
                f'<span class="feature-tag">spoiler-safe</span>・\n{indent}'
                f'<span class="feature-tag">multi-answer-css</span>・\n{indent}'
            )
            html = pattern.sub(m.group(1) + insertion, html, count=1)
            changes.append('S51: spoiler-safe / multi-answer-css added')
        else:
            changes.append('S51: PATTERN NOT FOUND')

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(html)
    return changes


def main():
    folder = r'C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam\outputs\000_TX\刑TX'
    files = sorted(glob.glob(os.path.join(folder, '*.html')))
    for fp in files:
        changes = fix(fp)
        name = os.path.basename(fp)
        print(f'  {name}: ' + (' / '.join(changes) if changes else 'no changes'))


if __name__ == '__main__':
    main()
