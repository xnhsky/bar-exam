# bar-exam プロジェクト指示書

> 司法試験・予備試験対策の HTML 教材自動生成プロジェクト。
> 短答式（TX）と論文・事例式（JX）の 2 シリーズを単一プロジェクトから運用する。

---

## §1. プロジェクトの全体像

### 2 つのシリーズ

| シリーズ | 内容 | 仕様書 | ファイル数の目安 |
|---|---|---|---|
| **TX** | 短答式（5択・○×・組合せ）の単問解説 HTML | `spec/tx-v9.1.0-mindmap-core.md` | 1 問 = 1 HTML（約 130〜180 KB） |
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

## §3. TX シリーズの運用（v10.0.0 GOLD-SKELETON・2026-05-27 確定）

### 3-1. 必読ファイル

- **baseline スケルトン（唯一の起点）**：`canonical/GENESIS.html`
  （刑TX311 が確定第 1 号として gold quality 到達。新規 TX はすべてここから clone）
- **配色カタログ**：`memory/reference_ingectar_palette.md`（P1/P2/P3 各 27 色 hex 一覧）
- **生成コマンド**：`.claude/commands/new-tx.md`（v10.0.0 GOLD-SKELETON 経路の全工程）
- **補助構造参考**：`canonical/KTX301.html`（v9.x 系の構造参考。本文流用は AP-42 違反）
- **旧 spec（read-only / 歴史的参照）**：`spec/tx-v9.2.0-deepdive-core.md`／
  `spec/tx-v9.1.0-mindmap-core.md`／`spec/tx-v9.0.0-genkei-core.md`
  （新規生成では使用しない。既存ファイルの解読補助のみ）

### 3-2. 新規 TX 生成手順（v10.0.0 GOLD-SKELETON）

詳細は `.claude/commands/new-tx.md` 参照。要約：

1. 問題 PDF を読解（`inputs/tx-pdfs/` 配下）し、正答率・出題形式・テーマを抽出
2. **冒頭応答必須**：「正答率 __%→パターン_『___』適用」（P1/P2/P3 振分け）
3. Concept 設計（AI 判断・問題ごとに別）→ ingectar-e 27 色から 15〜20 色を選定し
   CSS 変数 ~20 個（`--accent`〜`--kp-text-color` ＋派生色 10 個）へ役割割当て
4. **§2 命名規則**に従ってファイル名・出力先を確定
5. `canonical/GENESIS.html` を Read → 対象ファイル名でコピー作成
6. コピー直後に**本文を空文字列で初期化**（content-independence 確保）
7. section-by-section で内容差替（HEAD配色／HEADER／PART A〜D／SVG／footer）
8. **SVG 重なり機械検査**：rect/ellipse の bounding box を全ペア AABB 衝突判定
9. 配信前に `python scripts/validate-tx-gold.py <出力ファイル>` を実行
10. **G1〜G16 ERROR 0 件**を確認 → 視覚確認 → `present_files`

### 3-3. canonical text leakage の防止（v10.0.0 では物理的禁止で構造解決）

**v10.0.0 GOLD-SKELETON 経路の利点：** 新規 TX 生成の唯一の起点を
`canonical/GENESIS.html` に固定し、`outputs/*/` 配下からの
template 流用を物理的に禁止することで、KTX301/GENESIS 由来の本文流用を防ぐ。

**遵守事項：**

1. **逐語コピー対象（structural shell only）：** タグ名・class 名・id 名・属性キー・
   ネスト順序・CSS 全規則・JS 全規則・marker-legend 凡例本文・PART タイトル・
   sec-nav 航行ラベル・sec-icon・SVG 座標
2. **完全新規執筆対象（problem-specific content）：** `.problem-text` 本文／
   `data-explanation` 値／各 `.sub-card` 本文／`.basis-card-body` 本文／
   PART C 全本文／PART D drill-block 本文／footer-spec 1〜3 行目／SVG 内テキスト
3. **手順：** baseline を clone したら**まず本文を空文字列で初期化**してから
   問題 PDF を見て新規執筆する。baseline の本文を参照しながら執筆してはならない
4. **検証：** `validate-tx-gold.py` の G12（KTX301 由来禁止文言）・G13
   （GENESIS baseline との 5-gram 連続一致検出）で機械的に検出

### 3-4. 配色 V2（27 色 AI 自由選定）

