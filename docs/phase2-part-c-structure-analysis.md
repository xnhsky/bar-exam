# Phase 2: PART C 構造精密解析（gold standard: 刑TX300.html）

> 入力: `inputs/tx-legacy/刑TX300.html`（3713 行・刑法 共通H26-13 詐欺罪 5 大判例）
> 範囲: PART C ── 体系・記憶（7 セクション C-1〜C-7）
> 目的: schema 拡張・slot 化・render 関数の構造的根拠

---

## 0. 全体構成

```
<div class="part-title">PART C ── 体系・記憶</div>

<section class="section" id="c-1">  C-1 体系的解説
<section class="section" id="c-2">  C-2 概念比較・全肢俯瞰
<section class="section" id="c-3">  C-3 関連の深い科目との接続
<section class="section" id="c-4">  C-4 学説対立              (optional)
<section class="section" id="c-5">  C-5 総合フローチャート
<section class="section" id="c-6">  C-6 関連問題・出題傾向    (optional)
<section class="section" id="c-7">  C-7 三層構造記憶
```

各 `<section>` の共通骨格：
- `<nav class="sec-nav">` 前後ナビ（先頭）
- `<h2 class="section-title"><span class="sec-icon">EMOJI</span>C-N タイトル</h2>`
- 本文（セクション固有 HTML）
- `<div class="back-to-top">` 末尾

---

## 1. C-1 体系的解説（systematic）

**sec-icon**: ❀

### 1-1. ヘッダー（タイトル末尾の補足あり）

```html
<h2 class="section-title"><span class="sec-icon">❀</span>C-1 体系的解説──詐欺罪の成立要件と他罪の限界</h2>
```

「C-1 体系的解説」固定 + `title_suffix`（例: `──詐欺罪の成立要件と他罪の限界`）。

### 1-2. 趣旨ブロック

```html
<h3>趣旨（Why）──詐欺罪体系における「成立要件」</h3>
<div class="key-phrase-box">
  詐欺罪の成否を判断する基準は <span class="kp-strong">4段階の因果連鎖</span>──<br>
  ①<span class="kp-strong">人に対する欺罔行為</span>...<br>
  ...
</div>
<p>本問は、<span class="case-emphasis freq-high">詐欺罪 5大判例(...)</span>を素材として、...</p>
```

要素：
- `<h3>` 趣旨見出し
- `<div class="key-phrase-box">` 内に inline HTML（`<br>` 改行・`<span class="kp-strong">` 太字フレーズ）
- `<p>` 要約段落（`<span class="case-emphasis freq-high">` 等の inline span）

### 1-3. 結論一覧テーブル

```html
<h3>5 つの記述──結論一覧</h3>
<div class="cmp-table-wrap">
  <table>
    <thead><tr><th>記述</th><th>事案</th><th>結論</th><th>結びつく判例</th></tr></thead>
    <tbody>
      <tr><td>1</td><td>...</td><td><span class="case-emphasis freq-high">○ ...</span></td><td><a class="ref-case" href="#case-...">...</a></td></tr>
      ...
      <tr class="row-key"><td><strong>5</strong></td>...<td><span class="case-emphasis freq-high">× ...</span></td>...</tr>
    </tbody>
  </table>
</div>
<p style="font-size:.92em;">本問の正解は<strong>記述5</strong>...</p>
```

要素：
- `<h3>` テーブル見出し
- `cmp-table-wrap` ラッパー + `<table>`
- `<thead>` ヘッダー行（任意数の `<th>`）
- `<tbody>` データ行（任意数）。本問正解行は `<tr class="row-key">`
- `<span class="case-emphasis freq-high">` で結論ハイライト
- `<a class="ref-case" href="#case-...">` 判例リンク
- 末尾 `<p>` 注釈（小フォント）

---

## 2. C-2 概念比較・全肢俯瞰（comparison）

**sec-icon**: ❀

複数の `<h3>` + `<div class="cmp-table-wrap">` table の繰り返し。各テーブルは独立した「観点」を表す。

```html
<h3>詐欺罪 5大論点の俯瞰</h3>
<div class="cmp-table-wrap"><table>...</table></div>

<h3>各記述における4段階因果連鎖の成否</h3>
<div class="cmp-table-wrap"><table>...</table></div>
```

セル内 span:
- `<span class="ng-cell">× ...</span>` （× セル）
- `<span class="ok-cell">○ ...</span>` （○ セル）
- `<span class="case-emphasis freq-high">...</span>` （ハイライト結論）
- `<strong>...</strong>` （強調）

---

## 3. C-3 関連の深い科目との接続（connections）

**sec-icon**: ❀

