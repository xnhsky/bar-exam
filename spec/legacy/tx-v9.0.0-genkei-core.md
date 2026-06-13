# TX v9.0.0 GENKEI 仕様書

**GENKEI-skeleton · forged-from-archetype · readability-enhanced · hanging-indent-grid · single-document-self-sufficient · jp-prefix-naming · content-independence · a2-two-stage-reveal · 3-type-support · spoiler-leak-eradication · spoiler-strong-elimination · ox-grid-fa-unification · host-injection-safe**

> **GENKEI（原型）**: CSS/JS は刑TX300 由来の byte-lock（フォント・色・余白・動作の物理根拠）。HTML body は問題固有内容を抜き去った純粋な骨格スケルトン（プレースホルダ `[...]` ＋ 指示コメント `<!-- 指示: ... -->`）。AI は本仕様書骨格に従い、問題 PDF から解説・本文・判例引用を新規鋳造する。「個別問題の写しを正典とする」v8.x KTX301-canonical 系譜から、「構造の原型のみを規範化する」設計への転換。§0-quad コンテンツ独立性プロトコルが手続的に解こうとしてきた汚染問題を、構造そのもので解消する。

> 司法試験・予備試験 短答式（短答 = Tantō = TX）対策の単問解説 HTML 生成仕様。
> 全 7 法（憲法／民法／刑法／商法／民訴／刑訴／行政法）共通の汎用シリーズ名は **TX**。
>
> **科目別ファイル接頭辞（v8.11.1 canonical・日本語接頭辞 + TX 形式）：**
>
> | 科目 | 接頭辞 | 出力先 | ファイル名例 | レガシー接頭辞 |
> |---|---|---|---|---|
> | 刑法 | **刑TX** | `outputs/ktx/` | `刑TX299.html` | K |
> | 憲法 | **憲TX** | `outputs/kentx/` | `憲TX015.html` | KEN |
> | 民法 | **民TX** | `outputs/mintx/` | `民TX120.html` | MIN |
> | 商法 | **商TX** | `outputs/syotx/` | `商TX045.html` | SYO |
> | 民訴 | **民訴TX** | `outputs/minstx/` | `民訴TX078.html` | MINS |
> | 刑訴 | **刑訴TX** | `outputs/keistx/` | `刑訴TX033.html` | KEIS |
> | 行政法 | **行政TX** | `outputs/gsetx/` | `行政TX092.html` | GSE |
>
> レガシー接頭辞（K/KEN/MIN/SYO/MINS/KEIS/GSE）は v8.10.2 までの体系。**v8.11.1 以降の新規生成ファイルは必ず日本語接頭辞 + TX 形式**を採用し、出力先サブフォルダも上表に従う。詳細は §1-bis 参照。なお byte-level 正典として参照される model file は引き続き **KTX301** と呼称する（model 名称は歴史的識別子として保持）。
>
> **本仕様書は完全自己完結**：本ファイル 1 枚（本仕様書文＋ KTX301 model の §Annex A/B/C を全文埋込）と問題 PDF があれば、追加添付ファイル一切なしに完全な TX ファイルが生成可能。
>
> **v8.11.0 設計哲学：「KTX301 への canonical 移行＋可読性レイヤー canonical 化＋第二次対話セッション（chat-002）の恒久教訓化＋仕様書一元化」**
>
> v8.10.2 までは KTX296 を byte-level 正典とし、各 minor バージョンが「前版の §Annex 群を逐語継承」する系譜的構造をとっていた。v8.11.0 はこの系譜を断ち、**KTX301 を新 byte-level canonical** に昇格させた上で、**§Annex A/B/C を本仕様書 1 枚に完全埋込**し、過去の v8.x 系仕様書への参照を一切要しない自己完結文書とする。

---

## §0-prime. v8.11.1 → v8.11.7 統合差分

> **v8.11.7 の位置づけ**: v8.11.1（jp-prefix-naming + content-independence の本クリーン版基盤）に対し、旧プロジェクトで段階的に開発された v8.11.2〜v8.11.6-hotfix1 の機能を**一括統合**した版。番号衝突を避けるため一部の検査 ID／AP 番号を再採番。

### v8.11.7 改訂サマリ

1. **v8.11.2 由来**：A-2 2 段階開示プロトコル（a2-two-stage-reveal canonical）
2. **v8.11.3 由来**：3 Type 対応（single / multi / ox-grid、`data-answer-type` 属性駆動）
3. **v8.11.4 由来**：spoiler-leak-eradication（PART A 内「N（XX）正解」リテラル消去・data-explanation 先頭リテラル消去・FA 正解の数字のみ表示）
4. **v8.11.5 由来**：spoiler-strong-elimination（`<strong>N（XX）</strong>` 完全削除）＋ ox-grid-fa-unification（FA を `<span class="answer-num">` 形式に統一）
5. **v8.11.6-hotfix1 由来**：host-injection-safe（`<script>` 内 `</body>` リテラル禁止）
6. **番号再採番**：v8.11.1 で導入した「canonical text leakage」AP-30 → **AP-42**／S68〜S72 → **S78〜S82** に renumber。これにより原始 v8.11.x の AP-30〜AP-41／S68〜S77 と衝突せず併存可能

### v8.11.2 改訂 4 項目（A-2 2 段階開示）

1. **A-2 解答エリア 2 段階開示プロトコル**：
   - Stage 1（選択）：選択肢クリック → `.selected` ハイライトのみ。**フィードバック非表示**・**正誤判定なし**
   - Stage 2（開示）：「解答を表示」ボタンクリック → 正解/不正解の verdict と正解値のみ表示。**詳細解説は表示しない**（PART B sub-card.explanation と巻末 FINAL ANSWER で代替）
2. **`<p class="answer-instruction">` の canonical 文言固定**：「選択肢を選んで「解答を表示」を押してください。」（AP-33）
3. **`<button class="reveal-answer-btn" type="button" disabled>解答を表示</button>` 必須**（AP-34）
4. **§22-quinta CSS パッチ**：`.reveal-answer-btn`（4 規則）＋ `.answer-slot.selected` の合計 5 規則を §Annex A に追加
5. **§Annex C JS 改訂**：`handleAnswerSlot` を stage 1 専用化、`handleRevealAnswerBtn` 新設

### v8.11.3 改訂 4 項目（3 Type 対応）

1. **`data-answer-type` 属性で 3 Type 分岐**：
   - `"single"`: 単一選択（`data-correct-value="3"` 等）
   - `"multi"`: 複数選択（`data-correct-value="1,2"` 等・カンマ区切り集合一致）
   - `"ox-grid"`: ○×評価（`data-correct-value="11112"` 等・5 桁文字列で連結比較、各桁が 1/2）
2. **Type B (multi)**：selection-counter UI（「選択中: N / M 個」）＋ FIFO トグル
3. **Type C (ox-grid)**：`.answer-ox-grid` + `.ox-row` UI 新設
4. **§22-sexta CSS パッチ**：`.selection-counter`／`.answer-ox-grid`／`.ox-row`／`.ox-label`／`.ox-btn` 関連規則

**Type 自動判定ロジック：**

| `data-correct-value` パターン | 判定される type | 例 |
|---|---|---|
| `^\d+$` で 1〜2 桁の数字（3 桁目に 1/2 以外も含む） | `single` | `"3"`, `"5"`, `"10"` |
| `^[12]{2,}$`（2 桁以上で各桁が 1 or 2） | `ox-grid` | `"11112"`, `"22122"` |
| `^\d+(,\d+)+$`（カンマ区切り） | `multi` | `"1,2"`, `"3,4"` |

### v8.11.4 改訂 3 項目（spoiler-leak-eradication）

1. **PART A 内「N（XX）正解」リテラル完全消去**（AP-36）：組合せ型問題の選択肢列挙で `<strong>4（ウエ）正解</strong>` 等のネタバレを HTML レベルで強制排除
2. **`data-explanation` 属性の先頭リテラル消去**（AP-37）：`data-explanation="3,4。詐欺罪は..."` のような先頭正解値表示を排除
3. **FA `.answer-num` を正解の数字のみ表示**（AP-38）：
   - single: `<span class="answer-num">N</span>`（変更なし）
   - multi: 正解の数字のみセル化（`ans-incorrect` セル不生成）
   - ox-grid: '1' 桁に対応するラベルのみセル化（'2' 桁はスキップ）※ v8.11.5 で更に統一

### v8.11.5 改訂 2 項目（spoiler-strong + ox-grid 統一）

1. **PART A `<strong>N（XX）</strong>` 完全削除**（AP-39）：正解組合せのみ accent 太字でネタバレする状態を解消、全選択肢を同書式の平文に統一
2. **ox-grid 型 FA を single 形式に統一**（AP-40）：v8.11.4 では multi 構造で表示していたが、A-2 feedback では「正解は 11112」と数字表示しているため、FA も `<span class="answer-num">11112</span>` 形式に統一

**Type 別 FA `.answer-num` 表示仕様（v8.11.5 確定版）：**

| Type | `data-correct-value` 例 | FA 表示 HTML |
|---|---|---|
| **single** | `"3"` | `<span class="answer-num">3</span>` |
| **multi** | `"3,4"` | `<div class="answer-num answer-num-multi"><span class="ans-cell ans-correct">3</span><span class="ans-cell ans-correct">4</span></div>` |
| **ox-grid** | `"11112"` | `<span class="answer-num">11112</span>` |

### v8.11.6-hotfix1 改訂 1 項目（host-injection-safe）

1. **`<script>` 内 `</body>` リテラル禁止**（AP-41）：
   - **背景**：Lexia 等の host アプリは iframe `srcdoc` 注入時に `result.replace(/<\/body>/i, ...)` で**最初に出現する `</body>`** にホスト用 QUIZ_TRACKER スクリプトを注入する。`<script>` 内コメントやリテラルに `</body>` 文字列が含まれていると、本物の `</body>` より先にマッチし、JS 構文が完全崩壊
   - **症状**：iframe 内の全 JS 機能死亡（クイズハンドル・リンクジャンプ・○×ボタン等）
   - **代替表記**：「`body 閉じタグ`」「`</` + `body>`」「`</body\u200b>`（ゼロ幅スペース挟む）」「`< /body>`（半角スペース挟む）」

### 番号再採番マッピング表（v8.11.1 → v8.11.7）

| v8.11.1（私版）の番号 | v8.11.7 統合後の番号 | 内容 |
|---|---|---|
| **AP-30**「canonical text leakage」 | **AP-42** | KTX301 由来文言が別問題に流用される事故。§0-quad の対象 |
| **S68**（KTX301 ブラックリスト） | **S78** | 同上 |
| **S69**（§Annex B 元テキスト 3 単語以上一致） | **S79** | 同上 |
| **S70**（命名規則準拠） | **S80** | jp-prefix-naming |
| **S71**（出力先サブフォルダ整合） | **S81** | 同上 |
| **S72**（PDF 番号抽出整合） | **S82** | 同上 |

原始 v8.11.x チェーンの AP-30〜AP-41／S68〜S77 はそのまま採用。

### v8.11.0 までの差分（既存・継承）

1. **canonical model 交代**：byte-level 正典を KTX296 → **KTX301** に置換。§Annex A/B/C 全文を本仕様書末尾に逐語埋込

2. **PART 順序変更**：A-3 共通根拠条文・判例 section を **PART B の後・PART C の前**に再配置。PART A は問題文＋解答の 2 セクション構成に縮減され、A-3 は実質的に「PART B 直後の総括」位置に移動

3. **§24 readability layer 新設**：第二次対話セッションで段階的に追加された 6 つの可読性レイヤーを canonical 化：
   - §24-1：`.section h3` の小見出し強化（左 4px accent border + 淡 gradient）
   - §24-2：`.cross-grid .cross-card` 奇偶交互背景
   - §24-3：`.memory-list .memory-item` 奇偶交互背景（priority 別）
   - §24-4：`.lead-list` 箱化（左 border・影・dashed リード行区切り・hover）
   - §24-5：全 `<p>` の `text-indent:1em`（exclusion: `.figure-caption`, `.answer-instruction`, `.hanging`）
   - §24-6：ハンギングインデント（Grid 2-column + `<span class="hang-body">` ラップ）

4. **font-weight bumps の canonical 化**：
   - `.basis-card-body { font-weight: 600 }`（旧 400）── 細い明朝の本文を可読化
   - `a.ref-stat`, `a.ref-case { font-weight: 700 }`（旧 600）── 参照リンクの視認性向上

5. **AP-26〜AP-29／S64〜S67／K302-17 追加**：chat-002 観測症例の恒久カタログ化

### v8.10.2 までの差分（既存・継承）

A-2 feedback クラッシュ再発防止 6 層防御（`.fb-verdict` / `.fb-answer` 分離レンダリング・`#answer-feedback strong:not(.fb-verdict)` ガード等）／P1 absolute canon（P2/P3 は `:root{}` 単一ブロックの追記のみ）／rb-chip カラートークン化（`var(--freq-mid)` / `var(--freq-mid-deep)`）／K302-1〜K302-16 検出・S1〜S63 自己検証は完全継承。

---

## §0. 使い方（運用フロー）

### 0-1. 新規 TX ファイル生成

1. **本仕様書全文**（§0〜§Annex C すべて）＋ **問題 PDF** を AI に送信
2. AI は §0-tri 6 ステップ（ゼロベース再構築）を順次実行
3. AI は §0-bis 13 ステップ生成プロトコルを順次実行
4. AI は §31 S1〜S67 の自己検証を全件実行
5. 検証通過後に配信

### 0-2. 既存 TX ファイル（v8.10.2 以下）のアップグレード

1. 既存 HTML を本仕様書とともに送信
2. AI は §0-tri STEP 1（既存スタイル完全破棄）を**最優先**で実行
3. AI は §35 / §35-bis K302 失敗パターンを照合し違反検出時に regeneration
4. §34-bis 12 ステップで canonical 化（最終ステップで構造 diff 検査＋ S64〜S67 検証）

### 0-3. 改変ソース反映時

1. 内容変更箇所のみ波及修正
2. 改変前に §31-4 事前検証、改変後に §31-5 事後検証＋ S52〜S67

---

## §0-tri. ゼロベース再構築プロトコル（最優先命令）

既存ファイルの TX v8.11.0 化、または KTX301 を雛形にした新規ファイル生成において、AI は以下の **6 ステップを順序通り・例外なく**実行せよ。

### ■ STEP 1：既存スタイルの完全破棄（Zero-based Reconstruction）

既存ファイルに記述されている以下の要素は、**すべて読み捨てる・参照しない・引き継がない**：

#### CSS 領域

- `<head>` 内の **`<link href="https://fonts.googleapis.com/...">` フォントリンク全体**
- `<style>` ブロック **内部の全 CSS 規則**

#### 旧 PART 順序（v8.10.2 以下）

A-3 共通根拠 section が PART A 内（A-2 と PART B の間）に配置されていた構造を**完全破棄**。§Annex B v8.11.0 骨格で PART B の後ろに再配置する。関連する `<nav class="sec-nav">` も §2-1 の表に従って全件書き換え。

#### A-2 feedback 関連 旧バグ規則（v8.10.2 から継承）

```css
/* ❌ 旧 v8.6 以下の典型バグ規則（完全破棄） */
#answer-feedback strong{
  ...
  color:#fff !important;
  ...
}
#answer-feedback strong[style*="recall-correct"]{ ... }
#answer-feedback strong[style*="recall-incorrect"]{ ... }
```

#### 旧 JS A-2 feedback 出力パターン

```javascript
/* ❌ 旧 v8.6 以下バグ出力（完全破棄） */
feedback.innerHTML = '<strong style="color:var(--recall-correct)">✓ 正解</strong>　...' +
  '<strong style="background:transparent;color:var(--recall-correct);...">本文強調</strong>...';
```

#### 旧 HTML A-2 area 構造

```html
<!-- ❌ 旧 v8.6 以下構造（完全破棄） -->
<div class="answer-area">
  <div class="answer-slot" data-num="1">1</div>
  <div id="answer-feedback" hidden style="margin-top:12px;..."></div>
</div>
```

#### text-indent + overflow:hidden 不整合パターン（AP-26）

```css
/* ❌ 旧 padding-left + 負の text-indent パターン（overflow:hidden 祖先でクリップ事故） */
.basis-card-body > p:has(> .para-num:first-child){
  padding-left:5.5em;
  text-indent:-5.5em;
}
.basis-card-body > p:has(> strong:first-child){
  padding-left:4.5em;
  text-indent:-4.5em;
}
```

代わりに §24-6 の Grid 方式＋HTML wrap で再構築。

#### `<p>` 直当て flex/grid + 単純 strong マージン（AP-27）

```css
/* ❌ <p> に直接 display:flex/grid で内部 span が個別 item 化する事故 */
.basis-card-body > p:has(> .para-num:first-child){
  display:flex;
  align-items:baseline;
}
```

代わりに `<span class="hang-body">` で本文を atomic-wrap してから `display:grid` を適用（§24-6）。

#### `.ron-mark` display 改変（AP-28）

```css
/* ❌ .ron-mark の display:inline-block 化（長文ブロックジャンプ事故） */
.ron-mark{ display:inline-block; max-width:100%; vertical-align:baseline; }
```

canonical の `.ron-mark` は **inline 維持**。badge orphan は許容。

#### DOM 骨格・全 JS

- `<body>` 内の DOM 骨格（class 名・id・ネスト構造・タグ順序）
- `</body>` 直前の `<script>` ブロック内部の全 JS

**「KTX301 の構造を流用しつつ、既存ファイルの良いところも残そう」「既存 `#answer-feedback strong` 規則の方が familiar だから残そう」「`<div class="answer-slot">` のままでも動くから残そう」── このような部分的マージは絶対禁止。** AI は既存ファイルのスタイル・骨格・JS を**ゼロから完全に破棄**せよ。

> **AI 心得**：大規模言語モデル特有の「保守的書き換え（前のコードを引き継ごうとする癖）」を**強制的に無効化**せよ。特に「`!important` 付き規則」「inline style ベース innerHTML 構築」「`<div>` ベース対話要素」「負 text-indent ハンギング」「`.ron-mark` の display 改変」の 5 パターンは保守的書き換えが頻発する領域。

### ■ STEP 2：骨格の完全クローン（Clone KTX301 byte-for-byte）

本仕様書の以下を **1 バイトの改変もなく・逐語コピー**して新ファイルの土台とせよ：

1. **§Annex B-link の Google Fonts `<link>` タグ全文**
2. **§Annex A 内の `<style>` ブロック全文**（12-role font system + 27 色パレット + 全 CSS 規則 + §24 readability layer 含む・約 1800 行）
3. **§Annex B body skeleton 全文**（KTX301 構造・A-3 は PART B 後ろ・hanging 段落構造含む）
4. **§Annex C 内の `<script>` ブロック全文**（universal handler 等の JS）

### ■ STEP 3：コンテンツのみ抽出・流し込み

§Annex A/B/C の完璧なクローン構造に対して、既存ファイルから **以下のコンテンツ要素のみ**を抽出して流し込め：

| 抽出対象 | 抽出元 | 流し込み先 |
|---|---|---|
| 問題文（事例文・設問） | 旧 `.problem-text` 等 | `<section id="part-a">` |
| 各選択肢の本文 | 旧 `.choice-section .original` | 各 `.choice-section .sub-card.original` |
| 正解値 | 旧 `data-correct-value` 等 | `data-correct-value` 属性 + `.final-answer` |
| A-2 feedback 説明文 | 旧 JS 内 `feedback.innerHTML` 本文部分 | `data-explanation` 属性（プレーンテキスト） |
| 各記述の `explanation` | 旧 `.sub-card.explanation` | 各 `.sub-card.explanation` |
| 共通根拠テキスト | 旧 `<section id="basis">` 内 `.basis-card` | `.basis-card` 内（**ラベル始まり段落は `<p class="hanging"><span class="hang-body">` ラップ必須**） |
| `professor` sub-card 内容 | 旧 `.sub-card.professor` | `.sub-card.professor` |
| PART C コンテンツ | 旧 PART C 各 section | PART C 各 section |
| PART D ARENA 12 問 | 旧 PART D drill-block | 各 `.drill-block` |
| メタ情報 | 旧 doc-header / footer-spec | `.doc-header` / `.footer-spec` |

**禁止事項：**

- 旧 CSS class 名（旧版独自）の引きずり
- 抽出時の旧 style 属性温存
- A-2 feedback 本文中の旧 inline-style strong パターンの温存
- SVG 内のハードコード色温存（`fill="currentColor"` または CSS class 経由に置換）
- **ラベル始まり段落の bare 形式温存**（必ず `<p class="hanging"><span class="hang-body">` ラップ）

### ■ STEP 4：カラーパターンの適用

| 正答率 | パターン | 処理 |
|:-:|:--|:--|
| ≥ 60% | P1 ローズシャンブル | **追記不要**（§Annex A 既定値そのまま） |
| 40〜60% | P2 セージブラリー | §Annex A-bis-2 の `:root{}` 27 色変数ブロックのみ追記 |
| < 40% | P3 ラベンダードーン | §Annex A-bis-3 の `:root{}` 27 色変数ブロックのみ追記 |

**override の厳密形式（AP-24 防止）：** 追記してよいのは **単一の `:root{ ... }` ブロックのみ**。他のセレクタ追加・at-rule 追加・フォント変数 override・pattern marker 付与は**絶対禁止**。

### ■ STEP 5：footer-spec 更新（v8.11.0 版）

```html
<p class="footer-meta">
  Spec:
  <span class="feature-tag">TX v8.11.0</span>・
  <span class="feature-tag">ktx301-canon</span>・
  <span class="feature-tag">embedded-canon</span>・
  <span class="feature-tag">readability-layer</span>・
  <span class="feature-tag">hanging-grid</span>・
  <span class="feature-tag">basis-order-v2</span>・
  <span class="feature-tag">a2-feedback-canon</span>・
  <span class="feature-tag">rbchip-patched</span>・
  <span class="feature-tag">k302-immune</span>・
  <span class="feature-tag">p2p3-unified</span>・
  <span class="feature-tag">p1-absolute</span>・
  <span class="feature-tag">[P1|P2|P3] [パレット名]</span>・
  <span class="feature-tag">[特記事項]</span>
</p>
```

**v8.11.0 新規必須 tag**：`ktx301-canon`／`readability-layer`／`hanging-grid`／`basis-order-v2`

### ■ STEP 6：生成直前の自己検証

ファイル出力の **直前に**、以下を全件チェックし、1 項目でも不一致があれば**最初からやり直し**：

- [ ] §Annex A/B/C との byte-level 一致
- [ ] `<section id="basis">` が PART B の後ろ・PART C の前
- [ ] §24 readability layer 全 6 サブセクションが `<style>` 内に存在
- [ ] ラベル始まり段落が `<p class="hanging"><span class="hang-body">` 形式
- [ ] `.basis-card-body { font-weight: 600 }`
- [ ] `a.ref-stat`, `a.ref-case { font-weight: 700 }`
- [ ] `.ron-mark` に `display:inline-block` なし
- [ ] `.basis-card-body > p` に直接 `display:flex/grid` なし
- [ ] K302-1〜K302-17 非該当
- [ ] S1〜S72 全件通過（v8.11.1 で S68〜S72 追加）
- [ ] **§0-quad コンテンツ独立性プロトコル 7 ステップ全件履行（KTX301 本文の流用ゼロ）**
- [ ] **§1-bis 命名規則準拠（出力ファイル名・出力先サブフォルダ）**

---

## §0-quad. コンテンツ独立性プロトコル（v8.11.1 新規・最優先命令）

> **背景：** Claude Code 等の自動生成環境で本仕様書を投入すると、§Annex B body skeleton 内に **byte-level 逐語埋込された KTX301 の問題固有テキスト**（詐欺罪と他罪の成否論点・最判昭28.5.8・「背任行為が同時に詐欺の欺罔行為に当たる場合」等の具体的解説文言）が、新規生成ファイルにそのまま流用される事故が頻発する。これは「Annex を逐語コピー」という指示を AI が過度に保守的に解釈し、構造シェルだけでなく**本文テキストまで温存**してしまう現象である。
>
> v8.11.1 では、この **canonical text leakage（正典本文の流出）** を恒久的に遮断するため、以下のプロトコルを §0-tri と並ぶ最優先命令として運用する。

### §0-quad-1. 逐語コピー対象 vs 完全新規執筆対象の厳密分離

**【逐語コピー対象 = "structural shell only"】** ── §Annex の指示通り byte-level で温存：

| カテゴリ | 対象 |
|---|---|
| CSS 全体 | §Annex A／§Annex A-bis-2／§Annex A-bis-3 全規則 |
| JS 全体 | §Annex C universal handler 等すべて |
| HTML 構造 | タグ名・class 名・id 名・属性キー・ネスト順序・PART 区切り |
| 不変ラベル | `marker-legend` 凡例本文／PART タイトル文字列（"PART A ── 問題情報" 等）／`<nav class="sec-nav">` 内リンクラベル（"↑A-1"／"記述イ→" 等の航行用テキスト）／sec-icon 文字（❀／⚔ 等）／section-title 内の節番号部分（"A-1"／"A-2"／"B"／"C-1" 等） |
| footer-spec 構造 | `<div class="footer-spec">` の骨格と feature-tag 命名規則（中身は §1-bis 命名・問題情報で差替） |

**【完全新規執筆対象 = "problem-specific content"】** ── §Annex B 内の以下のテキストは**一切引用してはならない**。問題 PDF の内容のみを根拠に **AI が自前で執筆**せよ：

| カテゴリ | 対象タグ／属性 |
|---|---|
| ヘッダ | `.doc-header` 内テキスト／`<title>` 内テキスト |
| 問題本体 | `.problem-text` 内テキスト／`<h3>【記述】</h3>`等の派生小見出しの直後ブロック |
| 解答 | `data-correct-value` / `data-explanation` 値／`.final-answer` 内テキスト |
| 肢別解説 | 各 `.choice-section` 内の `.choice-summary`／`.verdict` テキスト／`.sub-card.original` 本文／`.sub-card.explanation` 本文／`.sub-card.basis-link` 内テキスト／`.sub-card.professor` の 4 prof-heading 直下本文／`.key-phrase-box` 内本文 |
| 共通根拠 | `.basis-card-header h3`／`.basis-card-body` 内段落の本文部分（`<span class="hang-body">` 内の本文）／`.ref-backlinks` 内本文 |
| 体系/記憶 | PART C 各 section の本文（cross-card／lead-list／memory-item／final-answer すべて） |
| ARENA | PART D 各 drill-block の `.quiz-question` 本文・`.quiz-btn` 選択肢・`.quiz-answer` 本文 |
| メタ | footer-spec 内 1〜3 行目の問題情報行（ファイル ID／科目／出典／論点／正答率／パターン／正解値） |

### §0-quad-2. 禁止文言ブラックリスト（KTX301 由来の特定文言）

以下は KTX301 の問題固有文言である。**新規生成ファイル内で問題 PDF が当該論点を扱っていない限り、出現を一切許さない**：

```
■ 論点・キーワード系
"詐欺罪と他罪の成否"
"詐欺罪のみが成立し得る"
"詐欺罪と他の罪の双方が成立し得る"
"詐欺罪は成立しない"
"背任行為が同時に詐欺の欺罔行為に当たる"
"背任罪を別個に構成せず"
"畏怖の一材料"
"業務上横領罪"
"集金業務を委託"
"偽造通貨行使罪に包含"
"放火だけでは詐欺の実行着手"

■ 判例引用系（KTX301 で参照される特定の最判・大判）
"最判昭28.5.8"
"最判昭24.2.8"
"東京高判昭28.6.12"
"大判明5.12.12"
"大判明43.6.30"

■ KTX301 専用の選択肢例（記述ア〜オの原文をそのまま流用するな）
"他人のためにその事務を処理する者が、任務に背いて"
"脅迫文言の中に虚偽の部分があり"
"新聞販売店から集金業務を委託されている集金員"
"保険金を詐取する目的で、火災保険の付された自己所有の家屋に放火"
"他人に売買代金として偽造通貨を行使"
```

**例外条項：** 新規 PDF の問題が**真に**上記論点・判例を扱う場合に限り、当該文言の使用を許容する。ただしその場合でも、解説本文・体系図解・ARENA 設問は KTX301 と異なる切り口・例示・順序で執筆すること（同一文章の bare copy は AP-30 として違反）。

### §0-quad-3. 7 ステップ独立性プロトコル

新規 TX ファイル生成時、AI は以下を §0-tri 6 ステップに**並行して**実行：

**STEP IQ-1：問題 PDF からの抽出（AI 自身の言語化）**

問題 PDF を読解後、以下を **AI 自身の整理した日本語**で内部メモ化（出力には含めない）：
- 問題のテーマ（1 行で要約）
- 各選択肢が問う論点（1 選択肢 1 行）
- 関連する条文番号・判例名（あれば）
- 出題形式（単一選択／5記述○×／空欄補充／組合せ）

**STEP IQ-2：§Annex B の本文を「無視リスト」化**

§Annex B body skeleton をクローンする際、**以下のテキスト要素は必ず空文字列で初期化**してからコンテンツを流し込む（temporary placeholder 化）：

```
.doc-header text content              → 空
.problem-text 各々の text content     → 空
data-correct-value                    → 空
data-explanation                      → 空
.choice-summary, .verdict             → 空
.sub-card.* 内のすべての <p> 本文     → 空
.basis-card-header h3                 → 空（カード ID 属性のみ保持）
.basis-card-body 内 <span class="hang-body"> 本文 → 空
.final-answer 内テキスト              → 空
PART C 全 section 本文                → 空
.drill-block 内設問・選択肢・解説     → 空
footer-spec 1〜3 行目                 → 空
```

この空骨格に対して、**STEP IQ-1 で AI 自身が言語化した問題内容**のみを参照して本文を執筆する。§Annex B の元テキストを参照しながら執筆してはならない。

**STEP IQ-3：執筆中の自己検閲**

執筆中、§0-quad-2 ブラックリストの語句を**反射的に書こうとしている**ことを検知したら、即座に停止し、当該文の構造を作り直す。具体的には：
- 出題テーマと無関係な「詐欺罪」「背任罪」「偽造通貨」等の語が浮かんだら停止
- 「最判昭28.5.8」等の特定判例番号が浮かんだら、PDF に当該番号があるか検証
- 「畏怖の一材料」等の KTX301 特有の言い回しが浮かんだら、別表現に置換

**STEP IQ-4：解説文の独自性確保**

各 `.sub-card.explanation` 本文は以下の構造で執筆（KTX301 の文体踏襲を回避）：

1. 結論（1 文）── 当該記述が正/誤である理由の中核
2. 法的根拠（1〜2 文）── 適用条文・判例の趣旨
3. 当てはめ（1〜2 文）── 本問の事案への適用
4. 補足（任意・1 文）── 周辺論点・反対説への言及

文末表現は「〜である。」「〜と解される。」「〜とするのが判例である。」等を**問題ごとに使い分け**、KTX301 の文体（〜成立する／〜包含される 等）の機械的反復を避ける。

**STEP IQ-5：professor sub-card の独自視点**

`.sub-card.professor` の 4 prof-heading（1 ポイント／2 考え方の道筋／3 イメージで掴む／4 あてはめ）は、本問の論点に即した**新規の比喩・図式・記憶術**を考案する。KTX301 の professor 本文（詐欺罪の包含関係に関する説明）を**形式的にも内容的にも踏襲しない**。

**STEP IQ-6：basis-card 本文の独自整理**

`.basis-card` 内の条文・判例本文は、出題に直接関係するもの**のみ**を掲載。KTX301 が複数判例（最判昭28.5.8／最判昭24.2.8／東京高判昭28.6.12 等）を並べているからといって、新規ファイルでも複数カード並列構成を機械的に踏襲しない。本問が単一判例で完結するなら 1 カード、複数条文の対比なら対比型、と問題に応じて構造選択する（ただし `.basis-card-header` + `.basis-card-body` の HTML 構造は §Annex B 通り）。

**STEP IQ-7：生成直前の leakage 検査**

ファイル出力直前に、生成 HTML の本文部分（タグ・class・id・属性キーを除く可視テキスト）に対して、§0-quad-2 ブラックリスト全項目を全文検索：

```
for keyword in blacklist:
  if keyword in generated_html_text_content:
    if problem_pdf does NOT cover this topic:
      ABORT: AP-30 違反 → STEP IQ-2 に戻って再生成
```

検査通過後にのみ S1〜S72 自己検証に進む。

### §0-quad-4. 「Annex B を逐語コピー」指示の正しい読み方

§0-tri STEP 2 および §0-bis STEP 8 の「§Annex B canonical body skeleton を逐語適用」という指示は、以下を意味する：

| ✓ 逐語コピーする | ✗ 逐語コピーしない |
|---|---|
| `<section class="choice-section odd" id="choice-1">` | `<span class="choice-summary">背任行為が…</span>` の本文 |
| `<div class="sub-card original"><span class="label">記述原文</span><p>` | `<p>他人のためにその事務を処理する者が…</p>` の本文 |
| `<div class="basis-card statute-card">` 開閉とその子構造 | `<h3 id="law-fraud">刑法246条</h3>` の中身 |
| `<p class="hanging"><strong>I.</strong><span class="hang-body">　…</span></p>` の構造 | `<span class="hang-body">　詐欺罪のみが成立し得る。</span>` の本文 |

