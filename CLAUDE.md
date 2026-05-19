# bar-exam プロジェクト指示書

> 司法試験・予備試験対策の HTML 教材自動生成プロジェクト。
> 短答式（TX）と論文・事例式（JX）の 2 シリーズを単一プロジェクトから運用する。

---

## §1. プロジェクトの全体像

### 2 つのシリーズ

| シリーズ | 内容 | 仕様書 | ファイル数の目安 |
|---|---|---|---|
| **TX** | 短答式（5択・○×・組合せ）の単問解説 HTML | `spec/tx-v8.11.7-core.md` | 1 問 = 1 HTML（約 110〜130 KB） |
| **JX** | 事例問題型（論文・予備）の総合教材 HTML | `spec/jx-v3.2-master.md` | 1 問 = 1 HTML（A〜H 8 サブ＋第 3〜5 部） |

### 7 科目共通

刑法／憲法／民法／商法／民訴／刑訴／行政法。出力先は科目別サブフォルダ（後述）。

---

## §2. ファイル命名規則（TX も JX も同形式）

### 2-1. 出力ファイル名フォーマット

```
{日本語科目接頭辞}{TX|JX}{3桁0埋め数字}.html
```

### 2-2. 接頭辞・出力先対応表

| 科目 | TX 接頭辞 | TX 出力先 | JX 接頭辞 | JX 出力先 |
|---|---|---|---|---|
| 刑法 | `刑TX` | `outputs/tx/刑TX/` | `刑JX` | `outputs/jx/刑JX/` |
| 憲法 | `憲TX` | `outputs/tx/憲TX/` | `憲JX` | `outputs/jx/憲JX/` |
| 民法 | `民TX` | `outputs/tx/民TX/` | `民JX` | `outputs/jx/民JX/` |
| 商法 | `商TX` | `outputs/tx/商TX/` | `商JX` | `outputs/jx/商JX/` |
| 民訴 | `民訴TX` | `outputs/tx/民訴TX/` | `民訴JX` | `outputs/jx/民訴JX/` |
| 刑訴 | `刑訴TX` | `outputs/tx/刑訴TX/` | `刑訴JX` | `outputs/jx/刑訴JX/` |
| 行政法 | `行政TX` | `outputs/tx/行政TX/` | `行政JX` | `outputs/jx/行政JX/` |

> **注：** JX v3.2 仕様書の第5-1表（科目アンカーパレット）は内部的に「行JX」表記だが、本プロジェクトではファイル名・フォルダ名は **TX と対称な「行政JX」** を採用する（ユーザー指示）。パレット適用時のみ仕様書「行JX」の `--accent:#425B80`／`--mid:#78B9C6`（行政科目のアンカー）を使用する。

### 2-3. PDF ファイル名からの番号抽出ルール

両シリーズ共通：

1. PDF ファイル名から **連続する数字を抽出**（最初に出現するもの）
2. 3 桁未満は前ゼロで 0 埋め（`1` → `001`、`22` → `022`、`299` → `299`）
3. 3 桁を超える場合はそのまま使用（`1234` → `1234`）
4. 複数の数字グループがあれば最初のまとまりを採用（`K310-2024-problem.pdf` → `310`）
5. 数字が抽出できない場合は **処理を中断** し、ユーザーに番号を確認する（無断推定禁止）

### 2-4. 命名例（実運用）

| 入力 PDF | 科目 | シリーズ | 出力 |
|---|---|---|---|
| `inputs/tx-pdfs/299.pdf` | 刑法 | TX | `outputs/tx/刑TX/刑TX299.html` |
| `inputs/jx-pdfs/15.pdf` | 民法 | JX | `outputs/jx/民JX/民JX015.html` |
| `inputs/tx-pdfs/予備R1-16詐欺.pdf` | 刑法 | TX | `outputs/tx/刑TX/刑TX001.html`（※最初の連続数字「1」を採用） |
| `inputs/jx-pdfs/kenpo-question-05.pdf` | 憲法 | JX | `outputs/jx/憲JX/憲JX005.html` |
| `inputs/tx-pdfs/民訴.pdf`（数字なし） | 民訴 | TX | **処理中断 → 番号確認** |

---

## §3. TX シリーズの運用

### 3-1. 必読ファイル

- **規律本体**：`spec/tx-v8.11.7-core.md`（§0〜§37 全規律 + §Annex A/B/C 埋込／自己完結・約 6100 行）
- **参考実装例**：`canonical/KTX301.html`（構造の完成形を確認するための **参考のみ**。本文・解説・判例引用の文字列をコピーする対象**ではない**）

