---
description: 新規 TX ファイルを問題 PDF から生成（v8.11.1）
---

新規 TX ファイル（短答式 HTML カード）を問題 PDF から生成する。

引数：問題 PDF のパス（例：`inputs/tx-pdfs/299.pdf`）

## 必須手順

### Phase 1: 準備

1. **規律を view**：`spec/tx-v9.0.0-genkei-core.md` を view（§0-tri／§0-quad／§0-bis／§1-bis を重点的に確認。GENKEI 設計により §Annex B は純骨格スケルトン）
2. **PDF 読解**：問題番号・科目・年度・全選択肢・正解・正答率・出題テーマを抽出
3. **冒頭応答必須**：「正答率 __%→パターン_『___』適用」を最初に出力
4. **パターン判定**：正答率 ≥60%→P1 ローズシャンブル／40-60%→P2 セージブラリー／<40%→P3 ラベンダードーン

### Phase 2: ファイル名・出力先の確定（§1-bis）

5. **PDF ファイル名から番号抽出**：最初の連続数字 → 3 桁ゼロ埋め
6. **科目接頭辞・出力先決定**：
   - 刑法 → `outputs/tx/刑TX/刑TX{NNN}.html`
   - 憲法 → `outputs/tx/憲TX/憲TX{NNN}.html`
   - 民法 → `outputs/tx/民TX/民TX{NNN}.html`
   - 商法 → `outputs/tx/商TX/商TX{NNN}.html`
   - 民訴 → `outputs/tx/民訴TX/民訴TX{NNN}.html`
   - 刑訴 → `outputs/tx/刑訴TX/刑訴TX{NNN}.html`
   - 行政法 → `outputs/tx/行政TX/行政TX{NNN}.html`
7. **数字抽出不能なら処理中断** → ユーザーに番号確認

### Phase 3: §0-tri ゼロベース再構築（既存ファイル改変時のみ）

8. STEP 1（既存スタイル完全破棄）を最優先実行（新規生成時はスキップ）

### Phase 4: §0-quad コンテンツ独立性プロトコル 7 ステップ（最重要）

9. **IQ-1**：問題 PDF を読解後、テーマ／各選択肢の論点／関連条文・判例／出題形式を **AI 自身の言語**で内部メモ化（出力には含めない）
10. **IQ-2**：§Annex B body skeleton をクローンする際、本文テキスト要素（`.problem-text`／`data-explanation`／各 `.sub-card.*`／`.basis-card-body` 内本文／PART C 本文／`.drill-block` 本文／footer-spec 1〜3 行目）を **すべて空文字列で初期化**
11. **IQ-3**：執筆中、§0-quad-2 ブラックリストの語句を反射的に書こうとしていることを検知したら即停止。「詐欺罪と他罪の成否」「畏怖の一材料」「最判昭28.5.8」等の KTX301 由来文言を新規ファイルに混入させない
12. **IQ-4**：各 `.sub-card.explanation` 本文を「結論→法的根拠→当てはめ→補足」の 4 段構成で執筆。文末表現は問題ごとに変える（KTX301 の文体反復を避ける）
13. **IQ-5**：`.sub-card.professor` の 4 prof-heading は本問の論点に即した **新規の比喩・記憶術**を考案
14. **IQ-6**：`.basis-card` は本問に直接関係する条文・判例のみを掲載（KTX301 が複数判例並列だからといって機械的に踏襲しない）
15. **IQ-7**：出力直前に生成 HTML の本文部分に対しブラックリスト全文検査 → 違反なら IQ-2 から再生成

### Phase 5: §0-bis 15 ステップ生成プロトコル

16. **§Annex A canonical CSS 全文を `<style>` 内に逐語コピー**（書き直し禁止／§24 readability layer 含む）
17. **P2/P3 の場合のみ** `:root{}` 上書きブロックを `<style>` 末尾に追記
18. **§Annex B body skeleton を逐語適用**（A-3 は PART B 後ろ・hanging 段落構造含む）── **本文は §0-quad-2 で空初期化済み**
19. **コンテンツ流し込み**（IQ-3〜IQ-7 の独自執筆結果）
    - A-2 解説文は `data-explanation` 属性にプレーンテキストで格納
    - 条文・判例 body のラベル始まり段落は必ず `<p class="hanging"><span class="hang-body">` ラップ
