#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX _lex の push 前ゲート（G41〜G45＋G50-G64・read-only）。

validate-tx-core.py の G41/G42/G44 を全 `*_lex.html` に横断適用し、「旧 _lex ベース流用＋
後付けパッチ script 接ぎ木」（codex 366-385 型）を push 前に機械的に弾く。さらに G42 で
「答え選択肢（組合せ1〜5）の当否を ox-stmt にした組合せ当否判定」（刑TX089/174/212/218/220/256/368 型）も弾く。
G45 は v12.2.1／v13 LOOP-CARD マーカーを持つファイル、またはコマンドで明示指定されたファイルに
適用し、TX355-359 実地修正後の表示LOCK（条文/判例ラベル、2カラム字下げ、物語ラベル非重畳、
物語本文の1字下げ）を弾く。G61/G62（v13n 不可侵原文ブロック＝マーカー字下げ・記述数一致）は
独立ゲートとして全 _lex に適用する（ブロック無しはスキップ＝誤爆ゼロ・監査 2026-07-11）。G63（カード⇄プール
三点整合）も同様に全 _lex へ適用し、正典↔corpus の CSS ドリフトは tx-lex-css-canonize --check を非ブロッキングで可視化する。

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


def _run_citation_era_gate(root: str = "outputs") -> int:
    """判例引用・元号の割れゲート（恒久対策・2026-07-09）。

    コーパス横断の不変条件（同一裁判所・数値年月日が別元号で引かれる＝OCR誤記の疑い）を
    check-citation-era.py で走査する。allowlist 済みの正当な別判例は抑止し、未確認の割れで 1。
    """
    import subprocess

    script = SCRIPTS / "check-citation-era.py"
    if not script.exists():
        return 0
    print("\n=== 判例引用・元号割れゲート (check-citation-era) ===")
    target = root if (ROOT / root).exists() else "outputs"
    proc = subprocess.run([sys.executable, "-X", "utf8", str(script), target])
    return proc.returncode


def _run_css_canonize_advisory() -> None:
    """正典↔corpus の共通CSSドリフト可視化（非ブロッキング・2026-07-11 監査対応）。

    tx-lex-css-canonize.py --check は「v13 の <style> 本体（palette :root 以外）＝全問共通」の
    照合ゲート。現状は生成世代差で不一致が多数（実測 102/110）のため push は止めず、
    件数と先頭数件だけを surfacing する（--apply 全展開＋実機確認の完了後にブロッキング昇格）。"""
    import subprocess

    script = SCRIPTS / "tx-lex-css-canonize.py"
    if not script.exists():
        return
    try:
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", str(script), "--check"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ROOT), timeout=300,
        )
    except Exception as e:
        print(f"\n[CSS-drift 可視化スキップ] {e}")
        return
    lines = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
    ng = [ln for ln in lines if ln.startswith("[CSS-NG]")]
    summary = next((ln for ln in reversed(lines) if ln.startswith("CSS canonical check")), "")
    print(f"\n[CSS-drift 可視化・非ブロッキング] {summary or 'summary なし'}")
    for ln in ng[:3]:
        print(f"  {ln}")
    if len(ng) > 3:
        print(f"  …ほか {len(ng) - 3} 件（一覧: python -X utf8 scripts/tx-lex-css-canonize.py --check）")
    if ng:
        print("  → 正典CSSとの世代差。tx-lex-css-canonize.py --apply の全展開＋実機確認後にブロッキング昇格予定。")


