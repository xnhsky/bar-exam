# -*- coding: utf-8 -*-
"""THE GIST ストーリー型（TX-GIST-STORY・§v14）の単一情報源。

旧 THE GIST（`<p class="syn-lead">`）は「結論→体系的位置づけ→専門用語→例え→当否」を 1 段落に
詰めていた。ストーリー型は同じ中身を役割ごとの面へ割る（2026-09-17・刑訴TX100 試作→ユーザー承認）：

  <div class="syn-lead tx-gist">
    💡 THE GIST タグ
    ① .tx-gist-head（○×マーク＋結論一文）
    ② .tx-gist-where（🧭 現在地＝問題の段階トラック 2〜4 段のうち今の段＋この記述の問い）
    ③ .tx-gist-story（🎬場面 → ❓問題 → ⚖判例・条文 → 🔍理由 の 4 段）
    ④ .tx-gist-terms（📘 キーワード 1〜3 語＝定義を本文から外す）
    ⑤ p.tx-gist-beat.is-image（🖼 イメージ＝🗝記憶のフックと同じ像）
    ⑥ .tx-gist-judge（判定＝記述のどこが判例と合う／ずれるか）

ここに置くもの（検出ゲートと書き換えツールが同じ式を使う＝「直したのに ERROR」を構造的に起こさない）：
  - render_card()      … JSON 仕様 → HTML（1 行）。書き換えツール scripts/tx-gist-story.py が使う
  - extract_cards()    … 生成済み HTML → JSON 仕様（往復テスト・後日の手直し用）
  - structure_problems() … bs4 の .syn-lead.tx-gist 要素を検査（validate-tx-core G81 が使う）
  - CSS 区画の正典抽出・注入（canonical/GENESIS-CARD.html の TX-GIST-STORY:BEGIN〜END が唯一の原本）
"""
from __future__ import annotations

import json
import re
from pathlib import Path

CSS_BEGIN = "/* TX-GIST-STORY:BEGIN"
CSS_END = "/* TX-GIST-STORY:END */"

# answer のラベルは「判例・条文」＝条文だけで答えが出るカード（令状不要の特則・通信傍受法の通知など）もあるため
# （2026-09-17 展開時に「⚖ 判例」固定では条文カードで内容と食い違うと判明して改名）。
BEATS = (("scene", "🎬 場面"), ("issue", "❓ 問題"), ("answer", "⚖ 判例・条文"), ("why", "🔍 理由"))
TRACK_MIN, TRACK_MAX = 2, 4
TERMS_MIN, TERMS_MAX = 1, 3
MARKS = {"○": "is-o", "×": "is-x"}
VERDICT_TO_MARK = {"o": "○", "x": "×"}
# 本文フィールドで許すインラインタグ（段落・ブロック要素は構造を壊すので不可）
ALLOWED_TAGS = {"strong", "b", "em", "a"}
# §v15（2026-09-22）：image は任意（空＝🖼 面を出さない）ので必須フィールドから外す
# ＝レンダラ（空なら面を出さない）・構造検査（is-image が無くても ERROR にしない）と規律をそろえる。
TEXT_FIELDS = ("head", "question", "scene", "issue", "answer", "why", "judge")

REPO = Path(__file__).resolve().parent.parent
CANONICAL = REPO / "canonical" / "GENESIS-CARD.html"


# ---------------------------------------------------------------- render
def _lab(cls: str, text: str) -> str:
    return f'<span class="tx-gist-lab {cls}">{text}</span>'


def render_card(card: dict, track: list[str]) -> str:
    """1 カード分の THE GIST（改行を含まない 1 行の HTML）。"""
    mark = card["mark"]
    mk = MARKS[mark]
    now = int(card["now"])
    steps = "".join(
        f'<span class="tx-gist-step{" is-now" if i == now else ""}">{t}</span>' for i, t in enumerate(track))
    beats = "".join(
        f'<p class="tx-gist-beat is-{k}">{_lab("is-" + k, lab)}<span class="tx-gist-body">{card[k]}</span></p>'
        for k, lab in BEATS)
    terms = "".join(
        f'<div class="tx-gist-term"><dt><span>{t}</span></dt><dd>{d}</dd></div>' for t, d in card["terms"])
    verdict = "○ 正しい" if mark == "○" else "× 誤り"
    return (
        '<div class="syn-lead tx-gist"><span class="syn-tag">💡 THE GIST</span>'
        f'<p class="tx-gist-head {mk}"><span class="tx-gist-mark">{mark}</span>'
        f'<span class="tx-gist-head-body">{card["head"]}</span></p>'
        f'<div class="tx-gist-where"><p class="tx-gist-map">{_lab("is-where", "🧭 現在地")}'
        f'<span class="tx-gist-track">{steps}</span></p>'
        f'<p class="tx-gist-q"><span class="tx-gist-q-lab">この記述の問い</span>'
        f'<span class="tx-gist-body">{card["question"]}</span></p></div>'
        f'<div class="tx-gist-story">{beats}</div>'
        f'<div class="tx-gist-terms"><span class="tx-gist-terms-lab">📘 キーワード</span><dl>{terms}</dl></div>'
        + ((f'<p class="tx-gist-beat is-image">{_lab("is-image", "🖼 イメージ")}'
            f'<span class="tx-gist-body">{card["image"]}</span></p>') if (card.get("image") or "").strip() else "")
        + f'<p class="tx-gist-judge {mk}">{_lab("is-judge " + mk, verdict)}'
        + f'<span class="tx-gist-body">{card["judge"]}</span></p>'
        + '</div>'
    )