### 3-2. 新規 TX 生成手順

1. 問題 PDF を読解（`inputs/tx-pdfs/` 配下）
2. **冒頭応答必須**：「正答率 __%→パターン_『___』適用」を最初に出力
3. `spec/tx-v8.11.7-core.md` を view（規律・Annex A/B/C 全文確認）
4. **§0-tri ゼロベース再構築プロトコル**（6 ステップ）を順次実行
5. **§0-quad コンテンツ独立性プロトコル**（7 ステップ）を必ず履行（§3-3 で詳述）
6. **§0-bis AI 15 ステップ生成プロトコル**を順次実行
7. **§1-bis 命名規則**に従ってファイル名・出力先を決定（§2 参照）
8. 配信前に `python scripts/validate-tx.py <出力ファイル>` を実行
9. **S1〜S82 全件通過**を確認してから `present_files`

### 3-3. canonical text leakage の防止（最重要）

**問題：** Claude Code で `spec/tx-v8.11.7-core.md` を投入すると、§Annex B body skeleton 内に byte-level 埋込された KTX301 の問題固有テキスト（詐欺罪論点・最判昭28.5.8 等の特定判例引用）が、別問題の生成時にそのまま流用される事故が起きる。

**対策：** 仕様書の §0-quad を最優先で履行する。要点：

1. **逐語コピー対象（structural shell only）：** タグ名・class 名・id 名・属性キー・ネスト順序・CSS 全規則・JS 全規則・marker-legend 凡例本文・PART タイトル・sec-nav 航行ラベル・sec-icon
2. **完全新規執筆対象（problem-specific content）：** `.problem-text` 本文／`data-explanation` 値／各 `.sub-card` 本文／`.basis-card-body` の本文／PART C 全本文／PART D drill-block 本文／footer-spec 問題情報行
3. **手順：** §Annex B をクローンしたら**まず本文を空文字列で初期化**し、その後に問題 PDF だけを参照して本文を新規執筆する。§Annex B 元テキストを参照しながら執筆してはならない
4. **検証：** `validate-tx.py` の S78（KTX301 由来文言ブラックリスト検査）と S79（§Annex B 元テキストとの 3 単語以上一致検出）で機械的に検出

### 3-4. 既存 TX のアップグレード（v8.11.7 統合版）

旧バージョン（v8.10.2 以下、または v8.11.x 系の旧 minor）のファイルを v8.11.7 に揃える場合：

1. `spec/tx-v8.11.7-core.md` の **§0-tri STEP 1（既存スタイル完全破棄）** を最優先実行
2. **§34-bis 12 ステップ移行手順**で v8.11.0 canonical 化
3. その後、現バージョンから v8.11.7 への段階的 minor 更新を順次適用：
   - **§34-quater**（v8.11.1 → v8.11.2）：a2-two-stage-reveal（reveal-answer-btn・answer-instruction 文言固定）
   - **§34-quinquies**（v8.11.2 → v8.11.3）：3 Type 対応（single/multi/ox-grid）
   - **§34-sexies**（v8.11.3 → v8.11.4）：spoiler-leak-eradication（PART A「N（XX）正解」消去）
   - **§34-septies**（v8.11.4 → v8.11.5）：spoiler-strong-elimination + ox-grid-fa-unification
   - **§34-octies**（v8.11.5/v8.11.6 → v8.11.6-hotfix1）：host-injection-safe（`<script>` 内 `</body>` 禁止）
   - **§34-novies**（v8.11.6-hotfix1 → v8.11.7）：命名規則 + content-independence 最終整備
4. 再度 `python scripts/validate-tx.py` で S1〜S82 全件通過確認

### 3-5. v8.11.7 統合された新規規律（最重要・自動生成時の必須遵守）

v8.11.7 では v8.11.2〜v8.11.6-hotfix1 由来の 7 機能が一括統合された。**新規 TX 生成時に最優先で履行：**

