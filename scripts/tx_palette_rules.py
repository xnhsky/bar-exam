#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX 難易度帯パレット規律の単一情報源（2026-07-21・LEX-403）。

正答率帯（P1≥60% / P2 40-60% / P3<40%）→ 11 名前付きパレットの対応と、
§5 宣言コメント・palette :root ブロックの機械抽出ヘルパを一元管理する。
利用者:
  - scripts/validate-tx-core.py  G71（既定パレットのまま＝未選定）/ G72（宣言と帯・実hexの整合）
  - scripts/check-tx-lex-engine.py  push 前ゲート（G71/G72 組込み）
  - scripts/tx-lex-repaint-palette.py  既存ファイルの帯別一括再選定（決定論・冪等）

背景（実害）: 2026-07-21 監査で _lex 483 本中 216 本が歴代正典の既定パレットのまま
（GENESIS-CARD #A8666E ×148 / GENESIS #A07895 ×47 / GENESIS-CORE #8E6E9A ×21）で
出荷されていた。生成時の Phase 4a（HEAD :root 配色 V3 適用）がスキップされても
G6/G7（変数の存在検査）は正典複製で必ず PASS するため、どのゲートにも掛からなかった。
パレット hex の正典 memory/reference_palette_v3.md も参照先に無かった（本コミットで復旧）。
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_JSON = Path(__file__).resolve().parent / "tx-palette-templates.json"

# --- 帯 → パレット（CLAUDE.md §3-4・new-tx.md Phase 1-3/1-4 と同一） ---
BAND_PALETTES = {
    "P1": ["Sweet Berry", "Fresh Citrus", "Rose Mist", "Antique Pearl", "Maison Blanche"],
    "P2": ["Crystal Blue", "Dusty Sage", "Mint Tea", "Fresh Mint"],
    "P3": ["Twilight Violet", "Sunset Harmony"],
}
PALETTE_BAND = {name: band for band, names in BAND_PALETTES.items() for name in names}

# corpus で実際に使われている palette ID（§5 コメント表記）。
# 出典 PDF（docs/palette-v3_2.pdf）のスター番号と Rose Mist だけ食い違う
# （PDF=01 / corpus=03）が、判定は名前で行うので ID は情報表示のみ。
PALETTE_IDS = {
    "Rose Mist": "03", "Mint Tea": "02", "Fresh Mint": "04", "Sweet Berry": "05",
    "Crystal Blue": "06", "Antique Pearl": "09", "Twilight Violet": "10",
    "Sunset Harmony": "11", "Maison Blanche": "12", "Fresh Citrus": "13", "Dusty Sage": "14",
}

# 歴代正典の既定 --accent（＝パレット未選定の徴表。ただし
# #A07895=Antique Pearl 正規 accent / #8E6E9A=Twilight Violet 正規 accent と衝突するため、
# 「未選定」の確定は §5 宣言の不在とブロックのバイト一致で行うこと）
DEFAULT_ACCENTS = {
    "#A8666E": "GENESIS-CARD",   # v13 既定（dusty rose・どのパレットの正規 accent でもない）
    "#A07895": "GENESIS",        # v10 既定（Antique Pearl 派生）
    "#8E6E9A": "GENESIS-CORE",   # v12 既定（Twilight Violet 派生）
}

# 一括再選定（repaint）の帯内ローテーション。テンプレは corpus 実証済みの
# 逐語ブロックがあるパレットのみ（Mint Tea / Fresh Mint は corpus 未使用のため除外。
# Antique Pearl は v10 既定と同一 hex で「未選定と見分けが付かない」ため rotation からも除外）。
# P3 は Twilight Violet 一本（2026-07-21 実機フィードバック・LEX-403 追補）：Sunset Harmony は
# accent #9A5C76 がピンク寄りモーブで旧既定 dusty rose #A8666E とほぼ見分けが付かず、
# 「難問＝紫」の帯シグナルにならない（刑TX409 実機報告）。SH は §3-4 の表上は P3 合法のまま
# （手動宣言は G72 を通る）が、自動選定では使わない。
REPAINT_ROTATION = {
    "P1": ["Sweet Berry", "Rose Mist", "Fresh Citrus", "Maison Blanche"],
    "P2": ["Crystal Blue", "Dusty Sage"],
    "P3": ["Twilight Violet"],
}

