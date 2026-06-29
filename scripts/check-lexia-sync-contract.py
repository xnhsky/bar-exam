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
  python scripts/check-lexia-sync-contract.py --json deploy/lexia-sync-manifest.json --json-format manifest
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = ("outputs", "references")
SCHEMA_VERSION = "lexia-sync-contract/v3"
ENTRY_JSON_FIELDS = (
    "sourcePath",
    "fileName",
    "code",
    "baseCode",
    "title",
    "subject",
    "subjectDir",
    "category",
    "bytes",
    "textLength",
    "stableSha256",
    "generated",
)
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
    r"<([a-zA-Z][\w-]*)\b[^>]*\bclass\s*=\s*(['\"])[^'\"]*\blexia-genmeta\b[^'\"]*\2[^>]*>.*?</\1>",
    re.S | re.I,
)
DATA_GENERATED_RE = re.compile(r"\bdata-generated\s*=\s*(['\"])(.*?)\1", re.I | re.S)
DATA_GENERATED_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2})$")
GENERATED_DISPLAY_RE = re.compile(r"Generated:\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}")
CODE_TOKEN_RE = re.compile(r"(刑訴|民訴|行政|刑|憲|民|商)(KJX|TX|JX|RX)0*(\d{1,4})(?:_0*(\d+))?", re.I)
SCRIPT_RE = re.compile(r"<script\b[^>]*>(.*?)</script>", re.S | re.I)
TAG_RE = re.compile(r"<[^>]+>")
ATTR_RE_TEMPLATE = r"\b{name}\s*=\s*(['\"])(.*?)\1"
CLASS_RE = re.compile(ATTR_RE_TEMPLATE.format(name="class"), re.I | re.S)
DATA_RX_RE = re.compile(ATTR_RE_TEMPLATE.format(name="data-rx"), re.I | re.S)
DATA_RECALL_RE = re.compile(ATTR_RE_TEMPLATE.format(name="data-recall"), re.I | re.S)
DATA_ATHENA_CODE_RE = re.compile(ATTR_RE_TEMPLATE.format(name="data-athena-code"), re.I | re.S)
DIV_OPEN_RE = re.compile(r"<div\b[^>]*>", re.I | re.S)
ARIADNE_RX_MAP_PATH = ROOT / "scripts" / "ariadne-backfill-rx-link.py"
ARIADNE_RX_MAP: dict[str, list[str | None]] | None = None
EMPTY_BLOB_SHA1 = "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"

