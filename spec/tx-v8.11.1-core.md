# TX v8.11.1 規律本体（core spec）

**KTX301-canonical · readability-enhanced · hanging-indent-grid · spoiler-safe · multi-answer-css-restored · lessons-from-chat-002-and-003**

司法試験・予備試験 短答式（短答 = Tantō = TX）対策の単問解説 HTML 生成仕様。  
全 7 法（憲法／民法／刑法／商法／民訴／刑訴／行政法）共通の汎用シリーズ名は **TX**。

科目別ファイル接頭辞：**KEN**(憲法)／**MIN**(民法)／**K**(刑法)／**SYO**(商法)／**MINS**(民訴)／**KEIS**(刑訴)／**GSE**(行政法)

> **本ファイルは規律本体のみ**。canonical コード（CSS・HTML骨格・JS）は以下の別ファイルを参照：
> - `spec/tx-v8.11.1-annex-A.css`（canonical CSS · 既定 P1 ローズシャンブル）
> - `spec/tx-v8.11.1-annex-A-bis-2.css`（P2 セージブラリー override · 末尾追記用）
> - `spec/tx-v8.11.1-annex-A-bis-3.css`（P3 ラベンダードーン override · 末尾追記用）
> - `spec/tx-v8.11.1-annex-B.html`（canonical body skeleton template）
> - `spec/tx-v8.11.1-annex-C.js`（canonical JS）
> - `canonical/KTX301.html`（canonical 実装例。byte-level 正典）

## §0-prime. v8.11.0 → v8.11.1 差分

### v8.11.1 改訂 3 項目

1. **spoiler-safe canonical 確立**:すべての `<div class="final-answer">` に `hidden` 属性を必須化。`spec/tx-v8.11.1-annex-C.js` の `revealFinalAnswer()` は v8.7 以来存在するが、対応する HTML 側 `hidden` 初期宣言が欠落しており JS reveal が実質 no-op となっていた canonical 欠陥を修復。`spec/tx-v8.11.1-annex-A.css` に `.final-answer[hidden]{display:none !important}` ＋ reveal アニメーション規則を追加

2. **§22-ter answer-num-multi CSS の §Annex A 組込み**:v8.11.0 で HTML canonical のみ定義されていた `.answer-num.answer-num-multi` / `.ans-cell` / `.ans-stmt` / `.ans-val` の 5 規則を `spec/tx-v8.11.1-annex-A.css` の §22 final-answer 直後・§23 cross-grid 直前に逐語追加。P2 セージブラリー・P3 ラベンダードーンで多解答セルが背景と同化する現象を恒久解消

3. **AP-30〜AP-32／K302-18／S68〜S70 追加・§22-quater 新設**:chat-003 観測症例の恒久カタログ化＋ `fa-summary` 内「正解はN」リテラル禁止の明文化

### v8.11.0 までの差分（既存・継承）

KTX301 canonical 移行・§24 readability layer 全 6 サブセクション・A-3 PART B 後再配置・font-weight 強化・§24-6 hanging-grid・AP-26〜AP-29／S64〜S67／K302-17 は完全継承。

---

---

## §0. 使い方（運用フロー）

### 0-1. 新規 TX ファイル生成

1. 問題 PDF を読み、問題番号・科目・年度・全選択肢・正解・正答率・出題テーマを抽出
2. §0-tri 6 ステップ（ゼロベース再構築）を順次実行
3. §0-bis 13 ステップ生成プロトコルを順次実行
4. §31 S1〜S70 の自己検証（`scripts/validate.py` 実行）
5. 検証通過後に配信

### 0-2. 既存 TX ファイル（v8.10.2 以下）のアップグレード

1. §0-tri STEP 1（既存スタイル完全破棄）を**最優先**で実行
2. §35 K302-1〜K302-18 失敗パターン照合し違反検出時に regeneration
3. §34-bis 12 ステップで canonical 化（最終ステップで S64〜S70 検証）

---

## §0-tri. ゼロベース再構築プロトコル（最優先命令）

