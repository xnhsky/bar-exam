# bar-exam プロジェクト指示書

> 司法試験・予備試験対策の HTML 教材自動生成プロジェクト。
> 短答式（TX）と論文・事例式（JX）の 2 シリーズを単一プロジェクトから運用する。

---

## §1. プロジェクトの全体像

### 2 つのシリーズ

| シリーズ | 内容 | 現行仕様（正典スケルトン／骨子） | ファイル数の目安 |
|---|---|---|---|
| **TX** | 短答式（5択・○×・組合せ）の単問解説 HTML | **v11.0.0 LOOP-CORE**：`canonical/GENESIS-CORE.html`＋`GENESIS-DEEP.html`／`spec/tx-v11.0.0-core.md` | 1 問 = コア＋別冊 |
| **JX** | 事例問題型（論文・予備）の総合教材 HTML | **v4.0.0 LOOP-FOLD**：`canonical/ATHENA.html`／`spec/jx-v4.0.0-core.md`（＋基盤規律 `jx-v3.2-master.md`） | 1 問 = 1 HTML（前半コア／後半deep折りたたみ） |

> **現行版・旧版・コードネームの一覧は `docs/canonical-lineage.md`（系譜・早見表）が正典**
> （`spec/README.md` はそこへの入口）。旧 spec（TX v8.x/v9.x は `spec/legacy/`・GENESIS.html 等）は
> legacy アップグレードツールが依存するため残置するが、新規生成では現行版のみを使う。

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
| 刑法 | `刑TX` | `outputs/000_TX/001_刑法/` | `刑JX` | `outputs/001_JX/001_刑法/` |
| 憲法 | `憲TX` | `outputs/000_TX/007_憲法/` | `憲JX` | `outputs/001_JX/007_憲法/` |
| 民法 | `民TX` | `outputs/000_TX/003_民法/` | `民JX` | `outputs/001_JX/003_民法/` |
| 商法 | `商TX` | `outputs/000_TX/004_商法/` | `商JX` | `outputs/001_JX/004_商法/` |
| 民訴 | `民訴TX` | `outputs/000_TX/005_民事訴訟法/` | `民訴JX` | `outputs/001_JX/005_民事訴訟法/` |
| 刑訴 | `刑訴TX` | `outputs/000_TX/002_刑事訴訟法/` | `刑訴JX` | `outputs/001_JX/002_刑事訴訟法/` |
| 行政法 | `行政TX` | `outputs/000_TX/006_行政法/` | `行政JX` | `outputs/001_JX/006_行政法/` |

> **注：** ファイル名・フォルダ名は **TX と対称な「行政JX」** を採用する（ユーザー指示）。
> なお JX の配色は 2026-06-02 に旧・科目アンカー固定色（行政＝ネイビー等）を廃止し、**全パレット（全 15 案＋派生）から問題の雰囲気で AI 自由選定**する方式へ変更した（5 役割・pale bg + dark text は TX と共通だが 11 種に限定しない・仕様書第 5 項）。

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
| `inputs/000_TX/001_刑法/299.pdf` | 刑法 | TX | `outputs/000_TX/001_刑法/刑TX299.html` |
| `inputs/001_JX/民/15.pdf` ＋ `inputs/001_JX/民/15.txt` | 民法 | JX | `outputs/001_JX/003_民法/民JX015.html` |
| `inputs/000_TX/001_刑法/予備R1-16詐欺.pdf` | 刑法 | TX | `outputs/000_TX/001_刑法/刑TX001.html`（※最初の連続数字「1」を採用） |
| `inputs/001_JX/憲/5.pdf` ＋ `inputs/001_JX/憲/5.txt` | 憲法 | JX | `outputs/001_JX/007_憲法/憲JX005.html` |
| `inputs/000_TX/001_刑法/民訴.pdf`（数字なし） | 民訴 | TX | **処理中断 → 番号確認** |

