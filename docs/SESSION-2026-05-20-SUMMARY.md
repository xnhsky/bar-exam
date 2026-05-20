# Session 2026-05-20 — Phase 4-12 完走 + パターン E (A+C + 局所 D) 新規確立 + render() 多段化

> 本セッションで bar-exam TX 系 slot 化整備が Phase 4-11 完了状態から **Phase 4-12
> 完了状態**まで前進した。**1 Phase 完走、4 commits (BACKLOG / render_part_a /
> render() 多段化 / templates + 境界検出)**。Phase 4-12 は **5 パターン目「E」を
> 新規確立** = A+C dispatch + 局所 D 配列駆動の組合せという、A/B/C/D 単独でも
> A+C 組合せでも捕捉できない初めての形態。本セッションの戦略的成果。**templates
> 累計 -11,989 bytes 削減**（本セッション最大規模、Phase 4-7 -70 KB に次ぐ 2 位）。

---

## §1. 本セッション完了 Phase と commit 履歴

### Phase 4-12: part_a 領域 slot 化（**パターン E 新規確立**: A+C + 局所 D）

8 templates の diff-allowed `part_a` 領域 (8 variants / 19〜52 lines / avg
1,515 bytes、PART A の `<div class="part-title">` から `</section>` までの全範囲)
を `{{PART_A_FRAME}}` 単行に集約 slot 化。

5 つの可変軸を全て解析・分類:

| # | 軸 | dispatch 方式 | パターン |
|:-:|---|---|---|
| 1 | sec_nav_back（A-1 nav back-link） | dict 派生 | A+C |
| 2 | h3_title（記述 H3 見出し）| dict 派生 (【記述】/【空欄】/【選択肢】) | A+C |
| 3 | choice_lines（problem-text 件数）| 件数別関数生成 (3/4/5) | A+C |
| 4 | combo_section（【組合せ】section）| **件数別関数生成 (0/5/8)** | **局所 D** |
| 5 | middle_line（VIEWS_BLOCK 行）| 2 値分岐 (sc5 のみ in) | A+C |

→ **軸 4 のみ件数可変なため局所的に D（配列駆動）を併用**。これは A/B/C/D
いずれの単独パターンでも、A+C 組合せ (Phase 4-6/4-9/4-11) でも捕捉できない
初めての組合せ → **パターン E として新規確立**。

設計判断（BACKLOG §2-1）:
- schema 変更なし、JSON 改修なし（既存 problem.instruction_type 派生）
- 未対応 instruction_type で RuntimeError raise（Phase 4-6/4-9/4-11 同方針）
- broken intermediate state なし（diff-allowed 領域・旧 slot 不在）
- PART_A_FRAME_TEMPLATE は Python .format() 名前付き placeholder（6 引数）
- {{INSTRUCTION}} 等の slot 参照は {{{{INSTRUCTION}}}} 形式で .format() エスケープ

#### 補足 commit: render() 多段置換化（meta-slot サポート）

Phase 4-12 で初めて **meta-slot**（展開後に nested {{X}} を含む slot）が要求された
ため、`render()` を 1 pass の単発置換から多段置換に変更。1 pass の置換結果に対して
再び全 slot を適用し、収束まで繰り返す。

互換性保証:
- Phase 4-11 までのすべての slot 値は nested {{X}} を含まなかったため、1 pass で
  必ず収束 → 多段化しても結果は完全同一
- 全 15 件 byte-identical 維持を本 commit 完了時点で確認

安全ガード: MAX_PASSES=5 を超えても収束しない場合は循環参照と判断し RuntimeError
raise（実用上 PART_A_FRAME は 1 段なので 2 pass で必ず収束）。

#### byte-identical 検証点 4 つ全 PASS

| # | 検証点 | 結果 |
|:-:|---|---|
| 1 | `render_part_a()` 単体出力 == 各 template の literal part_a region | **8/8 一致** |
| 2 | 全 15 件 `validate-tx.py` ERROR/WARNING | **0/0 維持** |
| 3 | `_cp_gate_check.py` PASS/DIFF | **PASS=14 / DIFF=1 (300)** |
| 4 | `check_template_sync.py` part_a variants | **8 → 1 に集約** |

#### commit 履歴

| commit | 内容 |
|---|---|
| `eff2abd` | docs: BACKLOG.md §1 Phase 4-12 part_a 領域 slot 化 スコープ展開（パターン E 新規確立: A+C + 局所 D）|
| `e075d13` | feat(phase4-12 render): PART_A_FRAME_TEMPLATE + PART_A_AXES_BY_TYPE + render_part_a() + slot 供給配線（パターン E 新規確立）|
| `bc7cb10` | feat(phase4-12 render): render() を nested slot 対応の多段置換に変更（meta-slot サポート）|
| `b056102` | feat(phase4-12 templates): 8 templates の part_a 領域を {{PART_A_FRAME}} に置換 + check_template_sync 境界検出修正 |

### commit 戦略の意図的分割

