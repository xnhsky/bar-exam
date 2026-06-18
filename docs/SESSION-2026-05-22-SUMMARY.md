# Session 2026-05-22 — Phase 4-14 完走 + パターン E 応用 2 例目確立 (part_b 領域 slot 化、diff-allowed 完走)

> 本セッションで bar-exam TX 系 slot 化整備が Phase 4-13 完了状態から **Phase 4-14
> 完了状態**まで前進した。**1 Phase 完走、4 commits (BACKLOG / render_part_b /
> templates + slotmap 注記 / docs 締め)**。Phase 4-14 は **Phase 4-12 で確立した
> パターン E (A+C + 局所 D) の応用 2 例目**を part_b 領域で実現。Phase 4-13 a2 で
> 必要だった UI 種別 dispatch (2 builder 切替) は不要 — 全 variants が同一の
> choice-section 構造を共有するため builder は 1 つで完結（軸数 3 / 引数数 2 /
> 補助関数 1、Phase 4-12 part_a よりさらに単純）。**templates 累計 -44,116 bytes
> 削減**（本シリーズ最大規模、Phase 4-7 -70 KB に次ぐ 2 位、Phase 4 系列累計 -160 KB）。
>
> **本 Phase で diff-allowed 6 領域すべての slot 化が完走**（toc / pre_part_a /
> basis / part_a / a2 / part_b の 6 領域すべて 1 variant に集約完了）。

---

## §1. 本セッション完了 Phase と commit 履歴

### Phase 4-14: part_b 領域 slot 化（**パターン E 応用 2 例目**: A+C + 局所 D・UI 種別 dispatch 不要）

8 templates の diff-allowed `part_b` 領域（最大規模、174-108 lines / avg 5,530 bytes、
PART B 見出し 〜 全 choice-section 〜 A-3 共通根拠スタブ preamble 末尾）を
`{{PART_B_FRAME}}` 単行に集約 slot 化。

3 つの可変軸を全て解析・分類:

| # | 軸 | dispatch 方式 | パターン |
|:-:|---|---|---|
| 1 | noun（記述 / 空欄 / 肢、3 値）| dict 派生 | A+C |
| 2 | labels（カナ ア-オ / 1-5 / A-E 等、6 系列）| dict 派生 | A+C |
| 3 | count（3 / 4 / 5、= len(labels)）| 件数別関数生成 | **局所 D 配列駆動** |

→ 軸 1〜2 は A+C 組合せ（dict 派生）。**軸 3 のみ件数可変のため局所 D（配列駆動）**を
併用。Phase 4-12 で確立したパターン E の応用 2 例目。Phase 4-13 a2 で必要だった
UI 種別 dispatch（ox-grid / slot-row 2 builder 切替）は不要 — 全 variants が同一の
choice-section 構造を共有するため builder は 1 つで完結。

設計判断（BACKLOG §2-1）:
- schema 変更なし、JSON 改修なし（既存 problem.instruction_type 派生）
- 未対応 instruction_type で RuntimeError raise（Phase 4-6/4-9/4-11/4-12/4-13 同方針）
- broken intermediate state なし（diff-allowed 領域・旧 slot 不在）
- PART_B_FRAME_TEMPLATE は Python .format() 名前付き placeholder（2 引数）
- {{CHOICE_X_*}} 等の slot 参照は {{{{...}}}} 形式で .format() エスケープ
- ox3comb8 (n=3) で CHOICE_D / CHOICE_E slot 未使用、build_slot_dict が既に空文字
  setdefault 済（render.py L1561-1570）→ 影響なし

#### 軸 3 (choice_blocks) の構造詳細

| count | template | section 構造 | parity 系列 |
|:-:|---|---|---|
| 3 | ox3comb8 | 3 件 (ア,イ,ウ) | odd, even, odd |
| 4 | ox4 | 4 件 (ア,イ,ウ,エ) | odd, even, odd, even |
| 5 | KTX/comb5/msel5/sc5/fillin/fillin8 | 5 件 (ア-オ / 1-5 / A-E) | odd, even, odd, even, odd |

choice-section 1 件 = 32 lines + trailing blank line（universal 28 + 可変 4）。
可変 4 lines は (1) コメントヘッダ / (2) sec-nav back+forward / (3) `<span class="label">{noun}原文</span>`
の 3 種類。

#### byte-identical 検証点 4 つ全 PASS

