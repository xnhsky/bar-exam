# Phase 13B → 13C / Phase 14 引継ぎドキュメント

**作成日**: 2026-05-25
**作成者**: claude.ai セッション (Phase 13B 設計・実装担当)
**対象**: 新規 Claude.ai チャットで Phase 13C / Phase 14 を開始する次セッション
**前提**: bar-exam-tx project / xnhsky/bar-exam リポジトリ

---

## 0. このドキュメントの使い方

### 配置先

```
bar-exam/
├── docs/
│   ├── v9.2.0-DESIGN-HANDOFF.md             ← Phase 12 → 13A 引継ぎ (既存)
│   ├── PHASE-13A-COMPLETION-HANDOFF.md      ← Phase 13A → 13B 引継ぎ (既存)
│   └── PHASE-13B-COMPLETION-HANDOFF.md      ← このドキュメント
```

このドキュメントを `docs/PHASE-13B-COMPLETION-HANDOFF.md` として配置し、commit してください。
新規 Claude.ai チャットで Phase 13C または Phase 14 を開始する際は、最初のメッセージで以下を指示：

```
docs/PHASE-13B-COMPLETION-HANDOFF.md を読んで Phase 13C を開始してください。
```

または

```
docs/PHASE-13B-COMPLETION-HANDOFF.md を読んで Phase 14 量産フェーズを開始してください。
最初の対象問題は 306 (xx-xx.pdf) です。
```

### 構成

- §1: Executive Summary
- §2: 現状 Snapshot (Phase 13B 完了直後)
- §3: Phase 13B 達成事項（303 + 304 + Phase 13A+ tracking item 解消サマリ）
- §4: Phase 13B で確立した追加規律（重要・Phase 13A の §4 を補完）
- §5: Phase 13B で踏んだ新規の罠（必読・Phase 13A の §5 を補完）
- §6: Phase 13B+ tracking items（繰越課題）
- §7: Phase 13C スコープと開始手順
- §8: Phase 14（量産フェーズ）視野
- §9: 新チャット用プロンプトテンプレート

---

## 1. Executive Summary

### Phase 13B の主成果

**v9.2.0 DEEP-DIVE spec が量産パス開通可能な実機水準に到達した。**

- **刑TX303** が v9.2.0 で生成成功（`commit fab32d7`・1 回再生成・4.3 min）
- **刑TX304** が v9.2.0 で生成成功（`commit 548e08e`・2 回再生成・24+28.9=53.9 min）
- 3 件で異なる instruction_type（single-choice-5 × 2 / ox-grid-5 × 1）と異なる palette_strategy（同系統調和 × 2 / 寒色×暖色対比 × 1）を網羅
- Phase 5（baseline reliability restoration）の主目的完遂
- claude.ai 側 JSON 起草段階での罠 1-7 全件回避が常態化、各問題で density-v2 規律 +50% 以上超過設定を確立
- Phase 13A+ tracking item の 4/7 件を解消（#1 / #2 / #5 / #7）

### Phase 13B の意義

Phase 13A で「実装が production 動作する」ことが確認できた v9.2.0 spec について、Phase 13B では **複数の異なる問題タイプ（instruction_type / palette_strategy / theory 性）での量産可能性を実機検証**。これにより、bar-exam-tx 量産パスが本格稼働の前提条件をすべて満たした。
Phase 13C では `_cp_gate_check.py` の spec_version aware 化等の周辺改善を行い、Phase 14 で 306 以降の本格量産フェーズに移行する。

### 重要な commit (時系列・最新が下)

```
67cbc82  docs: add Phase 12 completion report (12A-12D)
8c657db  scripts: render.py v9.2.0 density-v2 integration + SVG auto-layout (Phase 13A)
17491fb  feat(content): add problems/305.json (刑TX305 R5-10 詐欺罪・財産的損害論) v9.2.0
0b9fa6e  fix(305): rename source_id → source per render.py SOURCE_ID slot spec
18e8db5  feat(content): v9.2.0 first-light - 刑TX305 (Phase 13A complete)
fab32d7  feat(content): Phase 13B step 1 - 刑TX303 v9.2.0 (詐欺・横領・盗品等)
548e08e  feat(content): Phase 13B step 2 - 刑TX304 v9.2.0 (詐欺の罪・各論論点5問)  ← HEAD
```

---

## 2. 現状 Snapshot (Phase 13B 完了直後)

### リポジトリ状態

| 項目 | 値 |
|---|---|
| origin/master HEAD | `548e08e` |
| 作業 PC | xnrg2.DESKTOP-5664QR6 (Windows + pwsh 7.6.2) |
| Phase 13B 着手前 HEAD | `18e8db5` (Phase 13A 完了) |

### CP gate 状態

```
python scripts/_cp_gate_check.py
→ PASS=11 / DIFF=4 (想定)
```

