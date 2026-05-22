---
description: 5 問バッチで TX を連続生成（v9.1.0-mindmap・new-tx の全規律を継承）
---

# batch-tx：5 問バッチ生成コマンド

## 概要

`inputs/tx-pdfs/` 配下の PDF を 5 問単位で連続生成する。
`.claude/commands/new-tx.md` の全規律（v9.1.0-mindmap・6 段階 Write・
S84 検証・パレット連動・§0-quad コンテンツ独立性）をそのまま継承し、
5 問ループで実行する。

## 引数

`$ARGUMENTS`：開始 PDF 番号（例：`306`）または PDF ファイルパス
（例：`inputs/tx-pdfs/306.pdf`）。
未指定の場合は対象 PDF を user 確認。

---

## Phase 0：開始前確認（必須）

実行前に user へ以下を確認する。

### 0a. モード選択

選択肢を提示：

- **[1] 5×1 モード**（5 問のみ・1 時間 40 分〜2 時間 5 分）：
  開始 PDF から 5 連続生成して完全停止。次回別途指示。
- **[2] 5×2 モード**（10 問全部・3 時間 20 分〜4 時間 10 分）：
  バッチ 1 完了後、user に再起動を促し、再起動後に
  user が「バッチ 2 開始」と指示することで継続。
- **[3] キャンセル**

### 0b. 対象 PDF リスト提示

選択結果を確認後、対象 PDF リストを user へ提示してから処理開始：

```
バッチ 1 対象：306.pdf 〜 310.pdf（5 ファイル）
推定時間：1 時間 40 分〜2 時間 5 分
開始してよろしいですか？ [y/n]
```

`y` 確認後に Phase 1 へ進む。`n` の場合は中止。

---

## Phase 1〜N：5 問ループ実行

各問について `.claude/commands/new-tx.md` の Phase 0〜6 をそのまま実施：

- **Phase 0** 環境確認（outputs 既存確認・_quarantine 復活確認・template 流用経路チェック）
- **Phase 1** PDF 解析・正答率からパターン決定・冒頭応答（「正答率 __%→パターン_『___』適用」）
- **Phase 2-4** 命名（§1-bis）・コンテンツ独立性 7 ステップ（§0-quad）
- **Phase 5** の 6 段階 Write（head／HEADER+PART A／PART B／mindmap section／PART C+FA／PART D+footer）
- **Phase 6** 検証（`scripts/validate-tx.py` で S1〜S84 全件通過確認）と配信

### 各問完了時の内部記録

各問完了時に以下を内部記録（メモリに保持・最終レポートで出力）：

- `pdf_number`, `start_time`, `end_time`, `duration_minutes`
- `output_path`, `output_size_kb`
- `validate_errors`, `validate_warnings`
- `socket_error_count`, `template_leakage`
- `s84_status`, `palette`, `phase_completed`
- `status`: `SUCCESS` / `PARTIAL` / `FAILED`
- `failure_reason`

---

## エラーハンドリング

### ケース A：API socket error（生成中断）

- その問を **PARTIAL** とマーク
- `failure_reason` に `"socket error in Phase {N}"` を記録
- 中断ファイル（あれば）はそのまま残置
- 次の問へ進む（停止しない）

### ケース B：validate ERROR（生成完了したが検証失敗）

- その問を **FAILED** とマーク
- `failure_reason` に `"[S{番号}] {エラー文}"` を記録
- 出力ファイルはそのまま残置（後で再生成判断のため）
- 次の問へ進む

### ケース C：template 流用検出（self-report で発覚）

- その問を **FAILED** とマーク
- `failure_reason` に `"template leakage detected"` を記録
- 出力ファイルを `{科目}TX{N}.suspect.html` に rename
- 次の問へ進む

### ケース D：致命的エラー（PDF 読込失敗等）

- その問を **FAILED** とマーク
- 次の問へ進む

### 3 問連続失敗時：ループ強制停止

失敗が 3 問以上連続した場合、ループを停止して user に通知。
原因として API 不安定 / spec の不整合 / 環境問題を提示。
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
表形式（PDF / 状態 / 時間 / サイズ / ERROR / pattern）

【リスク警告】
- canonical text leakage: 検出件数
- socket error: 検出件数
- template 流用: 検出件数

【次のステップ】
失敗問の再生成方法： /new-tx inputs/tx-pdfs/{番号}.pdf
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
- mindmap section の体系層命名は前問と被らないよう確認
- 5 問完了時点で context 残量を概算報告（自己診断）

---

## 失敗問の自動 retry はしない

一度失敗した問は手動で `/new-tx` で再生成する設計。
理由：失敗原因の分析を user が確認できるため。
