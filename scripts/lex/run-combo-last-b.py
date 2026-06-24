# -*- coding: utf-8 -*-
"""rollout/combo-last-B の薄ランナー（自動ビルダ非対応の最難ケース）。
   build-lite-lex.py の build() を再利用（同ファイル未改変＝マージ衝突回避）。
   対象＝N個選びなさい（多答）／個別判定（各事例1か2か3）／部分組合せ／
   語句群組合せ／ox-other。いずれも build-ox-lex が mode判定不能（○/×が各1個でない）
   等で SystemExit するため、reuse 軽量ナビ＋keep_official（or 明示番号 single）で展開する。
   冪等：build() は公式が既に single/multi なら skip。"""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

b = _load("buildlitelex", os.path.join(HERE, "build-lite-lex.py"))
s = _load("specs_combo_last_b", os.path.join(HERE, "specs_combo_last_b.py"))

targets = sys.argv[1:] if len(sys.argv) > 1 else list(s.LITE_SPECS_CLB.keys())
for num in targets:
    if num not in s.LITE_SPECS_CLB:
        print(f"刑TX{num}: LITE_SPECS_CLB 未定義 → skip"); continue
    b.build(num, s.LITE_SPECS_CLB[num])
print("COMBO-LAST-B DONE")
