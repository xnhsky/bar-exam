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
| **4-14** | 8 templates の diff-allowed part_b 領域 (6 variants / 108〜174 lines / avg 5,530 bytes、**本シリーズ最大規模 diff-allowed**) を `{{PART_B_FRAME}}` 単行に集約 slot 化。**パターン E 応用 2 例目** (A+C dispatch + 局所 D 配列駆動・UI 種別 dispatch 不要): 3 軸のうち軸 3 (choice_blocks、件数 3/4/5 可変) のみ局所 D を併用、軸 1〜2 (noun / labels) は dict 派生 A+C。全 variants が同一の choice-section 構造を共有するため UI 種別 dispatch は不要、builder は 1 つで完結 → パターン E の **最も単純な応用形**（軸数 3 / 引数数 2 / 補助関数 1、Phase 4-12 part_a よりさらに単純）。PART_B_FRAME_TEMPLATE (Python .format() 名前付き placeholder、2 引数) + PART_B_AXES_BY_TYPE (8 entry dict、{noun, labels}) + 補助関数 1 つ (_build_part_b_choice_block) + render_part_b()。slotmap §5.10 §2 part_b 行に注記追加。**part_b variants 6 → 1 集約**、累計 **-44,116 bytes 削減** (Phase 4-7 -70 KB に次ぐ 2 位、本シリーズ最大規模)。**diff-allowed 6 領域すべての slot 化が本 Phase で完走** (toc / pre_part_a / basis / part_a / a2 / part_b すべて 1 variant 集約完了) | `f3dc20c` (BACKLOG) / `91291ed` (render: render_part_b) / `5c567e2` (templates + slotmap 注記) | ✅ 維持（300 のみ DIFF） |

CP gate 正準 baseline: `_phase3_2_pre_patch_baseline.json` (`docs/cp-gate.md` §1)

---

## §1. Phase 4-14: part_b 領域 slot 化（**パターン E 応用 2 例目**: A+C + 局所 D・UI 種別 dispatch 不要）

### 1-1. 領域の特性

`part_b` は diff-allowed 領域（最大規模、avg 5,530 bytes / 174-108 lines、8 templates × 6 variants）。
PART B（記述/空欄/肢別解説）の `<div class="part-title">PART B ...` から A-3 共通根拠スタブ
preamble 末尾までの全範囲を `{{PART_B_FRAME}}` 1 slot に集約する。残 diff-allowed 1 領域の
最終消化、本シリーズ最大規模の集約（Phase 4-7 -70 KB に次ぐ 2 位、約 -44 KB 削減見込）。

事前同形性判定（8 templates × part_b region dump で確認）：

- **全 8 templates が同一の choice-section 構造**（1 件 = 32 lines + trailing blank）を共有
- 差分は **3 軸のみ**: `noun`（記述 / 空欄 / 肢、3 値）/ `labels`（カナ ア-オ・数字 1-5・A-E、
  6 系列）/ `count`（3 / 4 / 5、= `len(labels)`）
- 6 variants の共起: KTX/comb5 (174L) ・ msel5/sc5 (174L) ・ ox4 (141L) ・ fillin (174L) ・
  ox3comb8 (108L) ・ fillin8 (174L)。2 ペア + 4 独立。

### 1-2. 3 つの可変軸の分解

| # | 軸 | 取り得る値 | dispatch 方式 |
|:-:|---|---|---|
| 1 | noun（記述名詞） | 3 種（記述 / 空欄 / 肢） | dict + instruction_type |
| 2 | labels（ラベル系列） | 6 系列（ア-オ / ア-エ / ア-ウ / 1-5 / A-E）| dict + instruction_type |
| 3 | count（choice-section 件数）| 3 値（5 / 4 / 3）= `len(labels)` | 局所 D 配列駆動 |

→ 軸 1〜2 は A+C 組合せ（dict 派生）。**軸 3 のみ件数可変のため局所的に D（配列駆動）**を併用。
Phase 4-12 part_a で確立したパターン E の応用 2 例目。Phase 4-13 a2 で必要だった UI 種別
dispatch（ox-grid / slot-row 2 builder 切替）は不要 — 全 variants が同一の `choice-section`
構造を共有するため、builder は 1 つ。**構造的にはむしろ Phase 4-12 より単純**（軸数 3 / 引数数 2）、
規模だけが大きい。

### 1-3. 8 instruction_type × 6 variants の axes 表

