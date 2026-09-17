#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一問一答カード面に残る「事例で身分を与えられた人物記号」の判定（単一情報源・2026-09-10・§v13z）。

`validate-tx-core.py` の G80（検出ゲート）と `scripts/tx-person-symbol-audit.py`（残件一覧）が
同じ式を共有する（「直したのに ERROR」「ERROR は出ないのに読めない」を構造的に起こさない）。

■ 何を弾くか
  共有事例型の `_lex` では、事例（`.tx-original-block` / `.tx-original-lead`）が
  「司法警察員X」「検察官Y」「Z医師」のように**記号へ身分を割り当てる**。この記号を
  一問一答の面（`.ox-stmt` / `.tx-inline-stmt-text` / `.syn-orig` / 正誤表の `data-brief-mark`）で
  そのまま使うと、Lexia の復習プールが 1 枚ずつバラで出したときに **誰の権限の話か分からず
  ○×を付けられない**。しかも令状の要否は主体の身分（検察官か司法警察員か医師か）で決まる
  ことが多く、記号のままだと論点そのものが消える。
  実害＝刑訴TX091_lex（「Yが検視を実施するには」「ZがVの死体を解剖するには」・実機報告 2026-09-10）。

■ 誤爆させないための限定（重要）
  人物記号一般（民法の当事者 A・B・C、刑法の甲・乙）は**対象にしない**。それらは
  「AがBに甲土地を売却し…」のように一文が事実を書き切っていれば単独カードでも読め、
  G31 でも登場人物ラベルとして許容されてきた（座談会型の例外を参照）。
  対象は **事例が身分（権限・資格）を与えた記号だけ**＝その身分が抜けると判定不能になる型に絞る。
  カード面の側で身分が添えられていれば（「司法警察員X」「作成者K」「見分者K」）通す。
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# 権限・資格が法的判定を左右する主体（この身分が抜けると命題が判定不能になる）
ROLE_WORDS = [
    "司法警察員", "司法巡査", "検察事務官", "検察官", "警察官", "警察署長", "検視官",
    "裁判官", "裁判長", "裁判所書記官", "鑑定人", "鑑定受託者", "鑑定嘱託を受けた医師",
    "医師", "歯科医師", "弁護人", "弁護士", "通訳人", "公証人", "執行官", "登記官",
    "刑務官", "看守", "保護観察官",
]
_ROLE = "(?:" + "|".join(sorted(ROLE_WORDS, key=len, reverse=True)) + ")"
ROLE_RE = re.compile(_ROLE)

# 半角・全角の大文字 1 字（前後に別のラテン文字が来ないもの）
_SYM = r"[A-ZＡ-Ｚ]"
_NOT_LATIN = r"(?![A-Za-zＡ-Ｚａ-ｚ])"
_SYM_RE = re.compile(r"(?<![A-Za-zＡ-Ｚａ-ｚ])(" + _SYM + r")" + _NOT_LATIN)

# 記号の直後に来ると「人物として使っている」ことが確かな助詞・語
_PERSON_TAIL = r"(?:が|は|を|に|の|と|へ|から|より|ら|も|方|宅|側|自身|及び|並びに|、|。|」|）|\))"
_PERSON_USE_RE = re.compile(
    r"(?<![A-Za-zＡ-Ｚａ-ｚ])(" + _SYM + r")" + _NOT_LATIN + r"(?=" + _PERSON_TAIL + r")")

# 事例側の同格（身分語＋記号／記号＋身分語）
_DEF_ROLE_FIRST_RE = re.compile("(" + _ROLE + r")(?:である|たる)?(" + _SYM + r")" + _NOT_LATIN)
_DEF_SYM_FIRST_RE = re.compile(r"(?<![A-Za-zＡ-Ｚａ-ｚ])(" + _SYM + r")(" + _ROLE + r")")

# カード面の側で記号に添えられていれば通す同格語（辞書に無い役でも拾う）
# 「作成者K」「見分者K」「立会人V」「目撃者W」…＝直前に付いた 者/官/人/員/医/長/士 終わりの名詞
_APPOS_RE = re.compile(
    r"[一-龥ぁ-んァ-ヶー]{1,8}(?:者|官|人|員|医|長|士|係|主|警察|検察)(?:である|たる)?$")

# 身分が近傍（前後）にあれば通す窓
NEAR_BEFORE = 14
NEAR_AFTER = 10


@dataclass(frozen=True)
class Hit:
    face: str      # 面の名前（記述本文／記述原文／一問一答／正誤表 原文帯）
    label: str     # data-stmt
    symbol: str    # 記号
    roles: tuple   # 事例が与えている身分
    context: str   # 人が読む前後文脈


def role_symbols(original_text: str) -> dict:
    """事例（不可侵原文エリア）が身分を与えている記号 → 身分の集合。"""
    out = {}
    for m in _DEF_ROLE_FIRST_RE.finditer(original_text):
        out.setdefault(m.group(2), set()).add(m.group(1))
    for m in _DEF_SYM_FIRST_RE.finditer(original_text):
        out.setdefault(m.group(1), set()).add(m.group(2))
    return out


def _introduced_in_face(text: str, sym: str) -> bool:
    """その面のどこかで記号に身分が添えられているか（＝面の中で紹介済み）。

    「鑑定人Bの供述の証明力を、Bが解剖時に…」のように初出で身分を書いてあれば、
    以降の同じ面での再登場は単独カードでも読める（面ごとに自己完結していればよい）。
    """
    for m in re.finditer(r"(?<![A-Za-zＡ-Ｚａ-ｚ])" + re.escape(sym) + _NOT_LATIN, text):
        before = text[max(0, m.start() - NEAR_BEFORE):m.start()]
        after = text[m.end():m.end() + NEAR_AFTER]
        if ROLE_RE.search(before) or ROLE_RE.search(after):
            return True
        if _APPOS_RE.search(before.strip()):
            return True
    return False


def _is_covered(text: str, start: int, end: int, sym: str, roles) -> bool:
    """カード面の側で身分が添えられているか（＝単独カードでも誰の話か読める）。"""
    before = text[max(0, start - NEAR_BEFORE):start]
    after = text[end:end + NEAR_AFTER]
    if any(r in before or r in after for r in roles):
        return True
    return _introduced_in_face(text, sym)


def scan_faces(faces, defined: dict):
    """faces=[(面名, ラベル, テキスト)] を走査して Hit を返す。"""
    hits = []
    if not defined:
        return hits
    for face, label, text in faces:
        if not text:
            continue
        for m in _PERSON_USE_RE.finditer(text):
            sym = m.group(1)
            roles = defined.get(sym)
            if not roles:
                continue
            if _is_covered(text, m.start(), m.end(), sym, roles):
                continue
            ctx = text[max(0, m.start() - 16):m.end() + 20]
            hits.append(Hit(face, label, sym, tuple(sorted(roles)), ctx))
    return hits
