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

`.tx-basis-honbun` は入れ子 div を持たない（corpus 5,882 箇所で実証）ため、生テキストの
非貪欲マッチで厳密に切り出せる。判定・修復ともタグの属性だけを触り、本文テキストは変えない。
"""
from __future__ import annotations

import re
from dataclasses import dataclass

ITEM_RE = re.compile(r'<div[^>]*class="(tx-basis-item[^"]*)"[^>]*>')
HONBUN_RE = re.compile(r'<div class="tx-basis-honbun">(.*?)</div>', re.S)
P_RE = re.compile(r'<p(\s+class="([^"]*)")?\s*>')
HANG_BODY_RE = re.compile(r'<span class="hang-body([^"]*)"')
HEAD_RE = re.compile(r'<div class="tx-basis-head">(.*?)</div>', re.S)


@dataclass(frozen=True)
class Issue:
    kind: str          # 'A' | 'B' | 'C'
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
        for pm in P_RE.finditer(inner):
            p_classes = pm.group(2) or ""
            # 段落の範囲（次の <p 直前まで／末尾まで）を粗く取り、judgment-text の有無を見る
            nxt = P_RE.search(inner, pm.end())
            seg = inner[pm.start(): nxt.start() if nxt else len(inner)]
            has_j = "judgment-text" in seg

            if kind == "case" and not has_j:
                hb = HANG_BODY_RE.search(seg)
                if hb:
                    span = (inner_off + pm.start() + hb.start(1), inner_off + pm.start() + hb.end(1))
                    issues.append(Issue("A", f"判例カードの判旨に判旨フォント未割当（{head}）",
                                        span, hb.group(1) + " judgment-text"))
                else:
                    cls = (p_classes + " judgment-text").strip()
                    span = (inner_off + pm.start(), inner_off + pm.end())
                    issues.append(Issue("A", f"判例カードの判旨に判旨フォント未割当（{head}）",
                                        span, f'<p class="{cls}">'))

            elif kind == "statute" and "judgment-text" in p_classes:
                new_cls = " ".join(owner.group(1).split() + ["is-case"])
                span = (owner.start(1), owner.end(1))
                iss = Issue("B", f"判旨本文なのにカード種別が条文（{head}）", span, new_cls)
                if iss not in issues:
                    issues.append(iss)

            elif kind == "theory" and "judgment-text" in p_classes:
                rest = " ".join(c for c in p_classes.split() if c != "judgment-text")
                span = (inner_off + pm.start(), inner_off + pm.end())
                new_p = f'<p class="{rest}">' if rest else "<p>"
                issues.append(Issue("C", f"学説カードの本文に判旨フォント（{head}）", span, new_p))

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