| # | 検証点 | 結果 |
|:-:|---|---|
| 1 | `render_part_b()` 単体出力 == 各 template の literal part_b region | **8/8 一致** |
| 2 | 全 15 件 `validate-tx.py` ERROR/WARNING | **0/0 維持** |
| 3 | `_cp_gate_check.py` PASS/DIFF | **PASS=14 / DIFF=1 (300)** |
| 4 | `check_template_sync.py` part_b variants | **6 → 1 に集約** |

#### commit 履歴

| commit | 内容 |
|---|---|
| `f3dc20c` | docs: BACKLOG.md §1 Phase 4-14 part_b 領域 slot 化 スコープ展開（パターン E 応用 2 例目: A+C + 局所 D）|
| `91291ed` | feat(phase4-14 render): PART_B_FRAME_TEMPLATE + PART_B_AXES_BY_TYPE + render_part_b() + slot 供給配線（パターン E 応用 2 例目）|
| `5c567e2` | feat(phase4-14 templates): 8 templates の part_b 領域を {{PART_B_FRAME}} に置換 + slotmap §5.10 §2 境界検出注記更新 |

### commit 戦略の Phase 4-13 比較

Phase 4-13 (3 commits + docs) と同形の 4 commits 体系。Phase 4-14 では render()
改修不要（Phase 4-12 多段置換を再利用）→ **3 commit + docs 締め 1 = 4 commits**
の同等規模。

| commit | 影響範囲 | ロールバック単位 |
|---|---|---|
| 1: BACKLOG | docs only | 設計記録のみ |
| 2: render_part_b | render.py（render_part_b 関数追加）| Phase 4-14 機能追加 |
| 3: templates + slotmap 注記 | templates + upgrade script + slotmap | template 層 + 注記 |
| 4: docs 締め（本サマリ） | docs only | セッション終了記録 |

### 本セッション通算 commit カウント

| 区分 | commits |
|---|---|
| Phase 4-14 (3 commits) | `f3dc20c` / `91291ed` / `5c567e2` |
| **本最終サマリ commit**（本ファイル + BACKLOG §0 P4-14 追記 + §4 part_b 完了マーク）| （今回追加、Phase 4-14 完走 SESSION 締め）|

Phase 4-14 のみ = **3 commits**、本最終サマリ更新込みで **4**。
remote `xnhsky/bar-exam` master への push は本サマリ commit 後に一括実施。

---

## §2. パターン E 応用 2 例目の構造化記述

### 2-1. Phase 4-12 (part_a) / Phase 4-13 (a2) / Phase 4-14 (part_b) の比較

| 項目 | Phase 4-12 part_a | Phase 4-13 a2 | **Phase 4-14 part_b** |
|---|---|---|---|
| diff-allowed variants | 8 | 8 | **6** |
| 集約 lines | 19〜52 | 25〜60 | **108〜174** |
| 集約 avg bytes | 1,515 | 1,643 | **5,531** |
| 削減合計 | -11,989 bytes | -13,050 bytes | **-44,116 bytes** |
| 軸数 | 5 | 6 | **3** |
| 件数可変軸 | 1 (combo_section) | 1 (ui_block) | **1 (choice_blocks)** |
| UI 種別 dispatch | なし | あり (2 builder) | **なし (1 builder)** |
| 件数可変ラベル系の軸 | なし | あり (digit / A〜E) | **あり (3 軸統合)** |
| FRAME_TEMPLATE 引数数 | 6 | 6 | **2** |
| render() 改修 | あり (多段置換化) | なし (再利用) | **なし (再利用)** |
| 補助関数数 | 2 | 2 | **1** |

### 2-2. パターン E の最も単純な応用形

Phase 4-14 は **構造的にはむしろ Phase 4-12 より単純**（軸数 3、引数数 2、補助関数 1）。
規模だけが大きい（本シリーズ最大規模）という特殊性を持つ。

パターン E の応用条件:
- A+C dispatch（dict 派生）で吸収できる軸 (1〜2)
- 局所 D 配列駆動で吸収できる件数可変軸 1 つ
- それ以外の sub-dispatch（UI 種別 / ラベル系切替 等）は局所 D 内で吸収可能

→ Phase 4-12〜4-14 で「パターン E は diff-allowed 領域の最終解」として実証完了。
追加の新パターン (F+) は本シリーズで不要を確認。

### 2-3. パターン E の次の応用候補

