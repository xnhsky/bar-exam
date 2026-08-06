#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx_source_text.py ── 設問・問題文原文（§v13s）の単一情報源。

公式 `outputs/000_TX/…`（PDF 由来の原文を保持）と Lexia 用 `_lex` を対照し、
「`_lex` に載っていない設問・問題文の原文」を求める判定式と、その原文を
§v13n の不可侵原文ブロック（`.tx-original-block`）へ逐語で組み直す組み立てを持つ。

利用者は 2 つ：
  * `scripts/validate-tx-core.py` G75 …… 欠落を機械検出する（検出層）
  * `scripts/tx-restore-original.py` …… 公式から逐語復元する（修復層）
判定式を共有するのは「直したのに ERROR が消えない／ERROR が出ないのに欠けている」を
構造的に起こさないため（検出 ⟺ 修復可能 を同値にする）。
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    BeautifulSoup = None

LEX_GLOB = "outputs/ux/000_TX/**/*_lex.html"

# PART A の原文エリアの終端マーカー（この手前までが設問・問題文）
END_MARKERS = (
    '<div class="tx-sysmap"',
    'class="solve-nav"',
    '<div class="tx-inline-list"',
    'id="answer-area"',
    'class="answer-area',   # 公式は class 形が混在する。sec-nav の href="#answer-area" は拾わない
    '<div class="part-title"',
)

# 共有本体を名乗る原文ラベル（見出しの自動補完に使う。原文に無いラベルは作らない）
BODY_LABELS = ("【会話】", "【対話】", "【事例】", "【事案】", "【文章】", "【資料】", "【説明】")

MARKER_RE = re.compile(r"^([ア-ンａ-ｚA-Za-z1-9①-⑳])[　\s]+(\S.*)$", re.S)

# 【会話】【記述】【語句群】… の見出し行（直後のブロックのラベルになる）
LABEL_RE = re.compile(r"^(【.{1,10}】|（参照条文）|\\(参照条文\\))")
# 設問原文でない区画（載せない）。参照条文は #basis の領分、解答は解答前に出さない。
SKIP_LABEL_RE = re.compile(r"参照条文|解答|正解")
# 解答前に見える場所へ持ち込んではならない行（§v13r・G19）。公式 PART A には
# 「正解：肢3（…）／正答率89%」のような露出が残る問があり、そのまま移送すると
# `_lex` の周回画面に正解が常時表示される（刑TX069 の実例）。
SPOILER_RE = re.compile(r"正解|正答率|誤り[＝=]|答え[：:]")
# 行ごと落とすのは行き過ぎな露出（選択肢一覧の末尾に付いた「（正解：肢1）」等）は
# 断片だけ切る。切った残りがまだ露出していれば行ごと落とす。
SPOILER_FRAG_RE = re.compile(r"[（(][^（）()<>]*(?:正解|正答)[^（）()<>]*[）)]|／?\s*正答率[^／<]*")
# 原文ではない編集注記の断片（公式側の見出しに付く「（本物の5択）」等）。
EDITORIAL_FRAG_RE = re.compile(r"[（(](?:本物の5択|本問|原題)[^）)]*[）)]")
# 編集注記の見出し（📖 本問…の本物の5択 ── 等）。原文ではないので載せない。
EDITORIAL_HEAD_RE = re.compile(r"^[\U0001F300-\U0001FAFF\u2600-\u27BF]")


# ---------------------------------------------------------------- 抽出


def part_a_region(html: str) -> tuple[str, int, int]:
    """#part-a の見出し直後〜体系マップ手前（＝設問・問題文エリア）を返す。"""
    i = html.find('id="part-a"')
    if i < 0:
        return "", -1, -1
    tail = html[i:]
    ends = [tail.find(k) for k in END_MARKERS]
    ends = [e for e in ends if e > 0]
    stop = min(ends) if ends else min(len(tail), 12000)
    h = tail.find("</h2>")
    if h < 0 or h > stop:
        return "", -1, -1
    start = i + h + len("</h2>")
    end = i + stop
    return html[start:end], start, end