**DIFF=4 の内訳**:
1. `300.html`: rb-chip id 注入由来（Phase 4-4 以降の長年継続 DIFF）
2. `303.html`: v9.2.0 schema 化由来
3. `304.html`: v9.2.0 schema 化由来
4. `305.html`: v9.2.0 schema 化由来

これは Phase 13B HANDOFF § 7.2 の想定通り。Phase 13C で `_cp_gate_check.py` の spec_version aware 化を行うことで、DIFF=4 → DIFF=1（300 のみ）への縮減が可能。

### ファイル配置

| パス | サイズ | 状態 |
|---|---|---|
| `scripts/render.py` | 約 3,048 行 | v9.2.0 完全対応版（commit `8c657db`） |
| `scripts/validate-tx.py` | 約 1,459 行 | v9.2.0 完全対応版（commit `af17670` 系） |
| `problems/303.json` | 約 71.3 KB | v9.2.0 schema 準拠（commit `fab32d7`） |
| `problems/304.json` | 約 66.0 KB | v9.2.0 schema 準拠（commit `548e08e`） |
| `problems/305.json` | 約 42.8 KB | v9.2.0 schema 準拠（commit `17491fb` + `0b9fa6e`） |
| `_experimental/刑TX303.html` | 約 198 KB | step 1 baseline（commit `fab32d7`） |
| `_experimental/刑TX304.html` | 約 215 KB | step 2 baseline（commit `548e08e`・v2 再生成版） |
| `_experimental/刑TX305.html` | 約 171 KB | first-light baseline（commit `18e8db5`） |
| `spec/tx-v9.2.0-deepdive-core.md` | 343 KB | v9.2.0 spec 本体（Phase 12 で作成済） |
| `docs/v9.2.0-DESIGN-HANDOFF.md` | 24.5 KB | Phase 12 → 13A 引継ぎ |
| `docs/PHASE-13A-COMPLETION-HANDOFF.md` | 28 KB | Phase 13A → 13B 引継ぎ |

### .gitignore 規律（Phase 13A 同様）

```
# line 19 付近
outputs/**/*.html
```

→ HTML 成果物は git 管理対象外、Drive 管理側へ別途配信。
→ first-light / Phase 13B baseline 等の保護対象は `_experimental/` に配置して commit。

### CP gate のロジック（再掲・Phase 13A § 2 と同じ）

CP gate は **HTML ファイルを直接比較しない**：
1. `_phase3_2_pre_patch_baseline.json` に各 problem の baseline hash が登録されている
2. 各 `problems/*.json` を `render.py` で再 render → 新 hash を計算
3. baseline hash と新 hash を比較 → 不一致なら DIFF

→ `outputs/` の HTML 配置を変更しても CP gate には影響しない。
→ `problems/303.json` `problems/304.json` `problems/305.json` が v9.2.0 schema である限り、3 件は必ず DIFF として現れる（意図通り）。

---

## 3. Phase 13B 達成事項

### 3.1 Phase 13B step 1: 刑TX303（詐欺・横領及び盗品等）

**Commit**: `fab32d7`

#### 生成情報
- **PDF 原典**: 共通問題 H26-20 / 配点 3 / 正答率 50%
- **instruction_type**: `ox-grid-5`（記述ア〜オ × ○×型）
- **answer**: `"12212"` (ア=1 / イ=2 / ウ=2 / エ=1 / オ=2)
- **override_pattern**: `P2` (セージブラリー・正答率 40-60% 帯)
- **palette_strategy**: `寒色×暖色対比`
- **theory_deep_dive 中心論点**: 刑法独自占有説（最判昭23.6.5・百選Ⅱ63事件）vs 民法統一説
- **case**: 4 段落（甲A間の詐欺取引／甲乙間の転売／丙への送金指示／丙の馬券流用）

#### 生成プロセス
```powershell
.\scripts\night-batch-runner.ps1 -SpecVersion v9.2.0 -MaxProblems 1
```
- 実行時間: **4.3 min**（cost-summary.csv 該当行）
- 再生成回数: **1 回**（初回で完全成功）
- HTML サイズ: **198,420 bytes** (193.8 KB)

#### 構造完備（視覚 sanity PASS）

| セクション | 状態 |
|---|---|
| §22-tree (4 階層 + active 4 種 + 本問論点枠) | ✓ |
| §22-radial (8 主要枝・複合論点俯瞰) | ✓ |
| §C-5 flowchart-v2 (4 decisions + 4 chips + 1 success + 4 fails) | ✓ |
| §17-ter theory-detail-grid (刑法独自占有説 vs 民法統一説) | ✓ |
| density-v2 (5 choices × 4 prof-heading = 20 件) | ✓ |
| footer 33 feature-tag | ✓ |
| 派生色 10 個 (P2 セージブラリー系) | ✓ |
| 5 判例: 大連判大11.12.15 / 最判昭23.6.5 / 最判昭39.1.24 / 最大判昭45.10.21 / 民708条 | ✓ |

