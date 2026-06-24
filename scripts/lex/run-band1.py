# -*- coding: utf-8 -*-
"""Band-1（刑TX058-136）の _lex＋公式単一5択を生成する薄ランナー。
   build-ox-lex.py の build() を再利用（同ファイルは未改変）。
   build-ox-lex.py の import 時に同ファイル内蔵 SPECS のループも走るが、
   それらは既に single 変換済み＝冪等ガードで全て skip（副作用なし）。"""
import importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

b = _load("buildoxlex", os.path.join(HERE, "build-ox-lex.py"))
s = _load("specs_band1", os.path.join(HERE, "specs_band1.py"))

for num, spec in s.SPECS.items():
    b.build(num, spec)
print("BAND1 DONE")
