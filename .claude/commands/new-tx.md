---
description: 新規 TX を問題 PDF から生成。_lex は active v13.1.0 LOOP-CARD（GENESIS-CARD baseline：統合解説昇格＋📚BASISトグル＋体系マップSVGハイブリッド＋正誤マーキング＋相互リンク往復）。公式版は本物5択。
---

新規 TX HTML（短答式・二系統＝公式 `000_TX`＋Lexia `_lex`）を問題 PDF から生成する。

> **【active＝v13.1.0 LOOP-CARD・2026-07-03】_lex の新規生成・v13 化はこの経路が唯一起点。** 最初に
> `docs/canonical-lineage.md` の active 行を読む。v13 の byte 正典は **`canonical/GENESIS-CARD.html`（gold=刑TX359）**＋
> **`canonical/GENESIS-CARD.placeholder.html`（スロット契約）**＋**`spec/tx-v13.1.0-loopcard-core.md`（構造 spec）**。
> 生成は GENESIS-CARD を複製し、placeholder のスロットだけを問題固有に埋める（CSS/JS/class/DOM/節順は固定・接ぎ木禁止）。
> - **設計の核**：v12.2.1 の「肢を解く UI（ANSWER箱＋5点フロー＋記憶フック）」を廃し、**旧 PART B の統合解説プロースを
>   記述カード本文へ昇格**。条文・判例は各カードの **「📚 BASIS」ボックス**（条文＝本文表示/解説トグル・判例＝判旨表示/以下トグル・**学説＝ラベンダー/任意項目**＝重要な学説対立の記述だけ `.tx-basis-item.is-theory`・**短答は既定で置かない＝焼損既遂/認識要否のような真に決定的な対立のみに限り横展開しない。学説の深掘りは JX/ARIADNE へ**）へ集約。
> - **縦順**：正誤表→**体系マップ(SVGハイブリッド・下部旧SVG2枚は廃止)**→横断(3軸マトリクス)→肢カード→物語(カード直後)→#basis(現行法note のみ)。
> - **正誤表(LOCKED・spec第2項)**：各行＝①**印付き記述原文**（`.tx-vb-orig-mark`＝各行`<tr>`の **`data-brief-mark`** にHTML。各肢カード `.syn-orig` と同じ marking の**要約版**。×=誤り核に赤波下線`.tx-stmt-x`+✕+`.tx-stmt-fix`「→正解」／○=緑下線`.tx-stmt-o`+✓。属性は二重引用・内側classは単引用`'…'`）＋②**法理コア**（`.tx-vb-core`＝`extractReviewCoreSummary` が **転用タグ**を1文抽出）。見出し行右に**成績**（`computeInlineScore`→`.tx-inline-answer-score`＝🎉全問正解！N/N ／ n/N 正解）。**重厚感**（額装フレーム・金プレート見出し📋・立体ヘッダー・正誤行の左アクセント帯・押し出しチップ）。**data-brief-mark は問題固有スロット＝各記述で必ず執筆**（未鋳造は validate-tx-core G50 が WARN）。
> - **体系マップ(LOCKED・spec第3項)**：客体三分ツリー＋本問N局面の記述札（`#stmt-N`）。各札に **✍規範核バッジ**（`.nb-badge`＋`.nb-badge-text`＝転用可能な**規範核1文**・ノード accent の暗色で白抜き11〜14字・ノード高さ118）。**`▼ 本問の帰結（○×）`箱は置かない**（答え先出し禁止）。帰結箱を除いた分 viewBox 下端を詰める。往路=`#stmt-N`／復路=各カード末尾 `.tx-sysmap-back`（`#tx-sysmap`）。**規範核バッジ文言は問題固有スロット＝必ず執筆**（未鋳造は G50 が WARN）。
> - **カード物理順**：判定バッジ→📜記述原文(正誤マーキング)→🎯統合解説(THE GIST/段階/（任意）📐図解 `.tx-dgm`＝効く論点だけ・物語側と同一複製 `data-dgm` 同期/🗝フック)→📌POINT→📚BASIS→
>   ⚠️間違いやすいポイント→🔗他科目横断(重要接点のある記述のみ・無理に足さない)。
> - **相互リンク往復**（条文参照→同カードBASIS条文へジャンプ＋戻る・配線JSは単一エンジンへ統合＝script2本）、
>   **正誤マーキング**（分かれ目を×赤波線/○緑下線）、**使い方説明は載せない**、タブラベル字下げ無効・本文1字下げ。
> - **検証**：`scripts/validate-tx-core.py`（G1〜G64＝G45表示LOCK＋**G50-G54 v13完全性**＝正誤表印付き原文/規範核バッジ/帰结箱不在/成績エンジン/BASIS中身/trap/相互リンク/🗝フック＋G56/G57 深さ助言＋G58 cross-cut＋G60 極性＋**G61/G62 v13n 不可侵ブロック＋G63 三点整合＋G64 バッジ⇄key矛盾＋G67 図解整合**）＋
>   `check-tx-lex-engine.py`（G41/script2本）＋`check-duplicates.py`。レンダリング実測（playwright）で往復リンク・トグル・
>   マーキング・**成績表示（○×を正解で選び「解答を表示」→🎉）・印付き正誤表**・pageerror0 を確認。
> - **正典 gold＝刑TX359（GENESIS-CARD）は正誤表リデザイン適用済。既存 v13（089/125/174/218/256/290-302/355-385・刑訴TX001 等）の
>   リデザインは「そのあと」**＝土台は `scripts/tx-lex-verdict-redesign.py`（CSS＋エンジン＋帰结箱除去を決定論注入）で載せ替え、
>   各問の**規範核バッジ文言・印付き原文（data-brief-mark）は1問ずつ執筆**（G50 WARN が残タスクを示す）。公式版（本物5択）は
>   `spec/tx-v11.1.0-twotrack.md` の二系統を継承。最新法令・判例・学説レビューと省エネ検証は v12 と同じ。
>
> ---
> **【以下は frozen＝v12.2.1 LOOP-CORE の記述（既存 355-358・360-385 の保守用・新規 _lex では使わない）】**
>
> active v12.2.1 LOOP-CORE 経路（2026-07-01 表示LOCK）：既存 v12 資産の保守時は
> `canonical/GENESIS-CORE.html`、`spec/tx-v12.1.0-inline-core.md`、`docs/tx-v12.2.1-inline-lock.md`。基盤として
> `spec/tx-v11.0.0-core.md`（肢単位管理）と `spec/tx-v11.1.0-twotrack.md`（公式/ Lexia 二系統）を継承する。
> 過去問を**問題単位でなく記述（肢）単位で管理**する設計に対応。
> - **誌面リスキン**：明朝（Shippori Mincho B1）＋極細罫の編集デザイン（CSS 変数 `--ed-*`・`<style>` §1〜§17）。
> - **PART A は ox-grid（5記述の○×収集）＋機械可読 answer-key**（Lexia 肢キー記録の一次情報源）。
> - **Lexia 用 `_lex` の主導線は問題文直後の `.tx-inline-card`**。各肢本文、○×、条文原文、文言・趣旨・射程・切断点・転用、記憶フック、答案圧縮、詳説トグルを同じカードに置く。
> - **PART B は記述（ア〜オ）単位の詳説ソース**。SYNTHESIS 子カード（`.syn-orig`記述原文／`.syn-lead`THE GIST／`.syn-path`①②③／`.syn-image`INTUITION）＋ `.choice-points`(POINT) ＋ `.basis-link`(BASIS) を作るが、通常周回では `.tx-inline-detail` へ吸収する。
> - **PART B+「横断・比較・罠コラム」**（`.cross-column`／cb-cross・cb-compare・cb-trap／col-key・col-warn(TRAP)・col-type(THROUGH-LINE)）。
> - **PART C・PART D（12問ドリル）は廃止**。深掘り層は別冊 `-deep.html`（`/deepen-tx` で誤答データ解禁時に後追い）。
> - 参考条文・判例＝条文（文言＋保護法益＋制度趣旨・**スモークブルー系**）／判例（**判旨に『⚖ 判旨』バッジ＋判旨以外を NOTE 化・コーラル系**）。体系ツリー＋放射マップ（＋深掘りでフロー）。
> - **配色住み分け（v12.1.1・最重要）**：①**大前提**（ヘッダー/フッター/紙面背景/PART見出し・section-title・リンク）＝従来の **V3 3パターン（11パレット）** 基調色。②**PART A 問題・解答エリア**＝**ナチュラルマイルド色**。③**インライン肢カード**＝Mildliner 系（条文=ブルー、判例=ピンク、補助根拠=グレー、文言/趣旨/射程/転用=レモンイエロー、切断点=ピンク、記憶フック=紫、答案圧縮=ピンク）。正誤の○緑/×赤は semantic 維持。
> - 唯一の起点は `canonical/GENESIS-CORE.html`（active v12.2.1）。validate は `scripts/validate-tx-core.py`（G1〜G64）と `scripts/check-tx-lex-engine.py`。
> - **物語解説 typography patch（v12.1.1）**：`.fa-narrative b` は `font-weight:560` 以下。ストーリー解説の強調語を600超・700系の太字へ戻さない。
> - **表示LOCK（v12.2.1）**：問題文と○×の一体化、解法ナビの非ネタバレヒント、条文/判例の題名・法理テーマチップ、ラベル付き本文2カラム字下げ、物語解説の reveal 後表示、カード内2行判定、解説冒頭の正誤表を維持する。
> - **品質LOCK**：公開・push 前に、最新法令・判例・主要学説と解説内容を最高エフォートで確認する。
>   **確認は「執筆した本人（同一エージェント）が丁寧に1回」自己照合する方式**（内部整合＝条文番号/項符合・label↔body 一致・ox-stmt正誤・記号フリー）＋**確信の持てない/非著名判例だけ的を絞ったWeb一次確認**（判例名・年月日・裁判所種別・学説か判例か・実在。著名判例は不要）。**別エージェントによる多重（例：5並列）敵対レビューや、機械整形後の再修正ループは常態化しない**（省エネ方針・[[feedback_lean_verification_author_once]]）。品質は執筆段階で一文一文丁寧に作り込んで担保し、被り・接ぎ木を執筆時点で出さない。安いpython機械ゲート（下記 Phase 6）は必ず通す＝これはトークンをほぼ消費しない安全網。
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
  - **記述数 N 個の `.ox-row`**（単純5択＝5個・`data-stmt="ア"…`。**特殊型は N が5でないので上記「特殊型の構造・
    作図ガイド」に従って N 個にし、`data-correct-value` も N 文字にする**）。各行 `.ox-label`＋**`.ox-main`**＋`.ox-btn`（○/×・`data-value`）。
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

