#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8 テンプレの PART B basis スタブを slot 化する（Phase 3-2）。

各 <section class="section" id="basis"> の内側にある TODO コメント 1 行を {{BASIS_CARDS}}
に置換する。nav / h2 / back-to-top は template に温存（nav は 6 variants の差分許容
セクション、template 固有の back-link を維持するため slot 範囲外とする）。

byte-identical 復元の前提:
  - render.py 側で slots["BASIS_CARDS"] = '    <!-- TODO: Phase 2 で JSON schema 拡張、本実装 -->'
    を供給すると既存 14 件と完全に同一バイト列を再生する。

dry-run:
  python scripts/upgrade_templates_basis_slot.py --dry-run
apply:
  python scripts/upgrade_templates_basis_slot.py
"""
import sys
import re
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

# basis セクション内の TODO コメント行（4-space indent + literal）。
# この 1 行を {{BASIS_CARDS}} に置換する。
OLD_LINE = '    <!-- TODO: Phase 2 で JSON schema 拡張、本実装 -->'
NEW_LINE = '{{BASIS_CARDS}}'

# 置換スコープ判定用に <section id="basis"> ブロックを取り出す regex。
BASIS_RE = re.compile(
    r'(<section class="section" id="basis">)([\s\S]*?)(</section>)',
    re.MULTILINE,
)


def patch_one(text: str) -> tuple[str, str]:
    """テンプレ全文を受け取り、(new_text, status) を返す。"""
    m = BASIS_RE.search(text)
    if not m:
        return text, "MISS_SECTION"
    open_tag, inner, close_tag = m.group(1), m.group(2), m.group(3)
    if NEW_LINE in inner:
        return text, "ALREADY"
    if OLD_LINE not in inner:
        return text, "MISS_TODO"
    new_inner = inner.replace(OLD_LINE, NEW_LINE, 1)
    new_section = open_tag + new_inner + close_tag
    new_text = text[: m.start()] + new_section + text[m.end():]
    return new_text, "OK"


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    results: list[tuple[str, str, int]] = []
    for fname in TEMPLATES:
        fp = TEMPLATES_DIR / fname
        original = fp.read_text(encoding="utf-8")
        patched, status = patch_one(original)
        size_delta = len(patched.encode("utf-8")) - len(original.encode("utf-8"))
        if status == "OK" and not dry_run:
            fp.write_text(patched, encoding="utf-8")
        results.append((fname, status, size_delta))

    width = max(len(f) for f in TEMPLATES)
    mode = "[DRY-RUN]" if dry_run else "[APPLY]"
    print(f"=== upgrade_templates_basis_slot.py {mode} ===")
    print(f"  OLD: {OLD_LINE!r}")
    print(f"  NEW: {NEW_LINE!r}")
    print()
    ok = sum(1 for _, s, _ in results if s == "OK")
    already = sum(1 for _, s, _ in results if s == "ALREADY")
    miss = sum(1 for _, s, _ in results if s.startswith("MISS"))
    for fname, status, delta in results:
        sign = "+" if delta >= 0 else ""
        print(f"  {status:<8}  {fname:<{width}}  bytes delta {sign}{delta}")
    print()
    print(f"  Summary: OK={ok}  ALREADY={already}  MISS={miss}  /  {len(TEMPLATES)} templates")
    if miss:
        print("  FAIL: at least one template did not match expected stub.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
