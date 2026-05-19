#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_content.py — 内容検証スクリプト

構造検証 (validate_structure.py / S1〜S77) と並行して実行され、
HTML の本文内容が、対応する problems/{id}.json と整合しているかを検証する。

検査は 2 種類：

1. Negative check（NG 語検査）
   問題の罪 (crime) と異なる罪のシグネチャ語が HTML 内に混入していないか。
   canonical 本文の流用を機械的に検出する。

2. Positive check（JSON↔HTML 整合検査）
   JSON の各値（罪名、正解、解説、判例引用 etc.）が HTML 内に正しく出現するか。

両者 pass で「内容として完成」と判定する。
fail 時は HTML を _quarantine/ に隔離し、exit code 1 で終了する。

使い方:
    python validate_content.py <html_path> <json_path>

例:
    python scripts/validate_content.py outputs/tx/刑TX/刑TX326.html problems/326.json
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Iterable


# ============================================================================
# 科目別シグネチャ二段辞書（K-1 案 β：subject パラメータ化）
# ============================================================================
# SIGNATURE_REGISTRY[subject][topic] = [signature 文字列, ...]
#   - subject: "KEI" / "KEN" / "MIN" / "SYO" / "MINS" / "KEIS" / "GSE"
#   - topic:   その科目内の論点 key（罪名 / 判例略称 / 学説 / 条文番号 etc.）
#   - 各 topic に固有な語のリスト。これらは「その topic を扱う問題でのみ自然に
#     登場する」語であり、他 topic の問題に出現したら誤混入を疑う根拠となる。
#
# 拡張方針:
#   - 新しい topic を扱うときは、該当 subject の dict に追記する
#   - 一般的すぎる語（"財物" など）は入れない。複数 topic で登場するため誤検出を招く
#   - 条文番号、topic 固有の技術用語、topic 名そのものを入れる
#   - 科目をまたぐ signature（例: 刑法 246 条と他科目）は別 subject に独立して定義する
#     ことで、negative_check が混線しないようにする
#
# 後方互換:
#   - CRIME_SIGNATURES は SIGNATURE_REGISTRY["KEI"] への alias を維持。
#     旧 import パス（from validate_content import CRIME_SIGNATURES）を温存する。
#
SIGNATURE_REGISTRY: dict[str, dict[str, list[str]]] = {
    "KEI": {
        "詐欺罪": [
            "246条",
            "1項詐欺",
            "2項詐欺",
            "欺罔",
            "錯誤に基づく交付",
            "詐欺利得",
        ],
        "盗品等罪": [
            "256条",
            "257条",
            "盗品等保管",
            "盗品等有償譲受",
            "盗品等無償譲受",
            "盗品等運搬",
            "盗品等有償処分あっせん",
            "贓物",
            "牙保",
        ],
        "窃盗罪": [
            "235条",
            "不法領得の意思",
            "占有侵害",
        ],
        "強盗罪": [
            "236条",
            "238条",
            "事後強盗",
            "強盗利得",
            "反抗を抑圧",
        ],
        "横領罪": [
            "252条",
            "253条",
            "業務上横領",
            "委託物横領",
            "占有離脱物横領",
        ],
        "背任罪": [
            "247条",
            "任務違背",
            "図利加害目的",
        ],
        "文書等毀棄罪": [
            "258条",
            "259条",
            "公用文書毀棄",
            "私用文書毀棄",
            "電磁的記録毀棄",
        ],
        "器物損壊罪": [
            "261条",
            "効用侵害",
        ],
        "住居侵入罪": [
            "130条",
            "正当な理由がないのに",
        ],
        "恐喝罪": [
            "249条",
            "1項恐喝",
            "2項恐喝",
        ],
        "信書隠匿罪": [
            "263条",
            "信書隠匿",
        ],
        # 必要に応じて追記
    },
    # 他 6 科目は当面空 dict。各 PDF 処理時に必要な signature を追加していく。
    "KEN":  {},
    "MIN":  {},
    "SYO":  {},
    "MINS": {},
    "KEIS": {},
    "GSE":  {},
}

# 後方互換 alias：旧 API（CRIME_SIGNATURES）を温存する。
# 326-330 シリーズや外部 import がこの名前を参照しているため、削除してはならない。
CRIME_SIGNATURES: dict[str, list[str]] = SIGNATURE_REGISTRY["KEI"]


# ============================================================================
# 検証本体
# ============================================================================

def load_problem(json_path: Path) -> dict:
    """problems/{id}.json を読み込む。"""
    with json_path.open(encoding="utf-8") as f:
        return json.load(f)


def negative_check(
    html: str,
    current_crime: str,
    allowed_cross_refs: list[str],
    signatures_for_subject: dict[str, list[str]],
) -> list[str]:
    """他 topic のシグネチャ語が HTML に混入していないかを検査する。

    signatures_for_subject: SIGNATURE_REGISTRY[subject] の中身。
        旧 API では CRIME_SIGNATURES (= SIGNATURE_REGISTRY["KEI"]) 固定だったが、
        subject パラメータ化に伴い呼出側から明示注入する形に変更。
    """
    errors: list[str] = []
    skip = set(allowed_cross_refs) | {current_crime}

    for crime, sigs in signatures_for_subject.items():
        if crime in skip:
            continue
        for sig in sigs:
            if sig in html:
                # 出現位置を文字オフセットで報告（デバッグ用）
                offset = html.find(sig)
                snippet = html[max(0, offset - 20): offset + len(sig) + 20]
                snippet = snippet.replace("\n", " ")
                errors.append(
                    f"[NEGATIVE] '{sig}' (signature of {crime}) found at offset {offset}: "
                    f"...{snippet}..."
                )
    return errors


