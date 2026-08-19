#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BASIS カード種別 ⇄ 本文の役割フォント割当ての判定（単一情報源・2026-08-17・LEX-441）。

`scripts/tx-basis-role-fix.py`（修復）と `validate-tx-core.py` G77（検出ゲート）が
同じ式を共有する（「直したのに ERROR」「ERROR は出ないのに崩れている」を構造的に起こさない）。

規約（v13 LOOP-CARD）:
  - 判例アイテム `.tx-basis-item.is-case` の判旨本文は `judgment-text`（＝`--font-judgment`）を持つ。
  - 学説アイテム `.tx-basis-item.is-theory` の本文は `judgment-text` を持たない（判旨ではない）。
  - 種別なし（条文枠）のアイテムに `<p class="judgment-text">` があるのは、中身が判旨なのに
    カード種別が条文になっている取り違え（枠色・見出し色まで条文で出る）。
  - 種別なし（条文枠）のアイテムの `<span class="para-num">判旨</span>` 段落は判旨であり、
    `judgment-text` を持つ。段落が全て判旨のカードは判例カード（`is-case`）である。

`.tx-basis-honbun` は入れ子 div を持たない（corpus 5,882 箇所で実証）ため、生テキストの
非貪欲マッチで厳密に切り出せる。判定・修復ともタグの属性だけを触り、本文テキストは変えない。

【2026-08-19・LEX-442 で修正した 2 つの検出穴】
  1. 旧 `P_RE` は `<p class="...">` の直後が `>` で終わる形しか拾わず、
     `<p class="judgment-text" data-hyakusen="刑訴百選34">` のような**属性が続く段落を全て素通り**
     していた（corpus 実測 67 段落／27 ファイル）。実害＝刑訴TX126（判旨 2 枚が条文枠のブルーで
     出るのに G77 は 0 件）。→ 属性を許す正規表現へ。
  2. 「判旨なのに `judgment-text` も種別も無い」**二重欠落**（型 D）は、A（判例カードの欠落）にも
     B（judgment-text からの逆算）にも掛からず設計上検出できなかった（corpus 実測 24 件／10 ファイル）。
     実害＝刑訴TX324（判旨 5 枚が条文枠＋答案書体）。→ `para-num` が「判旨」の段落を判旨と見て検査する。
