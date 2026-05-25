# Phase 13C → Phase 14 引継ぎドキュメント

**作成日**: 2026-05-25
**作成者**: claude.ai セッション (Phase 13C 設計・実装担当)
**対象**: 新規 Claude.ai チャットで Phase 14 量産フェーズを開始する次セッション
**前提**: bar-exam-tx project / xnhsky/bar-exam リポジトリ

---

## 0. このドキュメントの使い方

### 配置先

```
bar-exam/
├── docs/
│   ├── v9.2.0-DESIGN-HANDOFF.md             ← Phase 12 → 13A 引継ぎ (既存)
│   ├── PHASE-13A-COMPLETION-HANDOFF.md      ← Phase 13A → 13B 引継ぎ (既存)
│   ├── PHASE-13B-COMPLETION-HANDOFF.md      ← Phase 13B → 13C 引継ぎ (既存)
│   └── PHASE-13C-COMPLETION-HANDOFF.md      ← このドキュメント
```

このドキュメントを `docs/PHASE-13C-COMPLETION-HANDOFF.md` として配置し、commit してください。
新規 Claude.ai チャットで Phase 14 量産を開始する際は、最初のメッセージで以下を指示：

```
docs/PHASE-13C-COMPLETION-HANDOFF.md を読んで Phase 14 量産フェーズを開始してください。
最初の対象問題は 306 (xx-xx.pdf) です。
```

### 構成

- §1: Executive Summary
- §2: 現状 Snapshot (Phase 13C 完了直後)
- §3: Phase 13C 達成事項（5 タスク + 罠 11 副次発見）
- §4: Phase 13C で確立した追加規律
- §5: Phase 13C で踏んだ新規の罠（罠 11 詳細記録）
- §6: Phase 13C+ tracking items（繰越課題）
- §7: Phase 14（量産フェーズ）開始手順
- §8: Phase 14 量産規律
- §9: 新チャット用プロンプトテンプレート
- §10: memory 反映予定の事実
- §11: 締めくくり

---

## 1. Executive Summary

### Phase 13C の主成果

**Phase 14 量産フェーズに向けた品質保証基盤が完成した。**

- **3 層安全策**が確立: CP gate (spec_version aware) / validate-tx (S89 罠 9 検出) / runner warning (生成時間異常)
- **2 種規律ツール**が確立: drill_blocks 逆抽出 / density-v2 char 数計測
- **1 種 content 規律到達**: problems/305.json から render.py 単独で _experimental/刑TX305.html を byte-identical 再現可能（SHA-256 完全一致）
- **罠 11 副次発見**: claude -p AI judgement abridge（HTML markup overhead を増やしつつ本文 char を圧縮する逆転現象）
- **6 commits**完了・**API コスト $0**（実装中心・claude -p 不使用）
- Phase 13B+ tracking items の主要 3 件（旧 #3 / 旧 #1 / 新 #2）を完全解消

### Phase 13C の意義

Phase 13B で「v9.2.0 spec の量産可能性が実機検証された」ことを受け、Phase 13C では **量産フェーズの周辺基盤**を整備した。CP gate の運用正常化により、Phase 14 で v9.2.0 ファイルが増えても DIFF カウンタが暴走しない。validate-tx の skip→error 化により、罠 9（claude -p 不完全出力）が再発しても自動検出される。drill_blocks 逆抽出により、305 の再生成性が 100% 保証された。

さらに 13C-4 の density-v2 計測ツール実装中に**罠 11（claude -p AI abridge）**を副次発見。これは Phase 14 量産戦略を変える重要発見で、「JSON 完備時は claude -p 不要・render.py 経由が char 数規律精度で優位」という運用方針が確立した。

### 重要な commit (時系列・最新が下)

```
38a6ea2  docs: add Phase 13B completion handoff document
d8a4a93  scripts: _cp_gate_check.py spec_version aware (v9.2.0 skip)
141305c  scripts: validate-tx.py S89 罠 9 検出強化
b6e85dc  scripts: night-batch-runner.ps1 生成時間 warning 追加
c920be3  scripts: add extract_drill_blocks.py (drill_blocks 逆抽出)
82eacd7  feat(content): 305.json drill_blocks 12 件注入 (再生成性保証)
d8c23e2  scripts: add measure_density_v2.py + 罠 11 発見  ← HEAD
```

---

## 2. 現状 Snapshot (Phase 13C 完了直後)

### リポジトリ状態

| 項目 | 値 |
|---|---|
| origin/master HEAD | `d8c23e2` |
| 作業 PC | xnrg2.DESKTOP-5664QR6 (Windows + pwsh 7.6.2) |
| Phase 13C 着手前 HEAD | `38a6ea2` (Phase 13B HANDOFF doc) |
| 累積 commits (13C-1〜13C-4) | 6 件 |

### CP gate 状態

```
python scripts/_cp_gate_check.py
→ PASS=11 / DIFF=1 / EXTRA=0 / MISS=0 / SKIP_v92=3 / baseline=15
```

**DIFF=1 の内訳**:
1. `刑TX300.html`: rb-chip id 注入由来（Phase 4-4 以降の長年継続 DIFF）

**SKIP_v92=3 の内訳**:
1. `303.json` (spec_version="v9.2.0")
2. `304.json` (spec_version="v9.2.0")
3. `305.json` (spec_version="v9.2.0")

