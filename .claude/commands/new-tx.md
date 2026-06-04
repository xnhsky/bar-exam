---
description: 新規 TX ファイルを問題 PDF から生成（v10.0.0-gold-skeleton：GENESIS baseline + 配色 V3 + SVG 重なり検査）
---

新規 TX ファイル（短答式 HTML カード）を問題 PDF から生成する。

> **v10.0.0 GOLD-SKELETON 経路（2026-05-27 確定・2026-05-28 配色 V3 移行）**：刑TX311 で確定した
> 「baseline HTML スケルトン + 配色 V3 (11 名前付きパレット・5 役割定義) + SVG 重なり機械検査」の
> 3 本柱経路を新規生成の唯一の標準とする。
> 旧 v9.2.0 DEEP-DIVE 経路（§Annex B body skeleton + 6 段階 Write）は廃止。
> 旧 render.py 経路（JSON-render）も新規生成では使用しない（WIP 上書き事故予防）。

引数：問題 PDF のパス（例：`inputs/tx-pdfs/312.pdf`）

---

## 必須手順

### Phase 0：環境確認（最優先）

0a. **outputs/tx/{対象科目}/ に既存ファイルがあるか確認**
    - 既存ファイルが存在しても **template として Read/Edit 起点にしない**
    - 同番号が既存の場合のみユーザーに上書き可否を確認