| 候補 | 領域 | 件数可変軸の有無 | パターン E 適用見込 |
|---|---|---|---|
| なし（diff-allowed 完走） | 残 diff-allowed 0 領域 | — | — |

→ **diff-allowed 領域は本 Phase 4-14 で完走**。残作業は sync-required 2 領域 (css / js)
または別 Phase（Phase 5+ JX シリーズ）。

---

## §3. 検証最終状態

| 検証項目 | 結果 |
|---|---|
| **CP gate** (`scripts/_cp_gate_check.py`) | PASS=14 / DIFF=1 (300) / EXTRA=0 / MISS=0 |
| **check_template_sync** | sync-required 7 領域すべて 8 templates byte-identical／ diff-allowed `toc` / `pre_part_a` / `basis` / `part_a` / `a2` / **`part_b`** はすべて **1 variant に集約済** |
| **validate-tx 全 15 件** | ERROR 0 / WARNING 0（Phase 4-4 で達成、Phase 4-5〜4-14 で維持） |
| **baseline** | `_phase3_2_pre_patch_baseline.json` 据え置き（Phase 4-14 も byte-identical 維持型 patch のため、`docs/cp-gate.md` §4 規定により baseline 更新不要） |
| **remote 反映** | `https://github.com/xnhsky/bar-exam.git` master = local HEAD (本セッション最終 commit)、本サマリ commit 含む 4 commits 反映予定 |

300 のみ DIFF=1 は意図的（Phase 3-3 basis 構造化 + Phase 4-3 final_answer +
Phase 4-4 anchor 注入 + 8th basis card 追加の累積結果）。Phase 4-14 は 300 含め
全 15 件 byte-identical で hash 不変。

### 集約状況サマリ（Phase 4-14 完了時点）

**sync-required 7 領域**:
| 領域 | 状態 |
|---|---|
| ~~marker_legend~~ | Phase 4-5 集約済 |
| ~~footer_spec~~ | Phase 4-2 集約済 |
| ~~part_c_d~~ | Phase 2 + 4-7 集約済 |
| ~~body_pre_toc~~ | Phase 4-8 集約済 |
| ~~head~~ | Phase 4-10 集約済 |
| css / js | **残**（要設計、spec §Annex A/C 同期で構造化困難）|

**diff-allowed 6 領域**:
| 領域 | 状態 |
|---|---|
| ~~toc~~ | Phase 4-6 集約 (6 → 1 variant) |
| ~~pre_part_a~~ | Phase 4-9 集約 (8 → 1 variant) |
| ~~basis~~ | Phase 4-11 集約 (6 → 1 variant) |
| ~~part_a~~ | Phase 4-12 集約 (8 → 1 variant、パターン E 新規確立) |
| ~~a2~~ | Phase 4-13 集約 (8 → 1 variant、パターン E 応用 1 例目) |
| ~~part_b~~ | **Phase 4-14 集約 (6 → 1 variant、パターン E 応用 2 例目)** ← 本セッション最終成果 |

**→ diff-allowed 6 領域すべて 1 variant に集約完了（本 Phase で完走）。**

---

## §4. 次セッション第 1 タスク候補

### 候補 A: 残 sync-required 2 領域（css / js）の集約

- **css** sync 領域 (60,743 bytes / 1,997 lines)
- **js** sync 領域 (17,552 bytes / 405 lines)
- spec §Annex A/C と byte-level 同期で構造化困難、削減効果は大きいが構造化価値小
- 集約形態の検討要（universal const と spec 同期の両立、render.py 経由か直接 read か）

### 候補 B: Phase 5+ JX シリーズ着手

別仕様 (spec/jx-v3.2-master.md) 由来、別 Phase。1 問 1〜2 時間規模。

### 候補 C: 既存 14 baseline + 300 の本格内容生成（A-3 / PART C / PART D 等のスタブ解消）

`docs/Phase3-4-BACKLOG.md` §4 でスコープ外として保留中。schema 拡張と JSON 改修が必要、
1 問あたりの内容生成コストが大きい。

### 推奨順序

1. **A (css/js)** 大規模一括集約（構造化価値小、規模大、ただし TX シリーズの slot 化完走）
2. **B (Phase 5+ JX)** 別シリーズ着手
3. **C (本格内容生成)** schema 拡張系の本実装

または Phase 4 系列を本 4-14 で完全終了し、TX shape は据え置きで JX へ移行という選択肢も。

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

### 5-8: part_b inventory 用一時ファイル群（Phase 4-14 完了で削除）

