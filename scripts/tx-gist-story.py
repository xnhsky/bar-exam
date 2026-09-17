#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THE GIST ストーリー型（TX-GIST-STORY・§v14）の適用・抽出・検査ツール。

使い方:
  python -X utf8 scripts/tx-gist-story.py apply   <_lex.html> --spec <spec.json> [--dry-run]
  python -X utf8 scripts/tx-gist-story.py extract <_lex.html>            # 生成済み GIST → JSON 仕様
  python -X utf8 scripts/tx-gist-story.py css     <file>... [--check]     # CSS 区画を正典（GENESIS-CARD）へそろえる
  python -X utf8 scripts/tx-gist-story.py check   <file>...               # 構造検査（G81 と同じ式）
  python -X utf8 scripts/tx-gist-story.py materials <_lex.html>          # 執筆用の素材抜き出し（TJR-G の headless 用）
  python -X utf8 scripts/tx-gist-story.py scope   <_lex.html> [--ref HEAD] # 変更が GIST 行と CSS 区画だけか git と照合
  python -X utf8 scripts/tx-gist-story.py pending [--json|--unreplaceable] # 旧型 GIST が残る v13 _lex（TJR-G の対象）

spec.json:
  {"track": ["令状の種類", "許される要件", "実施の仕方"],          # 問題の段階（2〜4 段・体系マップの枝と同じ区分）
   "cards": {"1": {"mark": "×", "head": "…", "now": 0, "question": "…",
                   "scene": "…", "issue": "…", "answer": "…", "why": "…",
                   "terms": [["語", "定義"], …], "image": "…", "judge": "…"}, …}}

apply の安全装置（どれかに当たれば 1 字も書かない）:
  - ファイルの全カードの GIST 行を行単位で特定できる（article が行の途中から始まっても可。GIST が他の要素と
    同じ行に乗っている形は行置換できない＝NG）
  - 仕様がファイルの全カード（data-stmt）をちょうど覆う
  - mark が正誤表 tr[data-verdict] の正解と同じ向き（o→○ / x→×）
  - 旧 GIST にあったリンクの id（BASIS の「戻る」の戻り先）が新 GIST にそのまま残り、旧 GIST のリンク先
    （href="#…"）が書き換え後のファイルのどこかから引き続きリンクされている
  - 本文フィールドは 1 行・許可タグ（strong/b/em/a）のみ・タグの開閉がそろう。track と用語は素のテキスト
改行様式は行ごとに保持（本文行の CR とインデントを残す）。冪等（同じ仕様で再実行しても差分 0）。

scope（TJR-G のランナーが合否に使う）:
  - git の ref（既定 HEAD）と比べ、GIST 行と CSS 区画（＋ensure_css が足す改行 1 つ）以外が 1 字も変わっていない
  - ストーリー型の GIST 行が、仕様から組み直した HTML と完全一致する（手書き・行末への追記を弾く）
  - ストーリー型の GIST に出てくる判例の日付が、GIST の外（BASIS・段階解説・答案圧縮など）にもある
    （headless には判例検索手段が無い＝ファイル外の判例を新しく持ち込ませない）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tx_gist_story as G  # noqa: E402

# 行の途中から始まる article も拾う（刑TX366-385 は「</div></article><article …」、刑TX159・刑訴TX323 は
# 「<div class="tx-inline-list"><article …」が 1 行＝行頭一致だと取りこぼした・2026-09-17 レビュー指摘）
# 属性の並び順にも依存しない（刑TX360・371 は id="stmt-1" data-stmt="1" の順）
ART_RE = re.compile(r'<article\b(?=[^>]*\bclass="tx-inline-card")[^>]*\bdata-stmt="([^"]+)"')
LEAD_PREFIXES = ('<p class="syn-lead">', '<div class="syn-lead tx-gist">')
V13_STAMP = re.compile(r"TX v13\.\d+\.\d+ LOOP-CARD")
LEX_GLOB = "outputs/ux/000_TX/*/*_lex.html"
HREF_RE = re.compile(r'href="(#[^"]+)"')


def verdicts(text: str) -> dict[str, str]:
    out = {}
    for m in re.finditer(r'<tr\b[^>]*\bdata-stmt="([^"]+)"[^>]*\bdata-verdict="([ox])"', text):
        out.setdefault(m.group(1), m.group(2))
    return out