def norm(text: str) -> str:
    """全角/半角・空白の揺れを吸収した比較用キー（公式と `_lex` の同一文判定に使う）。"""
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text))


def visible_text(fragment: str) -> str:
    """記述の再掲（.problem-text）を除いた原文テキスト。"""
    frag = re.sub(r'<div class="problem-text"[\s\S]*?</div>', "", fragment)
    return norm(re.sub(r"<[^>]+>", "", frag))


def missing_ratio(official_region: str, lex_region: str) -> tuple[float, int]:
    """公式の原文が `_lex` からどれだけ欠けているか（24 字窓の非被覆率）。"""
    o = visible_text(official_region)
    l = visible_text(lex_region)
    chunks = [o[i:i + 24] for i in range(0, len(o), 24) if len(o[i:i + 24]) >= 12]
    if not chunks:
        return 0.0, 0
    miss = [c for c in chunks if c not in l]
    return len(miss) / len(chunks), len(o) - len(l)


# ---------------------------------------------------------------- 組み立て


def inner_html(node) -> str:
    """原文の行内マークアップ（<b>学生A．</b> 等）を保ったまま中身を返す。

    畳むのは ASCII の空白・改行だけ。全角スペース（U+3000）は原文の字配り
    （「（　）内」「1　ア　ク　　2　イ　エ」）そのものなので触らない。"""
    return re.sub(r"[ \t\r\n]+", " ", node.decode_contents()).strip()


def plain(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html)


def head_label(text: str) -> str:
    """【記述】── いずれの…を選ぶ → 【記述】（原文ラベルだけ残し編集注記の尾を落とす）。"""
    label = re.split(r"──|—|――", text)[0].strip()
    return re.sub(r"[（(](?:本物の5択|本問|原題)[^）)]*[）)]", "", label).strip()


def collect(region: str):
    """公式の原文エリアを **出現順の項目列** に分解する。値は全て HTML 断片。

    項目は (kind, label, rows)。kind は "lead"（設問リード）／"body"（共有本体＝会話・事例）／
    "list"（記述・語句群・組合せ等の行列）。ラベル（【会話】【記述】…）は直後のブロックに
    紐づける（リードとして平積みすると 刑TX174 型の「見出しだけ 4 連発」になる）。
    設問原文でない区画（参照条文・解答）は落とす。"""
    soup = BeautifulSoup(region, "html.parser")
    items: list[tuple[str, str | None, list[str]]] = []
    pending_label: str | None = None

    def paragraphs_of(node) -> list[str]:
        out = []
        for p in node.find_all(["p", "div", "li"], recursive=True):
            if p.find(["p", "div", "li"], recursive=False):
                continue
            h = inner_html(p)
            if plain(h).strip():
                out.append(h)
        if not out:
            h = inner_html(node)
            if plain(h).strip():
                out.append(h)
        return out

    def push(kind: str, rows: list[str]) -> None:
        nonlocal pending_label
        rows = [EDITORIAL_FRAG_RE.sub("", SPOILER_FRAG_RE.sub("", r)).strip() for r in rows]
        rows = [r for r in rows
                if plain(r).strip()
                and not SPOILER_RE.search(plain(r))
                and not EDITORIAL_HEAD_RE.match(plain(r).strip())]
        if not rows:
            return
        if pending_label and SKIP_LABEL_RE.search(pending_label):
            pending_label = None
            return
        items.append((kind, pending_label, rows))
        pending_label = None

    for el in soup.find_all(recursive=False):
        if getattr(el, "name", None) is None:
            continue
        classes = set(el.get("class") or [])
        # 公式が既に正典どおりの不可侵原文ブロックを持つ型は、丸ごと逐語で移送する
        # （中身を再組み立てするとラベル・リードを取りこぼす＝刑訴TX234 の実例）
        if "tx-original-block" in classes:
            items.append(("verbatim", None, [str(el)]))
            continue
        if el.name in ("p", "h3") and not classes & {"case-paragraph", "problem-text"}:
            h = inner_html(el)
            t = plain(h).strip()
            if not t:
                continue
            if LABEL_RE.match(t) and len(t) <= 80:
                pending_label = head_label(t)
            else:
                push("lead", [h])
            continue
        if "problem-text" in classes:
            # 記述ごとの再掲はインラインカードが持つので載せない。
            # 番号なしの長文＝共有前提なので本体として拾う。
            if el.find(class_="choice-num-inline"):
                pending_label = None
                continue
            h = inner_html(el)
            if len(plain(h)) >= 60:
                push("body", [h])
            continue
        if classes & {"case-description", "case-scene"}:
            st = el.find(class_="case-scene-title")
            if st is not None and pending_label is None:
                pending_label = head_label(st.get_text(" ", strip=True))
                st.extract()
            push("body", paragraphs_of(el))
            continue
        rows = paragraphs_of(el)
        if rows and pending_label is None:
            first = plain(rows[0]).strip()
            if LABEL_RE.match(first) and len(first) <= 80:
                pending_label = head_label(first)
                rows.pop(0)
        push("list", rows)
    return items


