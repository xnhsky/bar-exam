---
description: 既存 TX HTML を v8.11.1 にアップグレード
---

既存の TX ファイル（v8.10.2 以下、または v8.11.x の旧 minor）を v8.11.1 にアップグレードする。

> **🚫 v9.2.0 への upgrade パスは提供しない（§34-decies 由来）**
>
> v9.2.0 DEEP-DIVE は新規生成専用であり、v9.1.0 以下既存ファイルへのインプレース minor
> 更新パスを提供しない。理由：
> 1. §22-tree / §22-flowchart-v2 / §17-ter の新規追加で構造変更が大規模、逐次パッチは誤動作リスク
> 2. 既存 14 ファイル（KTX301 + 各科目 001 + 304）は v9.1.0/v8.11.7 で CP gate PASS=14/DIFF=1
>    を維持済、インプレース更新で CP gate 破壊リスク
> 3. 新規生成（305 番台以降）は v9.2.0 で直接生成する方が品質的・実装的に明快
>
> **例外**：何らかの事情で既存ファイルを v9.2.0 化する必要が生じた場合は、
> `spec/legacy/tx-v9.2.0-deepdive-core.md` §0-tri ゼロベース再構築プロトコルを完全に最初から実行する
> こと。逐次パッチではなく、PDF 原典からの新規生成として `/new-tx` を使う。
>
> 本コマンド `/upgrade-tx` は v8.x → v8.11.7 の minor 更新パスのみを扱う。
> v9.0.0-genkei → v9.1.0-mindmap → v9.2.0-deepdive は upgrade ではなく新規生成として処理せよ。

引数：対象 HTML ファイルのパス（例：`inputs/tx-legacy/K302.html` または `outputs/tx/刑TX/刑TX302.html`）

## 必須手順

### Phase 1: 準備

1. **規律を view**：`spec/legacy/tx-v9.0.0-genkei-core.md` を view（特に §0-tri／§0-quad／§34-bis を重点的に。GENKEI 設計により §Annex B は純骨格スケルトン）
2. **対象ファイルを view**：既存 HTML 全体を読み込み

### Phase 2: §0-tri STEP 1 ゼロベース再構築（最優先・例外なし）

3. **既存スタイル完全破棄**を最優先実行：
   - `<head>` 内のフォントリンクをすべて削除
   - `<style>` ブロック内部の全 CSS 規則を破棄（**部分マージ禁止**）
   - `<body>` 内 DOM 骨格をすべて破棄（タグ・class・id・ネスト構造）
   - `</body>` 直前 `<script>` 内の全 JS を破棄
4. **特に破棄を確実にすべき項目**：
   - 旧 `padding-left + 負 text-indent` ハンギング規則（AP-26）
   - `.ron-mark` の `display:inline-block`（AP-28）
   - `<p>` 直当て `display:flex/grid`（AP-27）
   - 旧 `#answer-feedback strong{color:#fff !important}`（K302-16）
   - 旧 inline-style innerHTML テンプレート
   - 旧 `<div class="answer-slot">`（→ `<button>` に置換）
   - レガシー接頭辞ファイル ID（`K302`／`MIN145` 等 → `刑TX302`／`民TX145` 形式に更新）

### Phase 3: §34-bis 12 ステップ移行手順

5. **STEP 2**：骨格の完全クローン
   - §Annex A 全文（CSS 約 1800 行）を `<style>` 内に逐語コピー
   - §Annex B body skeleton（A-3 は PART B 後ろ・hanging 段落構造）を逐語適用
   - §Annex C 全文（JS）を `</body>` 直前の `<script>` 内に逐語コピー
   - §Annex B-link の Google Fonts `<link>` タグを `<head>` に逐語コピー
6. **STEP 3**：コンテンツのみ抽出・流し込み（既存ファイルから）
   - 問題文／選択肢本文／正解値／既存解説／既存 basis-card 内容／PART C コンテンツ／PART D ARENA／メタ情報
   - **抽出時の禁止事項**：旧 class 名引きずり／旧 style 属性温存／旧 inline-style strong パターン温存／**ラベル始まり段落の bare 形式温存**（必ず `<p class="hanging"><span class="hang-body">` ラップ）

### Phase 4: §0-quad コンテンツ独立性プロトコル

7. **既存解説文の独立性確認**：
   - 既存ファイルに KTX301 由来文言が混入していないか確認
   - 該当があれば §0-quad-3 IQ-3 に従って書き直し
8. **§0-quad-2 ブラックリスト検査**を自己実行

### Phase 5: カラーパターン

9. **正答率からパターン判定**：≥60%→P1（追記不要）／40-60%→P2（§Annex A-bis-2 追記）／<40%→P3（§Annex A-bis-3 追記）
10. **P2/P3 の場合のみ** `:root{}` 上書きブロックを `<style>` 末尾に追記（**他のセレクタ・at-rule 追加禁止**・AP-24）

