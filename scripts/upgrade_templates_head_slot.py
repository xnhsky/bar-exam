#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8 テンプレの head 領域 (867 bytes / 9 行) を {{HEAD}} 化する（Phase 4-10）。

head は check_template_sync.py の sync-required 領域、8 templates 完全 byte-identical
(hash=ccd63a7fba54)。本パッチは全 8 同一 OLD 文字列を共通 NEW = {{HEAD}} に置換するため
sync 維持される。

byte-identical 復元の前提:
  - render.py 側 render_head(problem) が Python .format() で 4 個の動的値
    ({{JP_PREFIX}}/{{PROBLEM_ID}}/{{CRIME}}/{{SOURCE_ID}}) を埋め込んだ完成 HTML を返す
    (Phase 4-10 Commit 2 で実装、全 15 件で byte-identical 検証済)
  - OLD は最後の <link> タグ閉じ `>` で終わる (no trailing \\n)。次行の `<style>` は
    body_pre_toc/css 領域。NEW = {{HEAD}} の直後の \\n は template が持つ。

旧 4 slot ({{JP_PREFIX}}/{{PROBLEM_ID}}/{{CRIME}}/{{SOURCE_ID}}) は body_pre_toc /
footer-spec 等で他参照あり据え置き。本 slot は経路の重複となるが許容。broken
intermediate state は発生しない (Commit 2 完了直後でも render 動作)。

dry-run:
  python scripts/upgrade_templates_head_slot.py --dry-run
apply:
  python scripts/upgrade_templates_head_slot.py
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

# 9 行 literal head block ({{JP_PREFIX}} 等 4 placeholder 込み)。
# 8 templates すべてに同 byte 列で存在することは事前検証で hash=ccd63a7fba54 実証済。
# title 行の括弧は全角「（」「）」を厳守。
OLD = (
    '<!DOCTYPE html>\n'
    '<html lang="ja">\n'
    '<head>\n'
    '<meta charset="UTF-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    '<title>{{JP_PREFIX}}{{PROBLEM_ID}} - {{CRIME}}（{{SOURCE_ID}}）</title>\n'
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@400;500;700;800&family=Shippori+Antique&family=Zen+Old+Mincho:wght@400;500;700;900&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Zen+Maru+Gothic:wght@400;500;700&family=Noto+Serif+JP:wght@400;500;700&family=Noto+Sans+JP:wght@400;500;700&family=Kaisei+Decol:wght@400;500;700&family=Kosugi+Maru&family=Source+Code+Pro:wght@400;600;700&family=M+PLUS+Rounded+1c:wght@500;700;800&family=M+PLUS+1p:wght@500;700;800;900&display=swap" rel="stylesheet">'
)

NEW = '{{HEAD}}'


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
    print(f"=== upgrade_templates_head_slot.py {mode} ===")
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
        print("  FAIL: at least one template did not match expected OLD head block.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