0b. **`_quarantine*` や非 canonical フォルダが復活していないか確認**
    - 復活している場合は `bar-exam-archive\` への再排除を提案

0c. **直近のセッションログから「template 流用経路」が選ばれていないか確認**
    - `Read outputs/*.html` や `cp outputs/*.html` の痕跡があれば即停止して
      `canonical/GENESIS.html` から再開

### Phase 1：PDF 解析と配色 V3 判定

1. **PDF 読解**：問題番号・科目・年度・全選択肢・正解・正答率・出題テーマ・出題形式
   （single-choice-5 / ox-grid-5 / multi-choice / etc.）を抽出

2. **冒頭応答必須**：「正答率 __%→パターン_『___』 → 採用パレット『___』」を最初に出力

3. **パターン判定**（配色 V3）：
   - 正答率 ≥ 60% → **P1** ピンク系（候補：Sweet Berry / Fresh Citrus / Rose Mist / Antique Pearl / Maison Blanche）
   - 正答率 40〜60% → **P2** グリーン・ブルー系（候補：Crystal Blue / Dusty Sage / Mint Tea / Fresh Mint）
   - 正答率 < 40% → **P3** バイオレット系（候補：Twilight Violet / Sunset Harmony）

4. **パレット選定**（11 個から 1 つを AI 判断・問題ごとに別）：
   - テーマの重さ（道徳論点／重罪 → Antique Pearl / Dusty Sage / Twilight Violet）
   - 難度（易 → Rose Mist / Fresh Mint、難 → Maison Blanche / Sunset Harmony）
   - 罪名イメージ（財産罪 → ピンク系、手続 → Crystal Blue、身体犯 → Sunset Harmony）
   - 正解の意外性（罠多い → アクセント反対色強め、素直 → 同系統サブで統一）

5. **5 色役割割当て**：選定パレットの 5 色を以下に対応させる
   （`memory/reference_palette_v3.md` カタログ参照）：

   | 役割 | 比率 | CSS 変数 | 選定基準 |
   |:--|:-:|:--|:--|
   | ベース | 70% | `--base` | 最も pale で大面積背景に展開できる色 |
   | メイン | 25% | `--accent` | palette タイトルが描かれている最 chromatic な色（chip 直接使用・改変禁止） |
   | アクセント | 5% | `--mid` | メインと色相が離れた contrast 色。**11 パレット内 chip からのみ借用可**（P 越境 OK・palette 外独自 hex 禁止） |
   | サブ 1 | 残 | `--soft` | card surface に使えるニュートラル色 |
   | サブ 2 | 残 | `--light` | 補助 surface・薄塗り用 |
   | 文字色 | — | `--bg-dark` | 白・黒・黒寄りグレー（text 用は L<40 dark 可） |

   **派生色 10 個（2026-05-28 改訂・mid-tone 制限）：**
   - bg 系派生（`--accent-darker` / `--accent-soft` / `--accent-3` / `--border-mid`）は
     **L=55-65 の mid-tone に制限**（gradient で white text を contrast 維持するときは
     mid-tone でも可・真の dark L<40 は禁止）
   - text 系派生（`--kp-text-color` / `--freq-high-deep` / `--freq-mid-deep` / `--freq-low-deep`）
     は L<40 dark 可（text なので濃い方が読みやすい）

   **コントラスト制約（最重要・2026-05-27 追加 / V3 でも維持）**：
   - **`--border-mid` は `--paper`（白系）と `--base`（クリーム系）の双方に対し
     視認可能な濃さを確保**（推奨：HSL の L < 65、目安として #C0B0D0 より暗い）
     - 過去事故：刑TX310 で `--border-mid:#C3B4D1`（薄ラベンダー）に設定したため
       表罫線・cross-card 境界が背景と同化（コントラスト ~1.4:1）
   - **濃色（`--accent` / `--bg-dark` / `--accent-darker`）を背景に使う場合、
     その上の text は必ず light variant（`--paper` / `--light` / `--base`）を充てる**
   - **V3 11 パレットは全て pastel/soft なので、`--accent`（メイン）をそのまま
     background に使うと contrast 不足になりやすい**。メイン色は header／heading の
     text 色や border 色として使い、background は base/soft/light の薄色を採用

6. **Semantic exception**（[[feedback-semantic-exceptions]]）：
   - ✓ 緑（`--recall-correct`）：`#438B48` / `#7BA980` を全パレットで借用
   - 🏆 金（ARENA）：`#ffd54f` / `#ffaa00` inline hex で保持（CSS 変数化しない）

### Phase 2：ファイル名・出力先の確定（CLAUDE.md §2）

7. **PDF ファイル名から番号抽出**：最初の連続数字 → 3 桁ゼロ埋め

8. **科目接頭辞・出力先決定**：
   - 刑法 → `outputs/tx/刑TX/刑TX{NNN}.html`
   - 憲法 → `outputs/tx/憲TX/憲TX{NNN}.html`
   - 民法 → `outputs/tx/民TX/民TX{NNN}.html`
   - 商法 → `outputs/tx/商TX/商TX{NNN}.html`
   - 民訴 → `outputs/tx/民訴TX/民訴TX{NNN}.html`
   - 刑訴 → `outputs/tx/刑訴TX/刑訴TX{NNN}.html`
   - 行政法 → `outputs/tx/行政TX/行政TX{NNN}.html`

9. **数字抽出不能なら処理中断** → ユーザーに番号確認

### Phase 3：Baseline スケルトンの取得

10. **`canonical/GENESIS.html` を Read**（構造参考の唯一の正典）
    - 例外：`canonical/KTX301.html` も「構造参考」として Read 可
      （ただし 311 baseline の方が v10.0.0 設計に沿うため優先）

11. **対象ファイル名でコピー作成**（PowerShell `Copy-Item` または Write 経由）：
    ```powershell
    Copy-Item canonical/GENESIS.html outputs/tx/{科目TX}/{接頭辞}{NNN}.html
    ```

12. **コピー直後に本文初期化**（content-independence 確保）：
    - PART A `.problem-text` 本文
    - 各 choice-section の `.sub-card.original`／`.sub-card.explanation`／
      `.sub-card.basis-link`／`.sub-card.professor` 本文
    - PART A-3（参考｜共通根拠条文・判例）の各 `.basis-card-body` 本文
    - PART C C-1〜C-7 各 section 本文（table 内容含む）
    - SVG 内の `<text>` 要素テキスト（座標・class は据置・テキストのみ空文字列化）
    - PART D 前提ブロック `.arena-premise` の各 `.arena-premise-item` 本文
    - PART D drill-block × 12 の問題文・解説
    - footer-spec 1〜3 行目
    - これらを **空文字列で初期化**してから問題 PDF を見て新規執筆

### Phase 4：section-by-section 内容差替

各 section を独立して差替える。**1 メッセージで 50KB 超の Write/Edit は禁止**
（API socket error 予防）。Edit 単位で section ごとに分割。

#### 4a. HEAD（`<style>` 内 `:root{}`）の配色 V3 適用
- Phase 1-5 で決定した CSS 変数 ~20 個を `:root{}` に反映
  - 主要 6 個：`--base`(70%) / `--accent`(25%) / `--mid`(5%) / `--soft`(サブ1) / `--light`(サブ2) / `--bg-dark`(文字色)
  - 派生色 10 個（`--accent-darker` / `--accent-light` / `--mid-warm` / `--border-mid` / `--kp-text-color` 等）
- **V3 contrast 規律**（[[project-palette-v3]] / [[reference-palette-v3]]）：
  - 11 パレットは全 pastel なので、chip 1〜5 をそのまま `--accent` に当てると白文字背景に contrast 不足
  - `--accent` は palette identity hex を **HSL で暗くした派生**を採用（例：Antique Pearl chip 1 #D4B5C4 → `--accent: #A07895`、palette identity は `--accent-light` で保存）
  - `--mid` は palette 内 contrast 色がない場合、**palette 外の反対色 dark teal/dark mauve 等**を AI 判断で導入（例：Rose Mist は全部 rose 系なので `--mid: #5A8B8E` dusty dark teal を外挿）
- **structural CSS 規律**（GENESIS baseline で確立、改変禁止）：
  - 見出し系 12 セレクタ（`.section-title` / `.basis-card-header` / `.part-title` / `.container > section > h3` / `.memory-item .mem-title` 等）は **`color:var(--bg-dark)`** で固定
  - badge gradient は `linear-gradient(135deg, var(--accent), var(--accent-darker))` パターン（旧 `var(--accent), var(--mid)` は pale palette で右端白文字が消える構造的問題）
  - SVG tree L2/L3 active text は `--paper` 白（active cells の bg `--mid` は dark teal）
  - freq-mid / freq-low / priority-b / priority-c badge は `color:var(--bg-dark)`
- header／footer の表示テキストには **配色情報を書かない**（パレット名・役割割合・「AI 自由選定」等）

#### 4b. HEADER 差替
- `<div class="doc-header">` の問題番号
- `<h1>` の問題タイトル（出典・テーマ）
- `.exam-badge`（科目／試験種別／年度／問題番号）
- `.theme-tag`（本問の主要論点 5〜10 個）
- `.exam-meta`：**正答率と難度のみ**（配色記載なし）
- `.toc-row`（本問の section リンク）

#### 4c. PART A 差替（出題形式に応じて）
- A-1 `.problem-text`：PDF 逐語コピー
- A-2 `.answer-area`：
  - `data-answer-type` を出題形式に合わせて設定（single / multi / ox-grid）
  - `data-correct-value` を正解値で設定（例：`5` / `1,3` / `11112`）
  - `<button class="reveal-answer-btn" type="button" disabled>解答を表示</button>` 必須
  - `data-explanation` 先頭に正解値リテラル禁止（AP-37）

#### 4d. PART B 差替（記述ア〜オ または ○× 各記述）
- 各 choice-section に 4 sub-card（original / explanation / basis-link / professor）
- prof-heading 4 段構成 + key-phrase-box + analogy + warning + cross-link
- ref-stat / ref-case リンクは本問関連条文・判例の id を参照

#### 4e. A-3（参考｜共通根拠条文・判例）差替
- 本問に直接関係する条文・判例のみ 3〜5 枚に絞る（AI 判断）
- `.basis-card.statute` / `.basis-card.case` で振り分け
- 各 `.basis-card-body` は本問の文脈で執筆

#### 4f. SVG 差替（座標は 311 baseline のまま、テキスト・色 class のみ）
- **体系ツリー** (mindmap-tree)：L0/L1/L2/L3 の text を本問体系に
- **論点マインドマップ放射** (mindmap-radial)：8 主要枝・サブ要素 text を本問論点に
- **C-5 総合フローチャート** (flow-svg)：decision diamond / chip / end の text を本問判断フローに
- 詳細は **Phase 5 SVG 重なり検査** で全 bounding box を機械検査してから出力

##### 4f-rules. SVG class 命名規律（最重要・2026-05-27 追加）

- **GENESIS.html の `<style>` 内に CSS 定義がある class 名のみ使用可**
  - 新たな class 名を勝手に発明しない（例：`branch-active` / `tx-branch-active` / `node-positive` 等の独自命名は禁止）
  - SVG `<rect>` / `<text>` 等で `class` 属性を付ける際は、GENESIS のスタイル定義済 class（例：`branch-fill` / `tx-branch` / `sub-elem` / `tx-elem` / `sub-case` / `tx-case` / `sub-statute` / `tx-statute` / `issue-branch-fill` / `tx-issue-ttl` / `tx-issue-body` 等）から **必ず選択**
  - 独自命名された class は CSS 規則がないため SVG デフォルトの `fill="black"` が適用され、**黒塗りボックス**として描画される（過去事故：刑TX310 v10.0.0 first-light で `branch-active` 黒塗り 3 箇所）
- **肯定/否定など差別表示が必要な場合**：
  - 既存 class の組合せで対応（例：肯定＝`branch-fill`、否定＝`branch-fill` + stroke-dasharray を inline 適用）
  - または新 class を **GENESIS.html の CSS にも追加**してから使用（baseline 改修扱い・別 commit 推奨）

#### 4g. PART C 差替（C-1〜C-7）
- C-1 体系図解説（key-phrase-box + cmp-table）
- C-2 概念比較・全肢俯瞰（cmp-table 2 枚）
- C-3 cross-grid（関連の深い科目との接続・3 cross-card）
- C-4 学説対立（cmp-table + theory-detail-grid：主要説 vs 少数説）
  - 主要 2 説を AI 判断で選定
  - dt.why-adopted / why-not-adopted 必須
- C-5 総合フローチャート（4f で配置済）+ 解説
- C-6 ref-cases（重要判例 1〜3 件詳細）
- C-7 memory-item（3 層 priority-a/b/c）

#### 4h. PART D 差替（ARENA drill 12 問）
- **冒頭に前提ブロック `.arena-premise` を必ず配置**（`arena-intro` の直後・`arena-counter` の前）：
  - 12問エリアを**自己完結**させ、見解・事案・記述を確認するため上部 PART を遡読させない
  - `.arena-premise-item` を最低 2 件（事案／見解／各記述ア〜オ等）。本問の要点のみ簡潔に再掲
  - 構造シェル（`.arena-premise` / `-head` / `-icon` / `-note` / `-body` / `-item` / `-label`）と
    `.arena-premise-note` 定型文は GENESIS から逐語コピー。中身（事案・見解・記述）は本問固有で執筆
- ○×=6:6 で構築（本問オリジナル）
- 各 drill-block：問題文・選択肢・解説（本問関連で完結）
- **「本問の正解は肢N」型の正解再問 DRILL は禁止**（答えの暗記は学習効果ゼロ）：
  - DRILL 12 等で「本問の正解」「正解は肢N」「誤っている記述の組合せは肢N」を **quiz-question に書かない**
  - 代わりに**転用可能な法理**（判定基準・規範・概念）を問う設問にする
    （例：虚像射撃／実像狙撃の判定、規範の射程、構成要件の核心命題）
  - 解説 `.quiz-answer` は正解に言及して可（禁止は設問文 `.quiz-question` のみ）
  - `validate-tx-gold.py` G17（正解再問禁止）・G18（前提ブロック必須）が機械検出

##### 4h-bis. 1 drill-block の正典フォーマット（GENESIS 構造シェル・逐語）

各 drill は次の構造を厳守する。`{TAG}` `{○or×}` `{設問}` `{解説}` のみ本問固有で差替え、
class／属性キー／ネスト順は逐語コピーする。

```html
<div class="drill-block">
  <div class="drill-label"><span class="drill-num">DRILL&nbsp;NN</span><span class="drill-tag">{TAG}</span></div>
  <div class="self-check-quiz" data-arena="1" data-correct-value="{○or×}" data-explanation="{解説}">
    <div class="quiz-question">Q. {設問（正解再問は禁止・転用可能な法理を問う）}</div>
    <div class="quiz-buttons"><button class="quiz-btn" type="button" data-correct="{TRUE_IF_○}" data-value="○">○</button><button class="quiz-btn" type="button" data-correct="{TRUE_IF_×}" data-value="×">×</button></div>
    <div class="quiz-answer" hidden=""><span class="quiz-result"></span>{解説（data-explanation と同一文）}</div>
  </div>
</div>
```

**鉄則（一発で正しく出すための4項）：**
1. **`data-correct` と `data-correct-value` を必ず一致**させる。正解 `○` → ○ ボタン `data-correct="true"`／
   × ボタン `data-correct="false"`。正解 `×` → 逆。**両方 true／両方 false は不可**（採点 JS が破綻）。
2. **`data-explanation` 属性の文と `.quiz-answer` 内の本文は同一文**にする（解説は 2 箇所に同じものを書く）。
3. `data-value` は ○ ボタン＝`○`、× ボタン＝`×` で固定（差替えない）。
4. ○:× 比率は概ね半々。各設問は**転用可能な法理**（規範・判定基準・概念・判例の射程）を問い、
   「本問の正解は肢N」型は書かない（G17）。

#### 4i. footer-spec 差替
- 1 行目：`<strong>{接頭辞}{NNN}</strong>・{科目}（{出典}）`
- 2 行目：`正答率 {N}%／難度 {★}`（**配色情報は書かない**）
- 3 行目：`作成日：{YYYY-MM-DD}`
- `.footer-meta-hidden` 内 feature-tag（順序自由・先頭のみ固定）：
  - `TX v10.0.0 GOLD-SKELETON`（必須・先頭）
  - `genesis-baseline`
  - `palette-v3-11-named`
  - `palette: {パレット名} (P{N})` — 例：`palette: Antique Pearl (P1)`
  - `roles: base 70% / main 25% / accent 5% / sub 2`
  - `svg-overlap-checked`
  - `content-independence`
  - `jp-prefix-naming`

### Phase 5：SVG 重なり機械検査（必須・新規）

13. SVG 3 種すべての `<rect>` / `<ellipse>` / `<polygon>` について bounding box
    `(x_min, x_max, y_min, y_max)` を計算

14. 全ペアで衝突判定：
    `x_min_A < x_max_B AND x_max_A > x_min_B AND y_min_A < y_max_B AND y_max_A > y_min_B`
    が成立してはならない

15. マージン 16px 以上を確認（重なりなくても窮屈な隙間は避ける）

16. **衝突発見時の対処順序**（[[feedback-svg-box-overlap]]）：
    1. viewBox 拡張（最も安全・他要素への影響なし）
    2. 中心から放射する要素を更に外側へ
    3. ラベル短縮（最終手段）

### Phase 6：検証と配信

17. **新仕様 validate 実行**：
    ```bash
    python scripts/validate-tx-gold.py <出力ファイル>
    ```

18. **G1〜G16 ERROR 0 件確認**：
    - G1〜G5：構造（HEAD/HEADER/PART A〜D/footer 存在）
    - G6〜G8：配色 V3（:root 内 5 役割 CSS 変数 + 派生色 10 個・配色情報がヘッダー／フッター本文にない）
    - G9〜G11：SVG（3 種存在・ボックス重なり 0 件・viewBox 余白十分）
    - G12〜G13：content-independence（KTX301 / GENESIS 本文逐語コピー禁止）
    - G14〜G15：命名規則（ID 形式・出力先サブフォルダ）
    - G16：SVG class 整合性（未定義 class の黒塗り防止）
    - G17〜G18：PART D 自己完結（正解再問 DRILL なし・前提ブロック存在）

19. **視覚確認推奨**：ユーザーがブラウザで開いて gold quality 到達判定

20. **ERROR 0 件 + 視覚 OK** → `present_files` で完了報告

21. **ERROR があれば**：該当箇所を修正し、再検証

---

## 鉄則（絶対遵守）

### template 流用の物理的禁止（最重要）

- **`outputs/*/` 配下の既存 HTML を別問題生成の template として
  `cp` / `Read` / `Edit` の起点にすることは絶対禁止**
- **唯一許可される起点**：`canonical/GENESIS.html`（最優先）
  および `canonical/KTX301.html`（補助・構造参考のみ）
- 既存 `.html` を「速い経路」として参照することは canonical text leakage の温床

### canonical text leakage の禁止

- canonical/GENESIS.html および KTX301.html の本文・解説・判例引用を
  別問題ファイルにコピー禁止（AP-42）
- スケルトンを clone した直後に **本文を空文字列で初期化**してから執筆開始

### render.py 経路の禁止

- **`python scripts/render.py {問題番号}` 実行禁止**：JSON-render 結果が target ファイルを
  上書きし WIP 作業全消失（過去事故あり）
- 新規生成は問題 PDF + canonical baseline のみから新規鋳造

### 配色 V3 の越境（Semantic exception）

- ✓ 緑（recall-correct）：全パレットで #438B48 / #7BA980 を借用（V3 11 パレットは全 pastel で vivid green を持たないため強制継承）
- 🏆 金（ARENA）：全パターンで #ffd54f / #ffaa00 inline hex 保持
- 詳細：[[feedback-semantic-exceptions]]

### SVG ボックス重なり禁止

- Phase 5 の機械検査を必ず実施
- 311 で「本問の論点ボックス」が左右サブ要素と重なる事故あり
- 詳細：[[feedback-svg-box-overlap]]

### ヘッダー／フッター本文への配色記載禁止

- `.exam-meta` 内に「配色: P1 …」を書かない
- `.footer-meta-info` に「配色 P1「…」AI 自由選定」を書かない
- 配色情報は CSS の `:root{}` と footer-spec hidden feature-tag のみに記載

### 単一巨大出力の禁止（API socket error 予防）

- **1 メッセージで 50KB 超の `Write` / `Edit` 出力は禁止**
- section-by-section で Edit を分割（各 30〜50 KB 以下）

### 中断・再開時の禁則

- API socket error 等で中断した場合、**既存 outputs/*.html を template として
  参照する経路を選んではならない**
- 必ず canonical/GENESIS.html + PDF から続行
- 失敗した section だけ再生成し、他 section は流用しない

### 行動原則

- **「保守的書き換え」を絶対にしない**（既存コードを引き継ごうとする AI の癖を強制無効化）
- **冒頭応答必須**：「正答率__%→パターン_『___』適用」

$ARGUMENTS