# ---------------------------------------------------------------- spec checks
_TAG_RE = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>")


def markup_problems(value: str, allow_tags: bool = True) -> list[str]:
    """本文 1 フィールドの形式：1 行・許可タグのみ・タグの開閉がそろう（開きっぱなしの strong は
    ブラウザでカード外まで太字が漏れる＝2026-09-17 レビュー指摘）。"""
    out = []
    if "\n" in value or "\r" in value:
        out.append("改行がある（1 行で書く）")
    tags = list(_TAG_RE.finditer(value))
    if tags and not allow_tags:
        out.append("タグは使えない（語・段階ラベルは素のテキスト）")
        return out
    bad = sorted({m.group(1).lower() for m in tags} - ALLOWED_TAGS)
    if bad:
        out.append(f"使えないタグ {bad}（許可＝{sorted(ALLOWED_TAGS)}）")
    stack = []
    for m in tags:
        name = m.group(1).lower()
        if m.group(0).startswith("</"):
            if not stack or stack[-1] != name:
                out.append(f"タグの閉じ方がそろわない（</{name}>）")
                break
            stack.pop()
        elif not m.group(0).endswith("/>"):
            stack.append(name)
    else:
        if stack:
            out.append(f"閉じていないタグ {stack}")
    return out


def spec_problems(card: dict, track: list[str], label: str) -> list[str]:
    """JSON 仕様 1 カードの形式検査（内容の正しさは執筆者の自己照合が担う）。"""
    out = []
    if card.get("mark") not in MARKS:
        out.append(f"記述{label}: mark は ○ か × にする（{card.get('mark')!r}）")
    try:
        now = int(card.get("now"))
        if not 0 <= now < len(track):
            out.append(f"記述{label}: now={now} が track（{len(track)} 段）の範囲外")
    except (TypeError, ValueError):
        out.append(f"記述{label}: now は track の添字（0 始まりの整数）")
    for k in TEXT_FIELDS:
        v = card.get(k)
        if not isinstance(v, str) or not re.sub(r"<[^>]+>", "", v).strip():
            out.append(f"記述{label}: {k} が空")
            continue
        out += [f"記述{label}: {k}：{x}" for x in markup_problems(v)]
    img = card.get("image")
    if img is not None and not isinstance(img, str):
        out.append(f"記述{label}: image は文字列（空文字＝🖼 面を出さない）")
    elif isinstance(img, str) and re.sub(r"<[^>]+>", "", img).strip():
        out += [f"記述{label}: image：{x}" for x in markup_problems(img)]
    terms = card.get("terms")
    if not isinstance(terms, list) or not TERMS_MIN <= len(terms) <= TERMS_MAX:
        out.append(f"記述{label}: terms は {TERMS_MIN}〜{TERMS_MAX} 語の [語, 定義] 配列")
    else:
        for t in terms:
            if not (isinstance(t, list) and len(t) == 2 and all(isinstance(x, str) and x.strip() for x in t)):
                out.append(f"記述{label}: terms の要素は [語, 定義]（{t!r}）")
                continue
            out += [f"記述{label}: terms の語「{t[0]}」：{x}" for x in markup_problems(t[0], allow_tags=False)]
            out += [f"記述{label}: terms「{t[0]}」の定義：{x}" for x in markup_problems(t[1])]
    return out


def track_problems(track) -> list[str]:
    if not (isinstance(track, list) and TRACK_MIN <= len(track) <= TRACK_MAX
            and all(isinstance(t, str) and t.strip() for t in track)):
        return [f"track は {TRACK_MIN}〜{TRACK_MAX} 段の文字列配列"]
    return [f"track「{t}」：{x}" for t in track for x in markup_problems(t, allow_tags=False)]


