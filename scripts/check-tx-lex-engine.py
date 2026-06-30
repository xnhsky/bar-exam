#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX360 inline _lex の canonical エンジン整合ゲート（push 前・read-only）。

validate-tx-core.py の G41 を全 `*_lex.html` に横断適用し、「旧 _lex ベース流用＋
後付けパッチ script 接ぎ木」（codex 366-385 型）を push 前に機械的に弾く。

G1〜G40 は構造要素の存在しか見ないため、canonical/GENESIS-CORE.html の単一エンジンを
使わず旧 Annex C JS に band-aid(tx-inline-v1211-upgrade-js)を足した接ぎ木でも 1 ファイル
検証では PASS してしまう。本ゲートは G41 だけを束ねて配布前に走らせ、接ぎ木を含む
commit/push を止める（§7「保守的書き換え」禁止の構造的担保）。

対象は `.tx-inline-card` を持つ v12 インライン正典の _lex のみ。旧デザイン _lex
（インラインカード無し）と公式 000_TX は G41 自体が素通りなので無視される。

  python scripts/check-tx-lex-engine.py                 # 既定で outputs/ を走査
  python scripts/check-tx-lex-engine.py outputs/ux      # ルート指定
  python scripts/check-tx-lex-engine.py outputs/ux/000_TX/001_刑法/刑TX368_lex.html

失敗（接ぎ木検出）で終了コード 1。
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _load_validator():
    """validate-tx-core.py から Validator を動的ロード（ハイフン名のため import 不可）。"""
    spec = importlib.util.spec_from_file_location(
        "validate_tx_core", SCRIPTS / "validate-tx-core.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Validator


def _collect(roots: list[str]) -> list[Path]:
    files: set[Path] = set()
    for root in roots:
        p = Path(root)
        abs_path = p if p.is_absolute() else ROOT / p
        if abs_path.is_file() and abs_path.suffix == ".html":
            files.add(abs_path)
        elif abs_path.is_dir():
            files.update(abs_path.rglob("*_lex.html"))
    return sorted(files)


def main() -> int:
    Validator = _load_validator()
    roots = sys.argv[1:] or ["outputs"]
    files = _collect(roots)

    print("=== TX360 inline _lex canonical engine gate (G41) ===")
    print("roots=" + ", ".join(roots))

    scanned = 0
    offenders: list[tuple[Path, list[str]]] = []
    for f in files:
        if f.stem.endswith("_lex") is False:
            continue
        try:
            v = Validator(f)
        except Exception as e:  # 読込/parse 失敗は他ゲートが拾うのでスキップ
            print(f"  読込スキップ: {f} ({e})")
            continue
        # 対象判定（.tx-inline-card 無し＝旧デザイン）は g41 内で行われ、非対象は err を出さない
        v.g41_tx360_canonical_engine_integrity()
        g41_errs = [msg for code, msg in v.errors if code == "G41"]
        if v.soup.select_one(".tx-inline-card"):
            scanned += 1
        if g41_errs:
            offenders.append((f, g41_errs))

    print(f"\nv12 inline _lex 走査={scanned} / 接ぎ木検出={len(offenders)}")
    if offenders:
        print("\n[G41] 接ぎ木（旧エンジン流用＋後付けパッチ）を検出:")
        for f, errs in offenders:
            rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
            print(f"  ❌ {rel}")
            for m in errs:
                print(f"       - {m}")
        print(
            "\ncanonical/GENESIS-CORE.html の単一エンジンから作り直すこと。"
            "band-aid の手直しでは直らない（§7 保守的書き換え禁止）。"
        )
        return 1

    print("PASS ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
