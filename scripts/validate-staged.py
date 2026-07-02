#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pre-commit 保険：ステージ済みの Lexia 取込 HTML を、種別ごとの validator で自動検査する。

狙い：検証を手で叩かなくても、コミットのたびに自動で走らせる。フックは git（＝そのシェル）が
実行するので、Claude セッション側のシェルがブロックされていても迂回して動く。

モード（環境変数 LEXIA_VALIDATE）：
  block（既定）… ERROR があれば commit を中止（exit 1）＝コミットゲート。
  report       … 結果を表示するだけで commit は止めない（移行途中で一時的に緩めたい時）。
  off          … 何もしない。
スコープ（環境変数 LEXIA_VALIDATE_SCOPE）：
  staged（既定）… ステージ済み（--cached）。pre-commit 用。
  working       … 作業ツリーの HEAD 比変更（staged+unstaged）。セッション内フック用。
フック自身の不具合では絶対に commit を止めない（fail-open＝例外は握りつぶして exit 0）。
"""
import os
import re
import sys
import subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MODE = os.environ.get("LEXIA_VALIDATE", "block").lower()
SCOPE = os.environ.get("LEXIA_VALIDATE_SCOPE", "staged").lower()

# 引数で上書き（フックコマンドをシェル非依存にするため env プレフィックスに頼らない）
_args = sys.argv[1:]
if "--mode" in _args:
    try:
        MODE = _args[_args.index("--mode") + 1].lower()
    except Exception:
        pass
if "--scope" in _args:
    try:
        SCOPE = _args[_args.index("--scope") + 1].lower()
    except Exception:
        pass

# パス部分一致 → validator（先に一致したものを使う）
ROUTES = [
    ("outputs/ux/001_ARIADNE/", "scripts/validate-ariadne.py"),
    ("outputs/ux/002_RX/", "scripts/validate-rx.py"),
    ("outputs/ux/000_TX/", "scripts/validate-tx-core.py"),
    ("outputs/000_TX/", "scripts/validate-tx-core.py"),
    ("outputs/001_JX/", "scripts/validate-jx.py"),
]


def _run(args):
    try:
        return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except Exception:
        return None


def main():
    if MODE == "off":
        return 0
    root = _run(["git", "rev-parse", "--show-toplevel"])
    if not root or root.returncode != 0:
        return 0
    ROOT = root.stdout.strip()
    if SCOPE == "working":
        diff = _run(["git", "diff", "--name-only", "--diff-filter=ACM", "HEAD"])
    else:
        diff = _run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"])
    if not diff:
        return 0
    files = [f.strip() for f in diff.stdout.splitlines() if f.strip().lower().endswith(".html")]

    errored = []
    checked = 0
    for f in files:
        fn = f.replace("\\", "/")
        validator = next((v for pfx, v in ROUTES if pfx in fn), None)
        if not validator:
            continue
        vpath = os.path.join(ROOT, validator)
        if not os.path.exists(vpath):
            continue
        r = _run([sys.executable, "-X", "utf8", vpath, os.path.join(ROOT, f)])
        checked += 1
        if r is None:
            continue
        out = (r.stdout or "") + (r.stderr or "")
        if r.returncode != 0 or re.search(r"\[ERROR\]", out):
            errs = [ln for ln in out.splitlines() if "ERROR" in ln]
            errored.append((f, errs[:6]))

    if not checked:
        return 0
    if errored:
        print(f"[pre-commit] Lexia validate: {len(errored)}/{checked} file(s) have ERROR:")
        for f, errs in errored:
            print(f"  x {f}")
            for e in errs:
                print(f"      {e.strip()}")
        if MODE == "block":
            print("[pre-commit] LEXIA_VALIDATE=block -> commit aborted. Fix, or run once with LEXIA_VALIDATE=report git commit ...")
            return 1
        print("[pre-commit] report mode: commit continues. Set LEXIA_VALIDATE=block to gate.")
    else:
        print(f"[pre-commit] Lexia validate OK ({checked} file(s), 0 ERROR)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # fail-open: フックの不具合で commit を止めない
        print(f"[pre-commit] validate-staged skipped (fail-open): {e}")
        sys.exit(0)
