#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX _lex の push 前ゲート（canonical エンジン整合 G41 ＋ 組合せ当否判定 G42・read-only）。

validate-tx-core.py の G41 を全 `*_lex.html` に横断適用し、「旧 _lex ベース流用＋
後付けパッチ script 接ぎ木」（codex 366-385 型）を push 前に機械的に弾く。さらに G42 で
「答え選択肢（組合せ1〜5）の当否を ox-stmt にした組合せ当否判定」（刑TX089/174/212/218/220/256/368 型）も弾く。

G1〜G40 は構造要素の存在しか見ないため、canonical/GENESIS-CORE.html の単一エンジンを
使わず旧 Annex C JS に band-aid(tx-inline-v1211-upgrade-js)を足した接ぎ木でも 1 ファイル
検証では PASS してしまう。本ゲートは G41 だけを束ねて配布前に走らせ、接ぎ木を含む
commit/push を止める（§7「保守的書き換え」禁止の構造的担保）。

対象は `.tx-inline-card` を持つ v12 インライン正典の _lex のみ。旧デザイン _lex
（インラインカード無し）と公式 000_TX は G41 自体が素通りなので無視される。

  python scripts/check-tx-lex-engine.py                 # 既定で outputs/ を走査
  python scripts/check-tx-lex-engine.py outputs/ux      # ルート指定
  python scripts/check-tx-lex-engine.py outputs/ux/000_TX/001_刑法/刑TX368_lex.html

失敗（接ぎ木検出）で終了コード 1。
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

PARTB_SOURCE_LABELS = {
    "ア": "1", "イ": "2", "ウ": "3", "エ": "4", "オ": "5",
    "カ": "6", "キ": "7", "ク": "8", "ケ": "9", "コ": "10",
    "A": "1", "B": "2", "C": "3", "D": "4", "E": "5",
    "F": "6", "G": "7", "H": "8", "I": "9", "J": "10",
    "Ａ": "1", "Ｂ": "2", "Ｃ": "3", "Ｄ": "4", "Ｅ": "5",
    "Ｆ": "6", "Ｇ": "7", "Ｈ": "8", "Ｉ": "9", "Ｊ": "10",
}


def normalize_partb_source(value: str) -> str:
    key = (value or "").strip()
    key = re.sub(r"^(記述|肢|空欄)", "", key).strip()
    if key.isdecimal():
        return key
    return PARTB_SOURCE_LABELS.get(key) or PARTB_SOURCE_LABELS.get(key.upper(), key)


