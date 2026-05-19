# Phase 3/4+ slot 化 BACKLOG

> `templates/KTX_template*.html` のリテラル HTML を JSON-schema-driven な slot に
> 段階的に置換していく作業の継続管理ドキュメント。各 Phase 完了時に §0 へ追記し、
> §1 を次 Phase スコープで上書きする運用。

---

## §0. 完了済み phase 一覧

| Phase | 内容 | commit | byte-identical 14 件 |
|---|---|---|---|
| **2** | PART C 7 sections (C-1〜C-7) を `{{C1_SYSTEMATIC}}`〜`{{C7_MEMORY}}` に slot 化 | `47c1f1d` | ✅ 維持 |
| **3-1〜3-5** | PART B basis cards (statute / case) を `{{BASIS_CARDS}}` に slot 化 + 構造化レンダリング。300.json を 1st demo | `1f54a17` | ✅ 維持（300 のみ意図的 DIFF） |
| **4-1** | PART A 【見解】(sc5 単独) を `{{VIEWS_BLOCK}}` に slot 化 | `88b0486` | ✅ 維持 |
| **4-2** | footer-spec feature-tag 列 (8 templates 共通) を `{{FOOTER_FEATURE_TAGS}}` に slot 化 | `88b0486` | ✅ 維持 |
| **4-3** | C-7 末尾 final-answer DOM block (§22-bis 単一 / §22-ter 多解答) を render.py 内嵌型で実装。300.json に 1st demo (詐欺罪・single-choice-5)。thin schema (final_answer.summary_html + 任意 extra_html)、β 配置 (template 不変)、hidden 属性必須を render 側で強制 | `0f7e673` (BACKLOG) / `abd2a28` (schema) / `f327664` (data) / `dee2bc0` (render) | ✅ 維持（300 のみ DIFF） |
| **4-4** | basis card rb-chip back-link target id を inject_ref_ids() 後処理で auto-注入 (canonical 規約 `ref-X-NNN`)。300.json basis 規約整理 (`-1-` qualifier 削除) + 最判平8.4.26 anchor 化 + 8th basis card 追加で完全 resolve。全 15 件 ERROR 0 / WARNING 0 達成 | `41f0edf` (BACKLOG) / `b2bb088` (render) / `49dea8d` (data) | ✅ 維持（300 のみ DIFF） |
| **4-5** | 8 templates の sync-required marker-legend block (11 行・709 bytes) を `{{MARKER_LEGEND}}` に集約 slot 化。universal content (subject / instruction_type 無関係) のため schema/JSON 改修なし、引数なし render_marker_legend() 関数で完結。--dry-run 8/8 OK で universality 実証 → extra_legend_items hook 不要が確定 | `6b64e17` (BACKLOG) / `9caa756` (render) / `3cc412c` (templates) | ✅ 維持（300 のみ DIFF） |
| **4-6** | 8 templates の diff-allowed `toc` 領域 (6 variants → 1 集約) を `{{TOC_ROW}}` に集約 slot 化。thin schema 派生 (problem.instruction_type → TOC_CHOICE_LABELS_BY_TYPE) で choice ラベル系列を生成、universal 部分 (TOC_HEAD / TOC_TAIL) は const。未対応 instruction_type で RuntimeError raise (silent fallback 不採用) | `7555a40` (BACKLOG) / `1afefca` (render) / `e93c3cb` (templates) | ✅ 維持（300 のみ DIFF） |
| **4-7** | 8 templates の PART D drill 12 件固定 slot 方式 (旧 60 個 DRILL_NN_* slot) を `{{DRILL_BLOCKS}}` 1 slot + 構造化レンダリング (render_drill_blocks) に移行。**パターン D 確立** (Phase 3-3 basis structured rendering の再利用)、A/B/C/D の **4 パターン体系完成**。escape 旧仕様踏襲 (720 field-values 検証で 0 件確認)、num JSON 信頼、旧 60 slot 完全削除。8 templates 各 -8,850 bytes (本セッション最大規模、累計 -70 KB) | `5f4856a` (BACKLOG) / `39cf18b` (render) / `28e6e28` (templates) | ✅ 維持（300 のみ DIFF） |
| **4-8** | 8 templates の sync-required body_pre_toc (393 bytes / 12 lines) を `{{BODY_PRE_TOC}}` slot 化。**案 (δ) refined: Python .format() 名前付き placeholder** で動的値埋込 (旧 6 slot {{JP_PREFIX}} 等は据え置き、本 slot は経路の重複)。**パターン C の 4 例目**（universal const を .format() 拡張、broken intermediate state なし）。8 templates 各 -377 bytes、累計 -3,016 bytes | `ff09a5b` (BACKLOG) / `7331edb` (render) / `783c8bb` (templates) | ✅ 維持（300 のみ DIFF） |