"""
from __future__ import annotations

import re
from dataclasses import dataclass

ITEM_RE = re.compile(r'<div[^>]*class="(tx-basis-item[^"]*)"[^>]*>')
HONBUN_RE = re.compile(r'<div class="tx-basis-honbun">(.*?)</div>', re.S)
# 属性が続く <p ...> も拾う（旧実装は class="..." の直後が > の形しか拾えなかった）
P_RE = re.compile(r'<p\b([^>]*)>')
P_CLASS_RE = re.compile(r'class="([^"]*)"')
HANG_BODY_RE = re.compile(r'<span class="hang-body([^"]*)"')
HEAD_RE = re.compile(r'<div class="tx-basis-head">(.*?)</div>', re.S)
PARA_NUM_RE = re.compile(r'<span class="para-num">([^<]*)</span>')


@dataclass(frozen=True)
class Issue:
    kind: str          # 'A' | 'B' | 'C' | 'D'
    detail: str        # 人が読む説明
    span: tuple        # 生テキスト上の置換範囲
    replacement: str   # 置換後の文字列


def _item_kind(classes: str) -> str:
    if "is-case" in classes:
        return "case"
    if "is-theory" in classes:
        return "theory"
    return "statute"


def _head_text(raw: str, start: int, end: int) -> str:
    m = HEAD_RE.search(raw, start, end)
    if not m:
        return ""
    return re.sub(r"<[^>]+>", "", m.group(1)).strip()[:44]


def _paragraphs(inner: str):
    """honbun 内の段落を (開始, 終了, class 文字列, 段落テキスト範囲) で列挙する。"""
    ps = list(P_RE.finditer(inner))
    for i, pm in enumerate(ps):
        end = ps[i + 1].start() if i + 1 < len(ps) else len(inner)
        cm = P_CLASS_RE.search(pm.group(1))
        yield pm, inner[pm.start():end], (cm.group(1) if cm else "")


def _is_judgment_para(seg: str) -> bool:
    m = PARA_NUM_RE.search(seg)
    return bool(m and m.group(1).strip().startswith("判旨"))


def _add_judgment(inner_off: int, pm, seg: str, p_classes: str, kind_label: str, head: str) -> Issue:
    """段落へ judgment-text を足す Issue を作る（hang-body 優先＝正例 刑訴TX302_lex の形）。"""
    hb = HANG_BODY_RE.search(seg)
    if hb:
        span = (inner_off + pm.start() + hb.start(1), inner_off + pm.start() + hb.end(1))
        return Issue(kind_label, f"判旨に判旨フォント未割当（{head}）", span, hb.group(1) + " judgment-text")
    cls = (p_classes + " judgment-text").strip()
    attrs = pm.group(1)
    new_attrs = P_CLASS_RE.sub(f'class="{cls}"', attrs, count=1) if p_classes else f' class="{cls}"' + attrs
    span = (inner_off + pm.start(), inner_off + pm.end())
    return Issue(kind_label, f"判旨に判旨フォント未割当（{head}）", span, f"<p{new_attrs}>")


def find_issues(raw: str) -> list[Issue]:
    """種別と本文の役割フォントが食い違う箇所を列挙する（生テキストの置換範囲つき）。"""
    items = list(ITEM_RE.finditer(raw))
    if not items:
        return []
    issues: list[Issue] = []
    for hon in HONBUN_RE.finditer(raw):
        owner = None
        for it in items:
            if it.start() < hon.start():
                owner = it
            else:
                break
        if owner is None:
            continue
        kind = _item_kind(owner.group(1))
        inner = hon.group(1)
        inner_off = hon.start(1)
        head = _head_text(raw, owner.end(), hon.start())

        paras = list(_paragraphs(inner))
        judgment_like = []
        for pm, seg, p_classes in paras:
            has_j = "judgment-text" in seg
            is_j = _is_judgment_para(seg)
            judgment_like.append(has_j or is_j)

            if kind == "case" and not has_j:
                issues.append(_add_judgment(inner_off, pm, seg, p_classes, "A",
                                            f"判例カードの{head}"))

            elif kind != "case" and is_j and not has_j:
                issues.append(_add_judgment(inner_off, pm, seg, p_classes, "D",
                                            f"種別なしカードの{head}"))

            elif kind == "theory" and has_j and not is_j:
                rest = " ".join(c for c in p_classes.split() if c != "judgment-text")
                attrs = pm.group(1)
                new_attrs = (P_CLASS_RE.sub(f'class="{rest}"', attrs, count=1) if rest
                             else P_CLASS_RE.sub("", attrs, count=1).rstrip())
                span = (inner_off + pm.start(), inner_off + pm.end())
                issues.append(Issue("C", f"学説カードの本文に判旨フォント（{head}）",
                                    span, f"<p{new_attrs}>"))

        # 段落が全て判旨のカードは判例カード（種別なし＝条文枠で出ているのが取り違え）
        if kind == "statute" and paras and all(judgment_like):
            new_cls = " ".join(owner.group(1).split() + ["is-case"])
            span = (owner.start(1), owner.end(1))
            iss = Issue("B", f"判旨本文なのにカード種別が条文（{head}）", span, new_cls)
            if iss not in issues:
                issues.append(iss)

    return issues


def apply_fixes(raw: str, issues: list[Issue]) -> tuple[str, list[Issue]]:
    """後ろから置換して生テキストを更新する（重複範囲は 1 回だけ適用）。"""
    applied: list[Issue] = []
    seen: set[tuple] = set()
    for iss in sorted(issues, key=lambda i: i.span[0], reverse=True):
        if iss.span in seen:
            applied.append(iss)
            continue
        seen.add(iss.span)
        raw = raw[: iss.span[0]] + iss.replacement + raw[iss.span[1]:]
        applied.append(iss)
    return raw, applied
