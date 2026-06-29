---
description: 新規 TX コア（メイン）を問題 PDF から生成（v12.1.1 LOOP-CORE：GENESIS-CORE baseline + インライン肢カード + 詳説トグル + 記憶フック/答案圧縮 + 3層配色体系 + ox-grid/SM2 肢単位管理）
---

新規 TX コア HTML（短答式・周回＋誤答修正が単体で完結するメイン）を問題 PDF から生成する。

> **v12.1.1 LOOP-CORE 経路（2026-06-29 inline canon・刑TX360 を昇格、typography patch 反映）**：active 正典 `spec/tx-v12.1.0-inline-core.md`。基盤として `spec/tx-v11.0.0-core.md`（肢単位管理）と `spec/tx-v11.1.0-twotrack.md`（公式/ Lexia 二系統）を継承する。
> 過去問を**問題単位でなく記述（肢）単位で管理**する設計に対応。
> - **誌面リスキン**：明朝（Shippori Mincho B1）＋極細罫の編集デザイン（CSS 変数 `--ed-*`・`<style>` §1〜§17）。
> - **PART A は ox-grid（5記述の○×収集）＋機械可読 answer-key**（Lexia 肢キー記録の一次情報源）。
> - **Lexia 用 `_lex` の主導線は問題文直後の `.tx-inline-card`**。各肢本文、○×、条文原文、文言・趣旨・射程・切断点・転用、記憶フック、答案圧縮、詳説トグルを同じカードに置く。
> - **PART B は記述（ア〜オ）単位の詳説ソース**。SYNTHESIS 子カード（`.syn-orig`記述原文／`.syn-lead`THE GIST／`.syn-path`①②③／`.syn-image`INTUITION）＋ `.choice-points`(POINT) ＋ `.basis-link`(BASIS) を作るが、通常周回では `.tx-inline-detail` へ吸収する。
> - **PART B+「横断・比較・罠コラム」**（`.cross-column`／cb-cross・cb-compare・cb-trap／col-key・col-warn(TRAP)・col-type(THROUGH-LINE)）。
> - **PART C・PART D（12問ドリル）は廃止**。深掘り層は別冊 `-deep.html`（`/deepen-tx` で誤答データ解禁時に後追い）。
> - 参考条文・判例＝条文（文言＋保護法益＋制度趣旨・**スモークブルー系**）／判例（**判旨に『⚖ 判旨』バッジ＋判旨以外を NOTE 化・コーラル系**）。体系ツリー＋放射マップ（＋深掘りでフロー）。
> - **配色住み分け（v12.1.1・最重要）**：①**大前提**（ヘッダー/フッター/紙面背景/PART見出し・section-title・リンク）＝従来の **V3 3パターン（11パレット）** 基調色。②**PART A 問題・解答エリア**＝**ナチュラルマイルド色**。③**インライン肢カード**＝Mildliner 系（条文=ブルー、判例=ピンク、補助根拠=グレー、文言/趣旨/射程/転用=レモンイエロー、切断点=ピンク、記憶フック=紫、答案圧縮=ピンク）。正誤の○緑/×赤は semantic 維持。
> - 唯一の起点は `canonical/GENESIS-CORE.html`（v12.1.1）。validate は `scripts/validate-tx-core.py`（G1〜G35）。
> - **物語解説 typography patch（v12.1.1）**：`.fa-narrative b` は `font-weight:560` 以下。ストーリー解説の強調語を600超・700系の太字へ戻さない。
> - 旧 v10 GOLD-SKELETON（GENESIS.html・PART C/D・validate-tx-gold.py）は既存197問の保守に限定。
>
> **【二系統出力・2026-06-24 確定】TX 1 問＝2 ファイルで出力する**（正典 `spec/tx-v11.1.0-twotrack.md`）：
> - **公式**：`outputs/000_TX/{科目}/{接頭辞}{NNN}.html` ＝ 過去問そのままの **本物の5択**（single／組合せ番号）。Lexia は取り込まない。
> - **Lexia 用 `_lex`**：`outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html` ＝ **ox-grid（記述単位○×）＋解法ナビ**。Lexia はこれだけ取り込む。
> - 本文・解説・PART B/B+・参考条文判例・SVG は **両者で共有**。違いは **answer-area（公式=番号5択／_lex=ox-grid）と _lex の解法ナビ**のみ。
> - 解法ナビは `canonical/SOLVE-NAV.html`（正典スキャフォールド）から注入＝**エンジン JS は逐語コピー、問題固有データ（MODE/STMT or COMBOS/OFFICIAL/ORDER/STEP）だけ本問値**。
> - **全展開（既存問の _lex 化）はローカルPCのバッチで回す。** Lexia 側フィルタ `filterLexiaImportable` は _lex 未生成の問は従来どおり公式を取り込む（移行期は混在で安全）。

引数：問題 PDF のパス（例：`inputs/000_TX/001_刑法/312.pdf`）