20. **§Annex C canonical JS 全文を `</body>` 直前の `<script>` 内に逐語コピー**
21. **PART D ARENA を 12 問・○:×=6:6 で構築**（設問は本問オリジナル）
22. **§4-quater：全 section-title に sec-icon 配置**／§17-bis：PART C content wrapper 適用
23. **doc-header／title／footer-spec のファイル ID** を §1-bis-1 形式（`刑TX299` 等）で 3 箇所一致させる
24. **footer-spec の feature-tag** に以下 15 件以上を含める（§33 v9.0.0 GENKEI 版）：
    - `TX v9.0.0 GENKEI`／`genkei-skeleton`／`design-byte-lock`／`content-independence`
    - `ktx301-canon`／`jp-prefix-naming`／`spoiler-safe`／`multi-answer-css`
    - `a2-two-stage-reveal`／`a2-multi-ox-support`／`spoiler-leak-eradication`
    - `spoiler-strong-elimination`／`ox-grid-fa-unification`／`host-injection-safe`
    - `readability-layer`／`hanging-grid`／`basis-order-v2`／`a2-feedback-canon`

### Phase 5.5: 3 Type 対応の自動判定（v8.11.7）

24a. **`data-correct-value` から Type 自動判定**（§17-2）：
   - `^\d+$` (1〜2 桁) → **single**（`data-answer-type` 省略可）
   - `^[12]{2,}$` → **ox-grid**（`<div class="answer-ox-grid">` + `.ox-row` UI）
   - `^\d+(,\d+)+$` → **multi**（カンマ区切り、`<p class="selection-counter">` 追加）

24b. **A-2 2 段階開示プロトコル**（§17-5・必須）：
   - `<p class="answer-instruction">` 文言は canonical 固定（「選択肢を選んで「解答を表示」を押してください。」※ Type B/C は数字部分のみ可変）
   - `<button class="reveal-answer-btn" type="button" disabled>解答を表示</button>` 必須
   - `data-explanation` 先頭に正解値リテラルを書かない（AP-37）

24c. **FA は正解の数字のみ表示**（§22-ter / AP-38 / v8.11.5 統一）：
   - single: `<span class="answer-num">N</span>`
   - multi: `<div class="answer-num answer-num-multi">` 内に `.ans-cell.ans-correct` のみ（`.ans-incorrect` 不要）
   - ox-grid: `<span class="answer-num">11112</span>`（v8.11.5 で single 形式に統一）

24d. **PART A 内ネタバレ完全排除**（v8.11.4/5）：
   - 「N（XX）正解」リテラル禁止（AP-36）
   - `<strong>N（XX）</strong>` 太字禁止（AP-39）

24e. **すべての `<div class="final-answer">` に `hidden` 属性**（AP-30 / S68）

### Phase 6: 検証と配信

25. **検証実行**：
    ```bash
    python scripts/validate-tx.py <出力ファイル>
    ```
26. **S1〜S82 全件通過確認**（特に S60／S61／S62／S63／S64〜S67／**S68〜S77（v8.11.7 統合）／S78〜S82（命名規則・content-independence）** を最優先確認）
27. **ERROR 0 件確認後**：`present_files` で完了報告
28. **ERROR があれば**：該当箇所を修正し、再検証 → 通過するまで繰り返し

## 鉄則（絶対遵守）

- **§Annex A／§Annex C は byte-level 逐語コピー**（CSS／JS の書き直し禁止）
- **§Annex B は構造シェルのみ逐語**（タグ・class・id・属性キー）。**タグ内本文は完全新規執筆**
- **canonical/KTX301.html の本文・解説・判例引用を別問題ファイルにコピー禁止**（AP-42）
- **A-2 2 段階開示プロトコル厳守**：answer-instruction canonical 文言固定（AP-33）／reveal-answer-btn 必須（AP-34）
- **3 Type 対応**：data-answer-type と data-correct-value の整合（AP-35）
- **FA hidden 属性必須**（AP-30）／FA に不正解の数字混入なし（AP-38）／PART A 内 strong 太字禁止（AP-39）
- **`<script>...</script>` 内に `</body>` リテラル文字列禁止**（AP-41 / host-injection-safe・Lexia アプリ正規表現マッチで全機能死亡）
- **「保守的書き換え」を絶対にしない**（既存コードを引き継ごうとする AI の癖を強制無効化）
- **冒頭応答必須**：「正答率__%→パターン_『___』適用」

$ARGUMENTS
