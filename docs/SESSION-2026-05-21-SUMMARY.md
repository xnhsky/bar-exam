# Session 2026-05-21 — Phase 4-13 完走 + パターン E 応用 1 例目確立 (a2 領域 slot 化)

> 本セッションで bar-exam TX 系 slot 化整備が Phase 4-12 完了状態から **Phase 4-13
> 完了状態**まで前進した。**1 Phase 完走、4 commits (BACKLOG / render_a2 / templates +
> boundary / docs 締め)**。Phase 4-13 は **Phase 4-12 で確立したパターン E
> (A+C + 局所 D) の応用 1 例目**を a2 領域で実現。新たに **UI 種別 dispatch**
> (ox-grid / slot-row 2 builder の切替) を局所 D 内に組み込んだが、パターン E の枠内
> （dict 派生 + 配列駆動）に収まり新パターン F は不要を確認。**templates 累計
> -13,050 bytes 削減**（本セッション最大規模、Phase 4-7 -70 KB / Phase 4-12 -12 KB
> に次ぐ 3 位）。

---

## §1. 本セッション完了 Phase と commit 履歴

### Phase 4-13: a2 領域 slot 化（**パターン E 応用 1 例目**: A+C + 局所 D + UI 種別 dispatch）

8 templates の diff-allowed `a2` 領域 (8 variants / 25〜60 lines / avg 1,643 bytes、
A-2 解答エリアの `<section id="answer-area">` から `</section>` までの全範囲) を
`{{A2_FRAME}}` 単行に集約 slot 化。

6 つの可変軸を全て解析・分類:

| # | 軸 | dispatch 方式 | パターン |
|:-:|---|---|---|
| 1 | sec_nav_back（A-2 nav back-link） | dict 派生 | A+C |
| 2 | data_answer_type（answer-area attribute）| dict 派生 (5 種) | A+C |
| 3 | h3_title（answer-area H3 見出し）| dict 派生 (5 種) | A+C |
| 4 | answer_instruction（answer-instruction 文言）| dict 派生 (4 種) | A+C |
| 5 | selection_counter_line（selection-counter 行）| 2 値分岐 (msel5 のみ in) | A+C |
| 6 | ui_block（answer UI 構造）| **件数別関数生成 + UI 種別 dispatch** | **局所 D + 2 builder** |

→ 軸 1〜5 は A+C 組合せ（dict 派生）。**軸 6 のみ件数・block 種別・ラベル可変なため
局所 D（配列駆動）+ UI 種別 dispatch（2 builder の切替）を併用**。Phase 4-12 で
確立したパターン E の枠内（dict 派生 + 配列駆動の組合せ）に収まり、新パターン F は不要。

設計判断（BACKLOG §2-1）:
- schema 変更なし、JSON 改修なし（既存 problem.instruction_type 派生）
- 未対応 instruction_type で RuntimeError raise（Phase 4-6/4-9/4-11/4-12 同方針）
- broken intermediate state なし（diff-allowed 領域・旧 slot 不在）
- A2_FRAME_TEMPLATE は Python .format() 名前付き placeholder（6 引数）
- {{ANSWER}} 等の slot 参照は {{{{ANSWER}}}} 形式で .format() エスケープ
- answer_instruction 値内の {{SELECTION_COUNT}} は値として渡るため二重エスケープ不要
  （`.format()` は値を再解釈しない）

#### 軸 6 (ui_block) の構造詳細

| ui_kind | builder | 件数 | ラベル系 | template 構造 |
|---|---|---|---|---|
| ox-grid | `_build_a2_ox_grid_block(n)` | 4 / 5 | letters A〜E (隠れた) | `<div class="answer-ox-grid">` + `<div class="ox-row">` × N |
| slot-row | `_build_a2_slot_row_block(labels)` | 5 / 8 | digit (1〜N) or letters (A〜E) | `<div class="answer-row">` + `<button class="answer-slot">` × N |

