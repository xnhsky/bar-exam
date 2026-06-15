---
description: 新規 TX コア（メイン）を問題 PDF から生成（v11.0.0 LOOP-CORE：GENESIS-CORE baseline + PART A ox-grid + 記述単位 PART B + 肢単位管理）
---

新規 TX コア HTML（短答式・周回＋誤答修正が単体で完結するメイン）を問題 PDF から生成する。

> **v11.0.0 LOOP-CORE 経路（2026-06-13 確定）**：正典 `spec/tx-v11.0.0-core.md`（v0.4）。
> 過去問を**問題単位でなく記述（肢）単位で管理**する設計に対応。
> - **PART A は ox-grid（5記述の○×収集）＋機械可読 answer-key**（Lexia 肢キー記録の一次情報源）。
> - **PART B は出題形式によらず記述（ア〜オ）単位**。choice-points は論点コアを前倒し。教授は①②のみ。
> - **PART C・PART D（12問ドリル）は廃止**。深掘り層（教授③④・判例完全プロファイル・フローチャート・
>   PART C）は別冊 `-deep.html`（`/deepen-tx` で誤答データ解禁時に後追い生成）。
> - 参考条文・判例＝条文（文言＋保護法益＋制度趣旨）／判例（重要度濃淡）。体系ツリー＋放射マップの2枚。
> - 唯一の起点は `canonical/GENESIS-CORE.html`。validate は `scripts/validate-tx-core.py`（G1〜G26）。
> - 旧 v10 GOLD-SKELETON（GENESIS.html・PART C/D・validate-tx-gold.py）は既存197問の保守に限定。

引数：問題 PDF のパス（例：`inputs/tx-pdfs/312.pdf`）

---

## 必須手順

### Phase 0：環境確認（最優先）

0a. **outputs/tx/{対象科目}/ に既存ファイルがあるか確認**。既存でも **template として Read/Edit 起点にしない**。
    同番号が既存の場合のみ上書き可否を確認。
0b. **直近ログで「template 流用経路」（`Read outputs/*.html` / `cp outputs/*.html`）が選ばれていないか確認**。
    痕跡があれば即停止して `canonical/GENESIS-CORE.html` から再開。

### Phase 1：PDF 解析と配色 V3 判定

1. **PDF 読解**：問題番号・科目・年度・全記述（ア〜オ）・正解・正答率・出題テーマ・出題形式を抽出。
   - **記述別の正誤（○×）を必ず確定**（ア:○/× … オ:○/×）＝ox-grid の answer-key と final-answer 表の素。
   - 組合せ問題でも「組合せ番号」ではなく**各記述の○×**を一次データとして扱う（導き書§3-1）。
2. **冒頭応答必須**：「正答率 __%→パターン_『___』 → 採用パレット『___』」を最初に出力。
3. **パターン判定**（配色 V3）：≥60%→P1 ピンク系／40〜60%→P2 グリーン・ブルー系／<40%→P3 バイオレット系。
4. **パレット選定**（11個から1つ・問題ごとに別）：テーマの重さ・難度・罪名イメージ・正解の意外性で AI 判断。
5. **5色役割割当て**（`memory/reference_palette_v3.md`）：ベース70%`--base`／メイン25%`--accent`／
   アクセント5%`--mid`（11パレット内 chip 借用・palette外 hex 禁止）／サブ1`--soft`／サブ2`--light`／文字`--bg-dark`。
   派生色は bg系 L=55-65 mid-tone 制限、text系 L<40 可。`--border-mid` は白系/クリーム系双方に視認可能な濃さ。
6. **Semantic exception**：✓緑`#438B48`/`#7BA980`・🏆金`#ffd54f`/`#ffaa00`（[[feedback-semantic-exceptions]]）。

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
  条文・判例で足り、二重掲載しない（ユーザー指示）。