### Phase 6: メタ情報更新（§1-bis 命名規則）

11. **ファイル名を v8.11.7 形式に変換**：
    - レガシー `K302.html` → `刑TX302.html`
    - レガシー `MIN145.html` → `民TX145.html`
    - レガシー `KEN087.html` → `憲TX087.html`
    - レガシー `SYO012.html` → `商TX012.html`
    - レガシー `MINS078.html` → `民訴TX078.html`
    - レガシー `KEIS033.html` → `刑訴TX033.html`
    - レガシー `GSE092.html` → `行政TX092.html`
12. **`<title>` / `.doc-header` / footer-spec の 3 箇所**を新形式で一致させる
13. **footer-spec の feature-tag** を v9.0.0 GENKEI 用に更新（§33・15 件以上必須）：
    - `TX v9.0.0 GENKEI`
    - v9.0.0 GENKEI 由来：`genkei-skeleton`／`design-byte-lock`
    - 基盤（v8.11.0）：`ktx301-canon`／`embedded-canon`／`readability-layer`／`hanging-grid`／`basis-order-v2`／`a2-feedback-canon`／`rbchip-patched`／`k302-immune`／`p2p3-unified`／`p1-absolute`
    - v8.11.1 由来：`jp-prefix-naming`／`content-independence`
    - v8.11.x 統合：`spoiler-safe`／`multi-answer-css`／`a2-two-stage-reveal`／`a2-multi-ox-support`／`spoiler-leak-eradication`／`spoiler-strong-elimination`／`ox-grid-fa-unification`／`host-injection-safe`
14. **出力先サブフォルダ**：§1-bis-3 対応表通り（`outputs/tx/{科目TX}/` 配下）

### Phase 6.5: v8.11.2〜v8.11.6 由来の機能を順次適用（§34-quater〜§34-octies）

旧バージョンによって適用すべき STEP が変わる。**仕様書 §34-quater〜§34-octies の minor 更新ルート**を順次実行：

- 旧版が v8.10.x なら：本コマンドの Phase 1〜6（v8.11.0 まで）で完了 → 次のステップへ
- v8.11.0／v8.11.1 → v8.11.2：**§34-quater 5 ステップ**（a2-two-stage-reveal）
  - answer-instruction canonical 文言固定
  - reveal-answer-btn 挿入
  - §22-quinta CSS パッチ追加
  - handleAnswerSlot/handleRevealAnswerBtn JS 改訂
- v8.11.2 → v8.11.3：**§34-quinquies 5 ステップ**（3 Type 対応）
  - data-answer-type 属性追加
  - Type B/C の UI 構築
  - §22-sexta CSS パッチ追加
  - handleOxBtn 等 JS 改訂
- v8.11.3 → v8.11.4：**§34-sexies 5 ステップ**（spoiler-leak-eradication）
  - PART A 内「N（XX）正解」リテラル削除
  - data-explanation 先頭リテラル削除
  - FA を正解の数字のみ表示形式に変換
- v8.11.4 → v8.11.5：**§34-septies 5 ステップ**（spoiler-strong-elimination + ox-grid-fa-unification）
  - PART A 内 `<strong>N（XX）</strong>` 削除
  - ox-grid 型 FA を `<span class="answer-num">` 形式に統一
- v8.11.5/v8.11.6 → v8.11.6-hotfix1：**§34-octies 2 ステップ**（host-injection-safe）
  - `<script>` 内の `</body>` リテラルを代替表記に置換
- v8.11.6-hotfix1 → v8.11.7：**§34-novies 3 ステップ**（命名規則最終整備）

### Phase 7: 検証と配信

15. **検証実行**：
    ```bash
    python scripts/validate-tx.py <出力ファイル>
    ```
16. **S1〜S82 全件通過確認**（特に S64〜S82 を最優先）
17. **ERROR 0 件確認後**：`present_files` で完了報告
18. **ERROR があれば**：該当箇所を修正し、再検証 → 通過するまで繰り返し

## 鉄則（絶対遵守）

- **部分マージ絶対禁止**（「KTX301 構造を流用しつつ、既存ファイルの良いところも残す」は禁止）
- **§Annex A／§Annex C は byte-level 逐語コピー**
- **§Annex B は構造シェルのみ逐語**（本文は既存抽出 or 新規執筆、§0-quad 準拠）
- **canonical/KTX301.html の本文を別問題ファイルにコピー禁止**（AP-42）
- **「保守的書き換え」を絶対にしない**（大規模言語モデル特有の保守的癖を強制無効化）

$ARGUMENTS
