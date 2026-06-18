# Phase 13A → 13B 引継ぎドキュメント

**作成日**: 2026-05-25
**作成者**: claude.ai セッション (Phase 13A 設計・実装担当)
**対象**: 新規 Claude.ai チャットで Phase 13B を開始する次セッション
**前提**: bar-exam-tx project / xnhsky/bar-exam リポジトリ

---

## 0. このドキュメントの使い方

### 配置先

```
bar-exam/
├── docs/
│   ├── v9.2.0-DESIGN-HANDOFF.md          ← Phase 12 → 13A 引継ぎ (既存)
│   └── PHASE-13A-COMPLETION-HANDOFF.md   ← このドキュメント
```

このドキュメントを `docs/PHASE-13A-COMPLETION-HANDOFF.md` として配置し、commit してください。
新規 Claude.ai チャットで Phase 13B を開始する際は、最初のメッセージで以下を指示：

```
docs/PHASE-13A-COMPLETION-HANDOFF.md を読んで Phase 13B を開始してください。
今回の作業対象は 303.html と 304.html の v9.2.0 再生成です。
```

### 構成

- §1: Executive Summary
- §2: 現状 Snapshot (Phase 13A 完了直後)
- §3: Phase 13A 達成事項
- §4: Phase 13A で確立した規律（重要）
- §5: Phase 13A で踏んだ罠（必読）
- §6: Phase 13A+ tracking items（繰越課題）
- §7: Phase 13B スコープと開始手順
- §8: 新チャット用プロンプトテンプレート

---

## 1. Executive Summary

### Phase 13A の主成果

**v9.2.0 DEEP-DIVE spec が production 動作する実装に到達した。**

- 刑TX305 が **v9.2.0 で初の実生成成功** (`commit 18e8db5`)
- claude -p (headless) で **6.87 min/問** (想定 25-30 min の 1/4)
- validate-tx **S1-S91 全 PASS** (ERROR 0 / WARNING 0)
- v9.1.0 baseline 6 件 **byte-identical 維持** (PASS=14/DIFF=1 patch 単独)
- render.py 拡張: **+270 行** (density-v2 統合 + SVG auto-layout 3 関数)

### Phase 13A の意義

Phase 12 の v9.2.0 spec 設計から Phase 13A の実機検証へ、理論 → 実装の橋渡しが完了。**これで v9.2.0 化問題の量産パスが開通**。Phase 13B では 303/304 の v9.2.0 再生成を行い、Phase 5（baseline reliability restoration）の主目的を完遂する。

### 重要な commit (時系列・最新が下)

```
67cbc82  docs: add Phase 12 completion report (12A-12D)
8c657db  scripts: render.py v9.2.0 density-v2 integration + SVG auto-layout (Phase 13A)
17491fb  feat(content): add problems/305.json (刑TX305 R5-10 詐欺罪・財産的損害論) v9.2.0
0b9fa6e  fix(305): rename source_id → source per render.py SOURCE_ID slot spec
18e8db5  feat(content): v9.2.0 first-light - 刑TX305 (Phase 13A complete)  ← HEAD
```

---

## 2. 現状 Snapshot (Phase 13A 完了直後)

### リポジトリ状態

| 項目 | 値 |
|---|---|
| origin/master HEAD | `18e8db5` |
| 作業 PC | xnrg2.DESKTOP-5664QR6 (Windows + pwsh 7.6.2) |
| Phase 13A 着手前 HEAD | `67cbc82` (Phase 12 完了) |

### CP gate 状態

```
python scripts/_cp_gate_check.py
→ PASS=13 / DIFF=2
```

**DIFF=2 の内訳**:
1. `300.html`: rb-chip id 注入由来 (Phase 4-4 以降の長年継続 DIFF)
2. `305.html`: v9.2.0 schema 化由来 (mindmap-tree / theory-deep-dive 等が render に追加されたため)

これは **Phase 13B § 23 の想定通り**: 「303/304/305 が DIFF 側へ・baseline 更新として受容」。

Phase 13B で 303 / 304 を v9.2.0 化すれば PASS=11/DIFF=4 が想定される。