- A-2 `.answer-area`：
  - `data-answer-type="ox-grid"`／`data-correct-value="××○×○"`（記述ア〜オの正誤を○×で連結）
  - 5 `.ox-row`（`data-stmt="ア"…`）。各行 `.ox-label`＋`.ox-stmt`（記述の短い要約）＋`.ox-btn`（○/×・`data-value`）
  - `<button class="reveal-answer-btn" type="button" disabled>解答を表示</button>` 必須
  - `data-explanation` 先頭に正解値リテラル禁止（AP-37）。組合せ導出ナラティブを書かない（G21）
  - **final-answer 記述○×一覧表（G23）**：`<table class="statement-verdict-table" data-answer-key="ア:x,イ:x,ウ:o,エ:x,オ:o">`
    ＋各行 `<tr data-stmt="ア" data-verdict="x">`＋論点コアのセル。`.final-answer` は hidden（reveal で JS が開く）。
    **answer-key の o/x は data-correct-value と必ず一致**。

#### 4d. PART B 差替（記述ア〜オ・記述単位）
各 choice-section（choice-1=記述ア…choice-5=記述オ）の**バッジは単一記述（ア〜オ）**（組合せ見出し禁止・G20）。
ブロック順を厳守：
1. `.choice-header-block`：`.choice-big-badge`（ア）＋`.verdict`（✓/✗＋法理とのズレ一文・組合せ判定を書かない）＋`.choice-summary`
2. **`.choice-points`（論点コア・前倒し）**：2〜4点。各バレットの主語は法概念（規範コア／判例の結論と射程／
   区別基準／決め手の限定句）。任意で1点「ひっかけの型」（`exam-mark` マーカー流用）。
   **禁止：正解は肢N／組合せ判定／本記述は誤り・正しい／他記述参照「記述Xは」（G22）**
3. `.sub-card.original`（記述原文）
4. `.sub-card.explanation`（解説原文：法理の説明→本記述がどこでズレるか の順）
5. `.sub-card.basis-link`（参考条文・判例セクションへのアンカー）
6. `.sub-card.professor`：**①ポイント・②考え方の道筋のみ**（`prof-num` 1,2）。③イメージ④あてはめ・
   key-phrase-box・analogy・warning・cross-link は**書かない**（別冊 D-1 送り）。

#### 4e. 参考条文・判例 差替（#basis）
本問関連の条文・判例のみ。
- 条文カード（`.basis-card.statute-card`）：文言＋**保護法益**＋**制度趣旨**（`<strong>保護法益</strong>`/
  `<strong>制度趣旨</strong>` の hanging 行）。要件効果の網羅一覧は別冊。
- 判例カード（`.basis-card.case-card`）：**重要度濃淡**。★★★＝事案要旨＋判旨核心＋射程の段落要約、
  補助判例＝事件名＋規範。**【事案】【判旨】【補足】のラベル付き完全プロファイルは書かない（G24・別冊D-2）**。
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
feature-tag 先頭＝**`TX v11.0.0 LOOP-CORE`**（必須）。続けて genesis-core-baseline／part-b-statement-unit／
choice-points-front-loaded／refs-hogo-eki-shushi／mindmap-tree-and-radial／deep-volume-separated／
palette-v3-11-named／`palette: {名} (P{N})`／svg-overlap-checked／content-independence／jp-prefix-naming。

### Phase 5：SVG 重なり機械検査（体系ツリー＋放射マップ）

12. 2枚の `<rect>`/`<ellipse>` の bounding box を計算し全ペア AABB 衝突判定（衝突 0・マージン16px以上）。
13. 衝突時は viewBox 拡張を最優先（[[feedback-svg-box-overlap]]）。

### Phase 6：検証と配信

14. **`python scripts/validate-tx-core.py <出力ファイル>`** を実行。
15. **G1〜G26 ERROR 0 件確認**（特に G20 記述単位・G21 禁止句・G22 choice-points・G23 answer-key・
    G24 完全プロファイル不在・G25 ox-grid・G26 PART D不在）。WARNING は配信可。
16. ERROR があれば該当箇所を修正し再検証。視覚確認推奨 → `present_files`。

### Phase 7：git コミットで永続化（§9）

17. 検証通過後 `git add outputs/tx/{科目TX}/{ファイル名}.html` → 本問単位で `git commit`
    （例：`feat(刑TX): 刑TX346 を v11 LOOP-CORE で生成`）→ push（本線運用は master へ集約・§8）。
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
