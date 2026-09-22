#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx-v15-dedup.py ── §v15 DEDUP（記述カードの重複削減＋「1語差し替えで裏返る」比較表）の単一情報源ツール。

  base      <file>... [--check]   決定論の土台（内容執筆なし・冪等・改行様式保持）：
                                  ① GIST 🖼イメージ面を削除（🗝記憶のフック .syn-image があるカードだけ）
                                  ② 📌POINT（.choice-points）を削除
                                  ③ BASIS の「本問への帰結」kd-item と BASIS 直後の結論段落を削除・summary 文言を整える
                                  ④ 条文操作（.syn-path）末尾の「よって…本記述は正しい／誤り。」型の結論文を削除（読点なしの短文だけ）
                                  ⑤ TX-DGM CSS 区画を正典（GENESIS-CARD）へ同期
  materials <file>                headless 執筆用の素材（40 万字の HTML を丸読みさせない）
  apply     <file> --spec <json>  仕様 JSON から ⚠️罠枠（隣接命題＋📐比較表）／🗝フック／GIST 判定 1 行／正誤表の転用行／
                                  正誤表の図解ソース（＝カードの比較表の複製）を組む。契約違反なら 1 字も書かない
  check     <file>...             §v15 の構造検査（G82 と同じ式）
  scope     <file> [--spec json] [--ref HEAD]  変更が §v15 の許可領域だけか（git と照合）／罠枠が仕様どおりか
  pending   [--json] [--root .]   未適用（data-v15 の無い罠枠を持つ v13 `_lex`）の一覧
  css       <file>... [--check]   TX-DGM 区画を正典へそろえる

仕様 JSON（apply）:
  {"cards": {"1": {"judge": "…1 行…", "hook": "…一行の対比圧縮…", "tenyo": "…次の問題へ持ち出す 1 文…",
                   "trap": "…隣接命題 1〜2 文（strong/em/b/a 可）…",
                   "matrix": {"title": "…", "cols": ["こう変えると", "答え", "根拠"],
                              "rows": [["行見出し", ["セル", "is-ok"], ["セル", null]], …]} | null}, …}}
  matrix は最大 4 行×4 列（cols の先頭が行見出し列）。セルの class は is-ok / is-ng / is-acc / is-flat / null。
  セル・見出しには <span class="dgm-src">条文</span> チップだけ入れてよい。
  全カードを覆うこと。matrix が null のカードは比較表を置かない（偽表の禁止）＝正誤表の既存図解はそのまま。
  禁止語（罠・表・フック・転用）：記述N／肢N／本問／上記／丸数字／A説等のラベル／解答技術語
  （素直に・疑いすぎ・組合せ問題・思い込みの罠・先入観・ひっかけの型・引っかけの型）。