### ファイル配置

| パス | サイズ | 状態 |
|---|---|---|
| `scripts/render.py` | 約 3,048 行 | v9.2.0 完全対応版（commit 8c657db） |
| `problems/305.json` | 42.8 KB | v9.2.0 schema 準拠（commit 17491fb + 0b9fa6e） |
| `_experimental/刑TX305.html` | 171,315 bytes (3,399 行) | first-light baseline（commit 18e8db5） |
| `outputs/000_TX/001_刑法/刑TX305.html` | 171,315 bytes | Drive 管理側配信用（.gitignore 除外） |
| `spec/tx-v9.2.0-deepdive-core.md` | 343 KB | v9.2.0 spec 本体（Phase 12 で作成済） |
| `docs/v9.2.0-DESIGN-HANDOFF.md` | 24.5 KB | Phase 12 → 13A 引継ぎ（既存） |

### .gitignore 規律（重要）

```
# line 19 付近
outputs/**/*.html
```

→ HTML 成果物は git 管理対象外、Drive 管理側へ別途配信。
→ first-light baseline 等の保護対象は `_experimental/` に配置して commit。

### CP gate のロジック（明文化）

CP gate は **HTML ファイルを直接比較しない**：
1. `_phase3_2_pre_patch_baseline.json` に各 problem の baseline hash が登録されている
2. 各 `problems/*.json` を `render.py` で再 render → 新 hash を計算
3. baseline hash と新 hash を比較 → 不一致なら DIFF

→ `outputs/` の HTML 配置を変更しても CP gate には影響しない。
→ `problems/305.json` が v9.2.0 schema である限り、305 は必ず DIFF として現れる（意図通り）。

---

## 3. Phase 13A 達成事項

### 3.1 render.py 拡張 (commit 8c657db, +277/-7 行 net +270)

#### (A) density-v2 統合

`build_slot_dict()` の choices ループ内 professor 処理に分岐を追加：

```python
# 旧（v9.1.0 only）
slots[f"{prefix}_PROFESSOR_SUMMARY"] = str(professor.get("summary", ""))
slots[f"{prefix}_PROFESSOR_NOTE"] = str(professor.get("note", ""))

# 新（v9.2.0 対応）
if spec_version == "v9.2.0" and professor.get("point"):
    slots[f"{prefix}_PROFESSOR_SUMMARY"] = render_professor_density_v2(professor)
    slots[f"{prefix}_PROFESSOR_NOTE"] = ""
else:
    # 既存挙動を維持（v9.1.0 baseline byte-identical）
    slots[f"{prefix}_PROFESSOR_SUMMARY"] = str(professor.get("summary", ""))
    slots[f"{prefix}_PROFESSOR_NOTE"] = str(professor.get("note", ""))
```

#### (B) SVG auto-layout 3 関数 (約 160 行追加)

`render_mindmap_tree` の直前に挿入：
- `auto_layout_tree()`: parent_idx から階層 y 座標自動算出・接続線自動生成
- `auto_layout_radial()`: V92_RADIAL_BRANCH_POSITIONS から branch 座標・sub_nodes 接線分散
- `auto_layout_flowchart()`: decisions cy 自動算出・chip / end_success / end_fails 補完

座標が JSON に明示されていれば既存挙動維持（後方互換）。JSON が「意味データのみ」で動作可能に。

#### (C) render_flowchart_v2 終端ノード動的化

固定文字列 "成立" / "不成立" を `end_success_label` / `end_fail_labels[i]` から動的取得に変更。

### 3.2 problems/305.json 配置 (commit 17491fb + 0b9fa6e, 42.8 KB)

v9.2.0 拡張スキーマ準拠の最初の問題 JSON。構造：