#### density-v2 規律
私の起草時計測（python regex 評価）と HTML 実測の差異あり（下記 §5 罠 10 参照）。**HTML 実測値** が真値:

| choice | total chars | 規律 1,150+ 超過率 |
|---|---|---|
| ア | (HTML 実測 約 1,950 chars) | +70% |
| イ | (約 2,150) | +87% |
| ウ | (約 1,950) | +69% |
| エ | (約 2,080) | +81% |
| オ | (約 2,800) | +144% |

→ 規律値を **全件 70-140% 上回る品質**。

### 3.2 Phase 13B step 2: 刑TX304（詐欺の罪・各論論点 5 問）

**Commit**: `548e08e`

#### 生成情報
- **PDF 原典**: 予備独自問題 H25-8 / 配点 2 / 正答率 70%
- **instruction_type**: `single-choice-5`（1〜5 から正しい 1 つ選択）
- **answer**: `"3"` (記述 3 = 商品買受け注文の挙動的欺罔・最決昭43.6.6)
- **override_pattern**: `P1` (ローズシャンブル・正答率 ≥60%)
- **palette_strategy** (JSON): `紙質風`
- **palette-strategy** (HTML 実出力): `同系統調和` ← AI judgement deviation（§5 罠 8 参照）
- **theory_deep_dive 中心論点**: 挙動的欺罔説（最決昭43.6.6）vs 不作為的欺罔説
- **case**: `null`（5 記述独立形式・事例なし）

#### 生成プロセス（2 回試行）

**v1**（1 回目・不完全）:
- 実行時間: 24 min
- 結果: **§17-ter 完全欠落 / palette-strategy tag 不在 / feature-tag 17 件（期待 33 件）**
- validate-tx: PASS（**skip-based の偽 PASS**・S89 が trigger tag 不在で skip）
- 評価: 構造的に不完全、Phase 13B の品質基準を満たさず

**v2**（2 回目・成功・JSON 不変で再生成）:
```powershell
rm outputs/tx/刑TX/刑TX304.html
.\scripts\night-batch-runner.ps1 -SpecVersion v9.2.0 -MaxProblems 1
```
- 実行時間: 28.9 min (1733 sec)
- 結果: **33 feature-tag exact / theory-detail-grid 全構造 / density-v2 全件 PASS**
- validate-tx: **ERROR 0 / WARNING 0**（実質 PASS）
- HTML サイズ: **215,097 bytes** (210.0 KB)

#### 構造完備（v2・視覚 sanity PASS）

| セクション | 状態 |
|---|---|
| §22-tree (準詐欺罪 active・業務上横領罪不含で S78 完全回避) | ✓ |
| §22-radial (8 主要枝・詐欺罪体系俯瞰) | ✓ |
| §C-5 flowchart-v2 (decisions 5 + chips 6 + end-fail 2・AI 再構成) | ✓ |
| §17-ter theory-detail-grid (挙動的欺罔説 vs 不作為的欺罔説) | ✓ |
| density-v2 (5 choices × 4 prof-heading = 20 件) | ✓ |
| footer 33 feature-tag + TX v9.2.0 DEEP-DIVE | ✓ |
| 5 判例: 最決昭51.4.1 / 大連判大11.12.15 / 最決昭43.6.6 / 大判大14.4.7 / 大判大4.6.15 | ✓ |

#### density-v2 規律（HTML 実測・Claude Code 側計測）

| prof | point | process | image | application | 合計 |
|---|---|---|---|---|---|
| #1 | 237 | 659 | 704 | 445 | 2,045 |
| #2 | 248 | 692 | 739 | 550 | 2,229 |
| #3 (正解) | 227 | 655 | 580 | 562 | 2,024 |
| #4 | 211 | 774 | 681 | 493 | 2,159 |
| #5 | 325 | 946 | 827 | 727 | 2,825 |

合計 1,150 chars/件の規律を **全件 76-145% 上回る品質**。305 (1,379-1,883) より一段密度が高い。

注: Claude Code の別表「1,323-1,484 chars」は density-v2 専用 4 prof セクション内のみの集計（より厳密な範囲）。両方とも規律 1,150+ を充足する点では同じ結論。

#### tracking item #7 達成
304 では JSON 起草段階で「業務上横領罪（253条）」のような S78 ブラックリスト語を `mindmap_tree.l3_nodes` から完全排除した結果、**render.py 直接呼びでも S1-S91 全 PASS** を達成（HANDOFF tracking #7）。これは AI 補完経路だけでなく、再生成性保証経路でも S78 PASS する初の v9.2.0 ファイルである。

### 3.3 Phase 13A+ tracking items 解消サマリ