> **JX 入力レイアウト（2026-06-06 確定）：** 問題 PDF と同番号の講義逐語を
> **科目フォルダに同居** させる ── `inputs/001_JX/{00N_科目}/NN.pdf` ＋ `inputs/001_JX/{00N_科目}/NN.txt`
> （フォルダ = `001_刑法/002_刑事訴訟法/003_民法/004_商法/005_民事訴訟法/006_行政法/007_憲法`・
> 2026-06-20 に短縮名から outputs と対称な 00N_科目 へ統一）。逐語が無い PDF は `jx-batch-runner.ps1` が
> `SKIP_NO_TRANSCRIPT` で対象外にする。TX の入力 PDF は科目フォルダ `inputs/000_TX/{00N_科目}/` 配下に置く（2026-06-20 に旧フラット `inputs/tx-pdfs/` から移行・全 PDF は現状 `001_刑法`）。
>
> **逐語の番号は「内容照合済み」前提（2026-06-07 確定・最重要）：** 講義逐語の番号は
> 元々 PDF 番号と無関係な並びだった（例：旧 `刑法_重問28.txt` の中身は実は PDF34 の問題）。
> これを **PDF の事案と内容照合して同番号へ改名**することで、`jx-batch-runner.ps1` の
> 番号一致ペアリングが初めて正しく機能する。刑法は `inputs/001_JX/001_刑法/重問PDF/NN.pdf` ＋
> `inputs/001_JX/001_刑法/講義逐語/刑法_重問逐語NN.txt`（NN は PDF と一致）に整備済み・正典は
> **`inputs/001_JX/001_刑法/逐語-PDF対応表.md`**。番号抽出は `Get-TranscriptNumber` が
> `重問(?:逐語)?\s*0*(\d+)` で `重問逐語NN`／旧 `重問NN` 双方に対応。**PDF に対応する逐語が
> 無い余り逐語は `刑法_重問_余り旧NN_{論点}.txt` 等の「数字を抽出できない名前」にして
> ペアリング対象から除外**する（数字付き旧名で残すと別 PDF と誤ペアリングする）。
> 他科目（憲/民/商/民訴/刑訴/行政）も未照合なら同手順で内容照合→改名すること。
>
> **照合ガード（新規/再生成の冒頭で必須）：** JX 生成時は冒頭で **逐語の事案と PDF の事案が
> 一致するか自己照合**し、不一致なら逐語を使わず**中断・報告**する（番号ミスの将来検知）。
>
> **逐語取り込みプロトコル（再発防止・新規科目で必須・2026-06-07 確定）：** 講義動画の
> Whisper 逐語は**動画の通し番号で命名されており、重問PDFの問題番号とは別系統**（講座は
> 教育順、PDF はテキスト順）。刑法では動画連番≠PDF番号で全面的にズレていた（原因の実証は
> `inputs/001_JX/001_刑法/逐語-PDF対応表.md` 付録）。**番号を結合キーにしてはならない。中身だけが正。**
> 新規科目の取り込みは必ず次の順で行う：
> 1. PDF を画像化して全問の事案を読解（画像PDFは pdftotext 不可・pymupdf で rasterize）。
> 2. 各逐語の中身と PDF 事案を**内容照合**し、一致した PDF 番号で `{科目}_重問逐語NN.txt` に改名。
>    識別子（登場人物 甲乙丙・罪名・金額・凶器・判例年）で突き合わせ、低信頼は「要確認」に隔離。
>    照合補助に **`python scripts/jx-match-transcripts.py --subject {科目}`**（OCR＋文字n-gram
>    TF-IDF コサイン）を使うと CONFIDENT/REVIEW/RESIDUAL/逐語欠落PDF に層別した提案
>    `_match-proposal.md` が出る（刑法で top-3=100%・CONFIDENT 69件実証）。**自動改名はせず**
>    CONFIDENT を `--apply` で改名、REVIEW/RESIDUAL は PDF 実物で人手確定（§5-4）。
> 3. **PDF に対応しない余り逐語は「数字を抽出できない名前」**（例 `{科目}_重問_余り旧NN_{論点}.txt`）
>    にして番号一致ペアリングから除外（数字付き旧名で残すと別 PDF と誤ペアリングする）。
> 4. 結果を `inputs/001_JX/{00N_科目}/逐語-PDF対応表.md`（科目別正典）に記録し来歴も残す。
> 5. **総合問題など対象外の PDF レンジは対応表に明記**（逐語欠如の誤警告を防ぐ）。

---

## §3. TX シリーズの運用

> **【最重要・2026-06-13】新規生成は v11.0.0 LOOP-CORE が active。** 正典 `spec/tx-v11.0.0-core.md`。
> 過去問を**記述（肢）単位で管理**する設計（Lexia 肢キー pool＋弱点克服帳）に合わせ、
> **PART A=ox-grid（5記述○×＋機械可読 answer-key）／PART B=記述単位／PART C・PART D（12問ドリル）廃止／
> 参考条文判例（保護法益・制度趣旨・判例濃淡）＋体系ツリー・放射マップ2枚**で構成する。
> - 唯一の起点：`canonical/GENESIS-CORE.html`（コア）／`canonical/GENESIS-DEEP.html`（別冊）。
> - コマンド：`.claude/commands/new-tx.md`（v11）。検証：`scripts/validate-tx-core.py`（G1〜G26）／
>   別冊 `scripts/validate-tx-deep.py`（D1〜D13）。深掘り別冊は `/deepen-tx` で誤答データ解禁時に後追い。
> - Lexia 連携：[[lexia-tx-statement-tracking]]。
>
> **下記 §3-1〜§3-6 は旧 v10.0.0 GOLD-SKELETON の記述で、既存197問（v10）の保守用。** 新規生成では
> v11 を使う（GENESIS.html／PART C/D／12問ドリル規律／validate-tx-gold.py は v10 legacy 専用）。

### 3-1. 必読ファイル（v10 legacy・既存197問の保守用）

- **baseline スケルトン（唯一の起点）**：`canonical/GENESIS.html`
  （刑TX311 が確定第 1 号として gold quality 到達。新規 TX はすべてここから clone）
- **配色カタログ**：`memory/reference_palette_v3.md`（11 名前付きパレット × 5 色 hex 一覧）
- **生成コマンド**：`.claude/commands/new-tx.md`（v10.0.0 GOLD-SKELETON 経路の全工程）
- **補助構造参考**：`canonical/KTX301.html`（v9.x 系の構造参考。本文流用は AP-42 違反）
- **旧 spec（read-only / 歴史的参照）**：`spec/legacy/tx-v9.2.0-deepdive-core.md`／
  `spec/legacy/tx-v9.1.0-mindmap-core.md`／`spec/legacy/tx-v9.0.0-genkei-core.md`
  （新規生成では使用しない。既存ファイルの解読補助のみ）

### 3-2. 新規 TX 生成手順（v10.0.0 GOLD-SKELETON）

詳細は `.claude/commands/new-tx.md` 参照。要約：

1. 問題 PDF を読解（`inputs/000_TX/001_刑法/` 配下）し、正答率・出題形式・テーマを抽出
2. **冒頭応答必須**：「正答率 __%→パターン_『___』適用」（P1/P2/P3 振分け）
3. パレット選定（AI 判断・問題ごとに別）→ V3 11 パレットから 1 つ選び、その 5 色を
   ベース／メイン／アクセント／サブ 1／サブ 2 へ割当て、CSS 変数 ~20 個
   （`--base`/`--accent`/`--mid`/`--soft`/`--light`/`--bg-dark` ＋派生色 10 個）を更新
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

### 3-4. 配色 V3（11 名前付きパレット・5 役割定義・2026-05-28 確定）

正答率帯から P1/P2/P3 を自動判定後、該当パターン内の **1 パレット**（名前付き）を AI 選定し、
**5 色 × 4 役割**で `:root{}` に展開する：

| 役割 | 比率 | 用途 | CSS 変数 |
|:--|:-:|:--|:--|
| ベース | 約 70% | body 背景・大面積 surface | `--base` |
| メイン | 約 25% | ヘッダー・見出し・主要 CTA | `--accent` |
| アクセント | 約 5% | badge・反対色 contrast | `--mid` |
| サブ 1 | 残 | card 枠・border | `--soft` |
| サブ 2 | 残 | 補助 surface | `--light` |