### ■ STEP 1：既存スタイルの完全破棄

既存ファイルの以下は **すべて読み捨てる・参照しない・引き継がない**：

- `<head>` 内の `<link href="https://fonts.googleapis.com/...">` フォントリンク全体
- `<style>` ブロック **内部の全 CSS 規則**
- 旧 PART 順序（v8.10.2 以下では A-3 が PART A 内にあった構造）→ 完全破棄
- A-2 feedback 関連 旧バグ規則：
  - `#answer-feedback strong{...color:#fff !important; ...}`
  - 旧 JS の `feedback.innerHTML = '<strong style="color:var(--recall-correct)">...'`
  - 旧 HTML `<div class="answer-slot">` → `<button class="answer-slot">` に置換
- text-indent + overflow:hidden 不整合パターン（AP-26）：
  - `padding-left:Xem; text-indent:-Xem;` を**削除**
- `<p>` 直当て flex/grid + 単純 strong マージン（AP-27）：
  - `.basis-card-body > p { display:flex/grid }` を**削除**
- `.ron-mark { display:inline-block }`（AP-28）→**削除**
- `<body>` 内 DOM 骨格・全 JS を破棄

> **AI 心得**：「保守的書き換え」（前のコードを引き継ごうとする癖）を**強制的に無効化**せよ。以下は保守的書き換えが頻発する領域：
> 1. `!important` 付き規則
> 2. inline style ベース innerHTML 構築
> 3. `<div>` ベース対話要素
> 4. 負 text-indent ハンギング
> 5. `.ron-mark` の display 改変

### ■ STEP 2：骨格の完全クローン

以下を **1 バイトの改変もなく・逐語コピー**して新ファイルの土台とせよ：

1. §Annex B-link の Google Fonts `<link>` タグ（`spec/tx-v8.11.1-annex-B.html` 冒頭コメント参照）
2. `spec/tx-v8.11.1-annex-A.css` 全文
3. `spec/tx-v8.11.1-annex-B.html` の body skeleton
4. `spec/tx-v8.11.1-annex-C.js` 全文

### ■ STEP 3：コンテンツのみ抽出・流し込み

| 抽出対象 | 抽出元 | 流し込み先 |
|---|---|---|
| 問題文（事例文・設問） | 旧 `.problem-text` 等 | `<section id="part-a">` |
| 各選択肢の本文 | 旧 `.choice-section .original` | 各 `.choice-section .sub-card.original` |
| 正解値 | 旧 `data-correct-value` 等 | `data-correct-value` 属性 + `.final-answer` |
| A-2 feedback 説明文 | 旧 JS 内 `feedback.innerHTML` 本文部分 | `data-explanation` 属性（プレーンテキスト） |
| 各記述の `explanation` | 旧 `.sub-card.explanation` | 各 `.sub-card.explanation` |
| 共通根拠テキスト | 旧 `<section id="basis">` | `.basis-card` 内（**ラベル始まり段落は `<p class="hanging"><span class="hang-body">` ラップ必須**） |
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
| ≥ 60% | P1 ローズシャンブル | **追記不要**（annex-A.css 既定値そのまま） |
| 40〜60% | P2 セージブラリー | `spec/tx-v8.11.1-annex-A-bis-2.css` の `:root{}` ブロックを `<style>` 末尾に追記 |
| < 40% | P3 ラベンダードーン | `spec/tx-v8.11.1-annex-A-bis-3.css` の `:root{}` ブロックを `<style>` 末尾に追記 |

**override の厳密形式（AP-24 防止）：** 追記してよいのは **単一の `:root{ ... }` ブロックのみ**。他のセレクタ追加・at-rule 追加・フォント変数 override・pattern marker 付与は**絶対禁止**。

### ■ STEP 5：footer-spec 更新（v8.11.1 版）

```html
<p class="footer-meta">
  Spec:
  <span class="feature-tag">TX v8.11.1</span>・
    <span class="feature-tag">spoiler-safe</span>・
    <span class="feature-tag">multi-answer-css</span>・
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
  <span class="feature-tag">[P1|P2|P3] [パレット名]</span>
</p>
```

