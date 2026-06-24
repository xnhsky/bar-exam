# -*- coding: utf-8 -*-
"""band rollout/combo-058-136 の057方式/○×軽量ナビ型を生成する薄ランナー。
   build-lite-lex.py の build() を再利用（同ファイルは未改変）＝マージ衝突回避。
   冪等：build() は公式が既に single/multi なら skip。"""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

b = _load("buildlitelex", os.path.join(HERE, "build-lite-lex.py"))
s = _load("specs_lite_b", os.path.join(HERE, "specs_lite_b.py"))

targets = sys.argv[1:] if len(sys.argv) > 1 else list(s.LITE_SPECS_B.keys())
for num in targets:
    if num not in s.LITE_SPECS_B:
        print(f"刑TX{num}: LITE_SPECS_B 未定義 → skip"); continue
    b.build(num, s.LITE_SPECS_B[num])
print("LITE-B DONE")