**【特殊型（非単純5択）の構造・作図ガイド・最重要】** GENESIS-CARD の gold（刑TX359）は**単純5記述**なので、
特殊型はそのまま複製すると崩れる。canonical だけを見ず、**型が最も近い合格実例（下表）を Read して構造を写す**。
検証（G50/G51/G52）は記述数を数えないので、**要素数を記述数 N に合わせて増減してよい**（5固定ではない）：
- **記述数 N が5でない**（穴埋め8個・命題3個など）：`.ox-row`・`.tx-inline-card`（`#stmt-N`）・体系マップの記述札
  `#stmt-N` ノードを**すべて N 個**にする。体系マップ SVG は N ノードに合わせて x 座標を**再配置**し、Phase 4f の
  AABB 衝突検査で重なりゼロ＋viewBox 余白を確認する。裏 `.answer-ox-grid` の `data-correct-value` も **N 文字**。
- **組合せ・穴埋め・会話型**：各空欄／各命題を**独立した1つの○×命題に分解**する。**data-correct-value は
  判別性ある○×混在にする（全○は禁止）**：過去問の語句群がもつ**対立語（distractor：肯定/否定・同じ/異なる・
  条件付き権限/一律否定・成立し得る/し得ない・過去/将来 等）**を使い、一部の記述を**実際の誤り（distractor 主張）
  に差し替えて×**、他は正しい語句のまま○にする。distractor が語句群に無い型（見解対立等）は、対立説・典型的
  誤解を×命題として作る。**全○＝「正しい語句を並べて全部○と確認するだけ」は判別性ゼロの退化グリッドで禁止
  （L4 違反・`check-lex-oxgrid-integrity.py` が検出）。** 「組合せ番号#3は正しいか」型の行も禁止（G42/G46 違反）。
  問題文（会話・語句群・組合せ）は過去問 verbatim を保持し、○×へ作り替えるのは ox-stmt／記述カードだけ。
  **【一問一答自己完結の鉄則・全問共通・最重要】記述カードの見出し（`.tx-inline-stmt-text`）と ox-stmt は、
  そのカード単独で見て「問題として成立し、誰が見ても○×を判断できる完結した命題」にする**（Lexia は各記述を
  問題本体から切り離した一問一答カードとして提示するため）。必須：
  - 語句群記号（ア/イ・①〜・(a)〜）を外し、事実（事案）＋断定（結論）を1文に含めて句点「。」で結ぶ。
    例：「…宿泊者カードを作成した場合、私文書偽造罪が成立する。」／「…提示した場合、偽造有印公文書行使罪の未遂が成立する。」
  - **断片で終わらせない（何を○×するのか不明になる）**：`…した場合。`（結論欠落）／`事例（○○罪）`（罪名ラベルだけ）／
    `…評価`『…見解』（体言止め）／`…＝1個の恐喝罪`（＝ラベル）は不可。必ず動詞で成否・当否を言い切る。
  見本＝刑TX368_lex（組合せ・断定文）・刑TX369_lex（行使5事例・「…した場合、…罪が成立する。」）。
  判別性ある○×の実例＝**刑TX368_lex（組合せ・××○○○）・刑TX381_lex（会話穴埋め・×○○×○○○×）・刑TX428_lex（会話穴埋め・○×○×○）**。
  解法ナビは Phase 4h の `[SCRIPT-COMBO]`（COMBOS/OFFICIAL/ORDER/STEP）を使う。
  **許容される2方式のどちらかで作る**：(1) 上記の**判別性ある○×混在**（一部を distractor に差し替え×）、
  または (2) **blank-mode 2択誘導**（`data-oxgrid-mode="blank"`＝各空欄を正解語句と distractor の2択で選ばせる・
  `var B{loc,frag,q,tip,opts,ans,core}` 型・刑TX350/刑TX418 が原型）。**blank-mode は2択が判別性を担うので裏 ox-grid の
  data-correct-value は全○でよい**（`check-lex-oxgrid-integrity` が blank-mode を L4 から自動免除）。
  **禁止されるのは「素の○× ox-grid（blank-mode でない）を全○にする」＝判別性ゼロの退化グリッドだけ**（L4）。