**v8.11.1 新規必須 tag**：`ktx301-canon`／`readability-layer`／`hanging-grid`／`basis-order-v2`

### ■ STEP 6：生成直前の自己検証

`scripts/validate.py` を実行し、S1〜S70 全件通過を確認。違反があれば修正してから配信。

---

## §0-bis. AI 13 ステップ生成プロトコル

1. **問題 PDF を読解**：問題番号・科目・年度・全選択肢・正解・正答率・出題テーマを抽出
2. **正答率からパターン判定**：≥60%→P1／40-60%→P2／<40%→P3
3. **冒頭応答必須**：「正答率__%→パターン_『___』適用」を最初に出力
4. **問題形式の判定**：単一選択／5記述○×型／空欄補充型／組合せ型の4類型を識別
5. **§0-tri STEP 1（既存スタイル破棄）実行**（既存ファイル改変時のみ）
6. **annex-A.css を逐語コピー**
7. **P2 or P3 の場合のみ annex-A-bis-2 / -3 の `:root{}` 上書きブロックを末尾追記**
8. **annex-B.html の body skeleton を逐語適用**（A-3 が PART B 後ろ）
9. **content を差替え**。**A-2 解説文は `data-explanation` 属性に格納**しプレーンテキスト化。**条文・判例 body のラベル始まり段落は必ず `<p class="hanging"><span class="hang-body">` ラップ**
10. **annex-C.js を逐語コピー**
11. **PART D ARENA を ○/× rapid-fire で構築**（12 問・○:×=6:6）
12. **全 section-title に sec-icon 配置**
13. **`scripts/validate.py` で S1〜S70 自己検証** → 全件通過後に配信

---

## §2. 全体構造（PART 構成）── v8.11.1 改訂

```
HTML doc
├── <head>
│   ├── <meta>
│   ├── <title>
│   ├── <link>（Google Fonts）
│   └── <style>
│        ├── annex-A.css 逐語コピー
│        └── （P2/P3 のみ）annex-A-bis-2 or -3 の :root{} 単一ブロック末尾追記
└── <body id="top">
    └── <div class="container">
        ├── <header class="header">
        ├── <div class="marker-legend">
        │
        ├── <div class="part-title">PART A ── 問題情報</div>
        │   ├── <section id="part-a">（A-1：問題文）
        │   └── <section id="answer-area">（A-2：解答）
        │
        ├── <div class="part-title">PART B ── 肢別解説</div>
        │   └── <section class="choice-section odd|even" id="choice-1〜5"> × 5
        │
        ├── ★★★【v8.11.1 新配置】★★★
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
    <script>（annex-C.js 逐語コピー）</script>
```

### §2-1. v8.11.1 navigation 順序

A-3 が PART B 後に移動するため、関連する `<nav class="sec-nav">` 全件を以下に書き換え：

| section | v8.11.1 |
|---|---|
| A-1 sec-nav | `↓解答 / ↓記述ア` |
| A-2 sec-nav | `↑A-1 / ↓記述ア` |
| 記述ア sec-nav | `↑A-2 / 記述イ→` |
| 記述オ sec-nav | `←記述エ / ↓共通根拠` |
| A-3 sec-nav | `↑記述オ / ↓C-1` |
| C-1 sec-nav | `↑共通根拠 / C-2→` |

### §2-2. topbar TOC 順序

```
問題文 / 解答 / ア / イ / ウ / エ / オ / 共通根拠 / 体系 / 三層記憶 / ⚔ARENA
```

---

## §11. 必須コンポーネント

### sub-card 4 種

PART B 各記述内に必ず順序通り配置：
1. `original`（記述原文再掲）
2. `explanation`（解説原文）
3. `basis-link`（根拠条文・判例リンク）
4. `professor`（4 prof-heading：1ポイント／2考え方の道筋／3イメージで掴む／4あてはめ ＋ 内蔵 key-phrase-box）

### 補助カード（callout 4 種）