当初計画は 3 commit（BACKLOG / render.py / templates）だったが、実装中に PART_A_FRAME
slot の nested {{X}} 解決が render() の単発置換で破綻することを発見。修正自体は
小さいが、フレームワーク層の根本変更であり templates 置換とは独立した話題のため、
**Commit 2.5 として独立 commit に切り出す**判断をユーザと合意。

| commit | 影響範囲 | ロールバック単位 |
|---|---|---|
| 1: BACKLOG | docs only | 設計記録のみ |
| 2: render_part_a | render.py（render_part_a 関数追加）| Phase 4-12 機能追加 |
| 2.5: 多段置換 | render.py（render() 関数本体）| **フレームワーク根本変更** |
| 3: templates | templates + upgrade script + check_template_sync | template 層 + 検出器 |

この分割により git log で「meta-slot 対応で render() を多段化」が独立した記録として
残り、万一問題があった時のロールバック単位を最小化。

### 本セッション通算 commit カウント

| 区分 | commits |
|---|---|
| Phase 4-12 (4 commits) | `eff2abd` / `e075d13` / `bc7cb10` / `b056102` |
| **本最終サマリ commit**（本ファイル + BACKLOG §0 P4-12 追記）| （今回追加、Phase 4-12 完走 SESSION 締め）|

Phase 4-12 のみ = **4 commits**、本最終サマリ更新込みで **5**。
remote `xnhsky/bar-exam` master への push は本サマリ commit 後に一括実施。

---

## §2. パターン E の構造化記述

### 2-1. パターン E の定義

> **A+C dispatch + 軸の一部だけ D（局所配列駆動）を併用** する組合せ。固定軸
> （dict 派生で完結する軸）と件数可変軸（D 配列駆動で必要な軸）が混在する
> diff-allowed 領域で初めて要求された新形態。

### 2-2. 既存 A/B/C/D と A+C との関係

| パターン | 特徴 | 例 |
|---|---|---|
| A | thin schema 派生 | 4-3 final_answer / 4-6 TOC |
| B | post-processing 注入 | 4-4 inject_ref_ids |
| C | universal const（純粋形 / .format() refined）| 4-5 marker_legend / 4-8/4-10 |
| D | 構造化レンダリング（配列駆動）| 3-3 basis / 4-7 drill_blocks |
| A + C | dispatch 関数で variant 解決 | 4-6 TOC / 4-9 pre_part_a / 4-11 basis_secnav |
| **E (新規)** | **A+C + 局所 D** | **4-12 part_a** |

### 2-3. パターン E の適用条件

- diff-allowed 領域の variants が多軸で構成される
- 一部の軸は dict 派生で固定値を取り得る（A+C 適用可能）
- 一部の軸のみ件数可変が必要（D 配列駆動が必要）
- A+C 単独でも D 単独でも全体を表現できない混在ケース

### 2-4. パターン E の実装テンプレ

```python
AREA_AXES_BY_TYPE: dict[str, dict] = {
    "type1": {"axis1": ..., "axis2": ..., "count_axis": 0, ...},
    ...
}

AREA_FRAME_TEMPLATE: str = (
    '... {axis1} ...\n'
    '{count_axis_value}'  # D 局所配列駆動の結果
    '...'
)

def _build_count_axis_value(n: int) -> str:
    if n == 0:
        return ""
    return ...  # 配列駆動レンダリング

def render_area(instruction_type: str) -> str:
    if instruction_type not in AREA_AXES_BY_TYPE:
        raise RuntimeError(...)
    axes = AREA_AXES_BY_TYPE[instruction_type]
    return AREA_FRAME_TEMPLATE.format(
        axis1=axes["axis1"],
        ...
        count_axis_value=_build_count_axis_value(axes["count_axis"]),
    )
```

### 2-5. パターン E の次の応用候補

| 候補 | 領域 | 件数可変軸の有無 | パターン E 適用見込 |
|---|---|---|---|
| **a2** (diff-allowed 8 variants) | A-2 解答エリア構造差 | ox-grid 件数 / option 件数 | **高**（複数軸で件数可変、E or D 寄り）|
| **part_b** (diff-allowed 6 variants) | PART B choice-section | choice 件数 + ラベル系列 | 中（A+C 寄りだが規模大、設計セッション要）|

→ パターン E は a2 領域への直接応用が次セッション最有力。

---

## §3. 検証最終状態

| 検証項目 | 結果 |
|---|---|
| **CP gate** (`scripts/_cp_gate_check.py`) | PASS=14 / DIFF=1 (300) / EXTRA=0 / MISS=0 |
| **check_template_sync** | sync-required 7 領域すべて 8 templates byte-identical／ diff-allowed `toc` / `pre_part_a` / `basis` / **`part_a`** はすべて **1 variant に集約済** |
| **validate-tx 全 15 件** | ERROR 0 / WARNING 0（Phase 4-4 で達成、Phase 4-5〜4-12 で維持） |
| **baseline** | `_phase3_2_pre_patch_baseline.json` 据え置き（Phase 4-12 も byte-identical 維持型 patch のため、`docs/cp-gate.md` §4 規定により baseline 更新不要） |
| **remote 反映** | `https://github.com/xnhsky/bar-exam.git` master = local HEAD (本セッション最終 commit)、本サマリ commit 含む 5 commits 反映予定 |