```
{
  "id": "305", "subject": "KEI", "exam": "司法試験", "year": "R5",
  "page": "789", "source": "共通R5-10", "crime": "詐欺罪",
  "points": "2", "correct_rate": "71",
  "instruction": "...", "instruction_type": "single-choice-5",
  "answer": "3", "answer_explanation": "...",
  "override_pattern": "P1",
  "spec_version": "v9.2.0",         ← v9.2.0 専用
  "palette_strategy": "同系統調和",  ← v9.2.0 専用
  "case": { "paragraphs": [...4段落...] },
  "choices": [ 5 件 × density-v2 構造 ],
  "mindmap_tree": { ... 4 階層 + 本問論点 },
  "mindmap_radial": { ... 7 主要枝 + 論点枝 },
  "flowchart_v2": { ... 4 decisions + 4 chips + 4 end_fails },
  "theory_deep_dive": { ... major + minor + statute }
}
```

choices の professor は density-v2 構造：
```json
"professor": {
  "point": {"list": [...], "locus": "..."},          // 150+ chars
  "process": {"steps": [...]},                        // 400+ chars
  "image": {"scene": "...", "bridge": "...", "contrast": "..."},  // 300+ chars
  "application": {"major": "...", "minor": "...", "conclusion": "..."}  // 300+ chars
}
```

### 3.3 刑TX305.html first-light (commit 18e8db5, 171,315 bytes / 3,399 行)

#### 生成プロセス

```powershell
.\scripts\night-batch-runner.ps1 -SpecVersion v9.2.0 -MaxProblems 1
```

- 実行時間: **6.87 min** (cost-summary.csv `2026-05-25 13:19:21,刑TX305,412,171315,COMPLETED,0,True,PASS`)
- 想定 25-30 min の **1/4 に短縮** ← claude.ai 側で JSON + spec を高完成度で渡したため AI 補完負荷が激減

#### 構造完備（視覚 sanity PASS）

| セクション | 状態 |
|---|---|
| §22-tree (4 階層 + active L3 + 本問論点枠 + 破線矢印) | ✓ viewBox `0 0 1100 600` |
| §22-radial (中央楕円 + 主要枝 7 + 論点枝 1 + sub-nodes 17) | ✓ viewBox `0 0 1200 1000` |
| §C-5 flowchart-v2 (4 decisions + 4 chips + 1 success + 4 fails) | ✓ viewBox `0 0 900 800` |
| §17-ter theory-detail-grid (major/minor + statute) | ✓ |
| density-v2 (5 choices × 4 prof-heading = 20 件) | ✓ 1379-1883 chars/件 |
| footer 33 feature-tag | ✓ `TX v9.2.0 DEEP-DIVE` + `palette-strategy: 同系統調和` |
| 派生色 10 個 (P1 ローズシャンブル系) | ✓ `--accent-light #a83553` ほか |
| 旧 stepbox / 旧 #mindmap section | ✓ 不残存（完全置換） |

#### density-v2 規律（実測値）

| choice | point ≥150 | process ≥400 | image ≥300 | application ≥300 | total ≥1150 |
|---|---|---|---|---|---|
| 1 | 230 ✓ | 415 ✓ | 432 ✓ | 395 ✓ | 1,472 ✓ |
| 2 | 207 ✓ | 424 ✓ | 442 ✓ | 389 ✓ | 1,462 ✓ |
| **3 正解** | 298 ✓ | 535 ✓ | 560 ✓ | 490 ✓ | **1,883 ✓** |
| 4 | 217 ✓ | 417 ✓ | 372 ✓ | 373 ✓ | 1,379 ✓ |
| 5 | 207 ✓ | 477 ✓ | 395 ✓ | 349 ✓ | 1,428 ✓ |

→ 規律値を **全件 20-40% 上回る品質**。

---

## 4. Phase 13A で確立した規律（重要）

### 4.1 既存 render.py 規約準拠（最重要）

**v9.2.0 schema 設計時は spec docs だけでは不足。render.py の定数 dict と slot 注入パターンが authoritative source**。

#### subject フィールド

```python
# render.py:41-49
SUBJECT_TO_JP: dict[str, str] = {
    "KEI": "刑", "KEN": "憲", "MIN": "民", "SYO": "商",
    "MINS": "民訴", "KEIS": "刑訴", "GSE": "行政",
}
```

→ JSON: `"subject": "KEI"` (short code), NOT `"刑法"` / `"刑"` / その他。

