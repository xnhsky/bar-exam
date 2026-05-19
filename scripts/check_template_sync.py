#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_template_sync.py — 5 本立て template の同期義務違反を検出する。

slotmap §5.10 の設計合意に基づき、`templates/KTX_template*.html` を 13 論理セクションに
分割し、同期義務セクション (HEAD / CSS / body_pre_toc / marker_legend / pre_part_a /
part_c_d / footer_spec / JS) の SHA256 hash が 5 本すべてで一致するかを検証する。

差分許容セクション (toc / part_a / a2 / part_b / basis) は slotmap §5.1 §3 / §5.2 §3 /
§5.3 §3 / §5.4 §3 の意図差分テーブルに従う設計のため、内容の差は許容し、
種類数 (unique hash 数) のみ情報報告する。

Usage:
    python scripts/check_template_sync.py
    python scripts/check_template_sync.py --format=markdown --timing
    python scripts/check_template_sync.py --format=json

Exit codes:
    0: sync OK (同期義務違反なし)
    1: sync 違反検出 (unexpected diff あり)
    2: 実行エラー (file not found / parse error 等)
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
import time
from collections import Counter
from itertools import combinations
from pathlib import Path


# ============================================================================
# パス設定
# ============================================================================

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"
TEMPLATE_FILES = [
    "KTX_template.html",
    "KTX_template_ox4.html",
    "KTX_template_msel5.html",
    "KTX_template_sc5.html",
    "KTX_template_comb5.html",
    "KTX_template_fillin.html",   # 6 本目 (slotmap §6.6、fill-in 形式、KEN 等)
    "KTX_template_ox3comb8.html", # 7 本目 (slotmap §6.7、ox-grid-3 + combination-8、GSE)
    "KTX_template_fillin8.html",  # 8 本目 (slotmap §6.6b、fillin8 = 8 blanks + 5 options、KEIS)
]


# ============================================================================
# 意図差分仕様 (slotmap §5.10 §3)
# ============================================================================
# 本 dict は slotmap.md §5.1 §3 / §5.2 §3 / §5.3 §3 / §5.4 §3 の写しである。
# slotmap 更新時は本 dict も同期手動更新すること。
# 二重管理リスクは slotmap §5.10 §4 R1 として認識、将来 YAML front-matter 化 / dict を
# source of truth 化 を slotmap §5.10「将来の一般化」に明記。

INTENTIONAL_DIFFS: dict[str, dict] = {
    # 同期義務セクション (5 本で byte-identical を要求)
    "head":          {"sync_required": True,  "note": "DOCTYPE 〜 <style> 直前"},
    "css":           {"sync_required": True,  "note": "<style>...</style> 内側"},
    "body_pre_toc":  {"sync_required": True,  "note": "</style> 〜 TOC bar 直前"},
    "marker_legend": {"sync_required": True,  "note": "marker-legend ブロック"},
    "part_c_d":      {"sync_required": True,  "note": "basis end 〜 footer 直前 (PART C + PART D スタブ)"},
    "footer_spec":   {"sync_required": True,  "note": "footer-spec ブロック"},
    "js":            {"sync_required": True,  "note": "<script>...</script> 内側"},
    # 差分許容セクション (slotmap §5.1-§5.4 §3 の意図差分テーブルに従う)
    "toc":           {"sync_required": False, "note": "TOC ラベル系統差 (ア〜オ / 1〜5)"},
    "pre_part_a":    {"sync_required": False, "note": "PART A 見出しコメント差 (ox-grid-5 / -4 / multi / single / combination / fill-in / ox3comb8)"},
    "part_a":        {"sync_required": False, "note": "PART A 問題情報、形式別 (見解 / 組合せ section / 空欄 / N=3 等)"},
    "a2":            {"sync_required": False, "note": "A-2 解答エリア構造差 (ox-grid / multi / single / fill-in / ox3comb8)"},
    "part_b":        {"sync_required": False, "note": "PART B choice-section 件数 / ラベル系統差 (記述 / 空欄 / N=3)"},
    "basis":         {"sync_required": False, "note": "A-3 sec-nav back-link 差 (記述オ / 記述エ / 記述5 / 空欄E / 記述ウ 等)"},
}


# ============================================================================
# 論理セクション分割 (slotmap §5.10 §2)
# ============================================================================

def _find_line_idx(lines: list[str], pattern: str, start: int = 0) -> int:
    """最初に regex pattern にマッチする行の index を返す。なければ -1。"""
    pat = re.compile(pattern)
    for i in range(start, len(lines)):
        if pat.search(lines[i]):
            return i
    return -1