Phase 13C-1 の spec_version aware 化により、v9.2.0 ファイルは baseline 比較から除外され、SKIP_v92 として独立カウントされる。Phase 14 量産で v9.2.0 ファイルが増えても DIFF は増加しない（300 のみ）。

### ファイル配置

| パス | サイズ | 状態 |
|---|---|---|
| `scripts/_cp_gate_check.py` | 約 110 行 | spec_version aware 版（commit `d8a4a93`） |
| `scripts/validate-tx.py` | 約 1,490 行 | S89 罠 9 検出強化版（commit `141305c`） |
| `scripts/night-batch-runner.ps1` | (既存 + 9 行) | 生成時間 warning 追加版（commit `b6e85dc`） |
| `scripts/extract_drill_blocks.py` | 新規作成 | drill_blocks 逆抽出ツール（commit `c920be3`） |
| `scripts/measure_density_v2.py` | 新規作成 (約 152 行) | density-v2 計測ツール（commit `d8c23e2`） |
| `scripts/render.py` | 約 3,048 行 | v9.2.0 完全対応（変更なし） |
| `problems/303.json` | 約 71.3 KB | v9.2.0 schema 準拠（変更なし） |
| `problems/304.json` | 約 66.0 KB | v9.2.0 schema 準拠（変更なし） |
| `problems/305.json` | 約 43 KB | drill_blocks 12 件注入（commit `82eacd7`・top-level 22→23 keys） |
| `_experimental/刑TX303.html` | 約 198 KB | Phase 13B step 1 baseline（変更なし） |
| `_experimental/刑TX304.html` | 約 215 KB | Phase 13B step 2 v2 baseline（変更なし・**罠 11 観測対象**） |
| `_experimental/刑TX305.html` | 約 171 KB | Phase 13A first-light baseline（変更なし・**byte-identical 再現 PASS**） |

### 13C で新規追加されたファイル

```
scripts/extract_drill_blocks.py       # HTML から drill_blocks 12 件を逆抽出
scripts/measure_density_v2.py         # JSON/HTML 両モードの density-v2 char 数計測
```

### 13C で変更されたファイル

```
scripts/_cp_gate_check.py            # spec_version aware 化 (+20 / -1)
scripts/validate-tx.py               # check_theory_deep_dive S89 強化 (+28 / -3)
scripts/night-batch-runner.ps1       # 生成時間異常 warning (+9 / -0)
problems/305.json                    # drill_blocks 12 件注入 (+87 / -1)
```

### .gitignore 規律（不変）

```
# line 19 付近
outputs/**/*.html
```

→ HTML 成果物は git 管理対象外、Drive 管理側へ別途配信。
→ first-light / Phase 13B baseline 等の保護対象は `_experimental/` に配置して commit。

---

## 3. Phase 13C 達成事項

### 3.1 Phase 13C-1: _cp_gate_check.py spec_version aware 化

**Commit**: `d8a4a93`
**実装規模**: +20 / -1（3 箇所修正）

#### 変更内容
1. `skip_v92_count = 0` カウンタ追加（L51）
2. L62-78 に v9.2.0 判定ロジック追加:
   - JSON ロード後・render 開始前で `spec_version == "v9.2.0"` チェック
   - 該当時は `print(f"  {pid}: SKIP_v92 (spec_version=v9.2.0)")` + `continue`
   - `rendered_keys.add(skip_out_rel)` で後段 MISS 誤検出も回避（**CC 自主実装の改善**）
3. L100 最終 Summary print に `SKIP_v92=N` 追加

#### 期待効果と実測

| ステージ | PASS | DIFF | SKIP_v92 | 内訳 |
|---|---|---|---|---|
| Phase 13B 完了時 | 11 | 4 | (未対応) | 300 + 303 + 304 + 305 |
| Phase 13C-1 完了後 | 11 | 1 | 3 | 300 のみ DIFF + 303/304/305 SKIP_v92 |

Phase 14 量産で v9.2.0 ファイルが追加されても、DIFF は 1 のままで SKIP_v92 が増加するだけ。CP gate 運用が破綻しない。

### 3.2 Phase 13C-2: validate-tx.py S89 罠 9 検出強化

**Commit**: `141305c`
**実装規模**: +28 / -3（4 箇所修正）

#### 変更内容
1. `check_theory_deep_dive(soup, rep)` → `check_theory_deep_dive(target, soup, rep)` シグネチャ拡張（L1202）
2. L1208 以降、spec_version v9.2.0 判定後に JSON theory_deep_dive 存在判定を追加:
   ```python
   json_path = derive_problem_json_path(target)
   json_has_theory = False
   if json_path.exists():
       try:
           data = json.loads(json_path.read_text(encoding="utf-8"))
           json_has_theory = "theory_deep_dive" in data
       except (json.JSONDecodeError, OSError):
           pass
   html_has_tag = footer_has_tag(soup, "theory-deep-dive")
   if json_has_theory and not html_has_tag:
       rep.error("S89", 'JSON に "theory_deep_dive" 定義あるが HTML 出力に "theory-deep-dive" feature-tag 不在（罠 9・claude -p 不完全出力の可能性・要再生成）')
       return
   ```
3. L1475 caller を `check_theory_deep_dive(target, soup, rep)` に修正

#### 検証結果

