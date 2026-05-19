#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8 テンプレの body_pre_toc 領域 (393 bytes / 12 行) を {{BODY_PRE_TOC}} 化する（Phase 4-8）。

body_pre_toc は check_template_sync.py の sync-required 領域、8 templates 完全
byte-identical (hash=1fb1fe871c7e、Phase 4-8 Commit 2 着手前の事前検証で再確認済)。
本パッチは全 8 同一 OLD 文字列を共通 NEW = {{BODY_PRE_TOC}} に置換するため
sync 維持される。

byte-identical 復元の前提:
  - render.py 側 render_body_pre_toc(problem) が Python .format() で 6 個の動的値
    ({{JP_PREFIX}} 等) を埋め込んだ完成 HTML を返す (Phase 4-8 Commit 2 で実装、
    全 15 件で byte-identical 検証済)
  - OLD は `    </div>` (exam-meta 閉じ、no trailing \\n) で終わる。次行の {{TOC_ROW}} は
    Phase 4-6 で既に slot 化済。NEW = {{BODY_PRE_TOC}} の直後の \\n は template が持つ。

旧 6 slot ({{JP_PREFIX}}/{{PROBLEM_ID}}/{{CRIME}}/{{SOURCE_ID}}/{{CORRECT_RATE}}/
{{OVERRIDE_PATTERN}}) は footer-spec 等で他参照あり据え置き。本 slot は経路の重複と
なるが許容。broken intermediate state は発生しない (Commit 2 完了直後でも render 動作)。

dry-run:
  python scripts/upgrade_templates_body_pre_toc_slot.py --dry-run
apply:
  python scripts/upgrade_templates_body_pre_toc_slot.py
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

# 12 行 literal body_pre_toc block ({{JP_PREFIX}} 等 6 placeholder 込み)。
# 8 templates すべてに同 byte 列で存在することは事前検証で hash=1fb1fe871c7e 実証済。
OLD = (
    '</head>\n'
    '<body id="top">\n'
    '<div class="container">\n'
    '\n'
    '  <!-- HEADER -->\n'
    '  <header class="header">\n'
    '    <div class="doc-header">{{JP_PREFIX}}{{PROBLEM_ID}}</div>\n'
    '    <h1>No.{{PROBLEM_ID}} ── {{CRIME}}（{{SOURCE_ID}}）</h1>\n'
    '    <div class="exam-meta">\n'
    '      <span><strong>正答率:</strong>{{CORRECT_RATE}}</span>\n'
    '      <span><strong>パターン:</strong>{{OVERRIDE_PATTERN}}</span>\n'
    '    </div>'
)

NEW = '{{BODY_PRE_TOC}}'


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
    print(f"=== upgrade_templates_body_pre_toc_slot.py {mode} ===")
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
        print("  FAIL: at least one template did not match expected OLD body_pre_toc block.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