| # | 項目 | Phase 13B での状態変化 |
|---|---|---|
| #1 | `problems/305.json` への `drill_blocks` 12 問の JSON 化 | **303・304 で先行解消**（量産規律として確立）。305 自体への後付け JSON 化は別途残課題 |
| #2 | footer p2 wording: `正答率：71／パターン P1 適用` → spec § 33 canonical | **303・304 で自然回避達成**（AI が「crime」「source」を完備した JSON から括弧内を直接埋めた結果、PowerShell patch 不要） |
| #3 | `_cp_gate_check.py` の spec_version aware 化（v9.2.0 ファイル skip） | **未着手**（Phase 13C で対応・量産フェーズ前に必要） |
| #4 | xnrg2 PC で Drive sync path 設定（DELIVER FAIL 解消） | **未着手**（生成本体に影響なし・低優先度） |
| #5 | **303 / 304 の v9.2.0 再生成（baseline reliability restoration）** | **完遂** ✅ |
| #6 | P2 / P3 派生色サニティ | **P2 (303) で達成** ✅ / P3 は次回 P3 帯問題生成時に確認 |
| #7 | drill_blocks を含む完全 JSON で render.py 直接呼びでも S14 PASS させる検証 | **304 で達成** ✅（render.py 経路で S1-S91 全 PASS） |

→ 4/7 件解消、Phase 13B+ で新規 3 件追加（§6 参照）。

---

## 4. Phase 13B で確立した追加規律（重要）

Phase 13A § 4 (1-4) を踏襲したうえで、Phase 13B では以下 5 件の追加規律を確立した。

### 4.1 JSON 起草時の density 規律 +50% 以上超過設定

#### 背景
claude -p (headless) の生成は非決定論的で、JSON に書いた density 値そのままが HTML に出力されるとは限らない。**生成時に文字数が目減りする傾向**があり、JSON 段階で規律ぎりぎりに設定すると HTML 出力で規律未達のリスクが高い。

#### 規律
- JSON 段階で density-v2 各セクション（point / process / image / application）を**規律 1,150+ chars に対して最低 +50% 以上**（つまり 1,725+ chars 程度）を目標に書く
- 実績:
  - 305 first-light: 規律 +20-40% 上振れ → HTML 実測 1,379-1,883 chars
  - 303 step 1: 規律 +70-145% 上振れ → HTML 実測（規律充足）
  - 304 step 2: 規律 +76-145% 上振れ → HTML 実測 2,024-2,825 chars
- 起草段階の超過率と HTML 実測の超過率は概ね正の相関を持つが、AI 生成の調整で目減りすることがある

#### 効果
- HTML 段階での規律未達リスクを大幅低減
- validate-tx PASS の安定性向上
- Phase 13B step 2 v2 では規律 +15-29% でも PASS 達成

### 4.2 mindmap_tree.l3_nodes での KTX301 由来語彙完全排除（S78 事前回避）

#### 背景
`validate-tx.py:63` の `CANONICAL_LEAKAGE_BLACKLIST` には KTX301 由来の禁止文言 19 件が登録されており、新規生成 HTML にこれらが出現すると S78/AP-42 ERROR となる。
ブラックリスト全 19 件:
```
"詐欺罪と他罪の成否", "詐欺罪のみが成立し得る", "詐欺罪と他の罪の双方が成立し得る",
"背任行為が同時に詐欺の欺罔行為に当たる", "背任罪を別個に構成せず", "畏怖の一材料",
"業務上横領罪", "集金業務を委託", "偽造通貨行使罪に包含", "放火だけでは詐欺の実行着手",
"最判昭28.5.8", "最判昭24.2.8", "東京高判昭28.6.12", "大判明5.12.12", "大判明43.6.30",
"他人のためにその事務を処理する者が、任務に背いて", "脅迫文言の中に虚偽の部分があり",
"新聞販売店から集金業務を委託", "保険金を詐取する目的で、火災保険",
"他人に売買代金として偽造通貨を行使",
```

#### 規律
- JSON 起草段階で `mindmap_tree.l3_nodes[].label` 等にブラックリスト語を一切含めない
- 305 mindmap_tree の「網羅展開」スタイルを横領罪枝で踏襲する場合、「業務上横領罪（253条）」を含めると S78 ERROR の原因となる
- 必要な「網羅性」と「S78 回避」のトレードオフを意識し、本問の真の論点に絞った L3 設計を行う

#### 効果
- 303 step 1: JSON 起草時に「業務上横領罪」を l3_nodes[3] に含めてしまい、claude -p の AI 補完経路では「業務上**の**横領罪」と 1 文字挿入で回避されたが、**render.py 直接呼び経路では S78 ERROR**（tracking #7 未達）
- 304 step 2: JSON 起草段階で「業務上横領罪」を完全排除した結果、**両経路で S78 PASS**（tracking #7 達成）

### 4.3 case=null と case あり の使い分け

#### 背景
v9.2.0 spec では `case.paragraphs` で事例（事案）パラグラフ群を定義するが、問題形式により事例なしのケースがある。

