#!/usr/bin/env python3
"""Phase 13C: gold standard (_experimental/刑TX303-gold.html) から 3 SVG の inner content を
抽出し、problems/303.json の mindmap_tree / mindmap_radial / flowchart_v2 に
svg_override_inner / svg_viewbox / svg_defs_html フィールドとして注入する。

あわせて Bug-2: case.scenes (α 方式タイトル付き場面) を追加する。

usage:
    python scripts/_phase13c_inject_gold_svg.py

idempotent: 同じ値で何度実行しても結果同一。
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOLD = ROOT / "_experimental" / "刑TX303-gold.html"
JSON_PATH = ROOT / "problems" / "303.json"


def extract_svg_block(html: str, marker_section_id: str | None, svg_class: str) -> dict:
    """Return dict with viewbox / defs_html / body_html for one SVG.

    For tree / radial: locates section via id, then nested <svg class=...>.
    For flow: no section wrapper context — locate by svg class directly inside c-5.
    """
    if marker_section_id:
        # Find <section id="..."> ... </section> block
        sec_re = re.compile(
            rf'<section[^>]*id="{re.escape(marker_section_id)}"[^>]*>(.+?)</section>',
            re.DOTALL,
        )
        m = sec_re.search(html)
        if not m:
            raise RuntimeError(f"section #{marker_section_id} not found")
        scope = m.group(1)
    else:
        scope = html

    svg_re = re.compile(
        rf'<svg[^>]*class="{re.escape(svg_class)}"[^>]*viewBox="([^"]+)"[^>]*>(.+?)</svg>',
        re.DOTALL,
    )
    m = svg_re.search(scope)
    if not m:
        # try alternate attribute order
        svg_re2 = re.compile(
            rf'<svg[^>]*viewBox="([^"]+)"[^>]*class="{re.escape(svg_class)}"[^>]*>(.+?)</svg>',
            re.DOTALL,
        )
        m = svg_re2.search(scope)
    if not m:
        raise RuntimeError(f"svg.{svg_class} not found in scope")

    viewbox = m.group(1).strip()
    inner = m.group(2)

    # Split inner into defs vs body
    defs_re = re.compile(r"<defs>(.+?)</defs>", re.DOTALL)
    dm = defs_re.search(inner)
    if dm:
        defs_html = dm.group(1).rstrip("\n")
        # strip leading newline + the defs block itself from body
        body_html = (inner[: dm.start()] + inner[dm.end():]).strip("\n")
    else:
        defs_html = ""
        body_html = inner.strip("\n")

    return {
        "svg_viewbox": viewbox,
        "svg_defs_html": defs_html,
        "svg_override_inner": body_html,
    }


def main() -> None:
    html = GOLD.read_text(encoding="utf-8")
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    # 1. Tree
    tree_fields = extract_svg_block(html, "mindmap-tree", "tree-svg")
    data.setdefault("mindmap_tree", {})
    for k, v in tree_fields.items():
        data["mindmap_tree"][k] = v

    # 2. Radial
    radial_fields = extract_svg_block(html, "mindmap-radial", "radial-svg")
    data.setdefault("mindmap_radial", {})
    for k, v in radial_fields.items():
        data["mindmap_radial"][k] = v

    # 3. Flow
    flow_fields = extract_svg_block(html, "c-5", "flow-svg")
    data.setdefault("flowchart_v2", {})
    for k, v in flow_fields.items():
        data["flowchart_v2"][k] = v

    # 4. case.scenes (Bug-2 α 化)
    scene_titles = [
        "場面 1 — 不動産の詐取（甲 → A）",
        "場面 2 — 乙への転売（甲 → 乙、詐欺取得物の処分）",
        "場面 3 — 丙の代金受領（甲の指示による）",
        "場面 4 — 丙の馬券費消（横領）",
    ]
    case = data.get("case") or {}
    paragraphs = case.get("paragraphs", [])
    if paragraphs and len(scene_titles) == len(paragraphs):
        case["scenes"] = [
            {"title": scene_titles[i], "body": paragraphs[i]}
            for i in range(len(paragraphs))
        ]
        data["case"] = case
        print(f"case.scenes 設定: {len(case['scenes'])} 場面")
    else:
        print(
            f"warn: paragraphs={len(paragraphs)} != titles={len(scene_titles)}, "
            f"scenes 設定 skip"
        )

    JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK: {JSON_PATH}")
    print(
        f"  tree     viewBox={tree_fields['svg_viewbox']}  "
        f"defs={len(tree_fields['svg_defs_html'])} bytes  "
        f"body={len(tree_fields['svg_override_inner'])} bytes"
    )
    print(
        f"  radial   viewBox={radial_fields['svg_viewbox']}  "
        f"defs={len(radial_fields['svg_defs_html'])} bytes  "
        f"body={len(radial_fields['svg_override_inner'])} bytes"
    )
    print(
        f"  flow     viewBox={flow_fields['svg_viewbox']}  "
        f"defs={len(flow_fields['svg_defs_html'])} bytes  "
        f"body={len(flow_fields['svg_override_inner'])} bytes"
    )


if __name__ == "__main__":
    main()
