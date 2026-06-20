#!/usr/bin/env python3
"""既存 RX を正典 AXIOM 構造へ再テンプレート（2026-06-20）.

RX は TX(GENESIS)/JX(ATHENA) のような正典スケルトンを持たず自由生成されてきたため、
コンテナ（.card / .wrap）と inline CSS が 58 種類に割れていた（＝正典化が効いていない）。
本スクリプトは **既存の内容を保持したまま** `canonical/AXIOM.html` の構造・CSS・JS へ
移し替え、全 RX を 1 つの正典に統一する。

設計（content independence と非破壊を両立）：
- 構造シェル・CSS 全規則・JS は AXIOM から取得（＝58→1 に統一）。
- :root のパレット（--accent 等）は **元ファイルの値を継承**（問題ごとの配色を保持・TX と同様）。
- 本文（論点名・問題の所在・規範・理由・あてはめ・判例条文）は元ファイルから抽出して移植。
- ○×クイズ（.self-check-quiz）は **outerHTML を逐語コピー**（Lexia 連携の data-* を壊さない）。
- フェイルセーフ：必須要素（h1・規範ボックス・クイズ≥2）が取れない／レイアウト不明な
  ファイルは **変換せず原本を残し** report に出す（壊れたカードを生まない）。

冪等：既に AXIOM-RECANON マーカーを含むファイルはスキップ。
依存：beautifulsoup4 + lxml。
"""
from __future__ import annotations
import pathlib
import re
import sys

from bs4 import BeautifulSoup, Tag

REPO = pathlib.Path(__file__).resolve().parent.parent
RX_DIR = REPO / "outputs/ux/001_RX"
AXIOM = REPO / "canonical/AXIOM.html"
MARKER = "AXIOM-RECANON"

# h2 見出し → セクション種別（全角カッコや空白を除去して前方一致）
# 注意：「規範チェック」は「規範」を含むため quiz を norm より先に判定する。
SECTION_KEYS = [
    ("problem", ["問題の所在", "所在"]),
    ("quiz", ["規範チェック", "チェック", "○×", "クイズ", "自己確認", "確認テスト"]),
    ("norm", ["規範", "暗記"]),
    ("reason", ["理由"]),
    ("apply", ["あてはめ", "答案", "型"]),
    ("refs", ["関連判例", "判例", "条文", "参照"]),
]
# 保持する inline / 構造タグ（その他のラッパ div/span はアンラップして中身を残す）
KEEP_TAGS = {"p", "ul", "ol", "li", "b", "strong", "em", "i", "u", "br", "code", "span", "small", "sup", "sub",
             "table", "thead", "tbody", "tr", "th", "td", "caption"}
TABLE_ATTR = {"colspan", "rowspan"}


def classify(heading: str) -> str | None:
    h = re.sub(r"[（(].*?[)）]|\s|　", "", heading)
    for key, pats in SECTION_KEYS:
        for p in pats:
            if p in h:
                return key
    return None


def find_norm_box(soup):
    """規範ボックス本体を堅牢に検出する。クラスは norm-box / norm-body / norm-content /
    'norm hidden' / 素の norm 等と多様。トグルボタン（norm-toggle/norm-btn）やラッパ
    （norm-wrap）は除外し、残った候補のうち最もテキスト量の多いものを本体とみなす。"""
    cands = []
    for el in soup.find_all(class_=re.compile(r"\bnorm")):
        if el.name == "button":
            continue
        cls = " ".join(el.get("class", []))
        if re.search(r"toggle|btn|button|wrap|head|label|title", cls):
            continue
        cands.append(el)
    if not cands:
        return None
    return max(cands, key=lambda e: len(e.get_text(strip=True)))


def axiom_parts():
    """AXIOM から head(フォント+style) と script を取り出す。"""
    soup = BeautifulSoup(AXIOM.read_text(encoding="utf-8"), "lxml")
    head = soup.find("head")
    style = head.find("style")
    script = soup.find("script")
    return head, style, script


def extract_palette(soup: BeautifulSoup) -> dict[str, str]:
    """元ファイルの :root{...} から CSS 変数を読み取る。"""
    pal: dict[str, str] = {}
    for st in soup.find_all("style"):
        txt = st.string or st.get_text()
        if not txt:
            continue
        m = re.search(r":root\s*\{([^}]*)\}", txt, re.S)
        if m:
            for name, val in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1)):
                pal[name.strip()] = val.strip()
    return pal