**文字色**（`--bg-dark`）：白・黒・黒寄りグレーから雰囲気に合わせて AI 判断。

| パターン | 正答率帯 | パレット候補（11 個） |
|:-:|:-:|:--|
| **P1** | ≥ 60% | Sweet Berry / Fresh Citrus / Rose Mist / Antique Pearl / Maison Blanche |
| **P2** | 40〜60% | Crystal Blue / Dusty Sage / Mint Tea / Fresh Mint |
| **P3** | < 40% | Twilight Violet / Sunset Harmony |

各パレット 5 色 hex の正典：`memory/reference_palette_v3.md`（出典 `docs/palette-v3_2.pdf`）。

**AI 判断指標（パレット選定）：**
- テーマの重さ（道徳論点／重罪 → Antique Pearl / Dusty Sage / Twilight Violet）
- 難度（易 → Rose Mist / Fresh Mint、難 → Maison Blanche / Sunset Harmony）
- 罪名イメージ（財産罪 → ピンク系、手続 → Crystal Blue、身体犯 → Sunset Harmony）
- 正解の意外性（罠多い → アクセント反対色強め、素直 → 同系統サブで統一）

**反対色アクセント規律（2026-05-28 改訂・palette 外 hex 禁止）**：`--mid` の反対色アクセントは **11 パレット内 chip から借用**（P1 → P2 越境 OK・例：Sweet Berry の `--mid` に Mint Tea chip 1 `#AAD1B0` を借用）。**palette 外の独自 dark hex（例：dark teal `#4D7882`）は禁止**。HSL 派生 darker を作る場合は **L=55-65 の mid-tone に制限**（真の dark L<40 は禁止）。text 用 dark（`--bg-dark` / `--freq-deep` 等）は L<40 可。

**Semantic exception**（palette 完全越境）：
- ✓ 緑（recall-correct）：全パレットで `#438B48` / `#7BA980` を借用
- 🏆 金（ARENA）：全パターンで `#ffd54f` / `#ffaa00` inline hex 保持

**ヘッダー／フッター本文には配色情報を書かない**：`.exam-meta` に「配色: …」「Sweet Berry」、
`.footer-meta-info` に「ベース 70% / メイン 25%」「AI 自由選定」を書かない。配色情報は
`:root{}` と footer-spec hidden feature-tag のみで管理（G8 で機械検出）。

### 3-5. SVG ボックス重なり禁止

311 で「本問の論点ボックス」が左右サブ要素と重なる事故が発生。今後は以下を厳守：

1. SVG 出力前に各 `<rect>`/`<ellipse>` の bounding box を `(x_min, x_max, y_min, y_max)` で書き出す
2. 全ペアで衝突検査（AABB intersection）
3. マージン 16px 以上確保
4. `validate-tx-gold.py` G10 が rect/ellipse の全ペア衝突を機械検出
5. 衝突発見時は **viewBox 拡張** を最優先で対応（他要素への影響ゼロ）

### 3-5-bis. PART D 12問ドリルの自己完結（2026-05-29 確定）

ユーザー指摘：見解・事例を参照する設問が 12問エリアで出ると、毎回上部 PART まで
遡らないと解けず学習が中断する。また「本問の正解は肢N」を再度問う設問は答えの暗記しか
生まず学習効果がない。今後は以下を厳守：

1. **前提ブロック `.arena-premise` を PART D 冒頭に必須**（`arena-intro` 直後・`arena-counter` 前）
   - 本問の **事案・見解・記述ア〜オ** の要点を簡潔に再掲し、12問エリアを自己完結させる
   - 構造シェルと `.arena-premise-note` 定型文は GENESIS から逐語コピー、中身は本問固有で執筆
   - `validate-tx-gold.py` G18 が存在・非空を機械検出
2. **正解再問 DRILL 禁止**：quiz-question に「本問の正解は肢N」「誤っている記述の組合せは肢N」
   等を書かない。転用可能な法理（判定基準・規範・概念）を問う設問に差し替える
   - 解説 `.quiz-answer` は正解に言及して可（禁止は設問文のみ）
   - `validate-tx-gold.py` G17 が機械検出

### 3-6. 既存 TX のアップグレード（legacy / v8.x〜v9.x 系）

v8.x〜v9.x 系の既存ファイルは `validate-tx.py`（S1〜S91）で legacy 検証を継続。
v10.0.0 GOLD-SKELETON 経路への昇格は新規生成扱いとし、PDF から baseline 311 を
起点に clone し直す（既存ファイルの段階的 minor 更新は提供しない）。

---

## §4. JX シリーズの運用

### 4-1. 必読ファイル

- **規律本体**：`spec/jx-v3.2-master.md`（第 0 項〜第 23 項＋付録 A〜C・byte-level 正典）
- **正典スケルトン（唯一の clone 起点）**：`canonical/ATHENA.html`（JX の gold 基準＝TX の
  `GENESIS` に相当。V3 自由配色＋TX フォント＋`.lecturer-advice` 4 ブロックを実装した
  刑JX001 ベースの正典）。**2026-06-06 確定：新規 JX は TX 同様、ATHENA を物理複製
  （`cp`）→ 本文を空文字列化 → 問題固有内容を部ごとに Edit で鋳造する**（構造・CSS・
  11 タイポ・5 コンポーネント・`.lecturer-advice` 骨格が必ず正典品質で揃う＝二台運用でも
  同一出力）。**構造シェルは ATHENA から逐語コピー可。ただし本文（解説・規範・あてはめ・
  判例引用・`.lecturer-advice` 中身・採点講評・用語集 等）は完全新規執筆**（§4-4・
  content independence）＝ATHENA の文章をそのまま残さない。`outputs/001_JX/*/` の**他の**
  既存 HTML を起点にすることは禁止（起点は ATHENA のみ）。

