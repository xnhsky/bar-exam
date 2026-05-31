# Phase Y-4 CC 指示書 ── JSON Schema 完全化と first-light

> **作成日**: 2026-05-26
> **前提**: Phase Y-1〜Y-3 完了。`v9.2.0-COMPLETE-JSON-SCHEMA.md` 文書化済。
> **HEAD**: `b605784` 機能等価（Phase 14-2 完了時点・v9.3.0 完全撤回済）
> **目的**: render.py は無修正のまま、JSON データ補完だけで完璧な HTML を再現する
> **重要前提**: Phase X で行った「:root{} 二重 → 1 つに統合」は**誤った修正**だった可能性が高い

---

## 0. 状況の正確な再認識（CC への重要な伝達）

### 私 (user) と Claude.ai chat が今日確定した事実

1. **render.py は v9.1.0 機能を全て実装している**（C-1〜C-7 7 関数 + basis + cross-card + ref-case id 注入）
2. **303-307.json は 23 keys のみ・basis / part_c / chapter / section の 4 keys を欠く**
3. **その結果、render.py は PART_C_STUBS と BASIS_STUB を出力 → セクションが空白になっていた**
4. **313.html (v9.1.0 MINDMAP) は正常品質のリファレンス**（57 ref-case リンク・C-1〜C-7 全充填）
5. **313.html の :root{} は 2 つで正常**（フォント定義 + 色定義）

### Phase X の修正で何が起きた可能性が高いか

