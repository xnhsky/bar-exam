# TX v8.11.4 規律本体（core spec）

**KTX301-canonical · readability-enhanced · hanging-indent-grid · spoiler-safe · a2-two-stage-reveal · a2-multi-ox-support · spoiler-leak-eradication · lessons-from-chat-002-and-006**

司法試験・予備試験 短答式（短答 = Tantō = TX）対策の単問解説 HTML 生成仕様。  
全 7 法（憲法／民法／刑法／商法／民訴／刑訴／行政法）共通の汎用シリーズ名は **TX**。

科目別ファイル接頭辞：**KEN**(憲法)／**MIN**(民法)／**K**(刑法)／**SYO**(商法)／**MINS**(民訴)／**KEIS**(刑訴)／**GSE**(行政法)

> **本ファイルは規律本体のみ**。canonical コード（CSS・HTML骨格・JS）は以下の別ファイルを参照：
> - `spec/tx-v8.11.4-annex-A.css`（canonical CSS · 既定 P1 ローズシャンブル）
> - `spec/tx-v8.11.4-annex-A-bis-2.css`（P2 セージブラリー override · 末尾追記用）
> - `spec/tx-v8.11.4-annex-A-bis-3.css`（P3 ラベンダードーン override · 末尾追記用）
> - `spec/tx-v8.11.4-annex-B.html`（canonical body skeleton template）
> - `spec/tx-v8.11.4-annex-C.js`（canonical JS）
> - `canonical/KTX301.html`（canonical 実装例。byte-level 正典）

## §0-prime. v8.11.3 → v8.11.4 差分

### v8.11.4 改訂 4 項目（spoiler-leak-eradication）

1. **PART A 内の「N（XX）正解」リテラル完全消去**（AP-36）:組合せ型問題の選択肢列挙で `<strong>N（XX）正解</strong>` 形式の文字列が混入する深刻なネタバレ症状を恒久排除。HTML レベルで `<strong>4（ウエ）正解</strong>` 等を `<strong>4（ウエ）</strong>` に強制変換。S74 で検出。

2. **data-explanation 属性内の正解値先頭リテラル消去**（AP-37）:`data-explanation="3,4。詐欺罪は..."` のような先頭の正解値表示を恒久排除。属性内容を文末解説のみに統一。ページソース表示やデバッグ時のネタバレを完全防止。S74 拡張で検出。

3. **FA `.answer-num` を正解の数字のみ表示**（AP-38 / canonical 強化）:
   - single: `<span class="answer-num">N</span>`（変更なし）
   - multi: `<div class="answer-num answer-num-multi"><span class="ans-cell ans-correct">3</span><span class="ans-cell ans-correct">4</span></div>` — **正解の数字のみ表示。不正解の数字は表示しない**
   - ox-grid: `<div class="answer-num answer-num-multi"><span class="ans-cell ans-correct">ア</span>...</div>` — **正(1)と判定された記述ラベルのみ表示。誤(2)は表示しない**

4. **AP-36 / AP-37 / AP-38 / S74 / S75 / K302-21 追加**:ネタバレ症状の恒久カタログ化。

### v8.11.3 までの差分（既存・継承）

3 Type 対応 (single/multi/ox-grid)、a2-two-stage-reveal、spoiler-safe (final-answer hidden)、multi-answer-css、§22-quater/§22-quinta/§22-sexta、AP-26〜AP-35、S64〜S73、K302-17/18/19/20 は完全継承。

### v8.11.3 → v8.11.4 minor 更新ルート

既存 v8.11.3 ファイルは §34-sexies 5 ステップで minor 更新可能。

---

## §0-prime-prev4. v8.11.2 → v8.11.3 差分（履歴・参考）

### v8.11.3 改訂 4 項目

1. **A-2 解答エリア 3 Type 完全対応**:`data-answer-type` 属性で分岐
   - `"single"` (単一選択): `data-correct-value="3"` 等。既存 v8.11.2 と同等
   - `"multi"` (複数選択): `data-correct-value="1,2"` 等。カンマ区切りで複数値、集合一致判定
   - `"ox-grid"` (○×評価): `data-correct-value="11112"` 等。各記述に 1(正) or 2(誤) を判定、5桁文字列で連結比較