正答率帯から P1/P2/P3 を自動判定後、各パターン 27 色から問題ごとに別 Concept を組立てる：

| パターン | 正答率帯 | テーマ名 | カタログ |
|:-:|:-:|:--|:--|
| **P1** | ≥ 60% | ピンクを使った可愛い配色 | ingectar-e Color Pickup #16 |
| **P2** | 40〜60% | グリーンを使った可愛い配色 | ingectar-e Color Pickup #22 |
| **P3** | < 40% | ロマンティックなパープル配色 | ingectar-e PURPLE |

**AI 判断指標（Concept 設計）：**
- テーマの重さ（道徳論点／重罪 → 落ち着き寄り、日常論点 → 爽やか）
- 難度（易 → 明るめ、難 → 重め）
- 罪名イメージ（財産罪 → ピンク系優先、身体犯 → 暖系、手続 → クール）
- 正解の意外性（罠多い → コントラスト強、素直 → 同系統調和）

**Semantic exception**（palette 越境を許容）：
- ✓ 緑（recall-correct）：P1/P3 採用時も P2 緑 #438B48 / #7BA980 を借用
- 🏆 金（ARENA）：全パターンで `#ffd54f` / `#ffaa00` inline hex 保持

**ヘッダー／フッター本文には配色情報を書かない**：`.exam-meta` に「配色: P1 …」、
`.footer-meta-info` に「配色 P1「…」AI 自由選定」を書かない。配色情報は
`:root{}` と footer-spec hidden feature-tag のみで管理（G8 で機械検出）。

### 3-5. SVG ボックス重なり禁止

311 で「本問の論点ボックス」が左右サブ要素と重なる事故が発生。今後は以下を厳守：

1. SVG 出力前に各 `<rect>`/`<ellipse>` の bounding box を `(x_min, x_max, y_min, y_max)` で書き出す
2. 全ペアで衝突検査（AABB intersection）
3. マージン 16px 以上確保
4. `validate-tx-gold.py` G10 が rect/ellipse の全ペア衝突を機械検出
5. 衝突発見時は **viewBox 拡張** を最優先で対応（他要素への影響ゼロ）

### 3-6. 既存 TX のアップグレード（legacy / v8.x〜v9.x 系）

v8.x〜v9.x 系の既存ファイルは `validate-tx.py`（S1〜S91）で legacy 検証を継続。
v10.0.0 GOLD-SKELETON 経路への昇格は新規生成扱いとし、PDF から baseline 311 を
起点に clone し直す（既存ファイルの段階的 minor 更新は提供しない）。

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

### 5-1. TX 検証（v10.0.0 GOLD-SKELETON・新規生成用・推奨）

```bash
python scripts/validate-tx-gold.py outputs/tx/刑TX/刑TX312.html
```

**チェック内容（G1〜G16）：**

- **構造（G1〜G5）：** HEAD ／HEADER ／PART A〜D ／footer-spec の存在
- **配色 V2（G6〜G8）：**
  - G6: `:root{}` 内に主要 CSS 変数 (`--accent`/`--mid`/`--light`/`--base`/`--soft`/`--bg-dark`) が定義されているか
  - G7: 派生色 10 個（`--accent-darker`/`--accent-soft`/`--accent-3` 等）が定義されているか
  - G8: ヘッダー(`.exam-meta`)／フッター(`.footer-meta-info`) 表示テキストに配色 Concept 文言が残っていないか
- **SVG（G9〜G11）：**
  - G9: tree-svg／radial-svg／flow-svg の 3 種すべて存在
  - G10: rect/ellipse の bounding box 全ペア衝突検査（polygon は擬陽性多発のため除外）
  - G11: viewBox 下端余白が最下端要素から 20px 以上（推奨 40px 以上）
- **content-independence（G12〜G13）：**
  - G12: KTX301 由来禁止文言の不出現
  - G13: GENESIS baseline 本文との 5-gram 連続一致なし（自身検証時はスキップ）
- **命名規則（G14〜G15）：**
  - G14: ファイル ID 形式（{接頭辞}{NNN}）と出力先サブフォルダ整合
  - G15: footer-spec feature-tag 先頭が `TX v10.0.0 GOLD-SKELETON`

### 5-2. TX 検証（legacy・v8.x〜v9.x 既存ファイル用）

