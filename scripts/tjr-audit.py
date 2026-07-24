#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tjr-audit.py — TJR-F（修復ストリーム）のエラー品・未完成品 監査ツール。

【目的】TJR の T/J/R は「出力ファイルが存在するか」で対象を決めるため、生成が途中で
死んだり validate ERROR で commit されずに残った HTML は、存在するだけで
  - T: `Test-Path 公式` → SKIP（既存扱い）
  - R(a): _lex が v13 マーカーを持てば SKIP ／ R(b): 公式が存在すれば SKIP
  - J: `SKIP_EXISTS`
となり、**どのストリームからも不可視＝未完成のまま放置**される構造穴がある。
本ツールはその「事故の残骸（インシデント）」を毎バッチ検出し、TJR.ps1 の F ストリームが
自動修復（再生成 or 回収コミット）へ振り分けるための JSON を出力する。

【検査対象（インシデント・スコープ）】※コーパス全体の品質再監査ではない
  A. TX 二系統ペア欠け     … 公式のみ／_lex のみ（入力PDFが残っていれば再生成対象）
  B. 途切れ                … 末尾に </html> が無い（クラッシュ時の書きかけ）
  C. プレースホルダー残骸  … {{SLOT_NAME}} が本番出力に残存（スロット未充填）
  D. サイズ異常            … 30KB 未満（正常品は 150KB〜450KB 級）
  E. 未コミット残骸        … git status で outputs/ 配下に dirty が残る
                             → 検証 PASS なら「回収コミット」／FAIL なら「再生成」
  F. JX 副産物欠落         … 検出・報告のみ（修復は ②-verify／rx-arb-autofill の領分）

【意図的に検査しないもの】コミット済みで構造健全なファイルへの最新ゲート適用
（G70 等の後付けゲートに旧作が引っかかる問題は「TJR 付随で消化」＝R の領分・ユーザー方針）。

【安全設計】
  - 基本 read-only。書換えは --fix-safe 指定時の tx-sysmap-fit.py（決定論・冪等・本文不変）のみ。
  - 生成中ファイルの誤検出防止：関連ファイルの最終更新が --min-age-min 分以内なら
    「in-flight（生成中の可能性）」として今回はスキップ。
  - 検証ツールが動かない環境（bs4 欠落等）では自動判定せず report-only に落とす。

使い方:
  python scripts/tjr-audit.py                          # 監査して人間向けサマリ表示
  python scripts/tjr-audit.py --json logs/tjr-audit-latest.json
  python scripts/tjr-audit.py --fix-safe               # G66/G69 のみの失敗は sysmap-fit で自動修復
  終了コード: 0=修復対象なし / 1=修復対象あり（F の仕事あり） / 2=ツールエラー
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT_DEFAULT = Path(__file__).resolve().parents[1]

SUBJECT_FOLDERS = {
    "001_刑法": "刑",
    "002_刑事訴訟法": "刑訴",
    "003_民法": "民",
    "004_商法": "商",
    "005_民事訴訟法": "民訴",
    "006_行政法": "行政",
    "007_憲法": "憲",
}

MIN_HTML_BYTES = 30_000     # TX/JX 本体の下限（これ未満は書きかけ・骨だけとみなす）
TAIL_BYTES = 4096           # 途切れ判定で読む末尾バイト数
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z][A-Z0-9_]{2,}\}\}")
VALIDATOR_TIMEOUT = 420     # 秒（validate-tx-core は大きい _lex で数十秒かかる）


# ---------------------------------------------------------------- 基本ヘルパ
def read_tail(path: Path) -> str:
    try:
        size = path.stat().st_size
        with open(path, "rb") as fh:
            fh.seek(max(0, size - TAIL_BYTES))
            return fh.read().decode("utf-8", "ignore")
    except OSError:
        return ""


def is_truncated(path: Path) -> bool:
    return "</html>" not in read_tail(path).lower()