2. **Type B (multi): selection-counter UI + FIFO トグル**:選択肢クリックでトグル、最大数 (正解数) 到達後の追加クリックは FIFO で最古を解除。「選択中: N / M 個」のカウンター表示。M 個揃ったら reveal-answer-btn 有効化。

3. **Type C (ox-grid): `.answer-ox-grid` + `.ox-row` UI 新設**:各記述に対して 「1（正）」「2（誤）」の 2 ボタン行を生成。`data-ox-labels` 属性で記述ラベル指定可(デフォルト: ア・イ・ウ・エ・オ)。全行で選択完了したら reveal-answer-btn 有効化。

4. **§Annex A に §22-sexta CSS パッチ追加**:`.answer-area[data-answer-type="multi"]` 関連と `.answer-ox-grid` / `.ox-row` / `.ox-label` / `.ox-btn` 関連の規則。§22-quinta の直後・§23 cross-grid の直前。

### Type 自動判定ロジック

| `data-correct-value` パターン | 判定される type | 例 |
|---|---|---|
| `^\d+$` で 1 桁または 2 桁以上 (1, 2 以外を含む) | `single` | "3", "5", "10" |
| `^[12]{2,}$` (2 桁以上で各桁が 1 or 2) | `ox-grid` | "11112", "22122" |
| `^\d+(,\d+)+$` (カンマ区切り) | `multi` | "1,2", "3,4" |

### v8.11.2 までの差分（既存・継承）

a2-two-stage-reveal (選択 stage → reveal stage の分離)、spoiler-safe (final-answer hidden)、multi-answer-css、§22-quater/§22-quinta、AP-26〜AP-34、S64〜S72、K302-17/18/19 は完全継承。

### v8.11.2 → v8.11.3 minor 更新ルート

既存 v8.11.2 ファイルは §34-quinquies 5 ステップで minor 更新可能。

---

## §0-prime-prev3. v8.11.1 → v8.11.2 差分（履歴・参考）

### v8.11.2 改訂 4 項目

1. **A-2 解答エリア 2 段階開示プロトコル確立**（a2-two-stage-reveal）:選択肢クリック → 選択状態のハイライトのみ表示。「解答を表示」ボタンクリック → 正解/不正解と正解値のみ表示。詳細解説は PART B sub-card.explanation と巻末 FINAL ANSWER に統合し、A-2 では一切表示しない。

2. **answer-instruction canonical 文言の強制統一**:`<p class="answer-instruction">` の内容は「選択肢を選んで「解答を表示」を押してください。」固定。問題ごとのカスタム文言・正解値リテラル・解説テキスト等を絶対に含めない（AP-33）。

3. **§Annex A に §22-quinta CSS パッチ追加**:`.reveal-answer-btn` + `.answer-slot.selected` の 4 規則を §22-quater の直後・§23 cross-grid の直前に逐語追加。`spec/tx-v8.11.4-annex-A.css` を canonical 化。

4. **§Annex C JS に handleRevealAnswerBtn 新設・handleAnswerSlot 改訂**:選択 stage と reveal stage を分離。stage 1 は選択ハイライトのみ、stage 2 で初めて正誤判定と正解値を開示。詳細解説は表示しない。

### v8.11.1 までの差分（既存・継承）

KTX301 canonical 移行・§24 readability layer・A-3 PART B 後再配置・font-weight 強化・§24-6 hanging-grid・spoiler-safe（巻末 FINAL ANSWER hidden）・multi-answer-css・§22-quater・AP-26〜AP-32・S64〜S70・K302-17/18 は完全継承。

### v8.11.1 → v8.11.2 minor 更新ルート

既存 v8.11.1 ファイルは §34-quater 5 ステップで minor 更新可能。

---

## §0-prime-prev2. v8.11.0 → v8.11.1 差分（履歴・参考）

### v8.11.1 改訂 3 項目

