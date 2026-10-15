#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx-intro.py ── §v16 INTRO（解く前の🔰導入）の単一情報源ツール。判定式は scripts/tx_intro_rules.py。

  materials <file>                headless 執筆用の素材（設問・全記述・物語・体系マップ・BASIS・答案圧縮・解法ナビ）
  apply     <file> --spec <json>  仕様 JSON から導入を組んで差し込む（既存の導入は置き換え）＋CSS 区画の同期
                                  ＋（任意）解法ナビのヒント差し替え。契約違反なら 1 字も書かない。[--dry]
  extract   <file>                既存の導入を仕様 JSON に戻して表示
  check     <file>...             §v16 の契約検査（G84 と同じ式）。導入が無いファイルは NG
  scope     <file> --spec <json> [--ref HEAD]  変更が §v16 の許可領域（導入・CSS 区画・解法ナビのヒント）だけか／
                                  導入とヒントが仕様どおりか
  pending   [--json] [--root .]   導入が未設置のインライン周回 `_lex` の一覧
  css       <file>... [--check]   TX-INTRO 区画を正典（GENESIS-CARD）へそろえる

仕様 JSON（apply）:
  {"what":  "何の話？ 1〜3 文（<b> 可）",
   "tools": [{"term": "訴因変更", "ref": "312条1項", "def": "…定義 1 文…"}, …]  （0〜4 件・ref は空可）,
   "order": "読む順番 1〜2 文（記述が分かれる軸と、判定の手順。どちらに倒れるかは書かない）",
   "hints": {"ア": "…"}  （任意：解法ナビのヒントが結論を言っているときだけ差し替える）}
  禁止（apply が拒否する）：○×記号／正解／正しい／誤り／肢N／記述N／選択肢番号／解答技術語／
  改行／b・strong・em 以外のタグ。物語解説（.fa-narrative）には触れない（Lexia の復習カードが使う）。
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parent.parent

from tx_intro_rules import (  # noqa: E402  判定式の単一情報源
    read, write, strip_tags, render, intro_span, parse, place_intro, remove_intro,
    canonical_css, sync_css, css_region, step_data, set_hints, blank_hints,
    spec_problems, check_text, STYLE_OPEN,
)


def _txt(el, limit=0):
    if el is None:
        return ""
    t = re.sub(r"\s+", " ", el.get_text(" ", strip=True))
    return (t[:limit] + "…") if limit and len(t) > limit else t