```bash
python scripts/validate-tx.py outputs/tx/刑TX/刑TX299.html
```

S1〜S91（version-aware）。v8.11.7／v9.0.0-genkei／v9.1.0-mindmap／v9.2.0-deepdive
各バージョン対応。新規生成では `validate-tx-gold.py` を使用し、こちらは既存
ファイルの保守確認に限定。

### 5-3. JX 検証

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
| `/new-tx <PDFパス>` | 新規 TX ファイルを問題 PDF から生成（v10.0.0 GOLD-SKELETON） |
| `/batch-tx <番号 or PDFパス>` | 5 問バッチで連続生成（v10.0.0 GOLD-SKELETON） |
| `/new-jx <PDFパス>` | 新規 JX ファイルを問題 PDF から生成 |
| `/upgrade-tx <HTMLパス>` | 既存 TX（legacy）を v8.11.1 にアップグレード |
| `/validate <HTMLパス>` | TX または JX を自動判別して検証実行（修正なし） |

詳細は `.claude/commands/` 配下の各 `*.md` を参照。

---

## §7. 絶対禁止事項

### TX・JX 共通

- **canonical/GENESIS.html および KTX301.html の本文・解説・判例引用を
  別問題ファイルにコピー** すること（§3-3 / AP-42）
- **`<script>...</script>` 内に `</body>` リテラル文字列を含める** こと（host アプリ Lexia の正規表現マッチで全機能死亡。代替：「`body 閉じタグ`」「`</` + `body>`」等）
- **「保守的書き換え」**（既存コードを引き継ごうとする AI の癖）
- ファイル名・出力先サブフォルダの **§2 規則違反**（レガシー K/MIN/KEN 等の混在禁止）

### TX 固有（v10.0.0 GOLD-SKELETON）

#### template 流用の物理的禁止（最重要）

