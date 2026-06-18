#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S51 残課題のみ: spoiler-safe / multi-answer-css 直接追加"""
import glob, os

OLD = '<span class="feature-tag">ktx301-canon</span>・\n      '
NEW = ('<span class="feature-tag">ktx301-canon</span>・\n      '
       '<span class="feature-tag">spoiler-safe</span>・\n      '
       '<span class="feature-tag">multi-answer-css</span>・\n      ')

folder = r'C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam\outputs\000_TX\刑TX'
files = sorted(glob.glob(os.path.join(folder, '*.html')))
print(f'Processing {len(files)} files...')
for fp in files:
    with open(fp, encoding='utf-8') as f:
        h = f.read()
    if '<span class="feature-tag">spoiler-safe</span>' in h:
        print(f'  SKIP {os.path.basename(fp)}')
        continue
    if OLD not in h:
        print(f'  MISS {os.path.basename(fp)}')
        continue
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(h.replace(OLD, NEW, 1))
    print(f'  OK {os.path.basename(fp)}')