1. **spoiler-safe canonical 確立**:すべての `<div class="final-answer">` に `hidden` 属性を必須化。`spec/tx-v8.11.4-annex-C.js` の `revealFinalAnswer()` は v8.7 以来存在するが、対応する HTML 側 `hidden` 初期宣言が欠落しており JS reveal が実質 no-op となっていた canonical 欠陥を修復。`spec/tx-v8.11.4-annex-A.css` に `.final-answer[hidden]{display:none !important}` ＋ reveal アニメーション規則を追加

2. **§22-ter answer-num-multi CSS の §Annex A 組込み**:v8.11.0 で HTML canonical のみ定義されていた `.answer-num.answer-num-multi` / `.ans-cell` / `.ans-stmt` / `.ans-val` の 5 規則を `spec/tx-v8.11.4-annex-A.css` の §22 final-answer 直後・§23 cross-grid 直前に逐語追加。P2 セージブラリー・P3 ラベンダードーンで多解答セルが背景と同化する現象を恒久解消

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
4. §31 S1〜S75 の自己検証（`scripts/validate.py` 実行）
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

1. §Annex B-link の Google Fonts `<link>` タグ（`spec/tx-v8.11.4-annex-B.html` 冒頭コメント参照）
2. `spec/tx-v8.11.4-annex-A.css` 全文
3. `spec/tx-v8.11.4-annex-B.html` の body skeleton
4. `spec/tx-v8.11.4-annex-C.js` 全文

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
| 40〜60% | P2 セージブラリー | `spec/tx-v8.11.4-annex-A-bis-2.css` の `:root{}` ブロックを `<style>` 末尾に追記 |
| < 40% | P3 ラベンダードーン | `spec/tx-v8.11.4-annex-A-bis-3.css` の `:root{}` ブロックを `<style>` 末尾に追記 |

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

`scripts/validate.py` を実行し、S1〜S75 全件通過を確認。違反があれば修正してから配信。

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
13. **`scripts/validate.py` で S1〜S75 自己検証** → 全件通過後に配信

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

### §17-2. answer-area 必須属性（v8.11.3 改訂・3 Type 対応）

**Type A (single) - 単一選択型** — 既定:

```html
<div class="answer-area"
     data-correct-value="N"
     data-explanation="(任意・参考用、A-2 では表示されない)">
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


**Type B (multi) - 複数選択型** — カンマ区切り正解値:

```html
<div class="answer-area"
     data-correct-value="1,2"
     data-answer-type="multi"
     data-explanation="(任意・参考用)">
  <h3>誤っている記述を2個クリック</h3>
  <p class="answer-instruction">選択肢を2個選んで「解答を表示」を押してください。</p>
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

**Type C (ox-grid) - ○×評価型** — 各記述に 1(正)/2(誤) を判定:

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
    <!-- イ・ウ・エ・オ も同様 (合計 N 行 = 正解値の桁数) -->
  </div>
  <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>
  <div id="answer-feedback" hidden></div>
</div>
```

**v8.11.3 必須要件 (3 Type 共通):**
- `<p class="answer-instruction">` の内容は **`選択肢を選んで「解答を表示」を押してください。` 固定**（AP-33 違反禁止）
- `<button class="reveal-answer-btn" type="button" disabled>` 必須
- `data-explanation` は属性として保持可（A-2 では表示しないが、デバッグ・将来拡張用）
- 詳細解説は PART B sub-card.explanation と巻末 FINAL ANSWER に統合

**禁止事項:**
- `<div class="answer-slot">` ← `<button>` 必須
- `<div id="answer-feedback" hidden style="...">` ← inline style 一切なし
- `data-correct-value` 属性の省略
- HTML 側に長文 innerHTML テンプレートをハードコード
- **`<p class="answer-instruction">` 内に正解値リテラル・解説テキストを記述すること（v8.11.2 / AP-33）**
- **`<button class="reveal-answer-btn">` の欠落（v8.11.2 / AP-34）**

---

## §17-3. A-2 2 段階開示プロトコル（v8.11.2 新規・a2-two-stage-reveal canonical）

A-2 解答エリアの操作は厳格な 2 段階で構成される:

**Stage 1 — 選択:** ユーザーが選択肢ボタン (`.answer-slot`) をクリック
- 選択された選択肢に `.selected` クラスが付与され、ハイライト表示
- 他の選択肢の `.selected` クラスは外される
- フィードバック (`#answer-feedback`) は **絶対に表示されない**
- 正解/不正解の判定は **行われない**
- 「解答を表示」ボタン (`.reveal-answer-btn`) の `disabled` 属性が外れて有効化

