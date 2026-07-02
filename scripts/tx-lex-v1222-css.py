#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TXLEX v12.2.2 CSS injector (deterministic, idempotent).

Injects the 3 gold CSS blocks (base sysmap / 重厚感 override 2 / SVGテーマ統一)
extracted verbatim from the gold sample 刑TX360_lex.html into a target _lex file,
skipping any block already present. Insertion point = just before the first </style>.
Newlines preserved (newline='').

Usage: python -X utf8 scripts/tx-lex-v1222-css.py <target_lex.html> [<target2> ...]
"""
import io, sys, os

GOLD = os.path.join(os.path.dirname(__file__), "..",
                    "outputs", "ux", "000_TX", "001_刑法", "刑TX360_lex.html")

M_BASE = "/* === TX360 体系マップ:"
M_OV2  = "/* === 重厚感 override 2:"
M_SVG  = "/* === SVGノードをテーマ色"


def read(path):
    return io.open(path, encoding="utf-8", newline="").read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def extract_blocks(gold):
    i_base = gold.index(M_BASE)
    i_ov2 = gold.index(M_OV2, i_base)
    i_svg = gold.index(M_SVG, i_ov2)
    i_end = gold.index("</style>", i_svg)
    return {
        "base": gold[i_base:i_ov2],
        "ov2": gold[i_ov2:i_svg],
        "svg": gold[i_svg:i_end],
    }


def main():
    gold = read(GOLD)
    blocks = extract_blocks(gold)
    targets = sys.argv[1:]
    if not targets:
        print("usage: tx-lex-v1222-css.py <file> [...]"); sys.exit(2)
    for path in targets:
        h = read(path)
        inject = []
        # base sysmap CSS: skip if file already defines .tx-sysmap{
        if ".tx-sysmap{" not in h:
            inject.append(("base", blocks["base"]))
        if "重厚感 override 2" not in h:
            inject.append(("ov2", blocks["ov2"]))
        if "SVGノードをテーマ色" not in h:
            inject.append(("svg", blocks["svg"]))
        if not inject:
            print("[SKIP] %s (all 3 blocks present)" % path); continue
        payload = "".join(b for _, b in inject)
        pos = h.index("</style>")
        h2 = h[:pos] + payload + h[pos:]
        write(path, h2)
        print("[OK] %s injected: %s" % (path, ",".join(k for k, _ in inject)))


if __name__ == "__main__":
    main()