```html
<div class="cross-grid">
  <div class="cross-card">
    <h4><span class="cc-label">刑法各論</span>欺罔行為の重要事項基準</h4>
    <div class="cc-row"><span class="cc-key">共通点</span>...</div>
    <div class="cc-row"><span class="cc-key">相違点</span>...</div>
    <div class="cc-row"><span class="cc-key">関連条文・判例</span><a class="ref-stat" href="#law-246">246条1項</a>／<a class="ref-case" href="#case-...">最決平22.7.29</a></div>
  </div>
  ... (繰り返し N 枚)
</div>
```

要素：
- `<div class="cross-grid">` グリッドコンテナ
- `<div class="cross-card">` × N（5 枚程度）
- 各カード:
  - `<h4>`: `<span class="cc-label">` 分野ラベル + タイトルテキスト
  - `<div class="cc-row">` × M: `<span class="cc-key">` キー名 + 本文 HTML
- リンク: `<a class="ref-stat">`（条文）`<a class="ref-case">`（判例）

---

## 4. C-4 学説対立（doctrines, optional）

**sec-icon**: ⚔

複数の `<h3>`（① ② ③ ... ⑤）+ それぞれに cmp-table-wrap：

```html
<h3>① 欺罔行為の「重要事項」性──搭乗券詐欺（記述1）</h3>
<div class="cmp-table-wrap">
  <table>
    <thead><tr><th>学説</th><th>結論</th><th>論拠</th></tr></thead>
    <tbody>
      <tr class="row-key"><td><strong>重要事項基準説（判例・通説）</strong></td><td><span class="ok-cell">1項詐欺成立</span></td><td>...</td></tr>
      <tr><td>契約履行抗弁説</td><td><span class="ng-cell">不成立</span></td><td>...</td></tr>
    </tbody>
  </table>
</div>
```

各論点 = 1 つの「学説対立テーブル」。`row-key` で判例・通説をハイライト。

---

## 5. C-5 総合フローチャート（flowchart）

**sec-icon**: 🗺

```html
<div class="key-phrase-box">
  <span class="kp-strong">詐欺罪の成否5段階判定</span>──...
</div>

<div class="figure-wrap">
  <svg viewBox="0 0 720 700" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <marker id="arr5" ...><polygon .../></marker>
      <linearGradient id="step5" ...><stop ...><stop ...></linearGradient>
    </defs>
    <rect class="stepbox" x="180" y="20" width="360" height="80" rx="6"/>
    <text class="stepnum" x="200" y="44">STEP 1</text>
    <text class="steptitle" x="200" y="64">...</text>
    <text class="stepdesc" x="200" y="84">...</text>
    <line class="arrow" x1="360" y1="100" x2="360" y2="125"/>
    ... (STEP 1〜5 ボックス + 矢印)
  </svg>
  <p class="figure-caption">図：...</p>
</div>

<h3>運用上の鉄則</h3>
<ul class="lead-list">
  <li><strong>STEP 1 で「重要事項性」 を判定</strong>...<span class="exam-mark freq-mid">...</span></li>
  ... (STEP 1〜5)
</ul>
```

要素：
- `<div class="key-phrase-box">` イントロ
- `<div class="figure-wrap">` 内に `<svg>` フローチャート（任意ジオメトリ、SVG 全体を raw HTML として保持）+ `<p class="figure-caption">`
- `<h3>運用上の鉄則</h3>` + `<ul class="lead-list">` リスト

SVG は問題ごとに座標・本数が異なるため **構造化困難 → raw HTML フィールド推奨**。

---

## 6. C-6 関連問題・出題傾向（related_problems, optional）

**sec-icon**: 📚

```html
<h3>出題傾向の分析</h3>
<ul class="lead-list">
  <li><strong>「重要事項基準」は短答・論文両方で頻出</strong>搭乗券詐欺...</li>
  ...
</ul>

<h3>関連問題・参考</h3>
<ul class="lead-list">
  <li><strong>司H26-13</strong>搭乗券詐欺・なりすまし系欺罔──...</li>
  ...
</ul>
```

要素：
- 2 つの `<h3>` セクション
- 各 `<ul class="lead-list">` 内に `<li>` 複数（`<strong>` ラベル + 本文）

---

## 7. C-7 三層構造記憶（three_layer_memory）

**sec-icon**: 🧠