`warning` / `cross-link` / `prof-analogy` / `key-phrase-box`

---

## §17. PART A canonical 構造

### §17-2. answer-area 必須属性

```html
<div class="answer-area"
     data-correct-value="N"
     data-explanation="N。正解の根拠・論点・判例の趣旨を一文で要約。プレーンテキスト。">
  <h3>正しいと思う番号をクリック</h3>
  <p class="answer-instruction">クリックすると即座に正誤判定が表示されます。</p>
  <div class="answer-row">
    <button class="answer-slot" type="button" data-num="1" data-value="1">1</button>
    <button class="answer-slot" type="button" data-num="2" data-value="2">2</button>
    <button class="answer-slot" type="button" data-num="3" data-value="3">3</button>
    <button class="answer-slot" type="button" data-num="4" data-value="4">4</button>
    <button class="answer-slot" type="button" data-num="5" data-value="5">5</button>
  </div>
  <div id="answer-feedback" hidden></div>
</div>
```

**禁止事項：**
- `<div class="answer-slot">` ← `<button>` 必須
- `<div id="answer-feedback" hidden style="...">` ← inline style 一切なし
- `data-correct-value` / `data-explanation` 属性の省略
- HTML 側に長文 innerHTML テンプレートをハードコード

---

## §22-bis / §22-ter / §22-quater. final-answer canonical

### §22-bis. 単一解答型 final-answer（C-7 末尾配置）

3 段構成必須。**`hidden` 属性必須（v8.11.1）**:

```html
<div class="final-answer" hidden>
  <h3>🎯 正解</h3>
  <span class="answer-num">3</span>
  <p class="fa-summary"><strong>[一文要約]</strong>　[詳細]</p>
  <p>[追加説明＋ref-stat/ref-case リンク]</p>
</div>
```

`fa-summary` 内に「正解はN」リテラル禁止（AP-32）。

### §22-ter. 多解答型 final-answer（answer-num-multi）

```html
<div class="final-answer" hidden>
  <h3>🎯 正解</h3>
  <div class="answer-num answer-num-multi">
    <div class="ans-cell ans-correct"><span class="ans-stmt">ア</span><span class="ans-val">1</span></div>
    <div class="ans-cell ans-correct"><span class="ans-stmt">イ</span><span class="ans-val">1</span></div>
    <div class="ans-cell ans-correct"><span class="ans-stmt">ウ</span><span class="ans-val">1</span></div>
    <div class="ans-cell ans-incorrect"><span class="ans-stmt">エ</span><span class="ans-val">2</span></div>
    <div class="ans-cell ans-incorrect"><span class="ans-stmt">オ</span><span class="ans-val">2</span></div>
  </div>
  <p class="fa-summary"><strong>[一文要約]</strong>　[詳細]</p>
</div>
```

多解答型でも `fa-summary` に「正解は1・1・1・1・2」等のリテラル絶対禁止。

### §22-quater. final-answer spoiler-safe canonical（v8.11.1 新規）

v8.7 以来 `revealFinalAnswer()` JS は存在するが、HTML 側 `hidden` 初期宣言が欠落していたため JS reveal が no-op になっていた canonical 欠陥を修復。

- **§22-quater-1**: HTML 要件 — すべての `<div class="final-answer">` に `hidden` 属性必須
- **§22-quater-2**: `fa-summary` 本文の「正解はN」リテラル禁止（AP-32）
- **§22-quater-3**: `spec/tx-v8.11.1-annex-A.css` に CSS パッチ正典組込み（§22-bis fa-summary 直後・§23 cross-grid 直前）。`.answer-num.answer-num-multi` / `.ans-cell` / `.ans-correct` / `.ans-incorrect` / `.ans-stmt` / `.ans-val` / `.final-answer[hidden]` / `@keyframes faReveal` の 8 規則
- **§22-quater-4**: `spec/tx-v8.11.1-annex-C.js` の `revealFinalAnswer()` は変更なし（v8.7 以来既存）


---

## §24. Readability Enhancement Layer（v8.11.1 canonical）