def has_placeholder(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return bool(PLACEHOLDER_RE.search(text))


def newest_mtime(paths: list[Path]) -> float:
    best = 0.0
    for p in paths:
        try:
            best = max(best, p.stat().st_mtime)
        except OSError:
            pass
    return best


def leading_number(stem: str) -> int | None:
    m = re.match(r"^(\d+)", stem)
    return int(m.group(1)) if m else None


def rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()


# ---------------------------------------------------------------- git 状態
def git_dirty_outputs(root: Path) -> dict[str, str]:
    """outputs/ 配下の dirty path → status（'??','M','D' 等）。git 不能時は空。"""
    try:
        cp = subprocess.run(
            ["git", "-C", str(root), "-c", "core.quotepath=false", "status",
             "--porcelain=v1", "--no-renames", "--untracked-files=all", "--", "outputs"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
        )
    except Exception:
        return {}
    if cp.returncode != 0:
        return {}
    dirty: dict[str, str] = {}
    for line in cp.stdout.splitlines():
        if len(line) < 4:
            continue
        xy, p = line[:2], line[3:].strip()
        if p.startswith('"') and p.endswith('"'):
            p = p[1:-1]
        dirty[p] = xy.strip() or xy
    return dirty


# ---------------------------------------------------------------- 検証実行
class ValidatorRunner:
    def __init__(self, root: Path):
        self.root = root
        self.core = root / "scripts" / "validate-tx-core.py"
        self.engine = root / "scripts" / "check-tx-lex-engine.py"
        self.oxgrid = root / "scripts" / "check-lex-oxgrid-integrity.py"
        self.jx = root / "scripts" / "validate-jx.py"
        self.sysmap_fit = root / "scripts" / "tx-sysmap-fit.py"
        self.runs = 0

    def _run(self, script: Path, target: Path) -> tuple[int, str]:
        """(exit, stdout+stderr)。script 不在=0（ゲート無しと同じ扱い）、実行不能=-1。"""
        if not script.exists():
            return 0, ""
        self.runs += 1
        try:
            cp = subprocess.run(
                [sys.executable, str(script), str(target)],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=VALIDATOR_TIMEOUT, cwd=str(self.root),
            )
            return cp.returncode, (cp.stdout or "") + (cp.stderr or "")
        except Exception as exc:  # timeout 含む
            return -1, f"validator-exec-error: {exc}"

    @staticmethod
    def _unavailable(out: str) -> bool:
        return "beautifulsoup4 が必要" in out or "validator-exec-error" in out

    @staticmethod
    def _error_codes(out: str) -> set[str]:
        """validate-tx-core 出力の ERROR 行から G コードを抽出。"""
        codes: set[str] = set()
        for line in out.splitlines():
            if "❌" in line or "[ERROR]" in line:
                for m in re.finditer(r"\[G(\d+)", line):
                    codes.add(f"G{m.group(1)}")
        return codes

    def check_tx(self, path: Path, is_lex: bool, fix_safe: bool) -> tuple[str, list[str]]:
        """('pass'|'fail'|'unavailable', 理由リスト)。fix_safe 時は G66/G69 のみの失敗を
        tx-sysmap-fit.py（決定論・冪等）で自動修復して再検証する。"""
        rc, out = self._run(self.core, path)
        if self._unavailable(out):
            return "unavailable", ["validate-tx-core 実行不能（環境要確認）"]
        reasons: list[str] = []
        if rc != 0:
            codes = self._error_codes(out)
            if fix_safe and codes and codes <= {"G66", "G69"} and self.sysmap_fit.exists():
                frc, fout = self._run(self.sysmap_fit, path)
                rc2, out2 = self._run(self.core, path)
                if frc == 0 and rc2 == 0:
                    reasons.append(f"sysmap-fit 自動修復済（{'/'.join(sorted(codes))}）")
                    rc = 0
                else:
                    reasons.append(f"validate-tx-core ERROR（{'/'.join(sorted(codes)) or 'コード不明'}・sysmap-fit でも未解消）")
            else:
                reasons.append(f"validate-tx-core ERROR（{'/'.join(sorted(codes)) or 'コード不明'}）")
        if is_lex:
            erc, eout = self._run(self.engine, path)
            if self._unavailable(eout):
                return "unavailable", ["check-tx-lex-engine 実行不能（環境要確認）"]
            if erc != 0:
                reasons.append("check-tx-lex-engine ERROR（エンジン非正典）")
            orc, oout = self._run(self.oxgrid, path)
            if self._unavailable(oout):
                return "unavailable", ["check-lex-oxgrid-integrity 実行不能（環境要確認）"]
            if orc != 0:
                reasons.append("check-lex-oxgrid-integrity ERROR（○×健全性）")
        fixed_only = reasons and all(r.startswith("sysmap-fit 自動修復済") for r in reasons)
        if not reasons or fixed_only:
            return "pass", reasons
        return "fail", reasons

    def check_jx(self, path: Path) -> tuple[str, list[str]]:
        rc, out = self._run(self.jx, path)
        if self._unavailable(out):
            return "unavailable", ["validate-jx 実行不能（環境要確認）"]
        if rc != 0:
            return "fail", [f"validate-jx ERROR (exit {rc})"]
        return "pass", []


# ---------------------------------------------------------------- 索引構築
def build_tx_index(root: Path):
    """{folder: {'official': {n: Path}, 'lex': {n: Path}, 'pdf': {n: Path}}}"""
    idx: dict[str, dict[str, dict[int, Path]]] = {}
    for folder in SUBJECT_FOLDERS:
        entry = {"official": {}, "lex": {}, "pdf": {}}
        offdir = root / "outputs" / "000_TX" / folder
        if offdir.is_dir():
            for f in offdir.iterdir():
                m = re.match(r"^(.+?TX)(\d+)\.html$", f.name)
                if m:
                    entry["official"][int(m.group(2))] = f
        lexdir = root / "outputs" / "ux" / "000_TX" / folder
        if lexdir.is_dir():
            for f in lexdir.iterdir():
                m = re.match(r"^(.+?TX)(\d+)_lex\.html$", f.name)
                if m:
                    entry["lex"][int(m.group(2))] = f
        pdfdir = root / "inputs" / "000_TX" / folder
        if pdfdir.is_dir():
            for f in pdfdir.glob("*.pdf"):
                n = leading_number(f.stem)
                if n is not None and n not in entry["pdf"]:
                    entry["pdf"][n] = f
        idx[folder] = entry
    return idx


def build_jx_index(root: Path):
    """{folder: {'jx': {n: Path}, 'pdf': {n: Path}, 'transcript': {n: Path}}}"""
    idx: dict[str, dict[str, dict[int, Path]]] = {}
    for folder in SUBJECT_FOLDERS:
        entry = {"jx": {}, "pdf": {}, "transcript": {}}
        jxdir = root / "outputs" / "001_JX" / folder
        if jxdir.is_dir():
            for f in jxdir.iterdir():
                m = re.match(r"^(.+?JX)(\d+)\.html$", f.name)
                if m:
                    entry["jx"][int(m.group(2))] = f
        base = root / "inputs" / "001_JX" / folder
        for d in (base / "重問PDF", base):
            if d.is_dir():
                for f in d.glob("*.pdf"):
                    n = leading_number(f.stem)
                    if n is not None and n not in entry["pdf"]:
                        entry["pdf"][n] = f
        for d in (base / "講義逐語", base):
            if d.is_dir():
                for f in d.iterdir():
                    if f.suffix not in (".txt", ".md"):
                        continue
                    m = re.search(r"重問(?:逐語)?\s*0*(\d+)", f.stem)
                    n = int(m.group(1)) if m else leading_number(f.stem)
                    if n is not None and n not in entry["transcript"]:
                        entry["transcript"][n] = f
        idx[folder] = entry
    return idx


# ---------------------------------------------------------------- 監査本体
def file_incidents(path: Path, recent_cutoff: float, force_full: bool) -> list[str]:
    """1ファイルの構造インシデント（サイズ・途切れ・プレースホルダー）。"""
    reasons: list[str] = []
    try:
        size = path.stat().st_size
    except OSError:
        return reasons
    if size < MIN_HTML_BYTES:
        reasons.append(f"サイズ異常（{size:,}B < {MIN_HTML_BYTES:,}B）")
    if is_truncated(path):
        reasons.append("途切れ（末尾に </html> なし）")
    # プレースホルダー全文走査は「最近更新されたファイル」と「dirty ファイル」に限定（コスト制御）
    if force_full or path.stat().st_mtime >= recent_cutoff:
        if has_placeholder(path):
            reasons.append("プレースホルダー残骸（{{SLOT}} 残存）")
    return reasons


def audit(root: Path, min_age_min: int, recent_days: int, fix_safe: bool,
          max_validate: int, quiet: bool) -> dict:
    now = time.time()
    recent_cutoff = now - recent_days * 86400
    min_age_sec = min_age_min * 60
    dirty = git_dirty_outputs(root)
    vr = ValidatorRunner(root)

    tx_idx = build_tx_index(root)
    jx_idx = build_jx_index(root)

    tx_repairs: list[dict] = []
    tx_commits: list[dict] = []
    jx_repairs: list[dict] = []
    jx_commits: list[dict] = []
    inflight: list[dict] = []
    report_only: list[dict] = []
    byproduct_gaps: list[dict] = []
    validate_budget = [max_validate]
    handled: set[str] = set()   # 問題単位で審査済みの dirty path（末尾フォールバックの重複計上防止）

    def is_dirty(p: Path) -> str | None:
        return dirty.get(rel(root, p))

    def mark_handled(paths: list[Path]) -> None:
        for p in paths:
            handled.add(rel(root, p))

    def budget_ok() -> bool:
        return validate_budget[0] > 0

    def spend_budget():
        validate_budget[0] -= 1

    # ---- TX（二系統ペア単位） ----
    for folder, subj in SUBJECT_FOLDERS.items():
        entry = tx_idx[folder]
        numbers = sorted(set(entry["official"]) | set(entry["lex"]))
        for n in numbers:
            off = entry["official"].get(n)
            lex = entry["lex"].get(n)
            prefix = (off or lex).name.split("TX")[0] + "TX"
            problem_id = f"{prefix}{n:03d}"
            reasons: list[str] = []
            if off and not lex:
                reasons.append("_lex 欠落（公式のみ＝T/R から不可視の片肺）")
            if lex and not off:
                reasons.append("公式欠落（_lex のみ）")
            existing = [p for p in (off, lex) if p]
            pair_dirty = [p for p in existing if is_dirty(p)]
            for p in existing:
                for r in file_incidents(p, recent_cutoff, force_full=bool(is_dirty(p))):
                    reasons.append(f"{p.name}: {r}")

            if not reasons and not pair_dirty:
                continue  # 健全・コミット済み
            mark_handled(existing)

            # in-flight ガード（生成中の書きかけを事故扱いしない）
            age = now - newest_mtime(existing) if existing else 1e9
            if age < min_age_sec:
                inflight.append({"problemId": problem_id,
                                 "note": f"最終更新 {int(age/60)} 分前＝生成中の可能性。次回監査へ持ち越し"})
                continue

            item = {
                "id": f"TX:{subj}:{n}",
                "kind": "TX",
                "subject": subj,
                "folder": folder,
                "number": n,
                "problemId": problem_id,
                "officialPath": rel(root, off) if off else None,
                "lexPath": rel(root, lex) if lex else None,
                "reasons": reasons,
            }

            if not reasons and pair_dirty:
                # 構造は健全だが未コミット → 検証して PASS なら回収コミット
                if not budget_ok():
                    item["reasons"] = ["未コミット（検証枠超過＝次回監査で判定）"]
                    report_only.append({"path": rel(root, pair_dirty[0]), "reasons": item["reasons"]})
                    continue
                verdicts: list[str] = []
                notes: list[str] = []
                for p in existing:
                    spend_budget()
                    v, why = vr.check_tx(p, is_lex=(p is lex), fix_safe=fix_safe)
                    verdicts.append(v)
                    notes.extend(f"{p.name}: {w}" for w in why)
                if "unavailable" in verdicts:
                    report_only.append({"path": rel(root, pair_dirty[0]),
                                        "reasons": ["未コミット・検証環境なしで自動判定不可"] + notes})
                elif all(v == "pass" for v in verdicts):
                    tx_commits.append({**item,
                                       "paths": [rel(root, p) for p in pair_dirty],
                                       "note": "検証PASS・未コミット残骸の回収" + ("／" + "；".join(notes) if notes else "")})
                else:
                    item["reasons"] = ["未コミット・検証FAIL"] + notes
                    _queue_tx_repair(item, entry, root, tx_repairs, report_only)
            else:
                # 構造破損 → 再生成（入力 PDF がなければ report）
                _queue_tx_repair(item, entry, root, tx_repairs, report_only)

    # ---- JX ----
    for folder, subj in SUBJECT_FOLDERS.items():
        entry = jx_idx[folder]
        for n, jx in sorted(entry["jx"].items()):
            problem_id = jx.stem
            reasons = file_incidents(jx, recent_cutoff, force_full=bool(is_dirty(jx)))
            jdirty = is_dirty(jx)
            if not reasons and not jdirty:
                continue
            mark_handled([jx])
            age = now - newest_mtime([jx])
            if age < min_age_sec:
                inflight.append({"problemId": problem_id,
                                 "note": f"最終更新 {int(age/60)} 分前＝生成中の可能性。次回監査へ持ち越し"})
                continue
            item = {
                "id": f"JX:{subj}:{n}",
                "kind": "JX",
                "subject": subj,
                "folder": folder,
                "number": n,
                "problemId": problem_id,
                "jxPath": rel(root, jx),
                "reasons": reasons,
            }
            if not reasons and jdirty:
                if not budget_ok():
                    report_only.append({"path": rel(root, jx), "reasons": ["未コミット（検証枠超過＝次回監査で判定）"]})
                    continue
                spend_budget()
                v, why = vr.check_jx(jx)
                if v == "unavailable":
                    report_only.append({"path": rel(root, jx), "reasons": ["未コミット・検証環境なしで自動判定不可"] + why})
                elif v == "pass":
                    paths = [rel(root, jx)]
                    # 同問題の副産物・TTS が dirty なら簡易健全性チェックの上で同梱回収
                    for extra in _jx_side_artifacts(root, folder, problem_id):
                        if is_dirty(extra) and _sane_artifact(extra):
                            paths.append(rel(root, extra))
                    jx_commits.append({**item, "paths": paths, "note": "検証PASS・未コミット残骸の回収"})
                else:
                    item["reasons"] = ["未コミット・検証FAIL"] + why
                    _queue_jx_repair(item, entry, root, jx_repairs, report_only)
            else:
                _queue_jx_repair(item, entry, root, jx_repairs, report_only)

        # ---- JX 副産物欠落（検出のみ・修復は ②-verify／autofill の領分） ----
        for n, jx in sorted(entry["jx"].items()):
            problem_id = jx.stem
            missing = []
            if not (root / "outputs" / "ux" / "001_ARIADNE" / folder / f"{problem_id}_ARIADNE.html").exists():
                missing.append("ARIADNE")
            if not (root / "outputs" / "ux" / "003_TREE" / folder / f"{problem_id}_TREE.html").exists():
                missing.append("TREE")
            rxdir = root / "outputs" / "ux" / "002_RX" / folder / problem_id
            if not (rxdir.is_dir() and any(rxdir.glob("*.html"))):
                missing.append("RX")
            if missing:
                byproduct_gaps.append({"problemId": problem_id, "missing": missing})

    # ---- outputs 配下のその他 dirty（削除・分類不能・単独副産物） ----
    for coll in (tx_commits, jx_commits):
        for it in coll:
            handled.update(it.get("paths", []))
    for p, st in sorted(dirty.items()):
        if p in handled:
            continue
        if st == "D":
            report_only.append({"path": p, "reasons": [f"作業ツリーで削除（未コミット）。復元は `git checkout -- {p}`／意図的なら commit"]})
        elif re.match(r"^outputs/ux/00[123]_", p):
            report_only.append({"path": p, "reasons": ["副産物が未コミット（親 JX はコミット済）。健全なら手動 commit か次回 finalize で回収"]})
        elif p.startswith("outputs/002_TTS/"):
            report_only.append({"path": p, "reasons": ["TTS 台本が未コミット。次回 JX finalize か手動 commit で回収"]})
        else:
            # 修復キュー該当分（committed 破損）は dirty に出ないのでここは純粋な分類不能
            report_only.append({"path": p, "reasons": [f"outputs 配下の未コミット・分類不能（status={st}）"]})

    result = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "root": str(root),
        "minAgeMin": min_age_min,
        "validatorRuns": vr.runs,
        "txRepairs": tx_repairs,
        "txCommits": tx_commits,
        "jxRepairs": jx_repairs,
        "jxCommits": jx_commits,
        "inflight": inflight,
        "reportOnly": report_only,
        "byproductGaps": byproduct_gaps,
    }
    result["summary"] = {
        "actionable": len(tx_repairs) + len(tx_commits) + len(jx_repairs) + len(jx_commits),
        "txRepairs": len(tx_repairs),
        "txCommits": len(tx_commits),
        "jxRepairs": len(jx_repairs),
        "jxCommits": len(jx_commits),
        "inflight": len(inflight),
        "reportOnly": len(report_only),
        "byproductGaps": len(byproduct_gaps),
    }
    return result


def _queue_tx_repair(item: dict, entry: dict, root: Path,
                     tx_repairs: list, report_only: list) -> None:
    pdf = entry["pdf"].get(item["number"])
    if pdf:
        item["pdf"] = rel(root, pdf)
        tx_repairs.append(item)
    else:
        report_only.append({"path": item.get("officialPath") or item.get("lexPath") or item["problemId"],
                            "reasons": item["reasons"] + ["入力PDFなし＝再生成不能（Drive 抽出PDFから復元後に再対象化）"]})


def _queue_jx_repair(item: dict, entry: dict, root: Path,
                     jx_repairs: list, report_only: list) -> None:
    pdf = entry["pdf"].get(item["number"])
    ts = entry["transcript"].get(item["number"])
    if pdf and ts:
        item["pdf"] = rel(root, pdf)
        item["transcript"] = rel(root, ts)
        jx_repairs.append(item)
    else:
        lack = "入力PDFなし" if not pdf else "講義逐語なし"
        report_only.append({"path": item["jxPath"],
                            "reasons": item["reasons"] + [f"{lack}＝再生成不能（入力復元後に再対象化）"]})


def _jx_side_artifacts(root: Path, folder: str, problem_id: str) -> list[Path]:
    paths = [
        root / "outputs" / "ux" / "001_ARIADNE" / folder / f"{problem_id}_ARIADNE.html",
        root / "outputs" / "ux" / "003_TREE" / folder / f"{problem_id}_TREE.html",
    ]
    rxdir = root / "outputs" / "ux" / "002_RX" / folder / problem_id
    if rxdir.is_dir():
        paths.extend(sorted(rxdir.glob("*.html")))
    ttsdir = root / "outputs" / "002_TTS" / problem_id
    if ttsdir.is_dir():
        paths.extend(sorted(ttsdir.glob("*.txt")))
    return [p for p in paths if p.exists()]


def _sane_artifact(p: Path) -> bool:
    try:
        if p.stat().st_size == 0:
            return False
    except OSError:
        return False
    if p.suffix == ".html":
        return not is_truncated(p)
    return True


# ---------------------------------------------------------------- 表示
def print_report(res: dict, quiet: bool) -> None:
    s = res["summary"]
    print("=== TJR-F 監査（エラー品・未完成品） ===")
    print(f"  修復対象: TX再生成 {s['txRepairs']} / TX回収コミット {s['txCommits']} / "
          f"JX再生成 {s['jxRepairs']} / JX回収コミット {s['jxCommits']}")
    print(f"  その他  : 生成中スキップ {s['inflight']} / report-only {s['reportOnly']} / 副産物欠落 {s['byproductGaps']}")
    if quiet:
        return
    for it in res["txRepairs"] + res["jxRepairs"]:
        print(f"  [REGEN ] {it['problemId']}: {'；'.join(it['reasons'])}")
    for it in res["txCommits"] + res["jxCommits"]:
        print(f"  [COMMIT] {it['problemId']}: {it['note']}")
    for it in res["inflight"]:
        print(f"  [WAIT  ] {it['problemId']}: {it['note']}")
    for it in res["reportOnly"]:
        print(f"  [REPORT] {it['path']}: {'；'.join(it['reasons'])}")
    if res["byproductGaps"]:
        gaps = "、".join(f"{g['problemId']}({'/'.join(g['missing'])})" for g in res["byproductGaps"][:20])
        more = "…" if len(res["byproductGaps"]) > 20 else ""
        print(f"  [GAP   ] JX副産物欠落（修復は autofill/②-verify の領分）: {gaps}{more}")


def main() -> int:
    ap = argparse.ArgumentParser(description="TJR-F エラー品・未完成品 監査")
    ap.add_argument("--root", default=str(ROOT_DEFAULT))
    ap.add_argument("--json", default="", help="結果 JSON の出力先（TJR.ps1 が読む）")
    ap.add_argument("--min-age-min", type=int, default=45,
                    help="この分数以内に更新されたファイルは生成中とみなしスキップ（既定45）")
    ap.add_argument("--recent-days", type=int, default=14,
                    help="プレースホルダー全文走査の対象期間（既定14日・dirtyは常に走査）")
    ap.add_argument("--max-validate", type=int, default=60,
                    help="1回の監査で走らせる検証ツールの上限回数（既定60）")
    ap.add_argument("--fix-safe", action="store_true",
                    help="G66/G69 のみの検証失敗を tx-sysmap-fit.py（決定論・冪等）で自動修復")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not (root / "outputs").is_dir():
        print(f"[ERROR] outputs/ が見つかりません: {root}", file=sys.stderr)
        return 2

    try:
        res = audit(root, args.min_age_min, args.recent_days, args.fix_safe,
                    args.max_validate, args.quiet)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] 監査中に例外: {exc}", file=sys.stderr)
        return 2

    print_report(res, args.quiet)
    if args.json:
        out = Path(args.json)
        if not out.is_absolute():
            out = root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  JSON: {out}")
    return 1 if res["summary"]["actionable"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