def card_labels(text: str) -> list[str]:
    seen, out = set(), []
    for m in ART_RE.finditer(text):
        if m.group(1) not in seen:
            seen.add(m.group(1))
            out.append(m.group(1))
    return out


def lead_lines(lines: list[str]) -> dict[str, int]:
    """data-stmt → GIST 行の添字（各 article の後で最初に現れる、GIST で始まる行）。"""
    found, cur = {}, None
    for i, ln in enumerate(lines):
        ms = list(ART_RE.finditer(ln))
        if ms:
            cur = ms[-1].group(1)   # 1 行に複数あれば最後に開いたカード
            continue                # article と同じ行の GIST は行置換できない＝拾わない（layout_problems で NG）
        if cur is not None and cur not in found and ln.lstrip().startswith(LEAD_PREFIXES):
            found[cur] = i
    return found


def layout_problems(text: str, lines: list[str], where: dict[str, int]) -> list[str]:
    missing = [lab for lab in card_labels(text) if lab not in where]
    if missing:
        return [f"記述{','.join(missing)} の GIST 行を行単位で特定できない（GIST が他の要素と同じ行にある等）"
                "＝このツールでは書き換えられない。仕様の直しでは解決しないので V14G_FAIL にする"]
    bad = [lab for lab, i in where.items() if not lines[i].rstrip().endswith(("</p>", "</div>"))]
    if bad:
        return [f"記述{','.join(bad)} の旧 GIST が 1 行に収まっていない（行末が </p> でない）＝行置換できない"]
    return []


def cmd_apply(path: Path, spec_path: Path, dry: bool) -> int:
    raw = path.read_bytes().decode("utf-8")
    try:
        spec = G.load_spec(spec_path)
    except G.SpecError as e:
        print(f"NG {e}")
        return 2
    track = spec.get("track")
    problems = G.track_problems(track)
    track = track if isinstance(track, list) else []
    cards = spec.get("cards") or {}
    lines = raw.split("\n")
    where = lead_lines(lines)
    problems += layout_problems(raw, lines, where)
    if not problems and set(where) != set(cards):
        problems.append(f"仕様のカード {sorted(cards)} がファイルのカード {sorted(where)} と一致しない")
    vd = verdicts(raw)
    for label, card in cards.items():
        if not isinstance(card, dict):
            problems.append(f"記述{label}: カードの仕様がオブジェクトでない")
            continue
        problems += G.spec_problems(card, track, label)
        want = G.VERDICT_TO_MARK.get(vd.get(label, ""))
        if want and card.get("mark") != want:
            problems.append(f"記述{label}: mark {card.get('mark')} が正誤表の正解 {want} と逆")
    if problems:
        print("\n".join("NG " + p for p in problems))
        return 2

    changed = 0
    old_targets: set[str] = set()
    for label, idx in where.items():
        old = lines[idx]
        cr = "\r" if old.endswith("\r") else ""
        indent = old[:len(old) - len(old.lstrip())]
        new = G.render_card(cards[label], track)
        old_ids = set(re.findall(r'<a\b[^>]*\bid="([^"]+)"', old))
        lost = sorted(i for i in old_ids if f'id="{i}"' not in new)
        if lost:
            problems.append(f"記述{label}: 旧 GIST のリンクの id {lost} が新 GIST に無い（BASIS の「戻る」の戻り先が切れる。"
                            "<a …> を id・href ごと逐語で残す）")
            continue
        old_targets |= set(HREF_RE.findall(old))
        if old.strip() != new:
            lines[idx] = indent + new + cr
            changed += 1
    text = "\n".join(lines)
    unlinked = sorted(t for t in old_targets if f'href="{t}"' not in text)
    if unlinked:
        problems.append(f"旧 GIST からのリンク先 {unlinked} がファイルのどこからもリンクされなくなる"
                        "（id の無いリンクも <a …> ごと GIST のどこかに残す）")
    if problems:
        print("\n".join("NG " + p for p in problems))
        return 2
    text, css_changed = G.ensure_css(text, G.canonical_css())
    if dry:
        print(f"DRY {path.name}: カード {changed} 枚を書き換え・CSS {'更新' if css_changed else '据置'}")
        return 0
    if changed or css_changed:
        path.write_bytes(text.encode("utf-8"))
    print(f"OK {path.name}: カード {changed} 枚を書き換え・CSS {'更新' if css_changed else '据置'}")
    return 0