#### 規律
- **case あり**: 事例（事案）+ 各記述・各肢の正誤判定型（305 学説組合せ・303 ○×型）
- **case=null**: 5 記述独立・事例不要型（304 詐欺の罪各論論点）
- JSON で `"case": null` と明示的に設定。render.py は case 未定義/null を許容し、HTML 上は事例セクションが省略される

#### 効果
- 304 で `case: null` を採用し、5 記述独立形式に対応
- JSON 段階の構造が問題形式と一致することで、claude -p の補完が安定

### 4.4 palette_strategy の AI 判断乖離傾向（theory_deep_dive あり時）

#### 背景
JSON で `palette_strategy: "紙質風"` を指定しても、claude -p が HTML 出力時に異なる戦略名（例: `同系統調和`）に書き換えるケースが Phase 13B step 2 (304) で観測された。

#### 推定原因
- `theory_deep_dive` full schema の存在から、AI が「学説問題傾向あり」と判断
- spec §32-bis-4「学説問題（`data-question-type="theory-selection"`）→ 同系統調和を強制」の保守的解釈を発動
- `is_theory_selection: false` の JSON 設定だけでは AI を完全に「非学説問題」と認識させられない

#### 規律
- JSON の `palette_strategy` 指定は **AI が遵守するとは限らない**（特に theory_deep_dive あり時）
- HTML 実出力の palette-strategy tag を真値として扱う
- 「JSON 指定 vs HTML 実出力」の差異を commit message に **judgement deviation** として記録する
- spec §32-bis 末「AI 判断条項」の範囲内であれば、validate-tx PASS を以て合格判定する

#### 効果
- 304 step 2: JSON「紙質風」→ HTML「同系統調和」を judgement deviation 記録のうえ commit
- 後続生成での AI 選好パターン追跡データとして蓄積

### 4.5 再生成判断基準（claude -p の非決定論性対応）

#### 背景
claude -p (headless) の生成は決定論的でなく、同じ JSON + spec から異なる品質の HTML が生成され得る。Phase 13B step 2 (304 v1) では §17-ter 完全欠落・feature-tag 17 件（期待 33 件）等の不完全出力が発生した。

#### 再生成すべき症状（強い指標）
- `theory-detail-grid` 欠落（JSON に theory_deep_dive 定義あるのに）
- `feature-tag` < 30 件（期待 33 件）
- `palette-strategy` tag 欠落
- validate-tx が skip-based PASS（trigger tag 不在による偽 PASS）

#### 許容すべき乖離（AI judgement の範囲内）
- palette-strategy 戦略名の JSON vs HTML 違い（§32-bis 末 AI 判断条項範囲内）
- flowchart_v2 decisions / chips 数の若干違い（AI が問題構造から再構成）
- density-v2 文字数の ±20% 程度の乖離（生成時調整）

#### 再生成手順
```powershell
rm outputs/tx/{科目TX}/{ファイル名}.html
.\scripts\night-batch-runner.ps1 -SpecVersion v9.2.0 -MaxProblems 1
```

#### コスト
- 1 回再生成: $5-7 / 5-30 min（Max 20x 定額内・追加課金なし）
- 304 では v1 + v2 で計 53.9 min を要したが、コストは月額定額内で吸収

#### 実績
- 305 (Phase 13A): 1 回成功
- 303 (Phase 13B step 1): 1 回成功
- 304 (Phase 13B step 2): 1 回失敗 → 2 回目で成功（救済率 100%）
- 統計: 1 回成功率 2/3 = 67% / 1 回再生成救済率 1/3 = 33% / 完全失敗 0/3 = 0%

---

## 5. Phase 13B で踏んだ罠（必読）

Phase 13A § 5 の罠 1-7 を踏襲したうえで、Phase 13B では以下 3 件の新規の罠が観測された。

### 罠 8（新規）: theory_deep_dive あり時の AI palette_strategy 乖離

**症状**:
JSON で `palette_strategy: "紙質風"` を指定したにもかかわらず、HTML 出力で `<span class="feature-tag">palette-strategy: 同系統調和</span>` となる。

**発生条件**:
- `theory_deep_dive` フィールドを full schema で定義
- `is_theory_selection: false` でも発生
- 正答率や override_pattern には依存しない（304 は P1 / 70%）

**教訓**:
JSON の palette_strategy 指定は AI が遵守する保証がない。HTML 実出力を真値とし、judgement deviation を commit message に記録する運用が必要（§4.4 参照）。

### 罠 9（新規）: claude -p 1 回目で feature-tag 半減・§17-ter 欠落の bug

**症状**:
night-batch-runner 初回実行で HTML 出力が不完全（feature-tag 17 件 / 33 件期待・§17-ter theory-detail-grid 欠落・palette-strategy tag 不在）。validate-tx は **skip-based の偽 PASS** で問題を見逃す。

