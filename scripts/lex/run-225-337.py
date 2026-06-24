# -*- coding: utf-8 -*-
"""Band 225-337（②③型）の _lex＋公式を生成する薄ランナー。
   build-lite-lex.py / build-combo-lex.py の build() を再利用（両ファイル未改変）。
   問題固有データは specs_225_337.py（LITE / COMBO）のみ。
   引数で番号を絞れる（例: python run-225-337.py 226 227）。冪等（公式が single/multi なら skip）。"""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # build-lite-lex の `from lite_specs import ...` 解決用

def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

bl = _load("build_lite_lex", "build-lite-lex.py")
bc = _load("build_combo_lex", "build-combo-lex.py")
S  = _load("specs_225_337", "specs_225_337.py")

targets = set(sys.argv[1:])
for num, spec in S.LITE.items():
    if targets and num not in targets: continue
    bl.build(num, spec)
for num, spec in S.COMBO.items():
    if targets and num not in targets: continue
    bc.build(num, spec)
print("BAND 225-337 DONE")
