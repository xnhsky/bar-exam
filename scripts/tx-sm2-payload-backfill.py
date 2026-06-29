#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX360 inline _lex の SM2 用 payload を ox-row へ注入する。

Lexia の stmt 抽出は `.ox-pool-explain` がある場合、それを GIST/POINT の
最優先ソースにする。TX360 型では PART B 長文ではなく、裏の
`.statement-verdict-table` の `.tx-reflex-core` とインライン面の
`.tx-cycle-aids` を通常 SM2 カード本文に渡したいので、各 `.ox-row` 直下へ
記号フリーの `.ox-pool-explain` を追加する。

公式 outputs/000_TX は対象外。`*_lex.html` かつ inline-prototype-mode のみ処理する。
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 が必要です。pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


ROOT = Path(__file__).resolve().parents[1]


def text_of(el) -> str:
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip() if el else ""


def line_without_tag(line) -> tuple[str, str]:
    tag = line.select_one(".tx-reflex-tag")
    label = text_of(tag)
    clone = BeautifulSoup(str(line), "html.parser")
    for t in clone.select(".tx-reflex-tag"):
        t.decompose()
    body = text_of(clone)
    return label, body


def extract_payloads(src: str) -> tuple[dict[str, str], list[str]]:
    soup = BeautifulSoup(src, "html.parser")
    path_errors: list[str] = []
    area = soup.select_one('.answer-area.inline-prototype-mode[data-answer-type="ox-grid"]')
    if not area:
        return {}, ["inline-prototype-mode の ox-grid ではないため対象外"]

    payloads: dict[str, str] = {}
    for row in area.select(".answer-ox-grid .ox-row"):
        stmt = (row.get("data-stmt") or "").strip()
        if not stmt:
            continue
        tr = soup.select_one(f'.statement-verdict-table tr[data-stmt="{stmt}"]')
        core = tr.select_one(".tx-reflex-core") if tr else None
        lines = core.select(".tx-reflex-line") if core else []
        points: list[tuple[str, str]] = []
        cut = ""
        transfer = ""
        for line in lines:
            label, body = line_without_tag(line)
            if not label or not body:
                continue
            points.append((label, body))
            if label == "切断点":
                cut = body
            elif label == "転用":
                transfer = body

        card = soup.select_one(f'.tx-inline-card[data-stmt="{stmt}"]')
        if card:
            for p in card.select(".tx-cycle-aids p"):
                label_el = p.select_one(".tx-cycle-label")
                label = text_of(label_el)
                clone = BeautifulSoup(str(p), "html.parser")
                for t in clone.select(".tx-cycle-label"):
                    t.decompose()
                body = text_of(clone)
                if label and body:
                    points.append((label, body))

        if not points:
            path_errors.append(f"stmt {stmt}: tx-reflex-core / tx-cycle-aids が取れない")
            continue

        gist_parts = []
        if cut:
            gist_parts.append("切断点：" + cut)
        if transfer:
            gist_parts.append("転用：" + transfer)
        if not gist_parts:
            gist_parts.append(f"{points[0][0]}：" + points[0][1])
        gist = " ／ ".join(gist_parts)

        lis = "\n".join(
            f'            <li>{html.escape(label, quote=False)}：{html.escape(body, quote=False)}</li>'
            for label, body in points
        )
        payloads[stmt] = (
            '        <div class="ox-pool-explain" data-source="tx360-inline">\n'
            f'          <p class="ox-pool-gist">{html.escape(gist, quote=False)}</p>\n'
            '          <ul class="ox-pool-points">\n'
            f"{lis}\n"
            '          </ul>\n'
            '        </div>'
        )
    return payloads, path_errors


ROW_RE = re.compile(
    r'(?P<head><div class="ox-row" data-stmt="(?P<stmt>[^"]+)">\s*'
    r'(?:<span class="ox-label">.*?</span>\s*)?'
    r'<span class="ox-stmt">.*?</span>\s*'
    r'<span class="ox-btn-group">.*?</span>)'
    r'(?P<tail>\s*</div>)',
    re.S,
)


def inject(src: str, payloads: dict[str, str]) -> tuple[str, int]:
    changed = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal changed
        stmt = m.group("stmt")
        row_html = m.group(0)
        payload = payloads.get(stmt)
        if not payload or "ox-pool-explain" in row_html:
            return row_html
        changed += 1
        return m.group("head") + "\n" + payload + m.group("tail")

    return ROW_RE.sub(repl, src), changed


def process(path: Path, dry_run: bool = False) -> tuple[int, list[str]]:
    rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    if not path.name.endswith("_lex.html"):
        return 0, [f"{rel}: skip (not *_lex.html)"]
    src = path.read_text(encoding="utf-8", errors="replace")
    payloads, errors = extract_payloads(src)
    if errors and not payloads:
        return 0, [f"{rel}: " + "; ".join(errors)]
    out, changed = inject(src, payloads)
    msgs = [f"{rel}: payloads={len(payloads)} injected={changed}"]
    if errors:
        msgs.extend(f"{rel}: WARN {e}" for e in errors)
    if changed and not dry_run:
        path.write_text(out, encoding="utf-8", newline="")
    return changed, msgs


def main() -> int:
    ap = argparse.ArgumentParser(description="TX360 inline _lex に Lexia SM2 用 ox-pool-explain を注入")
    ap.add_argument("paths", nargs="+", help="対象 *_lex.html")
    ap.add_argument("--dry-run", action="store_true", help="書き込まず件数だけ表示")
    args = ap.parse_args()

    total = 0
    for raw in args.paths:
        path = Path(raw)
        if not path.is_absolute():
            path = ROOT / path
        changed, msgs = process(path, args.dry_run)
        total += changed
        for msg in msgs:
            print(msg)
    print(f"changed={total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