"""
from __future__ import annotations

import html as _html
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parent.parent

from tx_v15_rules import (  # noqa: E402  判定式の単一情報源
    TRAP_LABEL, MATRIX_CELL_CLS, MATRIX_MAX, ALLOWED_INLINE_TAGS, FORBIDDEN,
    read, write, strip_tags, block_end, cards, row_span, region, canonical_css,
    render_matrix, validate_matrix, text_problems, render_trap, check_text,
)

# 結論文（条文操作末尾）：読点を含まない短い一文だけを機械で落とす
CONCLUSION_RE = re.compile(
    r"^(?:よって|したがって|ゆえに|以上より|結局|だから|つまり|以上から)?[^。、，]{0,60}?"
    r"(?:とする|という|とした|としている)?(?:本)?記述は(?:正しい|誤り|誤っている|誤りである|正しいといえる)"
    r"(?:（[○×〇✕]）)?$"
)


# ---------------------------------------------------------------- base（決定論の土台）
def base_card(c: str) -> str:
    # ① GIST 🖼イメージ面（フックがあるカードだけ）
    if 'class="syn-image"' in c:
        c = re.sub(r'<p class="tx-gist-beat is-image">.*?</p>', "", c, count=1, flags=re.S)
    # ② 📌POINT
    c = re.sub(r'\n*<div class="choice-points">.*?</ol>\s*</div>\n?', "\n", c, count=1, flags=re.S)
    # ③ BASIS「本問への帰結」kd-item・空になった details・summary 文言・直後の結論段落
    c = re.sub(r'\n?<div class="kd-item"><span class="kd-label[^"]*">[^<]*本問[^<]*</span>.*?</div>', "", c, flags=re.S)

    def fix_details(m: re.Match) -> str:
        d = m.group(0)
        if 'class="kd-item"' not in d:
            return ""
        sm = re.search(r"<summary>＋ (.*?)を開く</summary>", d)
        if sm:
            parts = [p for p in sm.group(1).split("・") if "本問" not in p]
            d = d.replace(sm.group(0), f"<summary>＋ {'・'.join(parts) or '詳細'}を開く</summary>")
        return d
    c = re.sub(r'<details class="tx-basis-more">.*?</details>', fix_details, c, flags=re.S)
    bi = c.find('<div class="sub-card basis-link">')
    if bi >= 0:
        be = block_end(c, bi)
        seg = re.sub(r'\n<p style="font-size:\.92em; margin-top:6px;">.*?</p>', "", c[bi:be], flags=re.S)
        c = c[:bi] + seg + c[be:]
    # ④ 条文操作末尾の結論文
    pi = c.find('<div class="syn-path">')
    if pi >= 0:
        pe = block_end(c, pi)

        def drop_conclusion(m: re.Match) -> str:
            body = m.group(2)
            parts = body.split("。")
            keep = []
            for i, p in enumerate(parts):
                plain = strip_tags(p).strip()
                if plain and CONCLUSION_RE.match(plain):
                    continue
                keep.append(p)
            out = "。".join(keep)
            return m.group(1) + out + m.group(3)
        seg = re.sub(r'(<span class="syn-body">)(.*?)(</span>\s*</p>)', drop_conclusion, c[pi:pe], flags=re.S)
        c = c[:pi] + seg + c[pe:]
    return c


def cmd_base(paths: list[Path], check: bool) -> int:
    rc = 0
    css = canonical_css()
    for p in paths:
        s, nl = read(p)
        if 'class="tx-v13-verdict"' not in s:
            print(f"SKIP {p.name}: v13 LOOP-CARD でない")
            continue
        t = s
        for n, st, en in reversed(cards(t)):
            t = t[:st] + base_card(t[st:en]) + t[en:]
        r = region(t)
        if r is not None and t[r[0]:r[1]] != css:
            t = t[:r[0]] + css + t[r[1]:]
        if t == s:
            print(f"OK {p.name}: 土台は適用済み（変更なし）")
            continue
        if check:
            print(f"TODO {p.name}: 土台未適用")
            rc = 1
            continue
        write(p, t, nl)
        print(f"BASE {p.name}: 土台を適用")
    return rc


# ---------------------------------------------------------------- materials
def cmd_materials(path: Path) -> int:
    from bs4 import BeautifulSoup

    def txt(el, limit=0):
        if el is None:
            return ""
        t = re.sub(r"\s+", " ", el.get_text(" ", strip=True))
        return (t[:limit] + "…") if limit and len(t) > limit else t

    s, _ = read(path)
    soup = BeautifulSoup(s, "html.parser")
    out = [f"# {txt(soup.title)}（{path.name}）"]
    block = soup.select_one(".tx-original-block") or soup.select_one(".tx-original-lead") or soup.select_one("#part-a p")
    out.append("\n## 設問・問題文（冒頭）\n" + txt(block, 900))
    svg = soup.select_one(".tx-sysmap svg")
    if svg is not None:
        labels = [re.sub(r"\s+", " ", t.get_text(" ", strip=True)) for t in svg.select("text")]
        out.append("\n## 体系マップの文字\n" + " ｜ ".join(x for x in labels if x))
    vd = {tr.get("data-stmt"): tr.get("data-verdict") for tr in soup.select("tr[data-stmt][data-verdict]")}
    out.append("\n## 全記述（同じ問題の中で同型の表を作らないために一覧で見る）")
    for card in soup.select(".tx-inline-card[data-stmt]"):
        out.append(f"- 記述{card.get('data-stmt')}（{ {'o': '○', 'x': '×'}.get(vd.get(card.get('data-stmt')), '?')}）: "
                   + txt(card.select_one(".tx-inline-stmt-text")))
    for card in soup.select(".tx-inline-card[data-stmt]"):
        n = card.get("data-stmt")
        out.append(f"\n## 記述 {n}（正解 { {'o': '○', 'x': '×'}.get(vd.get(n), '?')}）")
        out.append("- 記述原文＋答案圧縮: " + txt(card.select_one(".syn-orig")))
        g = card.select_one(".syn-lead")
        if g is not None:
            out.append("- THE GIST 冒頭: " + txt(g.select_one(".tx-gist-head")) + " ／ 判定: " + txt(g.select_one(".tx-gist-judge")))
        for sel, name in ((".syn-path", "条文操作"), (".syn-image", "現在の🗝記憶のフック"),
                          (".tx-v13-trap", "現在の⚠️間違いやすいポイント"), (".tx-v13-cross", "他科目横断")):
            el = card.select_one(sel)
            if el is not None:
                out.append(f"- {name}: " + txt(el, 900))
        for item in card.select(".tx-basis-item"):
            cls = item.get("class") or []
            kind = "判例" if "is-case" in cls else ("学説" if "is-theory" in cls else "条文")
            out.append(f"- BASIS〔{kind}〕{txt(item.select_one('.tx-basis-head'))}: {txt(item.select_one('.tx-basis-honbun'), 500)}")
        tr = soup.select_one(f'tr[data-stmt="{n}"]')
        if tr is not None:
            for line in tr.select(".tx-reflex-line"):
                tag = txt(line.select_one(".tx-reflex-tag"))
                if tag in ("切断点", "転用"):
                    out.append(f"- 正誤表の{tag}: " + txt(line))
            story = tr.get("data-brief-story") or ""
            if story:
                out.append("- 正誤表の CONTEXT 帯: " + re.sub(r"\s+", " ", strip_tags(story))[:600])
            dg = tr.select_one(".tx-vb-dgm-src .tx-dgm-title")
            if dg is not None:
                out.append("- 正誤表の既存図解: " + txt(dg))
    print("\n".join(out))
    return 0


# ---------------------------------------------------------------- apply
def spec_problems(spec: dict, card_ids: list[str]) -> list[str]:
    errs = []
    cs = spec.get("cards") or {}
    missing = [n for n in card_ids if n not in cs]
    if missing:
        errs.append("仕様が全カードを覆っていない: " + "・".join(missing))
    for n, c in cs.items():
        for key in ("trap", "hook", "tenyo", "judge"):
            v = c.get(key)
            if not isinstance(v, str) or not v.strip():
                errs.append(f"記述{n}: {key} が空")
            else:
                errs.extend(text_problems(v, f"記述{n} {key}"))
        m = c.get("matrix")
        if m is not None:
            errs.extend(validate_matrix(m, f"記述{n} matrix"))
            errs.extend(text_problems(str(m.get("title", "")), f"記述{n} matrix.title", {"span"}))
            for r in m.get("rows") or []:
                for cell in r:
                    t = cell[0] if isinstance(cell, list) else cell
                    errs.extend(text_problems(str(t), f"記述{n} matrix セル", {"span"}))
    return errs


def apply_card(c: str, n: str, cs: dict, code: str) -> str:
    matrix_html = render_matrix(f"{code}-{int(n):02d}" if n.isdigit() else f"{code}-{n}", cs["matrix"]) if cs.get("matrix") else ""
    # 罠枠（入れ子 div を数えて丸ごと差し替え）
    ti = c.find('<div class="tx-v13-trap"')
    if ti < 0:
        raise ValueError(f"記述{n}: 罠枠（.tx-v13-trap）が無い")
    te = block_end(c, ti)
    c = c[:ti] + render_trap(cs["trap"], matrix_html) + c[te:]
    # 判定 1 行（ストーリー型 GIST があるときだけ）
    c = re.sub(r'(<p class="tx-gist-judge [^"]*"><span class="tx-gist-lab [^"]*">[^<]*</span><span class="tx-gist-body">).*?(</span></p>)',
               lambda m: m.group(1) + cs["judge"] + m.group(2), c, count=1, flags=re.S)
    # 🗝記憶のフック
    c = re.sub(r'(<p class="syn-image"><span class="syn-tag">[^<]*</span>).*?(</p>)',
               lambda m: m.group(1) + cs["hook"] + m.group(2), c, count=1, flags=re.S)
    return c


def apply_row(s: str, n: str, cs: dict, code: str) -> str:
    sp = row_span(s, n)
    if sp is None:
        return s
    row = s[sp[0]:sp[1]]
    row = re.sub(r'(<p class="tx-reflex-line"><span class="tx-reflex-tag">転用</span>).*?(</p>)',
                 lambda m: m.group(1) + cs["tenyo"] + m.group(2), row, count=1, flags=re.S)
    if cs.get("matrix"):
        dsrc = '<div class="tx-vb-dgm-src" hidden>' + render_matrix(f"{code}-{int(n):02d}" if n.isdigit() else f"{code}-{n}", cs["matrix"]) + "</div>"
        di = row.find('<div class="tx-vb-dgm-src"')
        if di >= 0:
            de = block_end(row, di)
            row = row[:di] + dsrc + row[de:]
        else:
            k = row.rfind("</td></tr>")
            if k < 0:
                raise ValueError(f"記述{n}: 正誤表の行末（</td></tr>）が見つからない")
            row = row[:k] + dsrc + row[k:]
    return s[:sp[0]] + row + s[sp[1]:]


def problem_code(path: Path) -> str:
    m = re.search(r"TX(\d+)", path.name)
    return m.group(1) if m else "000"


def cmd_apply(path: Path, spec_path: Path, dry: bool) -> int:
    s, nl = read(path)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    ids = [n for n, _, _ in cards(s)]
    errs = spec_problems(spec, ids)
    if errs:
        print(f"NG {path.name}:\n   " + "\n   ".join(errs))
        return 1
    code = problem_code(path)
    t = s
    try:
        for n, st, en in reversed(cards(t)):
            t = t[:st] + apply_card(t[st:en], n, spec["cards"][n], code) + t[en:]
        for n in ids:
            t = apply_row(t, n, spec["cards"][n], code)
    except ValueError as e:
        print(f"NG {path.name}: {e}")
        return 1
    if t == s:
        print(f"OK {path.name}: 変更なし（適用済み）")
        return 0
    if dry:
        print(f"DRY {path.name}: 適用可能")
        return 0
    write(path, t, nl)
    print(f"APPLIED {path.name}")
    return 0


def cmd_check(paths: list[Path]) -> int:
    rc = 0
    for p in paths:
        s, _ = read(p)
        res = check_text(s, p.name)
        bad = [r for r in res if r.startswith("ERROR")]
        if bad:
            rc = 1
            print(f"NG {p.name}:\n   " + "\n   ".join(res))
        elif res:
            print(f"OK {p.name}（助言あり）:\n   " + "\n   ".join(res))
        else:
            print(f"OK {p.name}")
    return rc


# ---------------------------------------------------------------- scope
def strip_v15_regions(s: str) -> tuple[str, list[str]]:
    """§v15 で書き換えてよい領域を落とした本文と、罠枠ブロックの一覧。
    罠枠はカード（article）の中、図解ソースは正誤表の行（tr[data-stmt]）の中だけを見る
    （CSS/JS のコメントに同じ文字列が現れるため、全文検索では入れ子が数えられない）。"""
    traps = []
    out = s
    for n, st, en in reversed(cards(out)):
        c = out[st:en]
        i = c.find('<div class="tx-v13-trap"')
        if i >= 0:
            e = block_end(c, i)
            traps.append(c[i:e])
            c = c[:i] + c[e:]
        out = out[:st] + c + out[en:]
    traps.reverse()
    out = re.sub(r'<p class="syn-image">.*?</p>', "", out, flags=re.S)
    out = re.sub(r'<p class="tx-gist-judge [^"]*">.*?</p>', "", out, flags=re.S)
    out = re.sub(r'<p class="tx-reflex-line"><span class="tx-reflex-tag">転用</span>.*?</p>', "", out, flags=re.S)

    def strip_row(m: re.Match) -> str:
        row = m.group(0)
        i = row.find('<div class="tx-vb-dgm-src"')
        if i < 0:
            return row
        return row[:i] + row[block_end(row, i):]
    out = re.sub(r'<tr[^>]*\bdata-stmt="[^"]+"[^>]*>.*?</tr>', strip_row, out, flags=re.S)
    r = region(out)
    if r is not None:
        out = out[:r[0]] + out[r[1]:]
    return out, traps


def cmd_scope(path: Path, spec_path: Path | None, ref: str) -> int:
    top = subprocess.run(["git", "-C", str(path.resolve().parent), "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, encoding="utf-8").stdout.strip()
    rel = path.resolve().relative_to(Path(top).resolve()).as_posix()
    base = subprocess.run(["git", "-C", top, "show", f"{ref}:{rel}"], capture_output=True)
    if base.returncode != 0:
        print(f"NG {path.name}: {ref} に {rel} が無い")
        return 2
    a, _ = strip_v15_regions(base.stdout.decode("utf-8").replace("\r\n", "\n"))
    # 生成物 HTML は歴代ツールの書き戻しで LF/CRLF が混在しうる（read() は全行 CRLF の時だけ
    # 正規化する）。base 側は必ず正規化するので、混在ファイルでは「1 行も変えていないのに
    # 許可領域外が変わっている」と誤検出していた。両側を同じ式で正規化してから比べる。
    new = read(path)[0].replace("\r\n", "\n")
    b, traps = strip_v15_regions(new)
    problems = []
    if a != b:
        al, bl = a.split("\n"), b.split("\n")
        diff = next((i for i, (x, y) in enumerate(zip(al, bl)) if x != y), min(len(al), len(bl)))
        problems.append(f"§v15 の許可領域以外が変わっている（許可領域除去後の {diff + 1} 行目付近）\n"
                        f"   before: {al[diff][:160] if diff < len(al) else '(EOF)'}\n"
                        f"   after : {bl[diff][:160] if diff < len(bl) else '(EOF)'}")
    if spec_path is not None:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        code = problem_code(path)
        ids = [n for n, _, _ in cards(new)]
        want = []
        for n in ids:
            cs = spec["cards"].get(n)
            if cs is None:
                continue
            mh = render_matrix(f"{code}-{int(n):02d}" if n.isdigit() else f"{code}-{n}", cs["matrix"]) if cs.get("matrix") else ""
            want.append(render_trap(cs["trap"], mh))
        if want != traps:
            problems.append("罠枠が仕様から組んだ HTML と一致しない（手書き・追記・壊れたタグ）")
    if problems:
        print(f"NG {path.name}: " + "\n   ".join(problems))
        return 1
    print(f"OK {path.name}: 変更は §v15 の許可領域（罠枠・フック・判定・転用・図解ソース・CSS 区画）だけ")
    return 0


# ---------------------------------------------------------------- pending / css
def cmd_pending(root: Path, as_json: bool) -> int:
    todo = []
    for p in sorted((root / "outputs" / "ux" / "000_TX").glob("*/*_lex.html")):
        s, _ = read(p)
        if 'class="tx-v13-verdict"' not in s or 'class="tx-v13-trap"' not in s:
            continue
        if re.search(r'<div class="tx-v13-trap"(?! data-v15="1")', s):
            todo.append(p)
    rel = lambda p: str(p.relative_to(root)).replace("\\", "/")
    if as_json:
        print(json.dumps([rel(p) for p in todo], ensure_ascii=False))
        return 0
    by: dict[str, int] = {}
    for p in todo:
        by[p.parent.name] = by.get(p.parent.name, 0) + 1
    print(f"§v15 未適用の v13 _lex: {len(todo)} 本 " + " / ".join(f"{k} {v}" for k, v in sorted(by.items())))
    return 0


def cmd_css(paths: list[Path], check: bool) -> int:
    css = canonical_css()
    rc = 0
    for p in paths:
        s, nl = read(p)
        r = region(s)
        if r is None:
            print(f"SKIP {p.name}: TX-DGM 区画が無い")
            continue
        if s[r[0]:r[1]] == css:
            print(f"OK {p.name}")
            continue
        if check:
            print(f"NG {p.name}: TX-DGM 区画が正典と違う")
            rc = 1
            continue
        write(p, s[:r[0]] + css + s[r[1]:], nl)
        print(f"CSS {p.name}: 正典へそろえた")
    return rc


# ---------------------------------------------------------------- main
def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    flags = {a for a in rest if a.startswith("--") and a not in ("--spec", "--ref", "--root")}
    opts = {}
    args = []
    i = 0
    while i < len(rest):
        a = rest[i]
        if a in ("--spec", "--ref", "--root"):
            opts[a] = rest[i + 1]
            i += 2
            continue
        if not a.startswith("--"):
            args.append(a)
        i += 1
    paths = [Path(a) for a in args]
    if cmd == "base":
        return cmd_base(paths, "--check" in flags)
    if cmd == "materials":
        return cmd_materials(paths[0])
    if cmd == "apply":
        return cmd_apply(paths[0], Path(opts["--spec"]), "--dry" in flags)
    if cmd == "check":
        return cmd_check(paths)
    if cmd == "scope":
        return cmd_scope(paths[0], Path(opts["--spec"]) if "--spec" in opts else None, opts.get("--ref", "HEAD"))
    if cmd == "pending":
        return cmd_pending(Path(opts.get("--root", ROOT)), "--json" in flags)
    if cmd == "css":
        return cmd_css(paths, "--check" in flags)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