#### id フィールド

```python
# render.py の CLI 引数解決
# "326" → problems/326.json (KEI 既定・3 桁ゼロパッド)
# "KEN001" → problems/KEN001.json (科目接頭辞 + 3 桁)
```

→ JSON: `"id": "305"` (数字 3 桁), NOT `"刑TX305"` / `"305 詐欺罪"` 等。

#### instruction_type フィールド

```python
# render.py:1843, TEMPLATES dict
{
  "single-choice-5":   ["1", "2", "3", "4", "5"],
  "combination-5":     ["ア", "イ", "ウ", "エ", "オ"],
  "multi-select-5":    [...],
  "ox-grid-5":         [...],
  "ox-grid-4":         [...],
  "ox-grid-3-combination-8": [...],
  "fillin8":           [...],
  "fill-in":           [...],
}
```

→ 305 のような「肢を 1〜5 から選ぶ・各肢が組合せ語句」型 → `"single-choice-5"` が正解。NOT `"single-5"` / `"combination-5"` (= ア〜オ 用)。

#### source フィールド

```python
# render.py:1300-1320 付近
'<title>{jp_prefix}{problem_id} - {crime}（{source_id}）</title>'
slots["SOURCE_ID"] = str(problem.get("source", ""))  ← source を読む
```

→ JSON: `"source": "共通R5-10"`, NOT `"source_id"` (これは render.py が無視するフィールド名)。

#### 検証手順（必須）

```bash
# v9.2.0 schema 設計時は必ず実行
grep -n 'slots\[f"{prefix}_.*" \?= \?str(problem\.get(' scripts/render.py
grep -n 'SUBJECT_TO_JP\b\|SUBJECT_TO_LABEL\b\|TEMPLATES\b' scripts/render.py
```

これで JSON が満たすべき field のフルリストが取得できる。**spec docs を読むだけでは見落としが発生する**（Phase 13A の罠）。

### 4.2 night-batch-runner と render.py の挙動差

| 観点 | night-batch-runner | render.py 直接呼び |
|---|---|---|
| 実体 | claude -p (headless) が JSON + spec から HTML を生成 | render.py が JSON フィールドを slot に注入 |
| 補完能力 | AI が drill 12 問・answer_explanation 等を spec 通りに自動補完 | 補完なし。JSON にない field は空欄 |
| 実行時間 | 6.87 min - 30 min | 秒単位 |
| 想定用途 | 新規問題の本生成 | パッチ適用後の再 render・ハッシュ確認 |
| 必要 JSON 完備度 | 中程度（中心 content があれば AI が膨らませる） | 高（全 field が必要） |

**重要**: 305.json で `drill_blocks` を省略しても night-batch-runner では drill 12 問が完備された HTML が出力された。しかし render.py 直接呼びでは drill 不在で S14 ERROR が発生する。

→ **再生成性を保証するには `drill_blocks` も JSON に書くべき**（Phase 13A+ tracking item #1）。

### 4.3 .gitignore と _experimental/ の運用

```
# .gitignore line 19
outputs/**/*.html
```

| ディレクトリ | 用途 | git 管理 |
|---|---|---|
| `outputs/000_TX/{科目TX}/` | 通常生成 HTML（Drive 配信用） | 除外 |
| `_experimental/` | first-light baseline・要保護成果物 | commit 対象 |
| `_quarantine/` | validate 失敗時の隔離（自動移動） | commit 対象 |

→ v9.2.0 first-light 等の重要 HTML は `_experimental/` に明示配置して commit する。
→ outputs/ にも同じ HTML を置くのは Drive 側配信を見据えた運用（commit には影響しない）。

### 4.4 type-driven over data-driven の戒め（既存規律の再確認）

`choice.image.contrast` を Python tuple `(string,)` で書いたまま JSON 化したため、HTML レンダリング時に list として処理されて TypeError が発生（Phase 13A 序盤）。

→ **JSON フィールドは型を意識して書く**。string が期待される場所に list/tuple が混入していないか確認するために、生成スクリプトに最終 type check を入れるのが推奨。

---

