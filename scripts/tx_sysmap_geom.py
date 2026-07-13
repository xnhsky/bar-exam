# -*- coding: utf-8 -*-
"""体系マップ（.tx-sysmap svg.tree-svg）内 <text> の幅推定とはみ出し判定（単一情報源）。

`scripts/tx-sysmap-fit.py`（決定論的な自動フィット・修正ツール）と
`scripts/validate-tx-core.py` G66（検証ゲート）／`check-tx-lex-engine.py`（push 前ゲート）が
本モジュールを共用する。ここを唯一の情報源にすることで、修正基準と検出基準がズレない。

なぜ必要か（2026-07-13）：体系マップの各カード見出し（fs 15.5・カード幅 260px 固定）は
問題ごとに AI が本文を書き換える「差替スロット」だが、見出しが長い問題では文字が
カード枠・viewBox 右端をはみ出して切れる事故が corpus 全体で 19 ファイル/45 見出しに発生
（実害：刑TX382 記述5「収得後知情行使は通貨のみ（152）」が viewBox 右端で切断）。
SVG の <text> は自動改行・自動縮小しないため、fit ツールが textLength+lengthAdjust で
「はみ出す見出しだけ」をカード内へ収まる実効幅へ圧縮する（本文改変なし・冪等）。

幅モデル：全角＝1.0em／半角英数記号≈0.58em の保守的（やや大きめ）推定。textLength 指定済みは
実効幅＝textLength。tspan の font-size を尊重（有形偽造 等の 18px 見出し混在に対応）。
"""
from __future__ import annotations

import re
import unicodedata

# 幅モデル（fit ツールと検証ゲートで共通・ズレ厳禁）
CJK_EM = 1.0            # 全角（漢字・かな・全角約物）
HALF_EM = 0.58         # 半角英数・記号（やや大きめ＝安全側）
# east_asian_width が Narrow/Halfwidth を返すが視覚的に全角相当で扱いたい約物
_FULLWIDTH_PUNCT = set("「」（）｛｝【】《》〔〕『』〈〉…—―・、。！？：；〜～")

# カード本体とみなす rect の最小幅（帯・バッジ・アクセントバー・小チップを除外）
MIN_CARD_W = 120.0
CARD_PAD = 8.0         # カード内側の右余白
VB_PAD = 6.0           # viewBox 端の余白


def char_em(ch: str) -> float:
    if ch in _FULLWIDTH_PUNCT:
        return CJK_EM
    return CJK_EM if unicodedata.east_asian_width(ch) in ("W", "F", "A") else HALF_EM


def _runs(text_el, default_fs):
    """<text> を (文字列, font-size) の run 列へ分解（tspan の font-size を尊重）。"""
    runs = []
    for node in text_el.children:
        name = getattr(node, "name", None)
        if name is None:  # NavigableString
            s = str(node)
            if s.strip():
                runs.append((s, default_fs))
        elif name == "tspan":
            try:
                fs = float(node.get("font-size", default_fs))
            except (TypeError, ValueError):
                fs = default_fs
            s = node.get_text()
            if s.strip():
                runs.append((s, fs))
        else:
            s = node.get_text() if hasattr(node, "get_text") else ""
            if s.strip():
                runs.append((s, default_fs))
    if not runs:
        s = text_el.get_text()
        if s.strip():
            runs.append((s, default_fs))
    return runs


def natural_width(text_el, default_fs: float) -> float:
    """<text> の自然な描画幅（px）を推定。"""
    return sum(char_em(c) * fs for s, fs in _runs(text_el, default_fs) for c in s)


def font_size_of(text_el, fallback: float = 15.0) -> float:
    try:
        return float(text_el.get("font-size", fallback))
    except (TypeError, ValueError):
        return fallback


def _parse_translate(t: str):
    if not t:
        return (0.0, 0.0)
    m = re.search(r"translate\(\s*(-?[\d.]+)[,\s]+(-?[\d.]+)\s*\)", t)
    return (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)


def abs_translate(el):
    """先祖 <g> の translate を合算した絶対オフセット。"""
    tx, ty = 0.0, 0.0
    cur = el.parent
    while cur is not None and getattr(cur, "name", None) == "g":
        ax, ay = _parse_translate(cur.get("transform", ""))
        tx += ax
        ty += ay
        cur = cur.parent
    return tx, ty


