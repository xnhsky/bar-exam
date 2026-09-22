#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx_v15_rules.py ── §v15 DEDUP の判定式（単一情報源）。
scripts/tx-v15-dedup.py（土台・注入・検査ツール）と scripts/validate-tx-core.py G82/G83 が同じ式を使う
（「直したのに ERROR」「ERROR は出ないのに欠けている」を構造的に起こさない）。"""
from __future__ import annotations

import html as _html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "canonical" / "GENESIS-CARD.html"
CSS_BEGIN = "/* TX-DGM:BEGIN"
CSS_END = "/* TX-DGM:END */"

TRAP_LABEL = "⚠️ 間違いやすいポイント"
MATRIX_CELL_CLS = {"is-ok", "is-ng", "is-acc", "is-flat"}
MATRIX_MAX = 4
ALLOWED_INLINE_TAGS = {"strong", "em", "b", "a", "span"}

# 罠・比較表・フック・転用に置いてはならない語（一問一答カードとしての自己完結＋解答技術の排除）
FORBIDDEN = [
    (r"記述\s*[0-9０-９アイウエオ]", "記述N の参照"),
    (r"肢\s*[0-9０-９アイウエオ]", "肢N の参照"),
    (r"本問", "「本問」"),
    (r"上記", "「上記」"),
    (r"[①-⑩]", "丸数字"),
    (r"[A-EＡ-Ｅ]\s*説", "A説ラベル"),
    (r"見解\s*[ⅠⅡⅢⅣⅤ]", "見解Ⅰ ラベル"),
    (r"素直に", "解答技術語「素直に」"),
    (r"疑いすぎ", "解答技術語「疑いすぎ」"),
    (r"組合せ問題", "解答技術語「組合せ問題」"),
    (r"思い込みの罠", "解答技術語「思い込みの罠」"),
    (r"先入観", "解答技術語「先入観」"),
    (r"[ひ引]っかけの型", "解答技術語「ひっかけの型」"),
]

# 解答技術語（罠枠・フック・転用に置かない＝§v15。G83 はこの部分集合を WARNING で見る）
ANSWER_TECHNIQUE_WORDS = ("素直に", "疑いすぎ", "組合せ問題", "思い込みの罠", "先入観", "ひっかけの型", "引っかけの型")
# 解法ナビ副題の帰結語（括弧内に出たら解答前の正解露出の疑い＝G19 WARNING）
NAV_VERDICT_WORDS = ("削除", "裁量", "も対象", "対象外", "できる", "できない", "不要", "必要", "成立", "不成立",
                     "有効", "無効", "義務", "認められる", "認められない", "不存在", "起点")
CARD_TEXT_LIMIT = 2200       # カード本文（空白除く・BASIS の折りたたみ内を除く）の目安（§v14 ストーリー型 GIST 込み）
DUP_SENTENCE_MIN = 30        # 同一文検出の最小長（空白・タグ除去後）

# ---------------------------------------------------------------- 低レベル
def read(path: Path) -> tuple[str, str]:
    raw = path.read_bytes().decode("utf-8")
    if "\r\n" in raw and raw.count("\r\n") == raw.count("\n"):
        return raw.replace("\r\n", "\n"), "\r\n"
    return raw, "\n"


def write(path: Path, text: str, nl: str) -> None:
    path.write_bytes((text.replace("\n", nl) if nl != "\n" else text).encode("utf-8"))


def strip_tags(s: str) -> str:
    return _html.unescape(re.sub(r"<[^>]+>", "", s))


def block_end(s: str, start: int) -> int:
    """start（`<div` の位置）から div の入れ子を数えて閉じ `</div>` の直後の位置を返す。"""
    depth = 0
    for m in re.finditer(r"<div\b|</div>", s[start:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            return start + m.end()
    raise ValueError("div の閉じが見つからない")


def cards(s: str) -> list[tuple[str, int, int]]:
    out = []
    for m in re.finditer(r'<article class="tx-inline-card" data-stmt="([^"]+)"[^>]*>', s):
        en = s.index("</article>", m.end())
        out.append((m.group(1), m.start(), en))
    return out


def row_span(s: str, n: str) -> tuple[int, int] | None:
    m = re.search(rf'<tr[^>]*\bdata-stmt="{re.escape(n)}"[^>]*>.*?</tr>', s, re.S)
    return (m.start(), m.end()) if m else None


def region(text: str) -> tuple[int, int] | None:
    i = text.find(CSS_BEGIN)
    if i < 0:
        return None
    j = text.find(CSS_END, i)
    return None if j < 0 else (i, j + len(CSS_END))


def canonical_css() -> str:
    s = CANONICAL.read_bytes().decode("utf-8").replace("\r\n", "\n")
    r = region(s)
    if r is None:
        raise SystemExit(f"正典 {CANONICAL} に TX-DGM 区画が無い")
    return s[r[0]:r[1]]


# ---------------------------------------------------------------- 比較表
def render_matrix(did: str, m: dict) -> str:
    cols = list(m["cols"])
    n = len(cols)
    cells = "".join(f'<p class="dgm-cell is-head">{c}</p>' for c in cols)
    for row in m["rows"]:
        head, rest = row[0], row[1:]
        cells += f'<p class="dgm-cell is-rowhead">{head}</p>'
        for cell in rest:
            t, cls = (cell[0], cell[1]) if isinstance(cell, list) else (cell, None)
            cells += f'<p class="dgm-cell {cls}">{t}</p>' if cls else f'<p class="dgm-cell">{t}</p>'
    return (f'<div class="tx-dgm is-matrix" data-dgm="{did}"><span class="tx-dgm-tag">📐 比較表</span>'
            f'<p class="tx-dgm-title">{m["title"]}</p><div class="tx-dgm-matrix is-c{n}">{cells}</div></div>')


def validate_matrix(m: dict, where: str) -> list[str]:
    errs = []
    cols = m.get("cols") or []
    rows = m.get("rows") or []
    if not (2 <= len(cols) <= MATRIX_MAX):
        errs.append(f"{where}: 列数 {len(cols)}（2〜{MATRIX_MAX}）")
    if not (1 <= len(rows) <= MATRIX_MAX):
        errs.append(f"{where}: 行数 {len(rows)}（1〜{MATRIX_MAX}）")
    if not str(m.get("title", "")).strip():
        errs.append(f"{where}: title が空")
    for r in rows:
        if len(r) != len(cols):
            errs.append(f"{where}: 行「{strip_tags(str(r[0]))[:20]}」のセル数 {len(r)} ≠ 列数 {len(cols)}")
        for cell in r[1:]:
            cls = cell[1] if isinstance(cell, list) else None
            if cls is not None and cls not in MATRIX_CELL_CLS:
                errs.append(f"{where}: セル class '{cls}' は許可外（{'/'.join(sorted(MATRIX_CELL_CLS))}）")
    return errs


def text_problems(txt: str, where: str, allow_tags: set[str] = ALLOWED_INLINE_TAGS) -> list[str]:
    errs = []
    if "\n" in txt or "\r" in txt:
        errs.append(f"{where}: 改行を含む（1 行で書く）")
    for tag in re.findall(r"</?([a-zA-Z]+)", txt):
        if tag.lower() not in allow_tags:
            errs.append(f"{where}: 許可外タグ <{tag}>")
    for pat, why in FORBIDDEN:
        m = re.search(pat, strip_tags(txt))
        if m:
            errs.append(f"{where}: {why}『{m.group(0)}』")
    return errs


def render_trap(body: str, matrix_html: str) -> str:
    return (f'<div class="tx-v13-trap" data-v15="1"><span class="tx-v13-trap-label">{TRAP_LABEL}</span>'
            f'<span class="tx-v13-trap-body">{body}</span>{matrix_html}</div>')


# ---------------------------------------------------------------- check
def check_text(s: str, name: str) -> list[str]:
    errs, warns = [], []
    if 'class="tx-v13-verdict"' not in s:
        return []
    for n, st, en in cards(s):
        c = s[st:en]
        if 'class="choice-points"' in c:
            warns.append(f"記述{n}: 📌POINT が残る（base 未適用）")
        if 'class="syn-image"' in c and 'tx-gist-beat is-image' in c:
            warns.append(f"記述{n}: GIST 🖼イメージ面がフックと二重（base 未適用）")
        if re.search(r'<span class="kd-label[^"]*">[^<]*本問', c):
            warns.append(f"記述{n}: BASIS「本問への帰結」が残る（base 未適用）")
        ti = c.find('<div class="tx-v13-trap"')
        if ti < 0:
            errs.append(f"記述{n}: 罠枠が無い")
            continue
        trap = c[ti:block_end(c, ti)]
        if 'data-v15="1"' not in trap[:60]:
            warns.append(f"記述{n}: 罠枠が §v15 未適用（data-v15 なし）")
        body = re.search(r'<span class="tx-v13-trap-body[^"]*">(.*?)</span>', trap, re.S)
        for pat, why in FORBIDDEN:
            m = re.search(pat, strip_tags(body.group(1) if body else trap))
            if m:
                errs.append(f"記述{n}: 罠枠に{why}『{m.group(0)}』")
                break
        mats = re.findall(r'<div class="tx-dgm is-matrix"[^>]*>.*?</div></div>', trap, re.S)
        if len(mats) > 1:
            errs.append(f"記述{n}: 罠枠に比較表が {len(mats)} 枚（1 枚まで）")
        for mt in mats:
            heads = len(re.findall(r'dgm-cell is-head', mt))
            rows = len(re.findall(r'dgm-cell is-rowhead', mt))
            if heads > MATRIX_MAX or rows > MATRIX_MAX:
                errs.append(f"記述{n}: 比較表が {rows} 行×{heads} 列（最大 {MATRIX_MAX}×{MATRIX_MAX}）")
            for pat, why in FORBIDDEN:
                m = re.search(pat, strip_tags(mt))
                if m:
                    errs.append(f"記述{n}: 比較表に{why}『{m.group(0)}』")
                    break
            did = re.search(r'data-dgm="([^"]+)"', mt)
            sp = row_span(s, n)
            if did and sp:
                rowm = re.search(r'<div class="tx-vb-dgm-src"[^>]*>(.*)', s[sp[0]:sp[1]], re.S)
                if not rowm or re.sub(r"\s+", "", strip_tags(mt)) not in re.sub(r"\s+", "", strip_tags(rowm.group(1))):
                    errs.append(f"記述{n}: 正誤表の図解ソースがカードの比較表と一致しない（apply で同期する）")
        hook = re.search(r'<p class="syn-image"><span class="syn-tag">[^<]*</span>(.*?)</p>', c, re.S)
        if hook:
            for pat, why in FORBIDDEN:
                m = re.search(pat, strip_tags(hook.group(1)))
                if m:
                    errs.append(f"記述{n}: 記憶のフックに{why}『{m.group(0)}』")
                    break
        sp = row_span(s, n)
        if sp:
            ten = re.search(r'<span class="tx-reflex-tag">転用</span>(.*?)</p>', s[sp[0]:sp[1]], re.S)
            if ten:
                for pat, why in FORBIDDEN:
                    m = re.search(pat, strip_tags(ten.group(1)))
                    if m:
                        errs.append(f"記述{n}: 転用行に{why}『{m.group(0)}』")
                        break
    if 'class="tx-dgm is-matrix"' in s and "TX-DGM-MATRIX" not in s:
        errs.append("比較表を使っているのに TX-DGM-MATRIX CSS が無い（css で正典へそろえる）")
    return [f"ERROR {e}" for e in errs] + [f"WARN {w}" for w in warns]




def card_dedup_problems(s: str) -> list[str]:
    """G82 助言＝カード内の同一文（30 字以上の再出）と字数上限。BASIS の折りたたみ（details）内は除く。"""
    out = []
    for n, st, en in cards(s):
        c = s[st:en]
        c = re.sub(r"<details class=\"tx-basis-more\">.*?</details>", "", c, flags=re.S)
        c = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", c, flags=re.S)
        body = strip_tags(c)
        compact = re.sub(r"\s+", "", body)
        if len(compact) > CARD_TEXT_LIMIT:
            out.append(f"記述{n}: 本文 {len(compact)} 字（目安 {CARD_TEXT_LIMIT} 字）")
        seen = set()
        dups = []
        for sent in re.split(r"[。\n]", body):
            key = re.sub(r"[\s、，・（）「」『』“”\"]", "", sent)
            if len(key) < DUP_SENTENCE_MIN:
                continue
            if key in seen and key not in dups:
                dups.append(key)
            seen.add(key)
        if dups:
            out.append(f"記述{n}: 同一文の再出 {len(dups)} 件（例『{dups[0][:36]}…』）")
    return out