def _load_validator():
    """validate-tx-core.py から Validator を動的ロード（ハイフン名のため import 不可）。"""
    spec = importlib.util.spec_from_file_location(
        "validate_tx_core", SCRIPTS / "validate-tx-core.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Validator


def _collect(roots: list[str]) -> list[Path]:
    files: set[Path] = set()
    for root in roots:
        p = Path(root)
        abs_path = p if p.is_absolute() else ROOT / p
        if abs_path.is_file() and abs_path.suffix == ".html":
            files.add(abs_path)
        elif abs_path.is_dir():
            files.update(abs_path.rglob("*_lex.html"))
    return sorted(files)


def main() -> int:
    Validator = _load_validator()
    roots = sys.argv[1:] or ["outputs"]
    files = _collect(roots)

    print("=== TX _lex push-front gate (G41 engine integrity + G42 combination-verdict + G43 detail-panel + G44 inline controls) ===")
    print("roots=" + ", ".join(roots))

    # スロット契約の存在＋版マーカー検査（ARIADNE の check_slot_contract 相当）。
    # 接ぎ木を「作った後に弾く」G41 の上流に、「そもそも自由編集させない」契約を据える。
    contract_fail = 0
    contract = ROOT / "canonical" / "GENESIS-CORE.placeholder.html"
    MARKER = "GENESIS_CORE_SLOT_CONTRACT"
    if not contract.exists():
        print("[ERROR] canonical/GENESIS-CORE.placeholder.html が無い（TX _lex スロット契約）")
        contract_fail = 1
    else:
        ctext = contract.read_text(encoding="utf-8", errors="replace")
        if MARKER not in ctext:
            print(f"[ERROR] GENESIS-CORE.placeholder.html に版マーカー {MARKER} が無い")
            contract_fail = 1
        elif "{{" not in ctext:
            print("[ERROR] GENESIS-CORE.placeholder.html に {{...}} スロットが無い")
            contract_fail = 1
        else:
            print(f"[OK] slot contract: {MARKER}")

    scanned = 0
    offenders: list[tuple[Path, list[str]]] = []
    for f in files:
        if f.stem.endswith("_lex") is False:
            continue
        try:
            v = Validator(f)
        except Exception as e:  # 読込/parse 失敗は他ゲートが拾うのでスキップ
            print(f"  読込スキップ: {f} ({e})")
            continue
        # G41＝接ぎ木（.tx-inline-card 無し＝旧デザインは g41 内で素通り）。
        # G42＝組合せ当否判定（ox-grid を持つ _lex 全般・旧デザイン含む）。各 g 内で対象判定。
        # G44＝inline 操作UI（解説だけ閲覧／解答を表示／二重番号／解法ナビ受け皿）の崩れを検出。
        v.g41_tx360_canonical_engine_integrity()
        v.g42_no_combination_verdict_stmt()
        v.g44_tx_inline_answer_controls_contract()
        gate_errs = [(code, msg) for code, msg in v.errors if code in ("G41", "G42", "G44")]
        if v.soup.select_one(".tx-inline-card"):
            scanned += 1
            # G43（v12.2 PLACEHOLDER-LOCK）＝詳説 panel 欠落（空 details）を弾く。
            # <details class="tx-inline-detail"> に data-partb-source panel が無いと
            # エンジン hydrateInlinePartBDetails の注入先が無く、詳説が空・無装飾になる
            # （361-385 で実際に出荷された既知事故）。インラインカードを持つ _lex のみ対象。
            for det in v.soup.select(".tx-inline-detail"):
                panel = det.select_one(".tx-detail-panel[data-partb-source]")
                if panel is None:
                    gate_errs.append(
                        ("G43", "詳説 <details class=tx-inline-detail> に data-partb-source panel が無い（空詳説・エンジン注入先欠落）")
                    )
                    break
                source = (panel.get("data-partb-source") or "").strip()
                if source and not source.isdecimal() and "resolvePartBSourceId" not in v.html:
                    gate_errs.append(
                        ("G43", f"詳説 data-partb-source='{source}' はラベル指定だが、エンジンに resolvePartBSourceId が無い（choice-N に解決できず空詳説になる）")
                    )
                    break
                source_id = normalize_partb_source(source)
                if source_id and not v.soup.find(id=f"choice-{source_id}") and not source.isdecimal():
                    gate_errs.append(
                        ("G43", f"詳説 data-partb-source='{source}' が PART B の choice-{source_id} に解決できない")
                    )
                    break
        if gate_errs:
            offenders.append((f, gate_errs))

    print(f"\nv12 inline _lex 走査={scanned} / G41(接ぎ木)+G42(組合せ当否)+G43(空詳説)+G44(回答UI) 検出ファイル={len(offenders)}")
    if offenders:
        print("\n[G41/G42/G43/G44] 接ぎ木 or 組合せ当否判定 or 空詳説 or 回答UI崩れを検出:")
        for f, errs in offenders:
            rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
            print(f"  ❌ {rel}")
            for code, m in errs:
                print(f"       - [{code}] {m}")
        print(
            "\nG41＝canonical/GENESIS-CORE.html の単一エンジンから作り直す（band-aid 不可）。"
            "G42＝組合せ当否判定を空欄/記述/事例単位の独立命題へ分解する（見本 刑TX350・§7 保守的書き換え禁止）。"
            "G44＝inline カードの操作UIを正典型（reveal-panel＋choice-num-inline＋sn-combos）へ戻す。"
        )
        return 1

    if contract_fail:
        return 1
    print("PASS ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