### 4-1-bis. v4 LOOP-FOLD 構造（2026-06-13・新規生成の構造はこちらが優先）

> 導き書の三層モデル（周回層／誤答修正層／深掘り層）に合わせ、JX を **v4.0.0 LOOP-FOLD**
> へ再設計した。骨子の正典は **`spec/jx-v4.0.0-core.md`**（項0〜12）。TX v11 とは意図的に
> 分岐し、**1枚もの維持・前半コア／後半deep・(A)一括生成＋物理順序再編**を採る
> （2ファイル分割 `-deep.html` は採らない。理由＝TREE/TTS 副産物が第4部に依存し deep 後追いは
> 副産物を壊すため・spec 第0項）。**`canonical/ATHENA.html` は既に v4 に再編済み**で、
> 複製すれば下記の v4 構造を自動継承する。**v3.2 の構造記述（exec-summary 等）はこの項で上書き**する。

v4 LOOP-FOLD の構造規律（ATHENA 複製で自動的に揃う・崩さない）：

1. **エグゼクティブサマリー（`#exec-summary`）は作らない**。「答えを先に見ずに構成する」導き書
   原則の構造担保＋生成コスト削減。**事案足場（本問の事案概要・登場人物図・時系列・ファクト仕分け・
   論点抽出）は前半コアに残す**（TREE の主題抽出に `#issue-extraction` が必須）。`#issue-extraction`
   は順序・優先度・配点を伏せた論点見出しリストにとどめる（結論を先出ししない）。
2. **後半 deep（第4部体系化＋第5部）は `<details id="deep-dive">` でデフォルト折りたたみ**。
   1周目は視界から外す。**折りたたみは DOM 温存が鉄則**（要素は DOM に残す＝RX/TREE/TTS 生成も
   validate-jx も DOM 走査なので無改修で動く）。
3. **模範答案＋採点講評は `<details class="reveal-answer">` で封じる**（既定クローズ・毎周
   「先に見ない」を再強制）。
4. **用語集 5-5＋略語 5-6 は deep 折りたたみの外**（`<section id="part5-ref">`・毎周クイック参照）。
5. **照合ナビ（`.collation-nav`）** を第3部 reveal 直前に置き、照合3段（①論点過不足→②規範→
   ③あてはめ事実）を A〜H へ動線づけ。**各 H 末尾に口頭骨格（`.oral-skeleton`）**（論点→条文→
   規範→結論の4点）を置き、3周目以降の口頭構成3〜5分を支える（新規要約は作らない）。
6. **xref は閉じた details 内を指してもジャンプ可**（末尾 JS が祖先 details を開いてからスクロール）。
   `@media print` で details は強制展開（紙では全文）。
7. **検証**：`python scripts/validate-jx.py <file>` が `<details id="deep-dive">` 検出で v4 と判定し
   **JC1〜JD1**（exec-summary 不在／コア→deep 順序／第4-5部の折りたたみ／模範答案 reveal／コア自己充足）を
   追加検査（当面 WARNING・新v系の安定後 ERROR 化）。`--core-only`／`--deep-only` フラグあり。
   **既存 v3.2 生成物（刑JX001 等）は v4 判定されず JC/JD 対象外＝温存**。
8. **未確定（spec 第12項）：** issue-extraction の薄め度／reveal の localStorage 保存可否ほか。
   生成時規律として G（頻出論証3層）を規範コアに絞り 3層フルを 5-4(deep)へ寄せる案は spec 第6項
   （任意・正典 ATHENA では未適用）。

### 4-2. JX の基本的な性質

- 1 問あたり情報量が膨大（A〜H の 8 サブセクション × 主要論点 2 件 + 第 3 部採点講評 + 第 4 部体系化 + 第 5 部完全プロファイル）
- 処理時間の目安：1〜2 時間／問
- 三層ペルソナ（法学教育者・認知心理学エディトリアル・機能的色彩設計）の統合判断
- 11 役割タイポグラフィ完全遵守（`--font-body` ほか 11 変数 ＋ TX 由来 `--font-impact`）。Google Fonts リンクは TX `canonical/GENESIS.html` と完全一致（2026-06-02 統一）
- **配色**：5 役割（ベース 70%／メイン 25%／アクセント 5%／サブ × 2）と「pale bg + dark text」は TX と共通。ただし **JX はパレットを 11 種に限定せず、全パレット（出典 `docs/palette-v3_2.pdf` の全 15 案・`docs/palette-v3-images/`）＋派生色から問題の雰囲気で AI が自由に選定**（複数パレット組合せ・中間派生色 OK・科目固定色なし）。可読性ガードレール（WCAG AA 4.5:1・5 系統制限・濃色背景セル内リンクは `color:#fff`）と semantic 緑／金のみ遵守。詳細は仕様書第 5 項
- **講師のアドバイス**：問題の講義逐語録（`*_文字起こし.txt` 等）が入力にある場合、`.lecturer-advice`（🎓・第13-2-bis項）に要点を整理し**該当論点・部の冒頭**に配置（逐語のまま貼らない）。新規生成・再生成とも標準工程

### 4-3. 新規 JX 生成手順