- **見解A/B・学説適用型**：Phase 4d-1bis の `.choice-premise`（🔎 前提見解）で A説/B説 定義を原文再掲（遡読防止）。
- **共有事例型（「甲の罪責を検討せよ」型・見解×事例型）＝不可侵原文ブロック必須（§v13n・G61/G62）**：
  `#part-a:has(.tx-inline-card) > .problem-text{display:none}` が事例を隠す（刑TX374 の事例消失事故）ため、
  問題文直下（解法ナビ・肢カードより上）に `.tx-original-block` を置き、PDF の問い＋事例＋（見解）＋記述/罪名列を
  **逐語のまま常時表示**する（付け足し・要約・改変ゼロ。区画ラベル「📖過去問原文」「【事例】/【罪名】」のみ可）。
  事例は `.case-description > .case-scene > .case-paragraph`（Lexia の extractCaseContext が各設問へ文脈添付）、
  記述/罪名列は `.tx-original-charges > .tx-charge`（丸囲み `.tx-charge-mk`）。CSS は GENESIS-CARD 同梱＝複製で自動継承。
  **各記述が独立自己完結の型（逐語のインラインカードがそのまま原文）では作らない**（長文の二重掲載になるだけ）。
  一問一答の数＝実質の記述数（表面の選択肢記号数ではない）。**G62** が `.ox-row` 数＝`.tx-charge` 数＝answer-key 長を、
  **G61** がマーカー字下げ（text-indent:0）を機械保証する。実例＝`刑TX374_lex`・`刑TX401_lex`。
  正典規約＝`docs/tx-v12.2.1-inline-lock.md` §v13n／`spec/tx-v13.1.0-loopcard-core.md` 第1-bis項。