---

## 必須手順

### Phase 0：環境確認（最優先）

0a. **outputs/000_TX/{対象科目}/ に既存ファイルがあるか確認**。既存でも **template として Read/Edit 起点にしない**。
    同番号が既存の場合のみ上書き可否を確認。
0b. **直近ログで「template 流用経路」（`Read outputs/*.html` / `cp outputs/*.html`）が選ばれていないか確認**。
    痕跡があれば即停止して `canonical/GENESIS-CORE.html` から再開。

### Phase 1：PDF 解析と配色 V3 判定（＝**大前提の基調色のみ**）

1. **PDF 読解**：問題番号・科目・年度・全記述（ア〜オ）・正解・正答率・出題テーマ・出題形式を抽出。
   - **記述別の正誤（○×）を必ず確定**（ア:○/× … オ:○/×）＝ox-grid の answer-key と final-answer 表の素。
   - 組合せ問題でも「組合せ番号」ではなく**各記述の○×**を一次データとして扱う（導き書§3-1）。
   - **二系統用に2つを併せて確定**（Phase 4h で使う）：
     1. **公式の本物の正解**＝過去問の正答（独立5択なら正しい/誤っている記述の番号＝single、複数なら multi、組合せ・穴埋めなら**組合せ番号と5択それぞれの中身**）。
     2. **解法ナビの型**＝ **○×型**（独立5択「正しい/誤っているものを1つ選べ」）か **組合せ型**（穴埋め・議論形式で答えが組合せ番号）。
2. **冒頭応答必須**：「正答率 __%→パターン_『___』 → 採用パレット『___』」を最初に出力。
3. **パターン判定**（配色 V3）：≥60%→P1 ピンク系／40〜60%→P2 グリーン・ブルー系／<40%→P3 バイオレット系。
4. **パレット選定**（11個から1つ・問題ごとに別）：テーマの重さ・難度・罪名イメージ・正解の意外性で AI 判断。
5. **5色役割割当て**（`memory/reference_palette_v3.md`）：ベース70%`--base`／メイン25%`--accent`／
   アクセント5%`--mid`（11パレット内 chip 借用・palette外 hex 禁止）／サブ1`--soft`／サブ2`--light`／文字`--bg-dark`。
   **ただし `--base`（紙面背景・70%surface）は全問固定クリーム `#F7F1E9`（パレット非依存・紙面統一・2026-06-16 確定）。
   パレット選定で base 役割色は使わず `--base` は GENESIS-CORE の `#F7F1E9` を変えない**（残り `--accent`/`--mid`/`--soft`/`--light`/`--bg-dark` のみ問題ごとに割当て）。
   派生色は bg系 L=55-65 mid-tone 制限、text系 L<40 可。`--border-mid` は白系/クリーム系双方に視認可能な濃さ。
6. **Semantic exception**：✓緑`#438B48`/`#7BA980`・🏆金`#ffd54f`/`#ffaa00`（[[feedback-semantic-exceptions]]）。
6-bis. **配色住み分け（v12.1.1・最重要）**：上記 V3 5色は **大前提のみ**（ヘッダー/フッター/紙面背景/PART見出し・
   section-title・リンク）に適用＝`:root` の主要6＋派生のみ設定する。**PART A 問題・解答エリア＝ナチュラルマイルド色**、
   **PART B/B+・共通根拠・SVG＝4分類パレットの役割固定色**、**inline 肢カード＝Mildliner 系役割色**は **GENESIS-CORE §18〜§24 に内蔵済み（content-independent）
   ＝複製で自動継承**。生成時に**再選定も上書きもしない**（§18〜§24 の hex は触らない）。正誤○緑/×赤は semantic 維持。

### Phase 2：ファイル名・出力先（CLAUDE.md §2）

7. PDF 番号抽出（最初の連続数字→3桁ゼロ埋め）。数字抽出不能なら**中断**しユーザーに番号確認。
8. 科目接頭辞・出力先＝**二系統で2つ**（刑の例。憲/民/商/民訴/刑訴/行政 同様）：
   - 公式：`outputs/000_TX/001_刑法/刑TX{NNN}.html`
   - Lexia 用：`outputs/ux/000_TX/001_刑法/刑TX{NNN}_lex.html`

### Phase 3：GENESIS-CORE の clone と本文初期化