def positive_check(html: str, problem: dict) -> list[str]:
    """JSON の各値が HTML 内に存在するかを検査する。"""
    errors: list[str] = []

    # メタデータの照合
    # answer は list（multi-select 系、例: [1, 4]）の場合 "1,4" に正規化、
    # dict（fill-in 系、例: {"A":"5"}）の場合 "A=5,B=7,..." に正規化して照合する
    # (render.py の _format_answer と同じ正規化、slotmap §6.6 §2.4)。
    for field in ("crime", "answer", "correct_rate", "source"):
        value = problem.get(field)
        if value is None:
            continue
        if isinstance(value, list):
            value_str = ",".join(str(v) for v in value)
            # render.py の _format_answer と同期: K=1 単一要素は末尾カンマ
            if len(value) == 1:
                value_str = value_str + ","
        elif isinstance(value, dict):
            value_str = ",".join(f"{k}={v}" for k, v in value.items())
        else:
            value_str = str(value)
        if value_str not in html:
            errors.append(f"[POSITIVE/META] '{field}' value '{value_str}' not found in HTML")

    # combinations の整合性検査（slotmap §5.4 §6: combination-5 系のみ）
    # - answer (integer) が combinations のいずれかの label と一致するか
    # - 各 combination の set に含まれる ア〜オ ラベルが HTML 内に出現するか（中黒連結で）
    combinations = problem.get("combinations", [])
    if combinations:
        answer = problem.get("answer")
        if isinstance(answer, int):
            labels = [c.get("label") for c in combinations]
            if str(answer) not in labels:
                errors.append(
                    f"[POSITIVE/COMBO] answer={answer} が combinations の label "
                    f"{labels} に存在しない"
                )
        for c in combinations:
            members = c.get("set", [])
            members_str = "・".join(members)
            if members and members_str not in html:
                errors.append(
                    f"[POSITIVE/COMBO] combinations label={c.get('label')} の "
                    f"set 連結文字列 '{members_str}' が HTML に出現しない"
                )

    # 各 choice の照合
    for choice in problem.get("choices", []):
        label = choice["label"]

        # explanation が null → そもそも未完成（PDF 抽出失敗）
        if choice.get("explanation") is None:
            errors.append(
                f"[POSITIVE/EXPLANATION] choice {label}: explanation is null in JSON. "
                f"PDF からの抽出が完了していない。問題を完成させる前に補完すること。"
            )
            continue

        # stem の先頭 30 文字が HTML に含まれるか
        stem_head = choice["stem"][:30]
        if stem_head not in html:
            errors.append(
                f"[POSITIVE/STEM] choice {label}: stem head '{stem_head}' not found in HTML"
            )

        # explanation の先頭 30 文字が HTML に含まれるか
        exp_head = choice["explanation"][:30]
        if exp_head not in html:
            errors.append(
                f"[POSITIVE/EXPLANATION] choice {label}: explanation head '{exp_head}' "
                f"not found in HTML"
            )

        # case_citations の各文字列が HTML に含まれるか
        for case in choice.get("case_citations", []):
            if case not in html:
                errors.append(
                    f"[POSITIVE/CASE] choice {label}: case citation '{case}' not found in HTML"
                )

    return errors


def quarantine(html_path: Path) -> Path:
    """検証失敗 HTML を _quarantine/ に移動する。"""
    quarantine_dir = html_path.parent / "_quarantine"
    quarantine_dir.mkdir(exist_ok=True)
    dest = quarantine_dir / html_path.name
    shutil.move(str(html_path), str(dest))
    return dest


def validate(html_path: Path, json_path: Path) -> int:
    """検証実行。pass→0, fail→1。"""
    if not html_path.exists():
        print(f"ERROR: HTML not found: {html_path}", file=sys.stderr)
        return 2
    if not json_path.exists():
        print(f"ERROR: JSON not found: {json_path}", file=sys.stderr)
        return 2

    html = html_path.read_text(encoding="utf-8")
    problem = load_problem(json_path)

    crime = problem.get("crime")
    if not crime:
        print(f"ERROR: 'crime' field missing in {json_path}", file=sys.stderr)
        return 2

    # subject 未指定は KEI（後方互換、326-330 シリーズ）。
    subject = problem.get("subject", "KEI")
    if subject not in SIGNATURE_REGISTRY:
        print(
            f"ERROR: unknown subject {subject!r} in {json_path}. "
            f"valid: {sorted(SIGNATURE_REGISTRY)}",
            file=sys.stderr,
        )
        return 2
    signatures_for_subject = SIGNATURE_REGISTRY[subject]

    allowed = problem.get("allowed_cross_refs", [])

    errors: list[str] = []
    errors += negative_check(html, crime, allowed, signatures_for_subject)
    errors += positive_check(html, problem)

    if errors:
        print(f"FAIL: {html_path.name} ({len(errors)} error(s))", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        dest = quarantine(html_path)
        print(f"  → quarantined: {dest}", file=sys.stderr)
        return 1

    print(f"PASS: {html_path.name}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    return validate(Path(argv[1]), Path(argv[2]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
