# -*- coding: utf-8 -*-
"""Band-2（刑TX137-224）②③型の _lex（＋必要時 公式単一5択）を生成する薄ランナー。
   build-lite-lex.py / build-combo-lex.py の build() を再利用（両ファイル未改変）。
   問題固有データは specs_band2.py（LITE_SPECS_B2 / COMBO_SPECS_B2）。

   使い方：
     python scripts/lex/run-band2.py            # 全 spec を処理（冪等ガードで変換済みは skip）
     python scripts/lex/run-band2.py 139 140    # 指定番号のみ
"""
import importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # build-lite-lex.py 内の `from lite_specs import LITE_SPECS` 解決用

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

lite  = _load("buildlite",  os.path.join(HERE, "build-lite-lex.py"))
combo = _load("buildcombo", os.path.join(HERE, "build-combo-lex.py"))

import specs_band2 as S

targets = set(sys.argv[1:])

def want(num):
    return (not targets) or (num in targets)

for num, spec in S.LITE_SPECS_B2.items():
    if want(num):
        lite.build(num, spec)
for num, spec in S.COMBO_SPECS_B2.items():
    if want(num):
        combo.build(num, spec)
print("BAND2 DONE")