**鉄則：** 「タグ・属性は KTX301 と byte-level 一致」「タグ内の自然言語テキストは KTX301 と byte-level 不一致でなければならない（問題が真に同一論点でない限り）」。

---

## §0-bis. AI 15 ステップ生成プロトコル（v8.11.1）

1. **問題 PDF を読解**：問題番号・科目・年度・全選択肢・正解・正答率・出題テーマを抽出
2. **正答率からパターン判定**：≥60%→P1／40-60%→P2／<40%→P3（§32）
3. **冒頭応答必須**：「正答率__%→パターン_『___』適用」を最初に出力
4. **問題形式の判定**：単一選択／5記述○×型／空欄補充型／組合せ型の4類型を識別。多解答型なら §22-ter 適用
5. **§0-tri STEP 1（既存スタイル破棄）実行**（既存ファイル改変時のみ）
6. **§Annex A canonical CSS を逐語コピー**（書き直し禁止／既定 `:root` は P1 ローズシャンブル／§17 fb-verdict/fb-answer canonical 6 規則＋§24 readability layer 含む）
7. **P2 or P3 を選んだ場合のみ §Annex A-bis-2 / A-bis-3 の `:root{}` 上書きブロックを `<style>` 末尾に追記**
8. **§Annex B canonical body skeleton を逐語適用**（A-3 が PART B 後ろ・hanging 段落構造含む）── **ただし §0-quad-2 の placeholder 化（本文空文字列初期化）を必須**
9. **§0-quad 7 ステップ独立性プロトコル（IQ-1〜IQ-7）を全件履行**：問題 PDF の内容を AI 自身の言語で言語化 → §Annex B 本文を一切参照せず新規執筆 → 禁止文言ブラックリスト検査
10. **content を差替え**。**A-2 解説文は `data-explanation` 属性に格納**しプレーンテキスト化。**条文・判例 body のラベル始まり段落は必ず `<p class="hanging"><span class="hang-body">` ラップ**。本文は KTX301 由来文言を含まないこと（§0-quad-2 検証済み）
11. **§Annex C canonical JS を逐語コピー**（書き直し禁止）
12. **PART D ARENA を ○/× rapid-fire で構築**（12 問・○:×=6:6）── 設問・解説は本問オリジナル（KTX301 の ARENA をテーマ流用しない）
13. **§4-quater 全 section-title に sec-icon 配置**／§17-bis PART C content wrapper を適用
14. **§1-bis 命名規則準拠**：PDF ファイル名から番号抽出 → 「日本語接頭辞 + TX + 3桁ゼロ埋め .html」形式でファイル名確定／`outputs/{ktx|kentx|mintx|syotx|minstx|keistx|gsetx}/` 配下に出力
15. **§31 S1〜S72 自己検証** → 全件通過後に配信。**S60/S61/S62/S63/S64/S65/S66/S67/S68/S69/S70/S71/S72 を最優先確認**

---

## §1. ファイルメタデータ

各 TX ファイル先頭の `<title>` および footer-spec に以下を必ず含める：

- **ファイル ID**：**日本語科目接頭辞 + TX + 3桁ゼロ埋め番号**（v8.11.1 canonical 形式）
  - 例：**刑TX299**（刑法）／**憲TX015**（憲法）／**民TX120**（民法）／**商TX045**（商法）／**民訴TX078**（民訴）／**刑訴TX033**（刑訴）／**行政TX092**（行政法）
  - **byte-level model file** は引き続き **KTX301** と呼称（歴史的識別子）
  - レガシー形式（K302／MIN145／KEN087 等）は v8.10.2 以前の表記。新規生成では使用しない
- **年度・問題番号**：例「予備R2-18」「本試H30-12」「旧司H20-20」
- **論点タイトル**：例「詐欺罪と他罪の成否」（本問固有の論点。KTX301 の論点をコピーするのではない）
- **正答率**：百分率
- **適用パターン**：P1 ローズシャンブル／P2 セージブラリー／P3 ラベンダードーン
- **Spec バージョン**：`TX v8.11.1` ＋ feature tag 群（§33 参照）

---

## §1-bis. PDF 入力→出力ファイル命名規則（v8.11.1 canonical）

### §1-bis-1. 出力ファイル名フォーマット

```
{日本語科目接頭辞}TX{3桁0埋め数字}.html
```

### §1-bis-2. PDF ファイル名からの番号抽出ルール

1. PDF ファイル名から**連続する数字を抽出**（最初に出現するもの）
2. 3 桁未満の場合は前ゼロで 0 埋め
   - `1` → `001`
   - `22` → `022`
   - `299` → `299`
   - `301` → `301`
3. 3 桁を超える場合はそのまま使用
   - `1234` → `1234`
4. ファイル名に複数の数字グループがある場合は**最初のまとまり**を採用
   - 例：「K310-2024-problem.pdf」 → `310` を抽出（2024 は使わない）
5. **数字が一切抽出できない場合は処理を中断**し、ユーザー（xnh）に番号を確認すること（無断で番号を生成・推定しない）

### §1-bis-3. 科目接頭辞・出力先サブフォルダ対応表

| 科目 | 接頭辞 | 出力先 | ファイル名例 |
|---|---|---|---|
| 刑法 | `刑TX` | `outputs/ktx/` | `刑TX299.html` |
| 憲法 | `憲TX` | `outputs/kentx/` | `憲TX015.html` |
| 民法 | `民TX` | `outputs/mintx/` | `民TX120.html` |
| 商法 | `商TX` | `outputs/syotx/` | `商TX045.html` |
| 民訴 | `民訴TX` | `outputs/minstx/` | `民訴TX078.html` |
| 刑訴 | `刑訴TX` | `outputs/keistx/` | `刑訴TX033.html` |
| 行政法 | `行政TX` | `outputs/gsetx/` | `行政TX092.html` |

### §1-bis-4. 命名例（実運用）

| 入力 PDF ファイル名 | 科目 | 抽出数字 | 出力ファイル |
|---|---|---|---|
| `299.pdf` | 刑法 | 299 | `outputs/ktx/刑TX299.html` |
| `310-problem.pdf` | 刑法 | 310 | `outputs/ktx/刑TX310.html` |
| `司法R1-16詐欺.pdf` | 刑法 | 1 → 001 | `outputs/ktx/刑TX001.html`（※「16」ではなく最初の数字「1」を採用） |
| `kenpo-question-05.pdf` | 憲法 | 5 → 005 | `outputs/kentx/憲TX005.html` |
| `mins-018.pdf` | 民訴 | 18 → 018 | `outputs/minstx/民訴TX018.html` |
| `K310-2024-problem.pdf` | 刑法 | 310 | `outputs/ktx/刑TX310.html` |
| `予備H30問15.pdf` | 民法 | 30 → 030 | `outputs/mintx/民TX030.html`（※「15」ではなく最初の「30」を採用） |
| `民法.pdf`（数字なし） | 民法 | 抽出不能 | **処理中断 → ユーザー確認** |

> **重要：** 「最初に出現する連続数字」のルール上、PDF ファイル名に年度数字や問番号が複数含まれる場合の挙動を上記の通り固定する。年度を採用したい場合・問番号を採用したい場合の使い分けは、運用者がリネーム段階で調整する責務（仕様としては「最初の連続数字」を機械的に採用）。

### §1-bis-5. `<title>` ／`.doc-header` への反映

```html
<title>刑TX299 ｜ 司法予備R1-16 詐欺罪と他罪の成否</title>
<!-- ... -->
<div class="doc-header">刑TX299</div>
```

`<title>` は「ファイル ID ｜ 年度問番号 論点」形式。`.doc-header` は**ファイル ID のみ**（KTX301 の慣例を継承）。

### §1-bis-6. ファイル ID の DOM への他所配置

- `<title>` 内
- `.doc-header` 内
- `footer-spec` 1 行目（科目名・出典・論点とともに）

上記 3 箇所すべてで同一の v8.11.1 形式ファイル ID を使用すること。混在（例：`<title>` は `刑TX299` だが footer-spec は旧形式 `K299`）は S70 違反として検出。

---

## §2. 全体構造（PART 構成）── v8.11.0 改訂

```
HTML doc
├── <head>
│   ├── <meta>
│   ├── <title>
│   ├── <link>（§Annex B-link 逐語）
│   └── <style>
│        ├── §Annex A 逐語コピー（§24 readability layer 含む）
│        └── （P2/P3 のみ）§Annex A-bis-2 or -3 の :root{} 単一ブロック末尾追記
└── <body id="top">
    └── <div class="container">
        ├── <header class="header">
        ├── <div class="marker-legend">
        │
        ├── <div class="part-title">PART A ── 問題情報</div>
        │   ├── <section id="part-a">（A-1：問題文）
        │   └── <section id="answer-area">（A-2：解答 ── data-correct-value/data-explanation 駆動）
        │
        ├── <div class="part-title">PART B ── 肢別解説</div>
        │   └── <section class="choice-section odd|even" id="choice-1〜5"> × 5
        │
        ├── ★★★【v8.11.0 新配置】★★★
        ├── <section class="section" id="basis">（A-3：共通根拠条文・判例）
        │   ※ PART B 直後・PART C 直前
        │
        ├── <div class="part-title">PART C ── 体系・記憶</div>
        │   └── <section id="c-1">〜<section id="c-7">
        │
        ├── <div class="part-title">PART D ── ACTIVE RECALL ARENA</div>
        │   └── <section class="section recall-arena" id="part-d">
        │
        └── <div class="footer-spec">
    </div>
    <script>（§Annex C 逐語コピー）</script>
```

### §2-1. v8.11.0 navigation 改訂

A-3 が PART B 後に移動するため、関連する `<nav class="sec-nav">` 全件を以下に書き換え：

| section | v8.10.2 まで（旧） | v8.11.0（新） |
|---|---|---|
| A-1 sec-nav | `↓解答 / ↓共通根拠` | `↓解答 / ↓記述ア` |
| A-2 sec-nav | `↑A-1 / ↓共通根拠` | `↑A-1 / ↓記述ア` |
| 記述ア sec-nav | `↑共通根拠 / 記述イ→` | `↑A-2 / 記述イ→` |
| 記述オ sec-nav | `←記述エ / ↓PART C` | `←記述エ / ↓共通根拠` |
| A-3 sec-nav | `↑A-2 / ↓記述ア` | `↑記述オ / ↓C-1` |
| C-1 sec-nav | `←記述オ / C-2→` | `↑共通根拠 / C-2→` |

### §2-2. topbar TOC 順序

```html
<!-- v8.11.0 canonical 順序 -->
<a href="#part-a">問題文</a>
<a href="#answer-area">解答</a>
<a href="#choice-1">ア</a>
<a href="#choice-2">イ</a>
<a href="#choice-3">ウ</a>
<a href="#choice-4">エ</a>
<a href="#choice-5">オ</a>
<a href="#basis">共通根拠</a>
<a href="#c-1">体系</a>
<a href="#c-7">三層記憶</a>
<a href="#part-d">⚔ARENA</a>
```

---

## §3-quater. 12-role font system canonical lock

§Annex A 冒頭の `:root{ --font-body / --font-soft / --font-display / --font-statute / --font-quote / --font-answer / --font-keyword / --font-judgment / --font-note / --font-professor / --font-mono / --font-impact }` を**逐語使用**。Google Fonts CDN による読み込みは §Annex B-link で完備。

**鉄則**：これら 12 ロールのフォント値は **P1/P2/P3 すべてで完全に同一**。`§Annex A-bis-2 / A-bis-3` の override で `--font-*` を再定義してはならない（AP-24）。

---

## §4-ter. DOM 骨格 canonical lock

§Annex B の body skeleton を**逐語適用**。タグ名・class 名・ネスト構造・id 命名規約を変更してはならない。content のみを差替える。

### 必須 ID 命名規約

| ID | 配置 | 用途 |
|---|---|---|
| `top` | `<body id="top">` | ページ先頭アンカー |
| `part-a` | A-1 問題文 section | PART A 起点 |
| `answer-area` | A-2 解答 section | A-2 起点 |
| `basis` | A-3 共通根拠 section（**PART B の後ろ**） | A-3 起点 |
| `choice-1`〜`choice-5` | 各記述 section | PART B 各記述起点 |
| `c-1`〜`c-7` | PART C 各 section | C-1〜C-7 起点 |
| `part-d` | recall-arena section | PART D 起点 |
| `answer-feedback` | A-2 内 feedback ボックス | fb-verdict / fb-answer 出力先 |
| `law-XXX`/`case-XXX` | basis-card 各カード | 共通根拠 ID |
| `ref-law-XXX-NNN`/`ref-case-XXX-NNN` | 各記述からの戻り先 span | 連番付き逆参照 ID |

**鉄則**：`body.p2` / `body.p3` / `[data-pattern="p2"]` 等の pattern-conditional class や data 属性を `<body>` や `<html>` に付与してはならない（AP-24／S61 検出）。

---

## §4-quater. section-title sec-icon canonical lock

すべての `<h2 class="section-title">` は以下構造：

```html
<h2 class="section-title"><span class="sec-icon">[ICON]</span>[SECTION-ID] [SECTION-NAME]</h2>
```

| Part | sec-icon |
|:-:|:-:|
| PART A（A-1, A-2） | `❀` |
| A-3 共通根拠（PART B 後ろ） | `❀` |
| PART B | choice-big-badge で代用（sec-icon 不要） |
| PART C（C-1〜C-7） | `❀`（一部 ⚔ / 🗺 / 📚 / 🧠 等の派生も許容） |
| PART D（D-1） | `⚔` |

---

## §6. doc-header canonical 構造

§Annex B 参照。KTX301 実装は `<div class="doc-header">[ファイル ID]</div>` 形式（簡素なファイル ID 表示のみ）。

---

## §7. PART A canonical 構造（A-1, A-2）

§Annex B 参照。**v8.11.0 では PART A は A-1 と A-2 のみで構成**（A-3 は PART B 後ろに移動）。

### §7-3-bis. A-2 直後スポイラー禁止

A-2 解答 section と PART B の間で、**各記述の正解（記述ア＝正／誤など）や個別解説を表示してはならない**。詳細は PART B に集約。違反は AP-3 として禁止。

### §7-4. A-2 解答 area の必須属性

| 属性 | 必須 | 内容 | 例 |
|---|---|---|---|
| `data-correct-value` | ✓ | 正解値 | `data-correct-value="5"` |
| `data-explanation` | ✓ | 解説本文（プレーンテキスト・先頭 `N。` プレフィックス保持） | `data-explanation="5。肢5は、…"` |

---

## §11. component canonical lock

### §11-1. sub-card 4 種

PART B 各記述内：`original` / `explanation` / `basis-link` / `professor` の 4 種を必ず順序通り配置。`professor` には 4 prof-heading（1 ポイント／2 考え方の道筋／3 イメージで掴む／4 あてはめ）＋ 内蔵 key-phrase-box が必須。

### §11-2. 補助カード（callout 4 種）

`warning` / `cross-link` / `prof-analogy` / `key-phrase-box`。

### §11-3. key-phrase-box フォント階層

`--font-impact`（M PLUS 1p）を継承し、コーナーに `::before { content:'🔑 KEY'; }` のラベル装飾。背景 gradient は `var(--accent-3) → var(--light) → var(--soft)`。

---

## §16. marker-legend canonical 構造

`</header>` の直後に配置（§Annex B 参照）。`lg-title` / `lg-item` / `lg-sample` / `lg-divider` の class 命名を使用。

---

## §17. PART A 問題文 / answer-area / answer-feedback canonical

### §17-1. problem-text

```html
<div class="problem-text"><span class="choice-num-inline">1</span>選択肢本文…</div>
```

### §17-2. answer-area 必須構造（v8.11.7・3 Type 対応）

A-2 解答エリアは `data-answer-type` 属性で 3 Type を分岐する。**いずれの Type でも `<button class="reveal-answer-btn" type="button" disabled>解答を表示</button>` 必須**（AP-34）。

#### Type A (single) ── 単一選択型【既定】

```html
<div class="answer-area"
     data-correct-value="N"
     data-explanation="(任意・参考用・A-2 では表示されない)">
  <h3>正しいと思う番号をクリック</h3>
  <p class="answer-instruction">選択肢を選んで「解答を表示」を押してください。</p>
  <div class="answer-row">
    <button class="answer-slot" type="button" data-num="1" data-value="1">1</button>
    <button class="answer-slot" type="button" data-num="2" data-value="2">2</button>
    <button class="answer-slot" type="button" data-num="3" data-value="3">3</button>
    <button class="answer-slot" type="button" data-num="4" data-value="4">4</button>
    <button class="answer-slot" type="button" data-num="5" data-value="5">5</button>
  </div>
  <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>
  <div id="answer-feedback" hidden></div>
</div>
```

#### Type B (multi) ── 複数選択型（カンマ区切り正解値）

```html
<div class="answer-area"
     data-correct-value="1,2"
     data-answer-type="multi"
     data-explanation="(任意・参考用)">
  <h3>誤っている記述を 2 個クリック</h3>
  <p class="answer-instruction">選択肢を 2 個選んで「解答を表示」を押してください。</p>
  <div class="answer-row">
    <button class="answer-slot" type="button" data-num="1" data-value="1">1</button>
    <button class="answer-slot" type="button" data-num="2" data-value="2">2</button>
    <button class="answer-slot" type="button" data-num="3" data-value="3">3</button>
    <button class="answer-slot" type="button" data-num="4" data-value="4">4</button>
    <button class="answer-slot" type="button" data-num="5" data-value="5">5</button>
  </div>
  <p class="selection-counter">選択中: 0 / 2 個</p>
  <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>
  <div id="answer-feedback" hidden></div>
</div>
```

**Type B 仕様：**

- `<p class="answer-instruction">` 内の数字は正解数（カンマ区切り個数）に応じて動的に挿入
- `<p class="selection-counter">` の `M`（分母）も同上
- FIFO トグル：最大数到達後の追加クリックは最古を解除
- `M` 個揃ったら `reveal-answer-btn` 有効化

#### Type C (ox-grid) ── ○×評価型（各記述に正誤を判定）

```html
<div class="answer-area"
     data-correct-value="11112"
     data-answer-type="ox-grid">
  <h3>各記述に正誤を判定</h3>
  <p class="answer-instruction">各記述に「1（正）」または「2（誤）」を選んで「解答を表示」を押してください。</p>
  <div class="answer-ox-grid">
    <div class="ox-row" data-pos="0">
      <span class="ox-label">ア</span>
      <div class="ox-btn-group">
        <button class="ox-btn" type="button" data-value="1">1（正）</button>
        <button class="ox-btn" type="button" data-value="2">2（誤）</button>
      </div>
    </div>
    <!-- イ・ウ・エ・オ も同様（合計 N 行 = 正解値の桁数） -->
  </div>
  <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>
  <div id="answer-feedback" hidden></div>
</div>
```

**Type C 仕様：**

- `data-correct-value` は N 桁の文字列。各桁が `1`（正）or `2`（誤）のみ
- 桁数 = `.ox-row` 数 = 記述数
- ラベルは ア・イ・ウ・エ・オ がデフォルト。問題の指示に応じて ①〜⑤ や a〜e も使用可
- 全 ox-row で 1 ボタン選択（行内で他は自動解除）すると `reveal-answer-btn` 有効化

#### 3 Type 共通要件

| 項目 | 値 |
|---|---|
| `<p class="answer-instruction">` | **正解値リテラル・解説テキストを絶対に含めない**（AP-33 違反禁止） |
| `<button class="reveal-answer-btn" type="button" disabled>` | 必須（AP-34 違反禁止） |
| `data-explanation` 属性 | 保持可。ただし A-2 では表示されない（PART B sub-card.explanation と巻末 FINAL ANSWER で代替）。**先頭リテラル（「N。」「3,4。」「11112（ア1・イ1…）。」等）も禁止**（AP-37 違反禁止） |
| `<button class="answer-slot">` / `<button class="ox-btn">` | `<div>` は使用不可（必ず `<button>`） |
| `<div id="answer-feedback" hidden>` | inline `style` 属性一切なし |

**禁止事項（再掲）：**

- `<div class="answer-slot">`（→ `<button>` 必須）
- `<div id="answer-feedback" hidden style="...">`（inline style 禁止）
- `data-correct-value` 属性の省略
- HTML 側に長文 innerHTML テンプレート（`<strong style="color:..."` 等）をハードコード
- `<p class="answer-instruction">` 内に正解値リテラル・解説テキスト（AP-33）
- `<button class="reveal-answer-btn">` の欠落（AP-34）
- `data-explanation` 先頭に正解値リテラル（AP-37）

### §17-3. answer-feedback canonical CSS（必須 7 規則）

§Annex A 内に**以下 7 規則を必ず逐語含めること**。1 つでも欠ければ S62/S63 違反：

```css
/* (1) フィードバックボックス自体 */
#answer-feedback{
  margin-top:14px !important;
  padding:16px 22px !important;
  border-radius:8px !important;
  font-family:var(--font-note) !important;
  line-height:1.95;
  font-size:.98em;
  box-shadow:0 2px 10px rgba(var(--accent-rgb),.10);
  letter-spacing:.02em;
}

/* (2) バッジ専用クラス */
#answer-feedback .fb-verdict{
  font-family:var(--font-display);
  font-size:1.08em;
  letter-spacing:.06em;
  display:inline-block;
  padding:2px 12px 1px;
  border-radius:5px;
  color:#fff;
  margin-right:6px;
  text-shadow:0 1px 2px rgba(0,0,0,.30);
  box-shadow:0 2px 5px rgba(0,0,0,.18), inset 0 1px 0 rgba(255,255,255,.20);
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}

/* (3) 正解バッジ */
#answer-feedback .fb-verdict.fb-correct{
  background:linear-gradient(135deg,var(--recall-correct),var(--recall-correct-light));
}

/* (4) 不正解バッジ */
#answer-feedback .fb-verdict.fb-incorrect{
  background:linear-gradient(135deg,#7e0024,var(--recall-incorrect));
}

/* (5) 本文番号 span 別レイヤー */
#answer-feedback .fb-answer{
  display:inline-block;
  font-family:var(--font-display);
  font-weight:800;
  font-size:1.18em;
  color:var(--recall-incorrect);
  background:transparent;
  padding:0 5px 1px;
  margin:0 2px;
  letter-spacing:.04em;
  border-bottom:2.5px solid var(--recall-incorrect);
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}

/* (6) :not() ガード */
#answer-feedback strong:not(.fb-verdict){
  font-weight:700;
  color:inherit;
}

/* (7) 【v8.11.0 新規】§24-5 全 p 字下げ干渉防止 */
#answer-feedback p{ text-indent:0; }
```

### §17-4. answer-feedback canonical JS

§Annex C 参照（`handleAnswerSlot` / `handleRevealAnswerBtn` / `handleOxBtn` / `getAnswerType` / `updateRevealBtnState` 等の関数群）。

---

### §17-5. A-2 2 段階開示プロトコル（v8.11.7 / a2-two-stage-reveal canonical）

A-2 解答エリアの操作は厳格な 2 段階で構成される。

#### Stage 1 ── 選択

ユーザーが選択肢ボタン（`.answer-slot` / `.ox-btn`）をクリック：

- 選択された選択肢に `.selected` クラス付与 → ハイライト表示
- Type A (single)：他の選択肢の `.selected` は外される
- Type B (multi)：FIFO トグル（最大数到達後の追加クリックは最古を解除）
- Type C (ox-grid)：行内で他の選択は外される
- フィードバック（`#answer-feedback`）は **絶対に表示されない**
- 正解/不正解の判定は **行われない**
- 必要数揃った時点で `<button class="reveal-answer-btn">` の `disabled` 属性が外れて有効化

#### Stage 2 ── 開示

ユーザーが `.reveal-answer-btn` をクリック：

- 全選択肢が `disabled` 化、正解選択肢に `.correct-mark`、不正解選択時はユーザー選択に `.incorrect-mark` 付与
- `#answer-feedback` が `hidden:false` で開示され、以下のいずれかが表示：
  - 正解: `<strong class="fb-verdict fb-correct">✓ 正解</strong>` のみ
  - 不正解: `<strong class="fb-verdict fb-incorrect">✗ 不正解</strong>　正解は<span class="fb-answer">N</span>` のみ
- **詳細解説は絶対に表示しない**（PART B sub-card.explanation と巻末 FINAL ANSWER で代替）
- `.answer-area` に `.answered` クラスが付与され、以降の操作を無効化
- 巻末 FINAL ANSWER の `hidden` 属性も同時に外される（`revealFinalAnswer()` 連動）

#### 設計理念

- 自答 → 確認 → 詳細学習のサイクルを厳格に分離
- A-2 ではあくまで「自答の結果が合っているか」のみを確認
- 詳細な判例・解説・論点は能動的にスクロール（PART B）またはクリック（FINAL ANSWER）で参照

---

### §17-6. A-2 ○×評価グリッド プロトコル（v8.11.7 / ox-grid canonical）

`data-answer-type="ox-grid"` 時の専用 UI 規律。

#### HTML 構造

- `<div class="answer-ox-grid">` をラッパーとし、各記述ごとに `<div class="ox-row" data-pos="N">` を 1 行ずつ配置
- 各 `.ox-row` 内：`<span class="ox-label">{記述ラベル}</span>` ＋ `<div class="ox-btn-group">`
- `.ox-btn-group` 内：`<button class="ox-btn" data-value="1">1（正）</button>` と `<button class="ox-btn" data-value="2">2（誤）</button>` の 2 ボタン

#### 操作プロトコル

- **Stage 1**：各 ox-row で 1 ボタン選択（行内で他は自動解除）。全行揃うまで `reveal-answer-btn` は無効
- **Stage 2**：「解答を表示」クリックで全行の選択値を結合（例：ア=1, イ=1, ウ=1, エ=1, オ=2 → `"11112"`）、`data-correct-value` と一致比較。一致でも不一致でも、各 ox-btn に `.correct-mark`／`.incorrect-mark` クラスを付与してマーク表示

#### 正解値の格納

- `data-correct-value="11112"` のように N 桁の文字列。各桁が 1（正）or 2（誤）のみ
- 桁数 = ox-row 数 = 記述数

---

## §17-bis. PART C content wrapper canonical

PART C 内の以下 3 要素は**必ず canonical wrapper で包装**。bare 形式は AP-21 禁止。

### 17-bis-1. テーブル

```html
<div class="cmp-table-wrap"><table>...</table></div>
```

### 17-bis-2. SVG

```html
<div class="figure-wrap">
  <svg viewBox="0 0 700 760">...</svg>
  <p class="figure-caption">図：[内容]</p>
</div>
```

### 17-bis-3. cross-card

```html
<div class="cross-grid">
  <div class="cross-card">
    <h4><span class="cc-label">SUBJ</span>...</h4>
    <p>...</p>
  </div>
</div>
```

---

## §19-quinquies. C-7 memory-item canonical

C-7 三層構造記憶リストは**必ず `.memory-item priority-a/b/c` で構築**。`sub-card original` 流用は AP-19 禁止。合計 14〜15 項目（A=5, B=5, C=4〜5）が canonical 標準。

---

## §22-bis. 単一解答型 final-answer（C-7 末尾配置・v8.11.7）

3 段構成必須。**`hidden` 属性必須**（v8.11.7 / AP-30）：

```html
<div class="final-answer" hidden>
  <h3>🎯 正解</h3>
  <span class="answer-num">3</span>
  <p class="fa-summary"><strong>[一文要約]</strong>　[詳細]</p>
  <p>[追加説明＋ref-stat/ref-case リンク]</p>
</div>
```

`fa-summary` 内に「正解はN」リテラル禁止（AP-32）。

## §22-ter. 多解答型 final-answer canonical（answer-num-multi・v8.11.7）

**正解の数字（または正と判定された記述ラベル）のみ表示**（AP-38）。不正解の数字・誤判定の記述は表示しない：

```html
<div class="final-answer" hidden>
  <h3>🎯 正解</h3>
  <div class="answer-num answer-num-multi">
    <div class="ans-cell ans-correct"><span class="ans-stmt">ア</span><span class="ans-val">1</span></div>
    <div class="ans-cell ans-correct"><span class="ans-stmt">イ</span><span class="ans-val">1</span></div>
    <div class="ans-cell ans-correct"><span class="ans-stmt">ウ</span><span class="ans-val">1</span></div>
    <!-- エ・オ は data-correct-value で '2' 判定なので **表示しない** -->
  </div>
  <p class="fa-summary"><strong>[一文要約]</strong>　[詳細]</p>
</div>
```

> **v8.11.5 確定版（AP-40）：** ox-grid 型は multi 構造ではなく **single 形式に統一**して `<span class="answer-num">11112</span>` で表示する（A-2 feedback と完全一致）。

多解答型でも `fa-summary` に「正解は1・1・1・1・2」等のリテラル絶対禁止。

## §22-quater. final-answer spoiler-safe canonical（v8.11.7）

v8.7 以来 `revealFinalAnswer()` JS は存在するが、HTML 側 `hidden` 初期宣言が欠落していたため JS reveal が no-op になっていた canonical 欠陥を修復。

- **§22-quater-1**: HTML 要件 ── すべての `<div class="final-answer">` に `hidden` 属性必須（**S68 / AP-30 検出**）
- **§22-quater-2**: `fa-summary` 本文の「正解はN」リテラル禁止（**S70 / AP-32 検出**）
- **§22-quater-3**: §Annex A に CSS パッチ正典組込み（§22-bis fa-summary 直後・§23 cross-grid 直前）：
  - `.answer-num.answer-num-multi` / `.ans-cell` / `.ans-correct` / `.ans-incorrect` / `.ans-stmt` / `.ans-val`
  - `.final-answer[hidden] { display:none !important }`
  - `@keyframes faReveal`
  - 計 8 規則必須（**S69 / AP-31 検出**）
- **§22-quater-4**: §Annex C JS の `revealFinalAnswer()` は変更なし（v8.7 以来既存）

## §22-quinta. A-2 reveal-answer-btn + answer-slot.selected canonical（v8.11.7）

§Annex A に CSS パッチ正典組込み（§22-quater の直後・§23 cross-grid の直前）：

- `.reveal-answer-btn` ── グラデーション + 影 + hover アニメーション。disabled 状態は `opacity:.42`
- `.reveal-answer-btn:hover:not(:disabled)` ── `translateY(-1px)` で浮上
- `.reveal-answer-btn:active:not(:disabled)` ── `translateY(0)` で押下感
- `.reveal-answer-btn:disabled` ── `opacity:.42 / cursor:not-allowed / box-shadow:none`
- `.answer-slot.selected` ── `--accent-soft` 背景 + `--accent` ボーダー + `box-shadow` による選択枠ハイライト

§Annex C JS：

- `handleAnswerSlot(btn)` ── stage 1: 選択ハイライトのみ、`reveal-answer-btn` 有効化
- `handleRevealAnswerBtn(btn)` ── stage 2: 正誤判定 + 正解値開示、`revealFinalAnswer()` 連動
- クリック委譲に `var rb = t.closest('.reveal-answer-btn'); if (rb) { handleRevealAnswerBtn(rb); return; }` を追加

## §22-sexta. A-2 multi-select + ox-grid canonical（v8.11.7）

§Annex A に §22-quinta の直後・§23 cross-grid の直前に CSS パッチ追加：

- `.answer-area[data-answer-type="multi"] .answer-row` ── counter 配置のための `position:relative`
- `.selection-counter` ── 「選択中: N / M 個」表示用、accent カラーの小フォント
- `.answer-ox-grid` ── flex 縦並びコンテナ、`gap:10px`
- `.ox-row` ── 各記述行、accent ホバー
- `.ox-label` ── 記述ラベル（ア/イ/ウ/エ/オ 等）、accent 太字
- `.ox-stmt` ── 任意の記述文配置用（現状未使用、将来拡張用）
- `.ox-btn-group` ── 1/2 ボタンの flex inline コンテナ
- `.ox-btn` ── 1（正）/ 2（誤）ボタン、`selected` / `correct-mark` / `incorrect-mark` 状態あり

§Annex C JS の改訂：

- `getAnswerType(area)` 新設 ── `data-answer-type` 取得
- `updateRevealBtnState(area)` 新設 ── Type 別の有効化判定 + counter 更新
- `handleAnswerSlot(btn)` 拡張 ── Type B (multi) で FIFO トグル
- `handleOxBtn(btn)` 新設 ── ox-row 内の単一選択
- `handleRevealAnswerBtn(btn)` 拡張 ── Type 別に判定ロジック分岐
- クリック委譲に `.ox-btn` ハンドラ追加

---

## §24. Readability Enhancement Layer（v8.11.0 新規 canonical）

`<style>` ブロックの **§23 cross-grid（C-3）規則の直後**、`@media` および SVG inline style consolidated 規則の直前に逐語配置する。

### §24-1. .section h3 小見出し強化

```css
.section h3{
  position:relative;
  margin:26px 0 14px;
  padding:8px 0 8px 14px;
  font-size:1.18rem;
  color:var(--bg-dark);
  border-left:4px solid var(--accent);
  background:linear-gradient(90deg,
    rgba(var(--accent-rgb),.06) 0%,
    transparent 70%);
}
```