| instruction_type | template | variant | noun | labels | count |
|---|---|:-:|:-:|---|:-:|
| ox-grid-5               | KTX_template          | 1 | 記述 | ア,イ,ウ,エ,オ | 5 |
| combination-5           | comb5                 | 1 | 記述 | ア,イ,ウ,エ,オ | 5 |
| multi-select-5          | msel5                 | 2 | 記述 | 1,2,3,4,5     | 5 |
| single-choice-5         | sc5                   | 2 | 記述 | 1,2,3,4,5     | 5 |
| ox-grid-4               | ox4                   | 3 | 記述 | ア,イ,ウ,エ    | 4 |
| fill-in                 | fillin                | 4 | 空欄 | A,B,C,D,E     | 5 |
| ox-grid-3-combination-8 | ox3comb8              | 5 | 記述 | ア,イ,ウ       | 3 |
| fillin8                 | fillin8               | 6 | 肢   | 1,2,3,4,5     | 5 |

### 1-4. universal vs per-instruction-type 境界

```html
<leading blank>                                                            ← universal
  <!-- ===... PART B ── {noun}別解説（{labels[0]}〜{labels[-1]}） -->     ← dict 派生
  <div class="part-title">PART B ── {noun}別解説（{labels[0]}〜{labels[-1]}）</div>  ← dict 派生
<blank>                                                                    ← universal

{choice_blocks}    ← 局所 D 配列駆動 (32 lines + trailing blank) × N (3/4/5)

  <!-- ===... A-3 共通根拠条文・判例（スタブ） -->                          ← universal (3 lines)
```

1 件の choice-section ブロック（32 lines + 末尾 blank、universal 28 lines + 可変 4 lines）:

```html
  <!-- =============== {noun}{labels[i]} =============== -->               ← 可変 (comment)
  <section class="choice-section {parity}" id="choice-{i+1}">              ← universal (parity 派生)
    <nav class="sec-nav">{back}{forward}</nav>                             ← 可変 (nav labels)
                                                                            ← universal (blank)
    <div class="choice-header-block">                                      ← universal
      <div class="choice-big-badge">{{CHOICE_X_LABEL}}</div>                ← universal
      <span class="verdict" data-verdict-label="{{CHOICE_X_VERDICT_LABEL}}">{{CHOICE_X_VERDICT_LABEL}}</span>  ← universal
    </div>                                                                  ← universal
                                                                            ← universal (blank)
    <div class="sub-card original">                                         ← universal
      <span class="label">{noun}原文</span>                                ← 可変 (noun)
      <p>{{CHOICE_X_STEM}}</p>                                              ← universal
    </div>                                                                  ← universal
                                                                            ← universal (blank)
    <div class="sub-card explanation">                                      ← universal (以下 13 行 universal)
      <h4>📖 解説原文</h4>
      <p>{{CHOICE_X_EXPLANATION}}</p>
    </div>

    <div class="sub-card basis-link">
      <h4>📚 根拠判例</h4>
      <p>{{CHOICE_X_CASES}}</p>
    </div>

    <div class="sub-card professor">
      <h4>👨‍🏫 教授の解説</h4>
      <p class="prof-summary">{{CHOICE_X_PROFESSOR_SUMMARY}}</p>
      <p class="prof-note">{{CHOICE_X_PROFESSOR_NOTE}}</p>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>
                                                                            ← universal (trailing blank)
```

各 section の nav 規則:
- 1 件目: `<a href="#answer-area">↑A-2</a><a href="#choice-2">{noun}{labels[1]}→</a>`
- 中間 (1 < s < N): `<a href="#choice-{s-1}">←{noun}{labels[s-2]}</a><a href="#choice-{s+1}">{noun}{labels[s]}→</a>`
- 最終 (s = N): `<a href="#choice-{N-1}">←{noun}{labels[N-2]}</a><a href="#basis">↓共通根拠</a>`

parity 規則: s 番目 (1-indexed) → `'odd' if s % 2 == 1 else 'even'`。

slot 名 X: s 番目 (1-indexed) → `"ABCDE"[s-1]`。

### 1-5. パターン E の応用位置付け

| パターン | 定義 | 例 |
|---|---|---|
| A | thin schema 派生（既存 field から render 派生）| 4-3 final_answer / 4-6 TOC |
| B | post-processing 注入 | 4-4 inject_ref_ids |
| C | universal const（純粋形 / .format() refined）| 4-5 marker_legend / 4-8/4-10 |
| D | 構造化レンダリング（配列駆動）| 3-3 basis / 4-7 drill_blocks |
| A + C | dispatch 関数で variant 解決（再利用定型化） | 4-6 TOC / 4-9 pre_part_a / 4-11 basis_secnav |
| E | **A+C dispatch + 軸の一部だけ D（局所配列駆動）を併用** | 4-12 part_a / 4-13 a2 (応用 1 例目) / **4-14 part_b (応用 2 例目)** |

