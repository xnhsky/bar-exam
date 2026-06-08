#!/usr/bin/env python3
"""
validate-tts.py - JX→TTS .txt サブパート検証

Usage:
  python scripts/validate-tts.py {OUTPUT_DIR}
      → OUTPUT_DIR 内の全 .txt を PROBLEM_ID 別にグループ化して一括検証
  python scripts/validate-tts.py {OUTPUT_DIR} {PROBLEM_ID}
      → ID 前方一致で対象を絞る（runner 連結時はこちら）

Exit code:
  0 = 全 PASS
  1 = 1 件以上 FAIL
  2 = 引数エラー / ディレクトリ不在 / 対象 0 件
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

CHAR_FLOOR = 1200
CHAR_CEIL = 2500

# 新命名（2026-06-08〜）：{問題ID}-{連番}.txt （フラット通し番号・1 起点・ゼロ埋めなし）
#   例 刑JX029-1.txt … 刑JX029-13.txt
FNAME_PAT = re.compile(r"^(?P<id>.+?)-(?P<seq>\d+)\.txt$")

TAG_CHECKS = [
    ("html_or_ssml_tag", re.compile(r"<[a-zA-Z/!?][^>]*>")),
    ("markdown_bold", re.compile(r"\*\*")),
    ("markdown_underscore", re.compile(r"__")),
    ("markdown_header", re.compile(r"^#", re.MULTILINE)),
    ("markdown_blockquote", re.compile(r"^>", re.MULTILINE)),
    ("bracket_markup", re.compile(r"\[[^\]\n]{1,30}\]")),
]


def count_chars(text: str) -> int:
    """空白除去後の文字数（\\s 全種・全角スペース U+3000 含む）"""
    return len(re.sub(r"\s", "", text))


def check_tags(text: str) -> list[tuple[str, str]]:
    """検出された (種別, サンプル) のリストを返す。空なら 0 件。"""
    findings: list[tuple[str, str]] = []
    for name, pat in TAG_CHECKS:
        m = pat.search(text)
        if m:
            sample = m.group(0)
            if len(sample) > 50:
                sample = sample[:50] + "..."
            findings.append((name, sample))
    return findings


def validate_file(path: Path) -> tuple[bool, list[str], dict | None, int | None]:
    """
    Returns (ok, reasons, parsed, char_count)
      parsed = {'id': str, 'main': int, 'sub': str} or None
    """
    reasons: list[str] = []
    fname = path.name

    m = FNAME_PAT.match(fname)
    if not m:
        reasons.append("filename_format: must be {ID}-{連番}.txt (例 刑JX029-1.txt)")
        return False, reasons, None, None

    parsed = {"id": m.group("id"), "seq": int(m.group("seq"))}

    try:
        text = path.read_text(encoding="utf-8-sig")
    except Exception as e:
        reasons.append(f"read_error: {e}")
        return False, reasons, parsed, None

    n = count_chars(text)
    if n < CHAR_FLOOR:
        reasons.append(f"char_count={n} (below floor {CHAR_FLOOR})")
    elif n > CHAR_CEIL:
        reasons.append(f"char_count={n} (above ceil {CHAR_CEIL})")

    for kind, sample in check_tags(text):
        reasons.append(f"tag_detected[{kind}]: {sample!r}")

    return (len(reasons) == 0), reasons, parsed, n


def validate_group(problem_id: str, members: list[tuple[Path, dict]]) -> list[str]:
    """グループ単位の連番・必須要件検証（フラット通し番号 1..N が欠番なく連続）"""
    reasons: list[str] = []
    seqs = sorted(parsed["seq"] for _, parsed in members)

    if not seqs:
        return ["group: no parseable files"]

    if seqs[0] != 1:
        reasons.append(f"group: 連番 1 missing (starts at {seqs[0]})")

    dup = {s for s in seqs if seqs.count(s) > 1}
    if dup:
        reasons.append(f"group: 連番 重複 {sorted(dup)}")

    max_seq = seqs[-1]
    present = set(seqs)
    for n in range(1, max_seq + 1):
        if n not in present:
            reasons.append(
                f"group: 連番 {n} missing (expected 1..{max_seq} continuous)"
            )

    return reasons


def main() -> int:
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(
            "Usage: python scripts/validate-tts.py {OUTPUT_DIR} [{PROBLEM_ID}]",
            file=sys.stderr,
        )
        return 2

    output_dir = Path(sys.argv[1])
    id_filter = sys.argv[2] if len(sys.argv) == 3 else None

    if not output_dir.is_dir():
        print(f"ERROR: {output_dir} is not a directory", file=sys.stderr)
        return 2

    all_txt = sorted(output_dir.glob("*.txt"))
    if id_filter:
        all_txt = [p for p in all_txt if p.name.startswith(id_filter + "-")]

    if not all_txt:
        msg = f"ERROR: no .txt files found in {output_dir}"
        if id_filter:
            msg += f" for ID {id_filter!r}"
        print(msg, file=sys.stderr)
        return 2

    per_file: list[tuple[Path, bool, list[str], dict | None, int | None]] = []
    groups: dict[str, list[tuple[Path, dict]]] = defaultdict(list)
    file_ok = file_fail = 0

    for path in all_txt:
        ok, reasons, parsed, n = validate_file(path)
        per_file.append((path, ok, reasons, parsed, n))
        if ok:
            file_ok += 1
        else:
            file_fail += 1
        if parsed:
            groups[parsed["id"]].append((path, parsed))

    print("=== Per-file validation ===")
    for path, ok, reasons, _, n in per_file:
        if ok:
            print(f"[OK]   {path.name}  ({n} chars)")
        else:
            print(f"[FAIL] {path.name}")
            for r in reasons:
                print(f"         {r}")

    print()
    print("=== Per-group validation ===")
    group_ok = group_fail = 0
    for gid, members in sorted(groups.items()):
        reasons = validate_group(gid, members)
        if reasons:
            group_fail += 1
            print(f"[FAIL] {gid}  ({len(members)} files)")
            for r in reasons:
                print(f"         {r}")
        else:
            group_ok += 1
            print(f"[OK]   {gid}  ({len(members)} files)")

    total = len(per_file)
    print()
    print("=== Summary ===")
    print(f"Files:  {total} total, {file_ok} OK, {file_fail} FAIL")
    print(f"Groups: {group_ok + group_fail} total, {group_ok} OK, {group_fail} FAIL")

    exit_code = 1 if (file_fail > 0 or group_fail > 0) else 0
    print(f"EXIT {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