def split_template(content: str) -> dict[str, str]:
    """template を 13 論理セクションに分割する。

    境界マーカー優先順位 (slotmap §5.10 §2): id > class > comment。
    CRLF は LF に正規化し、cross-platform 一貫性を確保。
    """
    # 改行コード正規化 (R6: CRLF / LF 混在対策)
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    lines = content.split("\n")

    # 境界 index の検出
    style_open = _find_line_idx(lines, r"<style>")
    style_close = _find_line_idx(lines, r"</style>")
    # Phase 4-6 以降: toc-row が {{TOC_ROW}} に slot 化されていれば単一行を
    # セクションとして扱う。レガシー (slot 化前) の <div class="toc-row"> にも
    # フォールバック対応。
    toc_slot_idx = _find_line_idx(lines, r"\{\{TOC_ROW\}\}")
    if toc_slot_idx >= 0:
        toc_open = toc_slot_idx
        toc_close = toc_slot_idx
    else:
        toc_open = _find_line_idx(lines, r'<div class="toc-row">')
        toc_close = _find_line_idx(lines, r"</div>", toc_open + 1) if toc_open >= 0 else -1
    # Phase 4-5 以降: marker-legend が {{MARKER_LEGEND}} に slot 化されていれば
    # 単一行をセクションとして扱う。レガシー (slot 化前) の <div class="marker-legend">
    # にもフォールバック対応。
    ml_slot_idx = _find_line_idx(lines, r"\{\{MARKER_LEGEND\}\}")
    if ml_slot_idx >= 0:
        marker_legend_open = ml_slot_idx
        marker_legend_close = ml_slot_idx
    else:
        marker_legend_open = _find_line_idx(lines, r'<div class="marker-legend"')
        marker_legend_close = (
            _find_line_idx(lines, r"</div>", marker_legend_open + 1)
            if marker_legend_open >= 0
            else -1
        )
    part_a_title = _find_line_idx(lines, r'<div class="part-title">PART A')
    answer_area_section = _find_line_idx(lines, r'<section[^>]+id="answer-area"')
    # A-2 内側に nested section は無い前提 (slotmap §5.10 §2: a2 sliced from
    # answer_area_section to first </section> after it)
    answer_area_close = (
        _find_line_idx(lines, r"^\s*</section>\s*$", answer_area_section + 1)
        if answer_area_section >= 0
        else -1
    )
    basis_section = _find_line_idx(lines, r'<section[^>]+id="basis"')
    basis_close = (
        _find_line_idx(lines, r"^\s*</section>\s*$", basis_section + 1)
        if basis_section >= 0
        else -1
    )
    footer_open = _find_line_idx(lines, r'class="footer-spec"')
    script_open = _find_line_idx(lines, r"<script>")
    script_close = _find_line_idx(lines, r"</script>")

    # 全ての必須境界が検出されたかチェック
    required = {
        "style_open": style_open,
        "style_close": style_close,
        "toc_open": toc_open,
        "toc_close": toc_close,
        "marker_legend_open": marker_legend_open,
        "marker_legend_close": marker_legend_close,
        "part_a_title": part_a_title,
        "answer_area_section": answer_area_section,
        "answer_area_close": answer_area_close,
        "basis_section": basis_section,
        "basis_close": basis_close,
        "footer_open": footer_open,
        "script_open": script_open,
        "script_close": script_close,
    }
    missing = [k for k, v in required.items() if v < 0]
    if missing:
        raise ValueError(f"境界マーカー検出失敗: {missing}")

    def joined(start: int, end_exclusive: int) -> str:
        return "\n".join(lines[start:end_exclusive])

    sections = {
        "head":          joined(0, style_open),
        "css":           joined(style_open + 1, style_close),
        "body_pre_toc":  joined(style_close + 1, toc_open),
        "toc":           joined(toc_open, toc_close + 1),
        "marker_legend": joined(marker_legend_open, marker_legend_close + 1),
        "pre_part_a":    joined(marker_legend_close + 1, part_a_title),
        "part_a":        joined(part_a_title, answer_area_section),
        "a2":            joined(answer_area_section, answer_area_close + 1),
        "part_b":        joined(answer_area_close + 1, basis_section),
        "basis":         joined(basis_section, basis_close + 1),
        "part_c_d":      joined(basis_close + 1, footer_open),
        "footer_spec":   joined(footer_open, script_open),
        "js":            joined(script_open + 1, script_close),
    }
    return sections