# ---------------------------------------------------------------- 判例引用（新規持ち込みの検知）
_ERA = {"明治": "明", "大正": "大", "昭和": "昭", "平成": "平", "令和": "令"}
_CITE_RE = re.compile(
    r"[判決]\s*(明治|大正|昭和|平成|令和|明|大|昭|平|令)\s*(元|\d{1,2})\s*[.．年]\s*(\d{1,2})\s*[.．月]\s*(\d{1,2})")


def citations(text: str) -> set[tuple[str, int, int, int]]:
    """「最決昭55.10.23」「最高裁昭和55年10月23日決定」の前半等を (元号, 年, 月, 日) に正規化して集める。
    判/決 の直後に日付が来る形だけを拾う（施行日・法律番号の日付を判例と誤認しない）。"""
    plain = re.sub(r"<[^>]+>", "", text)
    out = set()
    for m in _CITE_RE.finditer(plain):
        era = _ERA.get(m.group(1), m.group(1))
        year = 1 if m.group(2) == "元" else int(m.group(2))
        out.add((era, year, int(m.group(3)), int(m.group(4))))
    return out


def format_citation(c: tuple[str, int, int, int]) -> str:
    return f"{c[0]}{c[1]}.{c[2]}.{c[3]}"


# ---------------------------------------------------------------- extract (往復)
def extract_card(fragment: str) -> dict:
    def grab(pat):
        m = re.search(pat, fragment, re.S)
        return m.group(1) if m else ""
    card = {
        "mark": grab(r'<span class="tx-gist-mark">(.*?)</span>'),
        "head": grab(r'<span class="tx-gist-head-body">(.*?)</span></p>'),
        "question": grab(r'<span class="tx-gist-q-lab">この記述の問い</span><span class="tx-gist-body">(.*?)</span></p>'),
    }
    steps = re.findall(r'<span class="tx-gist-step( is-now)?">(.*?)</span>', fragment)
    card["now"] = next((i for i, (n, _) in enumerate(steps) if n), -1)
    for k, _ in BEATS + (("image", ""),):
        card[k] = grab(rf'<p class="tx-gist-beat is-{k}"><span class="tx-gist-lab is-{k}">[^<]*</span>'
                       rf'<span class="tx-gist-body">(.*?)</span></p>')
    card["terms"] = [[t, d] for t, d in re.findall(
        r'<div class="tx-gist-term"><dt><span>(.*?)</span></dt><dd>(.*?)</dd></div>', fragment)]
    card["judge"] = grab(r'<p class="tx-gist-judge [^"]*"><span class="tx-gist-lab [^"]*">[^<]*</span>'
                         r'<span class="tx-gist-body">(.*?)</span></p>')
    return card, [t for _, t in steps]