CP gate 正準 baseline: `_phase3_2_pre_patch_baseline.json` (`docs/cp-gate.md` §1)

---

## §1. Phase 4-9: pre_part_a slot 化（Phase 4-6 TOC と同形・A+C 組合せ 2 例目）

### 1-1. 領域の特性

`pre_part_a` は marker-legend 終了 〜 PART A タイトル直前の **diff-allowed 領域**（194-237
bytes / 4 lines、8 templates が **8 variants** で完全 1:1 対応）。各 variant は instruction_type
別の HTML コメントのみで、可変部分は **form 名文字列 1 つ**：

```html

  <!-- ============================================================
       PART A ── 問題情報（{form_name}）
       ============================================================ -->
```

variant の form 名対応:

| variant | template | instruction_type | form_name |
|:-:|---|---|---|
| 1 | sc5 | single-choice-5 | `single-choice-5 形式` |
| 2 | fillin8 | fillin8 | `fillin8 形式：8 blanks 表示 + 5 options 単一選択` |
| 3 | KTX_template | ox-grid-5 | `ox-grid-5 形式` |
| 4 | fillin | fill-in | `fill-in 形式` |
| 5 | msel5 | multi-select-5 | `multi-select-5 形式` |
| 6 | comb5 | combination-5 | `combination-5 形式` |
| 7 | ox3comb8 | ox-grid-3-combination-8 | `ox-grid-3 + combination-8 形式` |
| 8 | ox4 | ox-grid-4 | `ox-grid-4 形式` |

### 1-2. Phase 4-6 TOC と同形

| 観点 | Phase 4-6 TOC | Phase 4-9 pre_part_a |
|---|---|---|
| variant 数 | 6 (重複あり)| **8 (完全 1:1)** |
| 可変部分の規模 | choice 行数 + ラベル系列 | **form 名文字列 1 つ** |
| 設計 | dict + HEAD + TAIL + 関数 | dict + 単一 const + 関数 |
| パターン分類 | A + C 組合せ | A + C 組合せ (**2 例目**) |
| 削減 bytes | 累計 -約 3,200 | 累計 -約 1,600 |

→ Phase 4-6 TOC の dispatch ロジックを完全再利用。本セッション最小規模の slot 化対象。

### 1-3. 命名規約

| 項目 | 名称 |
|---|---|
| slot 名 | `{{PRE_PART_A}}` |
| dict 名 | `PRE_PART_A_FORM_NAMES_BY_TYPE` (instruction_type → form_name) |
| 関数名 | `render_pre_part_a(instruction_type: str) -> str` |
| upgrade スクリプト | `scripts/upgrade_templates_pre_part_a_slot.py` |

---

## §2. 設計（Phase 4-6 TOC 同形・確定版）

### 2-1. 採択方針

| 項目 | 設計 |
|---|---|
| schema 変更 | **なし** |
| JSON 改修 | **なし**（既存 `problem.instruction_type` から派生）|
| 新 slot | `{{PRE_PART_A}}` を 8 templates の pre_part_a 領域全体に置換 |
| render.py 改修 | `PRE_PART_A_FORM_NAMES_BY_TYPE` dict + `render_pre_part_a(instruction_type)` 関数 + slot 配線 |
| 未対応 instruction_type | **`RuntimeError`** raise（Phase 4-6 同方針、silent fallback 不採用）|
| 14 protected への影響 | byte-identical 維持期待（既存 variant が render 出力と一致）|
| 300 への影響 | 同上 |

### 2-2. render.py 追加内容

```python
PRE_PART_A_FORM_NAMES_BY_TYPE: dict[str, str] = {
    "ox-grid-5":               "ox-grid-5 形式",
    "ox-grid-4":               "ox-grid-4 形式",
    "ox-grid-3-combination-8": "ox-grid-3 + combination-8 形式",
    "multi-select-5":          "multi-select-5 形式",
    "single-choice-5":         "single-choice-5 形式",
    "combination-5":           "combination-5 形式",
    "fill-in":                 "fill-in 形式",
    "fillin8":                 "fillin8 形式：8 blanks 表示 + 5 options 単一選択",
}


def render_pre_part_a(instruction_type: str) -> str:
    """{{PRE_PART_A}} slot 値を返す（instruction_type 派生）。未対応 type で RuntimeError。"""
    if instruction_type not in PRE_PART_A_FORM_NAMES_BY_TYPE:
        raise RuntimeError(
            f"unknown instruction_type {instruction_type!r} for pre_part_a. "
            f"valid: {sorted(PRE_PART_A_FORM_NAMES_BY_TYPE)}"
        )
    form_name = PRE_PART_A_FORM_NAMES_BY_TYPE[instruction_type]
    return (
        '\n'
        '  <!-- ============================================================\n'
        f'       PART A ── 問題情報（{form_name}）\n'
        '       ============================================================ -->'
    )
```

