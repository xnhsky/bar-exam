# -*- coding: utf-8 -*-
"""薄ランナー：rollout/combo-339-444（②③ 二系統化）の lite 仕様を build-lite-lex.py の
build() に流す。仕様は specs_combo339_*.py（サブエージェント執筆・keep_official 型）に分割。
build-lite-lex.py は未改変 import 再利用（band1 の run-band1.py と同思想）。"""
import sys, os, importlib, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# build-lite-lex.py（ハイフン名）を spec で読み込み、build() を取得
_spec = importlib.util.spec_from_file_location("build_lite_lex", os.path.join(HERE, "build-lite-lex.py"))
_blite = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_blite)
build = _blite.build

# 分割仕様モジュールを集約（順序は問わない＝番号キーで一意）
SPEC_MODULES = [
    "specs_combo339_w1a", "specs_combo339_w1b", "specs_combo339_w1c",
    "specs_combo339_w2a", "specs_combo339_w2b", "specs_combo339_w2c",
]
MERGED = {}
for name in SPEC_MODULES:
    try:
        m = importlib.import_module(name)
    except ModuleNotFoundError:
        continue
    MERGED.update(m.SPECS)

if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else sorted(MERGED.keys())
    for num in targets:
        if num not in MERGED:
            print(f"刑TX{num}: combo339 仕様未定義 → skip"); continue
        build(num, MERGED[num])
    print("DONE")
