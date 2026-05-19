#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pdf_to_png.py — PDF を 1 ページ 1 PNG に展開する補助スクリプト

Usage:
    python scripts/pdf_to_png.py <pdf_path> <out_dir> [--zoom 2.0]

例:
    python scripts/pdf_to_png.py inputs/tx-pdfs/KEN.pdf _tmp_pdf_pages/KEN

各ページは {out_dir}/page-{NN}.png に保存される（1-origin、2 桁ゼロ埋め）。
画像ベース PDF (Wondershare PDFelement 等) を Claude の image understanding に
渡すための前処理。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz  # type: ignore[import-untyped]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out_dir")
    ap.add_argument("--zoom", type=float, default=2.0,
                    help="rendering zoom factor (default 2.0 = 144 DPI)")
    args = ap.parse_args(argv)

    pdf_path = Path(args.pdf)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    mat = fitz.Matrix(args.zoom, args.zoom)
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        dst = out_dir / f"page-{i:02d}.png"
        pix.save(str(dst))
        print(f"OK: {dst} ({pix.width}x{pix.height})")
    print(f"Total {len(doc)} pages → {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
