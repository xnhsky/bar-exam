#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8 テンプレの marker-legend block を {{MARKER_LEGEND}} 化する（Phase 4-5）。

marker-legend は check_template_sync.py の sync-required 領域。8 templates すべてに
同一 byte 列で存在（sha256 hash 1 種、universal content）。本パッチは全 8 同一 OLD
文字列を同一 NEW 文字列に置換するため sync 維持される。

byte-identical 復元の前提:
  - render.py 側 render_marker_legend() が 11 行 (709 bytes) の MARKER_LEGEND_DEFAULT
    を {{MARKER_LEGEND}} slot に注入することで、既存 14 件 + 300 すべて byte-identical
    で復元される。
  - 戻り値末尾に \\n を含めない（OLD の最終行が `  </div>` で終わり次行は元から別の
    HTML 要素のため、NEW = `{{MARKER_LEGEND}}` の直後 \\n は template 側が持つ）。

dry-run:
  python scripts/upgrade_templates_marker_legend_slot.py --dry-run
apply:
  python scripts/upgrade_templates_marker_legend_slot.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"

TEMPLATES = [
    "KTX_template.html",
    "KTX_template_ox4.html",
    "KTX_template_msel5.html",
    "KTX_template_sc5.html",
    "KTX_template_comb5.html",
    "KTX_template_fillin.html",
    "KTX_template_ox3comb8.html",
    "KTX_template_fillin8.html",
]

# 11 行リテラル marker-legend block（check_template_sync.py の marker_legend 領域）。
# 8 templates すべてに同 byte 列で存在することは hash=db531d3cae で実証済。
OLD = (
    '  <div class="marker-legend" aria-label="マーカー凡例">\n'
    '    <span class="lg-title">凡例</span>\n'
    '    <span class="lg-item"><span class="lg-sample lg-ron">論</span>論文関連</span>\n'
    '    <span class="lg-divider">|</span>\n'
    '    <span class="lg-item"><span class="exam-mark freq-high">高</span>短答頻出</span>\n'
    '    <span class="lg-item"><span class="exam-mark freq-mid">中</span>標準</span>\n'
    '    <span class="lg-item"><span class="exam-mark freq-low">低</span>関連</span>\n'
    '    <span class="lg-divider">|</span>\n'
    '    <span class="lg-item"><span class="statute-emphasis freq-high">条</span>条文</span>\n'
    '    <span class="lg-item"><span class="case-emphasis freq-high">判</span>判例</span>\n'
    '  </div>'
)

NEW = '{{MARKER_LEGEND}}'


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    results: list[tuple[str, str, int]] = []
    for fname in TEMPLATES:
        fp = TEMPLATES_DIR / fname
        original = fp.read_text(encoding="utf-8")
        if NEW in original and OLD not in original:
            results.append((fname, "ALREADY", 0))
            continue
        if OLD not in original:
            results.append((fname, "MISS", 0))
            continue
        patched = original.replace(OLD, NEW, 1)
        size_delta = len(patched.encode("utf-8")) - len(original.encode("utf-8"))
        if not dry_run:
            fp.write_text(patched, encoding="utf-8")
        results.append((fname, "OK", size_delta))

    width = max(len(f) for f in TEMPLATES)
    mode = "[DRY-RUN]" if dry_run else "[APPLY]"
    print(f"=== upgrade_templates_marker_legend_slot.py {mode} ===")
    print(f"  OLD: {len(OLD)} chars, {OLD.count(chr(10))} newlines")
    print(f"  NEW: {len(NEW)} chars, {NEW.count(chr(10))} newlines")
    print()
    ok = sum(1 for _, s, _ in results if s == "OK")
    already = sum(1 for _, s, _ in results if s == "ALREADY")
    miss = sum(1 for _, s, _ in results if s == "MISS")
    for fname, status, delta in results:
        sign = "+" if delta >= 0 else ""
        print(f"  {status:<8}  {fname:<{width}}  bytes delta {sign}{delta}")
    print()
    print(f"  Summary: OK={ok}  ALREADY={already}  MISS={miss}  /  {len(TEMPLATES)} templates")
    if miss:
        print("  FAIL: at least one template did not match expected OLD block.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