`build_slot_dict()` に 1 行追加:
```python
slots["PRE_PART_A"] = render_pre_part_a(problem.get("instruction_type", ""))
```

### 2-3. upgrade スクリプト方式（β variant 別 OLD dispatch）

Phase 4-6 TOC と同形。`TEMPLATE_TO_TYPE` 表 + `FORM_NAMES_BY_TYPE` 表で各 template に対応
する OLD を構築、共通 NEW = `{{PRE_PART_A}}` に置換。8 templates × 8 variants で完全 1:1
なので variant 別 OLD 構築方式。

### 2-4. check_template_sync 境界検出

pre_part_a 領域は `marker_legend_close + 1` 〜 `part_a_title` で挟まれている。slot 化後
は `{{PRE_PART_A}}` 単一行となるが、`marker_legend_close` (Phase 4-5 で `{{MARKER_LEGEND}}`
化済) と `part_a_title` (`<div class="part-title">PART A`) は不変なので **境界検出更新
不要**。slot 化後の領域は 8 templates 同一 hash となり、diff-allowed の variants 数が
**8 → 1 に集約**。

### 2-5. byte-identical 維持リスク

**極めて低い**:
- 全 8 variants の形 (HTML コメント) は完全規則的
- form_name 文字列 1 つだけが可変、他は固定
- Phase 4-6 TOC で実証済 dispatch パターンを再利用
- 全 15 件 byte-identical 維持期待
- broken intermediate state 発生せず（diff-allowed 領域、旧 slot 不在のため Commit 2/3
  中間状態でも render 動作）

---

## §3. 3 commit 実装計画

各 commit 後 STOP for review。各 commit で CP gate + check_template_sync + validate-tx（全 15 件）を実行。

| # | commit subject | 影響範囲 | CP gate | sync | validate-tx |
|---|---|---|---|---|---|
| 1 | `docs: BACKLOG.md §0 Phase 4-8 完了追記 + §1 Phase 4-9 pre_part_a スコープ` | docs only | PASS=14 / DIFF=1 維持 | ✅ | 全 15 件 ERROR 0 / WARNING 0 維持 |
| 2 | `feat(phase4-9 render): PRE_PART_A_FORM_NAMES_BY_TYPE + render_pre_part_a() + slot 供給配線` | scripts/render.py | PASS=14 / DIFF=1 維持（template 未変更、新 slot 未使用）| ✅ | 全 15 件維持 |
| 3 | `feat(phase4-9 templates): 8 templates の pre_part_a を {{PRE_PART_A}} に置換` | upgrade script + 8 templates + outputs (全 15 件 byte-identical 期待) | PASS=14 / DIFF=1 維持 | ✅ | 全 15 件維持 |

### Phase 4-9 完了条件

- 全 15 件 `validate-tx.py` で ERROR 0 / WARNING 0 を**維持**
- CP gate PASS=14 / DIFF=1（300 のみ DIFF、Phase 4-8 完了状態と同じ）
- check_template_sync sync-required 7 領域 PASS / diff-allowed pre_part_a が **8 variants → 1 variant** に集約
- 8 templates の pre_part_a (4 行) が `{{PRE_PART_A}}` 単行に縮減（累計 -約 1,600 bytes）

---

## §4. Phase 4-10 以降の候補（参考、未着手）

| 候補 | 領域 | 主要懸念 | 優先度 |
|---|---|---|---|
| **`head` 領域**（DOCTYPE 〜 `<style>` 直前）| head sync 領域（867 bytes / 8 lines） | 静的、変更頻度低、Phase 4-5 marker-legend と同形 universal const パターン | **中（最有力）** |
| `css` 領域（巨大）| css sync 領域（60,743 bytes / 1,996 lines） | spec の §Annex A canonical CSS と同期、構造化困難 | 低（要設計検討） |
| `js` 領域 | js sync 領域（17,552 bytes / 404 lines） | spec の §Annex C canonical JS と同期、構造化困難 | 低（要設計検討） |
| Phase 5+ JX シリーズ着手 | JX 系（事例式） | spec/jx-v3.2-master.md 由来の構造化 (A〜H 8 サブセクション + 第 3〜5 部)、1 問 1〜2 時間規模 | 別シリーズ・別 Phase（Phase 4 完了後） |

