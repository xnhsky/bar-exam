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
| **4-9** | 8 templates の diff-allowed pre_part_a 領域 (4 lines / 180-223 bytes、8 variants 完全 1:1 対応) を `{{PRE_PART_A}}` に集約 slot 化。**A + C 組合せ 2 例目** (Phase 4-6 TOC 同形、PRE_PART_A_FORM_NAMES_BY_TYPE 辞書 8 entry + HTML コメント枠 const)。未対応 instruction_type で RuntimeError raise。fillin8 form 名内コロン全角 (U+FF1A) を template byte-identical 保証。pre_part_a variants 8→1 集約、各 -180〜-223 bytes、累計 -約 1,526 bytes | `0a4eb04` (BACKLOG) / `5b61da4` (render) / `ec8f7ab` (templates) | ✅ 維持（300 のみ DIFF） |
| **4-10** | 8 templates の sync-required head 領域 (867 bytes / 9 lines、内部に 4 動的 slot {{JP_PREFIX}}/{{PROBLEM_ID}}/{{CRIME}}/{{SOURCE_ID}}) を `{{HEAD}}` に集約 slot 化。**C refined 3 例目** (Phase 4-8 body_pre_toc 同形・機械的踏襲、Python .format() 名前付き placeholder + HEAD_TEMPLATE const)。旧 4 slot 据え置き (body_pre_toc/footer-spec で他参照あり)。title 行括弧全角「（」「）」を byte-identical 保証。font URL に `{`/`}` リテラル不在を確認、各 -859 bytes、累計 -6,872 bytes | `ce51f0a` (BACKLOG) / `c4f9efe` (render) / `4fee199` (templates) | ✅ 維持（300 のみ DIFF） |
| **4-11** | 8 templates の diff-allowed basis 領域 第 2 行 sec-nav (6 variants 完全 1:1、msel5+sc5 / KTX_template+comb5 同一) を `{{BASIS_SECNAV}}` に集約 slot 化。**A + C 組合せ 3 例目** (Phase 4-6 TOC / 4-9 pre_part_a 機械的踏襲、BASIS_SECNAV_LINKS_BY_TYPE 8 entry dict + sec-nav wrapper 関数)。未対応 instruction_type で RuntimeError。**A+C dispatch ロジックの機械的踏襲が定型化したことを完全実証**。basis variants 6→1 集約、各 -71〜-76 bytes、累計 -約 600 bytes | `8cd27b1` (BACKLOG) / `aa65463` (render) / `eae2e1c` (templates) | ✅ 維持（300 のみ DIFF） |
| **4-12** | 8 templates の diff-allowed part_a 領域 (8 variants / 19〜52 lines / avg 1,515 bytes) を `{{PART_A_FRAME}}` 単行に集約 slot 化。**パターン E 新規確立** (A+C dispatch + 局所 D 配列駆動の組合せ): 5 軸のうち軸 4 (combo_section、件数可変) のみ局所 D を併用、軸 1/2/3/5 は dict 派生 A+C。PART_A_FRAME_TEMPLATE (Python .format() 名前付き placeholder、6 引数) + PART_A_AXES_BY_TYPE (8 entry dict、5 軸の値) + 補助関数 2 つ + render_part_a()。`render()` を meta-slot 対応の**多段置換**に変更 (Phase 4-11 まで完全互換、安全ガード MAX_PASSES=5)。check_template_sync の part_a 境界検出も {{PART_A_FRAME}} 単行に対応 (TOC / marker_legend と同形、レガシーフォールバック温存)。part_a variants **8 → 1 集約**、累計 **-11,989 bytes 削減** (本セッション最大規模) | `eff2abd` (BACKLOG) / `e075d13` (render: render_part_a) / `bc7cb10` (render: 多段置換) / `b056102` (templates + boundary) | ✅ 維持（300 のみ DIFF） |
| **4-13** | 8 templates の diff-allowed a2 領域 (8 variants / 25〜60 lines / avg 1,643 bytes) を `{{A2_FRAME}}` 単行に集約 slot 化。**パターン E 応用 1 例目** (A+C dispatch + 局所 D 配列駆動 + UI 種別 dispatch): 6 軸のうち軸 6 (ui_block、件数・block 種別・ラベル可変) のみ局所 D + UI 種別 dispatch を併用、軸 1〜5 は dict 派生 A+C。A2_FRAME_TEMPLATE (Python .format() 名前付き placeholder、6 引数) + A2_AXES_BY_TYPE (8 entry dict、6 軸の値) + 補助関数 2 つ (_build_a2_ox_grid_block / _build_a2_slot_row_block) + render_a2()。check_template_sync の a2 境界検出も {{A2_FRAME}} 単行に対応 (Phase 4-12 PART_A_FRAME 同形機械的踏襲、レガシーフォールバック温存)。a2 variants **8 → 1 集約**、累計 **-13,050 bytes 削減** (本セッション最大規模、Phase 4-7 / 4-12 に次ぐ 3 位) | `91d8b7a` (BACKLOG) / `c173aa6` (render: render_a2) / `f6f3972` (templates + boundary) | ✅ 維持（300 のみ DIFF） |