# ---------------------------------------------------------------- structure (G81)
def structure_problems(lead, verdict: str | None) -> tuple[list[str], tuple[str, ...]]:
    """bs4 Tag（.syn-lead.tx-gist）の構造検査。戻り値＝(問題文の配列, 段階トラックのラベル列)。
    verdict は正誤表 tr[data-verdict] の 'o'/'x'（無ければ None＝極性照合を省略）。"""
    out: list[str] = []

    def body_text(el):
        return el.get_text(" ", strip=True) if el is not None else ""

    head = lead.select_one(":scope > p.tx-gist-head")
    mark_el = head.select_one(".tx-gist-mark") if head is not None else None
    mark = body_text(mark_el)
    if head is None or mark not in MARKS:
        out.append("結論（.tx-gist-head の ○×マーク）が無い")
    else:
        if MARKS[mark] not in (head.get("class") or []):
            out.append(f"結論のマーク {mark} と見出しの class が食い違う")
        if not body_text(head.select_one(".tx-gist-head-body")):
            out.append("結論の一文が空")
        if verdict in VERDICT_TO_MARK and VERDICT_TO_MARK[verdict] != mark:
            out.append(f"結論のマーク {mark} が正誤表の正解（{VERDICT_TO_MARK[verdict]}）と逆")

    steps = lead.select(":scope > .tx-gist-where .tx-gist-track > .tx-gist-step")
    track = tuple(body_text(s) for s in steps)
    if not TRACK_MIN <= len(steps) <= TRACK_MAX:
        out.append(f"🧭 現在地の段階が {len(steps)} 段（{TRACK_MIN}〜{TRACK_MAX} 段にする）")
    if sum(1 for s in steps if "is-now" in (s.get("class") or [])) != 1:
        out.append("🧭 現在地の『今の段』（.is-now）がちょうど 1 つでない")
    if not body_text(lead.select_one(":scope > .tx-gist-where .tx-gist-q .tx-gist-body")):
        out.append("『この記述の問い』が空")

    beats = lead.select(":scope > .tx-gist-story > p.tx-gist-beat")
    kinds = [next((c[3:] for c in (b.get("class") or []) if c.startswith("is-")), "?") for b in beats]
    want = [k for k, _ in BEATS]
    if kinds != want:
        out.append(f"ストーリーの段が {kinds}（{want} の順の 4 段にする）")
    for b, k in zip(beats, kinds):
        if not body_text(b.select_one(".tx-gist-body")):
            out.append(f"ストーリーの段 {k} が空")

    terms = lead.select(":scope > .tx-gist-terms dl > .tx-gist-term")
    if not TERMS_MIN <= len(terms) <= TERMS_MAX:
        out.append(f"📘 キーワードが {len(terms)} 語（{TERMS_MIN}〜{TERMS_MAX} 語にする）")
    for t in terms:
        if not body_text(t.select_one("dt")) or not body_text(t.select_one("dd")):
            out.append("📘 キーワードに語か定義の空欄がある")

    # §v15（2026-09-22）：🖼 イメージ面は 🗝記憶のフック（.syn-image）と同じ像＝逐語重複のため任意化
    #（置く場合は空欄禁止・無い場合は ERROR にしない）。
    img = lead.select_one(":scope > p.tx-gist-beat.is-image")
    if img is not None and not body_text(img.select_one(".tx-gist-body")):
        out.append("🖼 イメージが空")
    judge = lead.select_one(":scope > p.tx-gist-judge")
    if judge is None or not body_text(judge.select_one(".tx-gist-body")):
        out.append("判定（.tx-gist-judge）が無い")
    elif mark in MARKS and MARKS[mark] not in (judge.get("class") or []):
        out.append("判定の ○× が結論のマークと食い違う")
    return out, track


# ---------------------------------------------------------------- CSS 区画
def region(text: str) -> tuple[int, int] | None:
    i = text.find(CSS_BEGIN)
    if i < 0:
        return None
    j = text.find(CSS_END, i)
    if j < 0:
        return None
    return i, j + len(CSS_END)


def canonical_css() -> str:
    s = CANONICAL.read_text(encoding="utf-8")
    r = region(s)
    if r is None:
        raise SystemExit(f"正典 {CANONICAL} に {CSS_BEGIN} 区画が無い")
    return s[r[0]:r[1]].replace("\r\n", "\n")


def ensure_css(text: str, css: str) -> tuple[str, bool]:
    """TX-GIST-STORY 区画を正典どおりにそろえる（あれば置換・無ければ第1 </style> の直前へ挿入）。
    改行様式は挿入位置の直前の行に合わせる。"""
    r = region(text)
    if r is not None:
        seg = text[r[0]:r[1]]
        nl = "\r\n" if "\r\n" in seg else "\n"
        new = css.replace("\n", nl)
        if seg == new:
            return text, False
        return text[:r[0]] + new + text[r[1]:], True
    k = text.find("</style>")
    if k < 0:
        raise ValueError("</style> が無い")
    line_start = text.rfind("\n", 0, k) + 1          # </style> 行の先頭
    prev_end = text.rfind("\n", 0, line_start - 1) if line_start > 0 else -1
    prev_line = text[prev_end + 1:line_start]
    nl = "\r\n" if prev_line.endswith("\r\n") else "\n"
    block = css.replace("\n", nl) + nl
    return text[:line_start] + block + text[line_start:], True


class SpecError(ValueError):
    pass


def load_spec(path: str | Path) -> dict:
    """仕様 JSON を読む。壊れていたら SpecError（呼び出し側で NG 行にする＝素の traceback を出さない）。"""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SpecError(f"仕様 JSON が無い: {path}")
    except json.JSONDecodeError as e:
        raise SpecError(f"仕様 JSON が壊れている（{e.lineno} 行 {e.colno} 列: {e.msg}）。"
                        "本文の半角 \" は「」にし、リンク属性の \" は \\\" とエスケープする"
                        "（Python の json.dump(ensure_ascii=False) で書き出すと確実）")
    if not isinstance(data, dict):
        raise SpecError("仕様 JSON の最上位は {\"track\": [...], \"cards\": {...}} のオブジェクト")
    return data
