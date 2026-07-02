#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX _lex クロスファイル「使い回し（機械的な流し込み）」ディテクタ。

展開・バッチで各問を作るとき、体系マップ／ANSWER／5点フロー／記憶フック／マトリクス／
物語解説などの「問題固有の作り込み要素」が、別問題からの丸コピー（＝機械的な流し込み）に
なっていないかを、複数ファイル横断で検出する。

単体の validate-tx-core / check-lexia-book-quality は 1 ファイル内検査、
check-duplicates は本文バイト完全一致のみ。本スクリプトは「作り込み要素だけを取り出して
ファイル間で照合」する（条文原文＝正当に共有・エンジン導出チップ＝同条文で同一 は除外）。

判定:
  [REUSE-EXACT] 作り込み要素の本文が別ファイルと正規化後に完全一致 → ERROR（exit 1）。
                問題固有のはずの文が別問題と同一＝流し込みの確定痕跡。
  [REUSE-NEAR]  別ファイル間で文字 8-gram Jaccard 類似度が高い（既定 .58）→ WARNING。
                言い換えコピーの疑い。人手レビューへ回す。

使い方:
  python scripts/check-tx-reuse.py outputs/ux/000_TX/001_刑法/刑TX361_lex.html outputs/ux/000_TX/001_刑法/刑TX360_lex.html
  python scripts/check-tx-reuse.py outputs/ux/000_TX            # ディレクトリ配下の *_lex.html を総当たり
  オプション: --near-threshold 0.6 / --no-near / --min-len 16
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 が必要です。pip install beautifulsoup4", file=sys.stderr)
    sys.exit(2)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 作り込み（問題固有）要素＝ファイル間で同一なら流し込み。
AUTHORED_SELECTORS = [
    (".tx-answer-box .tx-answer-body", "ANSWER"),
    (".tx-article-flow .tx-flow-body", "5点フロー"),
    (".tx-onepoint .tx-op-body", "記憶フック"),
    (".tx-matrix-body", "マトリクス本文"),
    (".tx-matrix-verdict", "判断式"),
    (".tx-sysmap-title", "体系マップ題名"),
    (".tx-sysmap-lead", "体系マップ・リード"),
    (".tx-sysmap-name", "体系マップ・ノード名"),
    (".tx-sysmap-branch", "体系マップ・分岐"),
    (".tx-sysmap-scope", "体系マップ・行説明"),
    (".tx-sysmap-graft", "体系マップ・擬制"),
    (".fa-narrative-body", "物語解説"),
    (".tx-detail-panel p", "詳説"),
]
# 除外＝正当に共有されうる（条文原文・エンジン導出チップ・SM2 ミラー）。
#  - tx-mini-law-text/body : 条文原文（同条文なら同一が正しい）
#  - tx-mini-law-heading/theme : エンジンが条番号から導出（同条文で同一が正しい）
#  - ox-pool / tx-reflex : 同一ファイル内の flow ミラー（cross は flow 側で拾える）

_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")
_LABEL = re.compile(r"^(判断式|文言|趣旨|射程|切断点|転用|詳説)")


def norm(node) -> str:
    t = node.get_text(" ", strip=True) if node is not None else ""
    t = _WS.sub("", t)
    t = _LABEL.sub("", t)
    return t