CP gate 正準 baseline: `_phase3_2_pre_patch_baseline.json` (`docs/cp-gate.md` §1)

---

## §1. Phase 4-13: a2 領域 slot 化（**パターン E 応用 1 例目**: A+C + 局所 D + UI 種別 dispatch）

### 1-1. 領域の特性

`a2` は diff-allowed 領域（avg 1,643 bytes / 60〜25 lines、8 templates × 8 variants）。
A-2 解答エリアの `<section class="section" id="answer-area">` から `</section>` までの
全範囲を `{{A2_FRAME}}` 1 slot に集約する。

事前同形性判定（8 templates × a2 region dump で確認）：

- **2 templates は ox-grid 構造**（KTX_template 60 行 / ox4 52 行）: `<div class="answer-ox-grid">`
  + `<div class="ox-row">` × N (5 or 4)
- **6 templates は answer-slot-row 構造**（25〜28 行）: `<div class="answer-row">` +
  `<button class="answer-slot">` × N (5 / 8)
- msel5 のみ `<p class="selection-counter">` 行を含む（multi-select-5 専用）
- fill-in のみ ラベル系が letters-A-E（他 7 は digits-1-N）

### 1-2. 6 つの可変軸の分解

| # | 軸 | 取り得る値 | dispatch 方式 |
|:-:|---|---|---|
| 1 | sec_nav_back（A-2 nav 内 back-link） | 4 種（記述ア / 記述1 / 空欄A / 肢1） | dict + instruction_type |
| 2 | data_answer_type（answer-area 属性値） | 5 種（ox-grid / multi / single / fill-in / ox3comb8） | dict + instruction_type |
| 3 | h3_title（answer-area H3 見出し） | 5 種 | dict + instruction_type |
| 4 | answer_instruction（answer-instruction 文言） | 4 種 | dict + instruction_type |
| 5 | selection_counter（selection-counter 行有無） | in / out の 2 値（msel5 のみ in） | dict + instruction_type → 2 値分岐 |
| 6 | ui_block（answer UI 構造 + 件数 + ラベル） | block 種別 (ox-grid / slot-row) × 件数 (4/5/8) × ラベル系 (digit / A〜E) | dict + instruction_type → **局所 D 配列駆動 + UI 種別 dispatch** |

→ 軸 1〜5 は A+C 組合せ（dict 派生）。**軸 6 のみ件数・block 種別・ラベル可変なため局所的に D（配列駆動）**を併用。
これは Phase 4-12 で確立したパターン E の応用 1 例目。UI 種別 (ox-grid / slot-row) の
dispatch は局所 D の builder 関数 2 つを A+C で切替えることで吸収（block 種別自体は dict 派生で固定、件数・labels が配列駆動）。

### 1-3. 8 variants × instruction_type の axes 表

| instruction_type | sec_nav_back | data_answer_type | h3_title | sel_counter | ui_kind | ui_labels |
|---|---|---|---|:-:|---|---|
| ox-grid-5               | `↓記述ア` | ox-grid | 各記述の正誤を判定 | ✗ | ox-grid | A〜E (n=5) |
| ox-grid-4               | `↓記述ア` | ox-grid | 各記述の正誤を判定 | ✗ | ox-grid | A〜D (n=4) |
| ox-grid-3-combination-8 | `↓記述ア` | ox3comb8 | 正しい組合せを選択 | ✗ | slot-row | 1〜8 |
| multi-select-5          | `↓記述1`  | multi    | 該当する選択肢を選択 | **✓** | slot-row | 1〜5 |
| single-choice-5         | `↓記述1`  | single   | 該当する選択肢を選択 | ✗ | slot-row | 1〜5 |
| combination-5           | `↓記述ア` | single   | 正しい記述の組合せを選択 | ✗ | slot-row | 1〜5 |
| fill-in                 | `↓空欄A` | fill-in  | 各空欄に該当する候補番号を確認 | ✗ | slot-row | A〜E |
| fillin8                 | `↓肢1`    | single   | 正しい組合せを選択 | ✗ | slot-row | 1〜5 |

### 1-4. universal vs per-instruction-type 境界