MIN_BYTES = {
    "TX_OFFICIAL": 20 * 1024,
    "TX_LEXIA": 20 * 1024,
    "JX": 20 * 1024,
    "KJX": 20 * 1024,
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
    textLength: int
    stableSha256: str
    generated: str


@dataclass
class AuditResult:
    files: list[Path]
    entries: list[Entry]
    per_file: list[tuple[Path, Entry | None, list[str], list[str]]]
    global_errors: list[str]
    global_warnings: list[str]
    category_counts: Counter

    @property
    def error_count(self) -> int:
        return sum(len(errors) for _path, _entry, errors, _warnings in self.per_file) + len(self.global_errors)

    @property
    def warning_count(self) -> int:
        return sum(len(warnings) for _path, _entry, _errors, warnings in self.per_file) + len(self.global_warnings)


def relpath(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def write_text_if_changed(path: Path, text: str) -> bool:
    try:
        if path.exists() and path.read_text(encoding="utf-8") == text:
            return False
    except OSError:
        pass
    path.write_text(text, encoding="utf-8")
    return True


def strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", s)).strip()


def title_of(html: str) -> str:
    m = TITLE_RE.search(html)
    return strip_tags(m.group(1)) if m else ""


def normalize_genmeta_for_stable_hash(html: str) -> str:
    def normalize_block(match: re.Match[str]) -> str:
        block = DATA_GENERATED_RE.sub('data-generated="<generated>"', match.group(0))
        return GENERATED_DISPLAY_RE.sub("Generated: <generated>", block)

    return GENMETA_RE.sub(normalize_block, html)


def first_attr_value(pattern: re.Pattern[str], text: str) -> str | None:
    m = pattern.search(text)
    return m.group(2) if m else None


def attr_values(pattern: re.Pattern[str], text: str) -> list[str]:
    return [m.group(2) for m in pattern.finditer(text)]


def has_class(tag: str, class_name: str) -> bool:
    classes = first_attr_value(CLASS_RE, tag)
    return bool(classes and class_name in re.split(r"\s+", classes.strip()))


def stable_content_sha256(html: str) -> str:
    return hashlib.sha256(normalize_genmeta_for_stable_hash(html).encode("utf-8")).hexdigest()


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

    # outputs/{NNN}_KJX/{subject}/{prefix}KJXNNN.html
    # KJX は論文過去問系の予約分類。実出力が増えても Lexia 側の category/code が揺れないよう、
    # 数字 prefix は固定せず NNN_KJX を受ける。
    if len(parts) == 4 and parts[0] == "outputs" and re.fullmatch(r"\d{3}_KJX", parts[1]):
        m = re.fullmatch(r"(.+?)KJX(\d{3})\.html", name)
        if not m:
            return None, warnings
        subject, subject_dir = subj_from_dir(parts[2], m.group(1))
        code = f"{m.group(1)}KJX{m.group(2)}"
        return dict(category="KJX", code=code, baseCode=code, subject=subject, subjectDir=subject_dir), warnings

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


def normalize_git_path(path_arg: str) -> str | None:
    path = Path(path_arg)
    abs_path = path if path.is_absolute() else ROOT / path
    try:
        return abs_path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None


def git_tracked_paths(roots: Iterable[str]) -> set[str] | None:
    if not (ROOT / ".git").exists():
        return None
    root_args = [p for p in (normalize_git_path(root) for root in roots) if p]
    if not root_args:
        return None
    try:
        completed = subprocess.run(
            ["git", "ls-files", "-z", "--stage", "--", *root_args],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return parse_git_stage_paths(completed.stdout)


def parse_git_stage_paths(output: bytes) -> set[str]:
    return {
        path.replace("\\", "/")
        for item in output.decode("utf-8", "replace").split("\0")
        if item
        for meta, sep, path in [item.partition("\t")]
        if sep
        for fields in [meta.split()]
        if len(fields) >= 3 and fields[1] != EMPTY_BLOB_SHA1
    }


def find_untracked_sync_files(files: Iterable[Path], tracked_paths: set[str] | None) -> list[str]:
    if tracked_paths is None:
        return []
    missing = []
    for path in files:
        rel = relpath(path)
        if rel not in tracked_paths:
            missing.append(rel)
    return sorted(missing)


def summarize_paths(paths: Iterable[str], limit: int = 12) -> str:
    vals = sorted(set(paths))
    shown = ", ".join(vals[:limit])
    if len(vals) > limit:
        shown += f", ... (+{len(vals) - limit})"
    return shown or "—"


def sorted_entries(entries: Iterable[Entry]) -> list[Entry]:
    return sorted(entries, key=lambda e: (e.sourcePath, e.category, e.code, e.fileName))


def entry_to_json(entry: Entry) -> dict[str, object]:
    raw = asdict(entry)
    return {field: raw[field] for field in ENTRY_JSON_FIELDS}


def entries_json(entries: Iterable[Entry]) -> list[dict[str, object]]:
    return [entry_to_json(entry) for entry in sorted_entries(entries)]


def text_density(entry: Entry) -> float:
    return entry.textLength / entry.bytes if entry.bytes > 0 else 0.0


def low_text_entries(entries: Iterable[Entry], limit: int) -> list[Entry]:
    if limit <= 0:
        return []
    return sorted(entries, key=lambda e: (e.textLength, text_density(e), e.sourcePath))[:limit]


def build_manifest_payload(
    *,
    roots: Iterable[str],
    files_count: int,
    entries: Iterable[Entry],
    category_counts: Counter,
    error_count: int,
    warning_count: int,
) -> dict[str, object]:
    entry_list = list(entries)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "roots": list(roots),
        "html": files_count,
        "classified": len(entry_list),
        "categories": {k: category_counts[k] for k in sorted(category_counts)},
        "errorCount": error_count,
        "warningCount": warning_count,
        "entries": entries_json(entry_list),
    }


def load_ariadne_rx_map() -> dict[str, list[str | None]]:
    global ARIADNE_RX_MAP
    if ARIADNE_RX_MAP is not None:
        return ARIADNE_RX_MAP
    ARIADNE_RX_MAP = {}
    try:
        tree = ast.parse(ARIADNE_RX_MAP_PATH.read_text(encoding="utf-8"))
    except OSError:
        return ARIADNE_RX_MAP
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = [target.id for target in node.targets if isinstance(target, ast.Name)]
            if "MAP" not in names:
                continue
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                value = {}
            if isinstance(value, dict):
                ARIADNE_RX_MAP = value
            break
    return ARIADNE_RX_MAP


def expected_ariadne_rx_values(filename: str) -> list[str | None] | None:
    mapping = load_ariadne_rx_map()
    values = mapping.get(filename)
    return values if isinstance(values, list) else None


def summarize_codes(codes: Iterable[str], limit: int = 12) -> str:
    vals = sorted(set(codes), key=lambda s: (code_key(s) or ("", "", 10**9, None), s))
    shown = ", ".join(vals[:limit])
    if len(vals) > limit:
        shown += f", ... (+{len(vals) - limit})"
    return shown or "—"


def genmeta_status(html: str) -> tuple[list[str], str]:
    stamps = list(GENMETA_RE.finditer(html))
    if not stamps:
        return ["lexia-genmeta 作成日フッターが無い"], ""
    problems = []
    if len(stamps) > 1:
        problems.append(f"lexia-genmeta が複数ある: {len(stamps)}")
    all_stamp_text = "\n".join(m.group(0) for m in stamps)
    dgs = attr_values(DATA_GENERATED_RE, all_stamp_text)
    generated = dgs[0] if dgs else ""
    if not dgs:
        problems.append("lexia-genmeta に data-generated が無い")
    elif len(dgs) > 1:
        problems.append(f"lexia-genmeta data-generated が複数ある: {len(dgs)}")
    elif not valid_generated_stamp(generated):
        problems.append(f"lexia-genmeta data-generated が ISO8601+TZ 形式ではない: {generated}")
    elif not generated_display_matches(generated, all_stamp_text):
        problems.append("lexia-genmeta 表示日時が data-generated と一致しない")
    if "Generated:" not in all_stamp_text:
        problems.append('lexia-genmeta 本文に "Generated:" が無い')
    if "作成日" in all_stamp_text:
        problems.append("lexia-genmeta が旧日本語 作成日 表記を含む")
    return problems, generated


def valid_generated_stamp(value: str) -> bool:
    if not DATA_GENERATED_ISO_RE.fullmatch(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def generated_display_matches(generated: str, stamp_html: str) -> bool:
    m = re.match(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})", generated)
    if not m:
        return False
    expected = f"Generated: {m.group(1)} {m.group(2)}"
    return expected in strip_tags(stamp_html)


def script_body_literal(html: str) -> bool:
    return any("</body>" in m.group(1) for m in SCRIPT_RE.finditer(html))


def extract_recall_open_tags(html: str) -> list[str]:
    return [
        tag
        for tag in (m.group(0) for m in DIV_OPEN_RE.finditer(html))
        if has_class(tag, "self-check-quiz") and DATA_RECALL_RE.search(tag)
    ]


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

    if meta["category"] in {"TX_OFFICIAL", "TX_LEXIA", "JX", "KJX", "ARIADNE"}:
        if not same_code(meta["baseCode"], title):
            errors.append(f"title の問題コードがファイル名由来 baseCode と一致しない: baseCode={meta['baseCode']} title={title[:80]}")

    if meta["category"] == "ARIADNE":
        target = first_attr_value(DATA_ATHENA_CODE_RE, html)
        if not target:
            errors.append("data-athena-code が無い（ATHENA ジャンプ不能）")
        elif not same_code(meta["baseCode"], target):
            errors.append(f"data-athena-code が baseCode と一致しない: {target} != {meta['baseCode']}")

        recall_tags = extract_recall_open_tags(html)
        if recall_tags:
            rx_values = []
            missing = 0
            intentional_missing = 0
            bad = []
            dangling = []
            expected_values = expected_ariadne_rx_values(path.name)
            if expected_values is not None and len(expected_values) != len(recall_tags):
                warnings.append(f"data-rx MAP 長と想起カード数が不一致: MAP={len(expected_values)} cards={len(recall_tags)}")
                expected_values = None
            expected = re.compile(r"^" + re.escape(meta["baseCode"].replace("JX", "RX")) + r"_\d+$")
            for i, tag in enumerate(recall_tags):
                m = DATA_RX_RE.search(tag)
                rx = m.group(2).strip() if m else ""
                if not rx:
                    if expected_values is not None and expected_values[i] is None:
                        intentional_missing += 1
                    else:
                        missing += 1
                    continue
                rx_values.append(rx)
                if not expected.fullmatch(rx):
                    bad.append(rx)
                elif not rx_exists_for(rel, rx):
                    dangling.append(rx)
            effective_total = len(recall_tags) - intentional_missing
            if missing and missing == effective_total:
                warnings.append(f"想起カード {len(recall_tags)} 枚すべて data-rx 欠落")
            elif missing:
                warnings.append(f"想起カード data-rx 欠落 {missing}/{len(recall_tags)} 枚")
            if bad:
                errors.append(f"data-rx の科目/JX 不整合: {', '.join(sorted(set(bad))[:8])}")
            if dangling:
                errors.append(f"data-rx 参照先 RX 不在: {', '.join(sorted(set(dangling))[:8])}")
            duplicate_rx = [rx for rx, count in Counter(rx_values).items() if count > 1]
            if duplicate_rx:
                warnings.append(f"data-rx 重複 {len(duplicate_rx)} 件: {', '.join(sorted(duplicate_rx)[:8])}")
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
        textLength=body_text_len,
        stableSha256=stable_content_sha256(html),
        generated=generated,
    )
    return entry, errors, warnings


def global_issues(entries: Iterable[Entry], untracked_sync_files: Iterable[str] = ()) -> tuple[list[str], list[str]]:
    entries = list(entries)
    source_paths = defaultdict(list)
    filenames = defaultdict(list)
    ids = defaultdict(list)
    titles = defaultdict(list)
    entry_by_path = {e.sourcePath: e for e in entries}
    for e in entries:
        source_paths[e.sourcePath].append(e.sourcePath)
        filenames[e.fileName].append(e.sourcePath)
        ids[(e.category, e.code)].append(e.sourcePath)
        if e.title:
            titles[e.title].append(e.sourcePath)

    global_errors: list[str] = []
    global_warnings: list[str] = []
    untracked = list(untracked_sync_files)
    if untracked:
        global_errors.append(
            f"git 未追跡の同期対象 HTML {len(untracked)} 件: {summarize_paths(untracked)}"
        )
    for key, paths in ids.items():
        if len(paths) > 1:
            global_errors.append(f"category+code 重複 {key}: {', '.join(paths[:6])}")
    for name, paths in filenames.items():
        if len(paths) > 1:
            # 同一 fileName は Lexia 側の fileName 表示や差分追跡で紛らわしいため警告ではなくエラー。
            global_errors.append(f"fileName 重複 {name}: {', '.join(paths[:6])}")
    for title, paths in titles.items():
        if len(paths) > 1:
            # 公式 TX と _lex の title 重複は既存 check-duplicates と同様に許容したい。
            cats = {entry_by_path[p].category for p in paths}
            base_codes = {entry_by_path[p].baseCode for p in paths}
            if not (cats <= {"TX_OFFICIAL", "TX_LEXIA"} and len(base_codes) == 1):
                global_errors.append(f"title 重複 '{title[:80]}': {', '.join(paths[:6])}")

    by_category: dict[str, set[str]] = defaultdict(set)
    for e in entries:
        by_category[e.category].add(e.baseCode)

    official_tx = by_category["TX_OFFICIAL"]
    lexia_tx = by_category["TX_LEXIA"]
    if missing := official_tx - lexia_tx:
        global_warnings.append(f"TX _lex 欠落 {len(missing)} 件: {summarize_codes(missing)}")
    if orphan := lexia_tx - official_tx:
        global_warnings.append(f"TX 公式 HTML 欠落 {len(orphan)} 件: {summarize_codes(orphan)}")

    jx = by_category["JX"]
    ariadne = by_category["ARIADNE"]
    tree = by_category["TREE"]
    rx_bases = by_category["RX"]
    if missing := jx - ariadne:
        global_warnings.append(f"JX 対応 ARIADNE 欠落 {len(missing)} 件: {summarize_codes(missing)}")
    if missing := jx - tree:
        global_warnings.append(f"JX 対応 TREE 欠落 {len(missing)} 件: {summarize_codes(missing)}")
    if orphan := ariadne - jx:
        global_warnings.append(f"JX 本体が無い ARIADNE {len(orphan)} 件: {summarize_codes(orphan)}")
    if orphan := tree - jx:
        global_warnings.append(f"JX 本体が無い TREE {len(orphan)} 件: {summarize_codes(orphan)}")
    if orphan := rx_bases - jx:
        global_warnings.append(f"JX 本体が無い RX {len(orphan)} 件: {summarize_codes(orphan)}")
    return global_errors, global_warnings


def audit_roots(roots: Iterable[str], allow_untracked_sync_artifacts: bool = False) -> AuditResult:
    roots = list(roots)
    files = collect_files(roots)
    tracked_paths = None if allow_untracked_sync_artifacts else git_tracked_paths(roots)
    untracked_sync_files = find_untracked_sync_files(files, tracked_paths)
    entries: list[Entry] = []
    per_file: list[tuple[Path, Entry | None, list[str], list[str]]] = []

    for path in files:
        entry, errors, warnings = audit_entry(path)
        if entry:
            entries.append(entry)
        per_file.append((path, entry, errors, warnings))

    global_errors, global_warnings = global_issues(entries, untracked_sync_files)
    category_counts = Counter(e.category for e in entries)
    return AuditResult(
        files=files,
        entries=entries,
        per_file=per_file,
        global_errors=global_errors,
        global_warnings=global_warnings,
        category_counts=category_counts,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Lexia 同期契約の横断検査")
    ap.add_argument("roots", nargs="*", default=list(DEFAULT_ROOTS), help="走査ルート（既定: outputs references）")
    ap.add_argument("--summary", action="store_true", help="問題のあるファイルだけ表示")
    ap.add_argument("--strict", action="store_true", help="WARNING も終了コード 1 にする")
    ap.add_argument("--json", dest="json_path", help="導出メタ情報を JSON で保存")
    ap.add_argument(
        "--json-format",
        choices=("entries", "manifest"),
        default="entries",
        help="--json の出力形式（entries: 既存互換 list / manifest: schemaVersion 付き object）",
    )
    ap.add_argument(
        "--allow-untracked-sync-artifacts",
        action="store_true",
        help="outputs/references 配下の未追跡 HTML を同期エラーにしない（ローカル作業中のみ）",
    )
    ap.add_argument(
        "--thin-report",
        type=int,
        default=0,
        metavar="N",
        help="本文テキスト量が少ない順に N 件を表示する（失敗条件にはしない）",
    )
    args = ap.parse_args()

    result = audit_roots(args.roots, allow_untracked_sync_artifacts=args.allow_untracked_sync_artifacts)
    err_count = result.error_count
    warn_count = result.warning_count

    print("=== Lexia 同期契約チェック ===")
    print(f"roots={', '.join(args.roots)} / html={len(result.files)} / classified={len(result.entries)}")
    print("categories: " + ", ".join(f"{k}={v}" for k, v in sorted(result.category_counts.items())))
    print()

    if result.global_errors:
        print("[GLOBAL ERROR]")
        for msg in result.global_errors:
            print(f"  ERROR {msg}")
        print()

    if result.global_warnings:
        print("[GLOBAL WARN]")
        for msg in result.global_warnings:
            print(f"  WARN  {msg}")
        print()

    for path, _entry, errors, warnings in result.per_file:
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

    if args.thin_report > 0:
        print(f"[LOW TEXT: {args.thin_report}]")
        for entry in low_text_entries(result.entries, args.thin_report):
            print(
                f"  text={entry.textLength:>7} bytes={entry.bytes:>7} "
                f"density={text_density(entry):.3f} {entry.category} {entry.code} {entry.sourcePath}"
            )
        print()

    if args.json_path:
        out = ROOT / args.json_path
        out.parent.mkdir(parents=True, exist_ok=True)
        payload: object
        if args.json_format == "manifest":
            payload = build_manifest_payload(
                roots=args.roots,
                files_count=len(result.files),
                entries=result.entries,
                category_counts=result.category_counts,
                error_count=err_count,
                warning_count=warn_count,
            )
        else:
            payload = entries_json(result.entries)
        write_text_if_changed(out, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        print(f"\njson={display_path(out)}")

    print("\n=== summary ===")
    print(f"ERROR={err_count}  WARNING={warn_count}")
    if err_count or (args.strict and warn_count):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