**Stage 2 — 開示:** ユーザーが「解答を表示」ボタンをクリック
- 全選択肢が `disabled` 化、正解選択肢に `.correct-mark`、不正解選択時はユーザー選択に `.incorrect-mark` 付与
- `#answer-feedback` が `hidden:false` で開示され、以下のいずれかが表示:
  - 正解: `<strong class="fb-verdict fb-correct">✓ 正解</strong>` のみ
  - 不正解: `<strong class="fb-verdict fb-incorrect">✗ 不正解</strong>　正解は<span class="fb-answer">N</span>` のみ
- **詳細解説は絶対に表示しない**（PART B sub-card.explanation と巻末 FINAL ANSWER で代替）
- `.answer-area` に `.answered` クラスが付与され、以降の操作を無効化
- 巻末 FINAL ANSWER の `hidden` も同時に外される（`revealFinalAnswer()` 連動）

**設計理念:**
- 自答 → 確認 → 詳細学習のサイクルを厳格に分離
- A-2 ではあくまで「自答の結果が合っているか」のみを確認
- 詳細な判例・解説・論点は能動的にスクロール（PART B）またはクリック（FINAL ANSWER）で参照


---

## §17-4. A-2 ○×評価グリッド プロトコル（v8.11.3 新規・ox-grid canonical）

`data-answer-type="ox-grid"` 時の専用 UI 規律。

**HTML 構造:**
- `<div class="answer-ox-grid">` をラッパーとし、各記述ごとに `<div class="ox-row" data-pos="N">` を 1 行ずつ配置
- 各 `.ox-row` 内には `<span class="ox-label">{記述ラベル}</span>` と `<div class="ox-btn-group">` を配置
- `.ox-btn-group` 内には `<button class="ox-btn" data-value="1">1（正）</button>` と `<button class="ox-btn" data-value="2">2（誤）</button>` の 2 ボタン
- ラベルは ア・イ・ウ・エ・オ がデフォルト。問題の指示に応じて ①・②・③… や a・b・c… も使用可

**操作プロトコル:**
- Stage 1: 各 ox-row で 1 ボタン選択(行内で他は自動解除)。全行揃うまで reveal-answer-btn は無効
- Stage 2: 「解答を表示」クリックで全行の選択値を結合(例: ア=1, イ=1, ウ=1, エ=1, オ=2 → "11112")、`data-correct-value` と一致比較。一致でも不一致でも、各 ox-btn に `.correct-mark` / `.incorrect-mark` クラスを付与してマーク表示

**正解値の格納:**
- `data-correct-value="11112"` のように N 桁の文字列。各桁が 1(正) or 2(誤) のみ
- 桁数 = ox-row 数 = 記述数



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
- **§22-quater-3**: `spec/tx-v8.11.4-annex-A.css` に CSS パッチ正典組込み（§22-bis fa-summary 直後・§23 cross-grid 直前）。`.answer-num.answer-num-multi` / `.ans-cell` / `.ans-correct` / `.ans-incorrect` / `.ans-stmt` / `.ans-val` / `.final-answer[hidden]` / `@keyframes faReveal` の 8 規則
- **§22-quater-4**: `spec/tx-v8.11.4-annex-C.js` の `revealFinalAnswer()` は変更なし（v8.7 以来既存）


### §22-quinta. A-2 reveal-answer-btn + answer-slot.selected canonical（v8.11.2 新規）

`spec/tx-v8.11.4-annex-A.css` に CSS パッチ正典組込み（§22-quater の直後・§23 cross-grid の直前）:

- `.reveal-answer-btn` — グラデーション + 影 + hover アニメーション、disabled 状態は opacity .42
- `.reveal-answer-btn:hover:not(:disabled)` — translateY(-1px) で浮上
- `.reveal-answer-btn:active:not(:disabled)` — translateY(0) で押下感
- `.reveal-answer-btn:disabled` — opacity .42 / cursor:not-allowed / box-shadow なし
- `.answer-slot.selected` — accent-soft 背景 + accent ボーダー + box-shadow による選択枠ハイライト