ox-grid は 4-5 で件数だけ可変、ラベルは固定（{{CHOICE_X_LABEL}} placeholder 経由）。
slot-row は件数・ラベル系両方が可変（digit vs A〜E）。両 builder とも配列駆動 (D)
で、A+C dispatch（ui_kind dict 派生）で切替える。

#### byte-identical 検証点 4 つ全 PASS

| # | 検証点 | 結果 |
|:-:|---|---|
| 1 | `render_a2()` 単体出力 == 各 template の literal a2 region | **8/8 一致** |
| 2 | 全 15 件 `validate-tx.py` ERROR/WARNING | **0/0 維持** |
| 3 | `_cp_gate_check.py` PASS/DIFF | **PASS=14 / DIFF=1 (300)** |
| 4 | `check_template_sync.py` a2 variants | **8 → 1 に集約** |

#### commit 履歴

| commit | 内容 |
|---|---|
| `91d8b7a` | docs: BACKLOG.md §1 Phase 4-13 a2 領域 slot 化 スコープ展開（パターン E 応用 1 例目: A+C + 局所 D + UI 種別 dispatch）|
| `c173aa6` | feat(phase4-13 render): A2_FRAME_TEMPLATE + A2_AXES_BY_TYPE + render_a2() + slot 供給配線（パターン E 応用 1 例目）|
| `f6f3972` | feat(phase4-13 templates): 8 templates の a2 領域を {{A2_FRAME}} に置換 + check_template_sync 境界検出修正 |

### commit 戦略の Phase 4-12 比較

Phase 4-12 は render() 多段置換化で commit が 3 → 4 に増加したが、Phase 4-13 は
render() 改修不要（A2_FRAME 内の nested {{X}} 解決は Phase 4-12 で既に多段置換化
済のため再利用）→ **3 commit + docs 締め 1 = 4 commits** の Phase 4-12 同等規模。

| commit | 影響範囲 | ロールバック単位 |
|---|---|---|
| 1: BACKLOG | docs only | 設計記録のみ |
| 2: render_a2 | render.py（render_a2 関数追加）| Phase 4-13 機能追加 |
| 3: templates + boundary | templates + upgrade script + check_template_sync | template 層 + 検出器 |
| 4: docs 締め（本サマリ） | docs only | セッション終了記録 |

### 本セッション通算 commit カウント

| 区分 | commits |
|---|---|
| Phase 4-13 (3 commits) | `91d8b7a` / `c173aa6` / `f6f3972` |
| **本最終サマリ commit**（本ファイル + BACKLOG §0 P4-13 追記）| （今回追加、Phase 4-13 完走 SESSION 締め）|

Phase 4-13 のみ = **3 commits**、本最終サマリ更新込みで **4**。
remote `xnhsky/bar-exam` master への push は本サマリ commit 後に一括実施。

---

## §2. パターン E 応用 1 例目の構造化記述

### 2-1. Phase 4-12 (part_a) との比較

| 項目 | Phase 4-12 part_a | Phase 4-13 a2 |
|---|---|---|
| diff-allowed variants | 8 | 8 |
| 集約 lines | 19〜52 | 25〜60 |
| 集約 avg bytes | 1,515 | 1,643 |
| 削減合計 | -11,989 bytes | -13,050 bytes |
| 軸数 | 5 | 6 |
| 件数可変軸 | 1 (combo_section) | 1 (ui_block) |
| UI 種別 dispatch | なし | **あり** (ox-grid / slot-row 2 builder) |
| 件数可変ラベル系の軸 | なし (combo は単一形式) | **あり** (digit / A〜E) |
| FRAME_TEMPLATE 引数数 | 6 | 6 |
| render() 改修 | あり (多段置換化) | **なし** (Phase 4-12 多段置換を再利用) |
| 補助関数数 | 2 (_build_part_a_choice_lines / _build_part_a_combo_section) | 2 (_build_a2_ox_grid_block / _build_a2_slot_row_block) |

### 2-2. パターン E は新たな応用条件にも対応可能と確認

Phase 4-12 で「件数可変軸を 1 つ持つ A+C diff-allowed 領域」に対するパターン E を
確立した。Phase 4-13 では:

