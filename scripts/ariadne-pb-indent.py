#!/usr/bin/env python3
"""ARIADNE 模範答案：全 .pb（番号付き役割カード含む）の本文先頭に1字下げ（2026-06-23・ユーザー指示）。
従来 .manorm の .pb だけ text-indent:1em で、role/mahang の .pb は text-indent:0 だった。
全 .pb に text-indent:1em＋display:block を効かせる（span でも確実に効くよう block 明示）。
ぶら下がりは列構造のまま不変＝text-indent は .pb 第1行のみ右へ。冪等・LF保存。"""
import glob, sys

PAIRS = [
    ('flex:1 1 auto; min-width:0; text-indent:0}',
     'flex:1 1 auto; min-width:0; text-indent:1em; display:block}'),   # role / mahang の .pb
    ('.model-answer p.manorm > .pb{text-indent:1em}',
     '.model-answer p.manorm > .pb{text-indent:1em; display:block}'),  # manorm の .pb に display:block 追記
]

def process(path):
    with open(path, encoding='utf-8', newline='') as f:
        s = f.read()
    orig = s
    for old, new in PAIRS:
        if new in s:
            continue
        s = s.replace(old, new)
    if s != orig:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(s)
        return True
    return False

def main():
    targets = sys.argv[1:] or (sorted(glob.glob('outputs/ux/000_ARIADNE/001_刑法/*_ARIADNE.html')) + ['canonical/ARIADNE.html'])
    n = sum(process(p) for p in targets)
    print(f"[pb-indent] {n}/{len(targets)} updated")

if __name__ == '__main__':
    main()
