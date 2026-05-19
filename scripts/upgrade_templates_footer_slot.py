#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8 テンプレの footer-spec 内 feature-tag 列を {{FOOTER_FEATURE_TAGS}} 化する（Phase 4-2）。

footer-spec は check_template_sync.py の sync-required 領域。
8 templates すべてに同一 OLD 文字列があり、同一 NEW 文字列に置換するため
sync 維持される。

byte-identical 復元の前提:
  - render.py 側 render_footer_feature_tags(override_pattern) が
    22 固定文字列 + override_pattern を irregular indent パターンに従って
    23 行の HTML として組み立て、{{FOOTER_FEATURE_TAGS}} slot に注入する。
  - 戻り値は 23 行 \\n 区切り、末尾 \\n なし。template 側の `{{FOOTER_FEATURE_TAGS}}\\n`
    が末尾改行を供給することで byte-identical 復元。

dry-run:
  python scripts/upgrade_templates_footer_slot.py --dry-run
apply:
  python scripts/upgrade_templates_footer_slot.py
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

# 22 固定 feature-tag + 末尾 {{OVERRIDE_PATTERN}} 行から成る 23 行ブロック。
# template の irregular indent (6/0/0/0/0/6/0/6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6) を逐語温存する。
# 末尾行は `</span>\n` で終わり（・ なし）、置換後 `{{FOOTER_FEATURE_TAGS}}\n` が
# 末尾 \n を供給するため、当 OLD も末尾 \n 込みで定義する。
OLD = (
    '      <span class="feature-tag">TX v8.11.7</span>・\n'
    '<span class="feature-tag">spoiler-safe</span>・\n'
    '<span class="feature-tag">a2-two-stage-reveal</span>・\n'
    '<span class="feature-tag">a2-multi-ox-support</span>・\n'
    '<span class="feature-tag">spoiler-leak-eradication</span>・\n'
    '      <span class="feature-tag">spoiler-strong-elimination</span>・\n'
    '<span class="feature-tag">ox-grid-fa-unification</span>・\n'
    '      <span class="feature-tag">spoiler-footer-purge</span>・\n'
    '      <span class="feature-tag">multi-answer-css</span>・\n'
    '      <span class="feature-tag">ktx301-canon</span>・\n'
    '      <span class="feature-tag">ktx-template-canon</span>・\n'
    '      <span class="feature-tag">embedded-canon</span>・\n'
    '      <span class="feature-tag">readability-layer</span>・\n'
    '      <span class="feature-tag">hanging-grid</span>・\n'
    '      <span class="feature-tag">basis-order-v2</span>・\n'
    '      <span class="feature-tag">a2-feedback-canon</span>・\n'
    '      <span class="feature-tag">rbchip-patched</span>・\n'
    '      <span class="feature-tag">k302-immune</span>・\n'
    '      <span class="feature-tag">p2p3-unified</span>・\n'
    '      <span class="feature-tag">p1-absolute</span>・\n'
    '      <span class="feature-tag">jp-prefix-naming</span>・\n'
    '      <span class="feature-tag">content-independence</span>・\n'
    '      <span class="feature-tag">{{OVERRIDE_PATTERN}}</span>\n'
)

NEW = '{{FOOTER_FEATURE_TAGS}}\n'


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
    print(f"=== upgrade_templates_footer_slot.py {mode} ===")
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