9. **`canonical/GENESIS-CORE.html` を Read**（v12 コア生成の唯一の起点。GENESIS.html や outputs/*.html は使わない）。
10. **対象ファイル名でコピー作成**（Write 経由 or bash `cp`。前面 PowerShell は Copy-Item がブロックされる→
    `.NET File` か bash を使う・[[feedback-powershell-remove-item-guard]]）：
    `cp canonical/GENESIS-CORE.html outputs/000_TX/{科目TX}/{接頭辞}{NNN}.html`
11. **コピー直後に本文を空文字列で初期化**（content-independence・§4-4）。空化対象：
    - PART A `.problem-text`／`.case-description`（見解・事例）／ox-row の `.ox-stmt`／`data-explanation`／final-answer 表
    - 各 choice-section の `.choice-summary`／`.choice-points`／`.sub-card.original`／`.explanation`／
      `.basis-link`／`.sub-card.professor`（①②）本文
    - 参考条文・判例（#basis）の各 `.basis-card-body` 本文（保護法益・制度趣旨・判例要約）
    - 体系ツリー・放射マップ SVG 内 `<text>` テキスト（座標・class は据置）
    - footer-spec 1〜3行目
    - **GENESIS-CORE には PART C・PART D は無い**（別冊送り）。空化リストにも無いことを確認。

### Phase 4：section-by-section 内容差替（各 Edit 30〜50KB・1メッセージ50KB超禁止）

#### 4a. HEAD `:root{}` 配色 V3 適用
Phase 1-5 の CSS 変数 ~20個（主要6＋派生10）を反映。pastel パレットは `--accent` をそのまま背景にすると
contrast 不足→`--accent` は HSL で暗くした派生、palette identity は `--accent-light` で保存。
見出し系は `color:var(--bg-dark)` 固定、badge は `linear-gradient(135deg,var(--accent),var(--accent-darker))`。
ヘッダー/フッター表示テキストに配色情報を書かない（G8）。
- **バッジ共通規約（2026-06-15 確定・全バッジ/タブで遵守）**：`letter-spacing` を付けるラベル・タブ
  （`.sub-card::before` 等）には**必ず同値の `text-indent` を併記**する。letter-spacing は文字の右側だけに
  余白を足すため、text-indent で左にも同量入れて視覚的に中央へ揃える（例 `letter-spacing:.18em; text-indent:.18em;`）。
  **絵文字付きラベルは絵文字の直後に半角スペースを1つ**入れて密着を防ぐ（例 `content:'📚 BASIS'`）。
  GENESIS-CORE は `.sub-card::before` に適用済み。バッジを新設・改名する時も同様に。
- **配色オーバーレイ §18〜§24 は触らない（v12.1.1）**：`<style>` 末尾の §18（バッジ共通規約）〜§24（inline canon
  ナチュラル色）は content-independent な配色体系（4分類役割色・ナチュラルマイルド色・SVG配色）。`:root` の
  V3 基調色だけ更新し、**§18〜§24 の hex・`!important` ルールは削除も改変もしない**（複製で自動継承）。

#### 4b. HEADER 差替
doc-header 問題番号／h1 タイトル（出典・テーマ）／exam-meta（**正答率と難度のみ**）／toc-row（本問の
section リンク＝#part-a/#answer-area/#choice-1〜5/#basis/#mindmap-tree/#mindmap-radial）。

#### 4c. PART A 差替（ox-grid・肢データ源・最重要）
- A-1 `.problem-text`：問題文・記述ア〜オ原文を PDF 逐語。組合せ型は【見解】を `.case-description`/`.case-scene` に。
  （**この【見解】は Lexia が記述の孤立復習時に文脈として表示する**＝省略しない）
- **単純5択型（独立5命題・「誤っているものはどれか」等）の場合は要削除**：組合せ型 canonical
  （GENESIS-CORE は刑TX311＝組合せ型）由来で PART A 末尾に残る ①「（参照条文）… の `blockquote.statute`」と
  ②「【組合せ】── 正しい記述の組合せを次から選択」見出し＋「1 ア　エ …」リストを**必ず削除**する
  （本問固有の参照条文があれば差替、無ければ丸ごと削除）。○×ラベル・`data-stmt`・`data-answer-key` は
  **肢1〜5**（例 `data-answer-key="1:x,2:o,3:o,4:o,5:o"`）。【見解】が無い問題は `.case-description` を本問の
  前提説明に差替。（※刑TX325 でこの2ブロックの消し忘れ事故あり・2026-06-13）
- **（参照条文ブロックの要否・全型共通・2026-06-15 確定）**：A-1 末尾の「（参照条文）…」
  `blockquote.statute` は、**PDF の問題文原文に参照条文が印刷されている場合のみ**その条文を載せる。
  PDF 原文に参照条文が無ければ（組合せ型・5択型を問わず）**丸ごと削除**する。条文は A-3 共通根拠
  条文・判例で足り、二重掲載しない（ユーザー指示）。**機械バックストップ：`validate-tx-core.py` の
  G27 が PART A に `blockquote.statute` を検出すると WARNING を出す**（PDF 原文に印刷されている場合のみ
  残す・無ければ削除＝GENESIS-CORE baseline は 0 個）。G27 が出たら PDF 原文を必ず確認すること。
- A-2 `.answer-area`：
  - `data-answer-type="ox-grid"`／`data-correct-value="××○×○"`（記述ア〜オの正誤を○×で連結）
  - 5 `.ox-row`（`data-stmt="ア"…`）。各行 `.ox-label`＋**`.ox-main`**＋`.ox-btn`（○/×・`data-value`）。
    **`.ox-main` は「要点先頭・全文折りたたみ」の2段**（移動中の高速判定用・2026-06-25 ユーザー指示）：
    - **`<p class="ox-gist">`（必須・要点一行）**：その記述/組合せの肝を **記号フリー（①②/a〜j を使わない）** で
      30〜50字に凝縮。立場・規範・結論を `／` で区切り、キーワードを `<b>` で太字（例：
      `<b>限定説</b>／判例に<b>反対</b>／発生は<b>認識不要</b>`）。**○×の結論はにじませない**（中立に書く）。
    - **`<details class="ox-detail"><summary>全文</summary><span class="ox-stmt">…</span></details>`**：
      自己完結命題（Lexia 記録・G30/G31 対象）の**全文は折りたたみに格納**＝既定で畳む。`.ox-stmt` 本文は
      従来どおり完全な自己完結命題（記号フリー・実体名主語化）で**無改変**＝検証 G30/G31 はそのまま通る。
    - CSS（`.ox-gist`/`.ox-main`/`.ox-detail`）は `canonical/SOLVE-NAV.html` [STYLE] に同梱済み＝逐語コピーで入る。
  - `<button class="reveal-answer-btn" type="button" disabled>解答を表示</button>` 必須
  - `data-explanation` 先頭に正解値リテラル禁止（AP-37）。組合せ導出ナラティブを書かない（G21）
  - **final-answer 記述○×一覧表（G23/G33）**：`<table class="statement-verdict-table" data-answer-key="ア:x,イ:x,ウ:o,エ:x,オ:o">`
    ＋各行 `<tr data-stmt="ア" data-verdict="x">`＋論点コアのセル。`.final-answer` は hidden（reveal で JS が開く）。
    **answer-key の o/x は data-correct-value と必ず一致**。
    - 論点コア列の見出しは **`登場した論点のコア（文言・趣旨・射程・切断点・転用）`** に固定。
    - 各行の論点コアセルは **5点セット必須**：`<div class="tx-reflex-core">` 内に
      `.tx-reflex-line` を5本置き、`.tx-reflex-tag` で **文言／趣旨／射程／切断点／転用** を明示する。
      切断点の行は `.tx-reflex-cut` を併用する。
    - 5点セットも Lexia の単独復習で表示されるため、**記号フリー・自己完結**（A説/B説・甲乙説・①②・(a)・本問依存表現を残さない）。
      Type A/combo/lite の補助生成器は旧文字列も受けるが、新規生成データは5キー（文言・趣旨・射程・切断点・転用）で渡す。

#### 4c-bis. `_lex` インライン周回面（TX360 正典・2026-06-29）
`_lex` では、問題文を読んでから別位置の ox-grid へスクロールさせない。PART A の問題文直後に
**各肢対応の `.tx-inline-card`** を置き、肢本文・○×ボタン・逐条解説を一体化する。gold は
`outputs/ux/000_TX/001_刑法/刑TX360_lex.html`、CSS/JS 正典は `canonical/GENESIS-CORE.html` の
`tx-inline-*`。

1. 各肢:
   - `<article class="tx-inline-card" id="stmt-1" data-stmt="1">` のように、裏の `.ox-row[data-stmt]` と同じキーを使う。
   - `.tx-inline-ox[data-stmt][data-value="○/×"]` は裏の ox-grid を click して同期する。裏の ox-grid は消さない。
2. 各肢の解説:
   - `.tx-mini-law`：登場条文本文をすべて入れる。メイン条文は濃いブルー、補助条文は淡いブルー、周辺条文はグレー。判例を入れる場合はピンク系。
   - `.tx-article-flow`：文言・趣旨・射程・切断点・転用を統合した本文。ラベル横に本文をぶら下げず、本文側に字下げを入れる。
   - `.tx-cycle-aids`：記憶フック（紫系）と答案圧縮（ピンク系）。どちらも一文。正解番号だけが分かるネタバレ文にしない。
   - `.tx-inline-detail`：「詳説を開く」で対応する PART B の `sub-card.synthesis` / `choice-points` / `basis-link` を開く。
3. 下の `.answer-area` は `inline-prototype-mode` を付け、表示上の素 ox-grid を隠してよい。ただし Lexia/SM2 記録・G23/G29/G30/G33 の単一情報源として保持する。
4. `解説だけ閲覧` ボタンを置く。全肢未選択でも解説と `.final-answer` を開くが、`answered` を付けず、Lexia/SM2 記録を発生させない。再クリックで閉じる。
5. `.final-answer` には旧 `fa-summary` を置かない。順序は **`.fa-narrative` → `.statement-verdict-table`**。

**問題都合ラベルの処理**：記号問題・組合せ問題・見解A/B・事例Ⅰ/Ⅱ・空欄①〜⑤などは、SM2 に残す知識ではない。
過去問原文には残してよいが、`.ox-stmt`・`.tx-reflex-core`・`.tx-cycle-aids`・`.tx-inline-explain` では、
必ず **論点コア・テーゼ** に置換する。見解は学説名または定義内容、記号は語句・制度・要件の実体へ置換する。
「本問」「上記」「記述ア」「肢3」依存は残さない。

#### 4d. PART B 差替（記述ア〜オ・記述単位・v12.1.1 詳説ソース）
各 choice-section（choice-1=記述ア…）の**バッジは単一記述**（組合せ見出し禁止・G20）。GENESIS-CORE の
v12.1.1 ブロック構造を埋める（順序厳守）：
1. `.choice-header-block`：`.verdict`（✓○/✗×＋法理とのズレ一文。**組合せ判定を書かない**）。
1-bis. **【学説・見解適用問題のみ】`.choice-premise`（🔎 この記述が前提とする見解）**：`.choice-header-block`
   直後に置く。その記述が前提とする見解（A説/B説/見解A…）の定義を **PART A の `.case-description`/`.case-scene`/
   `.problem-text` 原文どおり（要約せず）再掲**する（`.cp-title`＝見解見出し＋`.cp-body`＝定義本文）。複数見解を
   参照する記述（「Aの見解に対しBの見解から」「いずれの見解でも」）は参照する全見解を並べる。**目的＝遡読防止**：
   記述に入った瞬間に前提が確定し、PART A 冒頭へ戻らずに解説を読める。事案型・単純5択型では使わない（G28 が
   学説問題のみ検出・WARNING）。既存問題への一括挿入・抽出は `python scripts/add-choice-premise.py`。
2. `.sub-card.synthesis`（🎯 SYNTHESIS）：`.syn-orig`（📜 記述原文＝PDF逐語）→ `.syn-lead`（💡 THE GIST＝
   一文要約）→ `.syn-path`（①②③ の噛み砕き・イメージを交える）→ `.syn-image`（💭 INTUITION＝直感像）。
3. **`.choice-points`（📌 POINT・論点コア前倒し）**：2〜4点。主語は法概念（規範コア／判例の結論と射程／
   区別基準／決め手の限定句）。**禁止：正解は肢N／組合せ判定／本記述は誤り・正しい／他記述参照（G22）**。
4. `.sub-card.basis-link`（📚 BASIS＝参考条文・判例セクションへのアンカー）。
> 教授①②（考え方の道筋）は SYNTHESIS の `.syn-path` が担う。教授③④・key-phrase・analogy 等は別冊 D-1 送り。

#### 4d-bis. PART B+ 差替（横断・比較・罠コラム・v12.1.1）
`.cross-column` 内の 3 つの `.col-block` を埋める（GENESIS-CORE 据置の構造・色は §18〜§24 継承）：
- `cb-cross`（🔗 CROSS）：本問論点を他分野・他罪と結ぶ横断表＋`.col-key`（💡 決め手）＋`.col-type`（THROUGH-LINE＝通底する一本の糸）。
- `cb-compare`（📊 比較）：軸で束ねる比較表＋`.col-key`（💡 詰める順番）。
- `cb-trap`（⚠️ 罠）：`.col-warn`（TRAP N＝誤答の型）＋`.col-type`（THROUGH-LINE）。
- 表・チップ・タブの配色（オリーブ見出し／ゴールド col-key／バーミリオン TRAP 等）は §20 継承。本文のみ差替。

#### 4e. 参考条文・判例 差替（#basis・v12.1.1）
本問関連の条文・判例のみ。配色は §19 継承（**条文＝スモークブルー系／判例＝コーラル系／NOTE＝グレー**・薄め背景）。
- 条文カード（`.basis-card.statute-card`）：`.hanging` 文言＋ `.note` 内 `.kd-item`（役割ラベル `.kd-label`：
  保護法益／制度趣旨／要件／あてはめ等）。NOTE はグレー据え置き。要件効果の網羅一覧は別冊。
- 判例カード（`.basis-card.case-card`）：**判旨は `.judgment-text`**（『⚖ 判旨』バッジ＋コーラル地が CSS で付く）。
  **判旨以外の項目（射程・注意 等）は `<div class="note">` に格納**（旧 `.kd-list` は使わない＝NOTE 化）。
  重要度濃淡は ★ で。**【事案】【判旨】【補足】の完全プロファイルは書かない（G24・別冊D-2）**。
- ref-backlinks は `#choice-N`（記述）へ。

#### 4f. SVG 差替（体系ツリー＋放射マップの2枚のみ）
座標・色 class は GENESIS-CORE 据置、テキストのみ本問に差替。
- 体系ツリー（mindmap-tree）：L0/L1/L2/L3 を本問体系に。
- 放射マップ（mindmap-radial）：主要枝・サブ要素を本問論点に。
- **フローチャート（flow-svg）は core に置かない**（別冊 D-3）。
- class は GENESIS-CORE の `<style>` 定義済みのみ使用（独自命名は黒塗り・G16）。

#### 4g. footer-spec 差替
1行目 `<strong>{接頭辞}{NNN}</strong>・{科目}（{出典}）`／2行目 `正答率 {N}%／難度 {★}`（配色記載なし）／
3行目 `作成日：{YYYY-MM-DD}`／別冊リンク行 `{接頭辞}{NNN}-deep.html`。
feature-tag 先頭＝**`TX v12.1.1 LOOP-CORE`**（必須）。続けて genesis-core-baseline／editorial-reskin／
synthesis-subcards／part-b-plus-cross-column／refs-hogo-eki-shushi-smokeblue／case-judgment-badge-note／
mindmap-tree-and-radial／deep-volume-separated／palette-tier-3（大前提=V3／PARTA=natural-mild／他=4分類）／
`palette: {名} (P{N})`／svg-overlap-checked／content-independence／jp-prefix-naming。

#### 4h. 二系統出力（公式／Lexia 用 _lex に分離・v12.1.1 最重要）

ここまでで `outputs/000_TX/{科目}/{接頭辞}{NNN}.html` は **ox-grid コア**（＝_lex の素）が完成している。
これを 2 ファイルへ分ける。**本文・PART B/B+・参考条文判例・SVG・footer は共有**し、差し替えるのは answer-area と _lex の解法ナビだけ。

**手順（順序厳守：_lex を先に切り出してから公式を de-grid する）：**

1. **Lexia 用 `_lex` を切り出す**（ox-grid のまま複製）：
   `cp outputs/000_TX/{科目}/{接頭辞}{NNN}.html outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html`

2. **`_lex` に解法ナビを注入**（`canonical/SOLVE-NAV.html` を Read し、3 ブロックを移植・**エンジン JS は逐語コピー**）：
   - `[STYLE]`（`<style id="solve-nav-style">…`）→ `<head>` の `</style>` 直前へ。
   - `[SHELL]`（`<div class="solve-nav" id="solve-nav">…</div>`）→ PART A の answer-area `<h3>【解答】…` の直前へ。
   - **問題型に応じ 1 つだけ**：独立5択→`[SCRIPT-OX]`／組合せ・穴埋め・議論形式→`[SCRIPT-COMBO]` を `</body>` 直前へ。
   - SCRIPT 内「問題固有データ」デリミタ内**だけ**を本問値で記述（**エンジン本体は触らない**）：
     - **○×型**：`MODE`（`'correct'`＝正しいものを1つ選べ／`'incorrect'`＝誤っているものを1つ選べ）と
       `STMT`（各記述の `q`・`tip`・`note`）。答えは ox-grid の `data-correct-value` から自動導出（COMBOS 不要）。
     - **組合せ型**：`COMBOS`（本物の5択 番号→各空欄キー）・`OFFICIAL`（各空欄の正解キー）・
       `ORDER`（検討順）・`STEP`（各空欄の `q`/`loc`/`tip`/`opts`/`note`）。組合せ型は5択の中身を `.problem-text` に併記。
   - **`tip`（💡コツ）は「スパッと一行」**（移動中の高速判定用・2026-06-25 ユーザー指示）：列挙・場合分けの
     長文にしない。**決め手1点**に絞り `決め手は<b>◯◯</b>。…` の形で **1文・40〜70字**に凝縮する
     （複数観点を `——` で連ねる旧式は禁止）。`sn-sub`（ナビ冒頭の説明）も同様に短く引き締める。
   - footer-spec feature-tag に **`lexia-oxgrid-solvenav`** を追記。ox-grid・final-answer 表・answer-key は**そのまま保持**（Lexia 肢キー源）。

3. **公式（`outputs/000_TX/...`）を de-grid**（本物の5択へ）：
   - answer-area を `data-answer-type="single"`（多答は `"multi"`）／`data-correct-value="{本物の正解番号}"` に。
   - `.answer-ox-grid`（ox-row 群）を `.answer-row`（番号ボタン1〜5・`canonical/GENESIS-CORE.html` 既存の構造/CSS）に置換。
   - instruction を「記述1〜5のうち正しいものを1つ選び、『解答を表示』を押してください」へ。
     **組合せ・穴埋めは**【組合せ】見出し＋「1 ①a ②d…／2 …」を `.problem-text` に併記し「①〜⑤の組合せを 1〜5 から選ぶ」。
   - **解法ナビは公式に入れない**。`.final-answer`（○×一覧表）は real-exam では**任意**（残しても削っても可・G23 は公式で対象外）。
   - footer-spec feature-tag に **`official-5choice`** を追記。

4. **整合**：`_lex` の `data-correct-value`（○×）の **○ の位置と公式の正解番号が一致**すること（独立5択）。組合せ型は
   `OFFICIAL` から導く番号＝公式 `data-correct-value` が一致すること。両ファイルの `<title>`・doc-header・footer の問題コードは同一（ミラー）。

#### 4i. 物語解説の執筆・注入（`_lex` のみ・標準搭載・2026-06-26 ユーザー指示）

**基本書を読まない学習者が「本当にわからない時に読む救済テキスト」**として、`_lex` の `.final-answer` 冒頭に
**初学者向けの物語解説（読み物）**を入れる。**全 TX `_lex` の必須要素**（公式 `000_TX` には入れない）。

1. 本問の内容（核心論点・各記述の正誤理由）を、**一連の読み物**として執筆。要件：
   - **初学者でもわかるレベル**：その罪・論点がなぜ問題になるか、鍵概念（保護法益・構成要件・故意/過失・各制度趣旨 等）を初出で噛み砕く。
   - **記号フリー**：①〜/(a)〜(j)/「A説・B説」「甲乙説」「第N説」/記述記号(ア〜オ)への言及を使わない。見解は実体学説名、当事者は事案の登場人物名、各記述は内容で指す。
   - **問題の論理に沿って一本に**：核心（何が問われているか）→ 各記述がなぜ正/誤か → まとめ（幹1〜2本＋「番号は結果、覚えるのは理由づけ」）。
   - **物語性が薄い寄せ集め問題は偽の物語を捏造しない**：内容に即した**共通概念の枠組み**で束ねる（例：過失の下位類型なら「この論点に引かれた複数の"境界線"」）。筋がある問題は流れとして、寄せ集めは共通概念のフィールドガイドとして。
   - 形式：`{"title":"この問題を物語で読む ── <短い主題>","paras":["段落1",...]}`（**6〜9段落**・重要語は `<b>`・①記号やmarkdown禁止）。手本＝`outputs/ux/000_TX/001_刑法/刑TX311_lex.html` の `.fa-narrative`。
2. JSON を `/tmp/.../narrB-{接頭辞}{NNN}.json` に python で安全出力（json.dump, ensure_ascii=False）。
3. 注入：`python scripts/tx-inject-narrative.py {接頭辞}{NNN} <json>`（`.fa-narrative` を `.final-answer` 冒頭へ・CSS は GENESIS-CORE に同梱済みだが無ければ自動注入・冪等）。
   - 補助：素材が要れば `python scripts/tx-extract-source.py {接頭辞}{NNN}`（核心・各記述＋論点コア＋問題文要旨を compact 出力）。
   - **議論形式（Type A・空欄補充の組合せ）**は `tx-build-typeA.py` が物語を内蔵するので、そちら経由なら 4i 不要（重複注入しない）。

#### 4j. Lexia/SM2 解説ペイロード（TX360 正典）
SM2 は「長い読み物」ではなく「誤答肢を再判定する場所」。生成時は、Lexia が抽出してよい解説の優先順位を崩さない。

1. `.ox-stmt`：単独で○×判定できる本文。
2. `.tx-reflex-core`：文言・趣旨・射程・切断点・転用の5点セット。
3. `.tx-cycle-aids`：記憶フック／答案圧縮。短い想起補助。
4. メイン条文番号・条文本文：条文文言が正誤に直結する場合。
5. `.tx-inline-detail` / PART B 詳説：誤答時に開く補助。通常SM2表面に長く載せない。

`.fa-narrative` は初回理解用の救済テキストであり、SM2 の通常カード本文には載せない。必要時参照に留める。

### Phase 5：SVG 重なり機械検査（体系ツリー＋放射マップ）

12. 2枚の `<rect>`/`<ellipse>` の bounding box を計算し全ペア AABB 衝突判定（衝突 0・マージン16px以上）。
13. 衝突時は viewBox 拡張を最優先（[[feedback-svg-box-overlap]]）。

### Phase 6：検証と配信

14. **両ファイルを検証**（二系統）：
    - `python scripts/validate-tx-core.py outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html`（**ox-grid 必須**）
    - `python scripts/validate-tx-core.py outputs/000_TX/{科目}/{接頭辞}{NNN}.html`（**公式＝single/multi 可**。G23/G25 は公式で自動緩和）
    - `python scripts/check-duplicates.py outputs`（公式↔_lex の同一 title はミラーとして除外＝**正常**・他の重複のみ検出）
15. **G1〜G35 ERROR 0 件確認**（特に G20 記述単位・G21 禁止句・G22 choice-points・G23 answer-key（_lex）・
    G24 完全プロファイル不在・G25 ox-grid（_lex）/single・multi（公式）・G26 PART D不在・G30 記号のみ肢の禁止・
    G33 TX-LEX最終表5点セット）。
    WARNING は配信可だが、**G27（PART A 参照条文）が出たら §4c に従い PDF 原文を確認し、印刷が無ければ削除**してから配信する。
    **G31（プール対象テキストの自己完結・WARNING）が出たら、ox-stmt・verdict 論点コア列から
    問題ローカルのラベル（A説/学生A/①②/(a)/事例Ⅰ/本問 等）を除き、見解は実体学説名で主語化・記号は語句の実体に置換する**（spec 第3-bis項・新規生成では極力 0 件に）。
    **G33（TX-LEX最終表5点セット・WARNING）が _lex で出たら新規生成では配信禁止**。各行を
    文言・趣旨・射程・切断点・転用へ分解し、WARNING 0 件にしてから配信する（既存移行中のみ WARNING 扱い）。
16. ERROR があれば該当箇所を修正し再検証。視覚確認推奨 → `present_files`（公式・_lex の2枚）。
17. **物語解説の存在確認（_lex）**：`grep -c 'fa-narrative-title' outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html` が 1 以上であること（Phase 4i・未注入なら 4i を実行してから配信）。

### Phase 7：git コミットで永続化（§9）

16-bis. **両ファイルにフッター生成日時＋版を刻む（Lexia が raw 取得して読む・必須）：**
    commit 前に **`python scripts/stamp-created-date.py`** を実行（`outputs/000_TX` と `outputs/ux` を走査＝公式・_lex 双方に
    `Generated: YYYY-MM-DD HH:MM / TX v12.1.1 LOOP-CORE`・class=lexia-genmeta を刻む・冪等）。素の git commit でも
    pre-commit フック（§9）が保険で刻む。
17. 検証通過後 **両ファイルを add** → 本問単位で `git commit`（例：`feat(刑TX): 刑TX346 を二系統生成（公式5択／Lexia用 ox-grid＋解法ナビ）`）→ push（本線は master へ集約・§8）：
    `git add outputs/000_TX/{科目TX}/{接頭辞}{NNN}.html outputs/ux/000_TX/{科目TX}/{接頭辞}{NNN}_lex.html`
18. `present_files` 完了報告に commit hash と**2ファイルのパス**を併記。

### Phase 8：深掘り別冊（任意・後追い）

19. 別冊（`-deep.html`）は**全問では作らない**。Lexia の誤答データが解禁条件（同じ記述を繰返し誤答／
    弱点克服帳に同一論点が反復／直前期）を満たした問題にだけ **`/deepen-tx {NNN}`** で後追い生成
    （GENESIS-DEEP clone・教授③④＋判例完全プロファイル＋フローチャート＋PART C・validate-tx-deep）。

---

## 鉄則（絶対遵守）

- **template 流用の物理的禁止**：`outputs/*/` の**別問題**の HTML を起点に `cp`/`Read`/`Edit` しない。
  唯一の起点は `canonical/GENESIS-CORE.html`。clone 直後に本文を空文字列初期化してから執筆（AP-42）。
  - **例外（二系統のみ）**：Phase 4h の `cp 000_TX/{code}.html → ux/000_TX/{code}_lex.html` は**同一問題の自分自身**の複製であり許可（別問題の流用ではない）。解法ナビは `canonical/SOLVE-NAV.html`（正典）のエンジンを逐語コピーし、問題固有データのみ記述する。
- **二系統出力は必須**（Phase 4h）：1 問＝公式（`000_TX`・本物の5択）＋ `_lex`（`ux/000_TX`・ox-grid＋解法ナビ）の2ファイル。
  `_lex` は ox-grid・answer-key・final-answer 表を保持（Lexia 肢キー源）。公式と `_lex` の **answer は整合**（○の位置＝正解番号）。
- **物語解説は `_lex` の必須要素**（Phase 4i）：`.final-answer` 冒頭に初学者向けの読み物（`.fa-narrative`）を入れる。
  記号フリー・問題の論理準拠・寄せ集めは共通概念で束ねる（偽の物語を作らない）。`tx-inject-narrative.py` で注入（Type A は `tx-build-typeA.py` が内蔵）。
- **render.py 経路の禁止**（`python scripts/render.py` は WIP 上書き事故）。
- **第一原理：解説の対象は記述であって肢ではない**。組合せ導出ナラティブ・選択戦略語彙
  （消去法/絞り込み/2肢で正解 等）を全域で書かない（G21・導き書§3-1 と正反対の有害情報）。
- **PART C・PART D を core に作らない**（G26）。深掘りは別冊 `-deep.html`（`/deepen-tx`）。
- **ox-grid の answer-key／data-correct-value／final-answer 表の○×は三者一致**（Lexia 肢キー記録の整合性）。
- **SVG ボックス重なり禁止**（Phase 5 機械検査）。class は GENESIS-CORE 定義済みのみ（G16）。
- ヘッダー／フッター本文に配色情報を書かない（G8）。
- **1メッセージで 50KB 超の Write/Edit 禁止**（section 単位で分割・API socket error 予防）。
- 中断・再開時も**必ず GENESIS-CORE ＋ PDF から続行**。既存 outputs/*.html を template 参照しない。
- 「保守的書き換え」をしない。**冒頭応答必須**：「正答率__%→パターン_『___』→パレット『___』」。

$ARGUMENTS