# §5 宣言コメント（palette 選定の宣言）。既定配色/baseline を含むものは「未選定」。
DECL_RE = re.compile(
    r"/\*\s*===\s*§5 V3 (P[123]) ([A-Za-z][A-Za-z ]*?)\s*\(palette ID:\s*(\d+)\)\s*─([^*]*?)===",
    re.S,
)
# フッター/ヘッダーの正答率（公式・_lex 共通の実表記）
RATE_RE = re.compile(r"正答率\s*(\d{1,3})\s*[%％]\s*／\s*難度")
ACCENT_RE = re.compile(r"--accent:\s*(#[0-9A-Fa-f]{6})")
ROOT_BLOCK_RE = re.compile(r":root\s*\{[^}]*\}", re.S)


def band_of(rate: int | None) -> str | None:
    if rate is None:
        return None
    return "P1" if rate >= 60 else ("P2" if rate >= 40 else "P3")


def extract_rate(html: str) -> int | None:
    m = RATE_RE.search(html)
    return int(m.group(1)) if m else None


def find_declarations(html: str):
    """§5 宣言を全件返す（baseline/既定配色も含む）。
    各要素: dict(band, name, pid, desc, baseline, start, end)"""
    out = []
    for m in DECL_RE.finditer(html):
        desc = m.group(4)
        out.append({
            "band": m.group(1),
            "name": m.group(2).strip(),
            "pid": m.group(3),
            "desc": desc,
            "baseline": ("既定配色" in desc) or ("baseline" in desc),
            "start": m.start(),
            "end": m.end(),
        })
    return out


def last_selected_declaration(html: str):
    """最後の非 baseline 宣言（＝選定の宣言）。無ければ None。"""
    decls = [d for d in find_declarations(html) if not d["baseline"]]
    return decls[-1] if decls else None


def palette_root_blocks(html: str):
    """--accent: を含む :root ブロックを文書順に (start, end, text) で返す
    （block#2 と、移行ツールの末尾上書き＝cascade 勝ちブロックの双方を拾う）。"""
    out = []
    for m in ROOT_BLOCK_RE.finditer(html):
        if "--accent:" in m.group(0):
            out.append((m.start(), m.end(), m.group(0)))
    return out


def effective_accent(html: str) -> str | None:
    """CSS カスケードの実効 --accent（最後の定義が勝つ）。"""
    hits = ACCENT_RE.findall(html)
    return hits[-1].upper() if hits else None


@lru_cache(maxsize=1)
def canonical_default_blocks() -> dict:
    """歴代正典の palette :root（block#2）のバイト正文。{canonical名: block文字列}"""
    out = {}
    for name in ("GENESIS.html", "GENESIS-CORE.html", "GENESIS-CARD.html"):
        p = ROOT / "canonical" / name
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        blocks = palette_root_blocks(text)
        if blocks:
            out[name] = blocks[0][2]
    return out


@lru_cache(maxsize=1)
def load_templates() -> dict:
    """corpus 実証済みの逐語テンプレ（palette 名→ dict(band, palette_id, b2, b3, source)）。"""
    if not TEMPLATES_JSON.exists():
        return {}
    return json.loads(TEMPLATES_JSON.read_text(encoding="utf-8"))


def template_accent(name: str) -> str | None:
    t = load_templates().get(name)
    if not t:
        return None
    m = ACCENT_RE.search(t["b2"])
    return m.group(1).upper() if m else None