| 検証項目 | 結果 |
|---|---|
| regression: 303 ERROR 0 | ✓ |
| regression: 304 ERROR 0 | ✓ |
| regression: 305 ERROR 0 | ✓ |
| synthetic trap-9 test | **ERROR 正しく fire** ✓ |

CC が独自に synthetic test fixture を作成して罠 9 検出を実機確認した、想定外の検証品質。

#### 効果

Phase 13B step 2 v1 で発生した「304.json に theory_deep_dive あり + HTML に tag 不在 → S89 skip で偽 PASS」が、本強化で自動検出可能になった。Phase 14 量産で claude -p の不完全出力（罠 9）が再発しても、validate-tx 単独で検出され ERROR 化される。

### 3.3 Phase 13C-3: night-batch-runner.ps1 生成時間 warning 追加

**Commit**: `b6e85dc`
**実装規模**: +9 / -0

#### 変更内容
L168（`$elapsed` 確定直後）に挿入:
```powershell
if ($elapsed -gt 1200) {
    Write-Warning "生成時間異常: ${elapsed}秒（想定 4-7 min）- 罠 9（claude -p 不完全出力）警戒"
    Write-Warning "品質チェック推奨: feature-tag 33 件 / theory-detail-grid / palette-strategy"
}
```

#### 既知発火ケース予測（過去データ）

| problem | elapsed | warning |
|---|---|---|
| 305 | 412 sec (6.87 min) | 発火しない（正常） |
| 303 | 259 sec (4.3 min) | 発火しない（正常） |
| 304 v1 | 1437 sec (24 min) | **発火**（実際に罠 9） |
| 304 v2 | 1733 sec (28.9 min) | **発火**（完全出力だが時間超過） |

→ false-positive あり（v2 のように 20 min 超でも完全出力のケース）。これは設計通り：「警戒シグナル」であり「failure 判定」ではない。Phase 14 量産時に transcript ログ上で即座に判別可能。

### 3.4 Phase 13C-5: drill_blocks 逆抽出 + 305.json 注入

**Commits**: `c920be3` (extract_drill_blocks.py) + `82eacd7` (305.json 注入)
**実装規模**: 新規スクリプト + 87 行 JSON 追加

#### 変更内容

1. `scripts/extract_drill_blocks.py` 新規作成:
   - 引数: HTML パス
   - 出力: drill_blocks 配列 JSON を stdout に出力
   - sanity check: 12 件 exact ASSERT
   - escape 規律: BS4 で生値抽出（render.py 側の escape なし規律と整合）
   - Windows cp932 回避（utf-8 reconfigure）

2. `problems/305.json` に drill_blocks 12 件注入:
   - 抽出元: `_experimental/刑TX305.html` (commit 18e8db5)
   - top-level keys: 22 → 23（drill_blocks フィールド追加）

#### 検証結果

| 検証項目 | 結果 |
|---|---|
| 抽出件数 | 12 件 exact ✓ |
| sanity (num/tag/correct/explanation) | 全件適正 ✓ |
| JSON syntax | OK ✓ |
| **再 render → _experimental hash 比較** | **完全同一: 596a67b7434e36ee...** ✓ |

#### 検証成功の意味

**problems/305.json + render.py → outputs/tx/刑TX/刑TX305.html (171,375 bytes)**
**= _experimental/刑TX305.html (claude -p 生成・171,375 bytes)**
**完全同一 hash: 596a67b7434e36ee...**

つまり 305.json には AI 生成 HTML を完全再現するに足る情報がすべて格納された。drill_blocks 12 件含め、**claude -p なしでも render.py だけで Phase 13A first-light HTML を bit-exact 再構築可能**。

#### 副次効果

HANDOFF tracking #1（drill_blocks JSON 明示）が 305 で完全解消。303/304 と同水準の再生成性規律に到達。Phase 14 量産で「JSON のみで完全再現可能」という安定運用が可能。

### 3.5 Phase 13C-4: measure_density_v2.py + 罠 11 発見

**Commit**: `d8c23e2`
**実装規模**: +152 行（新規スクリプト）

#### 変更内容

`scripts/measure_density_v2.py` 新規作成:
- JSON モード: `problems/{ID}.json` の `choices[*].professor` から純 char 数集計
- HTML モード: BS4 で `<div class="prof-heading">` 内 text を集計（h4/h5 見出し除外）
- 規律判定: 1,150+ (PASS) / 800-1149 (WARN) / <800 (FAIL)
- 出力: 5 choices × 4 prof-headings の table + 集計

#### 検証結果

| 検証項目 | 結果 |
|---|---|
| JSON mode regression (303/304/305) | 全 15 件 PASS ✓ |
| HTML mode regression (303/304/305) | 全 15 件 PASS ✓ |
| 303/305 JSON vs HTML divergence | <1%（測定整合性確認） ✓ |
| **304 JSON vs HTML divergence** | **-37.6%（罠 11 観測）** ⚠️ |

#### 副次発見: 罠 11 の確定

詳細は §5 参照。要点：

| 経路 | 304 HTML char | JSON 比 | サイズ |
|---|---|---|---|
| render.py 経由（13C-4 検証中に CC 実行） | 1,982-2,189 | -0.34% | 189,704 bytes |
| claude -p 経由 (`_experimental/刑TX304.html`) | 1,239-1,393 | -37.6% | 215,097 bytes |

→ **claude -p が JSON content を AI judgement で abridge（圧縮）した**ことを確定。同時に **HTML markup を装飾的に増やしている**ため、ファイルサイズは大きいのに本文 char 数は少ない**逆転現象**。

