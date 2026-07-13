#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""体系マップ（.tx-sysmap svg.tree-svg）の見出し文字はみ出しを恒久修正する決定論ツール。

体系マップの各カード見出しは「問題ごとに AI が書き換える差替スロット」だが、カード幅（260px）と
viewBox（幅1500）は固定のため、長い見出しの問題では文字がカード枠・viewBox 右端をはみ出して
切れる（実害：刑TX382 記述5「収得後知情行使は通貨のみ（152）」）。SVG の <text> は自動改行・
自動縮小しないので、本ツールが **はみ出す <text> だけ** に `textLength`（収まる実効幅）＋
`lengthAdjust="spacingAndGlyphs"` を付与して字間・字形を圧縮し、カード内へ収める。

設計方針（bar-exam の「決定論的 recanon」哲学）：
  - 本文改変ゼロ：テキスト内容は 1 文字も変えない。付与するのは textLength/lengthAdjust の 2 属性だけ。
  - 冪等：既に収まっている見出しは触らない。2 回目以降は無変更。
  - 生テキスト編集：BeautifulSoup で対象 <text> を特定し、生 HTML 側を対象タグだけ書き換える
    （全文シリアライズによる無関係な差分・エンティティ化を避ける）。
  - 単一情報源：はみ出し判定は scripts/tx_sysmap_geom.py を共用（validate-tx-core G66 と同基準）。

使い方：
  python scripts/tx-sysmap-fit.py <file...>            # 指定ファイルを修正（書き込み）
  python scripts/tx-sysmap-fit.py --check <file...>    # 検出のみ（書き込みなし・exit 1 で残存を通知）
  python scripts/tx-sysmap-fit.py --all                # outputs/ux/000_TX 配下の *_lex.html 全件
  python scripts/tx-sysmap-fit.py --all --check
要件：pip install beautifulsoup4
"""
from __future__ import annotations

import glob
import os
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tx_sysmap_geom as geom  # noqa: E402

# はみ出しとみなす閾値（実際の枠線／viewBox 端を越えた px で判定）：
#   viewBox 端は 0.5px でも切れるので厳格。カード枠線は 2px を超えて越えたものだけ収める
#   （枠内 1px の微小接触＝視覚的に無害なサブタイトル等は触らず、差分を最小化）。
VB_TOL = 0.5
CARD_TOL = 2.0
MIN_TEXTLENGTH = 40.0  # これ未満へ圧縮が必要＝レイアウト異常。触らず報告のみ。


def _needs_fit(info) -> bool:
    return info["vb_over"] > VB_TOL or info["card_over"] > CARD_TOL


def _rewrite_tag(html: str, info) -> tuple[str, bool, str]:
    """生 HTML 中の対象 <text> 開始タグに textLength/lengthAdjust を付与（または更新）。"""
    t = info["el"]
    content = info["content"]
    x_raw = t.get("x")
    y_raw = t.get("y")
    fs_raw = t.get("font-size")
    tl = int(info["maxw"])
    if tl < MIN_TEXTLENGTH:
        return html, False, f"maxw={tl}px が小さすぎ（要レイアウト調整）: 「{content[:24]}」"

    # <text ...>content</text> を全走査し、x/y/font-size が一致する一意な要素を特定。
    esc = re.escape(content)
    matches = []
    for m in re.finditer(r"<text\b([^>]*)>(.*?)</text>", html, re.DOTALL):
        if m.group(2) != content:
            continue
        attrs = m.group(1)
        if x_raw is not None and f'x="{x_raw}"' not in attrs:
            continue
        if y_raw is not None and f'y="{y_raw}"' not in attrs:
            continue
        if fs_raw is not None and f'font-size="{fs_raw}"' not in attrs:
            continue
        matches.append(m)
    if len(matches) != 1:
        return html, False, (
            f"生HTMLで一意特定できず（{len(matches)}件マッチ）スキップ: 「{content[:24]}」"
        )
    m = matches[0]
    attrs = m.group(1)
    if "textLength=" in attrs or "textlength=" in attrs:
        new_attrs = re.sub(r'\s*(?:textLength|textlength)="[^"]*"', "", attrs)
        new_attrs = re.sub(r'\s*(?:lengthAdjust|lengthadjust)="[^"]*"', "", new_attrs)
    else:
        new_attrs = attrs
    new_open = f'<text{new_attrs} textLength="{tl}" lengthAdjust="spacingAndGlyphs">'
    new_el = new_open + m.group(2) + "</text>"
    html = html[: m.start()] + new_el + html[m.end():]
    return html, True, f"textLength={tl}px（自然{info['natural_w']:.0f}px）: 「{content[:24]}」"


def process_file(path: str, check_only: bool):
    html = open(path, encoding="utf-8").read()
    soup = BeautifulSoup(html, "html.parser")
    svgs = geom.find_sysmap_svgs(soup)
    if not svgs:
        return 0, 0, []
    # 対象（はみ出し）を収集。1 svg 想定だが複数でも可。
    todo = []
    for svg in svgs:
        for info in geom.iter_text_overflow(svg):
            if _needs_fit(info):
                todo.append(info)
    if not todo:
        return 0, 0, []
    logs = []
    fixed = 0
    if check_only:
        for info in todo:
            where = []
            if info["vb_over"] > VB_TOL:
                where.append(f"viewBox+{info['vb_over']:.0f}px")
            if info["card_over"] > CARD_TOL:
                where.append(f"カード枠+{info['card_over']:.0f}px")
            logs.append(f"  [未修正] {' '.join(where)}: 「{info['content'][:28]}」")
        return len(todo), 0, logs
    # 修正は「後ろの要素から」適用するとオフセットずれが無い。生 HTML 位置で降順に。
    # ただし _rewrite_tag は毎回 html を再走査するので順序非依存。安全のため 1 件ずつ再パースはせず、
    # content+x+y+fs で一意特定しているため連続適用で相互干渉しない。
    for info in todo:
        html, ok, msg = _rewrite_tag(html, info)
        logs.append(("  [修正] " if ok else "  [SKIP] ") + msg)
        if ok:
            fixed += 1
    if fixed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    return len(todo), fixed, logs


def main():
    args = sys.argv[1:]
    check_only = "--check" in args
    do_all = "--all" in args
    files = [a for a in args if not a.startswith("--")]
    if do_all:
        files = sorted(glob.glob("outputs/ux/000_TX/**/*_lex.html", recursive=True))
    if not files:
        print("使い方: python scripts/tx-sysmap-fit.py [--check] [--all] <file...>")
        return 2
    total_hits = 0
    total_fixed = 0
    touched = []
    for path in files:
        hits, fixed, logs = process_file(path, check_only)
        if hits:
            total_hits += hits
            total_fixed += fixed
            if fixed or check_only:
                touched.append(path)
            print(f"\n### {path}  (はみ出し {hits} 件 / 修正 {fixed} 件)")
            for ln in logs:
                print(ln)
    print(
        f"\n==== 走査 {len(files)} ファイル / はみ出し見出し {total_hits} 件 / "
        f"{'検出のみ' if check_only else f'修正 {total_fixed} 件（{len(touched)} ファイル書換）'} ===="
    )
    if check_only and total_hits:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
