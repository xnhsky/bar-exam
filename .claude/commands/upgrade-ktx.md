---
description: 既存 TX ファイル（v8.10.2 以下）を v8.11.5 にアップグレード
---

既存 TX ファイル（v8.10.2 以下）を TX v8.11.6 にアップグレードする。

引数：対象 HTML ファイルのパス（例：`inputs/tx-legacy/K298.html`）

## 必須手順

### STEP 1：§0-tri ゼロベース再構築（最優先）

既存ファイルの以下を**すべて破棄**：
- `<head>` 内の Google Fonts `<link>` タグ
- `<style>` ブロック**内部の全 CSS 規則**
- 旧 PART 順序（A-3 が PART A 内にあった構造）
- 旧 A-2 feedback バグ規則：
  - `#answer-feedback strong{...color:#fff !important; ...}`
  - 旧 JS の `feedback.innerHTML = '<strong style="color:...">'`
  - `<div class="answer-slot">` を `<button class="answer-slot">` に置換
- 旧ハンギング規則：
  - `padding-left:Xem; text-indent:-Xem;`（AP-26 違反）
  - `.basis-card-body > p { display:flex/grid }`（AP-27 違反）
  - `.ron-mark { display:inline-block }`（AP-28 違反）
- `<body>` 内 DOM 骨格・全 JS

### STEP 2：コンテンツのみ抽出

既存ファイルから以下の**コンテンツ要素のみ**を抽出：
- 問題文・選択肢本文
- 正解値・解説文
- 各記述の explanation / professor sub-card 内容
- 共通根拠テキスト（条文・判例 body）
- PART C コンテンツ
- PART D 12 問
- メタ情報（doc-header / footer-spec の文字情報）

### STEP 3：canonical 化

1. `spec/legacy/tx-v8.11.6-core.md` を view（規律確認）
2. `spec/legacy/tx-v8.11.6-annex-A.css` 全文を新 `<style>` 内に逐語コピー
3. パターン判定し、P2/P3 なら対応する annex-A-bis を末尾追記
4. `spec/legacy/tx-v8.11.6-annex-B.html` の skeleton 構造に整合
5. **A-3 共通根拠 section を PART B 後ろ・PART C 前に再配置**
6. `spec/legacy/tx-v8.11.6-annex-C.js` 全文を逐語コピー
7. answer-area の data 属性 / button 化を完全適用
8. **ラベル始まり段落を `<p class="hanging"><span class="hang-body">` 化**
   - `<span class="para-num">` で始まる段落
   - `<strong>【事案】</strong>` `<strong>【判旨】</strong>` `<strong>I.</strong>` 等で始まる段落
9. `lead-list` クラスを C-5「運用上の鉄則」／C-6「出題傾向の分析」・「関連問題・参考」の `<ul>` に付与
10. footer-spec を v8.11.5 仕様に更新（必須 feature-tag 完備）

### STEP 4：検証

1. `bash python scripts/validate.py <出力ファイル>` を実行
2. ERROR 0 件確認
3. WARNING があれば内容確認・必要なら修正
4. `present_files` で配信

## 鉄則

- 既存スタイルの「部分マージ」は**絶対禁止**
- canonical コードは**バイトレベルで逐語コピー**のみ
- 「familiarity」を理由とする旧構造温存を許可しない
- 検証は AI 目視ではなく `validate.py` に完全委譲

$ARGUMENTS