303/305 では <1% 乖離で問題なし、**304 固有現象**。Phase 13B step 2 で 28.9 min かかった理由がここで説明される（罠 9 警戒シグナルと罠 11 が合成発生）。

---

## 4. Phase 13C で確立した追加規律

これは Phase 13A §4 / Phase 13B §4 を補完する、Phase 13C で新たに確立した運用規律。

### 4.1 claude -p vs render.py の経路選択判断（重要）

**罠 11 発見により、量産フェーズの経路選択が体系化された**:

| シナリオ | 推奨経路 | 理由 |
|---|---|---|
| 新規問題の v9.2.0 first-light 生成 | **claude -p (night-batch-runner)** | JSON 設計だけでは AI 補完部分（drill_blocks / mindmap 詳細 / palette 派生色等）が再現不能 |
| 既存 v9.2.0 ファイルの再生成 | **render.py 経由** | JSON 完備時は char 数規律精度が優位・byte-identical 再現可能（305 で実証） |
| 軽微な JSON 編集後の更新 | **render.py 経由** | claude -p は AI abridge の罠 11 リスクあり |
| 大幅 JSON 改修（schema 追加等） | **claude -p（first-light 扱い）** | render.py の slot 未対応領域の AI 補完が必要 |

**判定フロー**:
1. JSON に全フィールド（drill_blocks 含む）が揃っているか？
2. YES → render.py 経由で十分・claude -p 不要・char 規律精度優位
3. NO → claude -p で first-light → 生成後 extract_drill_blocks.py 等で JSON 補完 → 再生成性確保

### 4.2 first-light → 逆抽出 → render.py 経路の確立

305 で実証された運用パターン:

```
[Step 1] JSON 起草（drill_blocks 等は skeleton or 空配列）
[Step 2] claude -p で first-light HTML 生成（AI が drill_blocks 補完）
[Step 3] extract_drill_blocks.py で HTML → JSON 逆抽出
[Step 4] JSON に drill_blocks マージ
[Step 5] render.py で再生成して byte-identical 確認（regression check）
[Step 6] 以降は render.py 経由で更新可能
```

**Step 5 byte-identical 不成立の場合は罠 11 検出**。Phase 14 量産で必須の品質保証手順。

### 4.3 AI abridge 検出時の対応

罠 11 観測時の運用基準:

| 状況 | 対応 |
|---|---|
| JSON vs HTML divergence <5% | 正常範囲・許容 |
| 5-15% | AI judgement の軽微な差・記録のみ |
| 15-30% | 罠 11 警戒・要原因究明 |
| 30%+ | **罠 11 確定**・render.py 経由再生成で baseline 統一推奨 |

304 の現状（-37.6%）は **30%+ ゾーン**で baseline 統一すべきだが、Phase 14 前の判断事項（§7.2 参照）。

### 4.4 density-v2 計測の正規実装（規律）

claude.ai 起草時計測の正規ロジック（罠 10 解消）:

```python
# JSON モード（claude.ai 起草時計測の正規実装）
point_chars = len(point["locus"]) + sum(len(x) for x in point["list"])
process_chars = sum(len(x) for x in process["steps"])
image_chars = sum(len(image[k]) for k in ("scene", "bridge", "contrast"))
app_chars = sum(len(application[k]) for k in ("major", "minor", "conclusion"))
total = point_chars + process_chars + image_chars + app_chars
# 1,150+ → PASS / 800-1149 → WARN / <800 → FAIL
```

旧 regex 計測（HANDOFF §5 罠 10）は破棄。Phase 14 では `scripts/measure_density_v2.py` の JSON モードを正規計測として採用。claude.ai 側でも同等ロジック（純 len() 集計）で起草時計測する。

### 4.5 skip→error 化による偽 PASS 検出パターン

S89 強化で確立した validate-tx 拡張パターン:

```python
# JSON 側にフィールドあり + HTML 側に対応 feature-tag 不在 → ERROR
if json_has_field and not html_has_tag:
    rep.error("SXX", "JSON に X 定義あるが HTML 出力に Y 不在（claude -p 不完全出力可能性・要再生成）")
    return
```

この pattern は S90/S91 等の他検査にも応用可能（§6 §6.1 §13C-2b）。Phase 14 量産で claude -p の不完全出力（罠 9）が再発しても自動検出可能になる基盤。

### 4.6 spec_version aware による永続的な多バージョン管理

Phase 13C-1 で導入した `spec_version aware` パターンは、今後 v9.3.0 等の新 schema 投入時にも応用可能:

```python
# 拡張パターン例（将来 v9.3.0 投入時）
if spec_version == "v9.2.0":
    skip_v92_count += 1
elif spec_version == "v9.3.0":
    skip_v93_count += 1
```

exact match（`==`）の判定なので、各バージョンを独立して管理可能。Phase 13C HANDOFF §4 設計判断 #2 で確認済。

---

## 5. Phase 13C で踏んだ新規の罠

これは Phase 13A §5 / Phase 13B §5 を補完する、Phase 13C で新たに踏んだ罠。

### 罠 11: claude -p AI judgement abridge（HTML markup 増 + 本文 char 減の逆転）

**発見経緯**: Phase 13C-4 で `measure_density_v2.py` を 303/304/305 全件 JSON/HTML 両モードで検証した際、303/305 は <1% 乖離で問題なかったが、**304 のみ -37.6% 乖離**を観測。

