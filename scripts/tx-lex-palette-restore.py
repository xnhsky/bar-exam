#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX _lex の派生パレット :root（block#3 = --accent-light…）を破壊前コミットから復元。

背景: 旧 tx-lex-recanon は per-file パレットを block#2（--accent:）しか保存せず、commit
d2fa8839「Recanon 366-385」で block#3（--accent-light/--accent-darker/--mid-* 等の派生 identity）を
canonical 既定（Twilight Violet）で上書きした。結果 367-385 で --accent(=各パレット) と
--accent-darker(=violet) の hue が割れ、ヘッダー/木SVG のグラデが破綻している。

本スクリプトは破壊直前コミット（既定 76cecf5e）から各ファイルの block#3 :root を取り出し、
現行ファイルの block#3 と差し替える（authentic な per-file 派生色を復元）。block#2（--accent:）と
本文・スクリプトには一切触れない。冪等（既に一致＝no-op）。restyle の前に走らせること
（restyle は file の block#3 をそのまま保存するため、先に正しい値へ戻す）。

  python -X utf8 scripts/tx-lex-palette-restore.py outputs/ux/000_TX/001_刑法            # dry-run
  python -X utf8 scripts/tx-lex-palette-restore.py outputs/ux/000_TX/001_刑法 --apply    # 反映
  python -X utf8 scripts/tx-lex-palette-restore.py <file> --from 76cecf5e --apply
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FROM = "76cecf5e"  # d2fa8839（block#3 破壊）の直前
DERIVED_SIG = r"--accent-light\s*:"  # block#3（派生パレット）を一意に同定


def find_derived_root(style_or_text: str):
    """--accent-light: を含む :root ブロック（block#3）の Match を返す。無ければ None。"""
    for m in re.finditer(r":root\s*\{[^}]*\}", style_or_text, re.S):
        if re.search(DERIVED_SIG, m.group(0)):
            return m
    return None


def git_show(rev: str, repo_rel: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "show", f"{rev}:{repo_rel}"],
            cwd=ROOT, capture_output=True, check=True,
        )
        return out.stdout.decode("utf-8", errors="replace")
    except subprocess.CalledProcessError:
        return None  # そのコミットに存在しない


def restore(text: str, old_text: str) -> str | None:
    """現行 text の block#3 を old_text（破壊前）の block#3 で差し替えた新 text を返す。
    どちらかに block#3 が無い／既に一致なら None（= no-op）。"""
    cur = find_derived_root(text)
    old = find_derived_root(old_text)
    if cur is None or old is None:
        return None
    if cur.group(0) == old.group(0):
        return None  # 既に正しい
    return text[: cur.start()] + old.group(0) + text[cur.end():]


def collect(paths):
    files = []
    for p in paths:
        ap = Path(p)
        ap = ap if ap.is_absolute() else ROOT / ap
        if ap.is_file() and ap.suffix == ".html":
            files.append(ap)
        elif ap.is_dir():
            files.extend(sorted(ap.rglob("*_lex.html")))
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--from", dest="rev", default=DEFAULT_FROM, help=f"復元元コミット（既定 {DEFAULT_FROM}）")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    files = collect(args.paths)
    scanned = restored = missing = noop = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        if "tx-inline-card" not in text:  # v12 inline のみ対象
            continue
        scanned += 1
        rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
        old_text = git_show(args.rev, rel)
        if old_text is None:
            missing += 1
            print(f"  [?]  {rel}: {args.rev} に存在せず（スキップ）")
            continue
        new = restore(text, old_text)
        if new is None:
            noop += 1
            continue
        restored += 1
        if args.apply:
            f.write_text(new, encoding="utf-8")
            print(f"  [w]  block#3 復元: {rel}")
        else:
            cur = find_derived_root(text); old = find_derived_root(old_text)
            cv = re.search(r"--accent-darker:\s*(#[0-9A-Fa-f]{6})", cur.group(0))
            ov = re.search(r"--accent-darker:\s*(#[0-9A-Fa-f]{6})", old.group(0))
            print(f"  [.]  would restore: {rel}  (--accent-darker {cv.group(1) if cv else '?'} -> {ov.group(1) if ov else '?'})")

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"\n[{mode}] from={args.rev} / scanned={scanned} / restored={restored} / already-ok={noop} / not-in-rev={missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