def _run_oxgrid_advisory(roots: list[str]) -> None:
    """特殊型 ○×健全性（L2/L3/L4）の可視化（非ブロッキング・2026-07-11 特殊問題監査対応）。

    L1（バッジ⇄key 矛盾＝最悪クラス）は G64 が三層でブロックする。L2 組合せ当否ナビ／L3 組合せ
    見出し／L4 全○退化は旧v11帯に既存分が残る（R 再生成で消滅予定）ため push は止めず、件数と
    先頭数件を surfacing する。検出 0 になったら check-lexia-preflight の oxgrid を strict 既定へ
    （docs/lex-oxgrid-integrity-audit.md §2）。"""
    import subprocess

    script = SCRIPTS / "check-lex-oxgrid-integrity.py"
    if not script.exists():
        return
    try:
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", str(script), "--warn-only", *roots],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ROOT), timeout=600,
        )
    except Exception as e:
        print(f"\n[特殊型 ox-grid 可視化スキップ] {e}")
        return
    lines = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
    ng = [ln for ln in lines if ln.startswith("[NG]")]
    summary = next((ln for ln in reversed(lines) if "check-lex-oxgrid-integrity" in ln), "")
    print(f"\n[特殊型 ox-grid 健全性 可視化・非ブロッキング] {summary.strip('= ') or 'summary なし'}")
    for ln in ng[:3]:
        print(f"  {ln}")
    if len(ng) > 3:
        print(f"  …ほか {len(ng) - 3} 件（一覧: python -X utf8 scripts/check-lex-oxgrid-integrity.py outputs/ux）")
    if ng:
        print("  → L1 は G64 がブロック済み。L2-L4 の既存分は旧v11帯＝R 再生成で消滅予定（0 になったら preflight strict 既定化）。")


def _run_solvenav_ownership_gate(files: list[Path]) -> int:
    """G68＝解法ナビ問題固有データ（var STEP/STMT・var ORDER）の所有権ゲート（ブロッキング）。

    実害（LEX388・2026-07-14）: tx-lex-v11-to-v13.py の engine swap が gold（刑TX359）の
    <script> を逐語移植し、59 ファイルの解法ナビが放火問題の設問を表示していた。
      (a) 複製検出: 同一の STEP/STMT JSON が複数ファイルに存在 → 本問データでない（ERROR）
      (b) 整合検出: var ORDER/KEYS のラベル集合 ≠ ox-row data-stmt 集合 → ナビが設問と同期不能（ERROR）
      (c) 未置換検出: __NUMS__/__KEYS__ プレースホルダ残存 → JS ReferenceError でナビ全体死亡（ERROR）
      (d) 写像欠落検出: 実ラベルがア〜オ等なのに 1..N の positional 行参照 → 回答が行に同期しない（ERROR）
    修正＝python -X utf8 scripts/fix-solvenav-step-mismatch.py --apply（(a)(b)）
        ＋python -X utf8 scripts/fix-solvenav-engine-keys.py --apply（(c)(d)）
    """
    step_owners: dict[str, list[Path]] = {}
    errors: list[str] = []
    for f in files:
        if not f.stem.endswith("_lex"):
            continue
        try:
            html = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rows = re.findall(r'<div class="ox-row" data-stmt="([^"]+)"', html)
        m = re.search(r"^[ \t]*var (?:STEP|STMT)\s*=\s*(\{.*\});", html, re.M)
        mo = re.search(r"^[ \t]*var ORDER\s*=\s*(\[[^\]]*\])", html, re.M)
        # 消去法エンジン（build-ox-lex 系）は ORDER=位置番号で、実 data-stmt は var KEYS が持つ。
        # その場合は KEYS を照合対象にする（ORDER 照合だと誤検出になる）。
        mk = re.search(r"^[ \t]*var KEYS\s*=\s*(\[[^\]]*\])", html, re.M)
        rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
        if m:
            step_owners.setdefault(m.group(1), []).append(f)
        # (c) ビルダプレースホルダ未置換（var NUMS = __NUMS__; 等）＝ JS ReferenceError でナビ死亡
        if re.search(r"<script\b[^>]*>[^<]*?__(?:NUMS|KEYS)__", html) or "__NUMS__" in html or "__KEYS__" in html:
            errors.append(f"{rel}: __NUMS__/__KEYS__ プレースホルダ未置換（ナビ JS が ReferenceError で死亡）")
        # (d) 実ラベル（ア〜オ等）に対する positional 行参照（1..N の番号ループのまま）＝同期不能
        rows_positional = rows == [str(i) for i in range(1, len(rows) + 1)]
        if (rows and not rows_positional
                and "var row = area.querySelector('.ox-row[data-stmt=\"'+b+'\"]');" in html
                and ("['1','2','3','4','5']" in html or re.search(r"\bvar NUMS\b", html))):
            errors.append(f"{rel}: positional 行参照が実ラベル {rows} と不一致（回答が ox-row に同期しない）")
        target = mk or mo
        if target and rows:
            try:
                import json as _json
                labels = _json.loads(target.group(1))
            except Exception:
                labels = None
            if labels is not None and set(labels) != set(rows):
                varname = "KEYS" if mk else "ORDER"
                errors.append(f"{rel}: var {varname} {labels} が ox-row ラベル {rows} と不一致（ナビ⇄設問の同期不能）")
    for sig, owners in step_owners.items():
        if len(owners) > 1:
            names = ", ".join(
                (p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p)) for p in owners
            )
            errors.append(f"同一の解法ナビ STEP/STMT が複数ファイルに存在（gold 混入の疑い）: {names}")
    if errors:
        print(f"\n[G68] 解法ナビ問題固有データの所有権崩れ {len(errors)} 件:")
        for e in errors:
            print(f"  ❌ {e}")
        print("  → python -X utf8 scripts/fix-solvenav-step-mismatch.py --apply で本問データへ復元")
        return 1
    print("[OK] G68 solve-nav ownership (STEP/STMT 複製なし・ORDER⇄ox-row 整合)")
    return 0