## 5. Phase 13A で踏んだ罠（必読）

### 罠 1: subject に日本語ラベルを書いた

```diff
- "subject": "刑法",          ← 誤り（SUBJECT_TO_LABEL の value）
+ "subject": "KEI",           ← 正解（SUBJECT_TO_JP の key）
```

**症状**: CP gate が `RuntimeError: unknown subject '刑法'` でクラッシュ。

**教訓**: render.py の定数 dict の key と value の区別。JSON は **key** を書く。

### 罠 2: id に jp_prefix を含めた

```diff
- "id": "刑TX305",
+ "id": "305",
```

**症状**: JP_PREFIX + PROBLEM_ID で `刑TX刑TX305` のような二重連結が発生する設計のため不整合。

**教訓**: id は数字 3 桁。`jp_prefix` は render.py が自動導出する。

### 罠 3: instruction_type に独自値

```diff
- "instruction_type": "single-5",
+ "instruction_type": "single-choice-5",
```

**症状**: `RuntimeError: unknown instruction_type 'single-5' for TOC. valid: [...]`

**教訓**: TEMPLATES dict / PART_B_AXES_BY_TYPE の key を必ず確認。

### 罠 4: source_id という field 名を発明

```diff
- "source_id": "共通R5-10",
+ "source": "共通R5-10",
```

**症状**: render.py は `problem.get("source", "")` を `SOURCE_ID` slot に注入するため、`source_id` 名は無視されて title/h1/footer の括弧が空欄に。

**教訓**: slot 名 `_SOURCE_ID` から field 名 `source_id` を逆推測したが、実際は field `source` → slot `SOURCE_ID` という変換。slot 注入パターンを直接 grep して確認すべき。

### 罠 5: drill_blocks 完全省略

**症状**: claude -p 生成では AI が補完して drill 12 問完備の HTML が出力。しかし render.py 直接呼びでは drill 不在で `S14 ERROR`（drill-block 存在しない）。

**教訓**: night-batch-runner と render.py の挙動差を認識。再生成性保証のため、drill_blocks も JSON に明示するのが推奨。

### 罠 6: tuple/list 混入

```python
prof_image_contrast=(
    "テキスト1"
    "テキスト2",   ← 末尾コンマで tuple 化！
),
```

**症状**: JSON 化されると list（`["テキスト1テキスト2"]`）になり、render.py が `html.escape()` で `AttributeError: 'list' object has no attribute 'replace'`。

**教訓**: パラ括弧（"...") とコンマの組合せに注意。Python の暗黙の string concatenation と tuple 化の境界を意識。

### 罠 7: 改行コード差異による大幅 git diff

`json.dump(... newline="\n")` で出力後、Windows side で改行コードが変換されると `git diff` が「576 insertions / 490 deletions」のような大量 diff になる。

**教訓**: `.gitattributes` または `core.autocrlf false` を確認。Phase 13A では memory item #4 にある PowerShell 規律で対応済。

---

## 6. Phase 13A+ tracking items（繰越課題）

| # | 項目 | 影響 | 優先度 | Phase |
|---|---|---|---|---|
| 1 | `problems/305.json` への `drill_blocks` 12 問の JSON 化 | 再生成性保証 | 中 | 13A+ |
| 2 | footer p2 wording: `正答率：71／パターン P1 適用` → spec § 33 canonical `正答率：[N]%／パターン [P1\|P2\|P3]「[名称]」適用` | template/render.py 改修 | 中 | 13A+ |
| 3 | `_cp_gate_check.py` の spec_version aware 化（v9.2.0 ファイル skip） | v9.2.0+ 量産時に必要 | 低 | 13A+ |
| 4 | xnrg2 PC で Drive sync path 設定（DELIVER FAIL 解消） | 生成本体に影響なし | 低 | 13A+ |
| 5 | **303 / 304 の v9.2.0 再生成（baseline reliability restoration）** | Phase 5 主目的 | **高** | **13B** |
| 6 | P2 / P3 派生色サニティ（次の P2 帯・P3 帯問題生成時） | パレット規律確認 | 低 | 13B 以降 |
| 7 | drill_blocks を含む完全 JSON で render.py 直接呼びでも S14 PASS させる検証 | 設計健全性 | 低 | 13C |