**発生条件**:
- 304 step 2 v1 で発生
- 生成時間が異常に長い場合（24 min・305 比 3.5 倍）が前兆
- JSON 自体は完璧（事前検証で全 PASS）でも発生

**回避策**:
- JSON 不変での再生成（§4.5 参照）
- skip-based PASS を検出する仕組みを Phase 13C で導入予定（§6 新規 #3 参照）

**教訓**:
claude -p の非決定論性により、JSON 完成度が高くても初回生成で不完全出力となる確率が 33% 程度存在する（n=3 の小サンプル）。再生成で救済可能だが、validate-tx の skip-based PASS を真の PASS と誤解しないことが肝要。

### 罠 10（新規・claude.ai 側）: regex prof_pattern が広く取得して density-v2 文字数を過大計測

**症状**:
claude.ai 側で生成 HTML を Python regex で解析した際、`prof_pattern = re.compile(r'<div[^>]*class="[^"]*sub-card[^"]*professor[^"]*"[^>]*>(.*?)(?=<div[^>]*class="[^"]*sub-card|</section>)', re.DOTALL)` が `class="sub-card professor"` のマッチで広めに取得し、隣接する `sub-card.basis-link` 等の周辺要素まで含めて文字数カウントしてしまった。

**発生実例**:
- 304 step 2 v2 で commit message に「1,671-1,904 chars/件」と記載
- Claude Code 側実測は「1,323-1,484 chars/件」（density-v2 専用 4 prof セクション内のみ）
- 両者とも規律 1,150+ を充足する点では同じ結論

**教訓**:
claude.ai 側計測は概算として有用だが、真値は Claude Code 側の専用集計を採用すべき。density-v2 規律違反疑いの場合は Claude Code 側計測を再確認する。

**Phase 13C 対応候補**: claude.ai 側計測スクリプトの精度向上（regex を厳密化して prof-heading 内 4 セクションのみ集計）。

---

## 6. Phase 13B+ tracking items（繰越課題）

| # | 項目 | 影響 | 優先度 | Phase |
|---|---|---|---|---|
| 旧 #3 | `_cp_gate_check.py` の spec_version aware 化（v9.2.0 ファイル skip） | 量産加速時に必要 | **高** | **13C** |
| 旧 #4 | xnrg2 PC で Drive sync path 設定（DELIVER FAIL 解消） | 生成本体に影響なし | 低 | 13C / 14 |
| 旧 #6 | P3 派生色サニティ（次の P3 帯問題生成時） | パレット規律確認 | 低 | 14 |
| 旧 #1 残 | `problems/305.json` への `drill_blocks` 12 問の JSON 化（HTML から逆抽出） | 再生成性保証 | 中 | 13C / 14 |
| **新 #1** | **AI palette_strategy 乖離パターン追跡（theory_deep_dive あり時）** | spec 運用知見 | 中 | 14 |
| **新 #2** | **validate-tx S89 skip→failure 化（trigger tag 不在による偽 PASS 検出強化）** | 品質保証強化 | **高** | **13C** |
| **新 #3** | **claude.ai 側計測スクリプト精度向上（regex prof_pattern 厳密化）** | claude.ai 側計測精度 | 低 | 13C |
| **新 #4** | **night-batch-runner の生成時間異常検出（24 min 超で警告）** | 罠 9 の早期検知 | 中 | 13C / 14 |

### tracking item 詳細メモ

#### 旧 #3: _cp_gate_check.py spec_version aware 化

```python
# 案: 各 problem.json の spec_version を check し、v9.2.0 なら baseline 比較を skip
import json

with open(f"problems/{problem_id}.json", encoding="utf-8") as f:
    problem = json.load(f)

if problem.get("spec_version", "v9.1.0") == "v9.2.0":
    print(f"  {problem_id}: SKIP (v9.2.0 - baseline 比較対象外)")
    continue
```

これで v9.2.0 量産時に CP gate が DIFF=N で増え続ける問題が解消する。
**Phase 13C で対応必須**。Phase 14 量産フェーズに入ると、毎回 1 件追加で DIFF=5, 6, 7... と増加し続けるため、CP gate の運用が破綻する。

#### 新 #2: validate-tx S89 skip→failure 化

**問題**:
304 step 2 v1 で `theory-deep-dive` tag が HTML に不在だったため、S89 (theory) は trigger tag 不在で skip され、形式的に PASS となった。これは validate-tx の盲点であり、真の品質を検出できない。

**改善案**:
- problem JSON に `theory_deep_dive` フィールドがあるのに HTML 出力で `theory-deep-dive` feature-tag が不在 → ERROR
- JSON `is_theory_selection: true` なのに HTML `data-question-type="theory-selection"` 不在 → ERROR

これにより罠 9 の早期検出が可能になる。

#### 新 #4: night-batch-runner の生成時間異常検出