def clean_html(node: Tag) -> str:
    """ラッパ div を外し、保持タグだけ残した内側 HTML 文字列を返す。"""
    if not isinstance(node, Tag):
        return str(node).strip()
    # コピーを破壊的に整形：保持タグ以外はアンラップ、保持タグは属性を落とす
    # （ただし表の colspan/rowspan は残してセル結合を保つ）。canonical CSS に無い
    # クラスを無効化し、58 種の独自スタイルへの依存を断つ。
    for tag in node.find_all(True):
        if tag.name not in KEEP_TAGS:
            tag.unwrap()
        else:
            tag.attrs = {k: v for k, v in tag.attrs.items() if k in TABLE_ATTR}
    return node.decode_contents().strip()


def collect_section_nodes(card, flat: bool):
    """h2 ごとに (heading, [content_tags]) を返す。flat=.card / block=.wrap。"""
    out = []
    if flat:
        for h2 in card.find_all("h2", recursive=False) or card.find_all("h2"):
            content = []
            sib = h2.next_sibling
            while sib is not None:
                if isinstance(sib, Tag) and sib.name == "h2":
                    break
                if isinstance(sib, Tag):
                    content.append(sib)
                sib = sib.next_sibling
            out.append((h2.get_text(strip=True), content))
    else:
        for block in card.find_all(class_="block"):
            h2 = block.find("h2")
            if not h2:
                continue
            content = [c for c in h2.find_next_siblings() if isinstance(c, Tag)]
            out.append((h2.get_text(strip=True), content))
    return out


CANON_HEADING = {
    "problem": "問題の所在", "reason": "理由づけ", "apply": "あてはめの型", "refs": "関連判例・条文",
}


def build_body(title, src_text, ordered, norm_inner, norm_cite, quizzes):
    """抽出物を AXIOM 構造の body 文字列に組み立てる。ordered は元の順序を保った
    [(kind, 元見出し, 内容html)]。未知 kind は元見出しを保持して落とさない。"""
    parts = ['<div class="card">', f"<h1>{title}</h1>", f'<p class="src">{src_text}</p>']

    def wrap(kind, html):
        if kind == "problem":
            return f'<div class="lead">{html}</div>'
        if kind == "refs":
            return f'<div class="refs">{html}</div>'
        return html  # reason / apply / 未知 は素のまま（canonical CSS が p/ol/table を整形）

    def norm_block():
        cite_html = f'<span class="cite">{norm_cite}</span>' if norm_cite else ""
        return (
            '\n<h2>規範（暗記対象）</h2>\n'
            '<button class="norm-toggle" onclick="toggleNorm(this)">規範を表示</button>\n'
            f'<div class="norm-box">{norm_inner}{cite_html}</div>\n'
        )

    norm_done = False
    for kind, heading, html in ordered:
        disp = CANON_HEADING.get(kind, heading)  # 未知は元見出しを保持
        parts.append(f"\n<h2>{disp}</h2>\n{wrap(kind, html)}\n")
        # 規範ボックスは問題の所在の直後（AXIOM の標準位置）に差し込む
        if kind == "problem" and norm_inner and not norm_done:
            parts.append(norm_block())
            norm_done = True
    if norm_inner and not norm_done:
        parts.append(norm_block())

    parts.append("\n<h2>規範チェック</h2>\n")
    for q in quizzes:
        parts.append(q)
    parts.append("\n</div>")
    return "\n".join(parts)