# ---------------------------------------------------------------- materials
def cmd_materials(path: Path) -> int:
    from bs4 import BeautifulSoup
    s, _ = read(path)
    soup = BeautifulSoup(s, "html.parser")
    out = [f"# {_txt(soup.title)}（{path.name}）"]
    pa = soup.find(id="part-a")
    if pa is not None:
        lead = [_txt(p) for p in pa.find_all("p", recursive=False)]
        out.append("\n## 設問（リード）\n" + "\n".join(x for x in lead if x))
        ob = pa.select_one(".tx-original-block")
        if ob is not None:
            out.append("\n## 原文ブロック（事例・見解・記述）\n" + _txt(ob, 2500))
    vd = {tr.get("data-stmt"): tr.get("data-verdict") for tr in soup.select("tr[data-stmt][data-verdict]")}
    out.append("\n## 全記述（カードの文。正解は書き手の確認用＝導入には絶対に書かない）")
    for card in soup.select(".tx-inline-card[data-stmt]"):
        n = card.get("data-stmt")
        out.append(f"- 記述{n}（{ {'o': '○', 'x': '×'}.get(vd.get(n), '?')}）: " + _txt(card.select_one(".tx-inline-stmt-text")))
    nar = soup.select_one(".fa-narrative")
    if nar is not None:
        out.append("\n## 物語解説（導入の主素材。前提＝何の話・用語・物差しだけを拾い、結論は拾わない）")
        for p in nar.select("p[data-fa-label]"):
            out.append(f"- 〔{p.get('data-fa-label')}〕{_txt(p)}")
    sm = soup.select_one(".tx-sysmap-title")
    if sm is not None:
        out.append("\n## 体系マップの題\n" + _txt(sm))
    tracks = []
    for tr in soup.select(".tx-gist-track"):
        steps = " → ".join(_txt(x) for x in tr.select(".tx-gist-step"))
        if steps and steps not in tracks:
            tracks.append(steps)
    if tracks:
        out.append("\n## 🧭現在地の段階トラック\n" + "\n".join(tracks))
    heads = []
    for h in soup.select(".tx-basis-head"):
        t = _txt(h).replace("↩ 戻る", "").strip()
        if t and t not in heads:
            heads.append(t)
    if heads:
        out.append("\n## BASIS の見出し（使う道具の条文・判例はここにあるものだけ）\n" + "\n".join("- " + h for h in heads))
    terms = []
    for dt in soup.select(".tx-gist-term"):
        t = _txt(dt, 160)
        if t and t not in terms:
            terms.append(t)
    if terms:
        out.append("\n## 📘キーワード（定義の素材）\n" + "\n".join("- " + t for t in terms[:14]))
    ac = []
    for sp in soup.select(".tx-inline-card .tx-anscomp-line"):
        t = _txt(sp)
        if t and t not in ac:
            ac.append(t)
    if ac:
        out.append("\n## 答案圧縮（＝答えになる命題。導入に同じ文を書かない）\n" + "\n".join("- " + a for a in ac))
    sub = soup.select_one(".solve-nav .sn-sub")
    sd = step_data(s)
    if sub is not None or sd is not None:
        out.append("\n## 解法ナビ（副題とヒント。ヒントが結論を言っていたら hints で差し替える）")
        if sub is not None:
            out.append("- 副題: " + _txt(sub))
        if sd is not None:
            for k, v in sd[0].items():
                if isinstance(v, dict):
                    out.append(f"- hint[{k}]: {v.get('hint', '')}")
    sp = intro_span(s)
    if sp is not None:
        out.append("\n## 既存の導入（仕様）\n" + json.dumps(parse(s[sp[0]:sp[1]]), ensure_ascii=False, indent=1))
    print("\n".join(out))
    return 0


# ---------------------------------------------------------------- apply
def build(s: str, spec: dict) -> str:
    t = place_intro(s, render(spec))
    t = sync_css(t, canonical_css())
    if spec.get("hints"):
        t = set_hints(t, spec["hints"])
    return t


def cmd_apply(path: Path, spec_path: Path, dry: bool) -> int:
    s, nl = read(path)
    if 'class="tx-inline-card"' not in s:
        print(f"NG {path.name}: インライン周回の _lex ではない")
        return 1
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    sd = step_data(s)
    errs = spec_problems(spec, list(sd[0]) if sd else [])
    if errs:
        print(f"NG {path.name}:\n   " + "\n   ".join(errs))
        return 1
    try:
        t = build(s, spec)
    except ValueError as e:
        print(f"NG {path.name}: {e}")
        return 1
    bad = [r for r in check_text(t, path.name, require=True) if r.startswith("ERROR")]
    if bad:
        print(f"NG {path.name}（組んだ結果が契約違反＝書かない）:\n   " + "\n   ".join(bad))
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


def cmd_extract(path: Path) -> int:
    s, _ = read(path)
    sp = intro_span(s)
    if sp is None:
        print(f"NG {path.name}: 導入が無い")
        return 1
    print(json.dumps(parse(s[sp[0]:sp[1]]), ensure_ascii=False, indent=1))
    return 0


def cmd_check(paths: list[Path]) -> int:
    rc = 0
    for p in paths:
        s, _ = read(p)
        res = check_text(s, p.name, require=True)
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
def strip_allowed(s: str) -> str:
    s = remove_intro(s)
    s = re.sub(re.escape(STYLE_OPEN) + r"\n.*?\n</style>\n", "", s, flags=re.S)
    r = css_region(s)
    while r is not None:
        end = r[1] + (1 if s[r[1]:r[1] + 1] == "\n" else 0)
        s = s[:r[0]] + s[end:]
        r = css_region(s)
    return blank_hints(s)