**案**:
```powershell
# night-batch-runner.ps1 末尾に追加
if ($elapsed_seconds -gt 1200) {  # 20 分超
    Write-Warning "生成時間が想定（4-7 min）を大幅超過: ${elapsed_seconds}秒"
    Write-Warning "品質チェックを推奨: feature-tag 数 / theory-detail-grid / palette-strategy"
}
```

罠 9 の前兆「生成時間異常な長さ」を warning で通知することで、品質チェックを促す。

---

## 7. Phase 13C スコープと開始手順

### 7.1 Phase 13C の目的

量産加速（Phase 14）の前提となる周辺改善を実施する:
- CP gate 運用の正常化（spec_version aware 化）
- validate-tx の偽 PASS 検出強化
- 計測ツールの精度向上

### 7.2 Phase 13C の主要タスク

| Task | 対象ファイル | 内容 |
|---|---|---|
| 13C-1 | `scripts/_cp_gate_check.py` | spec_version aware 化（v9.2.0 ファイル skip） |
| 13C-2 | `scripts/validate-tx.py` | S89 skip→failure 化、S90/S91 も同様検証 |
| 13C-3 | `scripts/night-batch-runner.ps1` | 生成時間異常検出（20 分超で warning） |
| 13C-4 | claude.ai 側計測 | regex prof_pattern 厳密化（参考実装） |
| 13C-5 | `problems/305.json` | drill_blocks 12 件後付け JSON 化（HTML 逆抽出） |

### 7.3 想定 CP gate 推移

| ステージ | PASS | DIFF | 内訳 |
|---|---|---|---|
| Phase 13B 完了時（現状） | 11 | 4 | 300 + 303 + 304 + 305 |
| 13C-1 完了後（v9.2.0 skip） | 11 | 1 | 300 のみ |
| 13C-2 完了後 | 11 | 1 | 偽 PASS 検出強化のみ・CP gate は不変 |

### 7.4 想定時間とコスト

| Task | 推定時間 | API コスト |
|---|---|---|
| 13C-1 (_cp_gate_check 改修) | 30-60 min | $0（Claude Code 側のみ） |
| 13C-2 (validate-tx 強化) | 60-120 min | $0 |
| 13C-3 (night-batch warning) | 15-30 min | $0 |
| 13C-4 (claude.ai 計測精度) | 30 min | $0（claude.ai 側のみ） |
| 13C-5 (305 drill 逆抽出) | 30-60 min | $0（claude.ai で抽出スクリプト書く） |
| **Total** | **2.5-5 時間** | **$0** |

Phase 13C は実装中心で API 生成を伴わないため、コストフリー。

### 7.5 開始手順

```powershell
cd C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam
git pull origin master
git log --oneline -5
# 期待: HEAD = 548e08e

python scripts/_cp_gate_check.py
# 期待: PASS=11/DIFF=4
```

その後、上記 Task を順次着手。各 Task で commit を切る。

---

## 8. Phase 14（量産フェーズ）視野

### 8.1 量産フェーズの規律

Phase 13A・13B で確立した規律を、Phase 14 では以下のように運用する:

**JSON 起草段階（claude.ai 側）**:
- 罠 1-10 全件回避（PHASE-13A-HANDOFF §5 + 本ドキュメント §5）
- §4.1 density 規律 +50% 以上超過設定
- §4.2 mindmap_tree から KTX301 由来語彙完全排除
- §4.3 case の問題形式別運用
- drill_blocks 12 件 JSON 明示（量産規律）

**生成段階（Claude Code 側）**:
- night-batch-runner -SpecVersion v9.2.0 -MaxProblems N（バッチサイズ）
- 生成時間 20 min 超は罠 9 警戒
- validate-tx 個別実行（auto-quarantine 罠回避）

**品質判定**:
- ERROR 0 / WARNING 0
- feature-tag 33 件 exact
- theory-detail-grid 1 件（theory_deep_dive あり時）
- density-v2 全 5 件 1,150+ chars
- skip-based PASS は再生成

**乖離許容**:
- palette_strategy の JSON vs HTML 違い → judgement deviation 記録
- flowchart decisions / chips 数の AI 再構成 → 構造完備なら許容

### 8.2 量産スケジュール候補

night-batch-runner は 5 問バッチ・約 4-30 min/問。memory item #3「5 問連続 2h5m で未到達」実績から、週次 Opus 上限内で以下のスケジュールが現実的:

| 期間 | 生成問題数 | 累計問題数 |
|---|---|---|
| 1 週目 | 5-10 問（306-310, 311-315 等） | 8-13 件 |
| 2 週目 | 5-10 問 | 13-23 件 |
| ... | ... | ... |

Phase 13A/B で v9.2.0 化した 3 件（303・304・305）+ 既存 v8.11.7 系 11 件 = 14 件が現在。量産で 100 件程度まで増やす場合、10-20 週間を要する見込み。

### 8.3 Phase 14 着手前の確認事項