- 件数可変軸が **block 種別 dispatch** を含む（ox-grid / slot-row 2 種の構造分岐）
- 件数可変軸が **ラベル系 dispatch** を含む（digit / A〜E 2 種のラベル系列分岐）

この 2 種の dispatch が局所 D の builder 関数選択 + 引数選択で吸収できることを実証。
パターン E は「A+C dispatch + 局所 D 配列駆動」という抽象構造を持つため、件数可変軸
内のさらなる sub-dispatch は局所 D の引数 / builder 選択で対応可能。

### 2-3. パターン E の次の応用候補

| 候補 | 領域 | 件数可変軸の有無 | パターン E 適用見込 |
|---|---|---|---|
| **part_b** (diff-allowed 6 variants) | PART B choice-section | choice 件数 + ラベル系列 | 中（A+C 寄りだが規模大、設計セッション要）|

→ part_b 領域への直接応用が次セッション最有力。残 diff-allowed は **part_b の 1 領域のみ**に縮減。

---

## §3. 検証最終状態

| 検証項目 | 結果 |
|---|---|
| **CP gate** (`scripts/_cp_gate_check.py`) | PASS=14 / DIFF=1 (300) / EXTRA=0 / MISS=0 |
| **check_template_sync** | sync-required 7 領域すべて 8 templates byte-identical／ diff-allowed `toc` / `pre_part_a` / `basis` / `part_a` / **`a2`** はすべて **1 variant に集約済** |
| **validate-tx 全 15 件** | ERROR 0 / WARNING 0（Phase 4-4 で達成、Phase 4-5〜4-13 で維持） |
| **baseline** | `_phase3_2_pre_patch_baseline.json` 据え置き（Phase 4-13 も byte-identical 維持型 patch のため、`docs/cp-gate.md` §4 規定により baseline 更新不要） |
| **remote 反映** | `https://github.com/xnhsky/bar-exam.git` master = local HEAD (本セッション最終 commit)、本サマリ commit 含む 4 commits 反映予定 |

300 のみ DIFF=1 は意図的（Phase 3-3 basis 構造化 + Phase 4-3 final_answer +
Phase 4-4 anchor 注入 + 8th basis card 追加の累積結果）。Phase 4-13 は 300 含め
全 15 件 byte-identical で hash 不変。

### 集約状況サマリ（Phase 4-13 完了時点）

**sync-required 7 領域**：
| 領域 | 状態 |
|---|---|
| ~~marker_legend~~ | Phase 4-5 集約済 |
| ~~footer_spec~~ | Phase 4-2 集約済 |
| ~~part_c_d~~ | Phase 2 + 4-7 集約済 |
| ~~body_pre_toc~~ | Phase 4-8 集約済 |
| ~~head~~ | Phase 4-10 集約済 |
| css / js | **残**（要設計、spec §Annex A/C 同期で構造化困難）|

**diff-allowed 6 領域**：
| 領域 | 状態 |
|---|---|
| ~~toc~~ | Phase 4-6 集約 (6 → 1 variant) |
| ~~pre_part_a~~ | Phase 4-9 集約 (8 → 1 variant) |
| ~~basis~~ | Phase 4-11 集約 (6 → 1 variant) |
| ~~part_a~~ | Phase 4-12 集約 (8 → 1 variant、パターン E 新規確立) |
| ~~a2~~ | **Phase 4-13 集約 (8 → 1 variant)** ← 本セッション最終成果（パターン E 応用 1 例目）|
| part_b | **残**（パターン E の次の応用候補、最大規模 diff-allowed）|

---

## §4. 次セッション第 1 タスク候補

### 候補 A: part_b 領域 slot 化（パターン E 応用 2 例目・最有力）

a2 集約完了で、残 diff-allowed は **part_b の 1 領域のみ**に縮減。

- **part_b** (6 variants, avg 5,530 bytes / 174 lines): PART B choice-section の
  ラベル系統差 (記述 / 空欄 / N=3 等)、最大規模 diff-allowed。設計コスト大
  （件数可変軸の構造化と sub-card レイアウトの dispatch 設計が必要）