Phase 4-14 は Phase 4-12 part_a で確立したパターン E の応用 2 例目。Phase 4-13 a2 で必要だった
UI 種別 dispatch（ox-grid / slot-row 2 builder の切替）は不要で、パターン E の単純形（dict 派生 +
配列駆動）の直接適用。Phase 4-12 part_a と同形（軸数 5 → 3 に縮減、引数数 6 → 2 に縮減、補助関数
2 → 1 に縮減）。

### 1-6. 命名規約

| 項目 | 名称 |
|---|---|
| slot 名 | `{{PART_B_FRAME}}` |
| template 名 | `PART_B_FRAME_TEMPLATE`（Python `.format()` 名前付き placeholder、2 引数）|
| 軸辞書名 | `PART_B_AXES_BY_TYPE`（instruction_type → `{noun, labels}` の 8 entry dict）|
| 関数名 | `render_part_b(instruction_type: str) -> str` |
| 補助関数 | `_build_part_b_choice_block(idx: int, label: str, noun: str, labels: list[str]) -> str`（1 関数のみ） |
| upgrade スクリプト | `scripts/upgrade_templates_part_b_slot.py` |

---

## §2. 設計（パターン E 応用 2 例目・確定版）

### 2-1. 採択方針

| 項目 | 設計 |
|---|---|
| schema 変更 | **なし** |
| JSON 改修 | **なし**（既存 `problem.instruction_type` から派生）|
| 新 slot | `{{PART_B_FRAME}}` を 8 templates の part_b 領域全体（108〜174 行）に置換 |
| render.py 改修 | `PART_B_FRAME_TEMPLATE` + `PART_B_AXES_BY_TYPE` + 補助 builder 1 関数 + `render_part_b()` + slot 配線 |
| 未対応 instruction_type | **`RuntimeError`** raise（Phase 4-6/4-9/4-11/4-12/4-13 同方針）|
| broken intermediate state | **なし**（diff-allowed 領域・旧 slot 不在、Commit 2 完了時点で templates は未変更のため render 動作維持）|
| 14 protected への影響 | byte-identical 維持期待（`render_part_b` 出力 = literal 一致）|
| 300 への影響 | 同上 |

### 2-2. PART_B_FRAME_TEMPLATE の 2 引数

`.format(**kwargs)` 名前参照。`{{CHOICE_X_*}}` 等 slot 参照は template 内で `{{{{...}}}}` 形式で
`.format()` エスケープ。

| 引数 | 由来 | 値の例 |
|---|---|---|
| `noun_full` | dict 派生（noun + range expansion）| `PART B ── 記述別解説（ア〜オ）` 等の冒頭タイトル |
| `choice_blocks` | 件数別関数生成（D 局所）| 32 lines 1 件 × N (3/4/5) を `\n` 区切り＋末尾改行 |

実装上、frame は noun と labels[0]/labels[-1] の単純連結を受け取り、内側で choice_blocks も生成する。

### 2-3. byte-identical 検証点（4 つ）

| # | 検証点 | 期待 |
|:-:|---|---|
| 1 | `render_part_b()` 単体出力 == 各 template の literal part_b region | 8/8 一致 |
| 2 | 全 15 件 `validate-tx.py` ERROR/WARNING | 0/0 維持 |
| 3 | `_cp_gate_check.py` PASS/DIFF | PASS=14 / DIFF=1 (300) |
| 4 | `check_template_sync.py` part_b variants | **6 → 1 に集約** |

### 2-4. upgrade スクリプト方式

Phase 4-12 part_a / Phase 4-13 a2 同形の β variant 別 OLD dispatch。各 template の OLD =
`render_part_b(instruction_type)` 出力（slot placeholder 含む literal）、共通 NEW =
`{{PART_B_FRAME}}` に置換。

### 2-5. check_template_sync 境界検出

part_b 領域は `answer_area_close + 1` 〜 `basis_section` で挟まれる（slot 化前後とも）。Phase 4-13
で `answer_area_close = a2_slot_idx`（A2_FRAME 単行）化済のため、part_b 開始位置はその直後の行。
slot 化後 part_b は `{{PART_B_FRAME}}` 単行となるが、boundary 検出器自体は part_b 単行
（基準は 'answer_area_close+1 〜 basis_section 直前'）のままで動く（追加分岐不要、Phase 4-12/4-13
の境界検出が既に part_b を「a2 close 後 〜 basis 前」と定義しているため、その range が 1 行
だろうと N 行だろうと検出可能）。slotmap §5.10 §2 にこれを明記する更新を併せて行う。