#### 観測データ

| 経路 | 304 HTML char (5 choices) | JSON 比 | ファイルサイズ |
|---|---|---|---|
| `render.py` 経由（JSON 完備版） | 1,982 / 2,199 / 2,052 / 2,028 / 2,026 | -0.34% | 189,704 bytes |
| `claude -p` 経由 (`_experimental/刑TX304.html`) | 1,239 / 1,274 / 1,285 / 1,226 / 1,393 | -37.6% | 215,097 bytes |

choice 単位の char 数:

| 経路 | choice 1 | choice 2 | choice 3 | choice 4 | choice 5 |
|---|---|---|---|---|---|
| render.py | 1,984 | 2,199 | 2,052 | 2,028 | 2,026 |
| claude -p | 1,239 | 1,274 | 1,285 | 1,226 | 1,393 |
| 乖離 | -38% | -42% | -37% | -40% | -31% |

#### 罠 11 の本質

**逆転現象**: ファイルサイズは AI 装飾で大きい（215K bytes）が、本文 char 数は少ない（1,239-1,393）。
つまり **claude -p が**:
1. JSON content（process.steps 等）を **AI judgement で abridge（圧縮）**
2. 同時に HTML markup や装飾要素を **追加で挿入**

これにより:
- 視覚的には豪華な HTML（feature-tag 33 件・theory-detail-grid 完備）
- char 数規律は **規律下限ギリギリ**まで圧縮されている

#### 原因解釈（3 仮説中の最有力）

1. **AI judgement の content abridge** ← 最有力（claude -p の本質的特性）
   - 「読みやすい長さ」に AI が自動調整
   - JSON content 4 step 各 180 char → 各 100 char に圧縮等
2. JSON フィールド設計が render path で消費されない部分を含む（Phase 12 起草時の設計問題）
3. 計測ロジックの不整合（13C-4 ツール側の問題）

→ render.py 経由で再生成した HTML が JSON char 数とほぼ一致（-0.34%）した時点で、**2 と 3 は否定**。原因は claude -p 固有の AI abridge と確定。

#### Phase 14 量産への影響

| 状況 | 対応 |
|---|---|
| first-light 生成（新規問題） | claude -p 使用 OK・ただし生成後 extract_drill_blocks.py で逆抽出して再生成性確保 |
| 既存問題の更新 | render.py 経由を推奨・claude -p 不要 |
| 規律違反検出時 | render.py 経由で再生成して baseline 統一を検討 |

→ §4.1 の経路選択判断と直結。

### 罠 12（候補・未確定）: AI abridge は HTML サイズが大きいので一見気づきにくい

**観測**: 304 の AI abridge ケースで、ファイルサイズは 215K bytes と平均的に見えた。視覚 sanity check（feature-tag 数・theory-detail-grid 等）も全 PASS。**サイズと視覚チェックだけでは罠 11 が見逃される**リスク。

**対応**: Phase 14 量産では生成後に `measure_density_v2.py` の JSON/HTML 両モード比較を必須化（§8.3 参照）。

### 罠 13（候補・未確定）: regression check で 1 件だけ大乖離 = AI judgement 固有

**観測**: 303/305 は <1% 乖離なのに 304 だけ -37.6%。同じ claude -p 経由でも、問題の構造（instruction_type / palette_strategy / theory 性）や AI judgement の作用で大きく結果が変わる。

**含意**: 罠 11 の発火条件は不定。**全 v9.2.0 ファイルで density 計測を必須化**することで、罠 11 を網羅的に検出する運用が必要。

---

## 6. Phase 13C+ tracking items（繰越課題）

| # | 項目 | 種別 | 優先度 | 担当 Phase |
|---|---|---|---|---|
| 繰越 旧 #4 | claude.ai 側計測スクリプト精度向上の正規化（spec § 18 への追記） | 規律文書化 | 中 | 14 |
| 繰越 旧 #5 | `_phase3_2_pre_patch_baseline.json` の旧 v9.1.0/v8.11.7 hash 残留削除 | リファクタ | 低 | 14+ |
| 繰越 旧 #6 | P3 派生色サニティ（次の P3 帯問題生成時） | パレット規律確認 | 低 | 14 |
| **新 #1** | **304 baseline 統一判断**: render.py 経由で再生成して density richer 版に統一するか、現状 _experimental の AI abridge 版を保持するか | content 戦略 | **高** | **14 開始時** |
| **新 #2** | **validate-tx S90/S91 同様強化**（罠 9 type の偽 PASS 検出を S89 以外にも展開） | 品質保証強化 | 中 | 14 |
| **新 #3** | **measure_density_v2.py の HTML モード精度向上**（h4/h5 除外ロジックの edge case 対応） | ツール精度 | 低 | 14+ |
| **新 #4** | **罠 11 検出の自動化**（生成後 JSON/HTML divergence 30%+ で warning） | 品質保証強化 | 中 | 14 |
| **新 #5** | **claude.ai 起草段階での density 計測ロジック spec 化**（spec § 18 に measure_density_v2.py JSON モードと同等の式を記載） | spec 文書化 | 中 | 14 |

### tracking item 詳細メモ

#### 新 #1: 304 baseline 統一判断（**Phase 14 開始前の判断必須**）