- `:root{}` を 1 つに統合 → CSS cascade で v9.2.0 元の色定義が失われた可能性
- このため 316.html の P3 色 (#E6A1AB) が v9.2.0 既定 (#8a1f3a) で上書きされる現象が起きた
- 真の修正は「`:root{}` を 1 つにする」ではなく、「v9.3.0 :root{} を後ろに置く」だった

つまり Phase X の Phase 14-2 baseline 更新で 303-307 がさらに劣化した可能性がある。

---

## 1. Phase Y-4 タスク全体

### タスク 1: 1 問で完全 schema first-light

303 を例に、`v9.2.0-COMPLETE-JSON-SCHEMA.md` に基づいて basis / part_c / chapter / section を補完する。
render.py で生成し、ブラウザで目視確認できる完璧な HTML が出ることを検証。

### タスク 2: 私 (user) によるレビュー gate

完成した 303.html を user に共有 → 313.html と比較レビュー → 品質確認 → 次タスクへの判断。

### タスク 3 (gate 通過後): 304-307 + 316 への展開

同じパターンで残り 5 ファイルの JSON を補完。

### タスク 4: night-batch-runner 改修方針確定

PDF → JSON 起草プロンプトを `v9.2.0-COMPLETE-JSON-SCHEMA.md` に準拠させる方針確定。

**本指示書ではタスク 1 + 2 のみ実施**。タスク 3-4 は user 判断後に別指示。

---

## 2. タスク 1 詳細: 303 の JSON 補完 + first-light

### 2.1 事前確認

```powershell
cd C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam

# HEAD 確認（b605784 機能等価のはず）
git log --oneline -3

# 303.json の現状確認
python -c "import json; d=json.load(open('problems/303.json',encoding='utf-8')); print('keys:', list(d.keys())); print('total:', len(d))"

# 既存 HTML の現状確認（PART C が空のはず）
python scripts\render.py 303
$html = "outputs\tx\刑TX\刑TX303.html"
$cnt = (Select-String -Path $html -Pattern '<!-- TODO' -AllMatches).Matches.Count
Write-Host "TODO stubs: $cnt (期待: 7 PART C + 1 basis = 8)"
```

### 2.2 補完作業（CC の本作業）

`problems/303.json` を以下の手順で更新：

#### Step 1: 既存 303.json を読み込む
- 23 keys を保持

#### Step 2: 補完 keys を追加
- `chapter`: PDF または既存解説から章名を確定（例: "第7章 詐欺罪"）
- `section`: 節名（例: "第2節 詐欺罪の要件"）
- `basis.cards[]`: 既存 case フィールド + 解説中の判例・条文をすべて抽出して構造化
- `part_c`: 既存 JSON の以下フィールドを基に 7 サブセクションを起草
  - `crime` / `answer_explanation` → C-1 summary_html
  - `theory_deep_dive` → C-4 doctrines
  - `choices[*].professor` → C-1 footer_note / C-7 layers の材料
  - `drill_blocks` → C-6 related items の材料
  - `mindmap_tree` / `mindmap_radial` → C-1 table / C-7 layers の材料

#### Step 3: ref-case リンクを各本文に挿入
- `basis.cards[]` の `id` と一致させる
- 例: `<a class="ref-case" href="#case-saiko-h13-7-29">最判平13.7.29</a>`

#### Step 4: render → validate → 目視
```powershell
python scripts\render.py 303
python scripts\validate-tx.py outputs\tx\刑TX\刑TX303.html
```

#### Step 5: STOP-for-review
**ここで一旦 commit せず、user に報告**。HTML を user がブラウザで開いて以下を確認：
- C-1〜C-7 すべて中身があるか
- ref-case リンクが機能しているか
- 配色が override_pattern (P1) に従っているか
- 313.html と同等の品質か
- 不足項目があれば再起草

### 2.3 起草で迷ったときの参考ファイル

| 参考 | 場所 | 内容 |
|---|---|---|
| 完全 schema | (本指示書と同送付の `v9.2.0-COMPLETE-JSON-SCHEMA.md`) | フィールド一覧と例 |
| baseline 実例 | (user が手元保有・必要なら user に提供依頼) `刑TX313.html` | 完璧な品質の HTML |
| spec | `spec/tx-v9.2.0-deepdive-core.md` | v9.2.0 仕様詳細 |
| render.py | `scripts/render.py` | 関数 render_basis (L380) / render_c1〜c7 (L2064-2270) |

---

## 3. STOP 条件（即報告）

以下に該当した場合は commit せず即報告：

| 条件 | 報告内容 |
|---|---|
| 既存 303.json の choices[*].professor フィールド構造が schema と乖離 | 何が違うか具体的に |
| basis.cards[] の判例引用元情報が PDF に不足 | どの判例の何情報が不足か |
| validate-tx で ERROR が出る | エラー番号と内容 |
| render 後の HTML サイズが 100KB 未満 | おそらく重大欠落あり |
| 起草 30 分以上経過したが進捗 50% 未満 | 残作業見積もりと user 判断要求 |

---

## 4. 完了報告フォーマット

```
## Phase Y-4 タスク 1 完了報告

### 303.json 補完結果
- 補完前 keys: 23
- 補完後 keys: N
- 追加 keys: [chapter, section, basis, part_c, ...]

### 補完サイズ (bytes)
- 補完前 303.json: X bytes
- 補完後 303.json: Y bytes
- 差分: +Z bytes

### basis.cards[] 起草内容
- statute: N 件 [law-247, ...]
- case: N 件 [case-saiko-..., ...]

### part_c 起草サマリ
- C-1 systematic: 起草済 (table N rows)
- C-2 comparison: 起草済 (N tables)
- C-3 connections: 起草済 (N cross-cards)
- C-4 doctrines: 起草済 (N topics)
- C-5 flowchart: 起草済 (figure svg / rules N items)
- C-6 related_problems: 起草済 (trends N / related N)
- C-7 three_layer_memory: 起草済 (N layers)

### render 結果
- HTML サイズ: NNN,NNN bytes
- validate-tx: ERROR 0 / WARNING N
- :root{} count: 2 (正常)
- ref-case リンク数: N
- TODO stub 残数: 0 (期待)

### commit
未実施（user STOP-for-review 待ち）

### 確認依頼事項
- 303.html を user にスクショ共有
- 313.html と並べて品質比較してください
- 不足項目 / 過剰項目があれば指摘してください
```

---

## END OF PHASE Y-4 指示書