- **合格実例（型別テンプレ・複製起点ではなく“構造の写経元”）**：
  | 型 | 実例 _lex | 版 | 何を写すか |
  |---|---|---|---|
  | 穴埋め・N=5・redesign完 | `刑TX368_lex` | v13.1.0 | v13.1.0 の全レイヤー（nb-badge✍規範核・data-brief-mark・trap）。**redesign層の第一参照**。 |
  | 組合せ・N≠5・COMBOエンジン | `刑TX089`(4)/`刑TX174`(6)/`刑TX218`(4)/`刑TX256`(6)`_lex` | v13.0.0 | N≠5 の記述札／ox-row／`#stmt-N` 配置と `[SCRIPT-COMBO]` の COMBOS/OFFICIAL/ORDER/STEP 配線。**⚠ answer-key は写すな**＝4本中3本（174/218/256）が L4 全○退化（判別性ゼロ・integrity NG）。キーの作り方は下行の混在キー gold に従う（2026-07-11 監査） |
  | 組合せ→独立命題分解・混在キー gold | `刑TX406`(×○××○)/`刑TX408`(×○○××)/`刑TX416`(○×○○×)/`刑TX433`(○×○×)`_lex` | v13.1.0 | 組合せ素材を自己完結の実体命題へ分解し、一部を distractor 差し替えで×にした**判別性ある answer-key** の写経元（キー設計・命題化の中身はこちら） |
  | 見解適用 | `刑TX290_lex` | v13.0.0 | `.choice-premise` の見解再掲と論点コア置換。 |
  ※ v13.0.0 実例は nb-badge/brief-mark を欠くので、**redesign層は必ず刑TX368＋GENESIS-CARD に合わせる**（構造だけ v13.0.0 実例から借りる）。

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
  - **判例百選 配線（該当時・ARIADNE spec §11-1-ter と対称）**：その判例が判例百選収録なら開始タグに
    `data-hyakusen="{科目}百選{巻}-{番号}"` を付す（`references/hyakusen/_index-{科目}.md` で判決日・裁判所種別から逆引き）。
    TX は**短答＝簡潔**なので **番号アンカーのみ**（フル百選深度は ARIADNE 側の責務）。id は `case-{裁判所略号}-{元号1字}{年}-{月}-{日}`
    （Lexia の caseId 結合キー＝ARIADNE の `ref-case-…` と `ref-` 除去で一致）。未収録判例・索引未整備科目には付さない。
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
feature-tag 先頭＝**`TX v12.2.1 LOOP-CORE`**（必須）。続けて genesis-core-baseline／editorial-reskin／
synthesis-subcards／part-b-plus-cross-column／refs-hogo-eki-shushi-smokeblue／case-judgment-badge-note／
mindmap-tree-and-radial／deep-volume-separated／palette-tier-3（大前提=V3／PARTA=natural-mild／他=4分類）／
display-lock-v12.2.1／`palette: {名} (P{N})`／svg-overlap-checked／content-independence／jp-prefix-naming。

