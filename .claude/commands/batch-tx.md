---
description: 5 問バッチで TX を連続生成（new-tx の active 規律を継承。_lex は v13.1.0 LOOP-CARD＝GENESIS-CARD baseline）
---

# batch-tx：5 問バッチ生成コマンド

> **active＝v13.1.0 LOOP-CARD（2026-07-03）**：`_lex` の新規生成は `new-tx` の v13 経路を継承する
> （唯一起点＝`canonical/GENESIS-CARD.html`＋`spec/tx-v13.1.0-loopcard-core.md`）。既存 v12 資産の保守は
> `GENESIS-CORE`。まず `docs/canonical-lineage.md` の active 行を確認する。

## 概要

`inputs/000_TX/{科目}/` 配下の PDF を 5 問単位で連続生成する。
`.claude/commands/new-tx.md` の **active v13.1.0 LOOP-CARD の全規律**
（唯一起点＝`canonical/GENESIS-CARD.html`＋`canonical/GENESIS-CARD.placeholder.html` スロット契約・
二系統出力・配色 V3 大前提のみ (11 パレット・`--base` 固定クリーム) + SVG 重なり機械検査）を
そのまま継承し、5 問ループで実行する。**版・起点は固定記憶でなく `docs/canonical-lineage.md` の
active 行で確定する。**

## 引数

`$ARGUMENTS`：開始 PDF 番号（例：`312`）または PDF ファイルパス
（例：`inputs/000_TX/001_刑法/312.pdf`）。
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
起点：canonical/GENESIS-CARD.html（active v13.1.0 LOOP-CARD・placeholder スロット・二系統）
配色：大前提のみ V3（正答率帯 → P1/P2/P3、11 パレット AI 選定）／--base 固定クリーム #F7F1E9
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
- **Phase 3** canonical/GENESIS-CARD.html を複製 → `canonical/GENESIS-CARD.placeholder.html` の
  スロットだけを本問固有に埋める（CSS/JS/class/DOM/節順は固定・接ぎ木禁止・例外は配色パレット）
- **Phase 4** v13.1.0 の中身を鋳造（正誤表＝印付き原文 `data-brief-mark`＋法理コア＋成績エンジン／
  体系マップ SVG＝記述札に ✍規範核バッジ `.nb-badge`・`▼本問の帰結`箱は置かない／横断3軸マトリクス／
  記述カード＝統合解説＋📚BASIS＋⚠️横串trap＋🗝記憶のフック＋相互リンク往復／物語解説は `_lex` のみ。
  v13m 執筆規約＝`docs/tx-v12.2.1-inline-lock.md` §v13m）
- **Phase 4h** 二系統出力：公式（`outputs/000_TX`・本物の5択）＋ `_lex`（`outputs/ux/000_TX`・ox-grid＋解法ナビ）の2ファイルに分離（new-tx Phase 4h 参照・解法ナビは `canonical/SOLVE-NAV.html` 逐語）
- **Phase 5** SVG 重なり機械検査（体系マップの bounding box AABB 全ペア衝突判定）
- **Phase 6** 検証（`scripts/validate-tx-core.py` を**両ファイル**に実行し G1〜G45＋**G50**（G51〜G55 ERROR）通過確認・
  `_lex`=ox-grid／公式=single/multi）＋`scripts/check-tx-lex-engine.py`（G41/G50〜G54）＋`scripts/check-duplicates.py outputs` と配信
- **Phase 7** git コミットで永続化（必須）：検証通過後、**公式と `_lex` の2ファイル**を
  `git add`（`outputs/000_TX/{科目TX}/{ファイル名}.html` ＋ `outputs/ux/000_TX/{科目TX}/{ファイル名}_lex.html`）
  → **本問単位で commit** → `git push`（本線 master へ集約・§8/§9）。
  生成＝コミットで GitHub に永続化。**各問完了ごとに即 commit/push**
  （バッチ途中で中断してもコンテナ回収による HTML ロストを防ぐ）。

### 各問完了時の内部記録

各問完了時に以下を内部記録（メモリに保持・最終レポートで出力）：

- `pdf_number`, `start_time`, `end_time`, `duration_minutes`
- `output_path`, `output_size_kb`
- `validate_errors`, `validate_warnings`（validate-tx-core.py の G1〜G45＋G50・check-tx-lex-engine）
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
失敗問の再生成方法： /new-tx inputs/000_TX/001_刑法/{番号}.pdf
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

## v13.1.0 LOOP-CARD 鉄則（new-tx から継承）

- **唯一許可される skeleton 起点**：`canonical/GENESIS-CARD.html`（＋`.placeholder.html` スロット契約）。
  スロットだけ本問固有に埋める（CSS/JS/class/DOM/節順/SVG エンジンは固定・接ぎ木禁止・例外は配色パレット）。
- **`outputs/*/` 配下の別問題からの template 流用は絶対禁止**（同一問題の公式→_lex 複製は二系統手順で許可）
- **render.py 経路の使用禁止**
- **二系統出力は必須**（公式＋_lex を両方 push・answer 整合）。**物語解説は `_lex` の必須要素**
- **配色 V3 は大前提のみ**：正答率帯から P1/P2/P3、11 パレットから AI 選定。`--base` は固定クリーム #F7F1E9
- **Semantic exception**：✓ 緑は P2 借用、🏆 金は inline 保持
- **SVG 重なり機械検査必須**：bounding box AABB 全ペア検査
- **ヘッダー／フッター本文に配色記載禁止**：`.exam-meta` と `.footer-meta-info` から
  配色 Concept 文を除外（feature-tag のみで管理）
- **冒頭応答必須**：「正答率__%→パターン_『___』→パレット『___』」
