#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全ファイル validate_structure.py 一括実行・サマリ表示

注: 旧 validate.py から PATCH §3 によりリネーム済み。構造検証 (S1〜S77) のみ。
    内容検証は別途 validate_content.py を回すこと。
"""
import subprocess, glob, os

folder = r'C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam\outputs\tx\刑TX'
script = r'C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam\scripts\validate_structure.py'
files = sorted(glob.glob(os.path.join(folder, '*.html')))

passed = []
warned = []
failed = []

for fp in files:
    name = os.path.basename(fp)
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    r = subprocess.run(
        ['python', script, fp],
        capture_output=True, text=True, env=env, encoding='utf-8'
    )
    out = r.stdout
    if 'ERROR が' in out and '件あります' in out:
        failed.append((name, out))
    elif 'WARNING' in out and '⚠️' in out:
        warned.append((name, out))
    else:
        passed.append(name)

print(f'\n=== サマリ ===')
print(f'  ✅ 全件通過: {len(passed)}')
print(f'  ⚠️  WARNING: {len(warned)}')
print(f'  ❌ ERROR:    {len(failed)}')

if warned:
    print('\n=== WARNING ===')
    for name, out in warned:
        # WARNING 行を抽出
        for line in out.split('\n'):
            if '[S' in line and ']' in line:
                print(f'  {name}: {line.strip()}')

if failed:
    print('\n=== ERROR ===')
    for name, out in failed:
        for line in out.split('\n'):
            if '[S' in line and 'ERROR' in line.upper():
                print(f'  {name}: {line.strip()}')