### §24-2. cross-card alternating bg

```css
.cross-grid .cross-card:nth-child(even){ background:var(--accent-3); }
.cross-grid .cross-card:nth-child(odd){  background:var(--paper); }
```

### §24-3. memory-item alternating bg by priority

```css
.memory-list .memory-item.priority-a:nth-of-type(even),
.memory-list .memory-item.priority-b:nth-of-type(even),
.memory-list .memory-item.priority-c:nth-of-type(even){ background:var(--accent-3); }
.memory-list .memory-item.priority-a:nth-of-type(odd),
.memory-list .memory-item.priority-b:nth-of-type(odd),
.memory-list .memory-item.priority-c:nth-of-type(odd){ background:var(--paper); }
```

### §24-4. lead-list boxed cards

```css
.lead-list{
  padding-left:0;
  list-style:none;
  margin:14px 0 18px;
}
.lead-list > li{
  position:relative;
  background:var(--paper);
  border-left:4px solid var(--accent);
  border-radius:0 8px 8px 0;
  padding:14px 18px;
  margin-bottom:12px;
  line-height:1.78;
  box-shadow:
    0 1px 2px rgba(0,0,0,.04),
    0 3px 10px rgba(var(--accent-rgb),.08);
  transition:transform .15s ease, box-shadow .15s ease;
}
.lead-list > li:hover{
  transform:translateX(2px);
  box-shadow:
    0 1px 2px rgba(0,0,0,.06),
    0 6px 16px rgba(var(--accent-rgb),.14);
}
.lead-list > li::marker{ content:""; }
.lead-list > li:nth-child(even){ background:var(--accent-3); }
.lead-list > li > strong:first-child{
  display:block;
  margin-bottom:.5em;
  padding-bottom:.4em;
  border-bottom:1px dashed rgba(var(--accent-rgb),.30);
  font-family:var(--font-display);
  font-size:1.05em;
  color:var(--bg-dark);
  letter-spacing:.02em;
}
```

**HTML 側要件：**

- 対象 ul には `class="lead-list"` を必ず付与
- 各 li 先頭の `<strong>` には**末尾「：」を入れてはならない**（dashed 区切り線が「：」の役割を果たす）

### §24-5. 全 `<p>` 字下げ（日本国語的体裁）

```css
p{
  text-indent:1em;
}
/* 除外 */
.figure-caption,
.answer-instruction{
  text-indent:0;
}
```

### §24-6. ハンギングインデント（Grid 方式・HTML wrap 併用）

ラベル始まりの段落の本文が 2 行目以降ラベル下に回り込まないようにする canonical pattern。

#### CSS

```css
.basis-card-body > p.hanging{
  display:grid;
  grid-template-columns:max-content 1fr;
  column-gap:.5em;
  align-items:baseline;
  text-indent:0;
}
.basis-card-body > p.hanging > .hang-body{
  display:block;
}
```

#### HTML pattern

```html
<!-- ❌ bare 形式（NG・AP-26/27 違反） -->
<p><span class="para-num">第108条</span>放火して…</p>
<p><strong>【事案】</strong>他人の事務処理者が…</p>

<!-- ✓ v8.11.0 canonical 形式 -->
<p class="hanging"><span class="para-num">第108条</span><span class="hang-body">放火して、…</span></p>
<p class="hanging"><strong>【事案】</strong><span class="hang-body">他人の事務処理者が…</span></p>

<!-- 判旨パラグラフの場合（class 併用） -->
<p class="judgment-text hanging"><strong>【判旨】</strong><span class="hang-body">「他人の委託により…」</span></p>
```

#### 適用条件

`.basis-card-body > p` の先頭子要素が以下のいずれかの場合 **必ず** `class="hanging"` ＋ `<span class="hang-body">` ラップ：

- `<span class="para-num">…</span>`（条文番号バッジ）
- `<strong>【事案】</strong>` ／ `<strong>【判旨】</strong>` ／ `<strong>I.</strong>` 等

判別基準：`【…】` 隅付き括弧 or `^[IVX]+\.$` ローマ数字 + ピリオド形式 → ラベル扱い。それ以外の `<strong>`（純粋強調）は対象外。

---

## §24-bis. Font Weight Bumps（v8.11.0 canonical）

§Annex A 内の 2 規則について、v8.10.2 から以下の値変更を canonical 化：

```css
/* v8.11.0 改訂 */
.basis-card-body{
  padding:18px 22px 16px;
  font-family:var(--font-quote);
  font-weight:600;         /* ← v8.10.2: 400 から変更 */
  line-height:1.95;
}

a.ref-stat,
a.ref-case{
  display:inline;
  font-family:inherit;
  font-weight:700;         /* ← v8.10.2: 600 から変更 */
  padding:0 3px;
  border-radius:3px;
  text-decoration:none;
  border-bottom:1.5px solid;
  transition:background .15s, color .15s;
}
```

理由：細い明朝（游明朝・Yu Mincho 系）の本文と参照リンクの視認性向上。

---

## §31. SEVERE 自己検証 S1〜S82

AI は配信前に以下を全件実行：

```
S1〜S5   : タグ開閉バランス（div / section / a / span / p）
S6       : <h1>〜<h6> 開閉バランス
S7       : id 重複なし
S8       : href="#X" の X がすべて id で実在
S9       : marker-legend が </header> 直後
S10      : 4 PART すべて存在
S11      : PART A に 2 section（A-1, A-2）← v8.11.0 改訂
S12      : PART B に 5 choice-section
S13      : PART C に 7 section (id="c-1"〜"c-7")
S14      : PART D に 12 drill-block
S15      : answer-area の data-correct-value 設定済み
S16      : answer-area の data-explanation 設定済み
S17      : 各 choice-section に 4 sub-card
S18      : 各 professor sub-card に 4 prof-heading
S19      : key-phrase-box 各 choice-section に 1 個以上
S20      : ref-stat/ref-case のリンク先 id が basis-card 内に存在
S21      : basis-card 各カードに ref-backlinks 存在
S22      : ref-backlinks 内の rb-chip リンク先 id 逆参照可能
S23      : marker-legend に freq-high/freq-mid/freq-low/ron-mark の凡例
S24      : final-answer が C-7 末尾に配置
S25      : footer-spec が PART D 後に配置
S26      : drill-block の ○:× 比率 6:6
S27      : §Annex C JS の universal handler 完備
S28      : doc-header の exam-badge × 4 配置
S29      : quiz-state の data-arena="1" 設定
S30      : KJX/MJX 視覚言語との整合性
S31      : marker-legend の class="marker-legend" 厳格
S32      : final-answer 3 段構成
S33      : fb-verdict/fb-answer 分離レンダリング
S34      : choice-points 配置
S35      : ref-stat/ref-case クラス使用一貫
S36      : ref-backlinks の rb-chip クラス使用一貫
S37      : 各 basis-card に basis-card-header/basis-card-body 構造
S38      : A-2 直後スポイラー禁止
S39      : final-answer 3 段構成厳格
S40      : 事前検証ゲート通過
S41      : 事後検証ゲート通過
S42      : --font-impact 変数定義あり / load 検証
S43      : DB カード内 back-link-row 完全禁止
S44      : rb-chip カラートークン化
S45      : K300 型異常（全文 Mincho 化）非該当
S46      : §Annex B DOM 骨格逐語適用
S47      : §Annex A CSS 12-role font system 完備
S48      : ron-mark::before content:'論' 装飾
S49      : freq-badge ★純化版
S50      : §Annex A canonical CSS 全文逐語コピー
S51      : footer-spec に "TX v8.11.7" 以上＋必須 feature-tag 完備
S52〜S59 : AP-16〜AP-23 検出
S60〜S61 : AP-24 検出（P2/P3 override 形式・pattern marker）
S62〜S63 : K302-16 検出（A-2 feedback クラッシュ）

=== v8.11.0 新規追加 ===
S64 : §24 readability layer 全 6 サブセクション存在検証
      - grep '.section h3{' → 1 件以上
      - grep '.cross-grid .cross-card:nth-child' → 1 件以上
      - grep '.memory-list .memory-item.priority-a:nth-of-type' → 1 件以上
      - grep '.lead-list > li{' → 1 件以上
      - grep '^p\{' で text-indent:1em を含む → 1 件以上
      - grep '.basis-card-body > p.hanging{' → 1 件以上

S65 : §24-6 ハンギングインデント HTML 構造検証
      - <span class="para-num"> または <strong>【…】</strong> で始まる
        .basis-card-body > p は必ず <p class="hanging"> 形式
      - <p class="hanging"> の数と <span class="hang-body"> の数が一致

S66 : PART 順序検証（v8.11.0 改訂）
      - <section id="basis"> が <section id="choice-5"> の後ろにある
      - <section id="basis"> が <section id="c-1"> の前にある
      - .toc-row 内のリンク順序：解答→ア…オ→共通根拠→体系→…

S67 : font-weight 改訂検証＋ AP-26/27/28 検出
      - .basis-card-body の font-weight が 600 以上
      - a.ref-stat / a.ref-case の font-weight が 700
      - .ron-mark{ ... } 内に display:inline-block 含まない（AP-28）
      - .basis-card-body > p に display:flex/grid 直当て rule 不存在（AP-27）
      - .basis-card-body > p に text-indent:-Xem の負値含む rule 不存在（AP-26）

=== v8.11.7 新規追加：spoiler-safe 系（AP-30〜AP-32）===
S68 : final-answer hidden 属性検証（AP-30 検出）
      - すべての <div class="final-answer"> に hidden 属性が付与されていること

S69 : §22-quater-3 CSS パッチ存在検証（AP-31 検出）
      - .answer-num.answer-num-multi
      - .ans-cell / .ans-correct / .ans-incorrect
      - .ans-stmt / .ans-val
      - .final-answer[hidden] { display:none !important }
      - @keyframes faReveal
      上記計 8 規則が <style> 内に存在

S70 : fa-summary 内「正解はN」リテラル禁止（AP-32 検出）
      - <p class="fa-summary"> 内に「正解はN」「正解は[XXXXX]」
        リテラル不存在

=== v8.11.7 新規追加：a2-two-stage-reveal 系（AP-33〜AP-34）===
S71 : answer-instruction canonical 文言固定（AP-33 検出）
      - <p class="answer-instruction"> 内容が
        「選択肢を選んで「解答を表示」を押してください。」固定
        （Type B/C の場合は数字「2 個」「N 個」のみ可変）
      - 正解値リテラル・解説テキスト一切不存在

S72 : reveal-answer-btn 存在検証（AP-34 検出）
      - A-2 解答エリアに
        <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>
        が存在

=== v8.11.7 新規追加：3 Type 対応（AP-35）===
S73 : data-answer-type 整合性検証（AP-35 検出）
      - data-correct-value の形式から判定される type と
        data-answer-type 属性値が一致
        - "^\d+$" → single（data-answer-type は省略可）
        - "^[12]{2,}$" → ox-grid
        - "^\d+(,\d+)+$" → multi
      - Type B/C で対応する UI 要素（.selection-counter / .answer-ox-grid）が存在

=== v8.11.7 新規追加：spoiler-leak-eradication（AP-36〜AP-38）===
S74 : PART A 内「N（XX）正解」リテラル不存在（AP-36 検出）
      - <section id="part-a"> 配下に「(\d+[（(][^）)]+[）)])正解」
        パターン不存在
      - <strong>4（ウエ）正解</strong> 等の混入を機械検出

S75 : data-explanation 先頭リテラル不存在（AP-37 検出）+
      FA .answer-num 構成検証（AP-38 検出）
      - data-explanation="..." 属性値の先頭が
        正解値リテラル（"3,4。"／"11112（ア1…）。"／"3。"等）
        で始まっていない
      - FA は以下の Type 別構成：
        - single: <span class="answer-num">N</span>
        - multi: <div class="answer-num answer-num-multi"> 内に
                 .ans-cell.ans-correct のみ（.ans-incorrect なし）
        - ox-grid: <span class="answer-num">N桁数字</span>（v8.11.5 統一）

=== v8.11.7 新規追加：spoiler-strong-elimination + ox-grid 統一（AP-39〜AP-40）===
S76 : PART A 内 strong での選択肢列挙ネタバレ禁止（AP-39 検出）
      + ox-grid 型 FA を single 形式に統一（AP-40 検出）
      - <section id="part-a"> 配下に
        <strong>\d+[（(][^）)]+[）)]</strong> パターン不存在
        （正解組合せのみ太字でネタバレする状態を解消）
      - ox-grid 型ファイルの FA は <span class="answer-num"> 形式

=== v8.11.7 新規追加：host-injection-safe（AP-41）===
S77 : <script> 内 </body> リテラル禁止（AP-41 検出）
      - 全 <script>...</script> ブロックを正規表現スキャン
      - コメント・文字列・テンプレートリテラル等を含めて
        "</body>" 文字列が 1 件でもヒットすれば違反
      - Lexia 等 host アプリの正規表現注入バグから保護

=== v8.11.7 新規追加：コンテンツ独立性 + 命名規則（AP-42 / S78〜S82）===
※ v8.11.1 の S68〜S72 を renumber

S78 : §0-quad-2 ブラックリスト全文検査（canonical text leakage 検出・AP-42）
      - 生成 HTML の可視テキスト部分から以下を grep し、
        該当問題 PDF で当該論点を扱っていない場合は 1 件でも違反：
          "詐欺罪と他罪の成否"
          "詐欺罪のみが成立し得る"
          "背任行為が同時に詐欺の欺罔行為に当たる"
          "畏怖の一材料"
          "業務上横領罪"
          "偽造通貨行使罪に包含"
          "最判昭28.5.8" "最判昭24.2.8" "東京高判昭28.6.12"
          "大判明5.12.12" "大判明43.6.30"
          "他人のためにその事務を処理する者が、任務に背いて"
          "新聞販売店から集金業務を委託"
          "保険金を詐取する目的で、火災保険"
          "他人に売買代金として偽造通貨を行使"
      - 1 件でもヒットすれば AP-42 として regeneration（§0-quad-3 IQ-2 から再実行）

S79 : §0-quad-1 placeholder 化検証（structural shell only 原則）
      - 以下の要素のテキストが、§Annex B の元テキストと
        3 単語（または 8 連続文字）以上一致する箇所が一切ないこと：
          .problem-text 各々
          .choice-summary, .verdict
          .sub-card.original, .sub-card.explanation, .sub-card.professor
          .basis-card-body の <span class="hang-body"> 本文
          PART C 各 section の本文
          .drill-block の設問・選択肢
      - 一致箇所が検出された場合、当該本文は §0-quad-3 IQ-4/IQ-5 を再実行して書き直す

S80 : §1-bis 命名規則準拠（v8.11.1）
      - <title> 内ファイル ID が「{日本語接頭辞}TX{3桁0埋め数字}」形式
      - .doc-header 内ファイル ID が同上形式
      - footer-spec 1 行目のファイル ID が同上形式
      - 上記 3 箇所のファイル ID が完全一致
      - レガシー形式（K302/MIN145/KEN087 等）が混在していないこと

S81 : 出力先サブフォルダ整合（v8.11.1）
      - 出力先パスが §1-bis-3 対応表に従う
      - 刑TX → outputs/tx/刑TX/、憲TX → outputs/tx/憲TX/、
        民TX → outputs/tx/民TX/、商TX → outputs/tx/商TX/、
        民訴TX → outputs/tx/民訴TX/、刑訴TX → outputs/tx/刑訴TX/、
        行政TX → outputs/tx/行政TX/

S82 : PDF ファイル名からの番号抽出整合（v8.11.1）
      - 入力 PDF ファイル名の最初の連続数字 = 出力ファイル ID 数字部分
      - 3桁未満は前ゼロ 0 埋め済み
      - 抽出不能 PDF（数字なし）は処理中断・確認要請のログあり
```

---

## §31-6. アンチパターンカタログ AP-1〜AP-42

### AP-1〜AP-25（v8.10.2 から継承）

[詳細は §35 / §35-bis 該当症例参照]

### AP-26（v8.11.0 新規）：negative text-indent + overflow:hidden 不整合

**禁止対象：**

```css
.ancestor-with-overflow-hidden .descendant{
  padding-left: Xem;
  text-indent: -Xem;
}
```

祖先要素（`.basis-card` 等）に `overflow:hidden` がある状態で負の text-indent を使うと、ラベルが祖先の左端外に押し出されてクリップされる。実観測症例：chat-002-001「`.para-num` バッジが極端に切れる」。

**正当な代替：** §24-6 の Grid 方式（`display:grid` + `<span class="hang-body">` ラップ）。

### AP-27（v8.11.0 新規）：`<p>` 直当て flex/grid + 混在インライン子要素

**禁止対象：**

```html
<p style="display:flex"><strong>【事案】</strong>本文 <span class="ron-mark">強調</span> 続き</p>
```

`<p>` を flex/grid コンテナにすると、内部の `<strong>` / `<span class="ron-mark">` / `<a class="ref-stat">` 等の**各インライン子要素が個別の flex/grid item になり**、本来単一の line-flow であるべきインライン強調が**別カラム化**して破綻する。実観測症例：chat-002-002「論バッジ＋本文が複数カラムに分裂」。

**正当な代替：** ラベル直後の本文を `<span class="hang-body">` で atomic-wrap してから `display:grid; grid-template-columns:max-content 1fr` を適用（§24-6）。

### AP-28（v8.11.0 新規）：`.ron-mark` display 改変

**禁止対象：**

```css
.ron-mark{
  display:inline-block;   /* ← NG */
  max-width:100%;
}
```

`.ron-mark` を `inline-block` 化すると、長文 ron-mark（10 文字以上）が **atomic block** として振る舞い、行末に収まらない場合に**全体ごと次行にブロックジャンプ**して大きな余白を生む。実観測症例：chat-002-003「ron-mark がブロック単位で改行」。

**正当な canonical：** `.ron-mark { display: inline; }`（既定）を維持。`::before` バッジは `display:inline-block` のまま。

### AP-29（v8.11.0 新規）：over-decoration tendency

**禁止対象：** AI が「user の可読性改善要望」に対して以下のような**過度な装飾追加**で応えること：

- ハブ＆スポーク SVG 図の自動追加
- 4 象限カードでの情報再配置
- trophy-style final-answer（gradient + foil + glow shadow）
- elaborate hover transitions
- 全 PART C を SVG 図表化

実観測症例：chat-002-004「ユーザーから即時撤回要請『そこまで凝らなくてもいい。背景色を交互にしたり、小見出しを見やすくしたりするくらいでよい』」。

**設計指針：** user request の「改善してほしい」「見やすくして」等の**シグナルの粒度**を慎重に読み取り、最小限の介入で要件を満たす。CSS で済むものは CSS で、HTML 改変は本当に必要な場合のみ。SVG 図表追加は **user が明示的に要求**した場合のみ。

判別ヒューリスティック：「user が示した不満点」と「自分の改善案」の差分が**3 倍以上**ある場合、過度装飾の兆候。step-down して最小介入版を提示せよ。

### AP-30（v8.11.7 統合・spoiler-safe）：final-answer hidden 属性欠落

**禁止対象：** `<div class="final-answer">` に `hidden` 属性が付与されていない状態。v8.7 以来 `revealFinalAnswer()` JS は存在するが、HTML 側 `hidden` 初期宣言が欠落しているとページロード時点で正解がそのまま表示され、A-2 で「正答率を見る前にスポイラー」状態となる。

```html
<!-- ❌ NG -->
<div class="final-answer">
  <h3>🎯 正解</h3>
  <span class="answer-num">3</span>
</div>

<!-- ✓ v8.11.7 canonical -->
<div class="final-answer" hidden>
  <h3>🎯 正解</h3>
  <span class="answer-num">3</span>
</div>
```

**検出：** S68 で全 `<div class="final-answer">` に `hidden` 属性が付与されていることを確認。

### AP-31（v8.11.7 統合・spoiler-safe）：§22-quater-3 CSS パッチ欠落

**禁止対象：** `<style>` 内に `.final-answer[hidden]{display:none !important}` ＋ `@keyframes faReveal` ＋ `.answer-num.answer-num-multi` 系 8 規則のいずれかが欠落している状態。AP-30 で `hidden` 属性を付与しても CSS パッチがなければ `display:none` が効かず、結局スポイラーが残る。

**検出：** S69 で §22-quater-3 の 8 規則がすべて `<style>` 内に存在することを確認。

### AP-32（v8.11.7 統合・spoiler-safe）：fa-summary 内「正解はN」リテラル

**禁止対象：** `<p class="fa-summary">` 本文内に「正解はN」「正解は[XXXXX]」等の正解値リテラルを記述すること。

```html
<!-- ❌ NG -->
<p class="fa-summary"><strong>正解は3。</strong>　詐欺罪が成立する...</p>

<!-- ✓ v8.11.7 canonical -->
<p class="fa-summary"><strong>背任と詐欺の二重評価回避</strong>　詐欺罪の欺罔行為に背任が含まれる場合、判例は詐欺罪のみを成立させる...</p>
```

「正解はN」を `fa-summary` 内に書くと、`final-answer[hidden]` が解除される前にソース表示・デバッグ操作でスポイラーが露出する。`<span class="answer-num">N</span>` が別途存在するため `fa-summary` 内では論点要約のみに留める。

**検出：** S70 で `<p class="fa-summary">` 内に該当リテラルが不存在であることを確認。

### AP-33（v8.11.7 統合・a2-two-stage-reveal）：answer-instruction 内に正解値・解説テキスト

**禁止対象：** `<p class="answer-instruction">` 内容を canonical 文言「選択肢を選んで「解答を表示」を押してください。」から逸脱させること。

```html
<!-- ❌ NG -->
<p class="answer-instruction">3 をクリックすると正解です。詐欺罪が成立する理由は...</p>
<p class="answer-instruction">正解：3。クリックすると詳細表示。</p>

<!-- ✓ v8.11.7 canonical（Type A） -->
<p class="answer-instruction">選択肢を選んで「解答を表示」を押してください。</p>

<!-- ✓ v8.11.7 canonical（Type B/C）── 数字部分のみ可変 -->
<p class="answer-instruction">選択肢を 2 個選んで「解答を表示」を押してください。</p>
<p class="answer-instruction">各記述に「1（正）」または「2（誤）」を選んで「解答を表示」を押してください。</p>
```

**検出：** S71 で `<p class="answer-instruction">` 内に正解値リテラル・解説テキストが不存在であることを確認。

### AP-34（v8.11.7 統合・a2-two-stage-reveal）：reveal-answer-btn 欠落

**禁止対象：** A-2 解答エリア内に `<button class="reveal-answer-btn" type="button" disabled>解答を表示</button>` が存在しない状態。これがないと Stage 1 → Stage 2 の 2 段階開示プロトコルが成立せず、A-2 が即時 reveal モードに退化する。

**検出：** S72 で `<button class="reveal-answer-btn">` の存在を確認。

### AP-35（v8.11.7 統合・3 Type 対応）：data-answer-type 不整合

**禁止対象：** `data-correct-value` の形式から自動判定される type と `data-answer-type` 属性値が不整合な状態。

```html
<!-- ❌ NG: data-correct-value="11112" は ox-grid のはずだが multi 宣言 -->
<div class="answer-area" data-correct-value="11112" data-answer-type="multi">

<!-- ❌ NG: data-correct-value="1,2" は multi のはずだが ox-grid UI -->
<div class="answer-area" data-correct-value="1,2" data-answer-type="ox-grid">
  <div class="answer-ox-grid">...</div>

<!-- ✓ v8.11.7 canonical -->
<div class="answer-area" data-correct-value="11112" data-answer-type="ox-grid">
  <div class="answer-ox-grid">...</div>
```

**検出：** S73 で `data-correct-value` 形式と `data-answer-type` 属性が整合し、対応する UI 要素（`.selection-counter` / `.answer-ox-grid`）が存在することを確認。

### AP-36（v8.11.7 統合・spoiler-leak-eradication）：PART A 内「N（XX）正解」リテラル

**禁止対象：** PART A の問題文セクション内に「N（XX）正解」形式のリテラルを記述すること（組合せ型問題で典型的）。

```html
<!-- ❌ NG -->
<section id="part-a">
  <div class="problem-text">
    1（アイ）／2（アオ）／<strong>4（ウエ）正解</strong>／5（エオ）
  </div>
</section>

<!-- ✓ v8.11.7 canonical -->
<section id="part-a">
  <div class="problem-text">
    選択肢：1（アイ）／2（アオ）／3（イウ）／4（ウエ）／5（エオ）
  </div>
</section>
```

**検出：** S74 で正規表現 `(\d+[（(][^）)]+[）)])正解` が PART A 配下に不存在であることを確認。

### AP-37（v8.11.7 統合・spoiler-leak-eradication）：data-explanation 先頭の正解値リテラル

**禁止対象：** `data-explanation` 属性値の先頭に正解値リテラル（"3,4。" / "11112（ア1・イ1…）。" / "3。" / "4（ウ・エ）。" 等）を記述すること。

```html
<!-- ❌ NG -->
<div class="answer-area" data-correct-value="3,4"
     data-explanation="3,4。背任罪と詐欺罪の関係について判例は...">

<!-- ✓ v8.11.7 canonical -->
<div class="answer-area" data-correct-value="3,4"
     data-explanation="背任罪と詐欺罪の関係について判例は...">
```

ページソース表示・デバッグツール経由のスポイラー露出を防ぐ。

**検出：** S75 で `data-explanation` 先頭の正解値リテラル不存在を確認。

### AP-38（v8.11.7 統合・spoiler-leak-eradication）：FA `.answer-num` に不正解の数字表示

**禁止対象：** Type B/C の FA で、不正解の数字（multi）や誤判定の記述（ox-grid '2' 桁）まで `.answer-num-multi` 内に表示すること。

```html
<!-- ❌ NG (multi 型・正解は 3,4 だが 1,2,5 も表示) -->
<div class="answer-num answer-num-multi">
  <span class="ans-cell ans-incorrect">1</span>
  <span class="ans-cell ans-incorrect">2</span>
  <span class="ans-cell ans-correct">3</span>
  <span class="ans-cell ans-correct">4</span>
  <span class="ans-cell ans-incorrect">5</span>
</div>

<!-- ✓ v8.11.7 canonical (multi 型) -->
<div class="answer-num answer-num-multi">
  <span class="ans-cell ans-correct">3</span>
  <span class="ans-cell ans-correct">4</span>
</div>
```

**検出：** S75 で FA `.answer-num-multi` 内に `.ans-cell.ans-incorrect` が存在しないことを確認。

### AP-39（v8.11.7 統合・spoiler-strong-elimination）：PART A 内 `<strong>N（XX）</strong>` 太字ネタバレ

**禁止対象：** PART A の問題文セクション内で、正解組合せのみ `<strong>` で太字強調すること。accent カラーで視覚的にネタバレが残存する。

```html
<!-- ❌ NG -->
<div class="problem-text">
  1（アイ）／2（アオ）／3（イウ）／<strong>4（ウエ）</strong>／5（エオ）
</div>

<!-- ✓ v8.11.7 canonical -->
<div class="problem-text">
  選択肢：1（アイ）／2（アオ）／3（イウ）／4（ウエ）／5（エオ）
</div>
```

`<strong>` タグごと削除し、全選択肢を同書式の平文に統一。AP-36 と組み合わせて完全なネタバレ消去を達成。

**検出：** S76 で PART A 配下に `<strong>\d+[（(][^）)]+[）)]</strong>` が不存在を確認。

### AP-40（v8.11.7 統合・ox-grid-fa-unification）：ox-grid 型 FA を multi 構造で表示

**禁止対象：** `data-answer-type="ox-grid"` 型ファイルで、FA を `.answer-num-multi` 構造で表示すること。A-2 feedback では「正解は 11112」と数字表示しているため、FA との表記不一致が生じる。

```html
<!-- ❌ NG (v8.11.4 までの仕様、v8.11.5 で廃止) -->
<div class="answer-num answer-num-multi">
  <span class="ans-cell ans-correct">ア</span>
  <span class="ans-cell ans-correct">イ</span>
  <span class="ans-cell ans-correct">ウ</span>
  <span class="ans-cell ans-correct">エ</span>
</div>

<!-- ✓ v8.11.5/v8.11.7 canonical (single 形式に統一) -->
<span class="answer-num">11112</span>
```

**検出：** S76 で ox-grid 型ファイルの FA が `<span class="answer-num">` 形式であることを確認。

### AP-41（v8.11.7 統合・host-injection-safe）：`<script>` 内 `</body>` リテラル混入

**禁止対象：** `<script>...</script>` ブロック内のコメント・文字列リテラル・テンプレートリテラル等あらゆる箇所に `</body>` のリテラル文字列を含めること。

**症状：** host アプリ（Lexia 等）が iframe `srcdoc` に単一 HTML を注入する際、`</body>` 直前にホスト用 QUIZ_TRACKER スクリプトを注入する正規表現が**最初の出現** = `<script>` 内のリテラルにマッチ。注入が `<script>` タグ内部（コメントの途中等）になり JS 構文崩壊。クイズハンドル・リンクジャンプ・○×ボタンなど iframe 内の**全ての JS 機能が完全に死ぬ**。

**v8.11.6 以前の事故：** §Annex C JS 先頭コメントに「`</body> 直前の <script> ブロック内部に逐語コピー`」と書いてあったため、全 TX 生成ファイル（例：刑TX299、K299 等）で本症状が発生。

**正当な代替表記：**

- 「`body 閉じタグ`」
- 「`</` + `body>`」（連結回避）
- 「`</body\u200b>`」（ゼロ幅スペース挟む）
- 「`< /body>`」（半角スペース挟む）

**修正済み canonical：** §Annex C 内の先頭コメントから当該リテラルを除去済み（「body 閉じタグ直前の script ブロック内部に逐語コピー」と表記変更）。

**検出：** S77 で全 `<script>` ブロックを正規表現スキャン。

### AP-42（v8.11.1 由来・最重要）：canonical text leakage（正典本文の流用）

> **本 AP は v8.11.1 で AP-30 として導入されたが、v8.11.7 統合時に番号衝突回避のため AP-42 に renumber された。内容は変更なし。**

**禁止対象：** §Annex B body skeleton に byte-level 埋込された KTX301 の**問題固有テキスト**を、別問題の TX ファイル生成時に**そのまま温存・流用**すること。

**典型的な発現パターン：**

```html
<!-- ❌ 民法の代理問題を生成しているのに、KTX301 の詐欺罪文言が混入 -->
<div class="problem-text"><span class="choice-num-inline">ア</span>
  他人のためにその事務を処理する者が、任務に背いて、その他人を欺く行為をし…
</div>

<!-- ❌ 憲法の表現の自由問題を生成しているのに、刑法の判例文言が混入 -->
<div class="sub-card explanation">
  <p>背任行為が同時に詐欺の欺罔行為に当たる場合、判例は背任罪を別個に構成せず…</p>
</div>

<!-- ❌ basis-card 内に本問と無関係な「最判昭28.5.8」がそのまま残存 -->
<div class="basis-card case-card">
  <div class="basis-card-header"><h3 id="case-fraud">最判昭28.5.8</h3></div>
  <div class="basis-card-body">
    <p class="hanging"><strong>【事案】</strong><span class="hang-body">　…</span></p>
  </div>
</div>
```

**原因：** Claude Code 等の自動生成環境で、§Annex A/B/C の「逐語コピー」指示を AI が**過度に保守的**に解釈し、構造シェルだけでなく**本文テキストまで温存**してしまう。とくに以下の認知エラーが頻発：

- 「とりあえず Annex B をそのまま貼ってから後で差替えればよい」→ 差替え漏れが発生
- 「KTX301 の文体が canonical だから流用すれば品質が安定する」→ 内容と無関係でも文言が温存
- 「PART C の体系は普遍的だから KTX301 のままでよい」→ 科目・論点が違うのに刑法体系が残る

**実観測症例：**

- xnh セッション「複数科目の生成で解説文がすべて KTX301 詐欺罪論点をなぞる」
- 民法問題なのに「業務上横領罪」「畏怖の一材料」等の刑法用語が PART C に出現
- 憲法問題の basis-card に刑法判例が並列配置される

**正当な canonical（§0-quad 全文）：**

§Annex の「逐語コピー」は **structural shell（タグ名・class 名・id 名・属性キー・ネスト順序）のみ**を対象とし、**タグ内の自然言語テキストは byte-level 不一致**でなければならない（問題が真に同一論点でない限り）。

検出基準は S68（ブラックリスト全文検査）／S69（structural shell 原則違反 ── §Annex B 元テキストとの 3 単語以上一致）。違反検出時は §0-quad-3 IQ-2 に戻り、本文を完全空文字列化してから再執筆。

**運用上の自己問答：** 生成完了直前に AI は以下を自問せよ──「いま生成したこの解説文を、KTX301（詐欺罪と他罪の成否）の解説文と並べて diff したとき、本文テキストレベルで一致する箇所が一文でもあるか？ あるなら、それは本当に偶然か、それとも §Annex B からの leakage か？」。判断に迷うなら書き直す。

---

## §32. 3 パターン色変換ルール（P1/P2/P3）── P1 absolute canon 継承