### tracking item 詳細メモ

#### #1: drill_blocks JSON 化

claude -p 生成 HTML から逆抽出する。BeautifulSoup で `.drill-block` 12 個を抽出し、各 drill の `stem` / `correct` / `explanation` 構造を JSON 化。Phase 13B で 303/304 を生成する際は drill_blocks も明示するのが推奨。

#### #2: footer p2 wording

```
現状: 正答率：71／パターン P1 適用
spec: 正答率：[N]%／パターン [P1|P2|P3]「[名称]」適用
```

- `%` 欠落
- パターン名（ローズシャンブル / セージブラリー / ラベンダードーン）欠落

調査範囲:
- `templates/KTX_template_sc5.html`（および各 template）の footer-spec 該当行
- `render.py` の `CORRECT_RATE` / `OVERRIDE_PATTERN_NAME` slot 生成箇所
- `spec/tx-v9.2.0-deepdive-core.md` § 33 canonical

#### #3: _cp_gate_check.py spec_version aware 化

```python
# 案: 各 problem.json の spec_version を check し、v9.2.0 なら baseline 比較を skip
if problem.get("spec_version", "v9.1.0") == "v9.2.0":
    continue
```

これで v9.2.0+ 量産時に CP gate が DIFF=N で増え続ける問題が解消する。

---

## 7. Phase 13B スコープと開始手順

### 7.1 Phase 13B の目的

Phase 5（baseline reliability restoration）の主目的を完遂：
- **303.html** の v9.2.0 再生成
- **304.html** の v9.2.0 再生成

これら 2 件は現在 v8.11.7 系の baseline HTML だが、Phase 5 pre-design findings によれば「source PDF との内容乖離あり」が指摘されている（memory recent_updates より）。v9.2.0 で再生成することで内容精度も向上する。

### 7.2 想定される CP gate 推移

| ステージ | PASS | DIFF | 内訳 |
|---|---|---|---|
| Phase 13A 完了時（現状） | 13 | 2 | 300 既存 + 305 v9.2.0 |
| 303 v9.2.0 化後 | 12 | 3 | 300 + 305 + 303 |
| 304 v9.2.0 化後 | 11 | 4 | 300 + 305 + 303 + 304 |
| Phase 13C（_cp_gate_check spec_version aware 化後） | 11 | 1 | 300 のみ |

### 7.3 必要 inputs

| ファイル | 用途 | 配置先 |
|---|---|---|
| `inputs/tx-pdfs/303.pdf` | 303 の元 PDF | 要事前配置 |
| `inputs/tx-pdfs/304.pdf` | 304 の元 PDF | 要事前配置 |

### 7.4 開始手順（推奨）

#### Step 1: 環境確認

```powershell
cd C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam
git pull origin master
git log --oneline -5
# 期待: HEAD = 18e8db5

python scripts/_cp_gate_check.py
# 期待: PASS=13/DIFF=2

ls inputs/tx-pdfs/30*.pdf
# 期待: 303.pdf, 304.pdf, 305.pdf (305 は既処理)
```

#### Step 2: 303 から先に着手

理由: Phase 13A で 305 を完了済 → 連番で 303 → 304 の順が運用安全。

```powershell
# 303.pdf を claude.ai に upload
# claude.ai 側で:
#   1. 303 のスキーマ + content を Phase 13A の規律で設計
#   2. problems/303.json を生成（drill_blocks も含めることを推奨・tracking #1）
#   3. xnrg2 PC に download → problems/303.json として配置
# Claude Code 側で:
#   1. validate JSON structure
#   2. night-batch-runner で生成
#   3. validate-tx
#   4. _experimental/ に配置 + commit
```

#### Step 3: 304 も同様に

```powershell
# 同じ手順を 304 で繰り返す
```

#### Step 4: Phase 13B 完了 commit