§Annex C JS:
- `handleAnswerSlot(btn)` — stage 1: 選択ハイライトのみ、reveal-answer-btn 有効化
- `handleRevealAnswerBtn(btn)` — stage 2: 正誤判定 + 正解値開示、`revealFinalAnswer()` 連動
- クリック委譲に `var rb = t.closest('.reveal-answer-btn'); if (rb) { handleRevealAnswerBtn(rb); return; }` を追加


### §22-sexta. A-2 multi-select + ox-grid canonical（v8.11.3 新規）

`spec/tx-v8.11.4-annex-A.css` に §22-quinta の直後・§23 cross-grid の直前に CSS パッチ追加:

- `.answer-area[data-answer-type="multi"] .answer-row` — counter 配置のための position:relative
- `.selection-counter` — 「選択中: N / M 個」表示用、accent カラーの小フォント
- `.answer-ox-grid` — flex 縦並びコンテナ、gap:10px
- `.ox-row` — 各記述行、accent ホバー
- `.ox-label` — 記述ラベル (ア/イ/ウ/エ/オ 等)、accent 太字
- `.ox-stmt` — 任意の記述文配置用 (現状未使用、将来拡張用)
- `.ox-btn-group` — 1/2 ボタンの flex inline コンテナ
- `.ox-btn` — 1(正)/2(誤) ボタン、selected/correct-mark/incorrect-mark 状態あり

§Annex C JS の改訂:
- `getAnswerType(area)` 新設 — data-answer-type 取得
- `updateRevealBtnState(area)` 新設 — Type 別の有効化判定 + counter 更新
- `handleAnswerSlot(btn)` 拡張 — Type B (multi) で FIFO トグル
- `handleOxBtn(btn)` 新設 — ox-row 内の単一選択
- `handleRevealAnswerBtn(btn)` 拡張 — Type 別に判定ロジック分岐
- クリック委譲に `.ox-btn` ハンドラ追加


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

## §31. SEVERE 自己検証 S1〜S75

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
- **S71（v8.11.2 新規）**：`<p class="answer-instruction">` 内に正解値リテラル不存在・canonical 文言固定（AP-33 検出）
- **S72（v8.11.2 新規）**：A-2 解答エリアに `<button class="reveal-answer-btn">` 存在（AP-34 検出）

---

## §32. 3 パターン色変換ルール

| パターン | 正答率帯 | 名称 | 処理 |
|:-:|:-:|:--|:--|
| **P1** | ≥ 60% | ローズシャンブル | annex-A.css 既定値そのまま使用。**override 追記不要** |
| **P2** | 40〜60% | セージブラリー | annex-A-bis-2.css の `:root{}` ブロックを `<style>` 末尾に追記 |
| **P3** | < 40% | ラベンダードーン | annex-A-bis-3.css の `:root{}` ブロックを `<style>` 末尾に追記 |

> **P1 absolute canon 鉄則**：P1 ファイルと P2/P3 ファイルを diff した際、差分は `:root{}` 27 行ブロックのみ（footer-spec のパレット名表記を除く）。

---

---

## §34-quater. v8.11.1 → v8.11.2 minor 更新 5 ステップ

v8.11.1 で生成済みの既存ファイルは §0-tri ゼロベース再構築を経ずに、以下 5 ステップのみで v8.11.2 化可能。

**STEP 1**: `<p class="answer-instruction">...</p>` の内容を「選択肢を選んで「解答を表示」を押してください。」固定文に強制統一（AP-33 解消）。

**STEP 2**: `<div class="answer-area">` 内の `<div id="answer-feedback"` の直前に `<button class="reveal-answer-btn" type="button" disabled>解答を表示</button>` を挿入（AP-34 解消）。

**STEP 3**: `<style>` ブロック内、§22-quater の直後・§23 cross-grid の直前に §22-quinta CSS パッチを逐語追加（`.reveal-answer-btn` / `.reveal-answer-btn:hover:not(:disabled)` / `.reveal-answer-btn:active:not(:disabled)` / `.reveal-answer-btn:disabled` / `.answer-slot.selected` の 5 規則）。