def viewbox_w(svg):
    vb = (svg.get("viewbox") or svg.get("viewBox") or "").split()
    if len(vb) != 4:
        return None
    try:
        return float(vb[2])
    except ValueError:
        return None


def _card_bounds(text_el):
    """text が属する最寄り <g> のカード本体 rect（最大幅・MIN_CARD_W 以上）の絶対 x 範囲。"""
    g = text_el.parent
    if g is None or getattr(g, "name", None) != "g":
        return None
    rects = g.find_all("rect", recursive=False)
    if not rects:
        return None
    def _w(r):
        try:
            return float(r.get("width", 0) or 0)
        except (TypeError, ValueError):
            return 0.0
    best = max(rects, key=_w)
    w = _w(best)
    if w < MIN_CARD_W:
        return None
    try:
        x = float(best.get("x", 0))
    except (TypeError, ValueError):
        return None
    tx, _ = abs_translate(best)
    return (x + tx, x + tx + w)


def iter_text_overflow(svg, min_fs: float = 0.0):
    """sysmap svg 内の各 <text> について幾何・はみ出し量を yield（dict）。

    キー：
      el           : <text> 要素
      content      : テキスト全文
      fs           : font-size
      anchor       : text-anchor（start/middle/end）
      natural_w    : 自然描画幅（推定 px）
      effective_w  : 実効幅（textLength 指定済みならその値／未指定なら natural_w）
      has_textlength : textLength 指定済みか
      ax, x0, x1   : 実効の絶対 x（開始・終端）
      card         : 属するカードの絶対 x 範囲 (l, r) または None
      vbw          : viewBox 幅
      vb_over      : viewBox 端（余白込）を超える px（0=収まる）
      card_over    : カード枠（余白込）を超える px（0=収まる）
      maxw         : anchor を考慮した「収まる実効幅」の上限（fit の textLength 目標）
    """
    vbw = viewbox_w(svg)
    for t in svg.find_all("text"):
        content = t.get_text()
        if not content.strip():
            continue
        fs = font_size_of(t)
        if fs < min_fs:
            continue
        anchor = (t.get("text-anchor") or "start").strip()
        tx, _ = abs_translate(t)
        try:
            ax = float(t.get("x", 0) or 0) + tx
        except (TypeError, ValueError):
            continue
        nat = natural_width(t, fs)
        tl = t.get("textlength") or t.get("textLength")
        try:
            eff = float(tl) if tl else nat
        except ValueError:
            eff = nat
        if anchor == "middle":
            x0, x1 = ax - eff / 2, ax + eff / 2
        elif anchor == "end":
            x0, x1 = ax - eff, ax
        else:
            x0, x1 = ax, ax + eff
        # 許容左右端（カード ∩ viewBox・余白込）
        left_lim = VB_PAD
        right_lim = (vbw - VB_PAD) if vbw is not None else None
        card = _card_bounds(t)
        if card:
            left_lim = max(left_lim, card[0] + CARD_PAD)
            r = card[1] - CARD_PAD
            right_lim = min(right_lim, r) if right_lim is not None else r
        # はみ出し量は「実際の枠線／viewBox 端を越えた px」で測る（内側余白ではなく可視の境界）。
        # 余白（PAD）は maxw＝fit 目標（枠内に少し余裕を残す）側にのみ使う。
        vb_over = 0.0
        if vbw is not None:
            vb_over = max(x1 - vbw, 0.0 - x0, 0.0)
        card_over = 0.0
        if card:
            card_over = max(x1 - card[1], card[0] - x0, 0.0)
        if right_lim is None:
            maxw = eff
        elif anchor == "middle":
            maxw = 2 * min(ax - left_lim, right_lim - ax)
        elif anchor == "end":
            maxw = ax - left_lim
        else:
            maxw = right_lim - ax
        yield {
            "el": t, "content": content, "fs": fs, "anchor": anchor,
            "natural_w": nat, "effective_w": eff, "has_textlength": bool(tl),
            "ax": ax, "x0": x0, "x1": x1, "card": card, "vbw": vbw,
            "vb_over": vb_over, "card_over": card_over, "maxw": maxw,
        }


def find_sysmap_svgs(soup):
    """検証対象の体系マップ SVG（.tx-sysmap 内 tree-svg）を列挙。"""
    return soup.select(".tx-sysmap svg.tree-svg")
