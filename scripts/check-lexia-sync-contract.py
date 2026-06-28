#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lexia 同期契約の横断検査（outputs/ + references/）。

Lexia は bar-exam の HTML を path / fileName / code / title / subject / category へ
分類して取り込む。単体 validator では拾いにくい「分類不能」「ID 揺れ」「作成日スタンプ
欠落」「ARIADNE data-rx の誤リンク」「本文不足」を read-only で検出する。

使い方:
  python scripts/check-lexia-sync-contract.py
  python scripts/check-lexia-sync-contract.py --summary
  python scripts/check-lexia-sync-contract.py --strict
  python scripts/check-lexia-sync-contract.py --json deploy/lexia-sync-audit.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = ("outputs", "references")
SKIP_DIR_PARTS = {"_failed", "__pycache__", "_experimental", "_migration"}

SUBJECT_DIR_TO_PREFIX = {
    "001_刑法": "刑",
    "002_刑事訴訟法": "刑訴",
    "003_民法": "民",
    "004_商法": "商",
    "005_民事訴訟法": "民訴",
    "006_行政法": "行政",
    "007_憲法": "憲",
}
PREFIX_TO_SUBJECT_DIR = {v: k for k, v in SUBJECT_DIR_TO_PREFIX.items()}
SUBJECT_LABEL = {k: k.split("_", 1)[1] for k in SUBJECT_DIR_TO_PREFIX}

REF_SUFFIX_TO_CATEGORY = {
    "GDE": "REFERENCE_GDE",
    "RON": "REFERENCE_RON",
    "MTD": "REFERENCE_MTD",
    "TAN": "REFERENCE_TAN",
}

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
GENMETA_RE = re.compile(
    r"<([a-zA-Z][\w-]*)\b[^>]*\bclass=\"[^\"]*\blexia-genmeta\b[^\"]*\"[^>]*>.*?</\1>",
    re.S,
)
DATA_GENERATED_RE = re.compile(r"\bdata-generated=\"([^\"]+)\"")
CODE_TOKEN_RE = re.compile(r"(刑訴|民訴|行政|刑|憲|民|商)(TX|JX|RX)0*(\d{1,4})(?:_0*(\d+))?", re.I)
SCRIPT_RE = re.compile(r"<script\b[^>]*>(.*?)</script>", re.S | re.I)
TAG_RE = re.compile(r"<[^>]+>")
DATA_RX_RE = re.compile(r'data-rx="([^"]*)"')
SELF_CHECK_OPEN_RE = re.compile(r'<div\b[^>]*\bclass="[^"]*\bself-check-quiz\b[^"]*"[^>]*>', re.I)

MIN_BYTES = {
    "TX_OFFICIAL": 20 * 1024,
    "TX_LEXIA": 20 * 1024,
    "JX": 20 * 1024,
    "ARIADNE": 20 * 1024,
    "RX": 4 * 1024,
    "TREE": 30 * 1024,
    "REFERENCE_GDE": 4 * 1024,
    "REFERENCE_RON": 4 * 1024,
    "REFERENCE_MTD": 4 * 1024,
    "REFERENCE_TAN": 4 * 1024,
    "REFERENCE": 4 * 1024,
}


@dataclass
class Entry:
    sourcePath: str
    fileName: str
    code: str
    baseCode: str
    title: str
    subject: str
    subjectDir: str
    category: str
    bytes: int
    generated: str


def relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", s)).strip()


def title_of(html: str) -> str:
    m = TITLE_RE.search(html)
    return strip_tags(m.group(1)) if m else ""


def code_key(s: str) -> tuple[str, str, int, int | None] | None:
    m = CODE_TOKEN_RE.search(s or "")
    if not m:
        return None
    return (m.group(1), m.group(2).upper(), int(m.group(3)), int(m.group(4)) if m.group(4) else None)


def same_code(a: str, b: str) -> bool:
    return code_key(a) is not None and code_key(a) == code_key(b)