def cmd_extract(path: Path) -> int:
    raw = path.read_bytes().decode("utf-8")
    lines = raw.split("\n")
    track, cards = None, {}
    for label, idx in lead_lines(lines).items():
        ln = lines[idx].strip()
        if not ln.startswith(LEAD_PREFIXES[1]):
            continue
        card, steps = G.extract_card(ln)
        track = track or steps
        cards[label] = card
    print(json.dumps({"track": track or [], "cards": cards}, ensure_ascii=False, indent=1))
    return 0


def classify(root: Path) -> tuple[list[Path], list[Path]]:
    """(TJR-G の対象, 旧型 GIST はあるが行構造のせいでツールが書き換えられないファイル)。
    v13 でない旧版は R（再生成）の領分なので数えない。"""
    todo, stuck = [], []
    for p in sorted(root.glob(LEX_GLOB)):
        raw = p.read_bytes().decode("utf-8", errors="replace")
        if '<p class="syn-lead">' not in raw or not V13_STAMP.search(raw):
            continue
        lines = raw.split("\n")
        where = lead_lines(lines)
        has_old = any(lines[i].lstrip().startswith(LEAD_PREFIXES[0]) for i in where.values())
        if layout_problems(raw, lines, where):
            stuck.append(p)
        elif has_old:
            todo.append(p)
    return todo, stuck


def pending_files(root: Path) -> list[Path]:
    return classify(root)[0]


def cmd_pending(root: Path, as_json: bool, unreplaceable: bool) -> int:
    todo, stuck = classify(root)
    rel = lambda p: str(p.relative_to(root)).replace("\\", "/")
    if as_json:
        print(json.dumps([rel(p) for p in (stuck if unreplaceable else todo)], ensure_ascii=False))
        return 0
    if unreplaceable:
        print("\n".join(rel(p) for p in stuck))
        return 0
    by = {}
    for p in todo:
        by[p.parent.name] = by.get(p.parent.name, 0) + 1
    print(f"旧型 THE GIST の v13 _lex: {len(todo)} 本 " + " / ".join(f"{k} {v}" for k, v in sorted(by.items())))
    if stuck:
        print(f"（行構造のせいでツールが書き換えられない {len(stuck)} 本は対象外＝--unreplaceable で一覧）")
    return 0


def _strip_gist(text: str) -> tuple[str, list[str]]:
    """(GIST 行と CSS 区画を除いた本文, ストーリー型 GIST 行の一覧)。
    ensure_css は区画の直後に改行を 1 つ足して </style> 行の前へ挿し込むので、区画と一緒にその改行も落とす
    （base/new の両方に同じ規則を当てる＝区画を新規挿入したファイルを誤って NG にしない）。"""
    lines = text.split("\n")
    where = lead_lines(lines)
    drop = set(where.values())
    story = [lines[i].strip() for i in sorted(drop) if lines[i].lstrip().startswith(LEAD_PREFIXES[1])]
    kept = "\n".join(ln for i, ln in enumerate(lines) if i not in drop)
    r = G.region(kept)
    if r is None:
        return kept, story
    tail = kept[r[1]:]
    tail = tail[2:] if tail.startswith("\r\n") else (tail[1:] if tail[:1] in ("\n", "\r") else tail)
    return kept[:r[0]] + tail, story