def build_block(items, n_oxrow: int) -> str:
    """項目列を §v13n の不可侵原文ブロックへ組み立てる（原文の字面は変えない）。"""
    out = ['<div class="tx-original-block">',
           '<span class="tx-original-tag">\U0001F4D6 過去問原文</span>']

    # .tx-charge を出すのは記述数＝ox-row 数が一致する時だけ（G62 の要求）
    charge_rows = [r for kind, label, rows in items
                   if kind == "list" and label == "【記述】" for r in rows]
    use_charge = bool(charge_rows) and len(charge_rows) == n_oxrow and all(
        MARKER_RE.match(plain(r)) for r in charge_rows)

    verbatim = [rows[0] for kind, _, rows in items if kind == "verbatim"]
    if verbatim:
        return "\n".join(verbatim)

    open_charges = False
    for kind, label, rows in items:
        if kind != "list" and open_charges:
            out.append("</div>")
            open_charges = False
        if kind == "lead":
            for h in rows:
                out.append(f'<p class="tx-original-lead">{h}</p>')
        elif kind == "body":
            out.append('<div class="case-description"><div class="case-scene">')
            if label:
                out.append(f'<p class="case-scene-title">{label}</p>')
            for h in rows:
                out.append(f'<p class="case-paragraph">{h}</p>')
            out.append("</div></div>")
        else:
            if not open_charges:
                out.append('<div class="tx-original-charges">')
                open_charges = True
                style = ""
            else:
                style = ' style="margin-top:10px;"'
            if label:
                out.append(f'<p class="tx-original-charges-title"{style}>{label}</p>')
            for h in rows:
                m = MARKER_RE.match(plain(h)) if label == "【記述】" else None
                if use_charge and m:
                    out.append('<p class="tx-charge">'
                               f'<span class="tx-charge-mk">{m.group(1)}</span>'
                               f'{m.group(2).strip()}</p>')
                else:
                    out.append(f'<p class="case-paragraph">{h}</p>')
    if open_charges:
        out.append("</div>")
    out.append("</div>")
    return "\n".join(out)



# ---------------------------------------------------------------- 判定


def official_path(lex_path) -> Path:
    rel = str(lex_path).replace("outputs/ux/000_TX/", "outputs/000_TX/")
    return Path(rel.replace("_lex.html", ".html"))