### §32-1. パターン判定

| パターン | 正答率帯 | 名称 | 構造 |
|:-:|:-:|:--|:--|
| **P1** | ≥ 60% | ローズシャンブル | **唯一の構造正典**。§Annex A の `:root` 既定値・§Annex B body skeleton・§Annex C JS をそのまま使用。override 追記不要 |
| **P2** | 40〜60% | セージブラリー | P1 と完全に同一の構造。§Annex A-bis-2 の `:root{}` 単一ブロックのみ追記 |
| **P3** | < 40% | ラベンダードーン | P1 と完全に同一の構造。§Annex A-bis-3 の `:root{}` 単一ブロックのみ追記 |

### §32-2. P1 absolute canon 鉄則

> **P1 ファイルと P2/P3 ファイルを diff した際、差分は §Annex A-bis-2 or -3 の `:root{}` 27 行ブロックのみでなければならない**（footer-spec のパレット名表記を除く）。

### §32-3. 27 色変数

§Annex A 冒頭の `:root` 第二ブロックに以下 27 変数（`--accent` / `--accent-rgb` / `--mid` / `--mid-rgb` / `--light` / `--base` / `--soft` / `--paper` / `--text` / `--bg-dark` / `--accent-3` / `--accent-soft` / `--border-mid` / `--kp-text-color` / `--hl-super` / `--hl-high` / `--hl-std` / `--tan-super` / `--tan-high` / `--tan-std` / `--rank-A` / `--rank-B` / `--rank-C` / `--rank-D` / `--freq-high` / `--freq-high-rgb` / `--freq-high-deep` / `--freq-mid` / `--freq-mid-rgb` / `--freq-mid-deep` / `--freq-low` / `--freq-low-rgb` / `--freq-low-deep` / `--recall-correct` / `--recall-correct-light` / `--recall-incorrect` / `--recall-incorrect-light`）。

### §32-4. override の厳密形式

P2/P3 の override ブロックは **`<style>` 末尾の単一 `:root{}` ブロックのみ**。他のセレクタ追加・at-rule 追加・フォント変数 override は絶対禁止（AP-24／S60）。

---

## §33. footer-spec canonical（v9.0.0 GENKEI 版）

```html
<div class="footer-spec">
  <p>[ファイル ID]・[科目]（[出典：年度-問題番号] [論点タイトル]）</p>
  <p>正答率：[N]%／パターン [P1|P2|P3]「[名称]」適用</p>
  <p>正解：[正解値]（[内容]）</p>
  <p class="footer-meta">
    Spec:
    <span class="feature-tag">TX v9.0.0 GENKEI</span>・
    <span class="feature-tag">genkei-skeleton</span>・
    <span class="feature-tag">design-byte-lock</span>・
    <span class="feature-tag">content-independence</span>・
    <span class="feature-tag">ktx301-canon</span>・
    <span class="feature-tag">embedded-canon</span>・
    <span class="feature-tag">readability-layer</span>・
    <span class="feature-tag">hanging-grid</span>・
    <span class="feature-tag">basis-order-v2</span>・
    <span class="feature-tag">a2-feedback-canon</span>・
    <span class="feature-tag">rbchip-patched</span>・
    <span class="feature-tag">k302-immune</span>・
    <span class="feature-tag">p2p3-unified</span>・
    <span class="feature-tag">p1-absolute</span>・
    <span class="feature-tag">jp-prefix-naming</span>・
    <span class="feature-tag">spoiler-safe</span>・
    <span class="feature-tag">multi-answer-css</span>・
    <span class="feature-tag">a2-two-stage-reveal</span>・
    <span class="feature-tag">a2-multi-ox-support</span>・
    <span class="feature-tag">spoiler-leak-eradication</span>・
    <span class="feature-tag">spoiler-strong-elimination</span>・
    <span class="feature-tag">ox-grid-fa-unification</span>・
    <span class="feature-tag">host-injection-safe</span>・
    <span class="feature-tag">[P1|P2|P3] [名称]</span>・
    <span class="feature-tag">[特記事項]</span>
  </p>
</div>
```

**v9.0.0 GENKEI 必須 feature-tag：**

- `TX v9.0.0 GENKEI`（**新規**：v8.11.7 → v9.0.0 メジャー昇格。Annex B が逐語正典から純骨格スケルトンに転換）
- v9.0.0 GENKEI 由来：`genkei-skeleton`（HTML body は問題固有内容を含まない骨格のみ）／`design-byte-lock`（CSS/JS は刑TX300 由来 byte-identical）
- v8.11.1 由来：`jp-prefix-naming`／`content-independence`（GENKEI で構造的に保証）
- v8.11.7 統合（原始 v8.11.1 由来）：`spoiler-safe`／`multi-answer-css`
- v8.11.2 由来：`a2-two-stage-reveal`
- v8.11.3 由来：`a2-multi-ox-support`
- v8.11.4 由来：`spoiler-leak-eradication`
- v8.11.5 由来：`spoiler-strong-elimination`／`ox-grid-fa-unification`
- v8.11.6-hotfix1 由来：`host-injection-safe`
- 既存（v8.11.0）：`ktx301-canon`（系譜継承タグ）／`embedded-canon`／`readability-layer`／`hanging-grid`／`basis-order-v2`／`a2-feedback-canon`／`rbchip-patched`／`k302-immune`／`p2p3-unified`／`p1-absolute`

> **注：** ファイル ID には §1-bis-1 形式（例：`刑TX299`）を使用。レガシー形式（K299 等）の混在は S80 違反。

---

## §34-bis. v8.10.2 → v8.11.0 移行手順（12 ステップ）

### ステップ 0：【最優先】§0-tri STEP 1（既存スタイル完全破棄）実行

**v8.11.0 で特に破棄ログに残すべき項目：**
- 旧 PART 順序（A-3 が PART A 内にあった構造）→ A-3 を抽出して PART B 後ろに再配置
- 旧 `padding-left + 負 text-indent` ハンギング規則 → 削除
- 旧 `<p>` 直当て flex/grid 規則 → 削除
- 旧 `.ron-mark { display:inline-block }` → 削除
- 旧 `#answer-feedback strong { color:#fff !important; ... }` → 削除（v8.10.2 規律継承）
- 旧 `feedback.innerHTML = '<strong style="...">'` → §Annex C handleAnswerSlot に置換
- 旧 `<div class="answer-slot">` → `<button class="answer-slot">` 置換

### ステップ 1：§35 / §35-bis K302 型異常検出（grep 走査・K302-17 含む）

### ステップ 2：§Annex A CSS 全文逐語上書き

§Annex A の埋込 CSS をそのまま `<style>` 内に貼付。**§24 readability layer（§24-1〜§24-6）が含まれていることを確認**。P2/P3 ファイルは §Annex A-bis-2 or -3 を末尾に追記。

### ステップ 3：§Annex C JS 全文逐語上書き

### ステップ 4：§Annex B body skeleton 構造に整合

**A-3 を PART B 後ろに再配置**。answer-area の data 属性 / answer-slot の button 化を完全適用。

### ステップ 5：section-title 全件 sec-icon 化

### ステップ 6：PART C content wrapper 化（§17-bis）

### ステップ 7：C-7 memory-item 化

### ステップ 8：多解答 final-answer 化

### ステップ 9：ラベル始まり段落の hanging 化

`.basis-card-body > p` の中で `<span class="para-num">` または `<strong>【…】</strong>` で始まるものを **すべて** `<p class="hanging"><[label]><span class="hang-body">[本文]</span></p>` 形式に書き換え。判旨パラグラフは `class="judgment-text hanging"` の併用。

### ステップ 10：lead-list 化

C-5「運用上の鉄則」／C-6「出題傾向の分析」・「関連問題・参考」の `<ul>` に `class="lead-list"` を付与。各 li 先頭 `<strong>` の末尾「：」を除去。

### ステップ 11：footer-spec バージョン更新（`TX v8.11.0` ＋必須 feature-tag 追記）

### ステップ 12：S60 / S61 / S62 / S63 / **S64 / S65 / S66 / S67** 実行＋構造 diff 検査

---

## §34-quater. v8.11.1 → v8.11.2 minor 更新 5 ステップ

v8.11.1 で生成済みの既存ファイルは §0-tri ゼロベース再構築を経ずに、以下 5 ステップのみで v8.11.2 相当へ minor 更新可能。

**STEP 1**：`<p class="answer-instruction">...</p>` の内容を「選択肢を選んで「解答を表示」を押してください。」固定文に強制統一（AP-33 解消）。

**STEP 2**：`<div class="answer-area">` 内の `<div id="answer-feedback"` の直前に `<button class="reveal-answer-btn" type="button" disabled>解答を表示</button>` を挿入（AP-34 解消）。

**STEP 3**：`<style>` ブロック内、§22-quater の直後・§23 cross-grid の直前に §22-quinta CSS パッチを逐語追加（`.reveal-answer-btn` 関連 4 規則 ＋ `.answer-slot.selected` の計 5 規則）。

**STEP 4**：`<script>` ブロック内の `handleAnswerSlot` 関数全体を新仕様（stage 1: 選択ハイライトのみ）に置換 ＋ `handleRevealAnswerBtn` 関数を新設（stage 2: 正誤判定＋正解値開示）＋ クリック委譲に `.reveal-answer-btn` 分岐を追加。

**STEP 5**：footer-spec の `TX v8.11.1` → `TX v8.11.2` 置換、`a2-two-stage-reveal` feature-tag を追加。S71／S72 検証通過を確認。

---

## §34-quinquies. v8.11.2 → v8.11.3 minor 更新 5 ステップ

v8.11.2 で生成済みの既存ファイルは §0-tri を経ずに、以下 5 ステップで v8.11.3 相当へ minor 更新可能。

**STEP 1**：`data-correct-value` 属性値から Type を自動判定し、`<div class="answer-area">` 開始タグに `data-answer-type="single|multi|ox-grid"` を追加。

**STEP 2**：Type B (multi) の場合、`<p class="answer-instruction">` 文言を「選択肢を {N} 個選んで「解答を表示」を押してください。」に変更し、`<div class="answer-row">` の直後に `<p class="selection-counter">選択中: 0 / {N} 個</p>` を挿入。

**STEP 3**：Type C (ox-grid) の場合、`<div class="answer-row">...</div>` を `<div class="answer-ox-grid">` 構造に置換（{N} 個の `.ox-row` を生成）。`<p class="answer-instruction">` 文言を「各記述に「1（正）」または「2（誤）」を選んで「解答を表示」を押してください。」に変更。`<h3>` を「各記述に正誤を判定」に変更。

**STEP 4**：`<style>` ブロックの §22-quinta 直後・§23 cross-grid 直前に §22-sexta CSS パッチを逐語追加。`<script>` ブロックの `handleAnswerSlot` / `handleRevealAnswerBtn` を新仕様（Type 別分岐）に置換、`handleOxBtn` / `getAnswerType` / `updateRevealBtnState` 関数を新設、クリック委譲に `.ox-btn` 分岐を追加。

**STEP 5**：footer-spec の `TX v8.11.2` → `TX v8.11.3` 置換、`a2-multi-ox-support` feature-tag を追加。S73 検証通過を確認。

---

## §34-sexies. v8.11.3 → v8.11.4 minor 更新 5 ステップ

v8.11.3 で生成済みの既存ファイルは §0-tri を経ずに、以下 5 ステップで v8.11.4 相当へ minor 更新可能。

**STEP 1**：PART A `<section id="part-a">` 内の `<strong>N（XX）正解</strong>` 形式を全て `<strong>N（XX）</strong>` に置換（AP-36 解消）。strong タグなしの「N（XX）正解」も同様に「正解」リテラルを削除。

**STEP 2**：`data-explanation="..."` 属性の値の先頭から、正解値リテラル（`3,4。`、`11112（ア1・イ1・...）。`、`3。`、`4（ウ・エ）。` 等）を句点まで削除（AP-37 解消）。

**STEP 3**：FA `.answer-num` を Type に応じて正解の数字のみ表示する形式に変換（AP-38 解消）：

- single: `<span class="answer-num">N</span>`（変更なし）
- multi: `<div class="answer-num answer-num-multi">` + `<span class="ans-cell ans-correct">N</span>` のみ（正解の数字数だけセルを生成、`ans-incorrect` セルは生成しない）
- ox-grid: `<div class="answer-num answer-num-multi">` + `<span class="ans-cell ans-correct">ラベル</span>` のみ（`data-correct-value` の `1` 桁に対応するラベルのみセル化、`2` 桁の記述はスキップ）。**注：v8.11.5 でさらに `<span class="answer-num">` 単一形式に統一**

**STEP 4**：footer-spec の `TX v8.11.3` → `TX v8.11.4` 置換、`spoiler-leak-eradication` feature-tag を追加。

**STEP 5**：S74／S75 検証通過を確認。

---

## §34-septies. v8.11.4 → v8.11.5 minor 更新 5 ステップ

v8.11.4 で生成済みの既存ファイルは §0-tri を経ずに、以下 5 ステップで v8.11.5 相当へ minor 更新可能。

**STEP 1**：PART A `<section id="part-a">` 内の `<strong>(\d+[（\(][^）\)]+[）\)])</strong>` 形式を `\1` に置換（strong タグごと削除・AP-39 解消）。組合せ型問題の選択肢列挙で正解のみ太字になっていた状態を解消し、全選択肢を同じ書式の平文に統一。

**STEP 2**：ox-grid 型ファイル（`data-answer-type="ox-grid"`）の FA `<div class="answer-num answer-num-multi">...</div>` を `<span class="answer-num">{data-correct-value}</span>` に置換（AP-40 解消）。multi 型と single 型は変更なし。

**STEP 3**：footer-spec の `TX v8.11.4` → `TX v8.11.5` 置換、`spoiler-strong-elimination` および `ox-grid-fa-unification` feature-tag を追加。

**STEP 4**：S76 検証通過を確認。

**STEP 5**：必要なら §34-octies（v8.11.6-hotfix1 適用）も即時実行。

---

## §34-octies. v8.11.5/v8.11.6 → v8.11.6-hotfix1 minor 更新 2 ステップ

v8.11.5 / v8.11.6 で生成済みの既存ファイルは以下 2 ステップで host-injection-safe 化可能。

**STEP 1**：`</body>` 直前の `<script>` ブロックの全コメント・文字列リテラルを走査し、`</body>` リテラルが含まれる箇所を以下のいずれかの代替表記に置換：

- 「`body 閉じタグ`」
- 「`</` + `body>`」
- 「`</body\u200b>`」（ゼロ幅スペース挟む）
- 「`< /body>`」（半角スペース挟む）

**STEP 2**：`python scripts/validate-tx.py <ファイル>` で S77 が通過することを確認。

---

## §34-novies. v8.11.6-hotfix1 → v8.11.7 minor 更新 3 ステップ

v8.11.6-hotfix1 まで終えたファイルを v8.11.7（本仕様書版）へ最終揃え。

**STEP 1**：footer-spec の `TX v8.11.6` → `TX v8.11.7` 置換。`jp-prefix-naming` ／ `content-independence` feature-tag を追加。

**STEP 2**：ファイル ID / `<title>` / `.doc-header` / footer-spec の 3 箇所を §1-bis-1 形式（{日本語接頭辞}TX{3桁0埋め}）に統一。レガシー接頭辞（K/MIN/KEN 等）の混在を排除。

**STEP 3**：出力先サブフォルダを §1-bis-3 対応表通り（`outputs/tx/{科目TX}/` 配下）に移動。S78〜S82 検証通過を確認。

---

## §35. K302 型異常 17 症状検出

| 症状 ID | 部位 | 症状 | 検出 SEVERE |
|:-:|:--|:--|:-:|
| K302-1 | PART D drill | `drill-header` / `drill-topic` 使用 | S52 |
| K302-2 | PART D quiz | `quiz-options` / `quiz-option` / `quiz-explanation` 使用 | S52 |
| K302-3 | PART D drill | MCQ 形式（3-4 択ボタン）使用 | S53 |
| K302-4 | PART D section | `id="part-d-arena"` 使用 | S52 |
| K302-5 | PART D counter | `arena-wrong` id 使用 | S52 |
| K302-6 | C-7 final-answer | `final-answer-label`/`final-answer-num`/`final-answer-detail` 使用 | S54 |
| K302-7 | C-7 memory | `<div class="sub-card original"><ol>...</ol></div>` 流用 | S55 |
| K302-8 | C-1〜C-7 section-title | 素 span（sec-icon 欠落） | S56 |
| K302-9 | PART C `<table>` | `cmp-table-wrap` 親 div 欠落 | S57 |
| K302-10 | PART C `<svg>` | `figure-wrap` + `figure-caption` 欠落 | S57 |
| K302-11 | C-3 cross-card | `cross-grid` 親欠落 | S57 |
| K302-12 | C-1〜C-7 section | `<nav class="sec-nav">` 不在 | (構造) |
| K302-13 | PART C title | U+2015 単独使用（canonical は U+2500×2 `──`） | (文字) |
| K302-14 | 多解答 final-answer | `<span class="answer-num">` に 2 文字超 | S58 |
| K302-15 | P2/P3 CSS override | `:root{}` 以外のセレクタ存在 or pattern-conditional marker | S60/S61 |
| K302-16 | A-2 feedback | 旧 `#answer-feedback strong{color:#fff !important}` 等 | S62/S63 |
| **K302-17（v8.11.0 新規）** | **A-3 配置 / §24 layer / hanging-indent / ron-mark display / over-decoration** | **以下のいずれか：(1) `<section id="basis">` が PART B の前にある／(2) §24 readability layer 全 6 サブセクションが `<style>` 内に存在しない／(3) `.basis-card-body > p` の `<span class="para-num">` 始まり段落が `class="hanging"` を持たない／(4) `.ron-mark` に `display:inline-block` が指定されている／(5) `display:flex` / `display:grid` が `.basis-card-body > p` に直接指定されている／(6) 負 text-indent パターン残存** | **S64〜S67** |

### §35-3. 救済手順

1. 単一症状＋周辺 canonical 完備 → 当該部位のみ §Annex B から再生成
2. 複数症状共存 → ファイル全体を §Annex A/B/C から再生成
3. K302-17 → A-3 配置／§24 layer／hanging 構造／ron-mark display の全領域を §Annex A/B/C から完全再生成。surgical fix は禁止

---

## §35-bis. 実観測症例カタログ

### v8.10.2 までの既存症例

K302 / K316 fonts 欠落、exam-badge 改竄、KTX298-v8.6 A-2 feedback クラッシュ症例等（v8.10.2 から継承）。

### chat-002-001：KTX301 v10「`.para-num` バッジ極端クリップ」

**発現条件：**

- `.basis-card { overflow:hidden }` が祖先に存在
- 子孫の `<p>` に `padding-left:5.5em; text-indent:-5.5em;` が適用

**症状：** 「第109条1項」「第1項」等のバッジが**極小の色片**にまでクリップされて文字内容がほぼ消失。

**真因：** `text-indent: -5.5em` がラベル inline-block を祖先の content-box 左端よりさらに 5.5em 左に押し出すが、祖先 `.basis-card { overflow:hidden }` がそれを切り捨てる。

**救済：** AP-26 救済 → §24-6 Grid 方式に置換。

### chat-002-002：KTX301 v9「論バッジ＋本文の複数カラム分裂」

**発現条件：** `<p>` に直接 `display:flex; align-items:baseline` が当たる＋内部に `<span class="para-num">` ＋プレーンテキスト＋`<span class="ron-mark">` 等の**混在インライン子要素**。

**症状：** 各 `<span>` が flex item として独立カラム化。「論バッジ→詐欺罪を構成し」と「右は単に」と「動機の不法」がそれぞれ別カラムに分裂。

**真因：** flex/grid コンテナの child は anonymous wrapper（テキストノード）も含めて個別 item 化する。混在 inline 子要素を atomic に保つには事前 wrap が必須。

**救済：** AP-27 救済 → `<span class="hang-body">` で本文をラップしてから Grid 適用（§24-6）。

### chat-002-003：KTX301 v11.1「ron-mark ブロックジャンプ」

**発現条件：** `.ron-mark { display:inline-block; max-width:100%; }` ＋長文 ron-mark（15 文字以上）。

**症状：** 行末に収まらない ron-mark が**全体ごと次行へジャンプ**。前後に大きな縦余白。

**真因：** inline-block の atomic 性質。content が長くて current line に入らない場合、wrap 不可で全体が次行送り。Japanese text の per-character 改行ルールと相性が悪い。

**救済：** AP-28 救済 → `.ron-mark { display: inline }`（既定）を維持。badge orphan は許容。

### chat-002-004：KTX301 v1「過度装飾の自動追加」

**発現条件：** user が「凝って美しく仕上げてほしい」と曖昧な要望→ AI が最大限解釈で SVG・4 象限カード・trophy 装飾等を 16,000 chars の CSS で追加実装。

**症状（user 反応）：** 即時撤回要請。

**真因：** AI 側の「全力で応える」バイアス。曖昧シグナルを最大解釈し、最小介入の選択肢を提示しない。

**救済：** AP-29 救済 → 最小介入案を先に提示し、user 反応に応じて段階的拡張。

---

## §36. v8.11.7 設計総括

### 36-1. v8.11.7 の核心

**v8.11.7 追加要素：「v8.11.2〜v8.11.6 全機能の一括統合 ＋ 番号衝突の合理的再採番」**

v8.11.0 で確立した「KTX301 canonical 移行＋可読性レイヤー化＋chat-002 教訓化＋仕様書一元化」、および v8.11.1 で導入した「日本語接頭辞 + TX 命名規則 ＋ §0-quad コンテンツ独立性プロトコル」を基盤に、v8.11.7 では原始 v8.11.x チェーン（v8.11.2〜v8.11.6-hotfix1）で蓄積された 7 機能を一括統合：

- **a2-two-stage-reveal**（v8.11.2 由来）：Stage 1 選択 → Stage 2 開示の厳格分離
- **3 Type 対応**（v8.11.3 由来）：single / multi / ox-grid 自動分岐
- **spoiler-leak-eradication**（v8.11.4 由来）：PART A 内・data-explanation 先頭のリテラル排除＋FA 正解のみ表示
- **spoiler-strong-elimination**（v8.11.5 由来）：PART A 内 strong 太字ネタバレ排除
- **ox-grid-fa-unification**（v8.11.5 由来）：ox-grid FA を single 形式に統一
- **host-injection-safe**（v8.11.6-hotfix1 由来）：`<script>` 内 `</body>` リテラル禁止（Lexia 等 host アプリ保護）

**番号衝突の合理的再採番：**

v8.11.1 で導入した「canonical text leakage」AP-30 ／ S68〜S72 を、原始 v8.11.x チェーンの AP-30〜AP-41 ／ S68〜S77 と衝突しないよう **AP-42 ／ S78〜S82** に renumber。実質的な意味・運用は不変。

継承事項：

- **KTX301 を byte-level canonical** として保持
- §24 readability layer の canonical 規範化
- chat-002 4 失敗症例の AP-26〜AP-29／S64〜S67
- **§Annex A/B/C 完全埋込**による自己完結性
- v8.11.1 由来の **§1-bis 日本語接頭辞 + TX 命名規則** ＋ **§0-quad コンテンツ独立性プロトコル**

### 36-2. 再発防止の構造的アプローチ

| 教訓 | v8.11.7 対策 |
|---|---|
| 負 text-indent + overflow:hidden 不整合 | AP-26 / S67 / §0-tri STEP 1 明示破棄 / §24-6 Grid canonical |
| `<p>` 直当て flex/grid + 混在 inline 子 | AP-27 / S67 / §0-tri STEP 1 明示破棄 / `<span class="hang-body">` wrap canonical |
| `.ron-mark` display 改変 | AP-28 / S67 / §0-tri STEP 1 明示破棄 / §15-bis `.ron-mark{display:inline}` lock |
| 過度装飾 | AP-29 / §31-6 設計指針「最小介入→段階的拡張」 |
| **final-answer hidden 属性欠落（スポイラー）** | **AP-30 / S68 / §22-quater HTML 要件** |
| **§22-quater CSS パッチ欠落** | **AP-31 / S69 / §22-quater-3 8 規則必須** |
| **fa-summary 内「正解はN」リテラル** | **AP-32 / S70 / §22-quater-2 禁止** |
| **answer-instruction の自由文化** | **AP-33 / S71 / §17-5 canonical 文言固定** |
| **reveal-answer-btn 欠落** | **AP-34 / S72 / §17-2 必須要素** |
| **data-answer-type 不整合** | **AP-35 / S73 / §17-2 Type 自動判定** |
| **PART A 内「N（XX）正解」リテラル** | **AP-36 / S74 / §17 spoiler-leak-eradication** |
| **data-explanation 先頭リテラル** | **AP-37 / S75 / §17 同上** |
| **FA に不正解の数字混入** | **AP-38 / S75 / §22-ter 正解のみ表示** |
| **PART A 内 strong 太字ネタバレ** | **AP-39 / S76 / spoiler-strong-elimination** |
| **ox-grid FA の multi 構造化** | **AP-40 / S76 / §22-ter single 統一** |
| **`<script>` 内 `</body>` リテラル** | **AP-41 / S77 / host-injection-safe** |
| **canonical text leakage（KTX301 本文流用）** | **AP-42 / S78 / S79 / §0-quad 7 ステップ独立性プロトコル** |
| **命名規則不整合（レガシー混在）** | **S80 / S81 / S82 / §1-bis 命名規則 + 出力先サブフォルダ + 番号抽出ルール** |

### 36-3. 系譜

| バージョン | 新規規律 |
|---|---|
| v7.3〜v8.9 | （既存・省略） |
| v8.10.0 | §Annex A/B/C に KTX296.html 実バイト逐語埋込／§0-tri ゼロベース再構築プロトコル |
| v8.10.1 | `a.rb-chip` カラートークン化パッチ |
| v8.10.2 | A-2 feedback クラッシュ再発防止・6 層防御 |
| v8.11.0 | canonical 移行（KTX296 → KTX301）／§24 readability layer canonical 化／A-3 PART B 後再配置／font-weight 強化／§24-6 ハンギングインデント Grid + HTML wrap canonical／chat-002 4 失敗症例 AP-26〜AP-29 化／S64〜S67 追加／§Annex A/B/C を本仕様書 1 枚に完全埋込（自己完結化） |
| v8.11.1（本クリーン版基盤） | §1-bis 日本語接頭辞 + TX 命名規則の正式化／§0-quad コンテンツ独立性プロトコル 7 ステップ／footer-spec に jp-prefix-naming・content-independence tag 追加 |
| v8.11.2（原始版・本仕様書に統合） | a2-two-stage-reveal（reveal-answer-btn 必須／answer-instruction canonical 文言固定）／AP-33・AP-34 |
| v8.11.3（原始版・本仕様書に統合） | 3 Type 対応（single / multi / ox-grid・data-answer-type 属性）／selection-counter UI／§22-sexta CSS パッチ／AP-35 |
| v8.11.4（原始版・本仕様書に統合） | spoiler-leak-eradication（PART A「N（XX）正解」消去・data-explanation 先頭リテラル消去・FA 正解のみ表示）／AP-36・AP-37・AP-38 |
| v8.11.5（原始版・本仕様書に統合） | spoiler-strong-elimination（PART A 内 strong タグ削除）／ox-grid-fa-unification（FA を single 形式統一）／AP-39・AP-40 |
| v8.11.6-hotfix1（原始版・本仕様書に統合） | host-injection-safe（`<script>` 内 `</body>` リテラル禁止）／AP-41 |
| **v8.11.7** | **v8.11.2〜v8.11.6-hotfix1 の 7 機能を本クリーン版（v8.11.1 ベース）に統合／AP-30〜AP-41 を採用／S68〜S77 を採用／旧 AP-30（canonical text leakage）を AP-42 に renumber／旧 S68〜S72 を S78〜S82 に renumber／footer-spec に統合 feature-tag 8 件追加** |

### 36-4. 運用上の core invariant（v8.11.7）

```
新規 TX ファイルと §Annex B(v8.11.7) 骨格を diff したとき:
  ━ 構造シェル（タグ・class・id・属性キー）は byte-level 一致
  ━ 本文テキスト（タグ内の自然言語）は byte-level 不一致
    （ただし不変ラベル：marker-legend 凡例 / PART タイトル /
       sec-nav 航行ラベル / sec-icon は一致）

加えて以下が成立:
  ━ v8.11.0 既存条件 ━
  - <section id="basis"> が PART B の後ろ・PART C の前にある (§2, S66)
  - §24 readability layer 全 6 サブセクションが <style> 内に存在 (S64)
  - .basis-card-body > p.hanging 形式遵守 (S65)
  - .basis-card-body の font-weight が 600 (S67)
  - .ron-mark に display:inline-block なし (S67/AP-28)
  - .basis-card-body > p に display:flex/grid 直当てなし (S67/AP-27)
  - 旧 padding-left + 負 text-indent ハンギングなし (S67/AP-26)
  - #answer-feedback strong{color:#fff !important} が 0 件 (S62)

  ━ v8.11.7 統合条件（spoiler-safe / 2-stage / 3-type / host-injection-safe）━
  - すべての <div class="final-answer"> に hidden 属性 (S68/AP-30)
  - §22-quater-3 CSS パッチ 8 規則完備 (S69/AP-31)
  - <p class="fa-summary"> 内に「正解はN」リテラル不存在 (S70/AP-32)
  - <p class="answer-instruction"> 内容が canonical 文言固定 (S71/AP-33)
  - <button class="reveal-answer-btn"> 存在 (S72/AP-34)
  - data-answer-type と data-correct-value 形式が整合 (S73/AP-35)
  - PART A 内に「N（XX）正解」リテラル不存在 (S74/AP-36)
  - data-explanation 先頭に正解値リテラル不存在 (S75/AP-37)
  - FA .answer-num に不正解の数字混入なし (S75/AP-38)
  - PART A 内に <strong>N（XX）</strong> 不存在 (S76/AP-39)
  - ox-grid 型 FA が <span class="answer-num"> 形式 (S76/AP-40)
  - <script>...</script> 内に </body> リテラル不存在 (S77/AP-41)

  ━ v8.11.1 由来条件（content-independence + jp-prefix-naming）━
  - §0-quad-2 禁止文言ブラックリスト 0 件ヒット (S78/AP-42)
  - §Annex B 元テキストとの 3 単語以上連続一致なし (S79)
  - <title> / .doc-header / footer-spec のファイル ID が
    「{日本語接頭辞}TX{3桁0埋め数字}」形式で完全一致 (S80)
  - 出力先サブフォルダが §1-bis-3 対応表に従う (S81)
  - PDF ファイル名の最初の連続数字 = 出力 ID 数字 (S82)
```

これを満たさないファイルは AP-X / K302-X として regeneration の対象。

---

# §Annex 群 ─ KTX301 model 実バイト逐語埋込

> **本仕様書 v8.11.7 の §Annex 群運用方針**：KTX301 を byte-level 正典とし、以下の §Annex B-link／A／B／C をすべて **本仕様書内に直接埋込**。過去の v8.x 仕様書への参照を一切要しない。
>
> **本 Annex 群を編集してはならない**。コンテンツ差替えは §0-tri STEP 3 ＋ §0-quad 7 ステップ独立性プロトコルで行う。色変更は §Annex A-bis-2／§Annex A-bis-3 を `:root{}` 単一ブロックで追記する形式のみ許容。
>
> **重要（v8.11.7）：** §Annex B body skeleton 内に逐語埋込されている KTX301 の **問題固有テキスト**（詐欺罪論点・特定判例文言・選択肢原文）は、**構造例示のためのプレースホルダ**であって、新規生成ファイルへの流用対象ではない。§0-quad-4 の表を厳守し、「タグ・class は逐語コピー、タグ内本文は完全新規執筆」を徹底すること。
>
> **追加注意（v8.11.7）：** §Annex C 内の先頭コメントから `</body>` リテラル文字列は除去済み（AP-41 対策・hotfix1）。生成時もコメント・文字列・テンプレートリテラル等のあらゆる箇所で `</body>` リテラルを混入させないこと。

---

## §Annex B-link. Google Fonts `<link>` タグ

`<head>` 内（`<title>` 直後）に逐語コピー：

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@400;500;700;800&family=Shippori+Antique&family=Zen+Old+Mincho:wght@400;500;700;900&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Zen+Maru+Gothic:wght@400;500;700&family=Noto+Serif+JP:wght@400;500;700&family=Noto+Sans+JP:wght@400;500;700&family=Kaisei+Decol:wght@400;500;700&family=Kosugi+Maru&family=Source+Code+Pro:wght@400;600;700&family=M+PLUS+Rounded+1c:wght@500;700;800&family=M+PLUS+1p:wght@500;700;800;900&display=swap" rel="stylesheet">
```

---

## §Annex A. Canonical CSS（GENKEI byte-lock — フォント/デザイン物理根拠）

`<style>` ブロック内部に逐語コピー。以下が **v8.11.0 canonical CSS 全文**（§17 fb-verdict/fb-answer canonical 7 規則／§24 readability layer 6 サブセクション／A-2 / A-3 関連規則・font-weight 改訂を**すべて含む**）：

```css
/* ============================================================
   TX v8.11.6 - canonical CSS (Annex A)
   KTX301 byte-level canonical / 司法試験R1-16 詐欺罪と他罪の成否
   既定値は P1 ローズシャンブル
   ============================================================ */