**現状**:
- `_experimental/刑TX304.html`: claude -p 経由・AI abridge 適用・char -37.6%
- 305 では byte-identical 再現が成立したが、304 では成立しない可能性

**選択肢**:

A. **render.py 経由再生成版を新 baseline に**
   - 利点: char 規律精度向上・密度 richer
   - 欠点: feature-tag 33 件や theory-detail-grid 構造の AI 装飾が失われる可能性
   - 検証: render.py 再生成 → 33 feature-tag exact / theory-detail-grid 完備 を validate-tx で確認

B. **現状 _experimental の AI abridge 版を保持**
   - 利点: AI 装飾の richness 保持・現状動作不変
   - 欠点: density 規律下限ギリギリ・305 のような byte-identical 保証なし

C. **両方を併存** (`_experimental/刑TX304_render.html` と `_experimental/刑TX304_claude.html`)
   - 利点: 比較研究材料として有用
   - 欠点: 管理コスト・どちらが正規か曖昧

**推奨**: A（render.py 経由 baseline）。理由:
- 305 で確立した「JSON 完備 → byte-identical 再現」path の一貫性
- char 数規律精度の優位（罠 11 回避）
- 305 と同水準の再生成性保証

ただし Phase 14 開始時に validate-tx での視覚 sanity を確認し、AI 装飾の欠落が許容範囲かを判断する。

#### 新 #2: validate-tx S90/S91 同様強化

S89 強化（13C-2）と同じパターンを S90 (meta-explanation) / S91 (professor-density) にも適用:

```python
# 例: S91 強化
json_has_density_v2 = any("professor" in c and "point" in c.get("professor", {}) 
                            for c in data.get("choices", []))
html_has_tag = footer_has_tag(soup, "professor-density-v2")
if json_has_density_v2 and not html_has_tag:
    rep.error("S91", "JSON に density-v2 (professor.point) 定義あるが HTML に professor-density-v2 feature-tag 不在")
```

Phase 14 量産で罠 9 type のリスクを網羅的に低減。

#### 新 #4: 罠 11 検出の自動化

night-batch-runner.ps1 への組込み案:

```powershell
# 生成完了後に追加
$density_json = python scripts\measure_density_v2.py problems\$pid.json | Select-String "total"
$density_html = python scripts\measure_density_v2.py outputs\tx\${jp}TX\${jp}TX$pid.html | Select-String "total"
# 各 choice の total 差を計算
$divergence = ((($json_avg - $html_avg) / $json_avg) * 100)
if ([Math]::Abs($divergence) -gt 30) {
    Write-Warning "罠 11 検出: JSON vs HTML density 乖離 ${divergence}% (>30%) - AI abridge の可能性"
}
```

Phase 14 量産で罠 11 を transcript ログ上で即座に判別可能になる。

---

## 7. Phase 14（量産フェーズ）開始手順

### 7.1 Phase 14 の目的

**306 以降の問題を v9.2.0 で量産生成し、bar-exam-tx の完成度を引き上げる。**

現状: v8.11.7 ベース 11 件 + v9.2.0 ベース 3 件 = 14 件
目標: 100 件程度まで段階的に拡張（10-20 週間想定）

### 7.2 Phase 14 開始前の判断事項（**必須**）

**判断 1: 304 baseline 統一（§6 新 #1）**

```
# 検証用 render
rm outputs\tx\刑TX\刑TX304.html
python scripts\render.py 304
python scripts\validate-tx.py outputs\tx\刑TX\刑TX304.html
# → ERROR 0 / WARNING 0 確認
python scripts\measure_density_v2.py outputs\tx\刑TX\刑TX304.html
# → 全 5 件 PASS 確認

# 視覚 sanity（feature-tag 33 件 / theory-detail-grid 等）
grep -c "feature-tag" outputs\tx\刑TX\刑TX304.html
# 期待: 33

# 判定 OK なら _experimental に baseline 統一
cp outputs\tx\刑TX\刑TX304.html _experimental\刑TX304.html
git add _experimental\刑TX304.html
git commit -m "fix(content): 304 baseline render.py 経由統一 (罠 11 回避)"
```

**判断 2: 量産対象問題の選定**

オプション:
- **連番**（306 / 307 / 308 ...）: 体系的・進捗管理しやすい
- **主題別**（刑法各論 全件 → 民法各論 ...）: 学習者視点で有用
- **難度別**（P1 → P2 → P3）: パレット規律検証しやすい

推奨: 連番ベース・必要に応じて優先問題を割込み。

**判断 3: バッチサイズ**

- night-batch-runner.ps1 既定: 5 問バッチ
- memory item: 5 問連続 2h5m で週次 Opus 上限未到達実績
- 推奨: 5 問バッチ × 週 2 回程度

### 7.3 Phase 14 開始手順（コマンドフロー）

```powershell
cd C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam
git pull origin master
git log --oneline -5
# 期待: HEAD = d8c23e2 (または 13C+ 後続 commits)

python scripts\_cp_gate_check.py
# 期待: PASS=11/DIFF=1/SKIP_v92=3 (または SKIP_v92=N 増加)

# 判断 1 を実施（304 baseline 統一）
# ...

# 量産開始
# Step 1: 306.json 起草（claude.ai で）
# Step 2: night-batch-runner で生成
.\scripts\night-batch-runner.ps1 -SpecVersion v9.2.0 -MaxProblems 5
# 範囲: 306-310
# Step 3: 各問題で validate-tx + measure_density_v2 で検証
# Step 4: 必要に応じて extract_drill_blocks → JSON 補完 → render.py で baseline 再生成
# Step 5: commit
```