Phase 4-9 完了後、優先度順にスコープ化する。**Phase 4-10 は head 領域が最有力候補**
（Phase 4-5 marker-legend と同形 universal const 純粋形、内部に動的 slot を含まず最小規模・
最低リスク。本セッションの slot 化対象の中で残る sync-required 静的領域は head/css/js の
3 つに集約された）。

---

## §5. 検証スクリプトと baseline

| スクリプト | 目的 | Phase 4-N 期待値 |
|---|---|---|
| `scripts/_cp_gate_check.py` | 全 15 件再 render → baseline と sha256 比較 | PASS=14 / DIFF=1 (300) |
| `scripts/check_template_sync.py` | 8 templates の sync-required 7 領域一致確認 | 全 commit で PASS |
| `scripts/validate-tx.py` | S1〜S82 構造/feature-tag/content independence 検証 | 全 15 件 ERROR 0 / WARNING 0 |

baseline は `_phase3_2_pre_patch_baseline.json` 据え置き（byte-identical 維持型 patch のため、`docs/cp-gate.md` §4 「baseline 更新ルール」 で更新不要に該当）。

---

## §6. 将来課題（未着手・参考）

### 6-1. 法条文の項・号 qualifier 付き ref-id 規約 `ref-law-X-Y-NNN`

Phase 4-4 では canonical KTX301 規約に揃え `ref-law-XXX-NNN`（項・号 qualifier なし）を採用。
ただし以下の限界がある:

- 同一条文の複数項（例: 246条1項 / 246条2項）を区別したい問題で、`ref-law-246-NNN` 単一系列は
  項を跨ぐ通し番号となり、basis chip 著者が記述ごとに該当項を特定する手数が増える
- 検索性・semantic 性で `ref-law-246-1-NNN` / `ref-law-246-2-NNN` の方が優れる

**着手判断条件**: 同一条文の複数項を同時参照する問題が出現したとき。それまでは canonical
規約で十分。実装時は `inject_ref_ids()` 内で anchor 表示テキストから「N項」「N号」を正規表現で
抽出し、id 構成に加える。

### 6-2. ref-case の冒頭以外への id 付与

現状 inject_ref_ids() は **document order の出現順**で NNN を付与する。記述N解説の文中で
ある case が複数回 inline 引用される場合、basis chip が "解説" / "あてはめ" / "考え方" 等の
複数ラベルで NNN を狙うが、NNN と段落 (h3, prof-summary, prof-note) との対応は chip 著者の
手作業で当てる必要がある。

**改善案**（着手条件: 大量の chip mis-targeting が発見されたとき）: render.py 側で
inline anchor の所属段落 (`<p class="prof-summary">` 内 / `<p class="prof-note">` 内 等) を
判定し、id に段落クラス情報を含める。但しこれは canonical 規約からの逸脱になるため、規約改定
の合意必要。

### 6-3. ref-id 全件の双方向検証

Phase 4-4 完了後、`validate-tx.py` の S8 は href→id 方向（chip が target を持つか）のみ検証する。
逆方向（id を target とする chip が存在するか）の検証は未実装。未使用 id があっても害はないが、
仕様の clean 性追求のため将来追加候補。

### 6-5. TOC choice ラベル series の拡張余地

Phase 4-6 で採用した `TOC_CHOICE_LABELS_BY_TYPE` は現状 4 series × 最大 3 N 値 = 6 cells 占用。
24 cells のうち 18 cells が拡張余地（例: ロ〜ホ系 / 漢数字 / N=6+ 等）。現状仕様外、設計に含めず
（YAGNI 重視）。新 instruction_type 追加時は辞書 1 行追加で対応可能。

### 6-6. drill-block field の HTML escape 規約

Phase 4-7 で旧仕様踏襲（escape なし）を採用。現運用では drill 各 field の HTML 内容が
attribute 安全な範囲に収まっているため byte-identical を優先。

**着手判断条件**: drill explanation 等に `<` `"` `&` 等の attribute-unsafe 文字が含まれる
問題が出現し、HTML 構文崩壊が顕在化したとき。実装時は `data-explanation` 等の attribute
内に出力する slot に対して個別に `html.escape(v, quote=True)` を適用、quiz-answer の text
content 出力は escape なし維持。**byte-diff が出るため新 baseline 切り替えが必要**になる
点に注意。