```html
  <section class="section" id="answer-area">                  ← universal
    <nav class="sec-nav"><a href="#part-a">↑A-1</a>{sec_nav_back}</nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>A-2 解答</h2>  ← universal

    <div class="answer-area"                                  ← universal
         data-correct-value="{{ANSWER}}"
         data-answer-type="{data_answer_type}"                ← dict 派生
         data-explanation="{{ANSWER_EXPLANATION}}">
      <h3>{h3_title}</h3>                                     ← dict 派生
      <p class="answer-instruction">{answer_instruction}</p>  ← dict 派生
{selection_counter_line}                                      ← msel5 のみ 1 行 in

{ui_block}                                                    ← 局所 D + UI 種別

      <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>
      <div id="answer-feedback" hidden></div>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>  ← universal
  </section>                                                  ← universal
```

### 1-5. パターン E の応用位置付け

| パターン | 定義 | 例 |
|---|---|---|
| A | thin schema 派生（既存 field から render 派生）| 4-3 final_answer / 4-6 TOC |
| B | post-processing 注入 | 4-4 inject_ref_ids |
| C | universal const（純粋形 / .format() refined）| 4-5 marker_legend / 4-8/4-10 |
| D | 構造化レンダリング（配列駆動）| 3-3 basis / 4-7 drill_blocks |
| A + C | dispatch 関数で variant 解決（再利用定型化） | 4-6 TOC / 4-9 pre_part_a / 4-11 basis_secnav |
| E | **A+C dispatch + 軸の一部だけ D（局所配列駆動）を併用** | 4-12 part_a / **4-13 a2 (応用 1 例目)** |

Phase 4-13 は Phase 4-12 part_a で確立したパターン E の応用 1 例目。本領域では局所 D の
builder が UI 種別 (ox-grid / slot-row) に応じて 2 関数に分岐するが、これは A+C dispatch で
切替えるため、パターン E の枠内（dict 派生 + 配列駆動の組合せ）に収まる。

### 1-6. 命名規約

| 項目 | 名称 |
|---|---|
| slot 名 | `{{A2_FRAME}}` |
| template 名 | `A2_FRAME_TEMPLATE`（Python `.format()` 名前付き placeholder、7 引数）|
| 軸辞書名 | `A2_AXES_BY_TYPE`（instruction_type → axes dict）|
| 関数名 | `render_a2(instruction_type: str) -> str` |
| 補助関数 | `_build_a2_ox_grid_block(n: int) -> str` / `_build_a2_slot_row_block(labels: list[str]) -> str` |
| upgrade スクリプト | `scripts/upgrade_templates_a2_slot.py` |

---

## §2. 設計（パターン E 応用・確定版）

### 2-1. 採択方針

| 項目 | 設計 |
|---|---|
| schema 変更 | **なし** |
| JSON 改修 | **なし**（既存 `problem.instruction_type` から派生）|
| 新 slot | `{{A2_FRAME}}` を 8 templates の a2 領域全体（25〜60 行）に置換 |
| render.py 改修 | `A2_FRAME_TEMPLATE` + `A2_AXES_BY_TYPE` + 補助 builder 2 関数 + `render_a2()` + slot 配線 |
| 未対応 instruction_type | **`RuntimeError`** raise（Phase 4-6/4-9/4-11/4-12 同方針）|
| broken intermediate state | **なし**（diff-allowed 領域・旧 slot 不在、Commit 2 完了時点で templates は未変更のため render 動作維持）|
| 14 protected への影響 | byte-identical 維持期待（render_a2 出力 = literal 一致）|
| 300 への影響 | 同上 |

### 2-2. A2_FRAME_TEMPLATE の 7 引数

`.format(**kwargs)` 名前参照で、insertion order 非依存。`{{ANSWER}}` 等 slot 参照は
template 内で `{{{{ANSWER}}}}` 形式で `.format()` エスケープ。`answer_instruction` 値内の
`{{SELECTION_COUNT}}` は値として渡るため二重エスケープ不要（`.format()` は値を再解釈しない）。

| 引数 | 由来 | 値の例 |
|---|---|---|
| `sec_nav_back` | dict 派生 | `<a href="#choice-1">↓記述ア</a>` |
| `data_answer_type` | dict 派生 | `ox-grid` / `multi` / `single` / `fill-in` / `ox3comb8` |
| `h3_title` | dict 派生 | `各記述の正誤を判定` / `該当する選択肢を選択` / ... |
| `answer_instruction` | dict 派生 | `選択肢を{{SELECTION_COUNT}}個選んで...`（msel5）等 |
| `selection_counter_line` | 2 値分岐 | `<p class="selection-counter">選択数: 0 / {{SELECTION_COUNT}}</p>\n`（msel5）/ `""`（他 7）|
| `ui_block` | 件数別関数生成（D 局所） | `<div class="answer-ox-grid">...</div>`（ox-grid 系）/ `<div class="answer-row">...</div>`（slot-row 系）|

### 2-3. byte-identical 検証点（4 つ）

