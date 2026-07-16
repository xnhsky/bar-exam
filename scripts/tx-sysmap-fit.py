#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""体系マップ（.tx-sysmap svg.tree-svg）の見出し文字の「はみ出し」と「重なり」を恒久修正する決定論ツール。

体系マップの各カード見出しは「問題ごとに AI が書き換える差替スロット」だが、カード幅（260px）と
viewBox（幅1500）は固定のため、長い見出しの問題では文字がカード枠・viewBox 右端をはみ出して
切れる（実害：刑TX382 記述5「収得後知情行使は通貨のみ（152）」）。SVG の <text> は自動改行・
自動縮小しないので、本ツールが **はみ出す <text> だけ** に `textLength`（収まる実効幅）＋
`lengthAdjust="spacingAndGlyphs"` を付与して字間・字形を圧縮し、カード内へ収める。

さらに（2026-07-16・LEX395）親ツリー（L1 カード）の見出し帯で、見出し fs18（x=-198）と
サブ見出し fs16（x=-120）を **<text> 2本の固定 x 並置** で書いた問題では、見出しが約 78px を
超えると2本目に文字が重なる（刑TX395_lex「職務の適法性」×「要件・現在性」ほか 10 ファイル/16 件）。
正典形は v13k-bis／pbox 正典の **1 <text>＋<tspan>（中央寄せ）** なので、本ツールが衝突を含む
sysmap の見出し帯 2 本組を正典形へマージする（同じ svg 内の非衝突ペアも併せて統一＝行の意匠一貫）。

設計方針（bar-exam の「決定論的 recanon」哲学）：
  - 本文改変ゼロ：テキスト内容は 1 文字も変えない（マージは正典どおり全角スペース1個で連結するだけ）。
  - 冪等：既に収まっている見出し・正典形の見出し帯は触らない。2 回目以降は無変更。
  - 生テキスト編集＋CRLF 保存：BeautifulSoup で対象 <text> を特定し、生 HTML 側を対象タグだけ
    書き換える（全文シリアライズによる無関係な差分・エンティティ化・改行コード変換を避ける）。
  - 単一情報源：判定は scripts/tx_sysmap_geom.py を共用（validate-tx-core G66/G69 と同基準）。

使い方：
  python scripts/tx-sysmap-fit.py <file...>            # 指定ファイルを修正（書き込み）
  python scripts/tx-sysmap-fit.py --check <file...>    # 検出のみ（書き込みなし・exit 1 で残存を通知）
  python scripts/tx-sysmap-fit.py --all                # ux の *_lex.html ＋公式 000_TX の全 HTML
  python scripts/tx-sysmap-fit.py --all --check
