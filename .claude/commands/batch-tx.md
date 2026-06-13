---
description: 5 問バッチで TX を連続生成（v11.0.0 LOOP-CORE：GENESIS baseline + 配色 V3 + SVG 重なり検査・new-tx の全規律を継承）
---

# batch-tx：5 問バッチ生成コマンド

## 概要

`inputs/tx-pdfs/` 配下の PDF を 5 問単位で連続生成する。
`.claude/commands/new-tx.md` の全規律（v11.0.0 LOOP-CORE：
canonical/GENESIS-CORE.html からのスケルトン clone +
配色 V3 (11 名前付きパレット・5 役割定義) + SVG 重なり機械検査）をそのまま継承し、
5 問ループで実行する。

## 引数

`$ARGUMENTS`：開始 PDF 番号（例：`312`）または PDF ファイルパス
（例：`inputs/tx-pdfs/312.pdf`）。
未指定の場合は対象 PDF を user 確認。

---

## Phase 0：開始前確認（必須）

実行前に user へ以下を確認する。

### 0a. モード選択

選択肢を提示：

- **[1] 5×1 モード**（5 問のみ・推定 1 時間 30 分〜2 時間）：
  開始 PDF から 5 連続生成して完全停止。次回別途指示。
- **[2] 5×2 モード**（10 問全部・推定 3 時間〜4 時間）：
  バッチ 1 完了後、user に再起動を促し、再起動後に
  user が「バッチ 2 開始」と指示することで継続。
- **[3] キャンセル**

### 0b. 対象 PDF リスト提示

選択結果を確認後、対象 PDF リストを user へ提示してから処理開始：

```
バッチ 1 対象：312.pdf 〜 316.pdf（5 ファイル）
推定時間：1 時間 30 分〜2 時間
baseline：canonical/GENESIS-CORE.html
配色：問題ごとに正答率帯 → P1/P2/P3 自動判定、11 パレットから AI 選定（V3）
開始してよろしいですか？ [y/n]
```

`y` 確認後に Phase 1 へ進む。`n` の場合は中止。

---

## Phase 1〜N：5 問ループ実行

各問について `.claude/commands/new-tx.md` の Phase 0〜6 をそのまま実施：

- **Phase 0** 環境確認（outputs 既存確認・_quarantine 復活確認・template 流用経路チェック）
- **Phase 1** PDF 解析・正答率からパターン判定・冒頭応答
  （「正答率 __%→パターン_『___』 → 採用パレット『___』」）・11 パレットから 1 つ選定
- **Phase 2** 命名（CLAUDE.md §2）
- **Phase 3** canonical/GENESIS-CORE.html を Read → 対象ファイル名でコピー →
  本文を空文字列で初期化
- **Phase 4** section-by-section 内容差替（HEAD配色／HEADER／PART A=ox-grid 5記述○×＋answer-key／
  記述単位 PART B（choice-points 前倒し・教授①②）／参考条文判例（保護法益・制度趣旨・判例濃淡）／
  体系ツリー・放射マップ2枚／footer。**PART C・PART D は作らない**＝深掘りは別冊 `/deepen-tx`）
- **Phase 5** SVG 重なり機械検査（体系ツリー・放射マップの bounding box AABB 全ペア衝突判定）
- **Phase 6** 検証（`scripts/validate-tx-core.py` で G1〜G26 全件通過確認）と配信
- **Phase 7** git コミットで永続化（必須）：検証通過後、`outputs/tx/{科目TX}/` の
  HTML を `git add` → **本問単位で commit** → `git push`（本線 master へ集約・§8/§9）。
  生成＝コミットで GitHub に永続化。**各問完了ごとに即 commit/push**
  （バッチ途中で中断してもコンテナ回収による HTML ロストを防ぐ）。

### 各問完了時の内部記録

各問完了時に以下を内部記録（メモリに保持・最終レポートで出力）：

- `pdf_number`, `start_time`, `end_time`, `duration_minutes`
- `output_path`, `output_size_kb`
- `validate_errors`, `validate_warnings`（validate-tx-core.py の G1〜G26）
- `socket_error_count`, `template_leakage`
- `palette_pattern`（P1/P2/P3）, `concept_description`
- `svg_overlap_detected`（あれば該当 SVG と要素名）
- `phase_completed`
- `committed`（commit hash + push 成否。未 commit なら最終レポートで警告）
- `status`: `SUCCESS` / `PARTIAL` / `FAILED`
- `failure_reason`

