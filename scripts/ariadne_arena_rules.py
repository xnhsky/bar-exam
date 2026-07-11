#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ARIADNE v1.4.0 ARENA-PURE 共有ルール（単一情報源）。

原則：**arena（`data-arena="1"`＝Lexia SM-2 復習プール対象）に載せてよいのは、
当該問題の法的実体知識（規範・要件・判別基準・判例の射程・条文）だけ。**
科目共通の答案方法論・受験技術（体系順・4点セット・評価語・構成予測・重い罪先行・
配点重心・実益薄論点の切捨て 等）はプールに載せない（2026-07-11 監査で
74ファイル×平均6枚が同一命題でプールへ流れていた実害の恒久対策）。

- 作法エリア（`.bc-wrap`）のドリルは data-arena を付けない＝ページ内確認専用。
- 解法ナビ各手のドリルは data-arena 必須のまま、下記 METHOD_RE 該当を禁止。

利用側（同一 dir から import）:
  - scripts/validate-ariadne.py  … A40（per-file ERROR）
  - scripts/check-ariadne-quiz-dedup.py … corpus 横断ゲート
  - scripts/ariadne-arena-pure.py … 既存ファイル一括是正（v1.3.0→v1.4.0）
"""
import re

# 科目共通の答案方法論（arena 禁止）を設問文で検出するパターン。
# 追加時は必ず実データ（全 ARIADNE の quiz-question）で
# 法的実体ドリルへの誤爆が無いことを確認してから足すこと。
METHOD_PATTERNS = [
    r'構成要件該当性\s*→\s*違法性\s*→\s*責任',      # 体系順そのもの
    r'[4４四]点セット',                              # 問規当結の呼称
    r'評価語を添え|評価語と結合',                    # あてはめ作法
    r'問題の所在.{0,10}規範.{0,14}あてはめ.{0,10}結論',  # 問規当結の列挙
    r'構成順を予測|書き出す前に.{0,12}(第一|構成)',  # 書き始めの作法
    r'答案の軸を据える',                             # 順序戦術（bc 由来）
    r'筆力を集中|紙幅',                              # 配点重心・分量配分
    r'どの立場に立っても結論が変わらない論点',       # 実益薄論点の切捨て
    r'規範を立てず',                                 # 規範先出しの作法
    r'答案は増やすより削る|論点を増やすゲーム',      # 締めの作法
    r'(段階|要件)は一言で(通|認定|素通)',            # 体系順の変形（素通し作法）
    r'争いのない要件は(端的|一言)',                  # 同上
    r'厚く論じるほど高評価|同じ分量で厚く論じ',      # 分量配分の作法
]
METHOD_RE = re.compile('|'.join(METHOD_PATTERNS))


def is_method_question(text: str) -> bool:
    """設問文が「科目共通の答案方法論」（arena 禁止）に該当するか。"""
    return bool(METHOD_RE.search(text or ''))


def norm_question(text: str) -> str:
    """corpus 横断の重複判定用の設問正規化（空白・句読点・括弧類を除去）。"""
    return re.sub(r'[\s　、。「」『』（）()・,．.]', '', text or '')
