---
description: 新規 TX コア（メイン）を問題 PDF から生成（v11.1.0 LOOP-CORE：GENESIS-CORE baseline + 誌面リスキン + 3層配色体系 + PART A ox-grid + 記述単位 PART B/B+ + 肢単位管理）
---

新規 TX コア HTML（短答式・周回＋誤答修正が単体で完結するメイン）を問題 PDF から生成する。

> **v11.1.0 LOOP-CORE 経路（2026-06-15 デザイン進化・刑TX327 を昇格）**：構造正典 `spec/tx-v11.0.0-core.md`（v0.4）＋ v11.1.0 誌面/配色規律。
> 過去問を**問題単位でなく記述（肢）単位で管理**する設計に対応。
> - **誌面リスキン**：明朝（Shippori Mincho B1）＋極細罫の編集デザイン（CSS 変数 `--ed-*`・`<style>` §1〜§17）。
> - **PART A は ox-grid（5記述の○×収集）＋機械可読 answer-key**（Lexia 肢キー記録の一次情報源）。
> - **PART B は記述（ア〜オ）単位**。SYNTHESIS 子カード（`.syn-orig`記述原文／`.syn-lead`THE GIST／`.syn-path`①②③／`.syn-image`INTUITION）＋ `.choice-points`(POINT) ＋ `.basis-link`(BASIS)。
> - **PART B+「横断・比較・罠コラム」**（`.cross-column`／cb-cross・cb-compare・cb-trap／col-key・col-warn(TRAP)・col-type(THROUGH-LINE)）。
> - **PART C・PART D（12問ドリル）は廃止**。深掘り層は別冊 `-deep.html`（`/deepen-tx` で誤答データ解禁時に後追い）。
> - 参考条文・判例＝条文（文言＋保護法益＋制度趣旨・**スモークブルー系**）／判例（**判旨に『⚖ 判旨』バッジ＋判旨以外を NOTE 化・コーラル系**）。体系ツリー＋放射マップ（＋深掘りでフロー）。
> - **配色住み分け（v11.1.0・最重要）**：①**大前提**（ヘッダー/フッター/紙面背景/PART見出し・section-title・リンク）＝従来の **V3 3パターン（11パレット）** 基調色。②**PART A 問題・解答エリア**＝**ナチュラルマイルド色**（オリーブ/ベージュ/クールグレー/ダスティピンク/クリーム）。③**それ以外**（PART B/B+・共通根拠・SVG）＝**4分類パレット**（渋/和み/親しみ/晴れやか）の役割固定色。**②③は GENESIS-CORE の §18〜§22 に内蔵（content-independent）＝複製で自動継承し、生成時に再選定・上書きしない**。正誤の○緑/×赤は semantic 維持。
> - 唯一の起点は `canonical/GENESIS-CORE.html`（v11.1.0）。validate は `scripts/validate-tx-core.py`（G1〜G27）。
> - 旧 v10 GOLD-SKELETON（GENESIS.html・PART C/D・validate-tx-gold.py）は既存197問の保守に限定。

引数：問題 PDF のパス（例：`inputs/tx-pdfs/312.pdf`）

---

## 必須手順

### Phase 0：環境確認（最優先）

0a. **outputs/tx/{対象科目}/ に既存ファイルがあるか確認**。既存でも **template として Read/Edit 起点にしない**。
    同番号が既存の場合のみ上書き可否を確認。
0b. **直近ログで「template 流用経路」（`Read outputs/*.html` / `cp outputs/*.html`）が選ばれていないか確認**。
    痕跡があれば即停止して `canonical/GENESIS-CORE.html` から再開。

### Phase 1：PDF 解析と配色 V3 判定（＝**大前提の基調色のみ**）

1. **PDF 読解**：問題番号・科目・年度・全記述（ア〜オ）・正解・正答率・出題テーマ・出題形式を抽出。
   - **記述別の正誤（○×）を必ず確定**（ア:○/× … オ:○/×）＝ox-grid の answer-key と final-answer 表の素。
   - 組合せ問題でも「組合せ番号」ではなく**各記述の○×**を一次データとして扱う（導き書§3-1）。