def recanon_one(path: pathlib.Path, head_html, script_html) -> str | None:
    raw = path.read_text(encoding="utf-8")
    if MARKER in raw:
        return "skip"
    soup = BeautifulSoup(raw, "lxml")
    container = soup.find(class_="card") or soup.find(class_="wrap") or soup.body
    if container is None:
        return "no-container"
    # .block ラッパの有無で「flat（h2＋兄弟）」か「block（.block 内）」かを判定。
    # .wrap でもフラットな変種があるため、コンテナ種別ではなく構造で見る。
    flat = container.find(class_="block") is None

    title_el = soup.find("title")
    h1_el = soup.find("h1")
    if not title_el or not h1_el or not h1_el.get_text(strip=True):
        return "no-title"
    title = title_el.get_text(strip=True)
    h1 = h1_el.get_text(strip=True)
    src_el = soup.find(class_="src")
    src_text = src_el.get_text(" ", strip=True) if src_el else f"出典: {path.parent.name}"

    quiz_tags = soup.find_all("div", class_="self-check-quiz")
    if len(quiz_tags) < 2:
        return "few-quiz"
    # ★ clean_html の破壊的処理より前に、クイズは outerHTML を文字列で確保（逐語保持）
    quizzes = [str(q) for q in quiz_tags]

    # ★ 規範ボックスを大域的に抽出（独自 h2 を持たず問題の所在に折り込まれた変種にも対応）。
    #   抽出後はツリーから除去し、問題の所在セクションに混入しないようにする。
    norm_inner = ""
    norm_cite = ""
    norm_box = find_norm_box(soup)
    if norm_box:
        cite_el = norm_box.find(class_="cite")
        if cite_el:
            norm_cite = cite_el.get_text(" ", strip=True)
            cite_el.extract()
        norm_inner = clean_html(norm_box)
        norm_box.decompose()
    for tg in soup.find_all(class_="norm-toggle"):
        tg.decompose()
    if not norm_inner.strip():
        return "no-norm"

    sec_nodes = collect_section_nodes(container, flat)
    ordered = []  # [(kind, 元見出し, html)]・元の順序を保持し未知セクションも残す
    for heading, nodes in sec_nodes:
        kind = classify(heading)
        if kind in ("norm", "quiz"):
            continue  # 規範は大域抽出済み／クイズは末尾で逐語付与
        html = "".join(clean_html(n) if isinstance(n, Tag) else str(n) for n in nodes).strip()
        if html:
            ordered.append((kind, heading, html))

    # フェイルセーフ：問題の所在が取れなければ怪しいので変換せず原本維持。
    if not any(k == "problem" for k, _, _ in ordered):
        return "no-problem"

    palette = extract_palette(soup)
    # AXIOM の style に元パレットを上書き
    style_html = str(head_html.find("style"))
    if palette:
        def repl_root(m):
            body = m.group(1)
            for name, val in palette.items():
                if re.search(re.escape(name) + r"\s*:", body):
                    body = re.sub(re.escape(name) + r"\s*:\s*[^;]+;", f"{name}:{val};", body)
                else:
                    body = body.rstrip() + f"\n  {name}:{val};"
            return ":root{" + body + "}"
        style_html = re.sub(r":root\s*\{([^}]*)\}", repl_root, style_html, count=1, flags=re.S)

    # 作成日コメントを継承（あれば）
    mdate = re.search(r"<!--\s*作成日：([0-9-]+)\s*-->", raw)
    date_comment = f"\n<!-- 作成日：{mdate.group(1)} -->" if mdate else ""

    body = build_body(h1, src_text, ordered, norm_inner, norm_cite, quizzes)
    out = (
        "<!DOCTYPE html>\n"
        f"<!-- {MARKER} v1.0（canonical/AXIOM.html へ統一・内容は元 RX を保持） -->\n"
        '<html lang="ja">\n<head>\n'
        + "\n".join(str(c) for c in head_html.find_all(["link", "meta"]))
        + f"\n<title>{title}</title>\n"
        + style_html
        + "\n</head>\n<body>\n"
        + body
        + "\n"
        + script_html
        + date_comment
        + "\n</body>\n</html>\n"
    )
    path.write_text(out, encoding="utf-8")
    return "ok"


def main() -> int:
    only = sys.argv[1] if len(sys.argv) > 1 else None
    head_html, _style, script_el = axiom_parts()
    script_html = str(script_el)
    stats: dict[str, int] = {}
    skipped_files: list[str] = []
    for f in sorted(RX_DIR.rglob("*.html")):
        if only and only not in str(f):
            continue
        r = recanon_one(f, head_html, script_html)
        stats[r] = stats.get(r, 0) + 1
        if r not in ("ok", "skip"):
            skipped_files.append(f"{r}: {f.relative_to(REPO)}")
    print("=== rx-recanon 結果 ===")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    if skipped_files:
        print("--- 変換せず原本維持（要確認）---")
        for s in skipped_files[:40]:
            print("  " + s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