| 規律 | 由来 | 検出 | 内容 |
|---|---|---|---|
| **A-2 2 段階開示**（Stage 1 選択 → Stage 2 開示） | v8.11.2 | S71/S72 / AP-33/34 | `<p class="answer-instruction">` canonical 文言固定／`<button class="reveal-answer-btn">` 必須 |
| **3 Type 対応**（single/multi/ox-grid） | v8.11.3 | S73 / AP-35 | `data-correct-value` 形式から自動判定・`data-answer-type` 属性で分岐 |
| **spoiler-leak-eradication** | v8.11.4 | S74/S75 / AP-36/37/38 | PART A 内「N（XX）正解」消去／`data-explanation` 先頭リテラル消去／FA は正解の数字のみ |
| **spoiler-strong-elimination** | v8.11.5 | S76 / AP-39 | PART A 内 `<strong>N（XX）</strong>` 完全削除 |
| **ox-grid-fa-unification** | v8.11.5 | S76 / AP-40 | ox-grid 型 FA を `<span class="answer-num">11112</span>` 形式に統一 |
| **host-injection-safe** | v8.11.6-hotfix1 | S77 / AP-41 | `<script>` 内に `</body>` リテラル禁止（Lexia 等正規表現バグ対策） |
| **final-answer hidden 属性** | v8.11.1 原始版 | S68 / AP-30 | すべての `<div class="final-answer">` に `hidden` 必須 |

---

## §4. JX シリーズの運用

### 4-1. 必読ファイル

- **規律本体**：`spec/jx-v3.2-master.md`（第 0 項〜第 23 項＋付録 A〜C・約 1320 行・byte-level 正典）

### 4-2. JX の基本的な性質

- 1 問あたり情報量が膨大（A〜H の 8 サブセクション × 主要論点 2 件 + 第 3 部採点講評 + 第 4 部体系化 + 第 5 部完全プロファイル）
- 処理時間の目安：1〜2 時間／問
- 三層ペルソナ（法学教育者・認知心理学エディトリアル・機能的色彩設計）の統合判断
- 11 役割タイポグラフィ完全遵守（`--font-body` ほか 11 変数）
- 科目アンカー `--accent`／`--mid` は仕様書第 5-1 表から取得（**改変禁止**）。`--light`／`--base`／`--soft` は AI の創造設計

### 4-3. 新規 JX 生成手順

1. 問題 PDF を読解（`inputs/jx-pdfs/` 配下）
2. `spec/jx-v3.2-master.md` を view（仕様確認）
3. 科目判定 → 科目アンカー `--accent`／`--mid` を仕様書第 5-1 表から取得
4. 第 3 項全体構成（第 0〜5 部）に従って骨格組立
5. 第 22 項チェックリスト全項目を満たすよう実装
6. **§2 命名規則**に従ってファイル名・出力先を決定
7. 配信前に `python scripts/validate-jx.py <出力ファイル>` を実行
8. **J1〜J20 ERROR 0 件**を確認してから `present_files`

### 4-4. JX における content independence

JX には TX の §0-quad のような明示的なコンテンツ独立性プロトコルは存在しないが、JX v3.2 仕様の三層ペルソナ設計が事実上同等の原則を担う：

- 各 JX ファイルは「その問題固有の事案・論点・判例」に基づく独自設計
- 他問題の文言・判例引用・体系説明を流用してはならない
- canonical 的参考実装が存在しないため、TX のような text leakage は構造的に発生しにくいが、**他 JX ファイルからの内容流用は禁止**

---

## §5. 検証スクリプト

### 5-1. TX 検証

```bash
python scripts/validate-tx.py outputs/tx/刑TX/刑TX299.html
```

**チェック内容（S1〜S82）：**

- 構造（S1〜S51）：タグバランス／PART 構成／sub-card 構造／final-answer／feature-tag 等
- §24 readability layer（S64〜S67）：v8.11.0 で追加された 6 層と hanging-grid・font-weight
- PART 順序（S66）：A-3 が PART B 後ろ・PART C 前
- **コンテンツ独立性（S78〜S79、v8.11.1）：** KTX301 由来禁止文言ブラックリスト検査／§Annex B との 3 単語以上連続一致検出
- **命名規則（S80〜S82、v8.11.1）：** ファイル ID 形式・出力先サブフォルダ・PDF 番号抽出整合

### 5-2. JX 検証

```bash
python scripts/validate-jx.py outputs/jx/民JX/民JX015.html
```

**チェック内容（J1〜J20）：**