0. **入力アラインメント・チェック（必須・最初に実行）**：`python scripts/check-jx-alignment.py {科目} {番号}` で逐語を解決。`[OK]` 以外（逐語欠落・keyword 不一致＝ズレ疑い）は**生成を中断**してマニフェスト（`inputs/001_JX/transcript-map.json`）を修正（§4-5）。**重問PDFと講義逐語は番号がズレる系列がある**（刑28/29/30 は −7 ズレ）ため、同番号を無断前提にしない
1. 問題 PDF を読解（実レイアウト：`inputs/001_JX/{00N_科目}/重問PDF/{n}.pdf`）。**手順0で解決した講義逐語を必ず併読**（逐語が論点・規範・あてはめの第一次情報源）。刑法の逐語は `inputs/001_JX/001_刑法/講義逐語/刑法_重問逐語NN.txt`（内容照合で PDF と同番号に改名済み・§2 注記）。**併読の冒頭で逐語の事案と PDF の事案が一致するか自己照合**し、不一致なら使わず中断・報告する（番号ミス検知の照合ガード）
2. **§2 命名規則**でファイル名・出力先を確定 → `canonical/ATHENA.html` を出力先へ **`cp` で複製**
3. 複製直後に**本文を空文字列で初期化**（content-independence 確保・§4-4）
4. **配色**：複製した `:root{}` を更新。問題の雰囲気で全パレット（全 15 案＋派生）から AI 自由選定（科目固定色なし）。科目が `刑` で ATHENA 配色のままでよければ流用可
5. 第 3 項全体構成（第 0〜5 部）に従い、**空化した各部を Edit で問題固有内容に鋳造**。**`.lecturer-advice`（複製済み骨格）に逐語ベースの講師アドバイスを該当論点冒頭で執筆**
6. 第 22 項チェックリスト全項目を満たすよう実装
7. 配信前に `python scripts/validate-jx.py <出力ファイル>` を実行
8. **J1〜J20 ERROR 0 件**を確認してから `present_files`
9. **回収（リモート永続化・§4-5③）**：`scripts/jx-push.sh "feat(jx): {ID} を生成保存"` で add→commit→push（指数バックオフ再試行付き）
10. **処理済 PDF＋逐語 削除（§4-5②・§4-5-bis）**：`scripts/jx-cleanup-pdf.sh {科目} {番号} --commit` → 再 push（**HTML commit 済＋Drive バックアップ存在**の二重ガードを満たすときのみ削除）。バッチ（`JX` パターン）は ⑦`jx-finalize.ps1` が commit/push＋削除まで自動実行

> headless バッチ（`jx-batch-runner.ps1` ＋ `prompts/new-jx-headless.md`）も同一動線。
> ランナーが `{CANONICAL_PATH}=canonical/ATHENA.html` を注入し、プロンプトが複製→空化→鋳造する。

### 4-4. JX における content independence（2026-06-06 改訂・ATHENA 複製動線）

TX §3-3 と対称の構造的解決を採る。ATHENA 複製動線では**逐語コピー対象**と
**完全新規執筆対象**を物理的に分離する：

- **逐語コピー対象（structural shell only）**：タグ名・class 名・id 名・属性キー・
  ネスト順序・CSS 全規則・JS 全規則・`.lecturer-advice` を含む全コンポーネントの骨格・
  第 0〜5 部のシェル・`::before` 凡例（`🔑 KEY`／`🎓 講師のアドバイス`）
- **完全新規執筆対象（problem-specific content）**：`.problem-text`／各部の解説・規範・
  あてはめ・結論／判例引用／`.lecturer-advice` の `.la-lead` 見出しと本文／採点講評／
  用語集／第 5 部各カード本文。**ATHENA の本文を残してはならない**
- **手順**：複製したら**まず本文を空文字列で初期化**してから問題 PDF＋逐語を見て新規執筆。
  ATHENA の本文を参照しながら書かない
- **唯一の起点は ATHENA**。他 JX ファイルからの内容流用は禁止

### 4-5. JX パイプライン補助システム（2026-06-06 新設・正典 `docs/jx-pipeline.md`）

JX 生成の前後を固める 3 つの補助システム。詳細・使い方は **`docs/jx-pipeline.md`**。

| # | 目的 | ツール | 要点 |
|---|---|---|---|
| ① | **入力アラインメント**（PDF↔逐語のズレ検出） | `scripts/check-jx-alignment.py`＋`inputs/001_JX/transcript-map.json` | 生成前に逐語を解決。既定は同番号、ズレは overrides に明示し keyword で本文照合。`[ERROR]` なら生成中断 |
| ② | **処理済 PDF＋逐語 削除**（git 管理） | `scripts/jx-cleanup-pdf.sh`（手動 bash）／`scripts/jx-finalize.ps1`（自動 pwsh） | **HTML commit 済＋Drive バックアップ存在**の二重ガードを満たすときのみ PDF と逐語を `git rm`（履歴に残り復元可）。既定 dry-run・`--commit` で実行 |
| ③ | **回収動線**（リモートコンテナ→git push） | `scripts/jx-push.sh`／`scripts/jx-finalize.ps1`（＋`scripts/jx-retrieval-manifest.py`） | add→commit→push を1コマンド＋指数バックオフ再試行。push 後に GitHub URL 付き回収一覧を表示 |

### 4-5-bis. Drive バックアップ＋入力削除の運用（2026-06-08 確定・ユーザー指示）

TX の「抽出PDF」と同型に、**JX も入力原本（PDF＋逐語）を Drive に常在バックアップし、inputs から削除**する：