def classify(path: Path) -> tuple[dict[str, str], list[str]] | tuple[None, list[str]]:
    rel = relpath(path)
    parts = rel.split("/")
    name = path.name
    stem = path.stem
    warnings: list[str] = []

    def subj_from_dir(subject_dir: str, prefix: str) -> tuple[str, str]:
        expected = SUBJECT_DIR_TO_PREFIX.get(subject_dir)
        if expected is None:
            warnings.append(f"未知の科目ディレクトリ: {subject_dir}")
        elif expected != prefix:
            warnings.append(f"科目ディレクトリとファイル接頭辞が不一致: dir={subject_dir} prefix={prefix}")
        return SUBJECT_LABEL.get(subject_dir, subject_dir), subject_dir

    # outputs/000_TX/{subject}/{prefix}TXNNN.html
    if len(parts) == 4 and parts[0] == "outputs" and parts[1] == "000_TX":
        m = re.fullmatch(r"(.+?)TX(\d{3})\.html", name)
        if not m:
            return None, warnings
        subject, subject_dir = subj_from_dir(parts[2], m.group(1))
        code = f"{m.group(1)}TX{m.group(2)}"
        return dict(category="TX_OFFICIAL", code=code, baseCode=code, subject=subject, subjectDir=subject_dir), warnings

    # outputs/ux/000_TX/{subject}/{prefix}TXNNN_lex.html
    if len(parts) == 5 and parts[:3] == ["outputs", "ux", "000_TX"]:
        m = re.fullmatch(r"(.+?)TX(\d{3})_lex\.html", name)
        if not m:
            return None, warnings
        subject, subject_dir = subj_from_dir(parts[3], m.group(1))
        base = f"{m.group(1)}TX{m.group(2)}"
        return dict(category="TX_LEXIA", code=f"{base}_lex", baseCode=base, subject=subject, subjectDir=subject_dir), warnings

    # outputs/001_JX/{subject}/{prefix}JXNNN.html
    if len(parts) == 4 and parts[0] == "outputs" and parts[1] == "001_JX":
        m = re.fullmatch(r"(.+?)JX(\d{3})\.html", name)
        if not m:
            return None, warnings
        subject, subject_dir = subj_from_dir(parts[2], m.group(1))
        code = f"{m.group(1)}JX{m.group(2)}"
        return dict(category="JX", code=code, baseCode=code, subject=subject, subjectDir=subject_dir), warnings

    # outputs/ux/001_ARIADNE/{subject}/{prefix}JXNNN_ARIADNE.html
    if len(parts) == 5 and parts[:3] == ["outputs", "ux", "001_ARIADNE"]:
        m = re.fullmatch(r"(.+?)JX(\d{3})_ARIADNE\.html", name)
        if not m:
            return None, warnings
        subject, subject_dir = subj_from_dir(parts[3], m.group(1))
        base = f"{m.group(1)}JX{m.group(2)}"
        return dict(category="ARIADNE", code=f"{base}_ARIADNE", baseCode=base, subject=subject, subjectDir=subject_dir), warnings

    # outputs/ux/002_RX/{subject}/{prefix}JXNNN/{prefix}RXNNN_i.html
    if len(parts) == 6 and parts[:3] == ["outputs", "ux", "002_RX"]:
        folder = parts[4]
        mf = re.fullmatch(r"(.+?)JX(\d{3})", folder)
        mn = re.fullmatch(r"(.+?)RX(\d{3})_(\d+)\.html", name)
        if not mf or not mn:
            return None, warnings
        subject, subject_dir = subj_from_dir(parts[3], mn.group(1))
        if mf.group(1) != mn.group(1) or mf.group(2) != mn.group(2):
            warnings.append(f"RX 親 JX フォルダと RX ファイル名が不一致: folder={folder} file={name}")
        base = f"{mn.group(1)}JX{mn.group(2)}"
        code = f"{mn.group(1)}RX{mn.group(2)}_{int(mn.group(3))}"
        return dict(category="RX", code=code, baseCode=base, subject=subject, subjectDir=subject_dir), warnings

    # outputs/ux/003_TREE/{subject}/{prefix}JXNNN_TREE.html
    if len(parts) == 5 and parts[:3] == ["outputs", "ux", "003_TREE"]:
        m = re.fullmatch(r"(.+?)JX(\d{3})_TREE\.html", name)
        if not m:
            return None, warnings
        subject, subject_dir = subj_from_dir(parts[3], m.group(1))
        base = f"{m.group(1)}JX{m.group(2)}"
        return dict(category="TREE", code=f"{base}_TREE", baseCode=base, subject=subject, subjectDir=subject_dir), warnings

    # outputs/ux/004_参考資料/** and references/**
    if parts[:3] == ["outputs", "ux", "004_参考資料"] or parts[0] == "references":
        cat = "REFERENCE"
        for suffix, refcat in REF_SUFFIX_TO_CATEGORY.items():
            if re.search(rf"_{suffix}(?:V\d+)?$|V\d+_{suffix}$|_{suffix}$", stem):
                cat = refcat
                break
        return dict(category=cat, code=stem, baseCode=stem, subject="参考資料", subjectDir=parts[1] if parts[0] == "references" and len(parts) > 1 else "004_参考資料"), warnings

    return None, warnings