annex-A.css 内に **§24-1〜§24-6** の 6 サブセクションが全件存在することが必須（S64 検証）。

### §24-6. ハンギングインデント（HTML wrap 必須）

`.basis-card-body > p` の先頭子要素が以下のいずれかの場合 **必ず** `class="hanging"` ＋ `<span class="hang-body">` ラップ：

- `<span class="para-num">…</span>`（条文番号バッジ）
- `<strong>【事案】</strong>` ／ `<strong>【判旨】</strong>` ／ `<strong>I.</strong>` 等

```html
<!-- ❌ bare 形式（NG・AP-26/27 違反） -->
<p><span class="para-num">第108条</span>放火して…</p>

<!-- ✓ v8.11.1 canonical 形式 -->
<p class="hanging"><span class="para-num">第108条</span><span class="hang-body">放火して、…</span></p>

<!-- 判旨パラグラフ -->
<p class="judgment-text hanging"><strong>【判旨】</strong><span class="hang-body">「他人の委託により…」</span></p>
```

---

## §31. SEVERE 自己検証 S1〜S70

`scripts/validate.py` で自動チェック。詳細は scripts ディレクトリ参照。

主要チェック項目：

- **S1〜S5**：タグ開閉バランス
- **S11**：PART A に 2 section（A-1, A-2）← v8.11.1 改訂
- **S64**：§24 readability layer 全 6 サブセクション存在
- **S65**：§24-6 ハンギングインデント HTML 構造（`<p class="hanging">` と `<span class="hang-body">` 数一致）
- **S66**：PART 順序（basis が choice-5 後・c-1 前）
- **S67**：font-weight 改訂検証＋AP-26/27/28 検出
  - `.basis-card-body { font-weight: 600 }`
  - `a.ref-stat`, `a.ref-case { font-weight: 700 }`
  - `.ron-mark` に `display:inline-block` 含まない（AP-28）
  - `.basis-card-body > p` に `display:flex/grid` 直当て不存在（AP-27）
  - 負 text-indent 不存在（AP-26）
- **S68（v8.11.1 新規）**：すべての `<div class="final-answer">` に `hidden` 属性付与（AP-30 検出）
- **S69（v8.11.1 新規）**：§22-quater-3 CSS パッチ存在検証（AP-31 検出）
  - `.answer-num.answer-num-multi` / `.ans-cell` / `.ans-correct` / `.ans-incorrect` / `.final-answer[hidden]` / `@keyframes faReveal`
- **S70（v8.11.1 新規）**：`<p class="fa-summary">` 内に「正解はN」「正解は[XXXXX]」リテラル不存在（AP-32 検出）

---

## §32. 3 パターン色変換ルール

| パターン | 正答率帯 | 名称 | 処理 |
|:-:|:-:|:--|:--|
| **P1** | ≥ 60% | ローズシャンブル | annex-A.css 既定値そのまま使用。**override 追記不要** |
| **P2** | 40〜60% | セージブラリー | annex-A-bis-2.css の `:root{}` ブロックを `<style>` 末尾に追記 |
| **P3** | < 40% | ラベンダードーン | annex-A-bis-3.css の `:root{}` ブロックを `<style>` 末尾に追記 |

> **P1 absolute canon 鉄則**：P1 ファイルと P2/P3 ファイルを diff した際、差分は `:root{}` 27 行ブロックのみ（footer-spec のパレット名表記を除く）。

---

## §35. K302 型異常 17 症状

| 症状 ID | 部位 | 症状 |
|:-:|:--|:--|
| K302-1〜5 | PART D drill | 旧 quiz 構造温存 |
| K302-6〜11 | PART C | wrapper 欠落、素 span、cross-grid 親欠落 |
| K302-13 | PART C title | U+2015 単独使用 |
| K302-15 | P2/P3 CSS override | `:root{}` 以外のセレクタ存在 or pattern-conditional marker |
| K302-16 | A-2 feedback | 旧 `#answer-feedback strong{color:#fff !important}` 等 |
| **K302-17** | **v8.11.1 新規** | **A-3 配置／§24 layer／hanging-indent／ron-mark display／over-decoration** |