def main() -> int:
    Validator = _load_validator()
    roots = sys.argv[1:] or ["outputs"]
    files = _collect(roots)
    explicit_files = {
        (Path(root) if Path(root).is_absolute() else ROOT / root).resolve()
        for root in roots
        if ((Path(root) if Path(root).is_absolute() else ROOT / root).is_file())
    }

    print("=== TX _lex push-front gate (G41-G45 + G50-G60 v13 + G61/G62 v13n + G63/G64 sync + G66 sysmapはみ出し + G67 dgm + SNTIP + citation-era) ===")
    print("roots=" + ", ".join(roots))

    # 判例引用・元号の割れゲート（恒久対策・2026-07-09）。他ゲートの early-return に
    # masked されないよう最初に走らせる。コーパス横断の不変条件なので常に全 outputs を検査。
    if _run_citation_era_gate() != 0:
        return 1

    # G68＝解法ナビ問題固有データの所有権（複製＝gold 混入・ORDER⇄ox-row 不一致）。
    # コーパス横断の不変条件なので per-file ループの外で最初に走らせる（LEX388 恒久対策・2026-07-14）。
    if _run_solvenav_ownership_gate(files) != 0:
        return 1

    # スロット契約の存在＋版マーカー検査（ARIADNE の check_slot_contract 相当）。
    # 接ぎ木を「作った後に弾く」G41 の上流に、「そもそも自由編集させない」契約を据える。
    contract_fail = 0
    # v12=CORE と v13=CARD（active）の両契約を検査する（監査 2026-07-11：従来は CORE のみで、
    # active の CARD 契約が消えても/版マーカーが壊れても気づけなかった）。
    for cname, marker in (
        ("GENESIS-CORE.placeholder.html", "GENESIS_CORE_SLOT_CONTRACT"),
        ("GENESIS-CARD.placeholder.html", "GENESIS_CARD_SLOT_CONTRACT"),
    ):
        contract = ROOT / "canonical" / cname
        if not contract.exists():
            print(f"[ERROR] canonical/{cname} が無い（TX _lex スロット契約）")
            contract_fail = 1
            continue
        ctext = contract.read_text(encoding="utf-8", errors="replace")
        if marker not in ctext:
            print(f"[ERROR] {cname} に版マーカー {marker} が無い")
            contract_fail = 1
        elif "{{" not in ctext:
            print(f"[ERROR] {cname} に {{{{...}}}} スロットが無い")
            contract_fail = 1
        else:
            print(f"[OK] slot contract: {marker}")

    scanned = 0
    g45_scanned = 0
    offenders: list[tuple[Path, list[str]]] = []
    depth_notes: list[tuple[Path, list[tuple[str, str]]]] = []  # G56/G57 助言（非ブロッキング・§v13m 深さ）
    fact_notes: list[tuple[Path, list[tuple[str, str]]]] = []   # G65 助言（非ブロッキング・ox-stmt 要件事実完全性）
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
        # v13 LOOP-CARD 完全性（G50 構造／G51 BASIS中身／G52 横串trap／G53 相互リンク／G54 記憶のフック）。
        #     g50 は .tx-v13-verdict 検出時のみ ERROR を出す（v11/v12 は素通り）。ERROR 級だけ push を止める
        #     （nb-badge/brief-mark 等の移行 WARNING は v.warnings なのでブロックしない）。2026-07-07 追加。
        v.g50_v13_loopcard_structure()
        # G55＝参考条文カードの条番号ラベル整合（別条列挙型で①誤ラベルを弾く・刑TX365/351 恒久対策）。
        v.g55_basis_article_number_label()
        # G56/G57＝v13m 解説の深さ助言（薄い GIST/横串を欠く罠）。機械化困難ゆえ非ブロッキング（push は止めない）。
        v.g56_v13m_depth_advisory()
        _depth = [(c, m) for c, m in v.warnings if c in ("G56", "G57")]
        if _depth:
            depth_notes.append((f, _depth))
        # G58＝cross-cut 表示規約（助詞直付き/チップCSS欠落/字下げずれ＝ERROR）。決定論的な表示崩れなので push を止める。
        v.g58_cross_cut_display()
        # G60＝ox-stmt（復習プール全文）と inline カード（通常周回）の結論極性の反転を弾く。
        #     同一命題で answer-key を共有するため、逆向きだと片面で正答が誤答表示になる
        #     （刑TX368 記述1・2／刑TX362 エ・オ の実害）。決定論的・誤爆ゼロ設計なので push を止める。
        v.g60_ox_stmt_inline_polarity()
        # G61/G62＝v13n 不可侵原文ブロック（マーカー字下げ／記述数一致）。ブロック無しはスキップ＝誤爆ゼロ。
        #     監査 2026-07-11：従来は g45 内包＋v12.2.1 マーカー判定のため v13 で一切走らなかった穴を恒久修正。
        v.g61_original_block_marker_indent()
        v.g62_original_block_stmt_count()
        # G63＝インラインカード⇄SM2プール⇄answer-key の三点整合（data-stmt 集合一致・key長）。
        #     全コーパス実測 検出0（2026-07-11）を確認して ERROR ゲート化。決定論・誤爆ゼロ設計。
        v.g63_inline_pool_alignment()
        # G64＝v13 判定バッジ⇄answer-key の矛盾（integrity L1 の三層化・刑TX368 型の最悪クラス）。
        #     全コーパス実測 検出0（2026-07-11 特殊問題監査）を確認して ERROR ゲート化。
        v.g64_verdict_badge_key_consistency()
        # G66＝体系マップ SVG 見出しの viewBox 端クリップ（文字が切れる致命的表示崩れ）。
        #     カード幅固定に対し AI 生成見出しが長すぎるとはみ出す（実害＝刑TX382 記述5「（152）」切断）。
        #     ERROR は viewBox ハードクリップのみ＝誤爆ゼロ。修正＝scripts/tx-sysmap-fit.py（textLength 付与）。
        v.g66_sysmap_text_overflow()
        # G67＝図解コンポーネント（TX-DGM・任意スロット）。図解の無いファイルは素通り＝誤爆ゼロ。
        #     使用時の CSS 存在・契約許可クラスのみ・inline style 禁止・物語⇄カード data-dgm 同期
        #     （同 id 内容不一致）を ERROR で弾く（片側のみ/id無しは WARNING＝ブロックしない）。2026-07-13 追加。
        v.g67_diagram_component()
        # G65＝ox-stmt（復習プール全文）の要件事実完全性（主体身分・目的要件・官公性・承諾）。
        #     語彙差分ヒューリスティックで誤検出があり得るため非ブロッキング（push は止めない）。
        #     実害＝刑TX378 記述3（「市立…公務員」が圧縮で消え公文書性が判定不能）。2026-07-13 追加。
        before_g65 = len(v.warnings)
        v.g65_ox_stmt_fact_completeness()
        _facts = [(c, m) for c, m in v.warnings[before_g65:] if c == "G65"]
        if _facts:
            fact_notes.append((f, _facts))
        gate_errs: list[tuple[str, str]] = [
            (code, msg) for code, msg in v.errors
            if code in ("G41", "G42", "G44", "G50", "G51", "G52", "G53", "G54", "G55", "G58", "G60", "G61", "G62", "G63", "G64", "G66", "G67")
        ]
        # G45＝v12.2.1 表示LOCK（条文/判例ラベル・2カラム字下げ・物語ラベル等。v13 LOOP-CARD も維持する規約）。
        # 既存の未移行 v12.1.1 を全件落とさないため、v12.2.1／v13 LOOP-CARD として生成・更新済みの
        # ファイルか、明示指定ファイルだけに適用する（監査 2026-07-11：v13 スタンプを追加）。
        g45_required = (
            f.resolve() in explicit_files
            or "TX v12.2.1 LOOP-CORE" in v.html
            or "v12.2.1 LOOP-CORE" in v.html
            or "LOOP-CARD" in v.html
        )
        if g45_required:
            g45_scanned += 1
            before = len(v.errors)
            v.g45_tx_v1221_presentation_lock()
            gate_errs.extend((code, msg) for code, msg in v.errors[before:] if code == "G45")
        # SNTIP＝解法ナビ『コツ』箱の本文が .sn-tip-b で包まれず生挿入されている（grid の子が
        # インライン断片に分裂＝<b>語が左端へ落ちるぶら下がり）。正典 SOLVE-NAV/GENESIS-CARD は
        # <span class="sn-tip-b"> で包む。旧世代エンジン流用の回帰を弾く（修正＝tx-lex-v13k-labelfix.py）。
        if "sn-tip-h\">💡 コツ</span>'+s.tip+'</div>" in v.html:
            gate_errs.append(("SNTIP", "解法ナビ『コツ』本文が .sn-tip-b で未包み（grid崩れ・ぶら下がり）→ tx-lex-v13k-labelfix.py --apply"))
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

    print(f"\nv12/v13 inline _lex 走査={scanned} / G45対象={g45_scanned} / G41(接ぎ木)+G42(組合せ当否)+G43(空詳説)+G44(回答UI)+G45(表示LOCK)+G50-G60(v13)+G61/G62(v13n)+G63/G64(三点整合・バッジ⇄key矛盾)+G66(sysmapはみ出し)+G67(図解) 検出ファイル={len(offenders)}")
    if offenders:
        print("\n[G41-G45/G50-G62] 接ぎ木 or 組合せ当否判定 or 空詳説 or 回答UI崩れ or 表示LOCK崩れ or v13/v13n 規約崩れを検出:")
        for f, errs in offenders:
            rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
            print(f"  ❌ {rel}")
            for code, m in errs:
                print(f"       - [{code}] {m}")
        print(
            "\nG41＝canonical/GENESIS-CORE.html の単一エンジンから作り直す（band-aid 不可）。"
            "G42＝組合せ当否判定を空欄/記述/事例単位の独立命題へ分解する（見本 刑TX350・§7 保守的書き換え禁止）。"
            "G44＝inline カードの操作UIを正典型（reveal-panel＋choice-num-inline＋sn-combos）へ戻す。"
            "G45＝条文/判例ラベル・2カラム字下げ・物語ラベルを v12.2.1 正典へ戻す。"
        )
        return 1

    if depth_notes:
        print(f"\n[G56/G57 助言・非ブロッキング] v13m 解説の深さ候補（薄い GIST / 横串を欠く罠）{len(depth_notes)} ファイル:")
        for f, notes in depth_notes:
            rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
            print(f"  ⚠️ {rel}")
            for code, m in notes:
                print(f"       - [{code}] {m}")
        print("  → 機械化困難ゆえ push は止めない（WARNING）。著者が自己照合で解消（詳細 python -X utf8 scripts/check-tx-v13m-depth.py <file> --detail）。")

    if fact_notes:
        print(f"\n[G65 助言・非ブロッキング] ox-stmt の要件事実欠落候補（原文にある主体身分/目的要件/官公性/承諾が復習プール文に無い）{len(fact_notes)} ファイル:")
        for f, notes in fact_notes:
            rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
            print(f"  ⚠️ {rel}")
            for code, m in notes:
                print(f"       - [{code}] {m.split('。')[0]}")
        print("  → 語彙差分ヒューリスティックゆえ push は止めない（WARNING）。原文と照合し、正誤の分かれ目となる事実を ox-stmt に復元する（spec 第5-bis-2項）。")

    # 正典↔corpus CSS ドリフトの可視化（非ブロッキング・2026-07-11）。
    _run_css_canonize_advisory()

    # 特殊型 ○×健全性 L2-L4 の可視化（非ブロッキング・L1 は G64 がブロック・2026-07-11）。
    _run_oxgrid_advisory(roots)

    if contract_fail:
        return 1
    print("NOTE: PASS は構造・表示ゲートの通過です。解説内容と最新法令・判例・学説（新旧差分時の立法経緯・改正経緯を含む）は docs/tx-v12.2.1-inline-lock.md の最高エフォートレビューを別途必須とします。")
    print("PASS ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