def collect_files(roots: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        p = (ROOT / root).resolve()
        if p.is_file() and p.suffix.lower() in (".html", ".htm"):
            if not (SKIP_DIR_PARTS & set(p.parts)):
                files.append(p)
        elif p.is_dir():
            files.extend(sorted(x for x in p.rglob("*.html") if x.is_file() and not (SKIP_DIR_PARTS & set(x.parts))))
            files.extend(sorted(x for x in p.rglob("*.htm") if x.is_file() and not (SKIP_DIR_PARTS & set(x.parts))))
    return sorted(set(files), key=lambda x: x.as_posix())


def genmeta_status(html: str) -> tuple[list[str], str]:
    stamps = GENMETA_RE.findall(html)
    if not stamps:
        return ["lexia-genmeta 作成日フッターが無い"], ""
    problems = []
    if len(stamps) > 1:
        problems.append(f"lexia-genmeta が複数ある: {len(stamps)}")
    all_stamp_text = "\n".join(m.group(0) for m in GENMETA_RE.finditer(html))
    dgs = DATA_GENERATED_RE.findall(all_stamp_text)
    generated = dgs[0] if dgs else ""
    if not dgs:
        problems.append("lexia-genmeta に data-generated が無い")
    if "Generated:" not in all_stamp_text:
        problems.append('lexia-genmeta 本文に "Generated:" が無い')
    if "作成日" in all_stamp_text:
        problems.append("lexia-genmeta が旧日本語 作成日 表記を含む")
    return problems, generated


def script_body_literal(html: str) -> bool:
    return any("</body>" in m.group(1) for m in SCRIPT_RE.finditer(html))


def extract_recall_open_tags(html: str) -> list[str]:
    return [m.group(0) for m in SELF_CHECK_OPEN_RE.finditer(html) if "data-recall" in m.group(0)]


def rx_exists_for(rel: str, rx_code: str) -> bool:
    parts = rel.split("/")
    if len(parts) < 5 or parts[:3] != ["outputs", "ux", "001_ARIADNE"]:
        return True
    m = re.fullmatch(r"(.+?)RX(\d{3})_\d+", rx_code)
    if not m:
        return False
    rx_path = ROOT / "outputs" / "ux" / "002_RX" / parts[3] / f"{m.group(1)}JX{m.group(2)}" / f"{rx_code}.html"
    return rx_path.is_file()


def audit_entry(path: Path) -> tuple[Entry | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    rel = relpath(path)
    meta, classify_warnings = classify(path)
    warnings.extend(classify_warnings)
    if meta is None:
        errors.append("Lexia 取込カテゴリへ分類できないパス/命名")
        return None, errors, warnings

    html = path.read_text(encoding="utf-8", errors="replace")
    title = title_of(html)
    size = len(html.encode("utf-8", "replace"))
    stamp_problems, generated = genmeta_status(html)
    errors.extend(stamp_problems)

    if not title:
        errors.append("<title> が無い/空")
    elif title.lower() in {"document", "untitled", "card"}:
        errors.append(f"<title> がプレースホルダ: {title}")

    min_bytes = MIN_BYTES.get(meta["category"], 4 * 1024)
    if size < min_bytes:
        errors.append(f"HTML 本文不足の疑い: {size}B < {min_bytes}B ({meta['category']})")

    body_text_len = len(strip_tags(html))
    min_text = 500 if meta["category"].startswith("REFERENCE") or meta["category"] == "RX" else 1000
    if body_text_len < min_text:
        errors.append(f"HTML テキスト本文不足の疑い: text={body_text_len} < {min_text}")

    if script_body_literal(html):
        errors.append("<script> 内に </body> リテラルがある（Lexia 挿入処理を壊す）")

    if meta["category"] in {"TX_OFFICIAL", "TX_LEXIA", "JX", "ARIADNE"}:
        if not same_code(meta["baseCode"], title):
            errors.append(f"title の問題コードがファイル名由来 baseCode と一致しない: baseCode={meta['baseCode']} title={title[:80]}")

    if meta["category"] == "ARIADNE":
        target = re.search(r'data-athena-code="([^"]+)"', html)
        if not target:
            warnings.append("data-athena-code が無い（ATHENA ジャンプ不能）")
        elif not same_code(meta["baseCode"], target.group(1)):
            errors.append(f"data-athena-code が baseCode と一致しない: {target.group(1)} != {meta['baseCode']}")

        recall_tags = extract_recall_open_tags(html)
        if recall_tags:
            rx_values = []
            missing = 0
            bad = []
            dangling = []
            expected = re.compile(r"^" + re.escape(meta["baseCode"].replace("JX", "RX")) + r"_\d+$")
            for tag in recall_tags:
                m = DATA_RX_RE.search(tag)
                rx = m.group(1).strip() if m else ""
                if not rx:
                    missing += 1
                    continue
                rx_values.append(rx)
                if not expected.fullmatch(rx):
                    bad.append(rx)
                elif not rx_exists_for(rel, rx):
                    dangling.append(rx)
            if missing == len(recall_tags):
                warnings.append(f"想起カード {len(recall_tags)} 枚すべて data-rx 欠落")
            elif missing:
                warnings.append(f"想起カード data-rx 欠落 {missing}/{len(recall_tags)} 枚")
            if bad:
                errors.append(f"data-rx の科目/JX 不整合: {', '.join(sorted(set(bad))[:8])}")
            if dangling:
                errors.append(f"data-rx 参照先 RX 不在: {', '.join(sorted(set(dangling))[:8])}")
        elif "data-recall" in html:
            warnings.append("data-recall はあるが self-check-quiz recall 開始タグとして抽出できない")

    entry = Entry(
        sourcePath=rel,
        fileName=path.name,
        code=meta["code"],
        baseCode=meta["baseCode"],
        title=title,
        subject=meta["subject"],
        subjectDir=meta["subjectDir"],
        category=meta["category"],
        bytes=size,
        generated=generated,
    )
    return entry, errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Lexia 同期契約の横断検査")
    ap.add_argument("roots", nargs="*", default=list(DEFAULT_ROOTS), help="走査ルート（既定: outputs references）")
    ap.add_argument("--summary", action="store_true", help="問題のあるファイルだけ表示")
    ap.add_argument("--strict", action="store_true", help="WARNING も終了コード 1 にする")
    ap.add_argument("--json", dest="json_path", help="導出メタ情報を JSON で保存")
    args = ap.parse_args()

    files = collect_files(args.roots)
    entries: list[Entry] = []
    per_file: list[tuple[Path, list[str], list[str]]] = []

    for path in files:
        entry, errors, warnings = audit_entry(path)
        if entry:
            entries.append(entry)
        per_file.append((path, errors, warnings))

    # 横断重複: sourcePath / fileName / category+code / title（空 title は単体側で検出）。
    source_paths = defaultdict(list)
    filenames = defaultdict(list)
    ids = defaultdict(list)
    titles = defaultdict(list)
    for e in entries:
        source_paths[e.sourcePath].append(e.sourcePath)
        filenames[e.fileName].append(e.sourcePath)
        ids[(e.category, e.code)].append(e.sourcePath)
        if e.title:
            titles[e.title].append(e.sourcePath)

    global_errors: list[str] = []
    for key, paths in ids.items():
        if len(paths) > 1:
            global_errors.append(f"category+code 重複 {key}: {', '.join(paths[:6])}")
    for name, paths in filenames.items():
        if len(paths) > 1:
            # 同一 fileName は Lexia 側の fileName 表示や差分追跡で紛らわしいため警告ではなくエラー。
            global_errors.append(f"fileName 重複 {name}: {', '.join(paths[:6])}")
    for title, paths in titles.items():
        if len(paths) > 1:
            # 公式 TX と _lex の title 重複は既存 check-duplicates と同様に許容したいが、実際は _lex suffix で
            # title が同一になり得る。その他は Lexia 重複誤認の原因なので検出する。
            cats = {next(e.category for e in entries if e.sourcePath == p) for p in paths}
            base_codes = {next(e.baseCode for e in entries if e.sourcePath == p) for p in paths}
            if not (cats <= {"TX_OFFICIAL", "TX_LEXIA"} and len(base_codes) == 1):
                global_errors.append(f"title 重複 '{title[:80]}': {', '.join(paths[:6])}")

    category_counts = Counter(e.category for e in entries)
    err_count = sum(len(e) for _, e, _ in per_file) + len(global_errors)
    warn_count = sum(len(w) for _, _, w in per_file)

    print("=== Lexia 同期契約チェック ===")
    print(f"roots={', '.join(args.roots)} / html={len(files)} / classified={len(entries)}")
    print("categories: " + ", ".join(f"{k}={v}" for k, v in sorted(category_counts.items())))
    print()

    if global_errors:
        print("[GLOBAL ERROR]")
        for msg in global_errors:
            print(f"  ERROR {msg}")
        print()

    for path, errors, warnings in per_file:
        if args.summary and not errors and not warnings:
            continue
        rel = relpath(path)
        if errors or warnings:
            print(f"[{rel}]")
            for msg in errors:
                print(f"  ERROR {msg}")
            for msg in warnings:
                print(f"  WARN  {msg}")
        elif not args.summary:
            print(f"[OK] {rel}")

    if args.json_path:
        out = ROOT / args.json_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps([asdict(e) for e in entries], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\njson={out.relative_to(ROOT).as_posix()}")

    print("\n=== summary ===")
    print(f"ERROR={err_count}  WARNING={warn_count}")
    if err_count or (args.strict and warn_count):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