def cmd_scope(path: Path, ref: str) -> int:
    """作業ツリーの変更が GIST 行と CSS 区画だけで、GIST が仕様どおりの HTML かを git の ref（既定 HEAD）と照合する。"""
    import subprocess
    top = subprocess.run(["git", "-C", str(path.resolve().parent), "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, encoding="utf-8").stdout.strip()
    rel = path.resolve().relative_to(Path(top).resolve()).as_posix()
    base = subprocess.run(["git", "-C", top, "show", f"{ref}:{rel}"], capture_output=True)
    if base.returncode != 0:
        print(f"NG {path.name}: {ref} に {rel} が無い")
        return 2
    new_raw = path.read_bytes().decode("utf-8")
    a, _ = _strip_gist(base.stdout.decode("utf-8"))
    b, story = _strip_gist(new_raw)
    problems = []
    if a != b:
        al, bl = a.split("\n"), b.split("\n")
        diff = next((i for i, (x, y) in enumerate(zip(al, bl)) if x != y), min(len(al), len(bl)))
        problems.append(f"THE GIST 以外が変わっている（GIST 除去後の {diff + 1} 行目付近）\n"
                        f"   before: {al[diff][:160] if diff < len(al) else '(EOF)'}\n"
                        f"   after : {bl[diff][:160] if diff < len(bl) else '(EOF)'}")
    tracks = set()
    for ln in story:
        card, steps = G.extract_card(ln)
        tracks.add(tuple(steps))
        try:
            again = G.render_card(card, steps)
        except Exception:
            again = None
        if again != ln:
            problems.append("ストーリー型 GIST 行が仕様から組んだ HTML と一致しない（手書き・行への追記・壊れたタグ）"
                            f"：{ln[:120]}…")
            break
    if len(tracks) > 1:
        problems.append("カードごとに 🧭 現在地の段階が違う")
    if story:
        outside = G.citations(b)
        inside = set().union(*(G.citations(ln) for ln in story))
        new_cites = sorted(inside - outside)
        if new_cites:
            problems.append("GIST にだけ出てくる判例 " + "・".join(G.format_citation(c) for c in new_cites) +
                            "（BASIS・段階解説・答案圧縮に無い判例は持ち込まない）")
    if problems:
        print(f"NG {path.name}: " + "\n   ".join(problems))
        return 1
    print(f"OK {path.name}: 変更は THE GIST 行と CSS 区画だけ（GIST は仕様どおり・判例はファイル内のものだけ）")
    return 0


def cmd_materials(path: Path) -> int:
    """headless 執筆用の素材抜き出し（40 万字の HTML を丸読みさせない）。"""
    from bs4 import BeautifulSoup

    def txt(el, limit=0):
        if el is None:
            return ""
        t = re.sub(r"\s+", " ", el.get_text(" ", strip=True))
        return (t[:limit] + "…") if limit and len(t) > limit else t

    soup = BeautifulSoup(path.read_bytes().decode("utf-8"), "html.parser")
    out = [f"# {txt(soup.title)}（{path.name}）"]
    block = soup.select_one(".tx-original-block")
    if block is not None:
        out.append("\n## 設問・問題文（冒頭）\n" + txt(block, 900))
    else:
        out.append("\n## 設問（冒頭）\n" + txt(soup.select_one(".tx-original-lead") or soup.select_one("#part-a p"), 400))
    svg = soup.select_one(".tx-sysmap svg")
    if svg is not None:
        labels = [re.sub(r"\s+", " ", t.get_text(" ", strip=True)) for t in svg.select("text")]
        out.append("\n## 体系マップの文字（track はこの枝の区分に合わせる）\n" + " ｜ ".join(x for x in labels if x))
    narr = soup.select_one(".fa-narrative")
    if narr is not None:
        out.append("\n## 物語解説")
        for p in narr.select("p"):
            lab = p.get("data-fa-label")
            out.append(f"- {('【' + lab + '】') if lab else ''}{txt(p, 500)}")
    vd = {tr.get("data-stmt"): tr.get("data-verdict") for tr in soup.select("tr[data-stmt][data-verdict]")}
    for card in soup.select(".tx-inline-card[data-stmt]"):
        n = card.get("data-stmt")
        ans = {"o": "○", "x": "×"}.get(vd.get(n), "?")
        out.append(f"\n## 記述 {n}（正解 {ans}＝mark はこれにする）")
        out.append("- 記述本文: " + txt(card.select_one(".tx-inline-stmt-text")))
        out.append("- 判定バッジ: " + txt(card.select_one(".tx-v13-verdict")))
        out.append("- 記述原文＋答案圧縮: " + txt(card.select_one(".syn-orig")))
        old = card.select_one(".syn-lead")
        if old is not None:
            anchors = [str(a) for a in old.select("a[href], a[id]")]
            out.append("- 旧 THE GIST: " + txt(old))
            if anchors:
                out.append("- 旧 GIST のリンク（id・href とも変えずに <a …>…</a> ごと新 GIST のどこかに残す）: " + " ".join(anchors))
        for sel, name in ((".syn-path", "段階解説"), (".syn-image", "🗝記憶のフック（image はこれと同じ像）"),
                          (".choice-points", "POINT"), (".tx-v13-trap", "間違いやすいポイント"),
                          (".tx-v13-cross", "他科目横断")):
            el = card.select_one(sel)
            if el is not None:
                out.append(f"- {name}: " + txt(el, 900))
        for item in card.select(".tx-basis-item"):
            cls = item.get("class") or []
            kind = "判例" if "is-case" in cls else ("学説" if "is-theory" in cls else "条文")
            out.append(f"- BASIS〔{kind}〕{txt(item.select_one('.tx-basis-head'))}: {txt(item.select_one('.tx-basis-honbun'), 500)}"
                       f" ／注記: {txt(item.select_one('.tx-basis-note'), 400)}")
    print("\n".join(out))
    return 0


def cmd_css(paths: list[Path], check: bool) -> int:
    css = G.canonical_css()
    bad = 0
    for p in paths:
        raw = p.read_bytes().decode("utf-8")
        if check and G.region(raw) is None and "tx-gist-head" not in raw:
            continue   # ストーリー型を使っていないファイルは対象外
        new, changed = G.ensure_css(raw, css)
        if changed:
            bad += 1
            if not check:
                p.write_bytes(new.encode("utf-8"))
            print(("NG " if check else "UPDATED ") + str(p))
    return 1 if (check and bad) else 0


def cmd_check(paths: list[Path]) -> int:
    from bs4 import BeautifulSoup
    bad = 0
    for p in paths:
        raw = p.read_bytes().decode("utf-8")
        soup = BeautifulSoup(raw, "html.parser")
        vd = {tr.get("data-stmt"): tr.get("data-verdict") for tr in soup.select("tr[data-stmt][data-verdict]")}
        tracks, old, out = set(), [], []
        for card in soup.select(".tx-inline-card[data-stmt]"):
            label = card.get("data-stmt")
            lead = card.select_one(".syn-lead")
            if lead is None:
                continue
            if "tx-gist" not in (lead.get("class") or []):
                old.append(label)
                continue
            probs, track = G.structure_problems(lead, vd.get(label))
            tracks.add(track)
            out += [f"記述{label}: {x}" for x in probs]
        gist_n = len(soup.select(".syn-lead.tx-gist"))
        if gist_n and G.region(raw) is None:
            out.append("CSS 区画 TX-GIST-STORY が無い")
        if len(tracks) > 1:
            out.append(f"カードごとに 🧭 現在地の段階が違う: {sorted(tracks)}")
        if gist_n and old:
            out.append(f"旧型 GIST が残るカード: {old}（一部だけストーリー型）")
        status = "NG" if out else ("OK" if gist_n else "--")
        print(f"{status} {p.name}: ストーリー型 {gist_n} 枚" + ("".join("\n   " + x for x in out)))
        bad += bool(out)
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply"); a.add_argument("file"); a.add_argument("--spec", required=True); a.add_argument("--dry-run", action="store_true")
    e = sub.add_parser("extract"); e.add_argument("file")
    c = sub.add_parser("css"); c.add_argument("files", nargs="+"); c.add_argument("--check", action="store_true")
    k = sub.add_parser("check"); k.add_argument("files", nargs="+")
    m = sub.add_parser("materials"); m.add_argument("file")
    sc = sub.add_parser("scope"); sc.add_argument("file"); sc.add_argument("--ref", default="HEAD")
    pe = sub.add_parser("pending"); pe.add_argument("--root", default=str(G.REPO))
    pe.add_argument("--json", action="store_true"); pe.add_argument("--unreplaceable", action="store_true")
    ns = ap.parse_args()
    if ns.cmd == "apply":
        return cmd_apply(Path(ns.file), Path(ns.spec), ns.dry_run)
    if ns.cmd == "extract":
        return cmd_extract(Path(ns.file))
    if ns.cmd == "css":
        return cmd_css([Path(f) for f in ns.files], ns.check)
    if ns.cmd == "materials":
        return cmd_materials(Path(ns.file))
    if ns.cmd == "scope":
        return cmd_scope(Path(ns.file), ns.ref)
    if ns.cmd == "pending":
        return cmd_pending(Path(ns.root), ns.json, ns.unreplaceable)
    return cmd_check([Path(f) for f in ns.files])


if __name__ == "__main__":
    sys.exit(main())