def analyze(lex_path, lex_html=None, official_html=None):
    """`_lex` の原文欠落を判定して (verdict, payload) を返す。

    verdict は次の 4 つ。
      * "restorable" …… 公式に在る原文が `_lex` に無く、逐語復元できる（G75 ERROR）。
                         payload に組み立て済みブロックと挿入位置が入る。
      * "review"     …… 公式と差はあるが、`_lex` が自前の共有本体（言い換え版）を
                         持つ。原文への差し替えは内容照合が要るので人手（G75 WARNING）。
      * "no-layer"   …… 原文層（.tx-original-block／.tx-original-lead）が一つも無い（WARNING）。
      * None         …… 問題なし。
    """
    lex_path = Path(lex_path)
    if lex_html is None:
        lex_html, _ = read_keep_newlines(lex_path)
    off_path = official_path(lex_path)
    has_layer = ('class="tx-original-block"' in lex_html
                 or 'class="tx-original-lead"' in lex_html)

    if official_html is None:
        if not off_path.exists():
            return (None if has_layer else "no-layer"), None
        official_html, _ = read_keep_newlines(off_path)

    off_region, _, _ = part_a_region(official_html)
    lex_region, lstart, lend = part_a_region(lex_html)
    if not off_region or not lex_region:
        return (None if has_layer else "no-layer"), None

    ratio, delta = missing_ratio(off_region, lex_region)
    if ratio < 0.5 or delta < 80:
        return (None if has_layer else "no-layer"), None

    # `_lex` が既に自前の共有本体（事例・会話・見解）を持つ型は機械復元しない。
    # 公式の原文と `_lex` の言い換え版が二重掲載になるため、1 問ずつ内容照合する。
    if re.search(r'class="(case-description|case-scene)', lex_region):
        return "review", dict(ratio=ratio, delta=delta)
    if 'class="tx-original-block"' in lex_region:
        return "review", dict(ratio=ratio, delta=delta)

    items = collect(off_region)
    lex_seen = visible_text(lex_region)

    def keep(row: str) -> bool:
        key = norm(plain(row))
        return len(key) < 12 or key not in lex_seen

    trimmed = []
    for k, lab, rows in items:
        if k == "verbatim":
            trimmed.append((k, lab, rows))
            continue
        rows = [r for r in rows if keep(r)]
        if rows:
            trimmed.append((k, lab, rows))
    items = trimmed
    if not any(k in ("body", "list", "verbatim") for k, _, _ in items):
        # 欠けているのは設問原文ではない区画（参照条文・解答・編集注記）だけ
        return (None if has_layer else "no-layer"), None

    n_oxrow = len(re.findall(r'class="ox-row[ "]', lex_html))
    block = build_block(items, n_oxrow)
    # G62（.tx-charge 数＝.ox-row 数）を壊さない。合わない問題は原文のまま
    # .case-paragraph へ降格する（.tx-charge 不使用なら G62 はスキップされる規約）。
    if block.count('class="tx-charge"') != n_oxrow:
        block = block.replace('<p class="tx-charge">', '<p class="case-paragraph">')

    moved = {norm(plain(r)) for k, _, rows in items if k == "lead" for r in rows}
    return "restorable", dict(ratio=ratio, delta=delta, block=block, moved=moved,
                              region=lex_region, lstart=lstart, lend=lend,
                              official=str(off_path), items=items)


def read_keep_newlines(path) -> tuple[str, str]:
    """改行コードを 1 バイトも変えずに読む（raw のまま返す）。

    corpus には CRLF ファイルと「LF 主体だが数十行だけ CRLF」の混在ファイルがある。
    以前は多数派へ寄せて書き戻していたため、混在ファイルが全行 diff になった
    （刑訴TX029/085/117＝1 万行超の偽 diff）。raw のまま扱い、挿入する塊にだけ
    多数派の改行を使う。第 2 戻り値は「挿入用の改行」。"""
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
        raw = fh.read()
    crlf = raw.count("\r\n")
    lf = raw.count("\n") - crlf
    return raw, ("\r\n" if crlf > lf else "\n")