### 7.4 想定スケジュール

| 期間 | 生成問題数 | 累計問題数（推定） |
|---|---|---|
| 1 週目 (Phase 14 立ち上げ) | 5 問（306-310） | 19 件 |
| 2-4 週目 | 各週 5-10 問 | 30-45 件 |
| 5-8 週目 | 各週 5-10 問 | 50-75 件 |
| 9-12 週目 | 各週 5-10 問 | 80-100 件 |

Phase 13C 確立の品質保証基盤（3 層安全策 + 2 種規律ツール）により、量産速度は Phase 13B より向上見込み。

---

## 8. Phase 14 量産規律

### 8.1 JSON 起草段階（claude.ai 側）

Phase 13A・13B・13C で確立した規律を Phase 14 で運用:

**罠回避**:
- 罠 1-11 全件回避（Phase 13A §5 + Phase 13B §5 + Phase 13C §5）
- 特に罠 11（AI abridge）を意識：density-v2 規律を明示的に measure_density_v2.py JSON モードで検証

**density 規律**:
- §4.4 の正規実装で計測（純 len() 集計）
- 1,150+ chars (PASS) 必須・1,500+ 推奨（+30% バッファ）

**drill_blocks 規律**:
- 12 件 JSON 明示（Phase 13C-5 で確立した規律）
- 既存パターン（303/304/305）をテンプレートとして 1:1 踏襲

**mindmap_tree 規律**:
- KTX301 由来語彙完全排除（Phase 13A §4 規律継続）
- S78 ブラックリスト適合

### 8.2 生成段階（Claude Code 側）

経路選択（§4.1 参照）:

| シナリオ | 経路 | 検証 |
|---|---|---|
| 新規問題の first-light | claude -p (night-batch-runner) | validate-tx + measure_density_v2 |
| 既存問題の更新 | render.py | validate-tx |
| JSON 完備の再生成 | render.py | byte-identical チェック |

**生成時間監視**:
- night-batch-runner warning（13C-3）: 20 min 超で罠 9/11 警戒
- 警戒シグナル発火時は measure_density_v2 で罠 11 検出を併せて実施

**バッチ運用**:
- 5 問バッチ・連続失敗 abort（既存規律）
- 個別 validate-tx 実行（auto-quarantine 回避）

### 8.3 品質判定（**Phase 14 必須チェックリスト**）

各問題の最終判定:

```
[ ] validate-tx: ERROR 0 / WARNING 0
[ ] measure_density_v2 JSON モード: 全 choice PASS (1,150+)
[ ] measure_density_v2 HTML モード: 全 choice PASS (1,150+)
[ ] JSON vs HTML divergence < 30% (罠 11 確認)
[ ] feature-tag 33 件 exact
[ ] theory-detail-grid 1 件（theory_deep_dive あり時）
[ ] palette-strategy tag 存在
[ ] 派生色 10 個完備
[ ] drill_blocks 12 件（HTML 側）
[ ] skip-based PASS が存在しない（S89/S90/S91 等が trigger tag 不在で skip していない）
```

**1 つでも不満たない場合は再生成 or JSON 補正**。

**罠 11 検出時の対応**:
- divergence 30%+: render.py 経由で再生成して baseline 統一を検討
- divergence 15-30%: 記録のみ・許容
- divergence <15%: 正常範囲

### 8.4 乖離許容（規律外として記録）

以下は規律違反ではなく judgement deviation として記録:

- **palette_strategy の JSON vs HTML 差**（Phase 13B step 2 で観測）: AI judgement・許容
- **flowchart decisions / chips 数の AI 再構成**: 構造完備なら許容
- **mindmap_tree の depth 差**: 全 4 階層完備なら許容

### 8.5 commit 規律

各問題 1 commit を推奨:

```
feat(content): 刑TX306 v9.2.0 ([問題タイトル])

- instruction_type: [type]
- override_pattern: [P1/P2/P3]
- palette_strategy: [strategy]
- theory_deep_dive: [yes/no]
- density-v2: 全件 PASS ([min]-[max] chars)
- generation time: [N] min
- validate-tx: ERROR 0 / WARNING 0
- measure_density_v2: divergence [N]%
```

---

## 9. 新チャット用プロンプトテンプレート

新規 Claude.ai チャットで Phase 14 を開始する際の初期メッセージ:

### プロンプト A: Phase 14 量産開始（306 から）

```
Phase 14 量産フェーズを開始します。

前提として docs/PHASE-13C-COMPLETION-HANDOFF.md を必ず読んでください。
Phase 13C 全 5 タスク完了済み（3 層安全策 + 2 種規律ツール + 1 種 content 規律到達）。

最初の作業:
1. Phase 14 開始前の判断事項（HANDOFF §7.2）を確認
   - 判断 1: 304 baseline 統一（推奨は render.py 経由再生成）
   - 判断 2: 量産対象問題の選定（連番 or 主題別）
   - 判断 3: バッチサイズ（5 問推奨）

2. 最初の量産対象問題: [問題番号]（[出典・配点]）
   PDF: inputs/tx-pdfs/[問題番号].pdf

進め方:
- 303/304/305 を骨格テンプレートとして 1:1 踏襲
- 罠 1-11 全件回避（Phase 13A/13B/13C §5）
- §4.1 経路選択判断で claude -p / render.py を選択
- §8.3 品質判定チェックリスト全項目 PASS 必須

慎重設計モードで進めてください。
```