2. **冒頭応答必須**：「正答率 __%→パターン_『___』 → 採用パレット『___』」を最初に出力。
3. **パターン判定**（配色 V3）：≥60%→P1 ピンク系／40〜60%→P2 グリーン・ブルー系／<40%→P3 バイオレット系。
4. **パレット選定**（11個から1つ・問題ごとに別）：テーマの重さ・難度・罪名イメージ・正解の意外性で AI 判断。
5. **5色役割割当て**（`memory/reference_palette_v3.md`）：ベース70%`--base`／メイン25%`--accent`／
   アクセント5%`--mid`（11パレット内 chip 借用・palette外 hex 禁止）／サブ1`--soft`／サブ2`--light`／文字`--bg-dark`。
   **ただし `--base`（紙面背景・70%surface）は全問固定クリーム `#F7F1E9`（パレット非依存・紙面統一・2026-06-16 確定）。
   パレット選定で base 役割色は使わず `--base` は GENESIS-CORE の `#F7F1E9` を変えない**（残り `--accent`/`--mid`/`--soft`/`--light`/`--bg-dark` のみ問題ごとに割当て）。
   派生色は bg系 L=55-65 mid-tone 制限、text系 L<40 可。`--border-mid` は白系/クリーム系双方に視認可能な濃さ。
6. **Semantic exception**：✓緑`#438B48`/`#7BA980`・🏆金`#ffd54f`/`#ffaa00`（[[feedback-semantic-exceptions]]）。
6-bis. **配色住み分け（v11.1.0・最重要）**：上記 V3 5色は **大前提のみ**（ヘッダー/フッター/紙面背景/PART見出し・
   section-title・リンク）に適用＝`:root` の主要6＋派生のみ設定する。**PART A 問題・解答エリア＝ナチュラルマイルド色**、
   **PART B/B+・共通根拠・SVG＝4分類パレットの役割固定色**は **GENESIS-CORE §18〜§22 に内蔵済み（content-independent）
   ＝複製で自動継承**。生成時に**再選定も上書きもしない**（§18〜§22 の hex は触らない）。正誤○緑/×赤は semantic 維持。

### Phase 2：ファイル名・出力先（CLAUDE.md §2）

7. PDF 番号抽出（最初の連続数字→3桁ゼロ埋め）。数字抽出不能なら**中断**しユーザーに番号確認。
8. 科目接頭辞・出力先：刑→`outputs/tx/刑TX/刑TX{NNN}.html`（憲/民/商/民訴/刑訴/行政 同様）。

### Phase 3：GENESIS-CORE の clone と本文初期化