- **`outputs/*/` 配下の既存 HTML を別問題生成の template として
  `cp` / `Read` / `Edit` の起点にすることは絶対禁止**
  - **唯一許可される起点**：`canonical/GENESIS.html`（v10.0.0 baseline）
  - 補助：`canonical/KTX301.html`（構造参考のみ・本文コピーは AP-42 違反）
  - `_quarantine*/` および非 canonical フォルダは `bar-exam-archive\` に物理排除済み
  - 既存 .html ファイル全般を「速い経路」として参照することは canonical text leakage の温床

#### render.py 経路の禁止

- **`python scripts/render.py {問題番号}` 実行禁止**：JSON-render 結果が target ファイルを
  上書きし WIP 作業全消失（過去事故あり・2026-05-27 確認）
- 新規生成は問題 PDF + canonical/GENESIS.html のみから新規鋳造

#### ヘッダー／フッター本文への配色記載禁止

- `.exam-meta` 内に「配色: P1 …」を書かない
- `.footer-meta-info` に「配色 P1「…」AI 自由選定」を書かない
- 配色情報は CSS の `:root{}` と footer-spec hidden feature-tag のみで管理
- `validate-tx-gold.py` G8 が機械検出

#### SVG ボックス重なり禁止

- 体系ツリー (`mindmap-tree`)・論点マインドマップ放射 (`mindmap-radial`)・
  C-5 総合フローチャート (`flow-svg`) の rect/ellipse の bounding box は
  全ペアで重ならないこと
- `validate-tx-gold.py` G10 が機械検出
- 衝突発見時は viewBox 拡張を最優先で対応

#### 単一巨大出力の禁止（API socket error 予防）

- **1 メッセージで 50KB 超の `Write` / `Edit` 出力は禁止**
- v10.0.0 では canonical baseline を Copy-Item で複製後、section 単位の
  Edit で内容差替する経路に統一（各 Edit 30〜50KB 以下）

#### 中断・再開時の禁則

- API socket error 等で中断した場合、**既存 outputs/*.html を
  template として参照する経路を選んではならない**
- 必ず canonical/GENESIS.html と PDF から続行
- 部分出力が失敗した場合、その section だけ再生成し、他 section は流用しない

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

- TX (v10.0.0)：G1〜G16 のうち ERROR があれば該当箇所を修正、再検証。WARNING は配信可
- TX (legacy)：S1〜S91 のうち ERROR があれば該当箇所を修正、再検証
- JX：J1〜J20 のうち ERROR があれば該当箇所を修正、再検証
- 何度も失敗する場合：canonical/GENESIS.html から clone し直して section ごとに再執筆

### 通信を日本語で

ユーザーへの応答は日本語で簡潔に。確認の取りすぎは禁物（ユーザーは中断を嫌う）。判断に迷う場合のみ確認する。

### TX 生成時の標準プロンプト雛形（v10.0.0 GOLD-SKELETON）

`/new-tx` 起動時または直接指示時に末尾に付加（短縮版）：

```
canonical/GENESIS.html と inputs/tx-pdfs/{NNN}.pdf のみから生成
（outputs/*.html を template として参照しない・render.py 経由禁止）。

工程：
1. baseline を対象ファイル名でコピー → 本文を空文字列で初期化
2. 正答率帯から P1/P2/P3 自動判定・27 色から AI 自由選定して :root{} 更新
3. section-by-section で Edit（各 30〜50KB 以下・1 メッセージ 50KB 超禁止）：
   - HEAD :root{} 配色 V2 適用
   - HEADER（exam-meta に配色記載しない）
   - PART A（出題形式に応じて single/multi/ox-grid）
   - PART B 各 choice-section
   - A-3 共通根拠（本問関連条文・判例のみ）
   - SVG 3 種（座標は baseline、テキストのみ差替）
   - PART C C-1〜C-7
   - PART D drill 12
   - footer-spec（配色記載しない・feature-tag は TX v10.0.0 GOLD-SKELETON 先頭）
4. SVG 重なり機械検査（rect/ellipse 全ペア AABB）
5. validate-tx-gold.py → G1〜G16 ERROR 0 件確認
```

### API socket error 発生時の対処

- 中断した時点でセッションを閉じず、user が「再開して」と指示
- AI には**必ず canonical/GENESIS.html と PDF から続行**させる
  （`outputs/{科目TX}/*.html` を template として参照させない）
- 失敗した section のみ再生成。完成済み他 section は流用しない
- 同じ section で 2 回連続 socket error が起きたら、その section を
  さらに細分化

### 生成時間の目安と内訳（v10.0.0 GOLD-SKELETON）

標準的な TX 1 問の所要時間：**20〜30 分**（baseline clone により仕様書 Read が
不要になり短縮）。内訳：

| 工程 | 標準時間 | 異常兆候 |
|---|---|---|
| PDF 読込 + 配色 Concept 設計 | 5〜8 分 | 10 分超 → PDF が読み取れていない可能性 |
| baseline clone + 本文空文字列初期化 | 1〜2 分 | 5 分超 → Edit 単位が大きすぎる |
| section-by-section 内容差替 | 12〜18 分 | 25 分超 → Edit 分割が機能していない |
| SVG 重なり機械検査 + validate | 2〜4 分 | 修正サイクル 3 回以上 → G12/G13 で leakage 疑い |

35 分超は異常。session log を確認し以下をチェック：
- Edit 回数（15 超で異常・section 細分化過剰の疑い）
- Bash 内 `cp outputs/...` コマンド（template 流用違反）
- Bash 内 `render.py` 呼出し（v10.0.0 で禁止）

### セッション開始時の状態確認推奨

新規 TX 生成前に以下を 1 回確認させると安全：

```
始める前に環境確認：
1. outputs/tx/{対象科目}/ に既存ファイルがあるか
2. _quarantine* や非 canonical フォルダが復活していないか
3. 直近のセッションログから「template 流用経路」が選ばれていないか
```

→ template 流用経路の再発を予防

### バッチ運用（v10.0.0 GOLD-SKELETON）

5 問単位の連続生成用に `/batch-tx` コマンドあり。
全工程は `.claude/commands/batch-tx.md` 参照。

使い方：

- `/batch-tx 312` （開始 PDF を指定）
- `/batch-tx`     （対象 PDF を確認）

Phase 0 で 5×1 / 5×2 / キャンセル を user 確認。
5×2 モードはバッチ 1 完了後に必ず `/exit` & `claude --resume` してから
「バッチ 2 開始」と指示すること（context window 保護）。

エラー時は自動継続（3 問連続失敗で停止）。
失敗問の再生成は `/new-tx` で個別実施。

**v10.0.0 推定時間**：5×1 モードで 1 時間 30 分〜2 時間（1 問あたり 20〜30 分）。