/* === §3 12役割フォント === */
:root{
  --font-body:    "A1 Gothic","A-OTF A1ゴシック Std","Zen Kaku Gothic Antique","Hiragino Sans","Yu Gothic Medium","Noto Sans JP",sans-serif;
  --font-soft:    "Zen Maru Gothic","Hiragino Maru Gothic ProN","Yu Gothic Medium",sans-serif;
  --font-display: "Shippori Mincho B1","Yu Mincho","Hiragino Mincho ProN","Noto Serif JP",serif;
  --font-statute: "Noto Serif JP","Yu Mincho","Hiragino Mincho ProN",serif;
  --font-quote:   "Yu Mincho","游明朝","Hiragino Mincho ProN","Noto Serif JP",serif;
  --font-answer:  "Shippori Antique","Yu Mincho","Hiragino Mincho ProN","Noto Serif JP",serif;
  --font-keyword: "Kaisei Decol","M PLUS Rounded 1c","Yu Mincho",serif;
  --font-judgment:"Zen Old Mincho","Yu Mincho","Hiragino Mincho ProN","Noto Serif JP",serif;
  --font-note:    "Zen Kaku Gothic Antique","Yu Gothic","Hiragino Sans",sans-serif;
  --font-professor:"Kosugi Maru","Hiragino Maru Gothic ProN","Yu Gothic",sans-serif;
  --font-mono:    "Source Code Pro","Consolas","Menlo",monospace;
  --font-impact:  "M PLUS 1p","Hiragino Sans","Yu Gothic","Noto Sans JP",sans-serif;

  /* === 見出しスケール === */
  --fs-base:1.0rem; --fs-sm:0.88rem;
  --fs-h5:1.0rem; --fs-h4:1.10rem; --fs-h3:1.35rem; --fs-h2:1.65rem; --fs-h1:1.85rem;
  --fs-h-sub:1.10rem; --fs-h-mid:1.35rem; --fs-h-top:1.85rem;
}

/* === §5 P1 ローズシャンブル 完全パレット === */
:root{
  --accent:        #8a1f3a;
  --accent-rgb:    138,31,58;
  --mid:           #dc4d71;
  --mid-rgb:       220,77,113;

  --light:         #fce4e8;
  --base:          #fbf3ed;
  --soft:          #f3e6da;
  --paper:         #FFFFFF;
  --text:          #231419;
  --bg-dark:       #5a1a30;
  --accent-3:      #fff8f0;
  --accent-soft:   #fdf0f3;
  --border-mid:    #e8c8d2;
  --kp-text-color: #1a0a10;

  --hl-super:#ffd54f; --hl-high:#aed581; --hl-std:#90caf9;
  --tan-super:#c62828; --tan-high:#ef6c00; --tan-std:#1565c0;
  --rank-A:#c62828;   --rank-B:#e65100;   --rank-C:#1565c0; --rank-D:#333333;

  --freq-high:        #b00032;
  --freq-high-rgb:    176,0,50;
  --freq-high-deep:   #7e0024;
  --freq-mid:         #a07030;
  --freq-mid-rgb:     160,112,48;
  --freq-mid-deep:    #7c5520;
  --freq-low:         #884d6b;
  --freq-low-rgb:     136,77,107;
  --freq-low-deep:    #5e3550;

  --recall-correct:        #1b5e20;
  --recall-correct-light:  #2e7d32;
  --recall-incorrect:      #b00032;
  --recall-incorrect-light:#c62828;
}

/* === §4 body === */
*{ box-sizing:border-box; }
html{ scroll-behavior:smooth; scroll-padding-top:20px; -webkit-text-size-adjust:100%; }
body{
  font-family:var(--font-body); font-weight:500; line-height:2.0;
  font-size:16px; letter-spacing:.04em;
  font-feature-settings:"palt" 1;
  -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale;
  text-rendering:optimizeLegibility;
  background:var(--base); color:var(--text);
  margin:0; padding:0; position:relative;
}
::selection{ background:rgba(var(--mid-rgb),.22); color:var(--bg-dark); }

h1{ font-family:var(--font-display); font-weight:700; letter-spacing:.06em; line-height:1.4; }
h2{ font-family:var(--font-display); font-weight:700; letter-spacing:.06em; line-height:1.4; }
h3{ font-family:var(--font-soft);    font-weight:700; letter-spacing:.04em; line-height:1.5; }
h4{ font-family:var(--font-soft);    font-weight:700; letter-spacing:.03em; }
h5{ font-family:var(--font-soft);    font-weight:700; letter-spacing:.03em; }
p{ margin:0 0 1em; }
ul,ol{ margin:0 0 1em; padding-left:1.6em; }
li{ margin-bottom:.35em; }
li::marker{ color:var(--mid); }
strong{ font-weight:700; }
code{ font-family:var(--font-mono); font-size:.92em; }
hr{ border:none; height:1px;
  background:linear-gradient(90deg,transparent,rgba(var(--accent-rgb),.20) 15%,var(--mid) 50%,rgba(var(--accent-rgb),.20) 85%,transparent);
  margin:28px 0;
}
a{ color:var(--accent); text-decoration:none; border-bottom:1px dotted rgba(var(--accent-rgb),.4); transition:.2s; }
a:hover{ color:var(--mid); border-bottom-color:var(--mid); }

/* === §4 container === */
.container{
  max-width:1080px; margin:0 auto;
  padding:0 20px 32px 20px;
  background:transparent;
}
@media (min-width:769px){
  .container{ padding:0 40px 48px 40px; }
}
.container > section{
  background:var(--paper); border-radius:14px;
  padding:32px 36px; margin:24px 0;
  box-shadow:0 4px 14px rgba(var(--accent-rgb),.10);
  border:none;
}
section section{
  background:transparent; padding:0;
  margin:24px 0 0 0; box-shadow:none; border-radius:0;
}

/* === §6 doc-header === */
.doc-header,
.header > .doc-header{
  position:absolute; top:14px; right:18px; z-index:100;
  display:inline-block;
  background:linear-gradient(135deg,var(--accent) 0%,var(--mid) 100%);
  color:#fff; padding:6px 14px; border-radius:8px;
  font-family:var(--font-mono);
  font-weight:600; font-size:16px; letter-spacing:.10em;
  border:1.5px solid rgba(255,255,255,.65);
  box-shadow:0 2px 6px rgba(0,0,0,.20);
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}