要件：pip install beautifulsoup4
"""
from __future__ import annotations

import glob
import io
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


def _find_text_tag(html: str, info):
    """生 HTML 中で info の <text> を一意特定して Match を返す（特定不能なら (None, 理由)）。

    content＋x/y/font-size 属性の一致で同定する。<tspan> 入り <text> はタグを剥いだ
    テキストで比較する（マージ済み見出し帯にも textLength を付けられるように）。
    """
    t = info["el"]
    content = info["content"]
    x_raw = t.get("x")
    y_raw = t.get("y")
    fs_raw = t.get("font-size")
    matches = []
    for m in re.finditer(r"<text\b([^>]*)>(.*?)</text>", html, re.DOTALL):
        inner = m.group(2)
        if inner != content and re.sub(r"<[^>]+>", "", inner) != content:
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
        return None, f"生HTMLで一意特定できず（{len(matches)}件マッチ）"
    return matches[0], ""


def _rewrite_tag(html: str, info) -> tuple[str, bool, str]:
    """生 HTML 中の対象 <text> 開始タグに textLength/lengthAdjust を付与（または更新）。"""
    content = info["content"]
    tl = int(info["maxw"])
    if tl < MIN_TEXTLENGTH:
        return html, False, f"maxw={tl}px が小さすぎ（要レイアウト調整）: 「{content[:24]}」"

    m, why = _find_text_tag(html, info)
    if m is None:
        return html, False, f"{why}スキップ: 「{content[:24]}」"
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


def _fmt_num(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else f"{v:.1f}"


def _merge_header_pair(html: str, pair) -> tuple[str, bool, str]:
    """見出し帯の <text> 2本組を正典形（1 <text>＋<tspan>・中央寄せ）へマージする。

    正典形（v13k-bis `tx-lex-sysmap-center.py` merge_pair／`tx-lex-sysmap-pbox.py` 正典ブロックと
    バイト同形）：
      <text x="{帯中央}" y="{y}" text-anchor="middle" fill="{fill}" font-weight="700"
            font-size="16"><tspan font-weight="800" font-size="18">{見出し}</tspan>　{サブ見出し}</text>
    """
    title, sub = pair["title"], pair["sub"]
    band = pair["band"]
    mt, why_t = _find_text_tag(html, title)
    ms, why_s = _find_text_tag(html, sub)
    if mt is None or ms is None:
        return html, False, (f"{why_t or why_s}スキップ: "
                             f"「{title['content'][:16]}」＋「{sub['content'][:16]}」")
    first, second = (mt, ms) if mt.start() < ms.start() else (ms, mt)
    if second.start() < first.end():
        return html, False, f"タグ位置が交差（想定外）スキップ: 「{title['content'][:16]}」"
    between = html[first.end():second.start()]
    if between.strip():
        return html, False, (f"見出し2本が隣接せずスキップ（間に要素あり）: "
                             f"「{title['content'][:16]}」＋「{sub['content'][:16]}」")
    cx = _fmt_num(band["x"] + band["w"] / 2.0)
    y_raw = title["el"].get("y") or _fmt_num(title.get("ly", 23))
    fill = sub["el"].get("fill") or title["el"].get("fill") or "#fff"
    merged = (f'<text x="{cx}" y="{y_raw}" text-anchor="middle" fill="{fill}" '
              f'font-weight="700" font-size="16">'
              f'<tspan font-weight="800" font-size="18">{mt.group(2)}</tspan>'
              f'　{ms.group(2)}</text>')
    html = html[: first.start()] + merged + html[second.end():]
    return html, True, (f"正典形へ統合: 「{title['content'][:16]}」＋「{sub['content'][:16]}」")


def _fix_collisions(html: str, soup) -> tuple[str, int, list[str]]:
    """pass 1：同一行の <text> 重なり（G69）を修復する。

    衝突を含む sysmap では、見出し帯の 2 本組（iter_header_pairs）を **衝突の有無に関わらず全て**
    正典形へマージする（親ツリー1行の中で中央寄せ・左寄せが混在しないように）。見出し帯以外の
    衝突（未対応パターン）は報告のみ（validate-tx-core G69 が ERROR/WARNING で捕捉し続ける）。
    """
    logs: list[str] = []
    merged = 0
    for svg in geom.find_sysmap_svgs(soup):
        collisions = list(geom.iter_text_collisions(svg))
        if not collisions:
            continue
        pairs = list(geom.iter_header_pairs(svg))
        pair_ids = {id(p["title"]["el"]) for p in pairs} | {id(p["sub"]["el"]) for p in pairs}
        for c in collisions:
            if id(c["a"]["el"]) not in pair_ids and id(c["b"]["el"]) not in pair_ids:
                logs.append(f"  [SKIP] 見出し帯以外の重なり（手動調整が必要・{c['overlap']:.0f}px）: "
                            f"「{c['a']['content'][:16]}」×「{c['b']['content'][:16]}」")
        for p in pairs:
            html, ok, msg = _merge_header_pair(html, p)
            logs.append(("  [統合] " if ok else "  [SKIP] ") + msg)
            if ok:
                merged += 1
    return html, merged, logs


def process_file(path: str, check_only: bool):
    with io.open(path, encoding="utf-8", newline="") as f:
        raw = f.read()
    crlf = "\r\n" in raw
    html = raw.replace("\r\n", "\n") if crlf else raw
    orig_html = html
    soup = BeautifulSoup(html, "html.parser")
    svgs = geom.find_sysmap_svgs(soup)
    if not svgs:
        return 0, 0, []
    logs: list[str] = []
    hits = 0
    fixed = 0

    # ── pass 1：同一行の <text> 重なり（親ツリー見出し帯の2本並置事故・G69）
    collisions = [c for svg in svgs for c in geom.iter_text_collisions(svg)]
    if collisions:
        hits += len(collisions)
        if check_only:
            for c in collisions:
                logs.append(f"  [未修正] 同一行の重なり {c['overlap']:.0f}px: "
                            f"「{c['a']['content'][:16]}」×「{c['b']['content'][:16]}」")
        else:
            html, _merged, mlogs = _fix_collisions(html, soup)
            logs.extend(mlogs)
            # マージ後の実測で解消数を数える（正典形マージが衝突を残していないかの自己検算）
            soup = BeautifulSoup(html, "html.parser")
            svgs = geom.find_sysmap_svgs(soup)
            remain = sum(1 for svg in svgs for _ in geom.iter_text_collisions(svg))
            fixed += len(collisions) - remain
            if remain:
                logs.append(f"  [残存] 重なり {remain} 件が未解消（validate-tx-core G69 で確認）")

    # ── pass 2：カード枠・viewBox 端のはみ出し（G66）
    todo = []
    for svg in svgs:
        for info in geom.iter_text_overflow(svg):
            if _needs_fit(info):
                todo.append(info)
    hits += len(todo)
    if check_only:
        for info in todo:
            where = []
            if info["vb_over"] > VB_TOL:
                where.append(f"viewBox+{info['vb_over']:.0f}px")
            if info["card_over"] > CARD_TOL:
                where.append(f"カード枠+{info['card_over']:.0f}px")
            logs.append(f"  [未修正] {' '.join(where)}: 「{info['content'][:28]}」")
        return hits, 0, logs
    # 修正は content+x+y+fs で一意特定するため連続適用で相互干渉しない。
    for info in todo:
        html, ok, msg = _rewrite_tag(html, info)
        logs.append(("  [修正] " if ok else "  [SKIP] ") + msg)
        if ok:
            fixed += 1
    if html != orig_html:
        out = html.replace("\n", "\r\n") if crlf else html
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(out)
    return hits, fixed, logs


def main():
    args = sys.argv[1:]
    check_only = "--check" in args
    do_all = "--all" in args
    files = [a for a in args if not a.startswith("--")]
    if do_all:
        files = sorted(glob.glob("outputs/ux/000_TX/**/*_lex.html", recursive=True))
        # 公式（本物5択）も sysmap を共有するため対象に含める（sysmap 無しは即スキップ）
        files += sorted(glob.glob("outputs/000_TX/**/*.html", recursive=True))
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
            print(f"\n### {path}  (はみ出し・重なり {hits} 件 / 修正 {fixed} 件)")
            for ln in logs:
                print(ln)
    print(
        f"\n==== 走査 {len(files)} ファイル / はみ出し・重なり {total_hits} 件 / "
        f"{'検出のみ' if check_only else f'修正 {total_fixed} 件（{len(touched)} ファイル書換）'} ===="
    )
    if check_only and total_hits:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