def cmd_scope(path: Path, spec_path: Path | None, ref: str) -> int:
    top = subprocess.run(["git", "-C", str(path.resolve().parent), "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, encoding="utf-8").stdout.strip()
    rel = path.resolve().relative_to(Path(top).resolve()).as_posix()
    base = subprocess.run(["git", "-C", top, "show", f"{ref}:{rel}"], capture_output=True)
    if base.returncode != 0:
        print(f"NG {path.name}: {ref} に {rel} が無い")
        return 2
    a = strip_allowed(base.stdout.decode("utf-8").replace("\r\n", "\n"))
    new = read(path)[0].replace("\r\n", "\n")
    b = strip_allowed(new)
    problems = []
    if a != b:
        al, bl = a.split("\n"), b.split("\n")
        d = next((i for i, (x, y) in enumerate(zip(al, bl)) if x != y), min(len(al), len(bl)))
        problems.append(f"§v16 の許可領域以外が変わっている（許可領域除去後の {d + 1} 行目付近）\n"
                        f"   before: {al[d][:160] if d < len(al) else '(EOF)'}\n"
                        f"   after : {bl[d][:160] if d < len(bl) else '(EOF)'}")
    if spec_path is not None:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        sp = intro_span(new)
        if sp is None or new[sp[0]:sp[1]] != render(spec):
            problems.append("導入が仕様から組んだ HTML と一致しない（手書き・追記）")
        sd = step_data(new)
        for k, v in (spec.get("hints") or {}).items():
            if sd is None or (sd[0].get(k) or {}).get("hint") != v:
                problems.append(f"解法ナビ hint[{k}] が仕様と一致しない")
    if problems:
        print(f"NG {path.name}: " + "\n   ".join(problems))
        return 1
    print(f"OK {path.name}: 変更は §v16 の許可領域（導入・CSS 区画・解法ナビのヒント）だけ")
    return 0


# ---------------------------------------------------------------- pending / css
def cmd_pending(root: Path, as_json: bool) -> int:
    todo = []
    for p in sorted((root / "outputs" / "ux" / "000_TX").glob("*/*_lex.html")):
        s = p.read_bytes().decode("utf-8")
        if 'class="tx-inline-card"' in s and 'class="tx-intro"' not in s:
            todo.append(p)
    rel = lambda p: str(p.relative_to(root)).replace("\\", "/")
    if as_json:
        print(json.dumps([rel(p) for p in todo], ensure_ascii=False))
        return 0
    by: dict[str, int] = {}
    for p in todo:
        by[p.parent.name] = by.get(p.parent.name, 0) + 1
    print(f"🔰導入が未設置のインライン _lex: {len(todo)} 本 " + " / ".join(f"{k} {v}" for k, v in sorted(by.items())))
    return 0


def cmd_css(paths: list[Path], check: bool) -> int:
    css = canonical_css()
    rc = 0
    for p in paths:
        s, nl = read(p)
        if intro_span(s) is None:
            print(f"SKIP {p.name}: 導入が無い")
            continue
        t = sync_css(s, css)
        if t == s:
            print(f"OK {p.name}")
            continue
        if check:
            print(f"NG {p.name}: TX-INTRO 区画が正典と違う（または配置が旧式）")
            rc = 1
            continue
        write(p, t, nl)
        print(f"CSS {p.name}: 正典へそろえた")
    return rc


# ---------------------------------------------------------------- main
def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    opts, args, flags = {}, [], set()
    i = 0
    while i < len(rest):
        a = rest[i]
        if a in ("--spec", "--ref", "--root"):
            opts[a] = rest[i + 1]
            i += 2
            continue
        (flags.add(a) if a.startswith("--") else args.append(a))
        i += 1
    paths = [Path(a) for a in args]
    if cmd == "materials":
        return cmd_materials(paths[0])
    if cmd == "apply":
        return cmd_apply(paths[0], Path(opts["--spec"]), "--dry" in flags)
    if cmd == "extract":
        return cmd_extract(paths[0])
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
