#!/usr/bin/env python3
"""作成日スタンプ（2026-06-20・既存 JX/ARIADNE/RX/TREE 向け・冪等）.

TX は GENESIS フッターに「作成日：YYYY-MM-DD」を埋め込むが、JX(ATHENA)・
ARIADNE/RX/TREE(副産物) は作成日を記録しておらず、Lexia 一覧で作成日が空欄になる。
本スクリプトは作成日を持たない HTML に **git 初回コミット日**（その問題が repo に
登録された日＝概算の作成日）を `<!-- 作成日：YYYY-MM-DD -->` コメントで </body> 直前に
埋め込む。Lexia の extractCreatedDate は raw HTML から「作成日：…」を拾うので一覧に出る。

- 冪等：既に「作成日」を含むファイルはスキップ。
- 改行コードは元ファイルに合わせて保持（CRLF/LF）。
- 対象：outputs/001_JX/** と outputs/ux/**（TX は既に作成日があるため対象外）。
"""
from __future__ import annotations
import subprocess
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
MARK = "作成日".encode("utf-8")
BODY = b"</body>"


def git_created(rel: str) -> str | None:
    out = subprocess.run(
        ["git", "-C", str(REPO), "log", "--diff-filter=A", "--format=%ad",
         "--date=format:%Y-%m-%d", "--", rel],
        capture_output=True, text=True,
    ).stdout.strip().splitlines()
    return out[-1] if out else None  # 末尾＝最初の add コミット日


def targets() -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    files += sorted((REPO / "outputs/001_JX").rglob("*.html"))
    files += sorted((REPO / "outputs/ux").rglob("*.html"))
    return files


def main() -> int:
    stamped = skipped = nodate = 0
    for f in targets():
        data = f.read_bytes()
        if MARK in data:
            skipped += 1
            continue
        date = git_created(str(f.relative_to(REPO)))
        idx = data.rfind(BODY)
        if not date or idx < 0:
            nodate += 1
            continue
        eol = b"\r\n" if b"\r\n" in data else b"\n"
        marker = ("<!-- 作成日：" + date + " -->").encode("utf-8") + eol
        data = data[:idx] + marker + data[idx:]
        f.write_bytes(data)
        stamped += 1
    print(f"stamped={stamped}  skipped(has作成日)={skipped}  nodate/no-body={nodate}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
