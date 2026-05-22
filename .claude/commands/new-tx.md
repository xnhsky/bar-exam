---
description: 新規 TX ファイルを問題 PDF から生成（v9.1.0-mindmap + 6 段階生成）
---

新規 TX ファイル（短答式 HTML カード）を問題 PDF から生成する。

引数：問題 PDF のパス（例：`inputs/tx-pdfs/299.pdf`）

## 必須手順

### Phase 0: 環境確認（2026-05-21 追加・最優先）

0a. **outputs/tx/{対象科目}/ に既存ファイルがあるか確認**
    - 既存ファイルが存在しても **template として Read/Edit 起点にしない**
    - 同番号が既存の場合のみユーザーに上書き可否を確認

0b. **`_quarantine*` や非 canonical フォルダが復活していないか確認**
    - 復活している場合は `bar-exam-archive\` への再排除を提案

0c. **直近のセッションログから「template 流用経路」が選ばれていないか確認**
    - `Read outputs/*.html` や `cp outputs/*.html` の痕跡があれば
      §0-quad-3 IQ-2 から再執筆

### Phase 1: 準備

1. **規律を view**：`spec/tx-v9.1.0-mindmap-core.md` を view
   （§0-tri／§0-quad／§0-bis／§1-bis／§22-quad を重点的に確認。
    GENKEI 設計を継承し §Annex B は純骨格スケルトン。
    v9.1.0 で参考｜共通根拠条文・判例（旧 A-3）と論点詳細マインドマップ
    section が新規）
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

9. **IQ-1**：問題 PDF を読解後、テーマ／各選択肢の論点／関連条文・判例／出題形式を
   **AI 自身の言語**で内部メモ化（出力には含めない）
10. **IQ-2**：§Annex B body skeleton をクローンする際、本文テキスト要素
    （`.problem-text`／`data-explanation`／各 `.sub-card.*`／`.basis-card-body` 内本文／
    PART C 本文／`.drill-block` 本文／footer-spec 1〜3 行目）を**すべて空文字列で初期化**
11. **IQ-3**：執筆中、§0-quad-2 ブラックリストの語句を反射的に書こうとしている
    ことを検知したら即停止
12. **IQ-4**：各 `.sub-card.explanation` 本文を「結論→法的根拠→当てはめ→補足」の
    4 段構成で執筆。文末表現は問題ごとに変える
13. **IQ-5**：`.sub-card.professor` の 4 prof-heading は本問の論点に即した
    **新規の比喩・記憶術**を考案
14. **IQ-6**：`.basis-card` は本問に直接関係する条文・判例のみを掲載
15. **IQ-7**：出力直前に生成 HTML の本文部分に対しブラックリスト全文検査
    → 違反なら IQ-2 から再生成

### Phase 5: 6 段階 Write プロトコル（v9.1.0-mindmap・mindmap section 追加で 5→6 段階に拡張）

**1 メッセージで 50KB 超の Write/Edit は禁止。**
**`outputs/*.html` を template として参照しない**。spec と PDF のみから新規鋳造。

各段階完了時に「**Write N/6 完了・出力 XX KB・累計 YY KB**」をログ出力すること。

#### Write 1/6：`<head>` 全体 + 空 `<body>` 骨格

- §Annex B-link Google Fonts `<link>` 全文
- `<style>` 内に §Annex A canonical CSS 全文を逐語コピー
  （書き直し禁止／§24 readability layer 含む）
- P2/P3 の場合のみ `:root{}` 上書きブロックを `<style>` 末尾に追記
- `</body>` 直前の `<script>` 内に §Annex C canonical JS 全文を逐語コピー
- `<body id="top"><div class="container"></div></body>` の空骨格のみ配置
- 期待サイズ：70〜80 KB（Annex A CSS + Annex C JS 内蔵のため）

#### Write 2/6：HEADER + marker-legend + PART A + 参考｜共通根拠条文・判例

- doc-header／header-top／h1／theme-tags／exam-meta／toc-row
- marker-legend（凡例固定文言）
- PART A：A-1 problem-text（PDF 逐語）／A-2 answer-area（3 Type 対応・2 段階開示）
- 参考｜共通根拠条文・判例 section（旧 A-3／PART B 後ろ・mindmap section 前に配置・
  section id="basis" は据置）
- 期待サイズ：10〜15 KB

#### Write 3/6：PART B（記述ア〜オ 5 choice-section）

- 各 choice-section に 4 sub-card（original / explanation / basis-link / professor）
- choice-section の class odd/even 交互配置
- prof-heading 4 段構成 + key-phrase-box + analogy + warning + cross-link
- ref-stat / ref-case リンク完備
- 記述オ sec-nav の右リンクは `↓参考`（旧 `↓共通根拠`）
- 期待サイズ：40〜50 KB

#### Write 4/6：論点詳細マインドマップ section（§22-quad / v9.1.0-mindmap 新規）

仕様書 §22-quad 参照。本問の論点を「体系×記述×根拠」で統合視覚化する SVG inline section。

**設計手順（IQ-mindmap）：**
1. 本問テーマから「中心ノード」を決定（例：詐欺罪体系、窃盗罪体系）
2. 体系層 4 個を本問テーマに沿って命名
   （例：客体論 / 行為論 / 因果論 / 罪数・隣接）
3. 各記述（5 つ）をどの体系層に属するか分類
4. 各記述の核心条文 1 個 + 核心判例 1 個を quadrant に配置
5. SVG コードを §22-quad-2/3/4/5/7 規律に沿って生成

**色彩（パレット連動・P1/P2/P3 自動切替）：**
- `var(--accent)` / `--accent-soft` / `--accent-3` で CSS 変数経由
- 5 種 linearGradient：centerGrad / branchGrad / recordGrad / statuteGrad / caseGrad

**フォント（役割別 CSS 変数）：**
- 中心・体系層・記述タイトル → `var(--font-display)`
- 記述本文・サブラベル → `var(--font-body)`
- 条文 → `var(--font-statute)` / 判例 → `var(--font-judgment)`
- 凡例 → `var(--font-note)` / 正解表示 → `var(--font-impact)`

**サイズ・構造規律：**
- viewBox=`"0 0 1100 900"` 固定（C-5 フローチャートの 720×700 より縦長）
- 親要素 `<div class="figure-wrap">` 必須
- `<p class="figure-caption">` 必須
- SVG に `role="img"` + `aria-label` 属性必須
- `<script>` / `<style>` タグ禁止（host-injection-safe / AP-41）
- 完全静的（onclick/animation 禁止）
- 中心 `<ellipse>` 1 個以上 + 4 体系層の `<rect>` 4 個以上必須
- nav の前後リンク：`↑参考 / ↓C-1`

**配置：**
- 参考｜共通根拠条文・判例 section の直後・PART C の直前
- `<section class="section" id="mindmap">` で囲む

**検証：完了後 validate-tx.py が S84 を自動起動（8 検査項目）して構造検査。**

- 期待サイズ：5〜10 KB

#### Write 5/6：PART C（C-1〜C-7）+ final-answer

- C-1 体系図／C-2 図解／C-3 cross-grid／C-4 timeline／C-5 lead-list／C-6 cases／
  C-7 memory-item（3 層 priority-a/b/c）
- final-answer（必ず `hidden` 属性）+ fa-summary + answer-num (Type 別)
- C-1 sec-nav の左リンクは `↑マインドマップ`（旧 `↑共通根拠`）
- 期待サイズ：30〜40 KB

#### Write 6/6：PART D（drill 12）+ footer-spec

- PART D ARENA を 12 問・○:×=6:6 で構築（設問は本問オリジナル）
- drill-block × 12（id="d-1" 〜 "d-12"）
- footer-spec に feature-tag 18 件以上（**先頭に `TX v9.1.0 MINDMAP` 必須・S84 起動トリガ**）：
  - `TX v9.1.0 MINDMAP`／`TX v9.0.0 GENKEI`／`genkei-skeleton`／`design-byte-lock`
  - `content-independence`／`ktx301-canon`／`jp-prefix-naming`／`spoiler-safe`
  - `multi-answer-css`／`a2-two-stage-reveal`／`a2-multi-ox-support`
  - `spoiler-leak-eradication`／`spoiler-strong-elimination`／`ox-grid-fa-unification`
  - `host-injection-safe`／`readability-layer`／`hanging-grid`／`basis-order-v2`
  - `a2-feedback-canon`／`mindmap-section`（v9.1.0 新規）
- 期待サイズ：15〜20 KB

#### 中断・再開時の禁則

- 各 Write 段階が API socket error 等で失敗した場合：
  - **失敗した PART のみ再生成**（他 PART は流用）
  - **既存 `outputs/*.html` を template として参照する経路を選んではならない**
  - 必ず spec と PDF のみから続行
- 同じ section で 2 回連続 socket error が起きたら、その section を
  さらに細分化（例：PART C を C-1〜C-3 と C-4〜C-7 で 2 段階に分割）

### Phase 5.5: 3 Type 対応の自動判定（v8.11.7）

24a. **`data-correct-value` から Type 自動判定**（§17-2）：
   - `^\d+$` (1〜2 桁) → **single**
   - `^[12]{2,}$` → **ox-grid**
   - `^\d+(,\d+)+$` → **multi**

24b. **A-2 2 段階開示プロトコル**（§17-5・必須）：
   - `<p class="answer-instruction">` 文言 canonical 固定
   - `<button class="reveal-answer-btn" type="button" disabled>解答を表示</button>` 必須
   - `data-explanation` 先頭に正解値リテラルを書かない（AP-37）

24c. **FA は正解の数字のみ表示**（§22-ter / AP-38 / v8.11.5 統一）：
   - single: `<span class="answer-num">N</span>`
   - multi: `<div class="answer-num answer-num-multi">` 内に `.ans-cell.ans-correct` のみ
   - ox-grid: `<span class="answer-num">11112</span>`

24d. **PART A 内ネタバレ完全排除**（v8.11.4/5）：
   - 「N（XX）正解」リテラル禁止（AP-36）
   - `<strong>N（XX）</strong>` 太字禁止（AP-39）

24e. **すべての `<div class="final-answer">` に `hidden` 属性**（AP-30 / S68）

### Phase 6: 検証と配信

25. **検証実行**：
    ```bash
    python scripts/validate-tx.py <出力ファイル>
    ```
26. **S1〜S84 全件通過確認**（特に最優先）：
    - **S60〜S67**（v8.11.0 readability / hanging-grid / font-weight）
    - **S68〜S77**（v8.11.7 統合：spoiler-safe / 2-stage / 3-type / host-injection）
    - **S78/S79**（content-independence：KTX301 由来文言 + §Annex B 元テキスト一致検出）
    - **S80/S81/S82**（命名規則：ID 形式 / 出力先サブフォルダ / NNN 整合）
    - **S83**（placeholder 残存検査・v8.11.x 以降全般：`[...]` / `<!-- 指示: -->` 検出）
    - **S84**（mindmap section 構造検査・v9.1.0-mindmap 専用・version-aware：footer-spec の
      feature-tag に `TX v9.1.0 MINDMAP` を含むファイルのみ 8 検査項目を厳格適用）
27. **ERROR 0 件確認後**：`present_files` で完了報告
28. **ERROR があれば**：該当箇所を修正し、再検証 → 通過するまで繰り返し
    - 修正サイクル 3 回以上 → S78/S79 で leakage 疑い・Phase 4 IQ-2 から再執筆

## 鉄則（絶対遵守）

### v9.1.0-mindmap 基盤（v9.0.0-genkei から継承＋拡張）

- **§Annex A／§Annex C は byte-level 逐語コピー**（CSS／JS の書き直し禁止）
- **§Annex B は構造シェルのみ逐語**（タグ・class・id・属性キー）。**タグ内本文は完全新規執筆**
- **canonical/KTX301.html の本文・解説・判例引用を別問題ファイルにコピー禁止**（AP-42）
- **参考｜共通根拠条文・判例 section**（旧 A-3）：表示文言を新仕様に合わせる（id="basis" は据置）
- **論点詳細マインドマップ section**（§22-quad / v9.1.0 新規）：必ず参考の直後・PART C の直前に配置

### template 流用の物理的禁止（2026-05-21 追加）

- **`outputs/*/` 配下の既存 HTML を別問題生成の template として
  `cp` / `Read` / `Edit` の起点にすることは絶対禁止**
- 例外：`canonical/KTX301.html` のみ「構造参考」として `Read` 可
  （本文・解説・判例引用の文字列コピーは AP-42 違反）
- 既存 `.html` を「速い経路」として参照することは canonical text leakage の温床

### 単一巨大出力の禁止（API socket error 予防・2026-05-21 追加）

- **1 メッセージで 50KB 超の `Write` / `Edit` 出力は禁止**
- 上記 Phase 5 の 5 段階 Write プロトコルに厳格に従う
- 各段階 30〜50KB 以下に収める
- 各段階完了時に「Write N/5 完了・出力 XX KB」をログ出力

### 中断・再開時の禁則（2026-05-21 追加）

- API socket error 等で中断した場合、**既存 `outputs/*.html` を
  template として参照する経路を選んではならない**
- 必ず spec と PDF のみから新規鋳造を継続
- 失敗した PART だけ再生成し、他 PART は流用しない

### v8.11.7 統合規律

- **A-2 2 段階開示プロトコル厳守**：answer-instruction canonical 文言固定（AP-33）／
  reveal-answer-btn 必須（AP-34）
- **3 Type 対応**：data-answer-type と data-correct-value の整合（AP-35）
- **FA hidden 属性必須**（AP-30）／FA に不正解の数字混入なし（AP-38）／
  PART A 内 strong 太字禁止（AP-39）
- **`<script>...</script>` 内に `</body>` リテラル文字列禁止**（AP-41 / host-injection-safe）

### 行動原則

- **「保守的書き換え」を絶対にしない**（既存コードを引き継ごうとする AI の癖を強制無効化）
- **冒頭応答必須**：「正答率__%→パターン_『___』適用」

$ARGUMENTS
