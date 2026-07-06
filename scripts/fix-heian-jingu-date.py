#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""平安神宮放火事件の判例年の誤りを一括是正する決定論スクリプト（冪等）。

正 = 最決平元.7.14（平成元年 = 1989）／誤 = 平7.7.14（平成7年）。
canonical/GENESIS-CORE.html・GENESIS-CARD.html の solve-nav linker と、
そこから既存 _lex・公式 HTML に boilerplate として波及した誤記を直す。

- 既定は dry-run（該当行のユニーク一覧を表示して文脈確認を兼ねる）。
- --apply で書き込み（str.replace の完全一致・冪等）。
- cp932 パイプ出力対策で UTF-8 を強制（feedback_python_cp932_piped_stdout_gate）。
"""
import sys
import pathlib

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent

# 誤 → 正。プレーンより先に正規表現リテラルを処理（相互に部分列でないため順序は無害だが明示）。
PAIRS = [
    (r'平7\.7\.14', r'平元\.7\.14'),        # JS 正規表現リテラル（linker の /最決平7\.7\.14/）
    ('平7.7.14',   '平元.7.14'),            # プレーン（needles / label / 本文）
    ('平成7年7月14日', '平成元年7月14日'),   # 完全日付（needles / 本文）
]

apply = '--apply' in sys.argv

targets = sorted(
    list((ROOT / 'canonical').glob('*.html')) +
    list((ROOT / 'outputs').rglob('*.html'))
)

uniq = {}
files = 0
hits = 0
for f in targets:
    try:
        # read_bytes/write_bytes で改行(LF/CRLF)を一切変換しない（Windows の
        # text-mode 改行変換で全行が差分化する事故を防ぐ・byte 保存）。
        text = f.read_bytes().decode('utf-8')
    except Exception:
        continue
    n = sum(text.count(a) for a, _ in PAIRS)
    if not n:
        continue
    files += 1
    hits += n
    if apply:
        new = text
        for a, b in PAIRS:
            new = new.replace(a, b)
        if new != text:
            f.write_bytes(new.encode('utf-8'))
            print(f"[fixed {n}] {f.relative_to(ROOT)}")
    else:
        for line in text.splitlines():
            if any(a in line for a, _ in PAIRS):
                key = line.strip()[:200]
                uniq[key] = uniq.get(key, 0) + 1

if not apply:
    print("=== 該当行のユニーク一覧（dry-run・文脈確認）===")
    for k, c in sorted(uniq.items(), key=lambda x: -x[1]):
        print(f"[x{c}] {k}")
print(f"--- {'APPLIED' if apply else 'DRY-RUN'}: {files} files, {hits} hits ---")