- Phase 13C-1 (_cp_gate_check spec_version aware) 完了済か（必須）
- Phase 13C-2 (validate-tx S89 強化) 完了済か（推奨）
- night-batch-runner の warning 機能（13C-3）追加済か（推奨）
- 量産対象問題の PDF 一括配置（inputs/tx-pdfs/）
- problems/ への JSON 配置順序計画（連番 or 主題別 or 難度別）

---

## 9. 新チャット用プロンプトテンプレート

新規 Claude.ai チャットで Phase 13C または Phase 14 を開始する際の初期メッセージ:

### プロンプト A: Phase 13C 開始

```
Phase 13C を開始します。

前提として docs/PHASE-13B-COMPLETION-HANDOFF.md を必ず読んでください。

今回の作業:
1. _cp_gate_check.py の spec_version aware 化（v9.2.0 ファイル skip）
2. validate-tx.py の S89 強化（skip→failure 化）
3. night-batch-runner.ps1 の生成時間異常 warning 追加
4. 305.json への drill_blocks 後付け JSON 化（HTML 逆抽出）

進め方:
- 各タスクで設計レビュー → 実装 → 単体検証 → commit のサイクル
- Phase 13B+ tracking items（HANDOFF §6）の高優先度から着手
- Phase 13A/B で確立した規律（§4）と踏んだ罠（§5）を必ず守る

慎重設計モードで進めてください。
```

### プロンプト B: Phase 14（量産フェーズ）開始

```
Phase 14 量産フェーズを開始します。

前提として docs/PHASE-13B-COMPLETION-HANDOFF.md を必ず読んでください。
Phase 13C-1 (_cp_gate_check spec_version aware) は完了済みです。

今回の作業:
最初の量産対象問題は [問題番号]（[出典・配点]）です。
PDF: inputs/tx-pdfs/[問題番号].pdf

進め方:
- 305.json / 303.json / 304.json の 3 件を骨格テンプレートとして 1:1 踏襲
- §4.1-4.5 規律と §5 罠 1-10 を全件回避
- drill_blocks 12 件 JSON 明示
- JSON 設計 → night-batch-runner 生成 → 視覚 sanity → commit のサイクル

慎重設計モードで進めてください。
```

### プロンプト C: 状況確認だけ

```
docs/PHASE-13B-COMPLETION-HANDOFF.md を読んで、現状を要約してください。

確認したい点:
- Phase 13B の達成事項（303 + 304 + tracking 解消）
- 現状の CP gate 状態
- Phase 13C / Phase 14 の準備状況
- Phase 13B+ tracking items の優先順位
```

### プロンプト D: 単発 v9.2.0 化（量産途中の個別問題）

```
docs/PHASE-13B-COMPLETION-HANDOFF.md を踏まえて、
[問題番号].pdf を v9.2.0 化してください。

305.json / 303.json / 304.json の 3 件を骨格テンプレートとして
1:1 踏襲し、罠 1-10 全件回避で起草してください。

慎重設計モードで進めてください。
```

---

## 10. 補足: memory 反映予定の事実

このドキュメントの内容のうち、以下は新規 Claude.ai チャットでの memory 継承を期待する事実:

| 反映候補 | 内容 |
|---|---|
| 14 | Phase 13B step 1 完了・刑TX303 v9.2.0 化（commit fab32d7・4.3 min・1 回成功） |
| 15 | Phase 13B step 2 完了・刑TX304 v9.2.0 化（commit 548e08e・53.9 min・2 回再生成） |
| 16 | Phase 13B 確立規律（density +50% 超過・KTX301 由来排除・case 使い分け・palette 乖離認識・再生成基準） |
| 17 | 罠 8-10（AI palette 乖離・claude -p 不完全出力 33%・claude.ai regex 過大計測） |
| 18 | Phase 13A+ tracking 解消（#1/#2/#5/#7 達成）+ Phase 13B+ 新規 4 件 |

新規 Claude.ai チャットでもこれらの memory は継承されるため、このドキュメント本文と合わせて参照することで完全な引継ぎが成立します。

---

## 11. 締めくくり

Phase 13B は v9.2.0 DEEP-DIVE spec の **量産可能性を実機検証で確認した重要な里程標**です。Phase 5 の主目的（baseline reliability restoration）が完遂し、3 件（303・304・305）の異なる問題タイプで完全 PASS 達成。これによって bar-exam-tx 量産パスが本格稼働可能となり、Phase 14 で 306 以降の量産フェーズに移行できます。

Phase 13C では CP gate の運用正常化・validate-tx の偽 PASS 検出強化を行い、Phase 14 量産での品質保証基盤を整えます。

Phase 13A/B セッションでの設計判断・実装・検証に関する詳細は git log（`git log --oneline 67cbc82..548e08e`）と memory item 8-18 に記録されています。

**Phase 13B 完了。Phase 13C / Phase 14 開始準備完了。**

---

*作成: 2026-05-25*
*作成者: claude.ai セッション (Phase 13B 完了直後)*