#### 4h. 二系統出力（公式／Lexia 用 _lex に分離・active v12.2.1 最重要）

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
4. **図解（TX-DGM・§v13p・2026-07-13）**：物語の**効く論点**（対比・裏命題ペア・分岐・時系列）のラベル段落直後へ
   `.tx-dgm`（対比レーン／ステップ＋分岐・許可クラスのみ）を置き、**同一図解を対応カードの `.syn-path` 直後にも複製**
   （`data-dgm="{番号}-{連番}"` 同期・G67）。導入/まとめへ強制しない（偽図解の禁止）。CSS は GENESIS-CARD 複製で自動継承。

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

> **省エネ検証方針（恒久・[[feedback_lean_verification_author_once]]）：** 消費の主因は検証スクリプトではなく「多重敵対レビュー＋再修正ループ」。よって検証は次の2段だけにする：
> **(a) 安いpython機械ゲート（下記 14-15・トークンほぼ0）を必ず通す**＝validate-tx-core・check-duplicates・check-tx-lex-engine・check-tx-reuse・check-lexia-book-quality・check-lex-oxgrid-integrity（特殊型 L1-L4・strict）。
> **(b) 執筆者本人が軽い自己チェックを1回**＝内部整合（条文番号/項が本文と符合・label↔body 一致・ox-stmt正誤と結論一致・記号フリー）。
> **(c) 的を絞ったWeb一次確認は残す**：判例名・年月日・裁判所種別（最判/最決/大判）・学説か判例か・**その判例の実在**は自己整合では検知できない。**確信の持てない/非著名/下級審の引用だけ**、裁判所裁判例検索・e-Gov・判例百選等で数回確認する（著名判例＝最大判・百選常連は不要）。旧公式（Codex期）本文を流用する場合は特に、埋め込まれた判例誤りを継承しうるので (c) を省かない。
> **やらないこと：** 別エージェントの5並列敵対レビュー、機械整形後の際限ない再修正ループ、生成やり直しの多重掛け。品質は執筆段階で作り込む。**(c) は "残す安全網" であり、廃止対象の敵対レビューと混同して一緒に飛ばさない。**

14. **両ファイルを検証**（二系統）：
    - `python scripts/validate-tx-core.py outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html`（**ox-grid 必須**）
    - `python scripts/validate-tx-core.py outputs/000_TX/{科目}/{接頭辞}{NNN}.html`（**公式＝single/multi 可**。G23/G25 は公式で自動緩和）
    - `python scripts/check-tx-lex-engine.py outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html`（単一エンジン・script2本・G41〜G45／G50-G64）
    - `python scripts/check-lex-oxgrid-integrity.py outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html`（**特殊型 L1-L4＝○×矛盾/組合せ当否/全○退化。新規生成は strict＝NG が出たら判別性ある○×へ直してから配信**。TJRランナーと同基準・2026-07-11 監査で追加）
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
    `Generated: YYYY-MM-DD HH:MM / TX v12.2.1 LOOP-CORE`・class=lexia-genmeta を刻む・冪等）。素の git commit でも
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