- 構造（J1〜J6）：lang／title／フォントリンク／11 役割変数／accent・mid／body 基本値
- v3.2 必須要素（J7〜J13）：`.key-box` 防御セレクタ／ラベル付きカード（note/warn/success/danger）／`.judgment-text`／`.para-num`／`.model-answer`／`.grading`
- レイアウト（J14〜J15）：container 1080px／doc-header 絶対配置
- 構文要素（J16〜J17）：旧第N項表記禁止／pattern 名禁止
- 部構成（J18）：第 5 部 back-refs ≥ 3
- 仕上げ（J19〜J20）：フッター励まし文言／スムーズスクロール JS

---

## §6. カスタムコマンド

| コマンド | 用途 |
|---|---|
| `/new-tx <PDFパス>` | 新規 TX ファイルを問題 PDF から生成 |
| `/new-jx <PDFパス>` | 新規 JX ファイルを問題 PDF から生成 |
| `/upgrade-tx <HTMLパス>` | 既存 TX を v8.11.1 にアップグレード |
| `/validate <HTMLパス>` | TX または JX を自動判別して検証実行（修正なし） |

詳細は `.claude/commands/` 配下の各 `*.md` を参照。

---

## §7. 絶対禁止事項

### TX・JX 共通

- **canonical/KTX301.html の本文・解説・判例引用を別問題ファイルにコピー** すること（§3-3 / AP-42）
- **`<script>...</script>` 内に `</body>` リテラル文字列を含める** こと（host アプリ Lexia の正規表現マッチで全機能死亡。代替：「`body 閉じタグ`」「`</` + `body>`」等）
- **「保守的書き換え」**（既存コードを引き継ごうとする AI の癖）
- **仕様書本文の要約**（byte-level 一致が必要な領域がある）
- ファイル名・出力先サブフォルダの **§2 規則違反**（レガシー K/MIN/KEN 等の混在禁止）

### TX 固有

#### v8.11.0 基盤の禁止事項

- A-3 共通根拠 section を PART A 内に配置（v8.11.1 以降は PART B 後ろ）
- ラベル始まり段落の bare 形式（必ず `<p class="hanging"><span class="hang-body">` 形式）
- `.basis-card-body` の `font-weight` が 600 未満
- `.ron-mark` の `display:inline-block` 化
- `<p>` 直当て `display:flex/grid`

#### v8.11.7 統合の禁止事項（最重要・新規）

- **`<div class="final-answer">` に `hidden` 属性欠落**（AP-30）
- **§22-quater-3 CSS パッチ 8 規則の欠落**（AP-31）
- **`<p class="fa-summary">` 内に「正解はN」リテラル**（AP-32）
- **`<p class="answer-instruction">` を canonical 文言から逸脱**（AP-33）
- **`<button class="reveal-answer-btn">` 欠落**（AP-34）
- **`data-answer-type` 不整合**（AP-35）
- **PART A 内「N（XX）正解」リテラル**（AP-36）
- **`data-explanation` 先頭に正解値リテラル**（AP-37）
- **FA `.answer-num-multi` に不正解の数字混入**（AP-38）
- **PART A 内 `<strong>N（XX）</strong>` 太字ネタバレ**（AP-39）
- **ox-grid 型 FA を `.answer-num-multi` 構造で表示**（AP-40・v8.11.5 で `<span class="answer-num">` に統一）

### JX 固有

- 11 役割タイポグラフィの欠落（`--font-keyword`／`--font-judgment`／`--font-note`／`--font-professor`／`--font-mono` の追加必須）
- `.key-box` 防御セレクタ三者結合の不実装
- `blockquote.statute`／`blockquote.case` の色差別化の欠落
- 第 22 項チェックリスト未履行

---

## §8. 運用上のヒント

### コマンド呼び出しは明示的に

「処理して」のような曖昧な指示は文脈で誤解釈される。**`/new-tx inputs/tx-pdfs/299.pdf`** のように明示的なパス＋スラッシュコマンドを使う。

### 1 問ずつ確実に

特に JX は処理時間が長い（1〜2 時間／問）。バッチ処理よりも 1 問完成 → 検証通過 → 次の問題、の単発運用が安定。

### 検証失敗時の挙動

- TX：S1〜S82 のうち ERROR があれば該当箇所を修正、再検証。WARNING は配信可（必要に応じて修正）
- JX：J1〜J20 のうち ERROR があれば該当箇所を修正、再検証
- 何度も失敗する場合：仕様書該当節を読み直す → §0-tri STEP 1 から再構築

### 通信を日本語で

ユーザーへの応答は日本語で簡潔に。確認の取りすぎは禁物（ユーザーは中断を嫌う）。判断に迷う場合のみ確認する。