/* === §7 cover / header === */
.header{
  background:linear-gradient(135deg,var(--accent) 0%,var(--mid) 100%);
  color:#fff;
  padding:60px 32px 36px 32px;
  border-radius:0 0 20px 20px;
  margin:0 0 24px 0;
  position:relative; overflow:hidden;
}
.header::before{
  content:''; position:absolute; inset:0; pointer-events:none;
  background:
    radial-gradient(ellipse at top right, rgba(255,255,255,.10) 0%, transparent 60%),
    radial-gradient(ellipse at bottom left, rgba(0,0,0,.08) 0%, transparent 60%);
}
.header > *{ position:relative; z-index:1; }
.header h1{
  margin:14px 0 14px 0;
  font-family:var(--font-display);
  font-size:1.9em; font-weight:700; letter-spacing:.06em;
  color:#fff; line-height:1.4;
  text-shadow:0 2px 4px rgba(0,0,0,.20);
}
.header-top{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:6px; align-items:center; }
.exam-badge{
  display:inline-block;
  background:rgba(255,255,255,.18);
  border:1px solid rgba(255,255,255,.42);
  border-radius:999px; padding:4px 14px;
  font-family:var(--font-soft);
  font-size:.78em; font-weight:700; letter-spacing:.10em;
  color:#fff;
}
.theme-tags{ display:flex; flex-wrap:wrap; gap:8px; margin:14px 0 12px 0; }
.theme-tag{
  display:inline-block;
  background:rgba(255,255,255,.14);
  border:1px solid rgba(255,255,255,.40);
  border-radius:6px; padding:4px 12px;
  font-family:var(--font-soft);
  font-size:.86em; font-weight:500;
  color:#fff; letter-spacing:.04em;
}
.exam-meta{
  margin-top:10px;
  font-family:var(--font-mono);
  font-size:.92em;
  color:rgba(255,255,255,.92);
  letter-spacing:.04em;
}
.exam-meta strong{ color:#fff; font-weight:600; margin-right:4px; }
.exam-meta span{ margin-right:18px; }
.toc-row{ margin-top:14px; font-family:var(--font-mono); font-size:.84em; }
.toc-row a{
  color:rgba(255,255,255,.92);
  margin-right:14px;
  border-bottom:1px dotted rgba(255,255,255,.5);
  text-decoration:none; padding:1px 2px;
  transition:.2s;
}
.toc-row a:hover{ color:#fff; border-bottom-color:#fff; background:rgba(255,255,255,.10); }

/* === §8 part-title === */
.part-title{
  font-family:var(--font-display); font-weight:800;
  font-size:1.4em; color:var(--accent);
  letter-spacing:.14em; text-align:center;
  margin:48px 0 22px;
  padding:14px 0 16px;
  position:relative;
  background:linear-gradient(180deg,transparent 0%,rgba(var(--mid-rgb),.04) 50%,transparent 100%);
}
.part-title::before,
.part-title::after{
  content:''; position:absolute; left:50%; transform:translateX(-50%);
  width:80%; max-width:520px; height:2px;
  background:linear-gradient(90deg,transparent,var(--mid) 30%,var(--accent) 50%,var(--mid) 70%,transparent);
  opacity:.7;
}
.part-title::before{ top:0; }
.part-title::after{ bottom:0; }

/* === §9 section-title / sec-nav / back-to-top === */
.section-title{
  color:var(--accent); font-size:1.6em; font-weight:700;
  font-family:var(--font-display);
  margin:0 0 18px 0;
  padding:10px 16px;
  background:var(--soft);
  border-left:8px solid var(--accent);
  border-radius:4px;
  line-height:1.4;
  display:flex; align-items:center; gap:10px;
}
.sec-icon{ color:var(--mid); font-size:.9em; }
.sec-nav{
  font-family:var(--font-mono); font-size:.82em;
  margin:0 0 12px 0;
  display:flex; gap:14px; flex-wrap:wrap;
  color:var(--text); opacity:.8;
}
.sec-nav a{
  color:var(--text);
  border-bottom:1px dotted rgba(var(--accent-rgb),.3);
  text-decoration:none; padding:1px 2px;
  transition:.2s;
}
.sec-nav a:hover{ color:var(--accent); border-bottom-color:var(--accent); background:var(--light); }
.back-to-top{
  margin-top:18px; text-align:right;
  font-family:var(--font-mono); font-size:.85em;
}
.back-to-top a{
  display:inline-block; padding:8px 18px;
  background:var(--accent); color:#fff;
  border-radius:999px;
  font-family:var(--font-soft);
  text-decoration:none; font-weight:700;
  letter-spacing:.05em;
  box-shadow:0 2px 4px rgba(0,0,0,.15);
  transition:.2s;
  margin-left:6px;
  border-bottom:none;
}
.back-to-top a:hover{ background:var(--mid); }

/* === §10 h3/h4/h5 === */
.container > section > h3,
.container > section > section > h3,
.recall-arena > h3{
  color:var(--accent); font-size:1.25em; font-weight:700;
  font-family:var(--font-soft);
  margin:26px 0 14px 0;
  padding:7px 14px;
  background:var(--accent-soft);
  border-left:5px solid var(--mid);
  border-radius:0 4px 4px 0;
}
.container > section h4{
  color:var(--mid); font-size:1.08em; font-weight:700;
  font-family:var(--font-soft);
  margin:18px 0 10px 0;
  padding-bottom:4px;
  border-bottom:1.5px dashed var(--mid);
}
.container > section h5{
  color:var(--accent); font-size:1em; font-weight:700;
  font-family:var(--font-soft);
  margin:14px 0 8px 0;
}
section[id^="c-"] > h3{
  background:transparent; border-left:none;
  padding:0 0 14px 0;
  margin:26px 0 18px 0;
  border-bottom:3px dotted var(--accent);
  border-radius:0;
}

/* === §11 key-phrase-box【v8.4 canonical】=== */
.key-phrase-box,
.section .key-phrase-box,
.container .key-phrase-box{
  position:relative;
  background:linear-gradient(135deg,#fff8f0 0%,var(--light) 60%,var(--soft) 100%);
  border:2px solid var(--accent);
  border-radius:10px;
  padding:52px 44px 34px 44px;
  margin:30px 0 24px;
  font-family:var(--font-impact);
  font-size:.98rem;
  font-weight:900;
  line-height:1.95;
  letter-spacing:.025em;
  color:var(--kp-text-color);
  box-shadow:
    0 6px 18px rgba(var(--accent-rgb),.16),
    0 2px 6px rgba(0,0,0,.08),
    inset 0 0 0 1px rgba(255,255,255,.65),
    inset 0 0 0 4px rgba(var(--accent-rgb),.05);
  -webkit-text-stroke:.01em transparent;
  text-rendering:optimizeLegibility;
}
.key-phrase-box p{
  font-family:inherit;
  font-weight:inherit;
  margin:0 0 .8em;
}
.key-phrase-box p:last-child{ margin-bottom:0; }
.key-phrase-box strong{
  font-family:inherit;
  font-weight:900;
  color:var(--bg-dark);
}
.key-phrase-box::before{
  content:'🔑 KEY';
  position:absolute;
  top:-15px; left:22px;
  background:linear-gradient(135deg,var(--accent) 0%,var(--mid) 100%);
  color:#fff;
  padding:6px 18px 5px;
  border-radius:5px;
  font-family:var(--font-impact),"Source Code Pro",monospace;
  font-size:.82rem;
  font-weight:900;
  letter-spacing:.16em;
  box-shadow:
    0 3px 8px rgba(var(--accent-rgb),.32),
    0 1px 2px rgba(0,0,0,.18);
  white-space:nowrap;
}
.key-phrase-box::after{
  content:''; position:absolute;
  top:0; right:0;
  width:72px; height:72px;
  background:radial-gradient(circle at top right, rgba(var(--accent-rgb),.10), transparent 72%);
  border-radius:0 10px 0 72px;
  pointer-events:none;
}
.key-phrase-box .kp-strong{
  display:inline-block;
  font-family:var(--font-impact);
  font-weight:900;
  color:var(--accent);
  font-size:1.06rem;
  letter-spacing:.04em;
  background:linear-gradient(
    transparent 58%,
    rgba(var(--mid-rgb),.32) 58%,
    rgba(var(--mid-rgb),.32) 92%,
    transparent 92%
  );
  padding:0 4px;
  margin-right:2px;
}
.key-phrase-box .ron-mark,
.key-phrase-box .ron-mark.freq-high,
.key-phrase-box .ron-mark.freq-mid,
.key-phrase-box .ron-mark.freq-low{
  font-family:inherit;
  font-weight:900;
}

/* === §12 callouts === */
.warning, .cross-link, .prof-analogy, .self-check-quiz{
  position:relative;
  margin:18px 0;
  border-radius:8px;
  font-family:var(--font-note); font-weight:500;
  line-height:1.95; letter-spacing:.03em;
  box-shadow:
    0 2px 6px rgba(0,0,0,.06),
    inset 0 0 0 1px rgba(255,255,255,.6);
}
.warning{
  background:#fff7e0;
  border:1px solid rgba(239,108,0,.32);
  padding:18px 32px 16px 32px;
}
.warning::before{
  content:'⚠ WARN'; display:inline-block;
  background:linear-gradient(135deg,#bf360c,#ef6c00);
  color:#fff; padding:3px 10px 2px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.72rem; font-weight:700; letter-spacing:.14em;
  margin:0 8px 10px 0;
  vertical-align:2px;
  box-shadow:0 1px 2px rgba(0,0,0,.18);
}
.warning p{ margin:0 0 .6em; }
.warning p:last-child{ margin-bottom:0; }
.cross-link{
  background:#e7f1ff;
  border:1px solid rgba(21,101,192,.30);
  padding:18px 32px 16px 32px;
}
.cross-link::before{
  content:'⇄ CROSS-LINK'; display:inline-block;
  background:linear-gradient(135deg,#0d47a1,#1565c0);
  color:#fff; padding:3px 10px 2px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.72rem; font-weight:700; letter-spacing:.14em;
  margin:0 8px 10px 0;
  vertical-align:2px;
  box-shadow:0 1px 2px rgba(0,0,0,.18);
}
.cross-link p{ margin:0 0 .6em; }
.cross-link p:last-child{ margin-bottom:0; }
.prof-analogy{
  background:linear-gradient(180deg,#fff8e8 0%,#fff5dc 100%);
  border:1px solid rgba(217,144,0,.35);
  padding:30px 36px 24px 36px;
}
.prof-analogy::before{
  content:'💡 ANALOGY';
  position:absolute; top:-12px; left:22px;
  background:linear-gradient(135deg,#a06a00,#d99000);
  color:#fff; padding:4px 14px 3px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.74rem; font-weight:700; letter-spacing:.16em;
  box-shadow:0 2px 5px rgba(0,0,0,.18);
}
.prof-analogy .scene-title{
  display:block;
  font-family:var(--font-display); font-weight:700;
  font-size:1.04em; color:#7c5520;
  margin-bottom:12px;
  padding-bottom:6px;
  border-bottom:1.5px dashed rgba(217,144,0,.5);
  letter-spacing:.04em;
}
.prof-analogy p{ margin:0 0 .8em; }
.prof-analogy p:last-child{ margin-bottom:0; }
.self-check-quiz{
  background:linear-gradient(180deg,#f7f1f3 0%,var(--paper) 100%);
  border:1.5px solid var(--mid);
  padding:18px 28px;
  margin:14px 0;
}
.self-check-quiz::before{
  content:'❓ QUIZ'; display:inline-block;
  background:linear-gradient(135deg,var(--accent),var(--mid));
  color:#fff; padding:3px 10px 2px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.72rem; font-weight:700; letter-spacing:.14em;
  margin:0 8px 10px 0;
  vertical-align:2px;
  box-shadow:0 1px 2px rgba(0,0,0,.18);
}

/* === §13 sub-card 4種 === */
.sub-card{
  position:relative;
  background:var(--paper);
  border:1px solid var(--border-mid);
  border-radius:10px;
  padding:30px 26px 22px;
  margin:18px 0;
  page-break-inside:avoid;
}
.sub-card::before{
  position:absolute; top:-12px; left:24px;
  color:#fff; padding:4px 14px 3px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.72rem; font-weight:600; letter-spacing:.18em;
  box-shadow:0 2px 5px rgba(0,0,0,.18);
  white-space:nowrap;
}
.sub-card.original{
  background:linear-gradient(180deg,var(--accent-soft) 0%,#fff 100%);
  border:1.5px solid var(--mid);
}
.sub-card.original::before{
  content:'ORIGINAL';
  background:linear-gradient(135deg,var(--accent),var(--mid));
}
.sub-card.original .label{ display:none; }
.sub-card.explanation{
  background:#fdfaf6;
  border:1px solid rgba(160,112,48,.30);
}
.sub-card.explanation::before{
  content:'📖 EXPLANATION';
  background:linear-gradient(135deg,#7c5520,#a07030);
}
.sub-card.explanation > h4{ display:none; }
.sub-card.explanation .label{ display:none; }
.sub-card.basis-link{
  background:var(--light);
  border:1px solid var(--border-mid);
  border-left:4px solid var(--accent);
  padding-top:24px;
}
.sub-card.basis-link::before{
  content:'📚 BASIS';
  background:linear-gradient(135deg,var(--accent),var(--mid));
  top:-12px; left:18px;
}
.sub-card.basis-link > h4{ display:none; }
.sub-card.basis-link .label{ display:none; }
.sub-card.basis-link .back-link-row{
  margin-top:0; background:transparent; padding:0;
  border-left:none;
}
.sub-card.basis-link .back-link-row::before{ content:''; }
.sub-card.professor{
  background:linear-gradient(180deg,#f7faf6 0%,var(--paper) 100%);
  border:1px solid rgba(46,125,50,.32);
  padding:32px 28px 24px;
  font-family:var(--font-professor);
  line-height:2.0;
}
.sub-card.professor::before{
  content:'👨‍🏫 PROFESSOR';
  background:linear-gradient(135deg,#1b5e20,#2e7d32);
}
.sub-card.professor > h4{ display:none; }
.sub-card.professor .label{ display:none; }
.sub-card.professor > p,
.sub-card.professor > ul{
  font-family:var(--font-professor);
  letter-spacing:.03em;
}
.sub-card.professor > ul{ padding-left:1.6em; }
.sub-card.professor > ul li{ margin-bottom:.4em; }
.prof-heading{
  display:flex; align-items:center; gap:10px;
  margin:22px 0 10px 0;
  font-family:var(--font-display);
  font-weight:700; font-size:1.08em;
  color:#1b5e20; letter-spacing:.04em;
  border-bottom:1.5px dashed rgba(46,125,50,.40);
  padding-bottom:6px;
}
.prof-num{
  display:inline-flex; align-items:center; justify-content:center;
  width:26px; height:26px;
  background:linear-gradient(135deg,#1b5e20,#2e7d32);
  color:#fff; border-radius:50%;
  font-family:var(--font-mono);
  font-weight:700; font-size:.86em;
  box-shadow:0 1px 3px rgba(0,0,0,.18);
  flex-shrink:0;
}

/* === §14 basis-card === */
.basis-card{
  background:#fff;
  border:1px solid var(--border-mid);
  border-radius:10px;
  padding:0; margin:18px 0;
  page-break-inside:avoid;
  overflow:hidden;
}
.basis-card.statute-card{ border-left:5px solid #6b7280; }
.basis-card.case-card{ border-left:5px solid var(--mid); }
.basis-card-header{
  background:#f3f4f6;
  padding:12px 22px;
  font-family:var(--font-display);
  font-weight:700; font-size:1.08em;
  color:var(--accent);
  border-bottom:1.5px solid var(--border-mid);
  letter-spacing:.04em;
}
.basis-card.case-card .basis-card-header{
  background:#ffeef1; color:var(--accent);
}
.basis-card-body{
  padding:18px 22px 16px;
  font-family:var(--font-quote);
  font-weight:600; line-height:1.95;
}
.basis-card-body p{ margin:0 0 .8em; }
.basis-card-body p:last-child{ margin-bottom:0; }
.basis-card-body .note{
  position:relative;
  background:#e7f1ff;
  border:1px solid rgba(21,101,192,.30);
  border-radius:8px;
  padding:18px 32px 14px;
  margin:14px 0 12px;
  font-family:var(--font-note); font-weight:500;
  line-height:1.95; letter-spacing:.03em;
  box-shadow:
    0 2px 6px rgba(0,0,0,.06),
    inset 0 0 0 1px rgba(255,255,255,.6);
}
.basis-card-body .note::before{
  content:'ℹ NOTE'; display:inline-block;
  background:linear-gradient(135deg,#0d47a1,#1565c0);
  color:#fff; padding:3px 10px 2px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.72rem; font-weight:700; letter-spacing:.14em;
  margin:0 8px 10px 0;
  vertical-align:2px;
  box-shadow:0 1px 2px rgba(0,0,0,.18);
}
.para-num{
  display:inline-block;
  background:var(--accent-3); color:var(--accent);
  padding:2px 10px; border-radius:3px;
  font-family:var(--font-statute);
  font-weight:700; font-size:.96em;
  margin-right:8px;
  border:1px solid var(--border-mid);
  letter-spacing:.04em;
}

/* === §15 強調マーカー === */
.exam-mark{
  background:linear-gradient(transparent 60%,currentColor 60%);
  background-size:100% 100%;
  background-repeat:no-repeat;
  padding:0 4px 1px;
  font-weight:700; letter-spacing:.09em;
  margin:0 1px;
  -webkit-font-smoothing:antialiased;
}
.exam-mark.freq-high{
  background:linear-gradient(transparent 55%,rgba(var(--freq-high-rgb),.42) 55%);
  color:var(--freq-high-deep);
}
.exam-mark.freq-mid{
  background:linear-gradient(transparent 55%,rgba(var(--freq-mid-rgb),.42) 55%);
  color:var(--freq-mid-deep);
}
.exam-mark.freq-low{
  background:linear-gradient(transparent 55%,rgba(var(--freq-low-rgb),.36) 55%);
  color:var(--freq-low-deep);
}
.hl-super{ background:linear-gradient(transparent 55%,rgba(255,213,79,.55) 55%); padding:0 4px 1px; font-weight:700; letter-spacing:.08em; }
.hl-high{  background:linear-gradient(transparent 60%,rgba(174,213,129,.55) 60%); padding:0 4px 1px; font-weight:700; letter-spacing:.08em; }
.hl-std{   background:linear-gradient(transparent 70%,rgba(144,202,249,.50) 70%); padding:0 4px 1px; font-weight:500; letter-spacing:.06em; }
.statute-emphasis{
  font-family:var(--font-statute);
  font-weight:700; padding:0 3px;
  letter-spacing:.06em;
}
.statute-emphasis.freq-high{ color:var(--freq-high-deep); }
.statute-emphasis.freq-mid { color:var(--freq-mid-deep); }
.statute-emphasis.freq-low { color:var(--freq-low-deep); }
.case-emphasis{
  font-family:var(--font-statute);
  font-weight:700; font-style:italic;
  padding:0 3px; letter-spacing:.06em;
}
.case-emphasis.freq-high{ color:var(--freq-high-deep); }
.case-emphasis.freq-mid { color:var(--freq-mid-deep); }
.case-emphasis.freq-low { color:var(--freq-low-deep); }
.judgment-text{
  font-family:var(--font-judgment);
  font-weight:700; letter-spacing:.03em;
  line-height:1.95;
}

/* === §15-bis ron-mark === */
.ron-mark{
  font-family:var(--font-statute);
  font-weight:700; letter-spacing:.04em;
  padding:0 4px 1px;
  background:linear-gradient(transparent 60%,rgba(var(--mid-rgb),.30) 60%);
  color:var(--accent);
  border-bottom:1.5px solid var(--mid);
}
.ron-mark::before{
  content:'論'; display:inline-block;
  background:linear-gradient(135deg,var(--accent) 0%,var(--mid) 100%);
  color:#fff;
  font-family:var(--font-display);
  font-size:.70em; font-weight:800;
  line-height:1;
  padding:2px 5px 1px;
  border-radius:3px;
  margin-right:5px;
  vertical-align:2px;
  letter-spacing:0;
  box-shadow:0 1px 2px rgba(var(--accent-rgb),.25), inset 0 1px 0 rgba(255,255,255,.20);
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
.ron-mark.freq-high{
  background:linear-gradient(transparent 55%,rgba(var(--freq-high-rgb),.40) 55%);
  color:var(--freq-high-deep);
  border-bottom-color:var(--freq-high);
}
.ron-mark.freq-high::before{
  background:linear-gradient(135deg,var(--freq-high-deep) 0%,var(--freq-high) 100%);
  box-shadow:0 1px 2px rgba(var(--freq-high-rgb),.30), inset 0 1px 0 rgba(255,255,255,.20);
}
.ron-mark.freq-mid{
  background:linear-gradient(transparent 55%,rgba(var(--freq-mid-rgb),.36) 55%);
  color:var(--freq-mid-deep);
  border-bottom-color:var(--freq-mid);
}
.ron-mark.freq-mid::before{
  background:linear-gradient(135deg,var(--freq-mid-deep) 0%,var(--freq-mid) 100%);
  box-shadow:0 1px 2px rgba(var(--freq-mid-rgb),.30), inset 0 1px 0 rgba(255,255,255,.20);
}

/* === §16 marker-legend === */
.marker-legend{
  display:flex; flex-wrap:wrap;
  align-items:center; gap:4px 12px;
  padding:7px 14px 6px;
  margin:14px 0 -8px;
  background:linear-gradient(180deg,rgba(255,255,255,.65) 0%,rgba(255,255,255,.42) 100%);
  -webkit-backdrop-filter:blur(6px);
  backdrop-filter:blur(6px);
  border:1px solid var(--border-mid);
  border-radius:8px;
  font-family:var(--font-note);
  font-size:.80em; line-height:1.4;
  letter-spacing:.02em; color:var(--text);
  box-shadow:0 1px 4px rgba(var(--accent-rgb),.06);
}
.marker-legend .lg-title{
  font-family:var(--font-mono);
  font-size:.82em; letter-spacing:.16em;
  font-weight:700; color:var(--accent);
  text-transform:uppercase;
  padding-right:2px;
}
.marker-legend .lg-divider{
  color:var(--border-mid); opacity:.85;
  font-weight:300; margin:0 1px; user-select:none;
}
.marker-legend .lg-item{
  display:inline-flex; align-items:center;
  gap:4px; white-space:nowrap; opacity:.92;
}
.marker-legend .lg-sample.lg-ron{
  display:inline-block;
  background:linear-gradient(135deg,var(--accent) 0%,var(--mid) 100%);
  color:#fff;
  font-family:var(--font-display);
  font-size:.84em; font-weight:800;
  line-height:1; padding:2px 5px 1px;
  border-radius:3px; letter-spacing:0;
  box-shadow:0 1px 2px rgba(var(--accent-rgb),.25),inset 0 1px 0 rgba(255,255,255,.20);
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
@media (max-width:768px){
  .marker-legend{ font-size:.74em; padding:6px 10px 5px; gap:3px 8px; margin-bottom:-10px; }
  .marker-legend .lg-divider{ display:none; }
  .marker-legend .lg-title{ font-size:.78em; }
}

/* === §17 problem-text / answer-area / answer-feedback === */
.problem-text{
  position:relative;
  margin:14px 0;
  padding:14px 18px 14px 20px;
  background:var(--soft);
  border-left:5px solid var(--accent);
  border-radius:0 6px 6px 0;
  font-family:var(--font-quote);
  font-weight:400; line-height:1.95;
  letter-spacing:.02em;
}
.choice-num-inline{
  display:inline-block;
  width:24px; height:24px;
  background:var(--accent); color:#fff;
  border-radius:50%;
  font-family:var(--font-mono);
  font-weight:700; font-size:.86em;
  text-align:center; line-height:24px;
  margin-right:8px; vertical-align:1px;
}
.answer-area{
  background:linear-gradient(180deg,var(--accent-soft) 0%,var(--paper) 100%);
  border:2px dashed var(--mid);
  border-radius:10px;
  padding:24px 26px 20px;
  margin:14px 0;
}
.answer-area > h3{
  margin:0 0 8px 0; padding:0; background:transparent;
  border:none;
  font-family:var(--font-display);
  font-size:1.15em; color:var(--accent);
  letter-spacing:.04em;
}
.answer-instruction{
  font-family:var(--font-note);
  font-size:.94em; color:var(--text);
  opacity:.85; margin:0 0 14px;
}
.answer-row{
  display:flex; gap:12px; flex-wrap:wrap;
  margin:14px 0 4px;
}
.answer-slot{
  width:62px; height:62px;
  display:flex; align-items:center; justify-content:center;
  background:var(--paper);
  border:2px solid var(--mid);
  border-radius:10px;
  font-family:var(--font-display);
  font-weight:700; font-size:1.5em;
  color:var(--accent);
  cursor:pointer; transition:.2s;
  user-select:none;
  box-shadow:0 2px 6px rgba(var(--accent-rgb),.10);
}
.answer-slot:hover{
  background:var(--light);
  transform:translateY(-2px);
  box-shadow:0 4px 10px rgba(var(--accent-rgb),.18);
}
.answer-slot.selected-correct, .answer-slot.correct-mark{
  background:#d8eed6; border-color:#2e7d32; color:#1b5e20;
  box-shadow:0 0 0 3px rgba(46,125,50,.25), 0 4px 10px rgba(46,125,50,.20);
}
.answer-slot.selected-incorrect, .answer-slot.incorrect-mark{
  background:#ffeef0; border-color:#c62828; color:#8a1818;
  box-shadow:0 0 0 3px rgba(198,40,40,.25), 0 4px 10px rgba(198,40,40,.20);
}

/* === §17 fb-verdict / fb-answer canonical 7 規則 === */
#answer-feedback{
  margin-top:14px !important;
  padding:16px 22px !important;
  border-radius:8px !important;
  font-family:var(--font-note) !important;
  line-height:1.95;
  font-size:.98em;
  box-shadow:0 2px 10px rgba(var(--accent-rgb),.10);
  letter-spacing:.02em;
}
#answer-feedback .fb-verdict{
  font-family:var(--font-display);
  font-size:1.08em; letter-spacing:.06em;
  display:inline-block;
  padding:2px 12px 1px;
  border-radius:5px;
  color:#fff;
  margin-right:6px;
  text-shadow:0 1px 2px rgba(0,0,0,.30);
  box-shadow:0 2px 5px rgba(0,0,0,.18), inset 0 1px 0 rgba(255,255,255,.20);
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
#answer-feedback .fb-verdict.fb-correct{
  background:linear-gradient(135deg,var(--recall-correct),var(--recall-correct-light));
}
#answer-feedback .fb-verdict.fb-incorrect{
  background:linear-gradient(135deg,#7e0024,var(--recall-incorrect));
}
#answer-feedback .fb-answer{
  display:inline-block;
  font-family:var(--font-display);
  font-weight:800; font-size:1.18em;
  color:var(--recall-incorrect);
  background:transparent;
  padding:0 5px 1px;
  margin:0 2px;
  letter-spacing:.04em;
  border-bottom:2.5px solid var(--recall-incorrect);
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
#answer-feedback strong:not(.fb-verdict){
  font-weight:700;
  color:inherit;
}
#answer-feedback p{ text-indent:0; }

/* === §18 choice-section === */
.container > .choice-section{
  background:var(--paper);
  border-radius:14px;
  padding:32px 36px;
  margin:24px 0;
  box-shadow:0 4px 14px rgba(var(--accent-rgb),.10);
  border:none;
  position:relative; overflow:hidden;
}
.container > .choice-section::before{
  content:''; position:absolute;
  top:0; left:0; right:0; height:4px;
  background:linear-gradient(90deg,var(--accent) 0%,var(--mid) 50%,var(--accent) 100%);
  opacity:.85;
}
.choice-section.even::before{
  background:linear-gradient(90deg,var(--mid) 0%,var(--accent) 50%,var(--mid) 100%);
}
.choice-header-block{
  display:flex; flex-wrap:wrap; align-items:center; gap:14px;
  margin-bottom:20px;
  padding-bottom:14px;
  border-bottom:2px dotted var(--border-mid);
}
.choice-big-badge{
  display:inline-flex;
  align-items:center; justify-content:center;
  width:48px; height:48px;
  background:linear-gradient(135deg,var(--accent),var(--mid));
  color:#fff; border-radius:50%;
  font-family:var(--font-display);
  font-weight:800; font-size:1.5em;
  box-shadow:0 3px 8px rgba(var(--accent-rgb),.30);
  flex-shrink:0;
}
.verdict{
  display:inline-block;
  font-family:var(--font-soft);
  font-size:.86em; font-weight:700;
  padding:4px 12px; border-radius:4px;
  color:#fff; letter-spacing:.08em;
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
.verdict.verdict-correct  { background:#1b5e20; border:2px solid #103d11; }
.verdict.verdict-incorrect{ background:var(--tan-super); border:2px solid #8a1818; }
.choice-summary{
  flex:1 1 100%;
  font-family:var(--font-quote);
  font-style:italic; color:var(--text);
  line-height:1.85; margin:0;
  padding:0 6px; opacity:.9;
}

/* === §19 badges / back-link === */
.freq-badge, .priority-badge{
  display:inline-block;
  font-family:var(--font-soft);
  font-size:.78em; padding:2px 9px;
  border-radius:4px; color:#fff;
  font-weight:700; margin-right:4px;
  letter-spacing:.08em; vertical-align:1px;
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
.freq-badge.freq-high{ background:var(--freq-high); border:2px solid var(--freq-high-deep); }
.freq-badge.freq-mid { background:var(--freq-mid); }
.freq-badge.freq-low { background:var(--freq-low); }
.priority-badge{
  font-family:var(--font-mono);
  font-size:.74em; letter-spacing:.10em;
}
.priority-badge.priority-a{ background:var(--tan-super); border:2px solid #8a1818; }
.priority-badge.priority-b{ background:var(--tan-high); }
.priority-badge.priority-c{ background:var(--tan-std); }
a.back-link{
  text-decoration:none; color:var(--accent);
  font-weight:700; padding:2px 8px;
  margin-right:4px;
  border:1px solid var(--border-mid);
  border-radius:4px;
  font-family:var(--font-note);
  font-size:.92em;
  background:var(--paper);
  transition:.2s; white-space:nowrap;
  display:inline-block; margin-bottom:4px;
}
a.back-link:hover{
  background:var(--light);
  border-color:var(--mid);
  color:var(--accent);
}
.back-link-row{
  margin-top:12px;
  padding:10px 14px;
  background:var(--light);
  border-radius:6px;
  border-left:3px solid var(--accent);
  font-family:var(--font-note);
}
.back-link-row::before{ content:'📌 '; font-size:1.05em; }

/* === §19-bis choice-points === */
.choice-points{
  margin:28px 0 14px 0;
  background:linear-gradient(135deg,var(--accent-soft) 0%,var(--accent-3) 100%);
  border:1.5px solid rgba(var(--accent-rgb),.32);
  border-left:5px solid var(--accent);
  border-radius:10px;
  padding:18px 22px 16px 24px;
  box-shadow:0 2px 8px rgba(var(--accent-rgb),.10);
  position:relative;
}
.choice-points::before{
  content:'📌 肢ポイントまとめ';
  display:block;
  font-family:var(--font-display);
  font-weight:700;
  font-size:.98em;
  color:var(--accent);
  letter-spacing:.06em;
  margin-bottom:8px;
  border-bottom:1px dotted rgba(var(--accent-rgb),.38);
  padding-bottom:4px;
}
.choice-points ol{
  margin:0; padding-left:1.4em;
  list-style-type:decimal;
  list-style-position:outside;
}
.choice-points li{
  margin-bottom:6px;
  font-family:var(--font-soft);
  font-size:.96em;
  line-height:1.7;
  color:var(--text);
}
.choice-points li::marker{
  color:var(--accent);
  font-weight:700;
}
.choice-points li strong{ color:var(--accent); }

/* === §19-ter ref-stat / ref-case (v8.11.0 font-weight: 700) === */
a.ref-stat,
a.ref-case{
  display:inline;
  font-family:inherit;
  font-weight:700;
  padding:0 3px;
  border-radius:3px;
  text-decoration:none;
  border-bottom:1.5px solid;
  transition:background .15s, color .15s;
}
a.ref-stat{
  color:#1a2540;
  background:rgba(20,40,90,.06);
  border-bottom-color:rgba(20,40,90,.45);
}
a.ref-stat:hover{
  color:#fff;
  background:#1a2540;
  border-bottom-color:#1a2540;
}
a.ref-case{
  color:#2a1018;
  background:rgba(120,30,50,.07);
  border-bottom-color:rgba(120,30,50,.50);
}
a.ref-case:hover{
  color:#fff;
  background:#2a1018;
  border-bottom-color:#2a1018;
}

/* === §19-quater ref-backlinks (rb-chip tokenized) === */
.ref-backlinks{
  margin:14px 0 0 0;
  padding:10px 14px 8px 14px;
  background:linear-gradient(180deg,rgba(var(--accent-rgb),.04) 0%,rgba(var(--accent-rgb),.10) 100%);
  border-top:1.5px dashed rgba(var(--accent-rgb),.30);
  border-radius:0 0 6px 6px;
  font-family:var(--font-mono);
  font-size:.82em;
  display:flex;
  flex-wrap:wrap;
  gap:6px 10px;
  align-items:center;
}
.ref-backlinks::before{
  content:'↩ 参照元';
  font-family:var(--font-soft);
  font-weight:700;
  font-size:1.02em;
  color:var(--accent);
  margin-right:6px;
  letter-spacing:.04em;
}
a.rb-chip{
  display:inline-block;
  padding:2px 9px;
  background:var(--freq-mid);
  color:#fff !important;
  border:none;
  border-radius:999px;
  font-family:var(--font-mono);
  font-size:.94em;
  font-weight:600;
  letter-spacing:.04em;
  text-decoration:none;
  transition:.15s;
}
a.rb-chip:hover{
  background:var(--freq-mid-deep);
  transform:translateY(-1px);
}

/* === §20 tables / figure === */
.cmp-table-wrap{
  overflow-x:auto; margin:18px 0;
  border-radius:8px;
  box-shadow:0 2px 8px rgba(var(--accent-rgb),.08);
}
table, .cmp-table{
  width:100%; border-collapse:collapse;
  margin:0; font-size:.96em;
  background:var(--paper);
  page-break-inside:avoid;
}
th,td{
  border:1px solid var(--border-mid);
  padding:10px 12px;
  text-align:left; vertical-align:top;
  line-height:1.7;
}
th{
  background:var(--accent); color:#fff;
  font-family:var(--font-soft);
  font-weight:700; letter-spacing:.04em;
}
tr:nth-child(even) td{ background:var(--soft); }
tr:hover td{ background:var(--light); }
.ok-cell{ color:var(--recall-correct); font-weight:700; }
.ng-cell{ color:var(--recall-incorrect); font-weight:700; }
.row-key td{ background:var(--accent-soft) !important; }
.figure-wrap{
  text-align:center; margin:24px 0;
  background:var(--paper);
  border-radius:10px;
  padding:18px;
  overflow-x:auto;
  page-break-inside:avoid;
  border:1px solid var(--border-mid);
  box-shadow:0 2px 8px rgba(var(--accent-rgb),.08);
}
.figure-wrap svg{ max-width:100%; height:auto; }
.figure-caption{
  margin-top:10px;
  font-family:var(--font-note);
  font-size:.88em; color:var(--text);
  opacity:.78; letter-spacing:.04em;
}
blockquote{
  margin:14px 0; padding:14px 18px;
  background:var(--soft);
  border-left:5px solid var(--accent);
  border-radius:0 6px 6px 0;
  font-family:var(--font-quote);
  font-weight:400; line-height:1.95;
}

/* === §21 memory-list / memory-item === */
.memory-list{ margin:14px 0 18px; padding-left:0; list-style:none; }
.memory-item{
  position:relative;
  display:flex; gap:14px; align-items:flex-start;
  background:var(--paper);
  border:1px solid var(--border-mid);
  border-radius:8px;
  padding:14px 16px;
  margin:10px 0;
  font-family:var(--font-note);
  line-height:1.95;
  box-shadow:0 2px 6px rgba(var(--accent-rgb),.06);
  transition:.2s;
}
.memory-item:hover{
  box-shadow:0 4px 12px rgba(var(--accent-rgb),.12);
  transform:translateX(2px);
}
.memory-item.priority-a{ border-left:4px solid var(--tan-super); }
.memory-item.priority-b{ border-left:4px solid var(--tan-high); }
.memory-item.priority-c{ border-left:4px solid var(--tan-std); }
.memory-item .priority-badge{ flex-shrink:0; margin-right:0; }
.memory-item .mem-body{ flex:1 1 auto; font-size:.96em; }
.memory-item .mem-title{
  display:block;
  font-family:var(--font-display);
  font-weight:700; font-size:1.04em;
  color:var(--accent);
  margin-bottom:6px;
  letter-spacing:.04em;
  line-height:1.55;
}
.memory-item .mem-hint{
  display:block;
  margin-top:8px;
  font-family:var(--font-mono);
  font-size:.84em;
  color:var(--text);
  opacity:.78;
  letter-spacing:.02em;
}
.memory-item .mem-hint a{
  color:var(--accent); text-decoration:none;
  border-bottom:1px dotted var(--accent);
  margin:0 4px; font-weight:700;
}
.memory-item .mem-hint a:hover{ color:var(--mid); border-bottom-color:var(--mid); }

/* === §22 final-answer === */
.final-answer{
  position:relative;
  background:linear-gradient(180deg,var(--accent-soft) 0%,#fff 100%);
  border:2px solid var(--accent);
  border-radius:10px;
  padding:34px 30px 28px 30px;
  margin:28px 0 18px;
  font-family:var(--font-answer);
  font-weight:400; line-height:2.05;
  letter-spacing:.02em;
  page-break-inside:avoid;
  box-shadow:0 4px 14px rgba(var(--accent-rgb),.15);
}
.final-answer::before{
  content:'🎯 FINAL ANSWER';
  position:absolute; top:-12px; left:24px;
  background:linear-gradient(135deg,var(--accent),var(--mid));
  color:#fff; padding:4px 14px 3px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.74rem; font-weight:600; letter-spacing:.18em;
  box-shadow:0 2px 5px rgba(0,0,0,.18);
}
.final-answer > h3{ display:none; }
.final-answer .answer-num{
  display:inline-block;
  width:64px; height:64px;
  background:linear-gradient(135deg,var(--accent),var(--mid));
  color:#fff; border-radius:50%;
  font-family:var(--font-display);
  font-weight:800; font-size:2.1em;
  text-align:center; line-height:64px;
  margin:6px 0 14px;
  box-shadow:0 4px 12px rgba(var(--accent-rgb),.30);
}
.final-answer p{
  margin:0;
  font-size:1.02em;
  font-family:var(--font-answer);
}

/* === §22-bis fa-summary === */
.final-answer p.fa-summary{
  background:rgba(255,255,255,.92);
  border-left:5px solid var(--freq-high);
  border-radius:6px;
  padding:14px 18px 12px 18px;
  margin-bottom:18px !important;
  font-family:var(--font-answer);
  font-size:1.04em;
  line-height:1.85;
  color:var(--bg-dark);
  position:relative;
}
.final-answer p.fa-summary strong:first-child{
  display:inline-block;
  background:var(--freq-high);
  color:#fff;
  padding:2px 12px;
  border-radius:999px;
  font-family:var(--font-display);
  font-size:.78em;
  font-weight:700;
  letter-spacing:.10em;
  margin-right:10px;
  vertical-align:.10em;
}
.final-answer p.fa-summary a.ref-case,
.final-answer p.fa-summary a.ref-stat{
  background:rgba(255,255,255,.55);
}
.final-answer p.fa-summary a.ref-case:hover,
.final-answer p.fa-summary a.ref-stat:hover{
  background:#2a1018;
}

/* ============================================================
   §22-quater  multi-answer cells + spoiler-safe reveal
   (v8.11.1 で §22-ter HTML canonical に対応する CSS を正典組込み)
   ============================================================ */

/* §22-ter answer-num-multi セル群 — 多解答型の正答表示 */
.final-answer .answer-num.answer-num-multi{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
  width:auto;
  height:auto;
  background:transparent;
  border-radius:0;
  box-shadow:none;
  margin:6px 0 14px;
  padding:0;
  line-height:1;
}
.final-answer .answer-num-multi .ans-cell{
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  width:62px;
  height:62px;
  border-radius:12px;
  font-family:var(--font-display);
  color:#fff;
  box-shadow:
    0 3px 8px rgba(0,0,0,.20),
    inset 0 1px 0 rgba(255,255,255,.20);
  -webkit-print-color-adjust:exact;
  print-color-adjust:exact;
}
.final-answer .answer-num-multi .ans-cell.ans-correct{
  background:linear-gradient(135deg,var(--recall-correct) 0%,var(--recall-correct-light) 100%);
}
.final-answer .answer-num-multi .ans-cell.ans-incorrect{
  background:linear-gradient(135deg,#7e0024 0%,var(--recall-incorrect) 100%);
}
.final-answer .answer-num-multi .ans-stmt{
  font-size:.92em;
  font-weight:700;
  letter-spacing:.04em;
  margin-bottom:3px;
  opacity:.95;
  text-shadow:0 1px 2px rgba(0,0,0,.30);
}
.final-answer .answer-num-multi .ans-val{
  font-size:1.55em;
  font-weight:800;
  text-shadow:0 1px 2px rgba(0,0,0,.30);
}

/* §22-quater spoiler-safe — 初期は非表示、JS revealFinalAnswer() で開示 */
.final-answer[hidden]{ display:none !important; }
.final-answer.revealed{
  animation:faReveal .4s ease-out;
}
@keyframes faReveal{
  from{ opacity:0; transform:translateY(8px); }
  to  { opacity:1; transform:translateY(0); }
}


/* ============================================================
   §22-quinta  A-2 reveal-answer-btn + selected ハイライト
   (v8.11.2 で a2-two-stage-reveal canonical を確立)
   ============================================================ */
.reveal-answer-btn{
  display:inline-block;
  margin:14px 0 8px;
  padding:11px 28px;
  background:linear-gradient(135deg,var(--accent),var(--mid));
  color:#fff;
  border:none;
  border-radius:8px;
  font-family:var(--font-display);
  font-weight:700;
  font-size:1em;
  letter-spacing:.10em;
  cursor:pointer;
  box-shadow:0 3px 8px rgba(var(--accent-rgb),.25);
  transition:transform .15s ease, box-shadow .15s ease, opacity .15s ease;
}
.reveal-answer-btn:hover:not(:disabled){
  transform:translateY(-1px);
  box-shadow:0 5px 12px rgba(var(--accent-rgb),.35);
}
.reveal-answer-btn:active:not(:disabled){
  transform:translateY(0);
}
.reveal-answer-btn:disabled{
  opacity:.42;
  cursor:not-allowed;
  box-shadow:none;
}
.answer-slot.selected{
  background:var(--accent-soft);
  border-color:var(--accent);
  color:var(--accent);
  box-shadow:0 0 0 3px rgba(var(--accent-rgb),.20);
  transform:translateY(-1px);
}


/* ============================================================
   §22-sexta  A-2 multi-select & ox-grid (v8.11.3)
   ============================================================ */
/* Type B (multi): 複数選択時の counter 表示と緩和ハイライト */
.answer-area[data-answer-type="multi"] .answer-row{
  position:relative;
}
.answer-area[data-answer-type="multi"] .selection-counter{
  display:block;
  margin:8px 0 4px;
  font-size:.85em;
  color:var(--accent);
  font-family:var(--font-display);
  font-weight:600;
  opacity:.75;
}

/* Type C (ox-grid): ○× 評価グリッド */
.answer-ox-grid{
  display:flex;
  flex-direction:column;
  gap:10px;
  margin:14px 0 6px;
}
.ox-row{
  display:flex;
  align-items:center;
  gap:14px;
  padding:10px 16px;
  background:rgba(0,0,0,.02);
  border:1px solid var(--border-mid);
  border-radius:10px;
  transition:background .15s, border-color .15s;
}
.ox-row:hover{
  background:rgba(var(--accent-rgb),.04);
}
.ox-label{
  display:inline-block;
  min-width:44px;
  font-family:var(--font-display);
  font-weight:800;
  color:var(--accent);
  font-size:1.05em;
  text-align:center;
  letter-spacing:.06em;
}
.ox-stmt{
  flex:1;
  font-size:.92em;
  color:var(--text-mid);
  margin:0 8px 0 0;
}
.ox-btn-group{
  display:inline-flex;
  gap:8px;
  flex-shrink:0;
}
.ox-btn{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  min-width:54px;
  height:38px;
  padding:0 12px;
  border-radius:7px;
  border:2px solid var(--accent);
  background:#fff;
  color:var(--accent);
  font-family:var(--font-display);
  font-weight:700;
  font-size:.95em;
  letter-spacing:.04em;
  cursor:pointer;
  transition:transform .15s ease, box-shadow .15s ease, background .15s, color .15s;
}
.ox-btn:hover:not(:disabled){
  transform:translateY(-1px);
  box-shadow:0 2px 6px rgba(var(--accent-rgb),.20);
}
.ox-btn.selected{
  background:var(--accent);
  color:#fff;
  box-shadow:0 0 0 3px rgba(var(--accent-rgb),.20);
}
.ox-btn.correct-mark{
  background:var(--recall-correct);
  color:#fff;
  border-color:var(--recall-correct);
  box-shadow:0 2px 8px rgba(46,125,50,.20);
}
.ox-btn.incorrect-mark{
  background:var(--recall-incorrect);
  color:#fff;
  border-color:var(--recall-incorrect);
  box-shadow:0 2px 8px rgba(176,0,50,.20);
}
.ox-btn:disabled{
  cursor:not-allowed;
}

/* === §23 cross-grid (C-3) === */
.cross-grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  gap:16px; margin:18px 0;
}
.cross-card{
  background:var(--paper);
  border:1px solid var(--border-mid);
  border-left:4px solid var(--mid);
  border-radius:8px;
  padding:18px 20px 14px;
  box-shadow:0 2px 6px rgba(var(--accent-rgb),.06);
  transition:.2s;
}
.cross-card:hover{
  box-shadow:0 4px 12px rgba(var(--accent-rgb),.12);
  transform:translateY(-2px);
}
.cross-card h4{
  margin:0 0 10px 0;
  padding:0 0 8px 0;
  font-family:var(--font-soft);
  font-weight:700; font-size:1.04em;
  color:var(--accent);
  border-bottom:1.5px dashed var(--mid);
  display:flex; flex-direction:column; gap:4px; align-items:flex-start;
}
.cc-label{
  display:inline-block;
  font-family:var(--font-mono);
  font-size:.70rem; font-weight:700;
  letter-spacing:.16em; color:#fff;
  background:linear-gradient(135deg,var(--accent),var(--mid));
  padding:2px 10px 1px;
  border-radius:3px;
  box-shadow:0 1px 2px rgba(0,0,0,.18);
  text-transform:uppercase;
}
.cross-card p{
  margin:0 0 .7em;
  font-family:var(--font-note);
  font-size:.94em; line-height:1.85;
}
.cross-card p:last-child{ margin-bottom:0; font-size:.88em; opacity:.85; }
.cross-card .cc-row{ margin:8px 0; }
.cross-card .cc-key{
  display:inline-block;
  background:var(--accent-soft);
  color:var(--accent);
  font-family:var(--font-mono);
  font-size:.72em; font-weight:700;
  letter-spacing:.10em;
  padding:1px 8px;
  border-radius:3px;
  margin-right:6px;
}

/* ============================================================
   §24 READABILITY ENHANCEMENT LAYER (v8.11.0 canonical)
   ============================================================ */

/* §24-1 Section h3 — clearer subheading */
.section h3{
  position:relative;
  margin:26px 0 14px;
  padding:8px 0 8px 14px;
  font-size:1.18rem;
  color:var(--bg-dark);
  border-left:4px solid var(--accent);
  background:linear-gradient(90deg,
    rgba(var(--accent-rgb),.06) 0%,
    transparent 70%);
}

/* §24-2 Alternating backgrounds — C-3 cross-card */
.cross-grid .cross-card:nth-child(even){
  background:var(--accent-3);
}
.cross-grid .cross-card:nth-child(odd){
  background:var(--paper);
}

/* §24-3 Alternating backgrounds — C-7 memory-item */
.memory-list .memory-item.priority-a:nth-of-type(even),
.memory-list .memory-item.priority-b:nth-of-type(even),
.memory-list .memory-item.priority-c:nth-of-type(even){
  background:var(--accent-3);
}
.memory-list .memory-item.priority-a:nth-of-type(odd),
.memory-list .memory-item.priority-b:nth-of-type(odd),
.memory-list .memory-item.priority-c:nth-of-type(odd){
  background:var(--paper);
}

/* §24-4 lead-list — boxed cards with shadow */
.lead-list{
  padding-left:0;
  list-style:none;
  margin:14px 0 18px;
}
.lead-list > li{
  position:relative;
  background:var(--paper);
  border-left:4px solid var(--accent);
  border-radius:0 8px 8px 0;
  padding:14px 18px 14px 18px;
  margin-bottom:12px;
  line-height:1.78;
  box-shadow:
    0 1px 2px rgba(0,0,0,.04),
    0 3px 10px rgba(var(--accent-rgb),.08);
  transition:transform .15s ease, box-shadow .15s ease;
}
.lead-list > li:hover{
  transform:translateX(2px);
  box-shadow:
    0 1px 2px rgba(0,0,0,.06),
    0 6px 16px rgba(var(--accent-rgb),.14);
}
.lead-list > li::marker{ content:""; }
.lead-list > li:nth-child(even){
  background:var(--accent-3);
}
.lead-list > li > strong:first-child{
  display:block;
  margin-bottom:.5em;
  padding-bottom:.4em;
  border-bottom:1px dashed rgba(var(--accent-rgb),.30);
  font-family:var(--font-display);
  font-size:1.05em;
  color:var(--bg-dark);
  letter-spacing:.02em;
}

/* §24-5 日本国語的字下げ — 本文段落すべて */
p{
  text-indent:1em;
}
.figure-caption,
.answer-instruction{
  text-indent:0;
}

/* §24-6 ハンギングインデント — grid 2-column */
.basis-card-body > p.hanging{
  display:grid;
  grid-template-columns:max-content 1fr;
  column-gap:.5em;
  align-items:baseline;
  text-indent:0;
}
.basis-card-body > p.hanging > .hang-body{
  display:block;
}

/* === §24-bis basis-card-body font-weight 改訂 (v8.11.0) === */
/* .basis-card-body の font-weight:600 は §14 の定義に含まれる */

/* === §24 PART D ARENA === */
.recall-arena{ position:relative; }
.recall-arena .section-title{
  background:linear-gradient(90deg,var(--bg-dark) 0%,var(--accent) 100%);
  color:#fff;
  border-left:8px solid var(--mid);
}
.recall-arena .section-title .sec-icon{
  color:#ffd54f;
  text-shadow:0 0 8px rgba(255,213,79,.6);
}
.arena-intro{
  font-family:var(--font-note);
  background:var(--accent-soft);
  border-left:4px solid var(--mid);
  padding:14px 18px;
  border-radius:0 6px 6px 0;
  margin:14px 0 22px;
  line-height:1.95;
}
.arena-counter{
  position:static; z-index:auto;
  background:linear-gradient(135deg,var(--bg-dark) 0%,var(--accent) 100%);
  color:#fff; border-radius:12px;
  padding:18px 22px 14px;
  margin:0 0 24px;
  box-shadow:0 6px 18px rgba(var(--accent-rgb),.30);
  border:2px solid rgba(255,255,255,.12);
}
.counter-label{
  font-family:var(--font-mono);
  font-size:.82em; letter-spacing:.18em;
  opacity:.85; margin-bottom:6px;
  text-transform:uppercase;
}
.counter-display{
  font-family:var(--font-display);
  font-weight:800; font-size:1.8em;
  letter-spacing:.06em; margin-bottom:10px;
}
.counter-current{ color:#ffd54f; text-shadow:0 0 8px rgba(255,213,79,.4); }
.counter-divider{ opacity:.6; margin:0 4px; }
.counter-total{ opacity:.85; }
.counter-bar{
  width:100%; height:8px;
  background:rgba(255,255,255,.18);
  border-radius:999px; overflow:hidden;
  margin-bottom:8px;
}
.counter-fill{
  height:100%;
  background:linear-gradient(90deg,#ffd54f,#ffaa00,#ffd54f);
  border-radius:999px;
  width:0%;
  transition:width .4s ease;
}
.counter-stats{
  display:flex; gap:16px;
  font-family:var(--font-mono);
  font-size:.84em; letter-spacing:.06em;
  opacity:.92;
}
.counter-stats span span{
  font-weight:700; font-size:1.1em;
  color:#fff; margin-right:4px;
}
.drill-block{
  background:var(--paper);
  border:1px solid var(--border-mid);
  border-left:4px solid var(--mid);
  border-radius:8px;
  padding:16px 20px;
  margin:14px 0;
  box-shadow:0 2px 6px rgba(var(--accent-rgb),.06);
}
.drill-label{
  display:flex; align-items:center; gap:12px;
  margin-bottom:10px;
  padding-bottom:8px;
  border-bottom:1px dashed var(--border-mid);
  flex-wrap:wrap;
}
.drill-num{
  display:inline-block;
  background:linear-gradient(135deg,var(--accent),var(--mid));
  color:#fff;
  font-family:var(--font-mono);
  font-weight:700; font-size:.84em;
  padding:3px 10px; border-radius:4px;
  letter-spacing:.10em;
  box-shadow:0 1px 3px rgba(var(--accent-rgb),.20);
}
.drill-tag{
  font-family:var(--font-mono);
  font-size:.84em; color:var(--text);
  opacity:.75; letter-spacing:.04em;
}
.drill-back{
  display:inline-block; margin-left:8px;
  font-family:var(--font-mono);
  font-size:.84em; color:var(--accent);
  text-decoration:none;
  border-bottom:1px dotted var(--accent);
  font-weight:700;
}
.drill-back:hover{ color:var(--mid); border-bottom-color:var(--mid); }
.quiz-question{
  font-family:var(--font-quote);
  font-size:1.04em; font-weight:500;
  margin:6px 0 12px; line-height:1.85;
  letter-spacing:.02em;
}
.quiz-buttons{ display:flex; gap:14px; margin:10px 0; }
.quiz-btn{
  width:54px; height:54px;
  background:var(--paper);
  border:2px solid var(--mid);
  border-radius:10px;
  font-family:var(--font-display);
  font-weight:800; font-size:1.4em;
  color:var(--accent);
  cursor:pointer; transition:.2s;
  box-shadow:0 2px 5px rgba(var(--accent-rgb),.10);
}
.quiz-btn:hover:not(:disabled){
  background:var(--light);
  transform:translateY(-2px);
  box-shadow:0 4px 10px rgba(var(--accent-rgb),.18);
}
.quiz-btn:disabled{ cursor:not-allowed; opacity:.7; }
.quiz-btn.correct-mark, .quiz-btn.quiz-correct-mark{
  background:#d8eed6; border-color:#2e7d32;
  color:#1b5e20;
  box-shadow:0 0 0 2px rgba(46,125,50,.30);
  opacity:1;
}
.quiz-btn.incorrect-mark, .quiz-btn.quiz-incorrect-mark{
  background:#ffeef0; border-color:#c62828;
  color:#8a1818; opacity:.8;
}
.quiz-answer{
  margin-top:14px;
  padding:14px 18px 12px;
  background:linear-gradient(180deg,var(--accent-soft) 0%,var(--paper) 100%);
  border-left:4px solid var(--mid);
  border-radius:0 8px 8px 0;
  font-family:var(--font-note);
  line-height:1.85; font-size:.96em;
  box-shadow:0 1px 4px rgba(var(--accent-rgb),.06);
  transition:.3s;
}
.quiz-answer.quiz-answer-correct{
  background:linear-gradient(180deg,#e8f5e9 0%,#f3faf4 60%,var(--paper) 100%);
  border-left:4px solid var(--recall-correct-light);
  box-shadow:0 0 0 1px rgba(46,125,50,.18), 0 4px 14px rgba(46,125,50,.14);
}
.quiz-answer.quiz-answer-incorrect{
  background:linear-gradient(180deg,#ffeef0 0%,#fff4f6 60%,var(--paper) 100%);
  border-left:4px solid var(--recall-incorrect);
  box-shadow:0 0 0 1px rgba(176,0,50,.18), 0 4px 14px rgba(176,0,50,.14);
}
.quiz-result{
  display:inline-block;
  font-family:var(--font-display);
  font-weight:800; font-size:1.0em;
  letter-spacing:.10em;
  margin-right:10px;
  padding:4px 14px 3px;
  border-radius:6px; color:#fff;
  vertical-align:1px;
  box-shadow:0 2px 6px rgba(0,0,0,.20), inset 0 1px 0 rgba(255,255,255,.20);
  text-shadow:0 1px 2px rgba(0,0,0,.30);
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
.quiz-result:empty{ display:none; }
.quiz-result.quiz-result-correct{
  background:linear-gradient(135deg,var(--recall-correct) 0%,var(--recall-correct-light) 100%);
}
.quiz-result.quiz-result-incorrect{
  background:linear-gradient(135deg,#7e0024 0%,var(--recall-incorrect) 100%);
}
.arena-scorecard{
  position:relative;
  background:linear-gradient(180deg,#fff8e1 0%,#fff5d8 100%);
  border:2px solid #d99000;
  border-radius:14px;
  padding:36px 28px 28px;
  margin:28px 0 12px;
  text-align:center;
  page-break-inside:avoid;
  box-shadow:0 6px 18px rgba(217,144,0,.20);
}
.arena-scorecard::before{
  content:'🏆 SCORECARD';
  position:absolute; top:-14px; left:50%;
  transform:translateX(-50%);
  background:linear-gradient(135deg,#a06a00,#d99000);
  color:#fff; padding:5px 18px 4px;
  border-radius:4px;
  font-family:var(--font-mono);
  font-size:.78rem; font-weight:700; letter-spacing:.18em;
  box-shadow:0 2px 6px rgba(0,0,0,.20);
  white-space:nowrap;
}
.scorecard-banner{
  font-family:var(--font-display);
  font-size:1.0em; color:#7c5520;
  letter-spacing:.18em;
  margin-bottom:10px; font-weight:700;
}
.scorecard-score{
  font-family:var(--font-display);
  font-weight:800; font-size:3em;
  color:#7c5520; letter-spacing:.04em;
  margin:6px 0; line-height:1.1;
}
.scorecard-num{ color:var(--accent); }
.scorecard-divider{ color:#a07030; margin:0 6px; opacity:.6; }
.scorecard-total{ color:#a07030; }
.scorecard-grade{
  display:inline-block;
  margin:10px 0 14px;
  padding:6px 18px;
  background:linear-gradient(135deg,#a06a00,#d99000);
  color:#fff;
  font-family:var(--font-display);
  font-weight:800; font-size:1.15em;
  letter-spacing:.10em;
  border-radius:6px;
  box-shadow:0 2px 6px rgba(217,144,0,.30);
}
.scorecard-msg{
  font-family:var(--font-note);
  font-size:1em; color:var(--text);
  line-height:1.85;
  max-width:640px;
  margin:8px auto 16px;
  letter-spacing:.02em;
}
.arena-reset{
  margin-top:8px;
  padding:8px 22px;
  background:var(--accent); color:#fff;
  border:none; border-radius:999px;
  font-family:var(--font-soft);
  font-weight:700; font-size:.92em;
  letter-spacing:.06em;
  cursor:pointer;
  box-shadow:0 2px 6px rgba(var(--accent-rgb),.20);
  transition:.2s;
}
.arena-reset:hover{
  background:var(--mid);
  transform:translateY(-1px);
  box-shadow:0 4px 10px rgba(var(--accent-rgb),.30);
}

/* === §25 footer-spec === */
.footer-spec{
  background:linear-gradient(135deg,var(--accent),var(--mid));
  color:#fff; text-align:center;
  padding:26px 24px;
  margin:48px 0 0 0;
  border-radius:16px 16px 0 0;
  font-family:var(--font-mono);
  font-size:.92em; letter-spacing:.04em;
  line-height:1.85;
}
.footer-spec strong{
  color:#fff;
  font-family:var(--font-display);
  font-weight:700; letter-spacing:.06em;
}
.footer-spec .feature-tag{
  display:inline-block;
  background:rgba(255,255,255,.15);
  border:1px solid rgba(255,255,255,.30);
  border-radius:4px;
  padding:1px 8px;
  margin:2px 1px;
  font-size:.85em;
  letter-spacing:.04em;
}

/* === §26 print === */
@media print{
  *{-webkit-print-color-adjust:exact!important; print-color-adjust:exact!important;}
  body{ background:#fff; font-size:11pt; line-height:1.85; color:var(--text); letter-spacing:.02em; }
  .container{ max-width:100%; padding:0; }
  .container > section, .container > .choice-section{
    box-shadow:none; border-radius:0; padding:14px 0; margin:14px 0;
    page-break-inside:avoid;
  }
  @page{ size:A4; margin:20mm 15mm; }
  .doc-header{ position:absolute; top:8mm; right:8mm; font-size:13px; padding:4px 10px; box-shadow:none; }
  .header{
    background:var(--accent)!important; color:#fff!important;
    padding:20px 18px; border-radius:0; margin-bottom:18px;
  }
  .marker-legend{ background:#f8f8f8!important; -webkit-backdrop-filter:none; backdrop-filter:none; }
  .back-to-top, .arena-counter, .arena-reset{ display:none!important; }
  .section-title, .part-title, h3, h4{ page-break-after:avoid; }
  .key-phrase-box, .warning, .cross-link, .prof-analogy, .self-check-quiz,
  .basis-card, .sub-card, .figure-wrap, .cmp-table-wrap, .memory-item,
  .final-answer, .arena-scorecard, .drill-block, table{
    page-break-inside:avoid;
  }
  .exam-mark, .ron-mark, .freq-badge, .priority-badge, .verdict, .para-num,
  .fb-verdict, .fb-answer{
    -webkit-print-color-adjust:exact!important; print-color-adjust:exact!important;
  }
  a{ color:var(--accent); text-decoration:none; }
}

/* === §27 mobile === */
@media screen and (max-width:768px){
  body{ font-size:15px; line-height:1.92; }
  .container{ padding:0 14px 32px 14px; }
  .doc-header{ top:10px; right:12px; font-size:13px; padding:4px 10px; }
  .header{ padding:50px 18px 28px; }
  .header h1{ font-size:1.4em; letter-spacing:.04em; }
  .container > section, .container > .choice-section{ padding:22px 18px; }
  .section-title{ font-size:1.25em; padding:8px 12px; }
  .container > section > h3, .recall-arena > h3{ font-size:1.1em; padding:6px 12px; }
  .part-title{ font-size:1.15em; }
  .key-phrase-box{ padding:44px 20px 26px; font-size:.94rem; letter-spacing:.02em; line-height:1.92; }
  .warning, .cross-link{ padding:16px 22px 14px; }
  .prof-analogy{ padding:26px 22px 20px; }
  .sub-card{ padding:24px 18px 18px; }
  .final-answer{ padding:30px 20px 22px; }
  .basis-card-header{ padding:10px 16px; font-size:1em; }
  .basis-card-body{ padding:14px 16px; }
  .answer-slot{ width:50px; height:50px; font-size:1.25em; }
  .quiz-btn{ width:46px; height:46px; font-size:1.2em; }
  .scorecard-score{ font-size:2.4em; }
  .arena-counter{ position:static; }
  table, .cmp-table{ font-size:.88em; }
  th,td{ padding:7px; }
  .memory-item{ flex-direction:column; gap:6px; }
}

/* === SVG inline style consolidated (C-5 flowchart) === */
.figure-wrap svg .stepbox{ fill:url(#step5); stroke:#dc4d71; stroke-width:1.5; }
.figure-wrap svg .stepnum{ font-family:var(--font-mono); font-size:11px; font-weight:700; fill:#7e0024; letter-spacing:.10em; }
.figure-wrap svg .steptitle{ font-family:"Shippori Mincho B1",serif; font-size:14px; font-weight:700; fill:#5a1a30; }
.figure-wrap svg .stepdesc{ font-family:"Noto Sans JP",sans-serif; font-size:11px; fill:#231419; }
.figure-wrap svg .stepyes{ font-family:"Source Code Pro",monospace; font-size:10px; fill:#1b5e20; font-weight:700; }
.figure-wrap svg .arrow{ stroke:#8a1f3a; stroke-width:2; marker-end:url(#arr5); fill:none; }
.figure-wrap svg .branch{ fill:#f3e6da; stroke:#a07030; stroke-width:1.2; stroke-dasharray:3,3; }
.figure-wrap svg .branchtxt{ font-family:"Noto Sans JP",sans-serif; font-size:10.5px; fill:#7c5520; }

```

---

## §Annex A-bis-2. P2 セージブラリー override

P2 ファイル生成時は、§Annex A の直後（`<style>` ブロック末尾）に**単一の `:root{}` ブロック**として以下を追記する。本仕様書 v8.10.2 と同形式：

```css
:root{
  /* P2 セージブラリー (40〜60% 帯) — 27 色変数のみ override */
  --accent:        #4a6c50;
  --accent-rgb:    74,108,80;
  --mid:           #87a585;
  --mid-rgb:       135,165,133;
  --light:         #e0ebdf;
  --base:          #f5f3ee;
  --soft:          #e8e3d6;
  --paper:         #FFFFFF;
  --text:          #1a221c;
  --bg-dark:       #2c3e30;
  --accent-3:      #f3f7f0;
  --accent-soft:   #ecf2e8;
  --border-mid:    #c8d8c4;
  --kp-text-color: #0d130f;

  --freq-high:        #6b8e23;
  --freq-high-rgb:    107,142,35;
  --freq-high-deep:   #4a6318;
  --freq-mid:         #8a7b3c;
  --freq-mid-rgb:     138,123,60;
  --freq-mid-deep:    #635828;
  --freq-low:         #6a7a5e;
  --freq-low-rgb:     106,122,94;
  --freq-low-deep:    #4a5440;

  --recall-correct:        #1b5e20;
  --recall-correct-light:  #2e7d32;
  --recall-incorrect:      #8e6210;
  --recall-incorrect-light:#a07d38;
}
```

**追記の厳密形式（AP-24 防止）：** **単一の `:root{ ... }` ブロックのみ**。他のセレクタ追加・at-rule 追加・フォント変数 override・pattern marker 付与は絶対禁止。

---

## §Annex A-bis-3. P3 ラベンダードーン override

P3 ファイル生成時は、§Annex A の直後（`<style>` ブロック末尾）に**単一の `:root{}` ブロック**として以下を追記：

```css
:root{
  /* P3 ラベンダードーン (< 40% 帯) — 27 色変数のみ override */
  --accent:        #5b428a;
  --accent-rgb:    91,66,138;
  --mid:           #a08fc4;
  --mid-rgb:       160,143,196;
  --light:         #e8e2f0;
  --base:          #f7f4ee;
  --soft:          #ede5f0;
  --paper:         #FFFFFF;
  --text:          #1c1722;
  --bg-dark:       #3a2a55;
  --accent-3:      #f5f1f8;
  --accent-soft:   #eee8f2;
  --border-mid:    #d5c8e0;
  --kp-text-color: #120e1a;

  --freq-high:        #7b3c8a;
  --freq-high-rgb:    123,60,138;
  --freq-high-deep:   #552460;
  --freq-mid:         #966030;
  --freq-mid-rgb:     150,96,48;
  --freq-mid-deep:    #6e4520;
  --freq-low:         #735578;
  --freq-low-rgb:     115,85,120;
  --freq-low-deep:    #503a55;

  --recall-correct:        #1b5e20;
  --recall-correct-light:  #2e7d32;
  --recall-incorrect:      #9c2a52;
  --recall-incorrect-light:#b04068;
}
```

**追記の厳密形式：** §Annex A-bis-2 と同様、**単一の `:root{ ... }` ブロックのみ**。

---

## §Annex B. GENKEI Body Skeleton（純骨格 — プレースホルダ＋指示コメント）

`<body id="top">` 〜 `</body>` までの **GENKEI 骨格スケルトン**。問題固有内容は一切含まず、プレースホルダ（`[…]`）と指示コメント（`<!-- 指示: ... -->`）のみで構成。**A-3 共通根拠 section は PART B の後ろ・PART C の前**に配置済み。HTML タグ・class・構造 ID・nav 配線・SVG defs・固定 UI 文言・feature-tag 列は逐語保持。AI は §0-tri / §0-bis / §0-quad に従い、問題 PDF から解説・本文・判例引用・選択肢を新規生成して各プレースホルダに埋め込む（v8.x の `canonical/KTX301.html` や他既存 HTML の本文を流用してはならない — AP-42）：

```html
<body id="top">
<div class="container">

  <!-- ============================================================
       HEADER ── 問題メタ情報
       問題固有値はすべて [角括弧] のプレースホルダ。タグ・クラス・構造は変更しない。
       ============================================================ -->
  <header class="header">
    <div class="doc-header">[ファイル名: 例「刑TX300」「民TX045」等。科目接頭辞 + TX + 通し番号]</div>
    <div class="header-top">
      <span class="exam-badge">📚 [科目: 例「刑法」「民法」]</span>
      <span class="exam-badge">📝 [試験区分: 例「司法試験」「予備試験」]</span>
      <span class="exam-badge">📅 [出題年度: 例「H30」「R5」]</span>
      <span class="exam-badge">🔢 [問題番号: 例「第12問」]</span>
    </div>
    <h1>No.[番号] ── [問題テーマの簡潔な要約（30字程度）]（[試験コード: 例「司法H30-12」]）</h1>
    <div class="theme-tags">
      <!-- 該当する条文・概念・判例のキーワードを 4〜8 個 -->
      <span class="theme-tag">[テーマタグ1]</span>
      <span class="theme-tag">[テーマタグ2]</span>
      <span class="theme-tag">[テーマタグ3]</span>
      <span class="theme-tag">[テーマタグ4]</span>
    </div>
    <div class="exam-meta">
      <span><strong>正答率:</strong>[XX%]</span>
      <span><strong>難度:</strong>[★☆☆ / ★★☆ / ★★★ のいずれか]</span>
      <span><strong>パターン:</strong>[P1 ローズシャンブル / P2 セージブラリー / P3 ラベンダードーン。§32 P1/P2/P3 色変換ルールで決定]</span>
    </div>
    <div class="toc-row">
      <!-- toc-row は構造固定。choice の数だけ動的に増減 -->
      <a href="#part-a">問題文</a>
      <a href="#answer-area">解答</a>
      <a href="#choice-1">記述1</a>
      <a href="#choice-2">記述2</a>
      <a href="#choice-3">記述3</a>
      <a href="#choice-4">記述4</a>
      <a href="#choice-5">記述5</a>
      <a href="#basis">共通根拠</a>
      <a href="#c-1">体系</a>
      <a href="#c-7">三層記憶</a>
      <a href="#part-d">⚔ARENA</a>
    </div>
  </header>

  <!-- ============================================================
       marker-legend は全 TX 共通の固定文言。問題によらず以下を逐語保持。
       ============================================================ -->
  <div class="marker-legend" aria-label="マーカー凡例">
    <span class="lg-title">凡例</span>
    <span class="lg-item"><span class="lg-sample lg-ron">論</span>論文関連</span>
    <span class="lg-divider">|</span>
    <span class="lg-item"><span class="exam-mark freq-high">高</span>短答頻出</span>
    <span class="lg-item"><span class="exam-mark freq-mid">中</span>標準</span>
    <span class="lg-item"><span class="exam-mark freq-low">低</span>関連</span>
    <span class="lg-divider">|</span>
    <span class="lg-item"><span class="statute-emphasis freq-high">条</span>条文</span>
    <span class="lg-item"><span class="case-emphasis freq-high">判</span>判例</span>
  </div>

  <!-- ============================================================
       PART A ── 問題情報（A-1 問題文 + A-2 解答）
       ============================================================ -->
  <div class="part-title">PART A ── 問題情報</div>

  <section class="section" id="part-a">
    <nav class="sec-nav"><a href="#answer-area">↓解答</a><a href="#choice-1">↓記述1</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>A-1 問題文</h2>

    <!-- リード文: PDF から問題リード文を抽出して挿入 -->
    <p style="font-weight:600;">
      [問題のリード文をPDFから逐語抽出。「○○に関する次の1から5までの各記述のうち、判例の立場に従って検討した場合、誤っているものはどれか」等。重要キーワードに <span class="exam-mark freq-high">…</span> 等のマーカーを付す]
    </p>

    <h3 style="background:transparent; border-left:none; padding:8px 0 4px 0; margin:20px 0 8px 0; border-bottom:2px dotted var(--border-mid); color:var(--accent); font-family:var(--font-display);">【記述】</h3>

    <!-- 各記述: PDF から逐語抽出（改変・要約禁止）。choice-num-inline 番号は記述番号と一致 -->
    <div class="problem-text"><span class="choice-num-inline">1</span>[記述1本文をPDFから逐語抽出]</div>
    <div class="problem-text"><span class="choice-num-inline">2</span>[記述2本文をPDFから逐語抽出]</div>
    <div class="problem-text"><span class="choice-num-inline">3</span>[記述3本文をPDFから逐語抽出]</div>
    <div class="problem-text"><span class="choice-num-inline">4</span>[記述4本文をPDFから逐語抽出]</div>
    <div class="problem-text"><span class="choice-num-inline">5</span>[記述5本文をPDFから逐語抽出]</div>
    <!-- 注: 選択肢が4個・6個等の場合は問題の実数に合わせて増減。choice-num-inline を必ず実番号に合わせる -->

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <section class="section" id="answer-area">
    <nav class="sec-nav"><a href="#part-a">↑A-1</a><a href="#choice-1">↓記述1</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>A-2 解答</h2>

    <!-- 単一解答(data-answer-type="single"): 1つの正解。answer-area / data-correct-value はその1値 -->
    <!-- 多解答(data-answer-type="multi"): §22-ter answer-num-multi 構造。data-correct-value は "2,4" 等カンマ区切り -->
    <!-- data-explanation 内: HTML属性内なので " は &quot; / & は &amp; にエスケープ。改行は \n 不可・ピリオド区切りで散文化 -->
    <div class="answer-area"
         data-correct-value="[正解番号: 単一なら 例『5』。多解答なら 例『2,4』]"
         data-answer-type="single"
         data-explanation="[300〜500字程度のスポイラーセーフな解説。本問のテーマ・各記述の判例的立場・正解記述の核心理由を凝集。HTML属性内のためエスケープ厳守]">
      <h3>[問題リード文を解答指示文に転換。例「判例の立場に従って検討した場合、誤っているものをクリック」]</h3>
      <p class="answer-instruction">選択肢を選んで「解答を表示」を押してください。</p>
      <div class="answer-row">
        <!-- 選択肢ボタン: 問題の実数に合わせて生成。data-num / data-value は実番号 -->
        <button class="answer-slot" type="button" data-num="1" data-value="1">1</button>
        <button class="answer-slot" type="button" data-num="2" data-value="2">2</button>
        <button class="answer-slot" type="button" data-num="3" data-value="3">3</button>
        <button class="answer-slot" type="button" data-num="4" data-value="4">4</button>
        <button class="answer-slot" type="button" data-num="5" data-value="5">5</button>
      </div>
      <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>
      <div id="answer-feedback" hidden></div>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- ============================================================
       PART B ── 記述別解説（記述ごとに1セクション）

       各 choice-section の必須構造:
         choice-header-block (badge + verdict + summary)
         sub-card.original    (記述原文)
         sub-card.explanation (解説原文 = 判例引用 + 法理)
         sub-card.basis-link  (根拠条文・判例リンク)
         sub-card.professor   (教授の解説: prof-heading 1〜4 + key-phrase-box + analogy + warning + cross-link)
         choice-points        (まとめ ol 3項目)

       class odd/even: 記述1=odd, 2=even, 3=odd, 4=even, 5=odd ... 交互
       verdict: verdict-correct (✓) / verdict-incorrect (✗) / verdict-neutral / verdict-tossup
         「誤っているもの」を問う問題で「正しい記述」→ verdict-correct
         「誤っている記述」→ verdict-incorrect
       ============================================================ -->
  <div class="part-title">PART B ── 記述別解説（1〜[N]）</div>

  <!-- =============== 記述1 (テンプレート例) =============== -->
  <section class="choice-section odd" id="choice-1">
    <nav class="sec-nav"><a href="#answer-area">↑A-2</a><a href="#choice-2">記述2→</a></nav>

    <div class="choice-header-block">
      <div class="choice-big-badge">1</div>
      <span class="verdict verdict-correct">✓ [結論ラベル: 例「○○罪成立」「○○罪不成立」「過失あり」]</span>
      <div class="choice-summary">[本記述の判例的結論を1〜2文で凝集。核心命題を明示]</div>
    </div>

    <div class="sub-card original">
      <span class="label">記述原文</span>
      <p>[記述1本文を PART A の problem-text と同一文言で逐語掲載]</p>
    </div>

    <div class="sub-card explanation">
      <h4>📖 解説原文</h4>
      <p>[判例引用 + 法理 + 結論を 1〜2 段落で。
           判例リンク: <a class="ref-case" id="ref-case-[判例コード]-001" href="#case-[判例コード]">[判例名: 例「最判平○○.○.○」「大判昭○○.○.○」等]</a>（[掲載: 例「百選○編○○事件」「重判○○年度○事件」等。任意]）
           条文リンク: <a class="ref-stat" id="ref-law-[条文番号]-001" href="#law-[条文番号]">[条文表記: 例「○○条○項」]</a>
           判旨引用は <span class="ron-mark freq-high">「…」</span> で囲む
           重要語句は <span class="exam-mark freq-high">…</span> でマーク]</p>
    </div>

    <div class="sub-card basis-link">
      <h4>📚 根拠条文・判例</h4>
      <div class="back-link-row">
        <a class="back-link" href="#law-[条文番号]">→ [条文表記]</a>
        <a class="back-link" href="#case-[判例コード]">→ [判例名]（[掲載]）</a>
      </div>
      <p style="font-size:.92em; margin-top:6px;">[本記述で機能する条文・判例の役割を1文で簡潔に]</p>
    </div>

    <div class="sub-card professor">
      <h4>👨‍🏫 教授の解説</h4>

      <div class="prof-heading"><span class="prof-num">1</span>ポイント</div>
      <p>[「要するに」で始めて本記述が問うている核心論点を1段落で。<span class="ron-mark freq-high">…</span> で論文関連語句をマーク]</p>

      <div class="prof-heading"><span class="prof-num">2</span>考え方の道筋</div>
      <p>[論証ステップ①: 条文の構造・要件の確認。条文リンク <a class="ref-stat" id="ref-law-[条文番号]-002" href="#law-[条文番号]">…</a>]</p>
      <p>[論証ステップ②: 判例の規範定立]</p>
      <p>[論証ステップ③: 本問事案への接続の準備]</p>

      <div class="key-phrase-box">
        [本記述の核心命題を 2〜3 行で凝集。重要語句を <span class="kp-strong">…</span> で強調]
      </div>

      <div class="prof-heading"><span class="prof-num">3</span>イメージで掴む</div>
      <div class="prof-analogy">
        <span class="scene-title">場面：[具体場面のタイトル]</span>
        <p>[第1段落: 具体的な状況描写]</p>
        <p>[第2段落: その状況が判例の規範にどう乗るかをイメージで]</p>
      </div>

      <div class="prof-heading"><span class="prof-num">4</span>あてはめ</div>
      <p>[本問の事実関係を判例規範に当てはめて結論導出。判例・条文リンクのバックリファレンスを付す: <a class="ref-case" id="ref-case-[判例コード]-002" href="#case-[判例コード]">…</a>]</p>

      <div class="warning">
        <p>[よくある誤解・落とし穴を1段落で。<span class="exam-mark freq-high">…</span> で短答頻出語句をマーク]</p>
      </div>

      <div class="cross-link">
        <p>[他記述・関連論点との横断接続を1段落で。<span class="exam-mark freq-mid">…</span> 等]</p>
      </div>
    </div>

    <div class="choice-points">
      <ol>
        <li>[要点①: 本記述の核心命題]</li>
        <li>[要点②: 判例引用 + 結論を <a class="ref-case" href="#case-[判例コード]">…</a> 付きで]</li>
        <li>[要点③: 本問内での記述の位置づけ「○○と一致しており正しい」「○○に反し誤り（本問正解）」等]</li>
      </ol>
    </div>
    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- =============== 記述2 =============== -->
  <!-- class="choice-section even" / nav 左="#choice-1" 右="#choice-3" / choice-big-badge="2" -->
  <!-- ref-* ID のサフィックス連番は記述番号と一意に対応 (例: ref-case-XXX-003, -004) -->
  <section class="choice-section even" id="choice-2">
    <nav class="sec-nav"><a href="#choice-1">←記述1</a><a href="#choice-3">記述3→</a></nav>
    [記述1と同一構造で記述2の内容を生成。class は "choice-section even"]
  </section>

  <!-- =============== 記述3 (odd) / 記述4 (even) / 記述5 (odd) ... =============== -->
  <!-- 上記同様。nav は順次連結。最終記述の右側 nav は <a href="#basis">↓共通根拠</a> -->
  <section class="choice-section odd" id="choice-3">
    <nav class="sec-nav"><a href="#choice-2">←記述2</a><a href="#choice-4">記述4→</a></nav>
    [記述3の内容]
  </section>

  <section class="choice-section even" id="choice-4">
    <nav class="sec-nav"><a href="#choice-3">←記述3</a><a href="#choice-5">記述5→</a></nav>
    [記述4の内容]
  </section>

  <section class="choice-section odd" id="choice-5">
    <nav class="sec-nav"><a href="#choice-4">←記述4</a><a href="#basis">↓共通根拠</a></nav>
    [記述5の内容。最終記述の右側 nav は #basis を指す]
  </section>

  <!-- ============================================================
       A-3 共通根拠条文・判例 (PART B の後・PART C の前に配置 - v8.11.0 正規配置)

       basis-card は以下の2種類:
         statute-card: 条文を扱う (📜 アイコン)
         case-card:    判例を扱う (⚖ アイコン)

       ID 規約:
         条文: id="law-[条文番号]" (例 law-246)
         判例: id="case-[裁判所コード-元号年-月-日]" (例 case-saiko-h22-7-29 = 最高裁・平成22年7月29日)
              裁判所コード: saiko=最高裁, koto=高裁, dairen=大連判, etc.

       ref-backlinks の rb-chip は各記述の解説内 ref-* id への逆参照
       ============================================================ -->
  <section class="section" id="basis">
    <nav class="sec-nav"><a href="#choice-[最終記述番号]">↑記述[最終番号]</a><a href="#c-1">↓C-1</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>A-3 共通根拠条文・判例</h2>

    <!-- ----- 条文カード（必要数: 通常 1〜3 枚） ----- -->
    <div class="basis-card statute-card" id="law-[条文番号]">
      <div class="basis-card-header">📜 <span class="statute-emphasis freq-high">[条文略称: 例「刑法第246条」]</span>（[条文見出し: 例「詐欺」]）<span class="freq-badge freq-high">[★★★/★★/★]</span></div>
      <div class="basis-card-body">
        <!-- p.hanging + span.para-num + span.hang-body の3点セット (§24-6 hanging-grid canonical) -->
        <p class="hanging"><span class="para-num">第1項</span><span class="hang-body">[1項本文。要件部に <span class="ron-mark freq-high">…</span> をマーク]</span></p>
        <p class="hanging"><span class="para-num">第2項</span><span class="hang-body">[2項本文]</span></p>
        <!-- 必要に応じて第3項以下 -->
        <div class="note">
          <strong>[条文の意義・構造ラベル]</strong>：[条文の構成要件・成立要件・体系上の位置づけを 2〜4 文で]
        </div>
        <!-- ref-backlinks: 各記述の解説で参照した ref-law-[条文番号]-NNN への逆リンク -->
        <div class="ref-backlinks">
          <a class="rb-chip" href="#ref-law-[条文番号]-001">記述1</a>
          <a class="rb-chip" href="#ref-law-[条文番号]-005">記述2</a>
          <!-- 必要数 -->
        </div>
      </div>
    </div>

    <!-- ----- 判例カード（必要数: 通常 3〜6 枚） ----- -->
    <div class="basis-card case-card" id="case-[判例コード]">
      <div class="basis-card-header">⚖ <span class="case-emphasis freq-high">[判例名: 例「最判平成○年○月○日」「大判昭和○年○月○日」]</span>──[判例通称: 任意。本問判例の通称]（[掲載: 例「百選○編○○」「重判○○年度」 任意]）<span class="freq-badge freq-high">[★★★/★★/★]</span></div>
      <div class="basis-card-body">
        <p class="hanging"><strong>【事案】</strong><span class="hang-body">[事案の要約 1〜2 文]</span></p>
        <p class="judgment-text hanging"><strong>【判旨】</strong><span class="hang-body">「<span class="ron-mark freq-high">[判旨の核心引用]</span>」。[判旨の補足説明]</span></p>
        <div class="note">
          <strong>[判例の意義ラベル]</strong>：[判例の射程・横展開・本問における意義を 2〜4 文で]
        </div>
        <div class="ref-backlinks">
          <a class="rb-chip" href="#ref-case-[判例コード]-001">記述N解説</a>
          <a class="rb-chip" href="#ref-case-[判例コード]-002">あてはめ</a>
        </div>
      </div>
    </div>

    <!-- 必要な判例の数だけ case-card を繰り返し -->

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- ============================================================
       PART C ── 体系・記憶 (c-1 〜 c-7)
       ============================================================ -->
  <div class="part-title">PART C ── 体系・記憶</div>

  <!-- ===== C-1 体系的解説 ===== -->
  <section class="section" id="c-1">
    <nav class="sec-nav"><a href="#basis">↑共通根拠</a><a href="#c-2">C-2→</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>C-1 体系的解説──[本問の論点を一言で]</h2>

    <h3>趣旨（Why）──[本問テーマ]の体系的位置づけ</h3>
    <div class="key-phrase-box">
      [本問の論点が当該分野の体系上どこに位置するかを <span class="kp-strong">…</span> 強調を用いて 3〜5 行で凝集。
       例: 「○○罪の成否を判断する基準は ①〜④ の段階構造──」のような図解的整理]
    </div>
    <p>[本問の俯瞰: 何を素材とし何を確認する問題か。正解はどれかを明示。<span class="case-emphasis freq-high">…</span> 等のマーカーを使用]</p>

    <h3>[N] つの記述──結論一覧</h3>
    <div class="cmp-table-wrap">
      <table>
        <thead>
          <tr><th>記述</th><th>事案</th><th>結論</th><th>結びつく判例</th></tr>
        </thead>
        <tbody>
          <tr><td>1</td><td>[事案要約]</td><td><span class="case-emphasis freq-high">○ [結論]</span></td><td><a class="ref-case" href="#case-[判例コード]">[判例名]</a></td></tr>
          <!-- 各記述につき1行 -->
          <!-- 正解記述(誤っている記述)の行は <tr class="row-key"> で強調 -->
          <tr class="row-key"><td><strong>[正解番号]</strong></td><td>[事案]</td><td><span class="case-emphasis freq-high">× [結論]</span></td><td><a class="ref-case" href="#case-[判例コード]">[判例名]</a></td></tr>
        </tbody>
      </table>
    </div>
    <p style="font-size:.92em;">本問の正解は<strong>記述[正解番号]</strong>（[問いに対する位置づけ: 「判例の立場に従って検討した場合、誤っているもの」等]）。</p>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- ===== C-2 概念比較・全肢俯瞰 ===== -->
  <section class="section" id="c-2">
    <nav class="sec-nav"><a href="#c-1">←C-1</a><a href="#c-3">C-3→</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>C-2 概念比較・全肢俯瞰</h2>

    <h3>[論点群を俯瞰する大見出し 例「○○罪の N 大論点の俯瞰」]</h3>
    <div class="cmp-table-wrap">
      <table>
        <thead>
          <tr><th>論点</th><th>判例</th><th>核心命題</th><th>本問該当記述</th></tr>
        </thead>
        <tbody>
          <tr><td>[論点1]</td><td>[判例]</td><td>[命題]</td><td>[該当記述]</td></tr>
          <!-- 主要論点ごとに行。本問正解論点の行は <tr class="row-key"> -->
        </tbody>
      </table>
    </div>

    <h3>[第2の俯瞰見出し: 任意。例「各記述における ○段階構造の成否」]</h3>
    <div class="cmp-table-wrap">
      <table>
        <thead><tr><th>記述</th><th>要件①</th><th>要件②</th><th>要件③</th><th>要件④</th><th>結論</th></tr></thead>
        <tbody>
          <tr><td>1</td><td>○ [充足]</td><td>○ [充足]</td><td>○ [充足]</td><td>○ [充足]</td><td>[結論]</td></tr>
          <!-- 各記述ごとに各要件の充足を ○/× で。<span class="ng-cell"> / <span class="ok-cell"> で強調 -->
          <tr class="row-key"><td><strong>[正解番号]</strong></td><td>○</td><td>○</td><td><span class="ng-cell">× [欠落理由]</span></td><td><span class="ng-cell">× [帰結]</span></td><td><span class="case-emphasis freq-high">[結論]</span></td></tr>
        </tbody>
      </table>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- ===== C-3 関連科目との接続 ===== -->
  <section class="section" id="c-3">
    <nav class="sec-nav"><a href="#c-2">←C-2</a><a href="#c-4">C-4→</a></nav>
    <h2 class="section-title"><span class="sec-icon">❀</span>C-3 関連の深い科目との接続</h2>

    <div class="cross-grid">
      <!-- 関連論点・関連科目ごとに cross-card 1 枚。通常 3〜5 枚 -->
      <div class="cross-card">
        <h4><span class="cc-label">[科目/分野ラベル: 例「刑法各論」「民法総則」]</span>[小論点見出し]</h4>
        <div class="cc-row"><span class="cc-key">共通点</span>[当該論点との共通構造]</div>
        <div class="cc-row"><span class="cc-key">相違点</span>[本問固有事情との対比・差異]</div>
        <div class="cc-row"><span class="cc-key">関連条文・判例</span><a class="ref-stat" href="#law-[条文番号]">[条文]</a>／<a class="ref-case" href="#case-[判例コード]">[判例]</a></div>
      </div>
      <!-- cross-card を必要数繰り返し -->
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- ===== C-4 学説対立 ===== -->
  <section class="section" id="c-4">
    <nav class="sec-nav"><a href="#c-3">←C-3</a><a href="#c-5">C-5→</a></nav>
    <h2 class="section-title"><span class="sec-icon">⚔</span>C-4 学説対立</h2>

    <!-- 学説対立がある論点ごとに h3 + cmp-table-wrap を 1 セット。通常 3〜5 論点 -->
    <h3>① [学説対立論点1]（記述[該当番号]）</h3>
    <div class="cmp-table-wrap">
      <table>
        <thead><tr><th>学説</th><th>結論</th><th>論拠</th></tr></thead>
        <tbody>
          <tr class="row-key"><td><strong>[多数説・判例の通説名]（判例・通説）</strong></td><td><span class="ok-cell">[結論]</span></td><td>[論拠と判例引用]</td></tr>
          <tr><td>[少数説名]</td><td><span class="ng-cell">[結論]</span></td><td>[論拠]</td></tr>
          <!-- 学説が3つ以上ある場合は3行目以降を追加 -->
        </tbody>
      </table>
    </div>

    <h3>② [学説対立論点2]（記述[該当番号]）</h3>
    <!-- ↑同様の構造 -->

    <!-- 学説対立論点を必要数繰り返し -->

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- ===== C-5 総合フローチャート ===== -->
  <section class="section" id="c-5">
    <nav class="sec-nav"><a href="#c-4">←C-4</a><a href="#c-6">C-6→</a></nav>
    <h2 class="section-title"><span class="sec-icon">🗺</span>C-5 総合フローチャート</h2>

    <div class="key-phrase-box">
      <span class="kp-strong">[判定フローの総括見出し]</span>──[STEP 1 → 2 → 3 ... の概観。各記述がフローのどのステップで脱落/通過するかを言及]
    </div>

    <div class="figure-wrap">
      <!-- SVG フローチャート: stepbox + stepnum + steptitle + stepdesc + arrow の組合せ
           viewBox: 内容に応じて。標準は 720×700。STEP 数で高さ調整 (1 step = 高さ80〜100, 間隔25)
           defs の marker / linearGradient は §Annex A 内の SVG CSS と一体。下記をそのまま使用 -->
      <svg viewBox="0 0 720 700" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arr5" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto">
            <polygon points="0 0, 10 5, 0 10" fill="#8a1f3a"/>
          </marker>
          <linearGradient id="step5" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0" stop-color="#fff"/>
            <stop offset="1" stop-color="#fce4e8"/>
          </linearGradient>
        </defs>
        <!-- STEP 1 -->
        <rect class="stepbox" x="180" y="20" width="360" height="80" rx="6"/>
        <text class="stepnum" x="200" y="44">STEP 1</text>
        <text class="steptitle" x="200" y="64">[STEP 1 見出し]</text>
        <text class="stepdesc" x="200" y="84">[STEP 1 説明 (40字程度)]</text>
        <line class="arrow" x1="360" y1="100" x2="360" y2="125"/>
        <!-- STEP 2 (y は +105) -->
        <rect class="stepbox" x="180" y="125" width="360" height="80" rx="6"/>
        <text class="stepnum" x="200" y="149">STEP 2</text>
        <text class="steptitle" x="200" y="169">[STEP 2 見出し]</text>
        <text class="stepdesc" x="200" y="189">[STEP 2 説明]</text>
        <line class="arrow" x1="360" y1="205" x2="360" y2="230"/>
        <!-- 必要なステップ数だけ追加。最終ステップでは矢印を出さず終了。説明行が長い場合 stepdesc を2行に分け y 座標 +20 ずつ -->
      </svg>
      <p class="figure-caption">図：[フローチャートの正式名]</p>
    </div>

    <h3>運用上の鉄則</h3>
    <ul class="lead-list">
      <li><strong>STEP 1 で[判定軸見出し] を判定</strong>[判定の指針]</li>
      <li><strong>STEP 2 で[判定軸見出し] を切り分け</strong>[判定の指針]</li>
      <!-- 各 STEP につき 1 li。SVG のステップ数と一致 -->
    </ul>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- ===== C-6 関連問題・出題傾向 ===== -->
  <section class="section" id="c-6">
    <nav class="sec-nav"><a href="#c-5">←C-5</a><a href="#c-7">C-7→</a></nav>
    <h2 class="section-title"><span class="sec-icon">📚</span>C-6 関連問題・出題傾向</h2>

    <h3>出題傾向の分析</h3>
    <ul class="lead-list">
      <li><strong>[論点1の頻出度評価]</strong>[本問関連の出題傾向と他問題への展開]</li>
      <!-- 主要論点ごとに 1 li。通常 3〜5 項目 -->
    </ul>

    <h3>関連問題・参考</h3>
    <ul class="lead-list">
      <li><strong>[他問題ID 例「司H26-13」「予R3-15」]</strong>[論点の説明と本問との関連]</li>
      <!-- 関連問題 3〜5 問 -->
    </ul>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- ===== C-7 三層構造記憶 + final-answer (§22-bis) ===== -->
  <section class="section" id="c-7">
    <nav class="sec-nav"><a href="#c-6">←C-6</a><a href="#part-d">PART D→</a></nav>
    <h2 class="section-title"><span class="sec-icon">🧠</span>C-7 三層構造記憶</h2>

    <div class="key-phrase-box">
      <span class="kp-strong">本セクションは三層×5項目＝全15項目</span>──<strong>A層</strong>＝各記述1〜[N]の核心命題／<strong>B層</strong>＝[本問テーマ]を貫く5本の柱／<strong>S層</strong>＝本問関連の補強知識。
    </div>

    <h3>Priority A — 各記述の核心命題（試験直前必須・[N]項目）</h3>
    <div class="memory-list">
      <!-- 各記述につき 1 個。priority-a 固定。A1〜A[N] -->
      <div class="memory-item priority-a">
        <span class="priority-badge priority-a">A1</span>
        <div class="mem-body">
          <span class="mem-title">記述1：[核心命題見出し]</span>
          [核心命題本文 2〜3 行。<strong>…</strong> で要点を強調]
          <span class="mem-hint">▶ 判例：<a class="ref-case" href="#case-[判例コード]">[判例名]</a> ／ 該当記述：<a href="#choice-1">記述1（[結論ラベル: 「正しい」「誤り（本問正解）」等]）</a></span>
        </div>
      </div>
      <!-- A2 〜 A[N] を同様に -->
    </div>

    <h3>Priority B — [本問テーマ]体系の柱（週次サイクル・5項目）</h3>
    <div class="memory-list">
      <!-- 5 項目程度。priority-b 固定。B1〜B5 -->
      <div class="memory-item priority-b">
        <span class="priority-badge priority-b">B1</span>
        <div class="mem-body">
          <span class="mem-title">[柱の見出し: 体系を貫く法理の要点]</span>
          [柱の本文 2〜3 行]
          <span class="mem-hint">▶ [条文/判例の参照: <a class="ref-stat" href="#law-…">…</a>／<a class="ref-case" href="#case-…">…</a>]</span>
        </div>
      </div>
      <!-- B2 〜 B5 -->
    </div>

    <h3>Priority S — 補強・関連知識（直前2週間・5項目）</h3>
    <div class="memory-list">
      <!-- 5 項目程度。priority-c クラスを使用 (S 表示・C 装飾) -->
      <div class="memory-item priority-c">
        <span class="priority-badge priority-c">S1</span>
        <div class="mem-body">
          <span class="mem-title">[補強知識見出し]</span>
          [補強知識本文 2〜3 行]
          <span class="mem-hint">▶ [条文/判例の参照]</span>
        </div>
      </div>
      <!-- S2 〜 S5 -->
    </div>

    <!-- ===== §22-bis final-answer (単一解答) =====
         多解答の場合は §22-ter answer-num-multi 構造 (answer-num が複数 + 連結語) を使用 -->
    <div class="final-answer" hidden>
      <h3>🎯 正解</h3>
      <span class="answer-num">[正解番号]</span>
      <p class="fa-summary"><strong>一文要約</strong>　<span class="ron-mark freq-high">[本問の核心命題を1文で凝集]</span>。[正解記述が誤り(または正しい)とされる理由＋他記述の判例的処遇]</p>
      <p>[判例のキーワード一覧: 各記述ごとに 1 判例を引用し、覚えるべき結合命題を提示]</p>
    </div>

    <div class="back-to-top">
      <a href="#top">↑ ページ先頭へ</a>
      <a href="#part-d">⚔ ARENAでテスト</a>
    </div>
  </section>

  <!-- ============================================================
       PART D ── ACTIVE RECALL ARENA（全12問の Rapid-Fire ○×ドリル）

       設計指針:
       - 全 12 問 = 各記述につき 2 問 (誤判断パターン + 正判断確認) × N記述 + 横断問題で 12 に調整
       - 奇数 DRILL (01, 03, 05, ...) は「典型的な誤解パターン」を出題し正解 = ×
       - 偶数 DRILL (02, 04, 06, ...) は「判例の核心命題」を出題し正解 = ○
       - 最後の 1〜2 問は横断問題（複数記述/論点を結ぶ）。drill-back のリンク先は #c-1 等の体系セクション
       ============================================================ -->
  <div class="part-title">PART D ── ACTIVE RECALL ARENA</div>

  <section class="section recall-arena" id="part-d">
    <nav class="sec-nav"><a href="#c-7">←C-7</a><a href="#top">↑先頭</a></nav>
    <h2 class="section-title"><span class="sec-icon">⚔</span>D-1 Rapid-Fire ○×ドリル（全12問）</h2>

    <p class="arena-intro">
      [本セクションの簡潔な導入。何の即答化を狙うか。記述ごとの 2 問 + 横断 2 問の枠組みを明示]
    </p>

    <!-- arena-counter は固定UI。問題内容と無関係 -->
    <div class="arena-counter" id="arena-counter">
      <div class="counter-label">Mastery Progress</div>
      <div class="counter-display">
        <span class="counter-current" id="arena-current">0</span>
        <span class="counter-divider">/</span>
        <span class="counter-total">12</span>
      </div>
      <div class="counter-bar"><div class="counter-fill" id="arena-fill"></div></div>
      <div class="counter-stats">
        <span><span id="arena-correct">0</span>correct</span>
        <span><span id="arena-incorrect">0</span>incorrect</span>
      </div>
    </div>

    <!-- DRILL 01 (テンプレート例): 記述1 / 誤解パターン (× が正解) -->
    <div class="drill-block">
      <div class="drill-label">
        <span class="drill-num">DRILL&nbsp;01</span>
        <span class="drill-tag">記述[該当番号] / [誤解の見出し: 例「契約履行の抗弁」]</span>
      </div>
      <div class="self-check-quiz" data-arena="1"
           data-correct-value="×"
           data-explanation="[なぜ × か。判例引用 + 核心法理を 1〜2 文で。HTML 属性内ゆえエスケープ厳守]">
        <div class="quiz-question">Q. [誤解パターンの命題文をクリーンに記述]</div>
        <div class="quiz-buttons">
          <button class="quiz-btn" type="button" data-correct="false" data-value="○">○</button>
          <button class="quiz-btn" type="button" data-correct="true" data-value="×">×</button>
        </div>
        <div class="quiz-answer" hidden>
          <span class="quiz-result"></span>[要点を 1 文で]<a class="drill-back" href="#choice-[該当番号]">→ 記述[該当番号]の解説</a>
        </div>
      </div>
    </div>

    <!-- DRILL 02: 記述1 / 判例核心 (○ が正解) -->
    <div class="drill-block">
      <div class="drill-label">
        <span class="drill-num">DRILL&nbsp;02</span>
        <span class="drill-tag">記述[該当番号] / [判例核心の見出し]</span>
      </div>
      <div class="self-check-quiz" data-arena="1"
           data-correct-value="○"
           data-explanation="[なぜ ○ か。判例の核心命題を 1〜2 文で]">
        <div class="quiz-question">Q. [判例核心の命題文。判例の規範をそのまま出題化]</div>
        <div class="quiz-buttons">
          <button class="quiz-btn" type="button" data-correct="true" data-value="○">○</button>
          <button class="quiz-btn" type="button" data-correct="false" data-value="×">×</button>
        </div>
        <div class="quiz-answer" hidden>
          <span class="quiz-result"></span>[要点を 1 文で]<a class="drill-back" href="#choice-[該当番号]">→ 記述[該当番号]の解説</a>
        </div>
      </div>
    </div>

    <!-- DRILL 03〜12 を同じ drill-block 構造で。
         03: 記述2 / 誤解 (×)
         04: 記述2 / 判例核心 (○)
         05: 記述3 / 誤解 (×)
         06: 記述3 / 判例核心 (○)
         07: 記述4 / 誤解 (×)
         08: 記述4 / 判例核心 (○)
         09: 記述5 / 誤解 (×)
         10: 記述5 / 判例核心 (○)
         11: 横断 (drill-back は #c-1 等)
         12: 横断 (drill-back は #c-1 等)
         (記述数が異なる場合はこの割り当てを調整)
    -->

    <!-- arena-scorecard は固定UI。JS が表示制御 -->
    <div class="arena-scorecard" id="arena-scorecard" hidden>
      <div class="scorecard-banner">Final Result</div>
      <div class="scorecard-score">
        <span class="scorecard-num" id="scorecard-correct">0</span>
        <span class="scorecard-divider">/</span>
        <span class="scorecard-total">12</span>
      </div>
      <div class="scorecard-grade" id="scorecard-grade">─</div>
      <div class="scorecard-msg" id="scorecard-msg"></div>
      <button class="arena-reset" id="arena-reset" type="button">⟲ Reset Arena</button>
    </div>

    <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
  </section>

  <!-- ============================================================
       footer-spec
       feature-tag のリストは §33 footer-spec canonical 仕様による固定群。
       最終の feature-tag だけが P1/P2/P3 のパターン名で変動。
       v9.0.0 では「genkei-skeleton」「design-byte-lock」が追加・「ktx301-canon」は GENKEI 後継としての位置づけで継承。
       ============================================================ -->
  <div class="footer-spec">
    <p><strong>[ファイル ID: 例「刑TX300」]</strong>・[科目]（[出典: 例「司法H30-12」] [論点タイトル]）</p>
    <p>正答率：[XX%]／パターン [P1 ローズシャンブル / P2 セージブラリー / P3 ラベンダードーン] 適用</p>
    <p>正解：[正解値]（[内容: 例「誤っているものは記述5」]）</p>
    <p class="footer-meta">
      Spec:
      <span class="feature-tag">TX v9.0.0 GENKEI</span>・
      <span class="feature-tag">genkei-skeleton</span>・
      <span class="feature-tag">design-byte-lock</span>・
      <span class="feature-tag">content-independence</span>・
      <span class="feature-tag">ktx301-canon</span>・
      <span class="feature-tag">embedded-canon</span>・
      <span class="feature-tag">readability-layer</span>・
      <span class="feature-tag">hanging-grid</span>・
      <span class="feature-tag">basis-order-v2</span>・
      <span class="feature-tag">a2-feedback-canon</span>・
      <span class="feature-tag">rbchip-patched</span>・
      <span class="feature-tag">k302-immune</span>・
      <span class="feature-tag">p2p3-unified</span>・
      <span class="feature-tag">p1-absolute</span>・
      <span class="feature-tag">jp-prefix-naming</span>・
      <span class="feature-tag">spoiler-safe</span>・
      <span class="feature-tag">multi-answer-css</span>・
      <span class="feature-tag">a2-two-stage-reveal</span>・
      <span class="feature-tag">a2-multi-ox-support</span>・
      <span class="feature-tag">spoiler-leak-eradication</span>・
      <span class="feature-tag">spoiler-strong-elimination</span>・
      <span class="feature-tag">ox-grid-fa-unification</span>・
      <span class="feature-tag">host-injection-safe</span>・
      <span class="feature-tag">[適用パターン名: 例「P1 ローズシャンブル」]</span>
    </p>
  </div>

</div><!-- /.container -->

<!-- §Annex C JS placeholder — see §Annex C below -->
</body>
```

---

## §Annex C. Canonical JS（GENKEI byte-lock — 動作物理根拠）

`</body>` 直前の `<script>` ブロック内部に逐語コピー：

```javascript
/* ============================================================
   TX v8.11.6 - Annex C canonical JS
   KTX301 byte-level canonical
   body 閉じタグ直前の script ブロック内部に逐語コピー
   ============================================================ */

(function(){
  'use strict';
  if (window.__txInteractive || window.__ktxInteractive) return;
  window.__txInteractive = true;
  window.__ktxInteractive = true;

  function escapeHTML(s){
    return String(s == null ? '' : s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  }
  function readCorrect(el){
    return (el && el.dataset && (el.dataset.correctValue || el.dataset.correct)) || '';
  }
  function readUserVal(btn){
    if (btn && btn.dataset && btn.dataset.value) return btn.dataset.value;
    var t = (btn && btn.textContent) ? btn.textContent.trim() : '';
    if (t.indexOf('○') === 0) return '○';
    if (t.indexOf('×') === 0) return '×';
    return '';
  }

  // ========================================================
  // A-2 解答エリア — v8.11.3: 3 Type 対応 (single / multi / ox-grid)
  //   single:  クリックで選択ハイライト → reveal で正誤判定
  //   multi:   複数クリックで選択 (max=正解数)、トグル可、FIFO で最古解除
  //   ox-grid: 各 ox-row で 1 つずつ選択、全行揃ったら reveal 有効化
  // ========================================================
  function getAnswerType(area){
    return (area && area.dataset && area.dataset.answerType) || 'single';
  }
  function updateRevealBtnState(area){
    if (!area) return;
    var type = getAnswerType(area);
    var rb = area.querySelector('.reveal-answer-btn');
    if (!rb) return;
    var ready = false;
    if (type === 'single') {
      ready = !!area.querySelector('.answer-slot.selected');
    } else if (type === 'multi') {
      var correct = readCorrect(area) || '';
      var maxSel = correct.split(',').length;
      var count = area.querySelectorAll('.answer-slot.selected').length;
      ready = (count === maxSel);
      // counter 更新
      var counter = area.querySelector('.selection-counter');
      if (counter) counter.textContent = '選択中: ' + count + ' / ' + maxSel + ' 個';
    } else if (type === 'ox-grid') {
      var rows = area.querySelectorAll('.ox-row');
      var allSel = rows.length > 0;
      rows.forEach(function(r){
        if (!r.querySelector('.ox-btn.selected')) allSel = false;
      });
      ready = allSel;
    }
    rb.disabled = !ready;
  }
  function handleAnswerSlot(btn){
    var area = btn.closest('.answer-area');
    if (!area || area.classList.contains('answered')) return;
    var type = getAnswerType(area);
    if (type === 'multi') {
      var correct = readCorrect(area) || '';
      var maxSel = correct.split(',').length;
      if (btn.classList.contains('selected')) {
        btn.classList.remove('selected');
      } else {
        var selected = area.querySelectorAll('.answer-slot.selected');
        if (selected.length >= maxSel) {
          selected[0].classList.remove('selected'); // FIFO
        }
        btn.classList.add('selected');
      }
    } else {
      // single
      area.querySelectorAll('.answer-slot').forEach(function(s){
        s.classList.remove('selected');
      });
      btn.classList.add('selected');
    }
    updateRevealBtnState(area);
  }
  function handleOxBtn(btn){
    var area = btn.closest('.answer-area');
    if (!area || area.classList.contains('answered')) return;
    var row = btn.closest('.ox-row');
    if (!row) return;
    row.querySelectorAll('.ox-btn').forEach(function(b){
      b.classList.remove('selected');
    });
    btn.classList.add('selected');
    updateRevealBtnState(area);
  }
  function handleRevealAnswerBtn(btn){
    var area = btn.closest('.answer-area');
    if (!area || area.classList.contains('answered')) return;
    var type = getAnswerType(area);
    var correct = readCorrect(area);
    if (!correct) return;
    var ok = false;
    if (type === 'single') {
      var selected = area.querySelector('.answer-slot.selected');
      if (!selected) return;
      var user = readUserVal(selected);
      ok = (user === correct);
      area.querySelectorAll('.answer-slot').forEach(function(s){
        s.disabled = true;
        var sv = readUserVal(s);
        if (sv === correct) s.classList.add('correct-mark');
        else if (s === selected) s.classList.add('incorrect-mark');
      });
    } else if (type === 'multi') {
      var correctArr = correct.split(',').map(function(s){return s.trim();});
      var correctSet = {};
      correctArr.forEach(function(v){ correctSet[v] = true; });
      var selectedSlots = area.querySelectorAll('.answer-slot.selected');
      var userArr = [];
      selectedSlots.forEach(function(s){ userArr.push(readUserVal(s)); });
      ok = (userArr.length === correctArr.length);
      if (ok) {
        for (var i = 0; i < userArr.length; i++){
          if (!correctSet[userArr[i]]) { ok = false; break; }
        }
      }
      var userSet = {};
      userArr.forEach(function(v){ userSet[v] = true; });
      area.querySelectorAll('.answer-slot').forEach(function(s){
        s.disabled = true;
        var sv = readUserVal(s);
        if (correctSet[sv]) s.classList.add('correct-mark');
        else if (userSet[sv]) s.classList.add('incorrect-mark');
      });
    } else if (type === 'ox-grid') {
      var rows = area.querySelectorAll('.ox-row');
      var userVal = '';
      var selectedBtns = [];
      rows.forEach(function(r){
        var sel = r.querySelector('.ox-btn.selected');
        userVal += (sel ? readUserVal(sel) : '?');
        selectedBtns.push(sel);
      });
      ok = (userVal === correct);
      rows.forEach(function(r, idx){
        var correctChar = correct.charAt(idx);
        var selBtn = selectedBtns[idx];
        r.querySelectorAll('.ox-btn').forEach(function(b){
          b.disabled = true;
          var bv = readUserVal(b);
          if (bv === correctChar) b.classList.add('correct-mark');
          else if (b === selBtn) b.classList.add('incorrect-mark');
        });
      });
    }
    btn.disabled = true;
    var fb = area.querySelector('#answer-feedback') || area.querySelector('.answer-feedback');
    if (fb){
      fb.hidden = false;
      if (ok) {
        fb.style.background = 'linear-gradient(180deg,#e8f5e9 0%,#f3faf4 60%,#ffffff 100%)';
        fb.style.borderLeft = '5px solid var(--recall-correct-light)';
        fb.style.boxShadow = '0 0 0 1px rgba(46,125,50,.18), 0 4px 14px rgba(46,125,50,.14)';
        fb.innerHTML = '<strong class="fb-verdict fb-correct">✓ 正解</strong>';
      } else {
        fb.style.background = 'linear-gradient(180deg,#ffeef0 0%,#fff4f6 60%,#ffffff 100%)';
        fb.style.borderLeft = '5px solid var(--recall-incorrect)';
        fb.style.boxShadow = '0 0 0 1px rgba(176,0,50,.18), 0 4px 14px rgba(176,0,50,.14)';
        fb.innerHTML = '<strong class="fb-verdict fb-incorrect">✗ 不正解</strong>　正解は<span class="fb-answer">' + escapeHTML(correct) + '</span>';
      }
    }
    revealFinalAnswer();
    area.classList.add('answered');
  }

  // ========================================================
  // A-2 互換型（choice-row + check-btn）
  // ========================================================
  var selectedChoice = null;
  var legacyARevealed = false;
  function handleChoiceRow(row){
    if (legacyARevealed) return;
    document.querySelectorAll('.choice-row').forEach(function(r){ r.classList.remove('selected'); });
    row.classList.add('selected');
    selectedChoice = row.dataset.choice || null;
  }
  function handleCheckBtn(btn){
    if (legacyARevealed) return;
    var area = btn.closest('.answer-area');
    var ar = document.getElementById('answer-result') || (area && area.querySelector('.answer-result'));
    if (!selectedChoice){
      if (ar){
        ar.innerHTML = '<div style="color:var(--recall-incorrect);font-weight:600;padding:8px 0;">先に肢を1つ選んでください。</div>';
        ar.classList.add('show');
      }
      return;
    }
    legacyARevealed = true;
    var correct = (area && area.dataset.correctValue) || '';
    var exp = (area && area.dataset.explanation) || '';
    var ok = (selectedChoice === correct);
    document.querySelectorAll('.choice-row').forEach(function(r){
      var c = r.dataset.choice;
      if (c === correct) r.classList.add('correct');
      else if (c === selectedChoice) r.classList.add('incorrect');
    });
    if (ar){
      var verdictHTML = ok
        ? '<strong class="fb-verdict fb-correct">✓ 正解</strong>'
        : '<strong class="fb-verdict fb-incorrect">✗ 不正解</strong>';
      ar.innerHTML = '<div class="result-msg" style="padding:14px 18px;border-radius:8px;background:' +
        (ok ? 'linear-gradient(180deg,#e8f5e9,#f3faf4)' : 'linear-gradient(180deg,#ffeef0,#fff4f6)') +
        ';border-left:5px solid ' + (ok ? 'var(--recall-correct-light)' : 'var(--recall-incorrect)') +
        ';">' + verdictHTML + '　' + exp.replace(/^[○×\d]+。\s*/,'') + '</div>';
      ar.classList.add('show');
    }
    btn.disabled = true;
    revealFinalAnswer();
  }
  function revealFinalAnswer(){
    var fa = document.querySelector('.final-answer');
    if (!fa) return;
    fa.hidden = false;
    fa.removeAttribute('hidden');
    fa.classList.add('revealed');
  }

  // ========================================================
  // ARENA tracking
  // ========================================================
  var arenaQuizzes = document.querySelectorAll('.self-check-quiz[data-arena="1"]');
  var arenaTotal = arenaQuizzes.length;
  var arenaState = { answered: 0, correct: 0, incorrect: 0 };
  var arenaCurrent  = document.getElementById('arena-current');
  var arenaFill     = document.getElementById('arena-fill');
  var arenaCorrect  = document.getElementById('arena-correct');
  var arenaIncorrect= document.getElementById('arena-incorrect');
  var scoreCard     = document.getElementById('arena-scorecard');
  var scoreCorrect  = document.getElementById('scorecard-correct');
  var scoreGrade    = document.getElementById('scorecard-grade');
  var scoreMsg      = document.getElementById('scorecard-msg');

  function updateArenaCounter(){
    if (!arenaCurrent) return;
    arenaCurrent.textContent = arenaState.answered;
    if (arenaCorrect)   arenaCorrect.textContent   = arenaState.correct;
    if (arenaIncorrect) arenaIncorrect.textContent = arenaState.incorrect;
    if (arenaFill && arenaTotal) arenaFill.style.width = (arenaState.answered / arenaTotal * 100) + '%';
  }
  function showScoreCard(){
    if (!scoreCard || !arenaTotal) return;
    if (scoreCorrect) scoreCorrect.textContent = arenaState.correct;
    var pct = arenaState.correct / arenaTotal;
    var grade, msg;
    if (pct === 1)        { grade = 'S — PERFECT';     msg = '全問完答。論点群を完全に固められた状態。本試験でも即答できる水準。'; }
    else if (pct >= 11/12){ grade = 'A — EXCELLENT';   msg = 'ほぼ完答。誤答した問題の論点を解説リンクで再確認すれば合格水準を超える。'; }
    else if (pct >= 9/12) { grade = 'B — GOOD';        msg = '良好な仕上がり。誤答した論点について解説リンクから戻り、なぜ間違えたかを言語化してから再演習を。'; }
    else if (pct >= 7/12) { grade = 'C — DEVELOPING';  msg = 'まだ取りこぼしが多い。各記述の解説（PART B）と体系（PART C）に戻って論点をもう一度紐解いてから再挑戦を。'; }
    else                  { grade = 'D — REBUILD';     msg = '論点知識が定着していない。PART AからPART Cまで通読し、軸を掴み直そう。'; }
    if (scoreGrade) scoreGrade.textContent = grade;
    if (scoreMsg)   scoreMsg.textContent   = msg;
    scoreCard.hidden = false;
    scoreCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  function resetArena(){
    arenaQuizzes.forEach(function(quiz){
      var buttons = quiz.querySelectorAll('.quiz-btn');
      var answer = quiz.querySelector('.quiz-answer');
      var result = quiz.querySelector('.quiz-result');
      buttons.forEach(function(b){
        b.disabled = false;
        b.classList.remove('correct-mark', 'incorrect-mark', 'quiz-correct-mark', 'quiz-incorrect-mark');
      });
      if (answer) {
        answer.hidden = true;
        answer.classList.remove('quiz-answer-correct', 'quiz-answer-incorrect');
      }
      if (result) {
        result.textContent = '';
        result.style.color = '';
        result.classList.remove('quiz-result-correct', 'quiz-result-incorrect');
      }
      quiz.dataset.done = '';
      quiz.classList.remove('answered');
    });
    arenaState.answered = 0;
    arenaState.correct  = 0;
    arenaState.incorrect = 0;
    updateArenaCounter();
    if (scoreCard) scoreCard.hidden = true;
  }

  // ========================================================
  // self-check-quiz
  // ========================================================
  function handleQuizBtn(btn){
    var quiz = btn.closest('.self-check-quiz');
    if (!quiz || quiz.classList.contains('answered') || quiz.dataset.done === '1') return;
    quiz.dataset.done = '1';
    quiz.classList.add('answered');

    var correct = readCorrect(quiz);
    var user = readUserVal(btn);
    var isArena = quiz.getAttribute('data-arena') === '1';

    var ok;
    if (correct) {
      ok = user ? (user === correct) : (btn.getAttribute('data-correct') === 'true');
    } else {
      ok = btn.getAttribute('data-correct') === 'true';
    }

    quiz.querySelectorAll('.quiz-btn').forEach(function(b){
      b.disabled = true;
      var bc = b.getAttribute('data-correct') === 'true';
      if (bc) b.classList.add('correct-mark');
      else    b.classList.add('incorrect-mark');
    });

    var answer = quiz.querySelector('.quiz-answer');
    var result = quiz.querySelector('.quiz-result');
    if (answer) answer.hidden = false;
    if (result) {
      if (ok) {
        result.textContent = '✓ 正解';
        result.classList.add('quiz-result-correct');
        if (answer) answer.classList.add('quiz-answer-correct');
      } else {
        result.textContent = '✗ 不正解';
        result.classList.add('quiz-result-incorrect');
        if (answer) answer.classList.add('quiz-answer-incorrect');
      }
    }

    if (isArena) {
      arenaState.answered += 1;
      if (ok) arenaState.correct += 1; else arenaState.incorrect += 1;
      updateArenaCounter();
      if (arenaState.answered === arenaTotal) setTimeout(showScoreCard, 600);
    }
  }

  // ========================================================
  // 単一クリック委譲
  // ========================================================
  document.addEventListener('click', function(e){
    var t = e.target;
    if (!t || !t.closest) return;
    var slot = t.closest('.answer-slot');       if (slot)     { handleAnswerSlot(slot); return; }
    var ox   = t.closest('.ox-btn');             if (ox)       { handleOxBtn(ox); return; }
    var rb   = t.closest('.reveal-answer-btn');  if (rb)       { handleRevealAnswerBtn(rb); return; }
    var row  = t.closest('.choice-row');      if (row)      { handleChoiceRow(row); return; }
    var ck   = t.closest('.check-btn');       if (ck)       { handleCheckBtn(ck); return; }
    var qb   = t.closest('.quiz-btn');        if (qb)       { handleQuizBtn(qb); return; }
    var rs   = t.closest('.arena-reset');     if (rs)       {
      if (confirm('ARENAをリセットしますか？すべての回答がクリアされます。')) resetArena();
      return;
    }
  }, false);

  // ========================================================
  // スムーズスクロール
  // ========================================================
  document.querySelectorAll('a[href^="#"]').forEach(function(a){
    a.addEventListener('click', function(e){
      var id = a.getAttribute('href');
      if (id.length <= 1) return;
      var tgt = document.querySelector(id);
      if (tgt){
        e.preventDefault();
        tgt.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  function init(){ updateArenaCounter(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();

```

---

## §37. 仕様書終了

> **TX v9.0.0 GENKEI 仕様書（GENKEI-skeleton · forged-from-archetype · readability-enhanced · hanging-indent-grid · single-document-self-sufficient · jp-prefix-naming · content-independence · a2-two-stage-reveal · 3-type-support · spoiler-leak-eradication · spoiler-strong-elimination · ox-grid-fa-unification · host-injection-safe）終わり**
>
> **使用方法（再掲）**:
>
> 1. **新規 TX ファイル生成**：本仕様書全文＋問題 PDF を AI に送信 → §0-tri 6 ステップ → §0-quad 7 ステップ独立性プロトコル（GENKEI 化により Annex B には汚染ソースが存在しないため大半が自動充足）→ §0-bis 15 ステップ → §1-bis 命名規則 → §17 3 Type 対応（single/multi/ox-grid 自動判定）→ §31 S1〜S82 自己検証通過後に配信。**追加の仕様書・参照ファイルは一切不要**（自己完結）
>
> 2. **既存 TX ファイル（v8.x 以下）アップグレード**：§0-tri STEP 1（既存スタイル完全破棄・GENKEI 拡張版）を最優先実行 → §35 K302-1〜K302-17 異常検出 → §34-bis〜§34-novies の v8.x 系移行ルートを参照しつつ、GENKEI スケルトンに沿って構造化 → S64〜S82 検証
>
> 3. **v8.x → v9.0.0 GENKEI への移行**：
>    - 既存 HTML 出力は形を保ったまま CSS/JS 部分が刑TX300 由来 byte-lock に揃っていれば視覚的に互換
>    - 新規生成時は §Annex B 骨格スケルトンに従い PDF から内容を新規鋳造（v8.x 系 byte-level 逐語からの脱却）
>    - footer-spec に `genkei-skeleton` / `design-byte-lock` / `TX v9.0.0 GENKEI` タグを追加
>
> 4. **改変ソース反映**：内容変更箇所のみ波及修正 → 事前事後検証＋ S52〜S82
>
> **v9.0.0 GENKEI で確立した経路**：(a) §Annex A CSS / §Annex C JS を**刑TX300 由来 byte-lock** に固定し、フォント・色・余白・動作の物理根拠を仕様書に埋込（design-byte-lock）、(b) §Annex B を**問題固有内容ゼロの純骨格スケルトン**に転換（genkei-skeleton）、(c) これにより §0-quad コンテンツ独立性プロトコルが手続的に解こうとしてきた KTX301-canonical からの本文流入問題を**構造そのもので解消**、(d) v8.11.x が積み上げてきた §1-bis 命名規則／§17 3 Type 対応／spoiler-* 系／host-injection-safe 等の機能はすべて継承、の 4 層で「個別問題の写しを正典とする」設計から「構造の原型のみを規範化する」設計への転換を完成させた。
>
> **絶対遵守**：§0-tri ゼロベース再構築プロトコル・**§0-quad コンテンツ独立性 7 ステップ**・**§1-bis 命名規則**・KTX301 byte-level law（構造シェルのみ）・A-3 PART B 後配置・§24 readability layer・§24-6 hanging-grid canonical・font-weight 強化・**A-2 2 段階開示プロトコル**（answer-instruction canonical 文言固定／reveal-answer-btn 必須）・**3 Type 自動判定**（data-answer-type 整合）・**FA hidden 属性必須**・**`<script>` 内 `</body>` リテラル禁止**・**AP-26〜AP-42 全禁止リスト**。