#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""outputs 配下の全 TX HTML のフッター feature-tag を
『生成バージョン 1 タグのみ（hidden）』に正規化する。

ユーザー指示（2026-05-30）:
  - フッターには「どのバージョンで生成したか」の最新の版だけを残す
  - 他の feature-tag（spoiler-safe / palette / role 等）は全削除
  - 形式: <p class="footer-meta-hidden" hidden>
            <span class="feature-tag" hidden>VERSION</span>
          </p>
  - outputs 配下の全ファイルに適用
"""
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"

# footer-spec 内の feature-tag を抱える <p> を丸ごと捕捉
#   legacy:  <p class="footer-meta"> ... </p>
#   v10   :  <p class="footer-meta-hidden" hidden=""> ... </p>
P_BLOCK = re.compile(
    r'<p class="footer-meta(?:-hidden)?"[^>]*>.*?</p>',
    re.DOTALL,
)
P_FIRST_TAG = re.compile(r'<span class="feature-tag"[^>]*>([^<]*)</span>')


def normalize_version(raw: str) -> str:
    t = raw.strip()
    if "v10.0.0 GOLD-SKELETON" in t:
        return "TX v10.0.0 GOLD-SKELETON"
    if "v8.11.7" in t:
        return "TX v8.11.7"
    # それ以外は先頭の "TX vX.Y.Z" 部分を抽出、無ければそのまま
    m = re.match(r"(TX\s+v[\d.]+(?:\s+\S+)?)", t)
    return m.group(1).strip() if m else t


def process(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    m = P_BLOCK.search(html)
    if not m:
        return f"SKIP (footer-meta block 不検出): {path.name}"
    block = m.group(0)
    tags = P_FIRST_TAG.findall(block)
    if not tags:
        return f"SKIP (feature-tag なし): {path.name}"
    version = normalize_version(tags[0])
    new_block = (
        '<p class="footer-meta-hidden" hidden="">\n'
        f'      <span class="feature-tag" hidden="">{version}</span>\n'
        '    </p>'
    )
    if block == new_block:
        return f"OK (変更なし): {path.name} [{version}]"
    html2 = html[:m.start()] + new_block + html[m.end():]
    path.write_text(html2, encoding="utf-8")
    return f"UPDATED: {path.name}  {len(tags)}タグ → 1 [{version}]"


def main():
    files = sorted(OUT.rglob("*.html"))
    print(f"対象: {len(files)} ファイル\n")
    for f in files:
        print("  " + process(f))


if __name__ == "__main__":
    main()