300 のみ DIFF=1 は意図的（Phase 3-3 basis 構造化 + Phase 4-3 final_answer +
Phase 4-4 anchor 注入 + 8th basis card 追加の累積結果）。Phase 4-12 は 300 含め
全 15 件 byte-identical で hash 不変。

### 集約状況サマリ（Phase 4-12 完了時点）

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
| ~~part_a~~ | **Phase 4-12 集約 (8 → 1 variant)** ← 本セッション最終成果（パターン E 新規確立）|
| a2 / part_b | **残**（パターン E の次の応用候補、a2 が最有力）|

---

## §4. 次セッション第 1 タスク候補

### 候補 A: a2 領域 slot 化（パターン E 応用 1 例目・最有力）

basis / part_a 集約完了で、残 diff-allowed は **a2 / part_b の 2 領域**に縮減。

- **a2** (8 variants, avg 1,643 bytes / 60 lines): A-2 解答エリア構造差
  （ox-grid 件数 / multi 件数 / single / fill-in / ox3comb8）。複数軸で件数可変
  のため **パターン E の直接応用** が見込まれる。設計コスト中（パターン E のロジックを
  応用、新規設計判断は軸の分解のみ）

### 候補 B: part_b 領域 slot 化（最大規模 diff-allowed）

- **part_b** (6 variants, avg 5,530 bytes / 174 lines): 最大規模 diff-allowed、
  A + D 組合せ可能性。設計セッション必要。a2 完了後に着手推奨

### 候補 C: 残 sync-required 2 領域（css / js）

- **css** sync 領域 (60,743 bytes / 1,997 lines)
- **js** sync 領域 (17,552 bytes / 405 lines)
- spec §Annex A/C と byte-level 同期で構造化困難、削減効果は大きいが構造化価値小

### 候補 D: Phase 5+ JX シリーズ着手

別仕様 (spec/jx-v3.2-master.md) 由来、別 Phase。1 問 1〜2 時間規模。

### 推奨順序

1. **A (Phase 4-13 a2)** を最初に消化（パターン E 応用、設計コスト中）
2. **B (Phase 4-14 part_b)** 着手（最大規模、設計セッション要）
3. **C (css/js)** 大規模一括集約（構造化価値小、規模大）
4. **D (Phase 5+ JX)** 別シリーズ着手

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

### 5-8: part_a_dump.txt（Phase 4-12 完了で削除）

- **状態**: Phase 4-12 着手前の事前調査用 part_a 領域 dump（256 行）
- **処理**: Phase 4-12 完了に伴い本セッション内で **削除**（コミット完了済、git
  に追加しない方針）

---

## §6. セッション統計

| 項目 | 数値 |
|---|---|
| 本セッション通算 commits（Phase 4-12 + サマリ）| **4**（本最終サマリ commit 含めれば **5**） |
| Phase 4-12 のみの commits | **4**（commit 戦略分割により 3 → 4 に増加）|
| 14 protected ファイルの byte-identical 維持 | ✅ 全 commit |
| 300 (demo) の hash 変化 | Phase 4-12 では不変 |
| 全 15 件 validate-tx ERROR 0 / WARNING 0 | 維持 |
| templates 行数削減 | part_a 各 19〜52 行 → 1 行 = 約 **140 行削減** |
| templates bytes 削減 | **-11,989 bytes ≒ -12 KB**（本セッション 1 Phase で達成、Phase 4-7 -70 KB に次ぐ 2 位）|
| diff-allowed variants 集約 | **part_a: 8 → 1**（4 つ目の集約済領域 = toc / pre_part_a / basis / part_a）|
| 新規確立パターン | **E**（A+C + 局所 D）|
| render() 改修 | 単発置換 → **多段置換**（meta-slot サポート、Phase 4-11 まで互換）|
| remote push | `xnhsky/bar-exam` master = local HEAD（本サマリ commit 後に push 予定）|
| BACKLOG.md 行数推移 | 約 230（Phase 4-11 完了）→ 約 250（Phase 4-12 完了）|

---

**本セッション、Phase 4-12 完走。**
**パターン E (A+C + 局所 D) 新規確立 = A/B/C/D 単独でも A+C 組合せでも捕捉できない**
**初の混在ケースを定型化、a2 領域への直接応用が次セッション最有力候補。**
**render() を meta-slot 対応の多段置換に変更（Phase 4-11 まで完全互換）。**

remote `xnhsky/bar-exam` master に外部 backup 完了予定（5 commits 反映）。
templates 累計 **-12 KB 削減**（本セッション 1 Phase で達成、累計 -103.5 KB）。

Phase 4-13 a2 領域 slot 化が次セッション最有力候補（パターン E 応用 1 例目）。