```powershell
git add _experimental/刑TX303.html _experimental/刑TX304.html
git add problems/303.json problems/304.json
git commit -m "feat(content): Phase 13B - 刑TX303/304 v9.2.0 baseline reliability restoration"

git push origin master
```

### 7.5 想定時間とコスト

| 工程 | 推定時間 | API コスト |
|---|---|---|
| 303 JSON 設計（claude.ai） | 30-60 min | $0 (Max 20x) |
| 303 生成（night-batch-runner） | 7-30 min | $5-7 |
| 303 視覚 sanity | 5-10 min | $0 |
| 304 JSON 設計 | 30-60 min | $0 |
| 304 生成 | 7-30 min | $5-7 |
| 304 視覚 sanity | 5-10 min | $0 |
| **Total** | **1.5-3.5 時間** | **$10-14** |

レートリミット余裕（memory item #3）: 5 問連続 2h5m で未到達確認済 → 2 問は十分余裕。

---

## 8. 新チャット用プロンプトテンプレート

新規 Claude.ai チャットで Phase 13B を開始する際の初期メッセージ：

### プロンプト A: Phase 13B 開始

```
Phase 13B を開始します。

前提として docs/PHASE-13A-COMPLETION-HANDOFF.md を必ず読んでください。

今回の作業:
1. 刑TX303.html を v9.2.0 で再生成
2. 刑TX304.html を v9.2.0 で再生成

進め方:
- 303 から先に着手
- 各問題で JSON 設計 → night-batch-runner 生成 → 視覚 sanity → commit のサイクル
- Phase 13A で確立した規律（§4）と踏んだ罠（§5）を必ず守る
- drill_blocks を JSON に明示することで再生成性を保証（tracking item #1）

慎重設計モードで進めてください。
```

### プロンプト B: tracking item を先に処理する場合

```
Phase 13A+ tracking item の以下を先に処理してから Phase 13B に進みます：

[該当する項目を指定]
- #1: drill_blocks の 305.json 化（claude -p 生成 HTML から逆抽出）
- #2: footer p2 wording 修正（template/render.py 改修）
- #3: _cp_gate_check.py の spec_version aware 化

docs/PHASE-13A-COMPLETION-HANDOFF.md § 6 を参照してください。
```

### プロンプト C: 状況確認だけ

```
docs/PHASE-13A-COMPLETION-HANDOFF.md を読んで、現状を要約してください。

確認したい点:
- Phase 13A の達成事項
- 現状の CP gate 状態
- Phase 13B の準備状況
- Phase 13A+ tracking items の優先順位
```

---

## 9. 補足: memory 反映済の事実

このドキュメントの内容は以下の memory item に既に反映されています：

| item # | 内容 |
|---|---|
| 8 | Phase 13A first-light 達成・生成 6.87 min・density-v2 規律 20-40% 上振れ |
| 9 | render.py 拡張 +270 行・3 機能統合 |
| 10 | v9.2.0 JSON schema 設計規律（既存 render.py の dict keys が authoritative） |
| 11 | night-batch-runner と render.py の挙動差 |
| 12 | Phase 13A+ tracking items 5 件 |
| 13 | .gitignore 規律と _experimental/ の運用 |

新規 Claude.ai チャットでもこれらの memory は継承されるため、このドキュメント本文と合わせて参照することで完全な引継ぎが成立します。

---

## 10. 締めくくり

Phase 13A は v9.2.0 DEEP-DIVE spec の実装と production 動作を達成した重要な里程標です。設計から実装、デバッグ、視覚 sanity、リポジトリ統合まで一気通貫で完了し、リポジトリは HEAD `18e8db5` で安定しています。

Phase 13B では Phase 5 の主目的（303/304 baseline reliability restoration）を完遂し、v9.2.0 化問題が 3 件揃うことで bar-exam-tx 量産パスが本格稼働します。

Phase 13A セッションでの設計判断・実装・検証に関する詳細は git log（`git log --oneline 67cbc82..18e8db5`）と memory item 8-13 に記録されています。

**Phase 13A 完了。Phase 13B 開始準備完了。**

---

*作成: 2026-05-25*
*作成者: claude.ai セッション (Phase 13A 完了直後)*