| # | 検証点 | 期待 |
|:-:|---|---|
| 1 | `render_a2()` 単体出力 == 各 template の literal a2 region | 8/8 一致 |
| 2 | 全 15 件 `validate-tx.py` ERROR/WARNING | 0/0 維持 |
| 3 | `_cp_gate_check.py` PASS/DIFF | PASS=14 / DIFF=1 (300) |
| 4 | `check_template_sync.py` a2 variants | **8 → 1 に集約** |

### 2-4. upgrade スクリプト方式

Phase 4-12 part_a 同形の β variant 別 OLD dispatch。各 template の OLD =
`render_a2(instruction_type)` 出力（slot placeholder 含む literal）、共通 NEW =
`{{A2_FRAME}}` に置換。

### 2-5. check_template_sync 境界検出

a2 領域は `answer_area_section` (`<section[^>]+id="answer-area"`) 〜 `answer_area_close`
(`</section>`) で挟まれる。slot 化後も a2 section open/close は A2_FRAME 内に内包される
ため境界自体は不変。検出器は `{{A2_FRAME}}` 単行に対応するための分岐を追加
（Phase 4-12 PART_A_FRAME 同形、レガシーフォールバック温存）。a2 slot 化時は
`answer_area_section = answer_area_close = a2_slot_idx` とすることで a2 section を
単行扱いし、part_b は `answer_area_close + 1` から開始する。

### 2-6. byte-identical 維持リスク

**中程度**:
- 軸 1〜5 の dict 派生は規則的（リスク低）
- 軸 6（ui_block）の D 配列駆動で件数依存出力 → Commit 2 着手中の関数単体検証で
  全 8 variants の literal との完全一致を確認
- ox-grid 系の indent（8/10/12 spaces）と slot-row 系の indent（6/8 spaces）の混在で
  1 文字ずれるとリグレッション → 関数単体検証で逐語確認
- msel5 の selection-counter 行（`{{SELECTION_COUNT}}` 含む）は `.format()` 経由でも
  raw 保持される（値は再解釈されない）→ Commit 2 単体検証で確認
- 4 規則（dict 派生 / selection_counter 分岐 / ui_block 2 builder / .format() escape）の
  どれか 1 つでも誤ると 8 protected で hash 変化

---

## §3. 4 commit 実装計画

各 commit 後 STOP for review はスキップ（auto モード）。各 commit で CP gate +
check_template_sync + validate-tx（全 15 件）を実行。

| # | commit subject | 影響範囲 | broken state |
|---|---|---|---|
| 1 | `docs: BACKLOG.md §0 Phase 4-12 完了追記 + §1 Phase 4-13 a2 スコープ（パターン E 応用 1 例目）` | docs only | なし |
| 2 | `feat(phase4-13 render): A2_FRAME_TEMPLATE + A2_AXES_BY_TYPE + render_a2() + slot 供給配線` | scripts/render.py | なし |
| 3 | `feat(phase4-13 templates): 8 templates の a2 領域を {{A2_FRAME}} に置換 + check_template_sync 境界検出修正` | upgrade script + 8 templates + check_template_sync | なし |
| 4 | `docs: 本セッション最終締め (Phase 4-13 完走) — SESSION-2026-05-21-SUMMARY + BACKLOG §0 Phase 4-13 完了追記` | docs only | なし |

### Phase 4-13 完了条件

- 全 15 件 `validate-tx.py` で ERROR 0 / WARNING 0 を**維持**
- CP gate PASS=14 / DIFF=1（300 のみ DIFF、Phase 4-12 完了状態と同じ）
- check_template_sync diff-allowed a2 が **8 variants → 1 variant** に集約
- 8 templates の a2 領域（25〜60 行）が `{{A2_FRAME}}` 単行に縮減

---

## §4. Phase 4-14 以降の候補（参考、未着手）

| 候補 | 領域 | 主要懸念 | 優先度 |
|---|---|---|---|
| `part_b` 領域 (diff-allowed 6 variants) | avg 5,530 bytes / 174 lines | 最大規模 diff-allowed、A + D 組合せ可能性 | **中（最有力）**（設計セッション要）|
| `css` 領域（巨大）| sync (60,743 bytes / 1,997 lines) | spec §Annex A canonical CSS と同期、構造化困難 | 低（要設計検討）|
| `js` 領域 | sync (17,552 bytes / 405 lines) | spec §Annex C canonical JS と同期、構造化困難 | 低（要設計検討）|
| Phase 5+ JX シリーズ着手 | JX 系（事例式）| spec/jx-v3.2-master.md 由来の構造化、1 問 1〜2 時間規模 | 別シリーズ・別 Phase（Phase 4 完了後）|

Phase 4-13 完了後、優先度順にスコープ化する。**Phase 4-14 は part_b 領域が最有力候補**
（最大規模 diff-allowed、A + D 組合せ可能性、設計セッション要）。残 diff-allowed は
**part_b の 1 領域のみ**に縮減。

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
