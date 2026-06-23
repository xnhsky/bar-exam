#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""既存フッタースタンプを英語表記 "Generated: …" へ一括移行する（一回限り・冪等）.

- genmeta 済み(JX/副産物/参考資料): 既存 data-generated の日時を厳密に保持して英語へ置換。
- TX 既存の日本語 footer-date「作成日：…」: git 初出コミット日時(時刻つき)で英語 genmeta へ置換。
- いずれも stamp_footer.stamp_html がフッターのコンテナ内に収める。

使い方:
    python scripts/restamp-english.py --dry-run --limit 6
    python scripts/restamp-english.py
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from stamp_footer import stamp_file, infer_version, JST  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent
DIRS = ("outputs/000_TX", "outputs/001_JX", "outputs/ux", "references")

_DATA_GEN_RE = re.compile(r'lexia-genmeta[^>]*data-generated="([^"]+)"')
_NATIVE_DATE_RE = re.compile(r'<p class="footer-date">作成日：(\d{4})-(\d{1,2})-(\d{1,2})')


def build_add_date_map() -> dict[str, datetime]:
    """全 .html の初出(add)コミット日時を 1 パスで取得 (path→最古日時)。"""
    out = subprocess.run(
        ["git", "-C", str(REPO), "-c", "core.quotepath=false", "log",
         "--diff-filter=A", "--name-only", "--format=@%cI", "--", "*.html"],
        capture_output=True, text=True,
    ).stdout
    m: dict[str, datetime] = {}
    cur: datetime | None = None
    for line in out.splitlines():
        if line.startswith("@"):
            cur = datetime.fromisoformat(line[1:]).astimezone(JST)
        elif line.strip() and cur is not None:
            # log は新しい順 → 上書きで最終的に最古(初出)が残る。
            m[line.strip()] = cur
    return m


def determine_dt(rel: str, txt: str, add_map: dict[str, datetime]) -> datetime:
    # 0) TX は git 初出日時(時刻つき)を最優先（旧 native は時刻無し・改名も無いため non-follow で正確）。
    if rel.replace("\\", "/").startswith("outputs/000_TX/") and rel in add_map:
        return add_map[rel]
    # 1) genmeta の data-generated を厳密保持（JX/副産物=改名ありは --follow 由来でこちらが正確）。
    mm = _DATA_GEN_RE.search(txt)
    if mm:
        try:
            return datetime.fromisoformat(mm.group(1)).astimezone(JST)
        except ValueError:
            pass
    # 2) TX 既存(native): git 初出日時(時刻つき)、無ければ表示日付の正午。
    g = add_map.get(rel)
    if g:
        return g
    nm = _NATIVE_DATE_RE.search(txt)
    if nm:
        return datetime(int(nm[1]), int(nm[2]), int(nm[3]), 12, 0, tzinfo=JST)
    return datetime.now(JST)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    files: list[pathlib.Path] = []
    for d in DIRS:
        base = REPO / d
        if base.is_dir():
            files += sorted(base.rglob("*.html"))
    if a.limit:
        files = files[: a.limit]

    add_map = build_add_date_map()
    changed = nochange = 0
    for f in files:
        txt = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(REPO))
        dt = determine_dt(rel, txt, add_map)
        if stamp_file(str(f), dt, infer_version(rel, txt), dry_run=a.dry_run):
            changed += 1
            if a.dry_run:
                print(f"[would] {dt.strftime('%Y-%m-%d %H:%M')}  {rel}")
        else:
            nochange += 1
    print(f"\n--- {'DRY-RUN ' if a.dry_run else ''}changed={changed} nochange={nochange} total={len(files)} ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