### 候補 B: 残 sync-required 2 領域（css / js）

- **css** sync 領域 (60,743 bytes / 1,997 lines)
- **js** sync 領域 (17,552 bytes / 405 lines)
- spec §Annex A/C と byte-level 同期で構造化困難、削減効果は大きいが構造化価値小

### 候補 C: Phase 5+ JX シリーズ着手

別仕様 (spec/jx-v3.2-master.md) 由来、別 Phase。1 問 1〜2 時間規模。

### 推奨順序

1. **A (Phase 4-14 part_b)** を最初に消化（パターン E 応用 2 例目、最大規模、設計コスト大）
2. **B (css/js)** 大規模一括集約（構造化価値小、規模大）
3. **C (Phase 5+ JX)** 別シリーズ着手

---

## §5. 保留事項（前セッションから継承、変動なし）

### 5-1〜5-7: 既存保留事項

- 5-1. `ref-law-X-Y-NNN` 規約（BACKLOG §6-1）
- 5-2. ref-case 段落クラス情報 id 注入（BACKLOG §6-2）
- 5-3. ref-id 双方向検証（BACKLOG §6-3）
- 5-4. TOC choice ラベル series の拡張余地（BACKLOG §6-5）
- 5-5. Phase 5+ JX シリーズ着手
- 5-6. `problems/_300_v6_backup.json`（git 未追跡、整理 commit で削除候補）
- 5-7. Phase 4-N 旧 baseline 群（同上）

### 5-8: a2_dump.txt（Phase 4-13 完了で削除）

- **状態**: Phase 4-13 着手前の事前調査用 a2 領域 dump（282 行、`_tmp_a2_dump.txt`）
- **処理**: Phase 4-13 完了に伴い本セッション内で **削除**（コミット完了済、git
  に追加しない方針）

---

## §6. セッション統計

| 項目 | 数値 |
|---|---|
| 本セッション通算 commits（Phase 4-13 + サマリ）| **3**（本最終サマリ commit 含めれば **4**） |
| Phase 4-13 のみの commits | **3**（render() 多段置換化が Phase 4-12 で完了済のため commit 増えず）|
| 14 protected ファイルの byte-identical 維持 | ✅ 全 commit |
| 300 (demo) の hash 変化 | Phase 4-13 では不変 |
| 全 15 件 validate-tx ERROR 0 / WARNING 0 | 維持 |
| templates 行数削減 | a2 各 25〜60 行 → 1 行 = 約 **279 行削減** |
| templates bytes 削減 | **-13,050 bytes ≒ -13 KB**（本セッション 1 Phase で達成、Phase 4-7 -70 KB / Phase 4-12 -12 KB に次ぐ 3 位）|
| diff-allowed variants 集約 | **a2: 8 → 1**（5 つ目の集約済領域 = toc / pre_part_a / basis / part_a / a2）|
| 確立パターン応用 | **E**（A+C + 局所 D + UI 種別 dispatch、応用 1 例目）|
| render() 改修 | **なし**（Phase 4-12 多段置換を再利用）|
| remote push | `xnhsky/bar-exam` master = local HEAD（本サマリ commit 後に push 予定）|
| BACKLOG.md 行数推移 | 約 250（Phase 4-12 完了）→ 約 280（Phase 4-13 完了）|

---

**本セッション、Phase 4-13 完走。**
**パターン E (A+C + 局所 D) の応用 1 例目を a2 領域で実現 = UI 種別 dispatch を局所 D**
**内に組み込み、新パターン F は不要を確認。pattern 体系の拡張可能性を実証。**
**render() 改修不要（Phase 4-12 多段置換を再利用）→ 3 commit + docs 締め = 4 commits 完走。**

remote `xnhsky/bar-exam` master に外部 backup 完了予定（4 commits 反映）。
templates 累計 **-13 KB 削減**（本セッション 1 Phase で達成、累計 -116.5 KB）。

Phase 4-14 part_b 領域 slot 化が次セッション最有力候補（残 diff-allowed 1 領域のみ）。