### プロンプト B: 304 baseline 統一の単独判断

```
docs/PHASE-13C-COMPLETION-HANDOFF.md §6 新 #1 / §7.2 判断 1 に従って、
304 baseline 統一の検証と判断を実施してください。

検証手順:
1. render.py 経由で 304 を再生成
2. validate-tx で ERROR 0 / WARNING 0 確認
3. measure_density_v2 で全 5 choice PASS 確認
4. 視覚 sanity（feature-tag 33 / theory-detail-grid / 33 feature-tag）

判定:
- 全 PASS → _experimental/刑TX304.html を render.py 版に統一
- 一部 FAIL → 原因究明・STOP-for-review

慎重設計モードで進めてください。
```

### プロンプト C: 状況確認だけ

```
docs/PHASE-13C-COMPLETION-HANDOFF.md を読んで、現状を要約してください。

確認したい点:
- Phase 13C の達成事項（5 タスク + 罠 11 副次発見）
- 現状の CP gate 状態
- Phase 14 開始前の判断事項
- Phase 13C+ tracking items の優先順位
- 罠 11 の詳細
```

### プロンプト D: 単発 v9.2.0 化（量産途中の個別問題）

```
docs/PHASE-13C-COMPLETION-HANDOFF.md を踏まえて、
[問題番号].pdf を v9.2.0 化してください。

303/304/305 を骨格テンプレートとして 1:1 踏襲し、
罠 1-11 全件回避で起草してください。

経路選択:
- 初回生成: claude -p (night-batch-runner)
- 再生成: render.py 経由
- §4.1 の判定フローに従う

品質判定: §8.3 チェックリスト全項目 PASS 必須

慎重設計モードで進めてください。
```

### プロンプト E: 罠 11 detailed investigation（必要に応じて）

```
docs/PHASE-13C-COMPLETION-HANDOFF.md §5 罠 11 を踏まえて、
[問題番号].html で JSON vs HTML divergence が観測されました。

検証:
1. measure_density_v2.py で JSON モード・HTML モード両方計測
2. divergence % 算出
3. render.py 経由で再生成して比較
4. 罠 11 確定 or 別原因か判定

結果に応じて baseline 統一 or 記録のみで対応。

慎重設計モードで進めてください。
```

---

## 10. memory 反映予定の事実

このドキュメントの内容のうち、以下は新規 Claude.ai チャットでの memory 継承を期待する事実:

| 反映候補 | 内容 |
|---|---|
| 19 | Phase 13C-1 完了・_cp_gate_check.py spec_version aware（commit d8a4a93）→ CP gate PASS=11/DIFF=1/SKIP_v92=3 |
| 20 | Phase 13C-2 完了・validate-tx S89 罠 9 検出強化（commit 141305c）→ skip-based 偽 PASS 自動検出 |
| 21 | Phase 13C-3 完了・night-batch-runner 生成時間 warning（commit b6e85dc）→ 20 min 超で罠 9/11 警戒 |
| 22 | Phase 13C-5 完了・305.json drill_blocks 12 件注入（commits c920be3 + 82eacd7）→ 305 byte-identical 再現確立 |
| 23 | Phase 13C-4 完了・measure_density_v2.py（commit d8c23e2）+ 罠 11 副次発見 |
| 24 | **罠 11: claude -p AI judgement abridge**（HTML markup 増 + 本文 char 圧縮の逆転現象）・304 で -37.6% 観測 |
| 25 | Phase 13C 確立の経路選択判断（first-light は claude -p / 再生成は render.py 優位）・Phase 14 量産戦略の基盤 |
| 26 | 304 baseline 統一判断が Phase 14 開始前に必要（HANDOFF §6 新 #1）・推奨は render.py 経由再生成 |

新規 Claude.ai チャットでもこれらの memory は継承されるため、このドキュメント本文と合わせて参照することで完全な引継ぎが成立します。

---

## 11. 締めくくり

Phase 13C は **Phase 14 量産フェーズの品質保証基盤を完成させた**重要な里程標です。

確立されたもの:
- **3 層安全策**: CP gate (spec-aware) / validate-tx (S89 罠 9 検出) / runner warning (生成時間)
- **2 種規律ツール**: drill_blocks 逆抽出 / density-v2 char 数計測
- **1 種 content 規律到達**: 305 で「JSON のみで byte-identical 再現」path を実証
- **副次発見**: 罠 11（claude -p AI abridge）・Phase 14 経路選択判断の基盤

これらにより、Phase 14 で 306 以降の量産が **安全・効率的・規律準拠**で実行可能になりました。claude -p の AI judgement リスク（罠 9・罠 11）も自動検出可能となり、品質保証コストが大幅に低減。

Phase 13A/B セッションでの設計判断・実装・検証に関する詳細は git log（`git log --oneline 67cbc82..d8c23e2`）と memory item 8-26 に記録されています。Phase 13C HANDOFF（本文書）を新規チャットで参照することで、Phase 14 量産が即座に開始可能です。

**Phase 13C 完了。Phase 14 量産フェーズ開始準備完了。**

---

*作成: 2026-05-25*
*作成者: claude.ai セッション (Phase 13C 完了直後)*