---

## §31-6. アンチパターンカタログ AP-1〜AP-32

### AP-26（v8.11.1 新規）：negative text-indent + overflow:hidden 不整合
祖先要素に `overflow:hidden` がある状態で負の text-indent を使うとラベルがクリップ。**正当な代替：§24-6 の Grid 方式**。

### AP-27（v8.11.1 新規）：`<p>` 直当て flex/grid + 混在インライン子要素
`<p>` を flex/grid コンテナにすると、内部の各インライン子要素が個別の flex/grid item になり line-flow が破綻。**正当な代替：`<span class="hang-body">` で本文を atomic-wrap してから `display:grid` を適用**。

### AP-28（v8.11.1 新規）：`.ron-mark` display 改変
`.ron-mark` を `inline-block` 化すると長文 ron-mark が全体ごと次行にブロックジャンプ。**canonical：`.ron-mark { display: inline }` を維持**。

### AP-29（v8.11.1 新規）：over-decoration tendency
ユーザーの「見やすく」「凝って」という曖昧要求に対する過度な装飾（SVG 図表自動追加、4 象限カード再配置、trophy-style final-answer、elaborate hover transitions 等）。**設計指針：最小介入版を先に提示し、段階的拡張**。

---

## §33. footer-spec canonical（v8.11.1 版）

```html
<div class="footer-spec">
  <p>[ファイル ID]・[科目]（[出典：年度-問題番号] [論点タイトル]）</p>
  <p>正答率：[N]%／パターン [P1|P2|P3]「[名称]」適用</p>
  <p>正解：[正解値]（[内容]）</p>
  <p class="footer-meta">
    Spec:
    <span class="feature-tag">TX v8.11.1</span>・
    <span class="feature-tag">spoiler-safe</span>・
    <span class="feature-tag">multi-answer-css</span>・
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
    <span class="feature-tag">[P1|P2|P3] [名称]</span>
  </p>
</div>
```

---

## §36. v8.11.1 core invariant

```
新規 TX ファイルと annex-B.html 骨格を diff したとき:
  差分は コンテンツ要素 + doc-header/footer-spec + (P2/P3 のみ) :root{} 27 行ブロック
        のみ

加えて以下が成立:
  - <section id="basis"> が PART B の後ろ・PART C の前 (§2, S66)
  - §24 readability layer 全 6 サブセクションが <style> 内に存在 (S64)
  - .basis-card-body > p のラベル始まり段落が class="hanging" + <span class="hang-body"> 形式 (S65)
  - .basis-card-body の font-weight が 600 (S67)
  - a.ref-stat/a.ref-case の font-weight が 700 (S67)
  - .ron-mark に display:inline-block が指定されていない (S67/AP-28)
  - .basis-card-body > p に display:flex/grid が直接指定されていない (S67/AP-27)
  - 旧 padding-left + 負 text-indent ハンギングが存在しない (S67/AP-26)
  - #answer-feedback strong{color:#fff !important} が CSS 全体で 0 件 (S62)
  - feedback.innerHTML が <strong class="fb-verdict fb-correct|fb-incorrect"> ＋ <span class="fb-answer"> 形式 (S63)

v8.11.1 で追加された invariant:
  - すべての <div class="final-answer"> に hidden 属性 (S68/AP-30)
  - .answer-num.answer-num-multi / .ans-cell / .ans-correct / .ans-incorrect
    / .final-answer[hidden] / @keyframes faReveal 規則が <style> 内に存在 (S69/AP-31)
  - <p class="fa-summary"> 内に「正解はN」「正解は[XXXXX]」リテラルが 0 件 (S70/AP-32)
  - footer-spec に feature-tag "TX v8.11.1" / "spoiler-safe" / "multi-answer-css" 存在
```

これを満たさないファイルは AP-X / K302-X として regeneration（K302-1〜17）または §34-ter minor 更新（K302-18）の対象。
