# -*- coding: utf-8 -*-
"""band rollout/combo-058-136 の組合せ型（350方式）を生成する薄ランナー。
   build-combo-lex.py の build() を再利用（同ファイルは未改変）＝マージ衝突回避。
   build-combo-lex.py の import 時に同ファイル内蔵 COMBO_SPECS のループは __main__ 限定で走らない。
   冪等：build() は公式が既に single/multi なら skip。"""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

b = _load("buildcombolex", os.path.join(HERE, "build-combo-lex.py"))
s = _load("specs_combo_b", os.path.join(HERE, "specs_combo_b.py"))

targets = sys.argv[1:] if len(sys.argv) > 1 else list(s.COMBO_SPECS_B.keys())
for num in targets:
    if num not in s.COMBO_SPECS_B:
        print(f"刑TX{num}: COMBO_SPECS_B 未定義 → skip"); continue
    b.build(num, s.COMBO_SPECS_B[num])
print("COMBO-B DONE")