def hash_section(content: str) -> str:
    """SHA256 hash (hex, lowercase)。"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ============================================================================
# 検証 (slotmap §5.10 §3)
# ============================================================================

def validate_sync(
    templates: dict[str, dict[str, str]],
) -> tuple[list[dict], list[dict]]:
    """5 本立て template の同期義務違反を検出する。

    Returns:
        (violations, intentional_diffs_summary)
    """
    violations: list[dict] = []
    diffs_summary: list[dict] = []

    for section_name, spec in INTENTIONAL_DIFFS.items():
        hashes = {
            fname: hash_section(sections[section_name])
            for fname, sections in templates.items()
        }
        unique = set(hashes.values())

        if spec["sync_required"]:
            if len(unique) > 1:
                # 同期義務違反: hash が分裂している
                cnt = Counter(hashes.values())
                canonical_hash, canonical_count = cnt.most_common(1)[0]
                outliers = sorted(
                    [fn for fn, h in hashes.items() if h != canonical_hash]
                )
                violations.append(
                    {
                        "section": section_name,
                        "unique_hashes_count": len(unique),
                        "canonical_hash": canonical_hash[:16] + "...",
                        "canonical_count": canonical_count,
                        "outliers": outliers,
                        "all_hashes": {
                            fn: h[:16] + "..." for fn, h in hashes.items()
                        },
                        "note": spec["note"],
                    }
                )
        else:
            # 差分許容セクション: 情報報告のみ
            diffs_summary.append(
                {
                    "section": section_name,
                    "unique_hashes_count": len(unique),
                    "note": spec["note"],
                }
            )

    return violations, diffs_summary


# ============================================================================
# 10 ペア diff 計測 (slotmap §5.10 §5)
# ============================================================================

def measure_pair_diffs(template_paths: dict[str, Path]) -> dict:
    """C(5,2) = 10 ペアの diff 行数と実行時間を計測する (raw template 比較)。

    実装ポイント:
      - difflib.unified_diff (n=0、純粋な diff のみ)
      - time.perf_counter (μs 精度)
      - 改行コード正規化 (R6 対策)
    """
    raw_lines: dict[str, list[str]] = {}
    for fname, path in template_paths.items():
        text = path.read_text(encoding="utf-8-sig")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        raw_lines[fname] = text.split("\n")

    pairs_data: list[dict] = []
    filenames = list(template_paths.keys())
    for a, b in combinations(filenames, 2):
        lines_a = raw_lines[a]
        lines_b = raw_lines[b]

        t_start = time.perf_counter()
        diff = list(difflib.unified_diff(lines_a, lines_b, n=0, lineterm=""))
        t_end = time.perf_counter()

        # +/- 行のみカウント (+++ / --- ヘッダーは除外)
        diff_count = sum(
            1
            for line in diff
            if (line.startswith("+") or line.startswith("-"))
            and not line.startswith(("+++", "---"))
        )
        ms = (t_end - t_start) * 1000.0
        pairs_data.append(
            {
                "a": a,
                "b": b,
                "diff_lines": diff_count,
                "time_ms": round(ms, 3),
            }
        )

    times = [p["time_ms"] for p in pairs_data]
    return {
        "pairs": pairs_data,
        "total_ms": round(sum(times), 3),
        "mean_ms": round(sum(times) / len(times), 3) if times else 0.0,
        "median_ms": round(sorted(times)[len(times) // 2], 3) if times else 0.0,
        "n_pairs": len(pairs_data),
    }


# ============================================================================
# 出力フォーマッタ (slotmap §5.10 §5: text / json / markdown)
# ============================================================================

def emit_text(
    violations: list[dict],
    diffs_summary: list[dict],
    timing: dict | None,
) -> None:
    """text フォーマット (人間向け CI ログ)。"""
    print("=== check_template_sync.py ===")
    print(f"Templates: {len(TEMPLATE_FILES)} files in {TEMPLATES_DIR}")
    print()
    print("--- Sync-required sections ---")
    section_to_violation = {v["section"]: v for v in violations}
    for sec_name, spec in INTENTIONAL_DIFFS.items():
        if not spec["sync_required"]:
            continue
        v = section_to_violation.get(sec_name)
        if v:
            print(
                f"  [VIOLATION] {sec_name:14s} : "
                f"{v['unique_hashes_count']} variants  outliers={v['outliers']}"
            )
        else:
            print(f"  [OK]        {sec_name:14s} : all {len(TEMPLATE_FILES)} match")
    print()
    print("--- Diff-allowed sections (informational, follows slotmap §5.N §3) ---")
    for d in diffs_summary:
        print(
            f"  [{d['unique_hashes_count']} variants]  "
            f"{d['section']:14s} : {d['note']}"
        )
    if timing:
        print()
        print("--- Pair diff timing (10 pairs) ---")
        for p in timing["pairs"]:
            print(
                f"  {p['a']:33s} vs {p['b']:33s} : "
                f"{p['diff_lines']:4d} lines, {p['time_ms']:7.3f} ms"
            )
        print(
            f"  Total: {timing['total_ms']:.3f} ms / "
            f"Mean: {timing['mean_ms']:.3f} ms / "
            f"Median: {timing['median_ms']:.3f} ms"
        )
    print()
    if violations:
        print(f"=== Result: FAIL ({len(violations)} sync violation(s), exit 1) ===")
    else:
        print("=== Result: PASS (exit 0) ===")


def emit_json(
    violations: list[dict],
    diffs_summary: list[dict],
    timing: dict | None,
) -> None:
    """json フォーマット (機械可読 / CI ログ集計用)。"""
    result = {
        "sync_required_sections": [
            s for s, spec in INTENTIONAL_DIFFS.items() if spec["sync_required"]
        ],
        "diff_allowed_sections": [
            s for s, spec in INTENTIONAL_DIFFS.items() if not spec["sync_required"]
        ],
        "violations": violations,
        "diff_allowed_summary": diffs_summary,
        "timing": timing,
        "pass": len(violations) == 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def emit_markdown(
    violations: list[dict],
    diffs_summary: list[dict],
    timing: dict | None,
) -> None:
    """markdown フォーマット (slotmap §5.N §8 への貼り付け用)。"""
    print("### check_template_sync.py 実行結果")
    print()
    print(f"- **同期義務違反**: {len(violations)} 件")
    print(f"- **意図差分セクション**: {len(diffs_summary)} 件")
    if violations:
        print()
        print("#### 違反詳細")
        print()
        print("| Section | Variants | Outliers |")
        print("|---|---:|---|")
        for v in violations:
            outliers = ", ".join(v["outliers"])
            print(
                f"| {v['section']} | {v['unique_hashes_count']} | {outliers} |"
            )
    print()
    print("#### 意図差分サマリ (情報報告、slotmap §5.N §3 に従う)")
    print()
    print("| Section | Unique variants | Note |")
    print("|---|---:|---|")
    for d in diffs_summary:
        print(f"| {d['section']} | {d['unique_hashes_count']} | {d['note']} |")
    if timing:
        print()
        print("#### 10 ペア diff timing")
        print()
        print("| Pair (A vs B) | Diff lines | Time (ms) |")
        print("|---|---:|---:|")
        for p in timing["pairs"]:
            print(
                f"| {p['a']} vs {p['b']} | {p['diff_lines']} | {p['time_ms']} |"
            )
        print()
        print(
            f"**Total**: {timing['total_ms']} ms / "
            f"**Mean**: {timing['mean_ms']} ms / "
            f"**Median**: {timing['median_ms']} ms"
        )


# ============================================================================
# エントリポイント
# ============================================================================

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="5 本立て template の同期義務違反を検出 (slotmap §5.10)。"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="出力フォーマット (デフォルト: text)",
    )
    parser.add_argument(
        "--timing",
        action="store_true",
        help="10 ペア diff の実行時間を計測して報告に含める",
    )
    args = parser.parse_args(argv[1:])

    # template 読込
    templates: dict[str, dict[str, str]] = {}
    template_paths: dict[str, Path] = {}
    for fname in TEMPLATE_FILES:
        path = TEMPLATES_DIR / fname
        if not path.exists():
            print(f"ERROR: template not found: {path}", file=sys.stderr)
            return 2
        try:
            # utf-8-sig で BOM があれば吸収 (R7 対策)
            content = path.read_text(encoding="utf-8-sig")
        except Exception as e:
            print(f"ERROR: failed to read {path}: {e}", file=sys.stderr)
            return 2
        try:
            templates[fname] = split_template(content)
            template_paths[fname] = path
        except ValueError as e:
            print(f"ERROR: failed to parse {fname}: {e}", file=sys.stderr)
            return 2

    # 検証
    violations, diffs_summary = validate_sync(templates)

    # 計測 (任意)
    timing = measure_pair_diffs(template_paths) if args.timing else None

    # 出力
    if args.format == "json":
        emit_json(violations, diffs_summary, timing)
    elif args.format == "markdown":
        emit_markdown(violations, diffs_summary, timing)
    else:
        emit_text(violations, diffs_summary, timing)

    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