> **バッチ終了時の確認（必須）**：最終レポートで `committed` が未完の問が
> 残っていないか点検する。コンテナ回収で HTML が消える前に、全 SUCCESS 問が
> GitHub に push 済みであることを保証する。

---

## エラーハンドリング

### ケース A：API socket error（生成中断）

- その問を **PARTIAL** とマーク
- `failure_reason` に `"socket error in Phase {N}"` を記録
- 中断ファイル（あれば）はそのまま残置
- 次の問へ進む（停止しない）

### ケース B：validate-tx-core ERROR（生成完了したが検証失敗）

- その問を **FAILED** とマーク
- `failure_reason` に `"[G{番号}] {エラー文}"` を記録
- 出力ファイルはそのまま残置（後で再生成判断のため）
- 次の問へ進む

### ケース C：template 流用検出（self-report で発覚）

- その問を **FAILED** とマーク
- `failure_reason` に `"template leakage detected"` を記録
- 出力ファイルを `{科目}TX{N}.suspect.html` に rename
- 次の問へ進む

### ケース D：SVG ボックス重なり検出

- その問を **FAILED** とマーク
- `failure_reason` に `"svg overlap in {svg-id}: {box-a} vs {box-b}"` を記録
- viewBox 拡張で自動再修正を試行（1 回のみ）
- 再修正失敗時は次の問へ進む

### ケース E：致命的エラー（PDF 読込失敗等）

- その問を **FAILED** とマーク
- 次の問へ進む

### 3 問連続失敗時：ループ強制停止

失敗が 3 問以上連続した場合、ループを停止して user に通知。
原因として API 不安定 / baseline の破損 / 環境問題を提示。
`/exit` して原因確認を推奨。

---

## Phase 最終：レポート出力

5 問完了後、以下のレポートを表示する。

```
バッチ 1 完了レポート（モード：5×{1 or 2}）
開始：開始日時
完了：完了日時
総所要時間：時間表記

【結果サマリ】
SUCCESS: N 問（番号リスト）
FAILED:  N 問（番号リスト・原因併記）
PARTIAL: N 問（番号リスト・原因併記）

【各問詳細】
表形式（PDF / 状態 / 時間 / サイズ / G-ERROR / palette / concept）

【リスク警告】
- canonical text leakage: 検出件数
- socket error: 検出件数
- template 流用: 検出件数
- SVG box overlap: 検出件数

【次のステップ】
失敗問の再生成方法： /new-tx inputs/tx-pdfs/{番号}.pdf
視覚確認推奨：ブラウザで開いて gold quality 到達を最終判定
```

### 5×2 モード選択時の追加表示

```
バッチ 1 終了。バッチ 2 への継続には：
1. このセッションを /exit で終了
2. claude --resume で再起動
3. 「バッチ 2 開始」と指示

これにより context をクリアして安定動作を保証します。
```

---

## context 管理

各問完了後、次の問へ移る前に以下を実施：

- 新しい PDF 読込時に「これは新規問題」と内部宣言
- 配色 Concept は前問と被らないよう確認（同じ P1 でも問題ごとに別 Concept）
- SVG レイアウトの座標は 311 baseline 由来だが、ラベル長によっては
  viewBox 微調整が必要なケースを記録
- 5 問完了時点で context 残量を概算報告（自己診断）

---

## 失敗問の自動 retry はしない

一度失敗した問は手動で `/new-tx` で再生成する設計。
理由：失敗原因の分析を user が確認できるため。

---

## v11.0.0 LOOP-CORE 鉄則（new-tx から継承）

- **唯一許可される skeleton 起点**：`canonical/GENESIS-CORE.html`
- **`outputs/*/` 配下からの template 流用は絶対禁止**
- **render.py 経路の使用禁止**
- **本文を空文字列で初期化してから問題 PDF を見て新規執筆**
- **配色 V3**：正答率帯から P1/P2/P3、11 パレットから AI 選定（パレット名 + 役割割当て）
- **Semantic exception**：✓ 緑は P2 借用、🏆 金は inline 保持
- **SVG 重なり機械検査必須**：bounding box AABB 全ペア検査
- **ヘッダー／フッター本文に配色記載禁止**：`.exam-meta` と `.footer-meta-info` から
  配色 Concept 文を除外（feature-tag のみで管理）
- **冒頭応答必須**：「正答率__%→パターン_『___』適用」