- **配置（⑥ `jx-deploy.ps1`）が入力 PDF＋逐語も Drive へバックアップ**する。配置先（科目フォルダ直下・HTML はフラット同居）：
  - HTML → `2 JX_論 文\{00N_科目}\`（従来どおりフラット）
  - **PDF → `2 JX_論 文\{00N_科目}\重問PDF\`**（新規・Drive のみ。repo ミラーは git 肥大化回避で対象外）
  - **逐語 → `2 JX_論 文\{00N_科目}\講義逐語\`**（新規・Drive のみ）
  - TTS 台本/音声 → `2 JX_論 文\A_重問耳トレ\{N 科目}\…`（従来どおり）
- **永続化＋削除（⑦ `jx-finalize.ps1`）**：HTML＋TTS を git commit/push（GitHub バックアップ）→ Drive バックアップ済みを確認してから入力 PDF＋逐語を `git rm`。
  バッチは `JX` パターンが既定で ⑦ まで通す（`-NoFinalize` で抑止）。単発手動は bash `jx-cleanup-pdf.sh {科目} {番号} --commit`。
- **Drive バックアップフォルダは全 7 科目分を作成済み**（`jx-deploy.ps1 -InitAll` でも再作成可）。
- **二重ガード**：Drive 未マウント or バックアップ未配置なら削除を HOLD（バックアップの無い消去を構造的に防止）。緊急回避は `--no-drive-check`／`-NoDriveCheck`。

- **実レイアウト（入力）**：`inputs/001_JX/{00N_科目}/重問PDF/{n}.pdf` ＋ `inputs/001_JX/{00N_科目}/講義逐語/{科目名}_重問{nn}.txt`
  （科目フォルダは 2026-06-20 に 00N_科目 へ統一。CLAUDE.md 旧記載の「同フォルダ同居・NN.txt」は実態と異なる。マニフェストが正典）。
- **既知のズレ**：刑 28/29/30 は重問PDFと講義逐語が **−7 ズレ**（内容照合で 21/22/23 が一致）。

### §4-6. RX/TREE/ARIADNE 副産物（2026-06-11 導入・2026-06-20 リモート対応）

検証 PASS 済み JX から Lexia 用の **RX 論証カード**（`outputs/ux/001_RX/`・1論点1HTML）・
**TREE 樹形図**（`outputs/ux/002_TREE/`・ARBOR 仕様）・**ARIADNE 解法ナビ**
（`outputs/ux/000_ARIADNE/`）を自動生成する（既定 ON・非致命）。

- **ローカル**：`jx-batch-runner.ps1` の ②-rx / ②-arb / ②-ariadne 段（`-SkipRx`/`-SkipArb`/`-SkipAriadne` で抑止）。
  既存 JX への後追いは `scripts/rx-arb-backfill.ps1`。
- **リモート（Claude Code on the web）**：`/new-jx` の **Phase 9** が `Agent` サブエージェントを
  RX → TREE → ARIADNE の順に起動して同じ副産物を生成する（バッチランナーの別 `claude -p` 相当）。
  **TREE は外部 arbor リポジトリ非依存の vendored モード**＝`canonical/ARBOR.html`（gold TREE 複製）を
  唯一の構造参照にし、`scripts/validate-tree.py`（T1〜T9）で検証する。永続化は `jx-push.sh` が
  `outputs/ux` も既定 stage。
- **3 種とも canonical スケルトンを複製**して鋳造する（TX/JX と同方針＝二台運用でも同一品質）：
  RX=`canonical/RX.html`／TREE=`canonical/ARBOR.html`／ARIADNE=`canonical/ARIADNE.html`。
  いずれも **TX v11 GENESIS を見本にした誌面**（ボックス・バッジ・12 役割フォント・V3 配色）。
  既存 RX の誌面アップグレードは `scripts/rx-restyle-backfill.py`（head デザインのみ差し替え・冪等）。

**詳細は `docs/rx-arb-byproducts.md` が正典**。

---

## §5. 検証スクリプト

### 5-1. TX 検証（v10.0.0 GOLD-SKELETON・新規生成用・推奨）

```bash
python scripts/validate-tx-gold.py outputs/000_TX/001_刑法/刑TX312.html
```

**チェック内容（G1〜G16）：**

- **構造（G1〜G5）：** HEAD ／HEADER ／PART A〜D ／footer-spec の存在
- **配色 V3（G6〜G8）：**
  - G6: `:root{}` 内に 5 役割 CSS 変数 (`--base`/`--accent`/`--mid`/`--soft`/`--light`/`--bg-dark`) が定義されているか
  - G7: 派生色 10 個（`--accent-darker`/`--accent-soft`/`--accent-3` 等）が定義されているか
  - G8: ヘッダー(`.exam-meta`)／フッター(`.footer-meta-info`) 表示テキストに配色 Concept 文言（パレット名・役割割合・「AI 自由選定」等）が残っていないか
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
- **SVG class 整合（G16）：**
  - G16: SVG 内 class が `<style>` 定義済み（未定義 class の黒塗り防止）
- **PART D 自己完結（G17〜G18・2026-05-29 追加）：**
  - G17: drill-block の quiz-question に「本問の正解は肢N」型の正解再問設問がない（答えの暗記は学習効果ゼロ）
  - G18: PART D に前提ブロック `.arena-premise`（見解・事案・記述の再掲）が存在し非空

### 5-2. TX 検証（legacy・v8.x〜v9.x 既存ファイル用）

```bash
python scripts/validate-tx.py outputs/000_TX/001_刑法/刑TX299.html
```

S1〜S91（version-aware）。v8.11.7／v9.0.0-genkei／v9.1.0-mindmap／v9.2.0-deepdive
各バージョン対応。新規生成では `validate-tx-gold.py` を使用し、こちらは既存
ファイルの保守確認に限定。

### 5-3. JX 検証

```bash
python scripts/validate-jx.py outputs/001_JX/003_民法/民JX015.html
```

**チェック内容（J1〜J20）：**

- 構造（J1〜J6）：lang／title／フォントリンク／11 役割変数／accent・mid／body 基本値
- v3.2 必須要素（J7〜J13）：`.key-box` 防御セレクタ／ラベル付きカード（note/warn/success/danger）／`.judgment-text`／`.para-num`／`.model-answer`／`.grading`
- レイアウト（J14〜J15）：container 1080px／doc-header 絶対配置
- 構文要素（J16〜J17）：旧第N項表記禁止／pattern 名禁止
- 部構成（J18）：第 5 部 back-refs ≥ 3
- 仕上げ（J19〜J20）：フッター励まし文言／スムーズスクロール JS

### 5-4. JX 逐語↔PDF 照合補助（番号ズレ対策・新規科目の取り込み）

```bash
python scripts/jx-match-transcripts.py --subject 刑              # 提案を _match-proposal.md に出力
python scripts/jx-match-transcripts.py --subject 刑 --validate   # 既存 重問逐語NN 命名で精度検証
python scripts/jx-match-transcripts.py --subject 刑 --apply      # CONFIDENT 層のみ git mv で改名
```

**目的：** 講義逐語の番号は動画通し番号で PDF 問題番号と別系統（CLAUDE.md §4 取り込み
プロトコル）。番号を結合キーにせず**中身で照合**して `{科目}_重問逐語NN.txt` 命名へ揃える。

**仕組み：** 重問PDF を pymupdf でラスタライズ→tesseract(jpn) OCR（`_ocr_cache/` に
キャッシュ）。ひらがな（話し言葉ノイズ）を除去し、漢字/カタカナ/英数字の**文字 n-gram
TF-IDF コサイン**で各逐語を最近傍 PDF へ競合 greedy 割当。結果を 4 層に出力：

- **CONFIDENT**：1 位かつ相対余白十分 → `--apply` で改名可
- **REVIEW**：競合・余白僅少 → PDF 実物で人手確認
- **RESIDUAL**：どの PDF にも割り当たらない逐語＝**総合問題/余り候補**（N問目以降と固定
  しきい値で決め打ちしない設計）
- **逐語欠落PDF**：逐語の付かない PDF（欠落／総合問題で対象外の可能性）

**実証（刑法）：** top-1≈96%・top-3=100%／CONFIDENT 69・REVIEW 6・RESIDUAL 3。
**自動改名はしない**（CONFIDENT のみ `--apply`）。生成時の照合ガード（冒頭で事案一致を
自己照合）が最終安全網。依存：`pymupdf pytesseract pillow scikit-learn` ＋ `tesseract-ocr-jpn`。

---

## §6. カスタムコマンド

| コマンド | 用途 |
|---|---|
| `/new-tx <PDFパス>` | 新規 TX コアを問題 PDF から生成（**v11.0.0 LOOP-CORE**：GENESIS-CORE・ox-grid・記述単位・validate-tx-core） |
| `/deepen-tx <NNN>` | 深掘り別冊 `-deep.html` を後追い生成（誤答データ解禁時・GENESIS-DEEP・validate-tx-deep） |
| `/batch-tx <番号 or PDFパス>` | 5 問バッチで連続生成（new-tx の v11 経路を継承） |
| `/rb <N-M>` | **リモートバッチ**：N番〜M番を v11 で連続生成＋各問 git commit/push で永続化（「346-350 を RB して」で起動） |
| `/new-jx <PDFパス>` | 新規 JX ファイルを問題 PDF から生成 |
| `/upgrade-tx <HTMLパス>` | 既存 TX（legacy）を v8.11.1 にアップグレード |
| `/validate <HTMLパス>` | TX または JX を自動判別して検証実行（修正なし） |

詳細は `.claude/commands/` 配下の各 `*.md` を参照。

### 6-2. 実行パターン（「パターン名で実行」運用・2026-06-06 確定）

バッチ生成は **パターン名**で呼び出す（チャットで「**JX で**」「**TX-PICK 366**」等）。
一覧・コマンド・鍵管理は **`docs/run-patterns.md`** が正典。

| パターン名 | 系統 | 動作 | 鍵 / 音声 |
|---|---|---|---|
| **TX-MARCH** | TX 連番NBR | tx-pdfs 最若番から N問（既定5）生成→検証→commit/push（GENESIS） | — |
| **TX-PICK** | TX 任意NBR | 指定番号/範囲の TX を生成（GENESIS） | — |
| **JX** | JX 生成 | inputs/001_JX 最若番から N問（既定3）JX→validate→台本→validate→配置まで（ATHENA・**音声なし**） | — |

- 実体は `scripts/patterns/{TX-MARCH,TX-PICK,JX}.ps1`（薄ラッパー）。
- **2026-06-08 統合：** 旧 JX-MAIN / JX-SUB は鍵（main/sub）区別の撤去で中身が同一になったため **`JX` 1 本に統合**。
  二台運用は各 PC で番号帯を分けて並行する（PC-A `-FromNumber 1 -ToNumber 20`／PC-B `-FromNumber 21 -ToNumber 40` 等）。
- **JX は TTS 台本生成まで。音声（wav）は自動化せず AI Studio で手動生成する**（2026-06-06 方針・課金見送りで継続）。
  台本は `outputs/002_TTS/{問題ID}/`（配置後は `…TTSファイル原本\{問題ID}\`）。これを AI Studio で音声化し
  wav を `…A_重問耳トレ\N 科目\{問題ID}\` に置く。鍵（main/sub）・Pro/Flash の区別・自動音声段(旧⑤)は撤回。
  - 理由：Gemini Pro TTS は API 無料枠が上限0（429）で課金必須・Flash は使わない方針のため。
  - 旧自動音声資産（`jx-batch-runner.ps1 ⑤` / `tts/run-tts.ps1` / `generate_tts.py`）は残置するがパターン経由では呼ばない。
- headless 起動は巨大プロンプトを **stdin パイプ**で `claude -p` に渡す（`-p 引数`渡しは PowerShell が壊す・nested 実行で顕著）。
- JX バッチは末尾 ⑥ で成果物を **Drive＋repo ミラー**へ自動配置（`scripts/jx-deploy.ps1`）。
  配置先：HTML→`2 JX_論 文\00N_科目`（フラット）／台本→`A_重問耳トレ\N 科目\TTSファイル原本\{問題ID}`／音声→`A_重問耳トレ\N 科目\{問題ID}`（台本・音声は問題IDサブフォルダ）。
  repo ミラーは `deploy\`（構造のみ git・実ファイルは `.gitignore`）。Drive は H: マウント時のみ。
  フォルダ作成は `jx-deploy.ps1 -InitAll`、配置停止は `-SkipDeploy`。

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

#### PART D 12問ドリルの前提欠如・正解再問の禁止

- **前提ブロック `.arena-premise` を省略**して 12問エリアを作らない
  （見解・事例を参照する設問が遡読を強いる事故・`validate-tx-gold.py` G18 検出）
- **quiz-question に「本問の正解は肢N」型の正解再問設問を書かない**
  （答えの暗記は学習効果ゼロ・転用可能な法理を問う設問に差し替える・G17 検出）

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

### 二台運用（owner PC / xnrg2 PC）と本線一元化（最重要・2026-06-04 確定）

このプロジェクトは 2 台の PC（OWNER PC・xnrg2 PC＝DESKTOP-5664QR6）＋複数の
Claude Code Web セッションで並行運用する。過去、各セッション／PC が**古い `master`
から別々のフィーチャーブランチを切り、`master` へ戻さない**運用をした結果、
入力 PDF（445 問）や spec（genesis v10.0.0）が「ブランチに無い＝消えた」ように
見える事故が頻発した（真因は二台すれ違いではなく**本線非更新**。二台運用は同期漏れを
増幅させる要因）。今後は以下を厳守する：

1. **本線は `master` の一本**。入力 PDF・spec・code はすべて `master` に集約する
   （HTML 成果物も 2026-06-05 から git 管理。生成＝コミットで永続化＝CLAUDE.md §9）。
2. **作業開始時：必ず本線を取得してから枝を切る**
   ```
   git checkout master && git pull origin master
   git fetch && git log --oneline origin/master -5   # 相手 PC / 別セッションの最新を確認
   git switch -c <作業ブランチ>
   ```
   古い `master` やローカルキャッシュから直接ブランチを切らない。
3. **作業終了時：本線へ戻す**（直接マージ or PR）。「ブランチを作って放置」を禁止。
   - fast-forward 可能なら `git checkout master && git merge --ff-only <作業ブランチ> && git push origin master`
4. **二台運用の鉄則**：一方の PC で push したら、もう一方の PC は**作業前に必ず `pull`**。
   両 PC とも git 識別子が同一（`xnh`）でコミットからは PC を区別できないため、
   「どっちで何をやったか」は人間側で意識する。
5. **PDF が見つからない時の最初の確認**：`git log --oneline --all -- inputs/000_TX/001_刑法/`
   と Drive「1 TX_短答 / 001_刑法 / 抽出PDF」（445 問の原本）を突き合わせる。
   原本は Drive に常在するのでデータロスではなく**ブランチ／同期の問題**である。

### コマンド呼び出しは明示的に

「処理して」のような曖昧な指示は文脈で誤解釈される。**`/new-tx inputs/000_TX/001_刑法/299.pdf`** のように明示的なパス＋スラッシュコマンドを使う。

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
canonical/GENESIS.html と inputs/000_TX/001_刑法/{NNN}.pdf のみから生成
（outputs/*.html を template として参照しない・render.py 経由禁止）。

工程：
1. baseline を対象ファイル名でコピー → 本文を空文字列で初期化
2. 正答率帯から P1/P2/P3 自動判定 → V3 11 パレットから 1 つ AI 選定 → 5 色を
   ベース/メイン/アクセント/サブ × 2 に役割割当てて :root{} 更新
3. section-by-section で Edit（各 30〜50KB 以下・1 メッセージ 50KB 超禁止）：
   - HEAD :root{} 配色 V3 適用
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
1. outputs/000_TX/{対象科目}/ に既存ファイルがあるか
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

---

## §9. HTML 成果物の永続化＝git コミット（2026-06-05 方針変更）

### なぜ git か（Drive 自動保存が破綻した経緯）

リモート実行環境（Claude Code on the web）は **ephemeral でコンテナが回収**される。
旧運用は HTML を `.gitignore` で除外し Drive MCP `create_file` で保存する設計だったが、
**`create_file` は内容をモデルがインライン出力する必要があり、250KB 級の TX-HTML は
1 問でも転送不能**（1 問読むだけで約 107K トークン）。実際に 346-350 のバッチで
Drive 自動保存が失敗した。よって **HTML も git 管理し、生成＝コミットで GitHub に
永続化**する方式へ統一した（`.gitignore` から `outputs/**/*.html` の除外を撤廃）。

### 鉄則

1. **生成・バッチで作った HTML は、検証通過後に必ず git に commit して push する**
   （TX は `new-tx` Phase 7 / `batch-tx`・`rb` は各問完了ごとに commit）。
   生成＝コミットなので、コンテナ回収でも GitHub に残り失われない。
2. **本線 `master` に集約**（§8）。作業ブランチで commit → 本線へマージ。
   ファイル名は §2 命名規則どおり（`outputs/000_TX/001_刑法/刑TX346.html` 等）。
3. **巨大 diff を避ける**：1 問ずつ commit（5 問バッチなら最大 5 commit）。
   1 コミットに数十問まとめない（push 失敗・レビュー困難の予防）。
4. **完了報告に commit 済みファイルと push 先ブランチを併記**。バッチ最終レポートでは
   `committed` 未完の問が無いか点検し、全 SUCCESS 問の GitHub 反映を保証する。

### 配布前ゲート：ファイル間の重複・ID 不整合（2026-06-13 追加）

`validate-*.py` は 1 ファイル内検査のみ。**別ファイル同士**の問題（同一 title・同一本文・
title/doc-header/footer の問題コードがファイル名と不一致＝他問からのコピペ残り）は
`scripts/check-duplicates.py` で検出する（詳細 `scripts/README.md`）。

- **push 前に必ず通す**：`python scripts/check-duplicates.py outputs`（検出時 exit 1）。
- 自動ゲート化済み：`jx-finalize.ps1`（commit 前・`-NoGate` で回避可）／
  `night-batch-runner.ps1`（バッチ後監査）。
- **既存 HTML をコピーして別番号問題を作らない**（ID 書換漏れ・本文重複の温床）。
  新規は必ず生成パイプラインで PDF・逐語から生成する。
- このゲートは Lexia 取込時の「重複誤検出」を源流で断つためのもの（Lexia 側は本文
  ハッシュ裏取りで対応済み）。

### Drive へのコピー（任意・手動）

Drive は閲覧用ミラーとして任意で使う（自動保存はしない）。必要時は GitHub から
ダウンロードして `マイドライブ / 1 TX_短答 / {00N_科目}` へ手動アップロードする。
科目フォルダ ID は `docs/drive-folders.md` 参照（接頭辞 → Folder ID）。
小さなファイル（数十 KB）に限り Drive MCP `create_file` も使えるが、TX-HTML
（250KB 級）はインライン転送不可のため Drive 自動保存には使わない。