def discover(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        pp = Path(p)
        if pp.is_file() and pp.name.endswith("_lex.html"):
            out.append(pp)
        elif pp.is_dir():
            out.extend(pp.rglob("*_lex.html"))
    return sorted(set(out))


def shingles(s: str, k: int = 8) -> set[str]:
    if len(s) < k:
        return {s}
    return {s[i:i + k] for i in range(len(s) - k + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / (len(a) + len(b) - inter)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--min-len", type=int, default=16, help="照合対象にする最小文字数（既定16）")
    ap.add_argument("--near-threshold", type=float, default=0.58, help="近似重複の Jaccard しきい値（既定0.58）")
    ap.add_argument("--no-near", action="store_true", help="近似重複検査を省略")
    args = ap.parse_args()

    files = discover(args.paths)
    files = [f for f in files if ".tx-inline-card" in f.read_text(encoding="utf-8", errors="ignore")]
    if len(files) < 2:
        print(f"対象 TX _lex が {len(files)} 件（2件未満）＝クロス照合不要。")
        return 0

    # file -> {kind: [normalized strings]}
    per_file: dict[str, list[tuple[str, str]]] = {}
    for f in files:
        soup = BeautifulSoup(f.read_text(encoding="utf-8", errors="ignore"), "html.parser")
        seen: set[str] = set()
        items: list[tuple[str, str]] = []
        for sel, kind in AUTHORED_SELECTORS:
            for node in soup.select(sel):
                t = norm(node)
                if len(t) < args.min_len or t in seen:
                    continue
                seen.add(t)
                items.append((t, kind))
        per_file[f.name] = items

    names = list(per_file.keys())

    # --- EXACT cross-file reuse ---
    owner: dict[str, list[str]] = {}
    kind_of: dict[str, str] = {}
    for name in names:
        for t, kind in per_file[name]:
            owner.setdefault(t, [])
            if name not in owner[t]:
                owner[t].append(name)
            kind_of[t] = kind
    exact = [(t, fs) for t, fs in owner.items() if len(fs) >= 2]
    exact.sort(key=lambda x: (-len(x[1]), -len(x[0])))

    # --- NEAR cross-file reuse（exact を除く）---
    near: list[tuple[float, str, str, str, str, str]] = []
    if not args.no_near:
        exact_set = {t for t, _ in exact}
        pool: list[tuple[str, str, str, set[str]]] = []  # (name, kind, text, shingles)
        for name in names:
            for t, kind in per_file[name]:
                if t in exact_set or len(t) < max(args.min_len, 20):
                    continue
                pool.append((name, kind, t, shingles(t)))
        for i in range(len(pool)):
            n1, k1, t1, s1 = pool[i]
            for j in range(i + 1, len(pool)):
                n2, k2, t2, s2 = pool[j]
                if n1 == n2:
                    continue
                sim = jaccard(s1, s2)
                if sim >= args.near_threshold:
                    near.append((sim, n1, n2, k1, t1, t2))
        near.sort(key=lambda x: -x[0])

    # --- report ---
    print("=" * 60)
    print(f"TX 使い回し検査: {len(files)} ファイル / 作り込み要素を横断照合")
    print("=" * 60)
    if exact:
        print(f"\n[REUSE-EXACT] 別ファイルと本文完全一致＝流し込み確定 ({len(exact)} 件):")
        for t, fs in exact[:40]:
            disp = t if len(t) <= 60 else t[:57] + "…"
            print(f"  ❌ 〔{kind_of[t]}〕{', '.join(fs)}\n       「{disp}」")
    else:
        print("\n[REUSE-EXACT] 完全一致の使い回し なし ✅")

    if not args.no_near:
        if near:
            print(f"\n[REUSE-NEAR] 近似（言い換えコピー疑い・Jaccard≥{args.near_threshold}） ({len(near)} 対):")
            for sim, n1, n2, kind, t1, t2 in near[:25]:
                d1 = t1 if len(t1) <= 48 else t1[:45] + "…"
                d2 = t2 if len(t2) <= 48 else t2[:45] + "…"
                print(f"  ⚠ {sim:.2f} 〔{kind}〕{n1} ↔ {n2}\n       「{d1}」\n       「{d2}」")
        else:
            print(f"\n[REUSE-NEAR] 近似重複（≥{args.near_threshold}） なし ✅")

    print("\n" + "=" * 60)
    if exact:
        print(f"❌ FAIL — 流し込み（完全一致 {len(exact)} 件）を作り直してください。")
        return 1
    if near:
        print(f"⚠ WARN — 近似 {len(near)} 対は人手レビューで流し込みでないか確認（exit 0）。")
        return 0
    print("✅ 使い回し・流し込みは見つかりませんでした。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