9. **`canonical/GENESIS-CORE.html` を Read**（v11 コア生成の唯一の起点。GENESIS.html や outputs/*.html は使わない）。
10. **対象ファイル名でコピー作成**（Write 経由 or bash `cp`。前面 PowerShell は Copy-Item がブロックされる→
    `.NET File` か bash を使う・[[feedback-powershell-remove-item-guard]]）：
    `cp canonical/GENESIS-CORE.html outputs/tx/{科目TX}/{接頭辞}{NNN}.html`
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
- **配色オーバーレイ §18〜§22 は触らない（v11.1.0）**：`<style>` 末尾の §18（バッジ共通規約）〜§22（PART A
  ナチュラル色）は content-independent な配色体系（4分類役割色・ナチュラルマイルド色・SVG配色）。`:root` の
  V3 基調色だけ更新し、**§18〜§22 の hex・`!important` ルールは削除も改変もしない**（複製で自動継承）。

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
  - 5 `.ox-row`（`data-stmt="ア"…`）。各行 `.ox-label`＋`.ox-stmt`（記述の短い要約）＋`.ox-btn`（○/×・`data-value`）
  - `<button class="reveal-answer-btn" type="button" disabled>解答を表示</button>` 必須
  - `data-explanation` 先頭に正解値リテラル禁止（AP-37）。組合せ導出ナラティブを書かない（G21）
  - **final-answer 記述○×一覧表（G23）**：`<table class="statement-verdict-table" data-answer-key="ア:x,イ:x,ウ:o,エ:x,オ:o">`
    ＋各行 `<tr data-stmt="ア" data-verdict="x">`＋論点コアのセル。`.final-answer` は hidden（reveal で JS が開く）。
    **answer-key の o/x は data-correct-value と必ず一致**。

#### 4d. PART B 差替（記述ア〜オ・記述単位・v11.1.0 SYNTHESIS 子カード）
各 choice-section（choice-1=記述ア…）の**バッジは単一記述**（組合せ見出し禁止・G20）。GENESIS-CORE の
v11.1.0 ブロック構造を埋める（順序厳守）：
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

#### 4d-bis. PART B+ 差替（横断・比較・罠コラム・v11.1.0）
`.cross-column` 内の 3 つの `.col-block` を埋める（GENESIS-CORE 据置の構造・色は §18〜§22 継承）：
- `cb-cross`（🔗 CROSS）：本問論点を他分野・他罪と結ぶ横断表＋`.col-key`（💡 決め手）＋`.col-type`（THROUGH-LINE＝通底する一本の糸）。
- `cb-compare`（📊 比較）：軸で束ねる比較表＋`.col-key`（💡 詰める順番）。
- `cb-trap`（⚠️ 罠）：`.col-warn`（TRAP N＝誤答の型）＋`.col-type`（THROUGH-LINE）。
- 表・チップ・タブの配色（オリーブ見出し／ゴールド col-key／バーミリオン TRAP 等）は §20 継承。本文のみ差替。

#### 4e. 参考条文・判例 差替（#basis・v11.1.0）
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
feature-tag 先頭＝**`TX v11.1.0 LOOP-CORE`**（必須）。続けて genesis-core-baseline／editorial-reskin／
synthesis-subcards／part-b-plus-cross-column／refs-hogo-eki-shushi-smokeblue／case-judgment-badge-note／
mindmap-tree-and-radial／deep-volume-separated／palette-tier-3（大前提=V3／PARTA=natural-mild／他=4分類）／
`palette: {名} (P{N})`／svg-overlap-checked／content-independence／jp-prefix-naming。

### Phase 5：SVG 重なり機械検査（体系ツリー＋放射マップ）

12. 2枚の `<rect>`/`<ellipse>` の bounding box を計算し全ペア AABB 衝突判定（衝突 0・マージン16px以上）。
13. 衝突時は viewBox 拡張を最優先（[[feedback-svg-box-overlap]]）。

### Phase 6：検証と配信

14. **`python scripts/validate-tx-core.py <出力ファイル>`** を実行。
15. **G1〜G27 ERROR 0 件確認**（特に G20 記述単位・G21 禁止句・G22 choice-points・G23 answer-key・
    G24 完全プロファイル不在・G25 ox-grid・G26 PART D不在）。WARNING は配信可だが、
    **G27（PART A 参照条文）が出たら §4c に従い PDF 原文を確認し、印刷が無ければ削除**してから配信する。
16. ERROR があれば該当箇所を修正し再検証。視覚確認推奨 → `present_files`。

### Phase 7：git コミットで永続化（§9）

17. 検証通過後 `git add outputs/tx/{科目TX}/{ファイル名}.html` → 本問単位で `git commit`
    （例：`feat(刑TX): 刑TX346 を v11.1.0 LOOP-CORE で生成`）→ push（本線運用は master へ集約・§8）。
18. `present_files` 完了報告に commit hash を併記。

### Phase 8：深掘り別冊（任意・後追い）

19. 別冊（`-deep.html`）は**全問では作らない**。Lexia の誤答データが解禁条件（同じ記述を繰返し誤答／
    弱点克服帳に同一論点が反復／直前期）を満たした問題にだけ **`/deepen-tx {NNN}`** で後追い生成
    （GENESIS-DEEP clone・教授③④＋判例完全プロファイル＋フローチャート＋PART C・validate-tx-deep）。

---

## 鉄則（絶対遵守）

- **template 流用の物理的禁止**：`outputs/*/` の既存 HTML を起点に `cp`/`Read`/`Edit` しない。
  唯一の起点は `canonical/GENESIS-CORE.html`。clone 直後に本文を空文字列初期化してから執筆（AP-42）。
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