```html
<div class="key-phrase-box">
  <span class="kp-strong">本セクションは三層×5項目＝全15項目</span>──...
</div>

<h3>Priority A — 各記述の核心命題（試験直前必須・5項目）</h3>
<div class="memory-list">
  <div class="memory-item priority-a">
    <span class="priority-badge priority-a">A1</span>
    <div class="mem-body">
      <span class="mem-title">記述1：搭乗券交付詐欺＝1項詐欺成立（重要事項基準）</span>
      他人を搭乗させる目的を秘して...
      <span class="mem-hint">▶ 判例：<a class="ref-case" href="#case-...">最決平22.7.29</a> ／ 該当記述：<a href="#choice-1">記述1（正しい）</a></span>
    </div>
  </div>
  ... (5 件)
</div>

<h3>Priority B — 詐欺罪体系の柱（週次サイクル・5項目）</h3>
<div class="memory-list">
  <div class="memory-item priority-b">
    <span class="priority-badge priority-b">B1</span>
    ...
  </div>
  ... (5 件)
</div>

<h3>Priority S — 補強・関連知識（直前2週間・5項目）</h3>
<div class="memory-list">
  <div class="memory-item priority-c">
    <span class="priority-badge priority-c">S1</span>
    ...
  </div>
  ... (5 件)
</div>

<!-- §22-bis: C-7 末尾配置 final-answer -->
<div class="final-answer" hidden>
  <h3>🎯 正解</h3>
  <span class="answer-num">5</span>
  <p class="fa-summary"><strong>一文要約</strong>　<span class="ron-mark freq-high">...</span></p>
  <p>本問は...</p>
</div>
```

要素：
- イントロ `<div class="key-phrase-box">`
- 3 層（A / B / S）× 5 項目 = 計 15 メモリーアイテム
- 各 `<div class="memory-list">` 配下に `<div class="memory-item priority-{a|b|c}">` × N
- メモリーアイテム:
  - `<span class="priority-badge priority-{a|b|c}">A1</span>` バッジ
  - `<div class="mem-body">`:
    - `<span class="mem-title">タイトル</span>`
    - 本文 HTML（inline `<strong>`、`<a class="ref-stat">` 等）
    - `<span class="mem-hint">▶ ヒント・判例参照</span>`
- 末尾 `<div class="final-answer" hidden>` ※KTX301 canon 互換（C-7 末尾配置）

**注**: 既存 14 件 (KEI 326-330, 303-305, 他 5 科目 001) も C-7 直前の basis セクション内に final-answer を持つため、C-7 末尾 final-answer は 刑TX300 固有実装。Phase 2 では C-7 のメモリーアイテム部分のみ slot 化し、final-answer は別経路（A-3 basis 内）の既存配置を維持。

---

## 8. 主要 CSS クラス一覧（PART C 固有）

| クラス | 用途 |
|---|---|
| `cmp-table-wrap` | 比較テーブルのラッパー（横スクロール許容） |
| `key-phrase-box` | 重要フレーズ強調ボックス |
| `kp-strong` | key-phrase-box 内の太字 inline |
| `case-emphasis` `freq-high/mid/low` | 判例・結論の強調 + 頻度マーカー |
| `row-key` | テーブル行ハイライト（判例・通説・正解行） |
| `ok-cell` / `ng-cell` | ○/× セル |
| `cross-grid` | C-3 横断科目グリッドコンテナ |
| `cross-card` | C-3 接続カード |
| `cc-label` / `cc-key` | C-3 ラベル・キー |
| `cc-row` | C-3 行 |
| `figure-wrap` / `figure-caption` | C-5 SVG ラッパー |
| `lead-list` | C-5/C-6 リード型 ul |
| `exam-mark` `freq-mid` 等 | 試験出題マーカー |
| `memory-list` | C-7 メモリーリスト |
| `memory-item` `priority-a/b/c` | C-7 個別メモリーアイテム |
| `priority-badge` `priority-a/b/c` | C-7 優先度バッジ |
| `mem-body` / `mem-title` / `mem-hint` | C-7 メモリー内部要素 |
| `ref-case` / `ref-stat` | 判例・条文リンク（既存・PART B でも使用） |

---

## 9. Phase 2 schema 設計方針

| セクション | フィールド名 | 必須/任意 | 設計方針 |
|---|---|---|---|
| C-1 | `systematic` | optional | 構造化 (title_suffix, intro key-phrase, summary, table, footer) |
| C-2 | `comparison` | optional | tables 配列（各テーブル独立） |
| C-3 | `connections` | optional | cards 配列（各 cross-card 構造化） |
| C-4 | `doctrines` | optional | topics 配列（各 ①②③ 学説対立を構造化） |
| C-5 | `flowchart` | optional | intro_box_html + svg_html (raw) + rules リスト |
| C-6 | `related_problems` | optional | trends + related の 2 リスト |
| C-7 | `three_layer_memory` | optional | intro_box_html + layers 配列（A/B/S）× items 配列 |

すべて `optional`。各セクションが個別に missing 可能（一部のみ実装も許容）。

**inline HTML 許容方針**: `<strong>` `<br>` `<span class="kp-strong">` `<span class="case-emphasis">` `<a class="ref-case/ref-stat">` 等の inline span/anchor は本文文字列内に raw HTML として埋込許可。`html.escape` は **適用しない**（既存運用との整合）。代わりに JSON 作成者の責任で安全な HTML 断片に限定する。

**SVG 等の任意ジオメトリ HTML**: 1 フィールドに raw HTML 文字列として格納（例: `flowchart.svg_html`）。
