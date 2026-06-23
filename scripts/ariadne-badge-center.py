#!/usr/bin/env python3
"""ARIADNE バッジ中央化（2026-06-23）：letter-spacing を持つが text-indent 欠落の
shrink-to-fit ピル 3 種へ text-indent=letter-spacing を併記して左右中央化。
冪等・LF 保存（open(newline='')）。対象：周回ドリル○×タブ／bc-flow チップ／条文項番号ピル。
他のバッジ（role::before/⚖判旨/🔑KEY/freq/kd-label/rank/ddl/ma-h 等）は既に ti=ls 済。
flex コンテナ・全幅ラベルは text-indent 無効/左寄せ意図のため対象外。"""
import glob, sys

PAIRS = [
    # (OLD, NEW) — 末尾 letter-spacing の直後に text-indent 同値を併記
    ('border-radius:7px; padding:2px 10px; letter-spacing:.03em}',
     'border-radius:7px; padding:2px 10px; letter-spacing:.03em; text-indent:.03em}'),  # .self-check-quiz::before
    ('letter-spacing:.03em; color:var(--li-deep); background:#fff; border:1px solid var(--li-line); border-radius:8px; padding:3px 11px}',
     'letter-spacing:.03em; text-indent:.03em; color:var(--li-deep); background:#fff; border:1px solid var(--li-line); border-radius:8px; padding:3px 11px}'),  # .bc-flow span
    ('margin-right:7px; border:1px solid var(--li-line); letter-spacing:.04em}',
     'margin-right:7px; border:1px solid var(--li-line); letter-spacing:.04em; text-indent:.04em}'),  # .basis-card-body .para-num
]

def process(path):
    with open(path, encoding='utf-8', newline='') as f:
        s = f.read()
    orig = s
    for old, new in PAIRS:
        if new in s:           # idempotent: already applied
            continue
        s = s.replace(old, new)
    if s != orig:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(s)
        return True
    return False

def main():
    files = sorted(glob.glob('outputs/ux/000_ARIADNE/001_刑法/*_ARIADNE.html')) + ['canonical/ARIADNE.html']
    n = 0
    for p in files:
        if process(p):
            n += 1
            print(f"  fixed {p}")
    print(f"[badge-center] {n} / {len(files)} files updated")

if __name__ == '__main__':
    main()