- **状態**: Phase 4-14 着手前の事前調査用一時ファイル群:
  - `_tmp_part_b_dump.py`（dump スクリプト）
  - `_tmp_part_b_variants/`（6 variants dump）
  - `_tmp_verify_render_part_b.py`（Commit 2 単体検証）
  - `_tmp_validate_content_all.py`（validate_content 一括実行）
- **処理**: Phase 4-14 完了に伴い本セッション内で **削除**（git に追加しない方針）

### 5-9: validate_content.py の 300.html 自動 quarantine 副作用

- **発生**: Phase 4-14 Commit 3 完了後の validate_content 全件実行で 300.html が
  自動的に `outputs/000_TX/001_刑法/_quarantine/刑TX300.html` を上書き
- **背景**: 300 は CP gate 上で DIFF=1 として意図的 baseline 差異が記録されており、
  Phase 4-4 由来の inject_ref_ids 後処理結果と JSON explanation prefix の不整合が
  validate_content の POSITIVE/EXPLANATION 検査で 5 件 FAIL する
- **対応**: 本セッション内で `git restore` により `_quarantine/刑TX300.html` の
  baseline コピーを復元、`outputs/000_TX/001_刑法/刑TX300.html` も CP gate 再 render で
  baseline hash に復元済
- **教訓**: validate_content.py は副作用としてファイル移動するため、Phase 4 系列の
  byte-identical 維持運用では **CP gate + check_template_sync + validate-tx の 3 件**
  を主要検証ゲートとし、validate_content は **個別ファイル単位**で扱う（一括実行は
  300 の意図的 DIFF を quarantine してしまうため非推奨）
- **将来課題**: BACKLOG §6 系列に「validate_content の 300 special-case 取扱い」を
  追加候補（300 は意図的 DIFF として除外する slot を持つよう改修、または quarantine
  動作の opt-out flag 追加）

---

## §6. セッション統計

| 項目 | 数値 |
|---|---|
| 本セッション通算 commits（Phase 4-14 + サマリ）| **3**（本最終サマリ commit 含めれば **4**） |
| Phase 4-14 のみの commits | **3**（render() 多段置換化が Phase 4-12 で完了済のため commit 増えず）|
| 14 protected ファイルの byte-identical 維持 | ✅ 全 commit |
| 300 (demo) の hash 変化 | Phase 4-14 では不変 |
| 全 15 件 validate-tx ERROR 0 / WARNING 0 | 維持 |
| templates 行数削減 | part_b 各 108〜174 行 → 1 行 = 約 **1,285 行削減** |
| templates bytes 削減 | **-44,116 bytes ≒ -44 KB**（本セッション 1 Phase で達成、Phase 4-7 -70 KB に次ぐ 2 位）|
| diff-allowed variants 集約 | **part_b: 6 → 1**（6 つ目の集約済領域、**diff-allowed 6 領域すべて完走**）|
| 確立パターン応用 | **E**（A+C + 局所 D・UI 種別 dispatch 不要、応用 2 例目）|
| render() 改修 | **なし**（Phase 4-12 多段置換を再利用）|
| remote push | `xnhsky/bar-exam` master = local HEAD（本サマリ commit 後に push 予定）|
| BACKLOG.md 行数推移 | 約 280（Phase 4-13 完了）→ 約 310（Phase 4-14 完了）|

---

**本セッション、Phase 4-14 完走。**
**パターン E (A+C + 局所 D) の応用 2 例目を part_b 領域で実現 = UI 種別 dispatch 不要**
**の最も単純な応用形（軸数 3 / 引数数 2 / 補助関数 1、Phase 4-12 part_a よりさらに単純）。**
**render() 改修不要（Phase 4-12 多段置換を再利用）→ 3 commit + docs 締め = 4 commits 完走。**
**diff-allowed 6 領域すべての slot 化が本 Phase で完走（toc / pre_part_a / basis /**
**part_a / a2 / part_b の 6 領域すべて 1 variant に集約完了）。**

remote `xnhsky/bar-exam` master に外部 backup 完了予定（4 commits 反映）。
templates 累計 **-44 KB 削減**（本セッション 1 Phase で達成、Phase 4 系列累計 -160 KB）。

次セッションは sync-required 2 領域（css / js）の集約、または Phase 5+ JX シリーズ着手が
候補。Phase 4 diff-allowed slot 化は本 Phase 4-14 で完全終了。