### 2-6. byte-identical 維持リスク

**低〜中程度**:
- 軸 1〜2 の dict 派生は規則的（リスク低）
- 軸 3（choice_blocks の N 回ループ）の D 配列駆動で件数依存出力 → Commit 2 着手中の関数単体
  検証で全 8 variants の literal との完全一致を確認
- choice-section 1 件 32 lines + trailing blank（universal 28 + 可変 4）の indent ずれが
  リグレッションの主リスク → 関数単体検証で逐語確認
- `{{` → `{` エスケープミスで `{{CHOICE_X_*}}` slot 参照が壊れる → Phase 4-12/4-13 同形踏襲で機械的に処理
- 3 規則（dict 派生 / choice_blocks builder / .format() escape）のどれか 1 つでも誤ると 8 protected で hash 変化
- ox3comb8 (n=3) で `{{CHOICE_D_*}}` / `{{CHOICE_E_*}}` slot が template から消失するが、
  build_slot_dict は既に未使用 slot を空文字で `setdefault` 済（render.py L1561-1570）→ 影響なし

---

## §3. 4 commit 実装計画

各 commit 後 STOP for review はスキップ（auto モード、設計確定承認済）。各 commit で CP gate +
check_template_sync + validate-tx（全 15 件）を実行。

| # | commit subject | 影響範囲 | broken state |
|---|---|---|---|
| 1 | `docs: BACKLOG.md §1 Phase 4-14 part_b 領域 slot 化 スコープ展開（パターン E 応用 2 例目: A+C + 局所 D）` | docs only | なし |
| 2 | `feat(phase4-14 render): PART_B_FRAME_TEMPLATE + PART_B_AXES_BY_TYPE + render_part_b() + slot 供給配線（パターン E 応用 2 例目）` | scripts/render.py | なし |
| 3 | `feat(phase4-14 templates): 8 templates の part_b 領域を {{PART_B_FRAME}} に置換 + slotmap §5.10 §2 境界検出注記更新` | upgrade script + 8 templates + slotmap | なし |
| 4 | `docs: 本セッション最終締め (Phase 4-14 完走) — SESSION-2026-05-22-SUMMARY + BACKLOG §0 Phase 4-14 完了追記 + §4 part_b 完了マーク` | docs only | なし |

### Phase 4-14 完了条件

- 全 15 件 `validate-tx.py` で ERROR 0 / WARNING 0 を**維持**
- CP gate PASS=14 / DIFF=1（300 のみ DIFF、Phase 4-13 完了状態と同じ）
- check_template_sync diff-allowed part_b が **6 variants → 1 variant** に集約
- 8 templates の part_b 領域（108〜174 行）が `{{PART_B_FRAME}}` 単行に縮減
- 残 diff-allowed 0 領域（5 領域 = toc / pre_part_a / basis / part_a / a2 / **part_b** 集約完了）

---

## §4. Phase 4-15 以降の候補（参考、未着手）

| 候補 | 領域 | 主要懸念 | 優先度 |
|---|---|---|---|
| ~~`part_b` 領域 (diff-allowed 6 variants)~~ | ~~avg 5,530 bytes / 174 lines~~ | ~~最大規模 diff-allowed、A + D 組合せ可能性~~ | **✅ Phase 4-14 で完了**（パターン E 応用 2 例目）|
| `css` 領域（巨大）| sync (60,743 bytes / 1,997 lines) | spec §Annex A canonical CSS と同期、構造化困難 | 低（要設計検討）|
| `js` 領域 | sync (17,552 bytes / 405 lines) | spec §Annex C canonical JS と同期、構造化困難 | 低（要設計検討）|
| Phase 5+ JX シリーズ着手 | JX 系（事例式）| spec/jx-v3.2-master.md 由来の構造化、1 問 1〜2 時間規模 | 別シリーズ・別 Phase（Phase 4 完了後）|

Phase 4-14 完了で **diff-allowed 6 領域すべての slot 化が完走**
（toc / pre_part_a / basis / part_a / a2 / part_b すべて 1 variant 集約完了）。
残作業は sync-required 2 領域（css / js）の集約、または Phase 5+ JX シリーズ着手。
TX shape の slot 化は Phase 4-14 で本質的に完了。

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
