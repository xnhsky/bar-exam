#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フォント変数の未定義参照ゲート（corpus 横断・read-only・2026-07-14・LEX-388）。

var(--font-*) を参照しているのに、その --font-* 定義が同一ファイル内に無い HTML を検出する。
未定義の var() はフォールバック値（無ければ継承＝ブラウザ既定フォント）に落ちるため、
12役割タイポグラフィが丸ごと既定フォントで描画され「正典とフォントが違う」誌面になる。

実害（2026-07-14 発見・LEX-388）：
  - 刑TX003.html／刑TX003_lex.html … 生成時にパレットを第1 :root（フォント12変数ブロック）へ
    誤上書きし、--font-* 全12変数が消滅。全既存ゲート PASS のまま push されていた。
  - 刑JX013_ARIADNE.html … 正典に無い var(--font-note) を inline style で参照（1箇所）。

同型の per-file ゲートは TX 系だけ validate-tx-core.py G68（＋push 前 check-tx-lex-engine.py）に
組込済み。本スクリプトは JX / RX / ARIADNE / TREE / references を含む全 Lexia 配信 HTML を
横断する最終網として check-lexia-preflight.py から呼ばれる。

  python scripts/check-font-vars.py                    # 既定 outputs references
  python scripts/check-font-vars.py outputs/ux         # ルート/ファイル指定

検出があれば一覧を出して終了コード 1（誤爆ゼロ設計＝定義済みなら値を問わない）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = ("outputs", "references")

USED_RE = re.compile(r"var\(\s*(--font-[a-z-]+)")
DEFINED_RE = re.compile(r"(--font-[a-z-]+)\s*:\s*[^;}]+[;}]")


def collect(roots: list[str]) -> list[Path]:
    files: set[Path] = set()
    for root in roots:
        p = Path(root)
        abs_path = p if p.is_absolute() else ROOT / p
        if abs_path.is_file() and abs_path.suffix == ".html":
            files.add(abs_path)
        elif abs_path.is_dir():
            files.update(abs_path.rglob("*.html"))
    return sorted(files)


def main() -> int:
    roots = sys.argv[1:] or list(DEFAULT_ROOTS)
    files = collect(roots)
    bad: list[tuple[Path, list[str]]] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"[WARN] 読めない: {f} ({e})")
            continue
        used = set(USED_RE.findall(text))
        if not used:
            continue
        missing = sorted(used - set(DEFINED_RE.findall(text)))
        if missing:
            bad.append((f, missing))

    print(f"=== フォント変数 未定義参照ゲート (check-font-vars) 走査 {len(files)} ファイル ===")
    if bad:
        for f, missing in bad:
            try:
                rel = f.relative_to(ROOT)
            except ValueError:
                rel = f
            print(f"[NG] {rel}: 未定義 {', '.join(missing[:12])}")
        print(f"\n{len(bad)} ファイルで未定義フォント変数を検出。第1 :root のフォント12変数ブロックの"
              "欠落／パレット誤上書き（刑TX003 型）、または正典に無い変数の参照（刑JX013_ARIADNE 型）を疑う。")
        return 1
    print("[OK] 未定義フォント変数の参照なし")
    return 0


if __name__ == "__main__":
    sys.exit(main())