**STEP 4**: `<script>` ブロック内の `handleAnswerSlot` 関数全体を新仕様（stage 1: 選択ハイライトのみ）に置換 + `handleRevealAnswerBtn` 関数を新設（stage 2: 正誤判定+正解値開示）+ クリック委譲に `.reveal-answer-btn` 分岐を追加。

**STEP 5**: footer-spec の `TX v8.11.1` → `TX v8.11.2` 置換、`a2-two-stage-reveal` feature-tag を追加。S71/S72 検証通過を確認。

---

## §34-quinquies. v8.11.2 → v8.11.3 minor 更新 5 ステップ

v8.11.2 で生成済みの既存ファイルは §0-tri ゼロベース再構築を経ずに、以下 5 ステップで v8.11.3 化可能。

**STEP 1**: `data-correct-value` 属性値から Type を自動判定し、`<div class="answer-area">` 開始タグに `data-answer-type="single|multi|ox-grid"` を追加。

**STEP 2**: Type B (multi) の場合、`<p class="answer-instruction">` 文言を「選択肢を{N}個選んで「解答を表示」を押してください。」に変更し、`<div class="answer-row">` の直後に `<p class="selection-counter">選択中: 0 / {N} 個</p>` を挿入。

**STEP 3**: Type C (ox-grid) の場合、`<div class="answer-row">...</div>` を `<div class="answer-ox-grid">` 構造に置換({N} 個の `.ox-row` を生成)。`<p class="answer-instruction">` 文言を「各記述に「1（正）」または「2（誤）」を選んで「解答を表示」を押してください。」に変更。`<h3>` を「各記述に正誤を判定」に変更。

**STEP 4**: `<style>` ブロックの §22-quinta 直後・§23 cross-grid 直前に §22-sexta CSS パッチを逐語追加。`<script>` ブロックの `handleAnswerSlot` / `handleRevealAnswerBtn` を新仕様(Type 別分岐)に置換、`handleOxBtn` / `getAnswerType` / `updateRevealBtnState` 関数を新設、クリック委譲に `.ox-btn` 分岐を追加。

**STEP 5**: footer-spec の `TX v8.11.2` → `TX v8.11.3` 置換、`a2-multi-ox-support` feature-tag を追加。S71/S72/S73 検証通過を確認。

---

## §34-sexies. v8.11.3 → v8.11.4 minor 更新 5 ステップ

v8.11.3 で生成済みの既存ファイルは §0-tri ゼロベース再構築を経ずに、以下 5 ステップで v8.11.4 化可能。

**STEP 1**: PART A `<section id="problem-text">` 内の `<strong>N（XX）正解</strong>` 形式を全て `<strong>N（XX）</strong>` に置換（AP-36 解消）。strong タグなしの「N（XX）正解」も同様に「正解」リテラルを削除。

**STEP 2**: `data-explanation="..."` 属性の値の先頭から、正解値リテラル（`3,4。`、`11122（ア1・イ1・...）。`、`3。`、`4（ウ・エ）。` 等）を句点まで削除（AP-37 解消）。

**STEP 3**: FA `.answer-num` を Type に応じて正解の数字のみ表示する形式に変換（AP-38 解消）:
- single: `<span class="answer-num">N</span>`（変更なし）
- multi: `<div class="answer-num answer-num-multi">` + `<span class="ans-cell ans-correct">N</span>` のみ（正解の数字数だけセルを生成、不正解の `ans-incorrect` セルは生成しない）
- ox-grid: `<div class="answer-num answer-num-multi">` + `<span class="ans-cell ans-correct">ラベル</span>` のみ（data-correct-value の '1' 桁に対応するラベルのみセル化、'2' 桁の記述はスキップ）

**STEP 4**: footer-spec の `TX v8.11.3` → `TX v8.11.4` 置換、`spoiler-leak-eradication` feature-tag を追加。

**STEP 5**: S74/S75 検証通過を確認。

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

## §36. v8.11.4 core invariant

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
