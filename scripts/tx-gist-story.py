#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THE GIST ストーリー型（TX-GIST-STORY・§v14）の適用・抽出・検査ツール。

使い方:
  python -X utf8 scripts/tx-gist-story.py apply   <_lex.html> --spec <spec.json> [--dry-run]
  python -X utf8 scripts/tx-gist-story.py extract <_lex.html>            # 生成済み GIST → JSON 仕様
  python -X utf8 scripts/tx-gist-story.py css     <file>... [--check]     # CSS 区画を正典（GENESIS-CARD）へそろえる
  python -X utf8 scripts/tx-gist-story.py check   <file>...               # 構造検査（G81 と同じ式）

spec.json:
  {"track": ["令状の種類", "許される要件", "実施の仕方"],          # 問題の段階（2〜4 段・体系マップの枝と同じ区分）
   "cards": {"1": {"mark": "×", "head": "…", "now": 0, "question": "…",
                   "scene": "…", "issue": "…", "answer": "…", "why": "…",
                   "terms": [["語", "定義"], …], "image": "…", "judge": "…"}, …}}

apply の安全装置（どれかに当たれば 1 字も書かない）:
  - 仕様がファイルの全カード（data-stmt）をちょうど覆う
  - mark が正誤表 tr[data-verdict] の正解と同じ向き（o→○ / x→×）
  - 旧 GIST にあった ref-stat の id（BASIS の「戻る」の戻り先）が新 GIST にそのまま残る
  - 本文フィールドは 1 行・許可タグ（strong/b/em/a）のみ
改行様式は行ごとに保持（本文行の CR を残す）。冪等（同じ仕様で再実行しても差分 0）。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tx_gist_story as G  # noqa: E402

ART_RE = re.compile(r'<article class="tx-inline-card" data-stmt="([^"]+)"')
LEAD_PREFIXES = ('<p class="syn-lead">', '<div class="syn-lead tx-gist">')


def verdicts(text: str) -> dict[str, str]:
    out = {}
    for m in re.finditer(r'<tr\b[^>]*\bdata-stmt="([^"]+)"[^>]*\bdata-verdict="([ox])"', text):
        out.setdefault(m.group(1), m.group(2))
    return out


def lead_lines(lines: list[str]) -> dict[str, int]:
    """data-stmt → GIST 行の添字（各 article 内の最初の syn-lead 行）。"""
    found, cur = {}, None
    for i, ln in enumerate(lines):
        m = ART_RE.match(ln)
        if m:
            cur = m.group(1)
            continue
        if cur is not None and cur not in found and ln.startswith(LEAD_PREFIXES):
            found[cur] = i
    return found


def cmd_apply(path: Path, spec_path: Path, dry: bool) -> int:
    raw = path.read_bytes().decode("utf-8")
    spec = G.load_spec(spec_path)
    track = spec.get("track")
    problems = []
    if not (isinstance(track, list) and G.TRACK_MIN <= len(track) <= G.TRACK_MAX
            and all(isinstance(t, str) and t.strip() for t in track)):
        problems.append(f"track は {G.TRACK_MIN}〜{G.TRACK_MAX} 段の文字列配列")
        track = track if isinstance(track, list) else []
    cards = spec.get("cards") or {}
    lines = raw.split("\n")
    where = lead_lines(lines)
    if set(where) != set(cards):
        problems.append(f"仕様のカード {sorted(cards)} がファイルのカード {sorted(where)} と一致しない")
    vd = verdicts(raw)
    for label, card in cards.items():
        problems += G.spec_problems(card, track, label)
        want = G.VERDICT_TO_MARK.get(vd.get(label, ""))
        if want and card.get("mark") != want:
            problems.append(f"記述{label}: mark {card.get('mark')} が正誤表の正解 {want} と逆")
    if problems:
        print("\n".join("NG " + p for p in problems))
        return 2

    changed = 0
    for label, idx in where.items():
        old = lines[idx]
        cr = "\r" if old.endswith("\r") else ""
        new = G.render_card(cards[label], track)
        old_ids = set(re.findall(r'<a\b[^>]*\bid="(ref-[^"]+)"', old))
        lost = sorted(i for i in old_ids if f'id="{i}"' not in new)
        if lost:
            problems.append(f"記述{label}: 旧 GIST の ref-stat id {lost} が新 GIST に無い（BASIS の戻り先が切れる）")
            continue
        if old.rstrip("\r") != new:
            lines[idx] = new + cr
            changed += 1
    if problems:
        print("\n".join("NG " + p for p in problems))
        return 2
    text = "\n".join(lines)
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
        ln = lines[idx].rstrip("\r")
        if not ln.startswith(LEAD_PREFIXES[1]):
            continue
        card, steps = G.extract_card(ln)
        track = track or steps
        cards[label] = card
    print(json.dumps({"track": track or [], "cards": cards}, ensure_ascii=False, indent=1))
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
    ns = ap.parse_args()
    if ns.cmd == "apply":
        return cmd_apply(Path(ns.file), Path(ns.spec), ns.dry_run)
    if ns.cmd == "extract":
        return cmd_extract(Path(ns.file))
    if ns.cmd == "css":
        return cmd_css([Path(f) for f in ns.files], ns.check)
    return cmd_check([Path(f) for f in ns.files])


if __name__ == "__main__":
    sys.exit(main())
