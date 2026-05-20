# KTX_template.html slotmap

`canonical/KTX301.html`（3743 行）を `templates/KTX_template.html` にテンプレ化する際の slot 設計。
**Step 3 承認待ち**。承認後に Step 4（KTX_template.html 生成）に進む。

---

## 0. 重大な構造的ギャップ（先に判断を仰ぐ）

### Gap-A. PART A の出題形式が canonical (KTX301) と 326 で異なる

| 項目 | KTX301 | 326 |
|---|---|---|
| `instruction_type` | (組合せ型 5択) | `ox-grid-5` |
| 設問構造 | 「アからオの記述を結論Ⅰ/Ⅱ/Ⅲと組合せ、正しい肢を1〜5から選ぶ」 | 「アからオの各記述を ○× 判定」 |
| canonical 該当行 | L2070-2112（【記述】＋【結論】basis-card＋【選択肢】table） | — |
| 解答 UI | `data-answer-type="single"` の 1〜5 ボタン (L2118-2133) | `data-answer-type="ox-grid"` の ox-row × 5 が必要 |

**判断選択肢**：

- **(A)** PART A を **ox-grid-5 形式に書き直す**（326 互換、KTX301 固有の「結論Ⅰ/Ⅱ/Ⅲ＋組合せ table」は捨てる）
- **(B)** KTX301 の組合せ型構造のまま残し、ox-grid-5 問題用の分岐は **将来の拡張**（このテンプレでは 326 を render できない＝ Step 5/6 失敗確実）
- **(C)** instruction_type で 2 形式分岐するテンプレを 1 ファイルに同居させる（CSS/JS で切替）

**推奨：(A)**。テンプレは ox-grid-5 を主構造とし、組合せ型は将来別テンプレ（あるいは override slot）で対応。canonical KTX301 が組合せ型なのは「構造の参考例」だが、Step 5 で 326 を試走する以上、構造は 326 互換が必須。

### Gap-B. A-3 / PART C / PART D の内容は JSON 未供給

| section | canonical 行範囲 | 内容 | JSON 対応フィールド |
|---|---|---|---|
| A-3 共通根拠条文・判例 | L2518-2669 | 条文 6本（246/247/249/253/109/148）＋判例 5本 | **無し** |
| PART C 体系・記憶 (C-1〜C-7) | L2671-3047 | 体系解説、比較表、学説対立、フローチャート、関連問題、三層記憶 | **無し** |
| PART D ARENA | L3049-3317 | 12 問の ○× ドリル | **無し** |

`render.py` は未定義 slot を 1 つでも残したら FAIL する。よって：

- canonical の詐欺罪本文を **そのまま流用** → PATCH §1 禁則違反、validate_content で fail
- 細粒度 slot 化（各条文・各 drill を個別 slot に）→ JSON schema 拡張必須
- 単一の大型 slot（`{{A3_BASIS_HTML}}` 等）→ JSON schema 拡張必須
- **スタブ化**（HTML コメントのプレースホルダ）→ 当面 render は通るが、A-3/C/D は空のまま

**推奨：スタブ化 (D)**。A-3/PART C/PART D は「TODO」コメント＋最小骨格のみ残し、内部 slot は置かない。

これにより：
- render.py：未定義 slot なしで通る
- validate_structure.py：骨格があれば通る（S77 群はまだ未確認だが、骨格保持で対処可能）
- validate_content.py：詐欺罪固有語が出現しないので negative check 通過、positive check も 326.json の値が PART A〜PART B に出るので通過

A-3/C/D の本格生成は **フェーズ 2**（JSON schema 拡張と並行）として分離。

### Gap-C. canonical 固有メタ（KTX301）

| 行 | 内容 | 扱い |
|---|---|---|
| L6 | `<title>KTX301 - 詐欺罪と他罪の成否（司法試験R1-16）</title>` | slot 化（`{{PROBLEM_ID}}` + `{{CRIME}}` + `{{SOURCE_ID}}`） |
| L2015 | `<div class="doc-header">KTX301</div>` | slot 化（`刑TX{{PROBLEM_ID}}`） |
| L2017-2020 | exam-badge 4 件（刑法／司法試験／令和元年／第16問） | slot 化（科目固定で「刑法」、年度・問番号は `{{SOURCE_ID}}` 由来） |
| L2022 | `<h1>No.301 ── 詐欺罪と他罪の成否（司法試験R1-16）</h1>` | slot 化 |
| L2024-2031 | theme-tags 8 件（詐欺罪/背任罪/恐喝罪…） | スタブ（`{{CRIME}}` のみ表示／JSON 拡張で複数対応） |
| L2034-2036 | exam-meta（正答率65%／難度／パターン） | slot 化 |
| L2038-2050 | toc-row（A/B/C/D 各リンク） | byte-level 一致（変動なし） |
| L3322-3347 | footer-spec（正答率/パターン/feature-tag列） | slot 化（meta部分のみ） |

---

## 1. 行番号 → slot 名 → 元テキスト抜粋

### §1.1 HEAD/メタ

| 行 | slot | canonical 元テキスト抜粋 |
|---:|---|---|
| 6 | `{{PROBLEM_ID}}` / `{{CRIME}}` / `{{SOURCE_ID}}` | `<title>KTX301 - 詐欺罪と他罪の成否（司法試験R1-16）</title>` → `<title>刑TX{{PROBLEM_ID}} - {{CRIME}}（{{SOURCE_ID}}）</title>` |

### §1.2 HEADER

| 行 | slot | canonical 元テキスト抜粋 |
|---:|---|---|
| 2015 | `{{PROBLEM_ID}}` | `<div class="doc-header">KTX301</div>` → `<div class="doc-header">刑TX{{PROBLEM_ID}}</div>` |
| 2017 | 固定 | `<span class="exam-badge">📚 刑法</span>` （刑法シリーズ固定） |
| 2018 | `{{EXAM_TYPE}}`（SOURCE_ID から派生 or 固定） | `<span class="exam-badge">📝 司法試験</span>` — H29-12 形式から司法/予備の判定が必要だがスタブで「短答」固定が安全 |
| 2019 | `{{ERA}}`（SOURCE_ID から派生） | `<span class="exam-badge">📅 令和元年</span>` — H29 → 平成29年への変換。**スタブ：`{{SOURCE_ID}}` を直挿入** |
| 2020 | `{{Q_NUM}}`（SOURCE_ID から派生） | `<span class="exam-badge">🔢 第16問</span>` — **スタブで省略 or `{{SOURCE_ID}}` の後半 (-12) を抽出** |
| 2022 | `{{PROBLEM_ID}}` / `{{CRIME}}` / `{{SOURCE_ID}}` | `<h1>No.301 ── 詐欺罪と他罪の成否（司法試験R1-16）</h1>` → `<h1>No.{{PROBLEM_ID}} ── {{CRIME}}（{{SOURCE_ID}}）</h1>` |
| 2024-2031 | 削除（または `{{CRIME}}` 1件のみ） | 詐欺罪固有の theme-tag 8 件（246条/247条/249条/253条/109条/148条2項/罪数論/実行の着手）— **削除推奨**。シリーズによっては `{{CRIME}}` のみ 1 件出す |
| 2034 | `{{CORRECT_RATE}}` | `<span><strong>正答率:</strong>65%</span>` → `<span><strong>正答率:</strong>{{CORRECT_RATE}}</span>` |
| 2035 | 削除（or `{{DIFFICULTY}}` スタブ） | `<span><strong>難度:</strong>★★☆</span>` — JSON に難度フィールド無し、削除推奨 |
| 2036 | `{{OVERRIDE_PATTERN}}` + `{{PATTERN_NAME}}` | `<span><strong>パターン:</strong>P1 ローズシャンブル</span>` — P1〜P5 → 色名のマップが必要。**スタブ：`P{{OVERRIDE_PATTERN}}`** |
| 2038-2050 | byte-level 一致 | toc-row 全体（A-1/A-2/choice-1〜5/basis/c-1/c-7/part-d）— 構造固定 |

### §1.3 marker-legend (L2053-2063)

byte-level 一致対象。slot なし。

### §1.4 PART A 問題情報 (L2065-2112)

**Gap-A の判断 (A) を前提とした ox-grid-5 構造への書き換え案**：

| 行（書換後） | slot | canonical 元テキスト抜粋 |
|---:|---|---|
| 2070 | (固定) | `<section class="section" id="part-a">` |
| 2071 | (固定) | `<nav class="sec-nav"><a href="#answer-area">↓解答</a><a href="#choice-1">↓記述ア</a></nav>` |
| 2072 | (固定) | `<h2 class="section-title"><span class="sec-icon">❀</span>A-1 問題文</h2>` |
| 2075 | `{{INSTRUCTION}}` | `次のアからオまでの各【記述】を判例の立場に従って検討した場合、後記の各【結論】との組合せとして正しいものは、後記1から5までのうちどれか。…` → `<p>{{INSTRUCTION}}</p>` |
| 2078-2086 (canonical) | 削除 | 【記述】見出し＋【結論】basis-card＋【選択肢】table（**組合せ型固有**、ox-grid-5 では不要） |
| 新規 | `{{CHOICE_A_LABEL}}` / `{{CHOICE_A_STEM}}` | `<div class="problem-text"><span class="choice-num-inline">{{CHOICE_A_LABEL}}</span>{{CHOICE_A_STEM}}</div>` |
| 新規 | `{{CHOICE_B_*}}〜{{CHOICE_E_*}}` 同様 | 5 行（ア〜オ） |

### §1.5 PART A-2 解答エリア (L2114-2136)

ox-grid-5 形式への書き換え：

| 行（書換後） | slot | canonical 元テキスト抜粋 / 書換 |
|---:|---|---|
| 2114 | (固定) | `<section class="section" id="answer-area">` |
| 2118 | `{{ANSWER}}` | `data-correct-value="3"` → `data-correct-value="{{ANSWER}}"` |
| 2120 | 固定 | `data-answer-type="single"` → `data-answer-type="ox-grid"` |
| 2121 | 削除（→ `{{ANSWER_EXPLANATION}}` 不要、326.json に無い） | `data-explanation="各記述の判例による分類は…"` — 削除 or 空文字 |
| 2124-2130 (canonical) | 削除 | `<div class="answer-row">` の 1〜5 ボタン群（組合せ型固有） |
| 新規 | ox-grid 構造 | `<div class="answer-ox-grid">` で `<div class="ox-row">` × 5（ア〜オ） |
| 新規 | `{{CHOICE_*_LABEL}}` / `{{CHOICE_*_STEM}}` | 各 ox-row に label + stem + ○× ボタン |
| 2131 | 固定 | `<button class="reveal-answer-btn">解答を表示</button>` |
| 2132 | 固定 | `<div id="answer-feedback" hidden></div>` |

### §1.6 PART B 肢別解説 (L2138-2516)

各記述（ア〜オ）の 5 セット。各セット同型構造。

#### 共通構造（記述 ア = letter A 例、L2143-2217）

| 行 | slot | canonical 元テキスト抜粋（詐欺罪・ア） |
|---:|---|---|
| 2144 | 固定（odd/even は順番） | `<section class="choice-section odd" id="choice-1">` |
| 2145 | 固定 | `<nav class="sec-nav">…</nav>` |
| 2148 | `{{CHOICE_A_LABEL}}` | `<div class="choice-big-badge">ア</div>` |
| 2149 | `{{CHOICE_A_VERDICT_LABEL}}` + verdict class | `<span class="verdict verdict-correct">→ 結論Ⅰ 詐欺罪のみが成立し得る</span>` → 326 用：`<span class="verdict verdict-{{CHOICE_A_VERDICT_CLASS}}">{{CHOICE_A_VERDICT_LABEL}}</span>`（verdict_label「正しい/誤っている」） |
| 2150 | 削除（or `{{CHOICE_A_SUMMARY}}` JSON拡張） | choice-summary（背任行為が同時に欺罔行為に当たる場合…）— JSON に summary フィールド無し、削除 or 空 |
| 2155 | `{{CHOICE_A_STEM}}` | `<p>他人のためにその事務を処理する者が、任務に背いて…</p>` |
| 2160 | `{{CHOICE_A_EXPLANATION}}` | `<p><a class="ref-case">最判昭28.5.8</a>は、「他人の委託により…</p>` — 326.json では `choices[0].explanation` を全文挿入 |
| 2163-2171 | 削除（or {{CHOICE_A_BASIS_HTML}}） | basis-link card（条文・判例リンク）— 個別ハードコードされた条文 ID は他罪では使えない、**スタブ削除推奨** |
| 2173-2207 | 削除 | professor card（教授の解説：ポイント／道筋／key-phrase／analogy／warning／cross-link）— 完全に詐欺罪固有、**スタブ削除推奨** |
| 2209-2215 | 削除（or {{CHOICE_A_POINTS_HTML}}） | choice-points（肢ポイントまとめ ol）— JSON に points フィールド無し、削除 |

**選択肢 A〜E（記述ア〜オ）について同型に展開**。

#### 簡素化テンプレ案（PART B 1 セットあたり）

```html
<section class="choice-section {{CHOICE_A_PARITY}}" id="choice-1">
  <nav class="sec-nav">...</nav>
  <div class="choice-header-block">
    <div class="choice-big-badge">{{CHOICE_A_LABEL}}</div>
    <span class="verdict verdict-{{CHOICE_A_VERDICT_CLASS}}">{{CHOICE_A_VERDICT_LABEL}}</span>
  </div>
  <div class="sub-card original">
    <span class="label">記述原文</span>
    <p>{{CHOICE_A_STEM}}</p>
  </div>
  <div class="sub-card explanation">
    <h4>📖 解説原文</h4>
    <p>{{CHOICE_A_EXPLANATION}}</p>
  </div>
  <div class="sub-card basis-link">
    <h4>📚 根拠判例</h4>
    <p>{{CHOICE_A_CASES}}</p>
  </div>
  <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
</section>
```

- `{{CHOICE_*_PARITY}}` → render.py で odd/even 自動付与（JSON 非依存）が望ましいが、現実装にない。**ハードコード（A,C,E=odd / B,D=even）が現実的**。
- `{{CHOICE_*_VERDICT_CLASS}}` → render.py で `verdict_label` から「正しい→correct / 誤っている→incorrect」マップ。現 render.py にない。**slot 名としては `CHOICE_*_VERDICT_LABEL` のみで verdict クラスは固定で `verdict-incorrect` をデフォとし、後で修正**

→ verdict class マッピングは **render.py 拡張** が必要。slotmap.md で別途提案。

### §1.7 A-3 共通根拠条文・判例 (L2518-2669)

**スタブ化推奨**。

```html
<section class="section" id="basis">
  <nav class="sec-nav"><a href="#choice-5">↑記述オ</a><a href="#c-1">↓C-1</a></nav>
  <h2 class="section-title"><span class="sec-icon">❀</span>A-3 共通根拠条文・判例</h2>
  <!-- TODO: {{CRIME}} の根拠条文・判例を JSON 拡張で供給 -->
  <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
</section>
```

### §1.8 PART C 体系・記憶 (L2671-3047)

**スタブ化推奨**。各 section (c-1〜c-7) の骨格のみ残し、本文は TODO コメント。

### §1.9 PART D ARENA (L3049-3317)

**スタブ化推奨**。drill-block 群は完全削除し、骨格のみ残す。`arena-counter` の `total` を `0` または slot 化。

### §1.10 footer-spec (L3322-3347)

| 行 | slot | canonical 元テキスト抜粋 |
|---:|---|---|
| 3323 | `{{PROBLEM_ID}}` / `{{CRIME}}` / `{{SOURCE_ID}}` | `<p><strong>KTX301</strong>・刑法（司法試験R1-16 詐欺罪と他罪の成否）</p>` → `<p><strong>刑TX{{PROBLEM_ID}}</strong>・刑法（{{SOURCE_ID}} {{CRIME}}）</p>` |
| 3324 | `{{CORRECT_RATE}}` / `{{OVERRIDE_PATTERN}}` | `正答率：65%／パターン P1「ローズシャンブル」適用` → `正答率：{{CORRECT_RATE}}／パターン {{OVERRIDE_PATTERN}}適用` |
| 3326-3346 | byte-level 一致 | feature-tag 群（spec バージョン等、固定値） |

### §1.11 script (L3352-3741)

byte-level 一致対象。slot なし。

---

## 2. 全 slot 一覧（render.py が必要とする）

CLAUDE.md PATCH §2 ＋ 326.json 整合のため、以下を使用：

### 既存 slot (render.py 対応済み)

| slot | source | 値例（326） |
|---|---|---|
| `{{PROBLEM_ID}}` | `id` | `326` |
| `{{SOURCE_ID}}` | `source` | `H29-12` |
| `{{CRIME}}` | `crime` | `盗品等罪` |
| `{{CHAPTER}}` | `chapter` | `第4章 財産に対する罪` |
| `{{SECTION}}` | `section` | `第8節 盗品等に関する罪` |
| `{{PAGE}}` | `page` | `845` |
| `{{POINTS}}` | `points` | `4` |
| `{{CORRECT_RATE}}` | `correct_rate` | `47%` |
| `{{INSTRUCTION}}` | `instruction` | `次のアからオまでの各記述を判例の立場に従って検討し…` |
| `{{ANSWER}}` | `answer` | `12222` |
| `{{OVERRIDE_PATTERN}}` | `override_pattern` | `P2` |
| `{{CHOICE_A_LABEL}}` 〜 `{{CHOICE_E_LABEL}}` | `choices[*].label` | `ア`〜`オ` |
| `{{CHOICE_A_STEM}}` 〜 `{{CHOICE_E_STEM}}` | `choices[*].stem` | （長文） |
| `{{CHOICE_A_VERDICT}}` 〜 `{{CHOICE_E_VERDICT}}` | `choices[*].verdict` | `1`/`2` |
| `{{CHOICE_A_VERDICT_LABEL}}` 〜 `{{CHOICE_E_VERDICT_LABEL}}` | `choices[*].verdict_label` | `正しい`/`誤っている` |
| `{{CHOICE_A_EXPLANATION}}` 〜 `{{CHOICE_E_EXPLANATION}}` | `choices[*].explanation` | （長文） |
| `{{CHOICE_A_CASES}}` 〜 `{{CHOICE_E_CASES}}` | `choices[*].case_citations` | `最判昭24.10.20（百選Ⅱ77事件）` |

### 未使用（テンプレに置かない）

`{{POINTS}}` / `{{CHAPTER}}` / `{{SECTION}}` / `{{PAGE}}` は HTML への露出箇所がないため slot として配置しない（render.py で値が作られても問題なし、置換対象が存在しないので無害）。

### **要追加検討の派生 slot**

| 派生 slot | 必要性 | 現実装での扱い |
|---|---|---|
| `{{CHOICE_*_VERDICT_CLASS}}`（`correct`/`incorrect`） | PART B の `<span class="verdict verdict-...">` | **render.py 拡張**：`verdict_label` から `correct/incorrect` 派生。または `verdict` (1/2) → `correct/incorrect` マップ。本タスクではテンプレ側で `{{CHOICE_A_VERDICT_LABEL}}` のみ使い、verdict class は `verdict-correct` で固定（または verdict-correct/incorrect の両 class を span で並記）して妥協する案も。 |
| `{{PATTERN_NAME}}`（`ローズシャンブル`等） | header / footer | **render.py 拡張**：`override_pattern` (P1〜P5) → 色名マップ。当面省略。 |
| `{{ERA}}`（`令和元年` 等）/ `{{Q_NUM}}`（`第16問`） | exam-badge | **省略**。canonical の exam-badge 個別表示はスタブ化（`{{SOURCE_ID}}` 1 個に集約）。 |

---

## 3. PART A の構造書換案（Gap-A の (A) 採用前提）

326（ox-grid-5）の PART A は次の形：

```html
<section class="section" id="part-a">
  <nav class="sec-nav"><a href="#answer-area">↓解答</a><a href="#choice-1">↓記述ア</a></nav>
  <h2 class="section-title"><span class="sec-icon">❀</span>A-1 問題文</h2>
  <p style="font-weight:600;">{{INSTRUCTION}}</p>

  <h3 style="...">【記述】</h3>
  <div class="problem-text"><span class="choice-num-inline">{{CHOICE_A_LABEL}}</span>{{CHOICE_A_STEM}}</div>
  <div class="problem-text"><span class="choice-num-inline">{{CHOICE_B_LABEL}}</span>{{CHOICE_B_STEM}}</div>
  <div class="problem-text"><span class="choice-num-inline">{{CHOICE_C_LABEL}}</span>{{CHOICE_C_STEM}}</div>
  <div class="problem-text"><span class="choice-num-inline">{{CHOICE_D_LABEL}}</span>{{CHOICE_D_STEM}}</div>
  <div class="problem-text"><span class="choice-num-inline">{{CHOICE_E_LABEL}}</span>{{CHOICE_E_STEM}}</div>

  <div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>
</section>
```

A-2 解答エリア（ox-grid 形式）：

```html
<section class="section" id="answer-area">
  <nav class="sec-nav">...</nav>
  <h2 class="section-title"><span class="sec-icon">❀</span>A-2 解答</h2>

  <div class="answer-area"
       data-correct-value="{{ANSWER}}"
       data-answer-type="ox-grid">
    <h3>各記述の正誤を判定</h3>
    <p class="answer-instruction">各記述について「正しい (1)」か「誤っている (2)」を選んでください。</p>

    <div class="answer-ox-grid">
      <div class="ox-row">
        <span class="ox-label">{{CHOICE_A_LABEL}}</span>
        <p class="ox-stmt">{{CHOICE_A_STEM}}</p>
        <span class="ox-btn-group">
          <button class="ox-btn" type="button" data-value="1">正しい</button>
          <button class="ox-btn" type="button" data-value="2">誤っている</button>
        </span>
      </div>
      <!-- B/C/D/E 同様、計 5 行 -->
    </div>

    <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>
    <div id="answer-feedback" hidden></div>
  </div>

  <div class="back-to-top">...</div>
</section>
```

---

## 4. 既知の不確実事項（ユーザに判断仰ぐ）

1. **Gap-A の判断**：(A) ox-grid-5 書換 / (B) 組合せ型維持 / (C) 両対応分岐 → **推奨 (A)**
2. **Gap-B の判断**：A-3/PART C/PART D のスタブ化 / JSON 拡張先行 / canonical 流用（禁則） → **推奨スタブ化**
3. **verdict class マッピング**：`render.py` を拡張するか、テンプレ側で `verdict_label` を直接 class 名に流す妥協（CSS で対応）か → **推奨 render.py 拡張**
4. **theme-tags / difficulty 等の canonical 固有メタ**：削除 / `{{CRIME}}` 1 個に集約 / JSON 拡張 → **推奨削除**

---

## 5. Step 3 承認依頼項目（要回答）

- [ ] Gap-A の判断（推奨：(A) ox-grid-5 書換）
- [ ] Gap-B の判断（推奨：A-3/PART C/PART D スタブ化）
- [ ] verdict class マッピング（推奨：render.py 拡張）
- [ ] theme-tags / difficulty 等の扱い（推奨：削除）
- [ ] このまま Step 4（KTX_template.html 生成）に進んでよいか

承認後、上記方針で Step 4 を実行する。

---

### §5.1 ox-grid-N 形式分岐 (R-1: ox-grid-4 対応)

#### 背景

問題 327 (予備 R2-10、盗品等罪) は ア〜エの 4 択 ○× 判定で構成され、現行
`templates/KTX_template.html` (ア〜オの 5 件ハードコード) では未置換 slot
`{{CHOICE_E_*}}` が残り render fail する。今後の形式拡張可能性を踏まえ、
以下の方針で対応する。

#### 決定事項

##### 1. schema 拡張

- `schema/problem.schema.json` の `instruction_type` enum に `"ox-grid-4"` を
  追加する。
- 当面サポートは `ox-grid-5` / `ox-grid-4` の 2 値とする。
- `multi-select-*`, `combination-*`, `single-choice`, `ranking`, `fill-in`
  は別フェーズの案件として扱う (今フェーズではスコープ外)。
- `answer.description` に 4 桁例 `'2212'` を追記する。pattern `^[12]+$` は
  桁数自由のため変更不要。
- `choices.minItems` / `maxItems` および `choice.label.enum` は既に柔軟
  (1〜10、ア〜コ) のため変更不要。

##### 2. テンプレート構成

- `templates/KTX_template_ox4.html` を新規作成する。
- ベースは `templates/KTX_template.html` (ox-grid-5 版) から E 系 (オ) を
  機械的に削除した派生とする。
- 単一 template に CSS/JS 分岐を埋め込む案は採用しない。HTML 構造そのものの
  増減を CSS 表示制御で隠すと:
  - validate_structure.py の S12 / S17 (choice-section 5 件期待) が fail する
  - DOM ノイズが残り、screen reader / DevTools 上で混乱を招く
  - 「非表示の choice-5」を解析する自動化スクリプトを誤動作させる
  という 3 重の害が出る。

##### 3. 意図的な差分箇所 (KTX_template.html ↔ KTX_template_ox4.html)

差分は以下 4 種類のみに限定し、それ以外は byte-level 同期を義務とする:

| 差分箇所 | 5 件版 | 4 件版 |
|---|---|---|
| TOC アンカー | ア〜オ 5 件 | ア〜エ 4 件 |
| PART A 問題文 (problem-text) | A〜E 5 行 | A〜D 4 行 |
| A-2 ox-grid (ox-row) | A〜E 5 件 | A〜D 4 件 |
| PART B choice-section | choice-1〜choice-5、parity = odd/even/odd/even/odd | choice-1〜choice-4、parity = odd/even/odd/even、choice-4 の forward nav は「↓共通根拠」 |

HEAD / CSS / JS / PART C スタブ / PART D スタブ / A-3 / footer-spec は
byte-level 同期。両 template を編集する際は同一の修正を双方に反映すること。

##### 4. canonical 構成

- 形式別 canonical は **追加しない**。
- `canonical/KTX301.html` を引き続き構造参考として固定する。
- ox-grid-N 系の運用 reference は「最初に 3 段検証 (render → structure →
  content) を完走した実例 HTML」とする:
  - ox-grid-5 → `outputs/tx/刑TX/刑TX326.html`
  - ox-grid-4 → 完成後の `outputs/tx/刑TX/刑TX327.html`
- canonical ファイル数を増やさないことで、コピー禁則対象とテンプレ役割の
  分裂を防ぐ。

##### 5. render.py の template 選択分岐

- `scripts/render.py` に `TEMPLATE_PATHS` dict を導入する:
  - `"ox-grid-5"` → `templates/KTX_template.html`
  - `"ox-grid-4"` → `templates/KTX_template_ox4.html`
- `problems/{id}.json` の `instruction_type` から template を選択する。
- **デフォルト挙動**: `instruction_type` が未指定の場合は `ox-grid-5` を選択し
  (既存 326 のセマンティクス維持)、stdout に WARN ログを出力する。
- `instruction_type` が dict に無い値 (例: 旧 `single-choice` 等) の場合は
  ERROR で exit 2。silently 失敗させない。

##### 6. validate_structure.py の動的化

- S12 (PART B choice-section) と S17 (sub-card 検査) を choice-section 数
  ハードコード 5 から動的化する。
- 期待数 N の導出は以下の **三者一致** を要件とする:
  1. HTML 内の `[id^="choice-"]` 実数
  2. `answer-area .answer-area[data-correct-value]` の桁数
  3. (JSON が利用可能な場合) `choices` 配列長
- 三者が不一致の場合は ERROR を発する (誤って「3 件で正しい」と認定される
  リスクを潰すため)。
- S73-AP35 (ox-row 数 == cv 桁数) は既に動的、変更不要。

##### 7. 両 template の同期義務

`templates/KTX_template.html` を修正する際は同一の修正を
`templates/KTX_template_ox4.html` にも反映する。差分は §3 で列挙した 4 種類
のみとし、それ以外の場所が乖離した場合は同期不備とみなす。

将来的な PR / レビュー観点として、両 template の `diff` を取り、差分が想定 4
箇所のみであることを確認する手順を推奨する (CI 化の検討余地あり)。

#### 将来の一般化 (保留)

`ox-grid-N` (N=3, 6, ...) が必要になった場合、template 別ファイル方式は
N 個のファイル爆発で破綻する。その時点で以下のいずれかへ移行する:

- (a) JS による行動的レンダリング (ランタイムで `<div class="ox-row">` を生成)
- (b) JSON 駆動の partial 合成 (render.py をテンプレ生成側に拡張、各
      ox-row / problem-text / choice-section をループ展開)

本フェーズでは N ∈ {4, 5} の 2 ファイル方式で凍結する。N=3 または N>=6 の
問題が新規入手された時点で再設計トリガーとする。

#### AP-37 抵触回避ガイド

`answer_explanation` フィールドの値は、326 と同じく
「解答および各記述の正誤判定」を基本句とする。罪名・正解番号・PDF タイトル
固有句を含めないこと (validate_structure.py の S74-AP37 が正解値リテラルの
先頭混入を検知)。

#### crime 表記揺れの取り扱い

PDF タイトルの罪名表記は問題ごとに揺れる:

- 326: 「盗品等罪」
- 327: 「盗品等に関する罪」

`problems/{id}.json` の `crime` 値は CRIME_SIGNATURES のキーに統一して
`"盗品等罪"` とする (validate_content.py の negative check キーと一致させる
ため)。PDF タイトルの正式名称を HTML 上で表示する必要が出た場合は、将来
`{{CRIME_DISPLAY}}` 等の派生 slot を導入することを検討する (本フェーズでは
スコープ外)。

---

### §5.2 multi-select-N 形式分岐 (R-2: multi-select-5 対応)

#### 背景

問題 328 (司法 R7-19、盗品等罪) は「1〜5 の各記述から誤っているものを 2 個
選びなさい」という複数選択型問題で構成され、ox-grid (各記述に独立した ○×
判定) とは A-2 解答エリアの UI 構造が根本的に異なる。既存 v8.11.3 に
`data-answer-type="multi"` 用の CSS / JS / validator (S73-AP35 / S71-AP33
multi canonical 文言) インフラが既に揃っているため、template 派生と schema
拡張で対応する。

### 決定事項

#### 1. schema 拡張

- `schema/problem.schema.json` の `instruction_type` enum に `"multi-select-5"` を
  追加する。当面サポートは `ox-grid-5` / `ox-grid-4` / `multi-select-5` の 3 値。
- `answer` フィールドを **`oneOf` 分岐**に変更:
  - string + `pattern: ^[12]+$` (既存 ox-grid 系の ○× 列、後方互換維持)
  - array of integer (1〜5)、`minItems: 1`、`maxItems: 5`、`uniqueItems: true`
    (新規 multi-select 系の正解番号集合)
- `choice.label.enum` に **算用数字 `"1"〜"5"`** を追加 (ox-grid 系のカナ ア〜コ は
  維持、add only)。
- `choices.minItems` / `maxItems` は既存 4 / 5 を維持 (multi-select-5 は 5 件で
  上限と一致)。
- 後方互換: 既存 326.json / 327.json は引き続き valid (string answer + カナ label の
  経路が `oneOf` の第 1 ブランチで通る)。

#### 2. テンプレート構成

- `templates/KTX_template_msel5.html` を新規作成する。
- ベースは `templates/KTX_template.html` (ox-grid-5 版) から派生。
- A-2 解答エリアを ox-grid 構造から **multi 構造に全面書換**:
  - `data-answer-type="multi"` (S73-AP35 の自動判定と一致)
  - `<div class="answer-row">` 配下に `<button class="answer-slot">` × 5
  - `<p class="selection-counter">` を必須配置 (S73-AP35 multi で WARN を出さないため)
  - `<p class="answer-instruction">` は v8.11.3 multi canonical 文言
    「選択肢を{{SELECTION_COUNT}}個選んで「解答を表示」を押してください。」を採用
    (S71-AP33 の正規表現 `^選択肢を\d+個選んで「解答を表示」を押してください。$` に整合)
- 単一 template に CSS/JS 分岐を埋め込む案は採用しない (slotmap §5.1 §2 と
  同じ理由)。

#### 3. 意図的な差分箇所 (KTX_template.html ↔ KTX_template_msel5.html)

差分は以下 7 種類のみに限定し、それ以外は byte-level 同期を義務とする:

| 差分箇所 | 5 件版 (ox-grid-5) | multi-select-5 版 |
|---|---|---|
| TOC アンカー | ア〜オ 5 件 | **算用数字 1〜5** 5 件 |
| PART A 見出しコメント | `ox-grid-5 形式` | `multi-select-5 形式` |
| PART A 問題文 sec-nav | `↓記述ア` | `↓記述1` |
| A-2 解答エリア（全面書換） | ox-grid 構造（`ox-row` × 5、各行 ○× ボタン） | multi 構造（`answer-row` + `answer-slot` × 5 + `selection-counter`、`data-answer-type="multi"`） |
| A-2 `<h3>` および `answer-instruction` 文言 | 「各記述の正誤を判定」「各記述について…」 | 「該当する選択肢を選択」「選択肢を{{SELECTION_COUNT}}個選んで…」 |
| PART B 見出しコメント / part-title | 「PART B ── 記述別解説（ア〜オ）」 | 「PART B ── 記述別解説（1〜5）」 |
| PART B choice-section 内 sec-nav の表記 / セクションコメント / A-3 back-nav | 「記述ア / 記述イ / … / 記述オ」 | 「記述1 / 記述2 / … / 記述5」 |

HEAD / CSS / JS / PART C スタブ / PART D スタブ / A-3 / footer-spec の構造部分は
byte-level 同期。CSS / JS は既に v8.11.3 で 3 Type 対応 (single / multi / ox-grid)
を持つため、template を multi 構造に書換えるだけで JS の `multi` 分岐が動作する。

#### 4. canonical 構成

- 形式別 canonical は **追加しない** (slotmap §5.1 §4 の原則を踏襲)。
- `canonical/KTX301.html` を引き続き構造参考として固定する。
- multi-select-N 系の運用 reference は「最初に 3 段検証 (render → structure →
  content) を完走した実例 HTML」とする:
  - ox-grid-5 → `outputs/tx/刑TX/刑TX326.html`
  - ox-grid-4 → `outputs/tx/刑TX/刑TX327.html`
  - multi-select-5 → 完成後の `outputs/tx/刑TX/刑TX328.html`
- canonical ファイル数を増やさないことで、コピー禁則対象とテンプレ役割の
  分裂を防ぐ。

#### 5. render.py の template 選択分岐

- `scripts/render.py` の `TEMPLATE_PATHS` dict に `"multi-select-5"` を追加:
  - `"ox-grid-5"`      → `templates/KTX_template.html`
  - `"ox-grid-4"`      → `templates/KTX_template_ox4.html`
  - `"multi-select-5"` → `templates/KTX_template_msel5.html`
- `LABEL_TO_LETTER` に算用数字マッピングを追加: `"1"→A`, `"2"→B`, `"3"→C`,
  `"4"→D`, `"5"→E`。slot 名 (`CHOICE_A_*` 等) は ox-grid と共通化することで、
  template / render.py の両方の保守コストを下げる。
- `build_slot_dict` に `_format_answer` helper を追加:
  - answer が list → `","` 連結文字列 ("1,4")
  - answer が string → そのまま ("12222")
- `SELECTION_COUNT` slot を追加: answer が list なら要素数、ox-grid なら空文字。
  multi 用 template の `{{SELECTION_COUNT}}` placeholder を埋める。
- **デフォルト挙動**: `instruction_type` が dict に無い値・未指定の場合は
  既存 `KTX_template.html` (ox-grid-5) にフォールバック (R8 と同方針)。

#### 6. validate_structure.py の対応

- helper `_derive_cv_info(soup)` を新設し、`(mode, n_choices, n_correct)` を返す:
  - cv に `","` 含有 → `('multi', 5, K)` (K はカンマ区切り要素数)
  - cv が `^[12]{2,}$` → `('ox-grid', len(cv), len(cv))`
  - cv が `^\d+$` → `('single', 5, 1)`
  - その他 → `('unknown', 5, 5)`
- 既存 `_derive_expected_choice_count` は `_derive_cv_info` の `n_choices` を返す
  thin wrapper として API 互換を維持。
- S12 の三者一致 sanity check を mode 別に分岐:
  - ox-grid: cv 桁数 == choice-section 数 == ox-row 数
  - multi: choice-section 数 == answer-slot 数 == 5 (template 固定)、
           K ≤ N の制約も検証
- S73-AP35 (cv 形式と data-answer-type の自動判定整合) は既に multi 自動判定済 (v8.11.3)、
  変更不要。
- S71-AP33 (answer-instruction canonical 文言) は既に multi 用パターン
  `^選択肢を\d+個選んで「解答を表示」を押してください。$` を許容、変更不要。

#### 7. validate_content.py の対応

- positive check の `("crime", "answer", "correct_rate", "source")` 照合ロジックで、
  `answer` が list (新規 multi-select 系) の場合は `","` 連結文字列に正規化して
  HTML 内検索する (render.py の `_format_answer` と同じ正規化)。
- 既存 string answer 経路には影響なし。

#### 8. 三 template の同期義務

`KTX_template.html` / `KTX_template_ox4.html` / `KTX_template_msel5.html` の
3 本立てとなる。同期義務:

- **同期対象** (3 本で byte-level 一致を維持): HEAD / `<style>` 内 CSS 全体 /
  `<script>` 内 JS 全体 / marker-legend / PART C スタブ (c-1〜c-7) /
  PART D スタブ / A-3 共通根拠スタブ (リンク先 id を除く) / footer-spec の構造。
- **意図差分対象** (各 template 固有): TOC アンカー / PART A 問題文行数 /
  A-2 解答エリア / PART B choice-section 数および表示ラベル。
  各形式の意図差分は本書 §5.1 §3 (ox-grid-4) / §5.2 §3 (multi-select-5) に列挙する。

##### 同期義務違反の検出方法

将来の保守において、3 本の同期義務違反を早期検出するため、以下の手順を推奨:

1. **diff 二重照合**: 任意の 2 本ペアで `diff` を取得し、差分が当該ペアの意図差分
   テーブル (§5.1 §3 / §5.2 §3) に列挙された箇所のみであることを確認する。
   - `diff KTX_template.html KTX_template_ox4.html`     → §5.1 §3 と一致
   - `diff KTX_template.html KTX_template_msel5.html`   → §5.2 §3 と一致
   - `diff KTX_template_ox4.html KTX_template_msel5.html` → 上記 2 つの和差
2. **HEAD / CSS / JS / PART C スタブ / PART D スタブ / A-3 / footer-spec の
   特定範囲のみ抽出した部分 diff** を取り、3 本で byte-level 一致を直接確認する
   方法も可。CI 化する場合はこちらを推奨。
3. **想定外差分が検出された場合の対処**:
   - 意図差分テーブルに該当しない差分 → 同期不備として **修正必須** (3 本で揃える)
   - 新しい意図差分が必要な場合 → 先に slotmap §5.1 / §5.2 / §5.3+ のテーブル
     更新を行ってからコードを変更する (設計→実装の順を逆転させない)

PR / レビュー時にこの 3 通り diff を機械的に確認する仕組み (簡易シェルスクリプトまたは
CI ステップ) を将来検討する。

### 将来の一般化 (保留)

`multi-select-N` (N≠5) や `multi-select-N` で K=1 (実質 single-choice-5 と同等)、
`combination-N` (組合せ型単一選択、KTX301 と同型) など、形式バリエーションが
増えていくと **N 個の template ファイル爆発**で破綻する。閾値の議論:

- 3 ファイル (本フェーズ) は限界に近い。これ以上増やさない方針を取りたい。
- 次フェーズ (329 / 330) で 4 件目の template が必要になる場合、まず
  **一般化リファクタの設計**を slotmap §5.3 / §5.4 に書いてから実装する。
- 候補移行先:
  - (a) JS による行動的レンダリング (ランタイムで PART A / A-2 を組み立て、
        choice-section も配列駆動で生成)
  - (b) JSON 駆動の partial 合成 (render.py を Jinja2 等のテンプレエンジンに
        移行し、ループとマクロで形式差を吸収)
- 本フェーズ (multi-select-5) では (a)(b) いずれも採用せず、template 派生方式を
  使う。次フェーズで切替トリガーを発火する。

### AP-37 抵触回避ガイド (継承)

`answer_explanation` フィールドの値は、326 / 327 と同じく
「解答および各記述の正誤判定」を基本句とする。罪名・正解番号・PDF タイトル
固有句を含めないこと (validate_structure.py の S74-AP37 が正解値リテラルの
先頭混入を検知)。multi-select 系でも同じ基本句を流用する。

### answer 表記正規化ガイド

- JSON 側は **int の配列** (例: `[1, 4]`) で持つ。
- HTML 側は **ASCII カンマ連結文字列** (例: `"1,4"`) として
  `data-correct-value` 属性に展開される。
- 配列は **昇順、重複なし** を schema レベルで強制 (`uniqueItems: true`)。
- PDF 上の「1、4（順不同）」等の全角カンマ表記は、JSON 化時に **数値配列に
  正規化**する (表記揺れを source に閉じ込めない)。
- HTML 表示用に「1、4（順不同）」表記を別 slot で持つかは別フェーズ案件。

### crime / source 表記揺れの取り扱い (§5.1 §7 を継承)

- `crime` 値は CRIME_SIGNATURES のキーに統一 (例: PDF が「盗品等に関する罪」でも
  `"盗品等罪"` で正規化)。
- `source` は予備独自問題で `"予備R{N}-{M}"`、司法試験で `"R{N}-{M}"` または
  `"H{N}-{M}"` 形式。

---

### §5.3 single-choice-N 形式分岐 + 【見解】slot 導入 (R-3: single-choice-5 対応)

#### 背景

問題 329 (司法 H20-16、信書隠匿罪と器物損壊罪) は **1〜5 の 5 記述から「誤っているもの」
を 1 個選ぶ単一選択型**で、加えて設問前に **【見解】A/B/C の 3 学説** が提示され、
各記述がそれら見解のどれを採用した場合の帰結かを問う構造を持つ。

- 形式としては §5.2 multi-select-5 の **K=2 を K=1 に縮めた派生** に近い。
- 既存 v8.11.3 multi インフラには `single` mode も完備されており (CSS の
  `.answer-slot` 共通スタイル、JS の `type === 'single'` 分岐、validate_structure
  の `_derive_cv_info` が `('single', 5, 1)` を返す、S71-AP33 の single canonical
  文言 `^選択肢を選んで「解答を表示」を押してください。$` 登録済)、
  template 派生 + schema 拡張で完結する見込み。
- ただし **【見解】section は新概念** であり、既存 ox-grid / multi-select 系には
  存在しない構造要素。これが §5.3 最大の追加点。

調査記録は `docs/session-328-completion.md` §8 「329 への引き継ぎ」を起点に、
本書 §5.3 で設計合意を凍結する。

### 決定事項

#### 1. schema 拡張

- `schema/problem.schema.json` の `instruction_type` enum に `"single-choice-5"` を
  追加する (add only)。当面サポートは `ox-grid-5` / `ox-grid-4` / `multi-select-5` /
  `single-choice-5` の 4 値。
- `answer` フィールドの `oneOf` に **第 3 ブランチ「integer (1〜5)」** を追加:
  - 第 1 ブランチ: string + `pattern: ^[12]+$` (ox-grid 系の既存パス、後方互換維持)
  - 第 2 ブランチ: array of integer 1〜5、`uniqueItems: true` (multi-select 系)
  - **第 3 ブランチ**: integer (1〜5) 単体 (single-choice 系の新規)
- `$defs.View` を新規定義:
  - `{ label: string (enum ["A","B","C"]), body: string (minLength 10) }`
  - 当面は固定 3 件 (A/B/C) を前提とし、`additionalProperties: false`。
- `properties.views`:
  - `type: array, items: { $ref: "#/$defs/View" }, minItems: 3, maxItems: 3`
  - **conditional required**: `instruction_type === "single-choice-5"` のときに限り
    `required` に追加する (JSON Schema の `allOf` + `if/then` で表現)。
- 後方互換: 既存 326.json / 327.json / 328.json は引き続き valid (string answer /
  array answer の経路が `oneOf` の第 1/第 2 ブランチで通る、`views` 未指定は
  ox-grid / multi-select 系では required 対象外)。

#### 2. テンプレート構成

- `templates/KTX_template_sc5.html` を新規作成する。**template 本数は 4 本目**に到達する。
- ベースは `templates/KTX_template_msel5.html` (multi-select-5 版) から派生:
  - K=2 → K=1 の縮小により selection-counter を削除
  - `data-answer-type` を `"multi"` → `"single"` に変更
  - `answer-instruction` を v8.11.3 single canonical 文言に変更
  - PART A 内に **【見解】section** を新規追加 (problem-text 群の前に配置)
- 単一 template に CSS/JS 分岐を埋め込む案は採用しない (slotmap §5.1 §2 / §5.2 §2
  と同じ理由)。

#### 3. 意図的な差分箇所 (KTX_template_msel5.html ↔ KTX_template_sc5.html)

差分は以下 4 種類のみに限定し、それ以外は msel5 と byte-level 同期を義務とする:

| 差分箇所 | multi-select-5 版 (msel5) | single-choice-5 版 (sc5) |
|---|---|---|
| A-2 `data-answer-type` 属性 | `"multi"` | `"single"` |
| A-2 `<p class="selection-counter">` | 存在 ("選択数: 0 / {{SELECTION_COUNT}}") | **削除** (single は 1 つだけ選ぶため不要) |
| A-2 `<p class="answer-instruction">` | `「選択肢を{{SELECTION_COUNT}}個選んで「解答を表示」を押してください。」` | `「選択肢を選んで「解答を表示」を押してください。」` (S71-AP33 single canonical 文言、`\d+個` を持たない) |
| PART A 内の【見解】section | 存在しない | **新規追加**。problem-text 群の前 (A-1 タイトル直後) に `<section class="views-section" id="part-a-views">` を配置、内部に 3 つの `<div class="view-block">`、各々 `{{VIEW_A_LABEL}}` / `{{VIEW_A_BODY}}` 〜 `{{VIEW_C_LABEL}}` / `{{VIEW_C_BODY}}` の slot を持つ |

HEAD / CSS / JS / marker-legend / PART B / PART C スタブ / PART D スタブ /
A-3 / footer-spec はすべて **msel5 と byte-level 同期**。具体的には:
- TOC アンカー (`<a href="#choice-1">1</a>` 〜 `<a href="#choice-5">5</a>`) は同じ
- PART B 5 件の choice-section / parity / nav 表記 (記述1〜記述5) は同じ
- 選択肢ラベルは数字 1〜5 (msel5 と共通)

CSS / JS は v8.11.3 の 3 Type 対応により `data-answer-type="single"` で
自動的に正しい挙動を取る。**CSS/JS の追加・変更は一切不要**。

#### 4. canonical 構成

- 形式別 canonical は **追加しない** (slotmap §5.1 §4 / §5.2 §4 の原則を踏襲)。
- `canonical/KTX301.html` を引き続き構造参考として固定する。KTX301 自体は実は
  `data-answer-type="single"` の 5 番号ボタン UI を内包しており、single-choice-5
  の構造 reference として最も近い既存実例だが、**本フェーズで KTX301 を直接
  reference 化することはしない**。
- single-choice-N 系の運用 reference は「最初に 3 段検証 (render → structure →
  content) を完走した実例 HTML」とする:
  - ox-grid-5      → `outputs/tx/刑TX/刑TX326.html`
  - ox-grid-4      → `outputs/tx/刑TX/刑TX327.html`
  - multi-select-5 → `outputs/tx/刑TX/刑TX328.html`
  - **single-choice-5 → 完成後の `outputs/tx/刑TX/刑TX329.html`**

#### 5. render.py の template 選択分岐

- `scripts/render.py` の `TEMPLATE_PATHS` dict に `"single-choice-5"` を追加:
  - `"ox-grid-5"`      → `templates/KTX_template.html`
  - `"ox-grid-4"`      → `templates/KTX_template_ox4.html`
  - `"multi-select-5"` → `templates/KTX_template_msel5.html`
  - **`"single-choice-5"` → `templates/KTX_template_sc5.html`**
- `LABEL_TO_LETTER` は msel5 で導入した算用数字マッピング (`"1"→A` 〜 `"5"→E`) を
  そのまま流用。追加変更不要。
- `build_slot_dict` に **【見解】slot の展開ロジック**を追加:
  - JSON の `views` 配列 (長さ 3、A/B/C 固定) から 6 個の slot を構築:
    - `VIEW_A_LABEL`, `VIEW_A_BODY`
    - `VIEW_B_LABEL`, `VIEW_B_BODY`
    - `VIEW_C_LABEL`, `VIEW_C_BODY`
  - `views` が未指定 (ox-grid / multi-select 系) の場合は空文字を入れる
    (sc5 以外の template に slot が存在しないので無害)。
- `_format_answer` は **既に integer 単体に対応済み** (`str(2)` → `"2"`、§5.2 で
  future-proof 化済)。追加変更不要。
- `SELECTION_COUNT` slot は single では使用されないが、空文字を入れて
  msel5/sc5 共通の slot 辞書構造を維持。
- **デフォルト挙動**: `instruction_type` が dict に無い値・未指定の場合は
  既存 `KTX_template.html` (ox-grid-5) にフォールバック (§5.1 §5 / §5.2 §5 と同方針)。

#### 6. validate_structure.py の対応

- 既存 `_derive_cv_info` は `('single', 5, 1)` を返すよう既に実装済み (§5.2 で
  future-proof 化)。**helper 自体の追加変更不要**。
- ただし `check_S12_part_b_choices` の三者一致 sanity check に **single mode 分岐
  が未追加**のため、以下を補う:
  - single mode: choice-section 数 == answer-slot 数 == 5 (template 固定)、
    K=1 は cv が単一整数文字列で保証される。
- S71-AP33 (answer-instruction canonical 文言) は既に single 用パターン
  `^選択肢を選んで「解答を表示」を押してください。$` を許容、**変更不要**。
- S73-AP35 (cv 形式と data-answer-type の自動判定整合) は既に single 自動判定済
  (cv が `^\d+$` で `,` を含まない場合)、**変更不要**。

#### 7. validate_content.py の対応

- positive check の `answer` 照合ロジックは **integer 単体にも対応済み**:
  - 既存実装で `isinstance(value, list)` ブランチに該当しない場合 `str(value)` を
    使うため、integer `2` は `"2"` として HTML 内検索される。
- **追加変更は不要**。

#### 8. 四 template の同期義務 + (b) refactor 発火条件

`KTX_template.html` / `KTX_template_ox4.html` / `KTX_template_msel5.html` /
`KTX_template_sc5.html` の **4 本立て**となる。

##### 同期対象と意図差分対象

- **同期対象** (4 本で byte-level 一致を維持): HEAD / `<style>` 内 CSS 全体 /
  `<script>` 内 JS 全体 / marker-legend / PART C スタブ (c-1〜c-7) /
  PART D スタブ / A-3 共通根拠スタブ (リンク先 id を除く) / footer-spec の構造。
- **意図差分対象** (各 template 固有):
  - TOC アンカー (カナ / 数字)
  - PART A 問題文行数およびラベル
  - **【見解】section の有無** (sc5 のみ)
  - A-2 解答エリア構造 (ox-grid / multi / single)
  - PART B choice-section 数およびラベル
  - sec-nav の表記

各形式の意図差分は §5.1 §3 (ox-grid-4) / §5.2 §3 (multi-select-5) /
§5.3 §3 (single-choice-5) に列挙する。

##### diff ペア数の増加

| 本数 | ペア数 | 検証コスト |
|---|---|---|
| 3 本 (§5.2 完了時) | 3 | 手動で許容 |
| **4 本 (§5.3 完了時)** | **6** | 手動境界に到達 |
| 5 本 (将来 §5.4 完了時) | 10 | CI 化必須 |
| 6 本 (将来 §5.5+) | 15 | CI 化前提でも限界 |

本セッション (§5.3) は 4 本目への到達点。手動 diff 検証の境界にあり、次の
判断ポイント (§5.4 着手前) で本格的な意思決定が必要となる。

##### (b) refactor 発火条件 (本書による正式宣言)

`docs/session-328-completion.md` §5 「三 template 同期義務の限界宣言」を引き継ぎ、
**partial 合成または JS 動的レンダリングへの移行 (= "(b) refactor")** を発火する
条件を以下に明示する:

- **AND 条件 (両方満たすこと)**:
  1. **330 PDF (combination-5) の構造調査の結果、既存 4 本のいずれの派生でも
     合理的に収まらない** ことが判明する。
  2. **形式 #6 以降の予定が 2 件以上 confirmed** となる
     (schema enum に残存する `"ranking"` / `"fill-in"` 等の実装決定が下る)。

両方を満たした時点で、330 着手前に (b) refactor を Phase 3b として実行する。
どちらか一方でも満たさない場合は (a) 5 本目追加で 330 を実装し、refactor は
形式 #6 着手時まで遅延する。

##### 330 入口で実測マージコストを記録する義務

§5.4 設計調査時 (330 PDF 構造調査と並行) に、**直前までに到達している template
同期作業の実測コスト**を以下のフォーマットで本書に追記する義務がある:

```
### §5.3 完了時点の同期実測 (記入義務)
- 326 / 327 / 328 / 329 の byte-identity 維持に要した時間:
- 4 本立て diff 6 ペアの手動 / 自動検証時間:
- §5.3 §3 意図差分テーブルから漏れた予期せぬ差分:
- (b) refactor を発火すべきと感じた主観的圧力 (1-5 スケール):
```

これにより (b) refactor 判断が「推定」ではなく「実測」に基づくものとなる。

##### 同期義務違反の検出方法 (§5.2 §8 を継承・拡張)

将来の保守において、4 本の同期義務違反を早期検出するため、以下を推奨:

1. **diff 6 ペア照合**: 任意の 2 本ペアで `diff` を取得し、差分が当該ペアの意図
   差分テーブル (§5.1 §3 / §5.2 §3 / §5.3 §3 の組み合わせ) のみであることを
   確認する。本数増加に伴い CI 化が必須に近づく。
2. **部分 diff 化**: HEAD / CSS / JS / PART C / PART D / A-3 / footer-spec の
   特定範囲のみ抽出した部分 diff で 4 本一致を直接確認する方法を推奨 (CI 化対応)。
3. **想定外差分の対処** (§5.2 §8 と同様): 意図差分テーブルに該当しない差分は
   同期不備として修正必須。新しい意図差分が必要な場合は **先に slotmap §5.N の
   テーブル更新**を行ってからコードを変更する。

#### 【見解】slot の実装方式

**採用方式: 固定 3 件の個別 slot** (`{{VIEW_A_LABEL}}` / `{{VIEW_A_BODY}}` /
`{{VIEW_B_LABEL}}` / `{{VIEW_B_BODY}}` / `{{VIEW_C_LABEL}}` / `{{VIEW_C_BODY}}`)

##### 採用理由 (動的 HTML 単一 slot 案を不採用とする根拠)

| 観点 | 固定 3 件個別 slot (採用) | 動的 HTML 単一 slot `{{VIEWS_HTML}}` (不採用) |
|---|---|---|
| render.py の追加実装 | 6 個の slot を views 配列から抽出するだけ | views 配列を HTML 文字列に組立てる関数が必要 |
| template の構造可視性 | 高い (HTML 構造が template 上で見える) | 低い (render.py を読まないと最終構造が不明) |
| HTML 構造のばらつき | なし (template で固定) | ばらつきうる (render.py の生成ロジック次第) |
| 検証の容易さ | view-block の DOM が固定で validate_structure 拡張が容易 | DOM 構造が動的で validator 拡張が複雑化 |
| 4 件以上への拡張 | slot 数追加 or 動的方式への移行 | slot 数の変化なし、ロジック側で吸収 |
| AP-37 (正解値リテラル) リスク | view 本文は学説本文で正解番号を含まないため非該当 | 同 |

3 件固定で運用し、template に構造を残す方が **保守性・検証性で優位**。

##### 4 件以上 (D 説 / E 説 等) が必要になった場合の対処

- 将来、4 件以上の【見解】を持つ問題が新規入手された場合、以下のいずれかへ移行:
  - **(α) slot 数の追加**: `{{VIEW_D_LABEL}}` / `{{VIEW_D_BODY}}` を template と
    render.py に追加。schema の `$defs.View` の `label.enum` も拡張。少数 (最大 5 件
    程度) なら最も簡単。
  - **(β) 動的 HTML 生成への移行**: `{{VIEWS_HTML}}` 単一 slot 化し、render.py で
    HTML を組立。views の件数が可変・問題ごとに異なる場合に必要。
- 本フェーズでは (α) を維持。(β) への移行は `view` の件数バリエーションが
  3 件以上のパターンで出現したときに発火 (slotmap §5.10+ 候補)。

##### body のマークアップ規則

- `body` フィールドは plain text (HTML エスケープなし、改行は `\n` で表現)。
- 強調や引用が必要な場合は将来 `view.body_html` フィールドを追加検討
  (本フェーズではスコープ外)。
- `body` 内に正解番号や罪名固有句を含めない (AP-37 抵触回避)。

#### 将来の一般化 (保留)

- 形式 #5 (combination-5 = 330) は **§5.4 として別途設計**する (本書 §5.3 では
  スコープ外)。
- 形式 #6 以降 (ranking / fill-in 等) は本書 §8 の (b) refactor 発火条件が
  該当する可能性が高く、その時点で template 別ファイル方式を廃して
  **partial 合成または JS 動的レンダリング**に移行する。
- §5.3 配下の【見解】slot は本フェーズで固定 3 件 (α 方式)、将来の D/E 件数
  バリエーションが出れば §5.10+ で β 方式 (動的 HTML) に移行検討。

#### AP-37 抵触回避ガイド (継承)

`answer_explanation` フィールドの値は、326 / 327 / 328 と同じく
「解答および各記述の正誤判定」を基本句とする。罪名・正解番号・PDF タイトル
固有句を含めないこと (validate_structure.py の S74-AP37 が正解値リテラルの
先頭混入を検知)。single-choice 系でも同じ基本句を流用する。

加えて、**【見解】の `body` 内にも正解番号 / 罪名を含めない** こと。
学説の本文自体は罪固有句を含んでよい (例: 「器物損壊罪の『損壊』とは…」) が、
解答に直結する数字 (「正解は 2」等) は禁止。

#### crime / source 表記揺れの取り扱い (§5.1 §7 / §5.2 を継承)

- 329 の PDF タイトルは「信書隠匿罪と器物損壊罪」と **2 つの罪名併記**。
- **採用方針**: `problems/329.json` の `crime` 値を **`"器物損壊罪"` (CRIME_SIGNATURES
  の既存キー) に統一**し、`allowed_cross_refs` に `["信書隠匿罪"]` を明示。
  - validate_content の negative check で「器物損壊罪」シグネチャ (`261条`,
    `効用侵害`) が current crime として skip される。
  - 「信書隠匿罪」は現在 CRIME_SIGNATURES に未登録のため、`allowed_cross_refs`
    に書いても効果はないが、**設計意図のドキュメンテーションとして明示**しておく
    (将来 CRIME_SIGNATURES に追加された時点で自動的に有効化される)。
- **CRIME_SIGNATURES 拡張 (信書隠匿罪 = `["263条", "信書隠匿"]` 等の追加) は
  別案件として `§5.9` で扱う** (本書 §5.3 ではスコープ外)。
- `source` は司法試験 `"H20-16"` 形式を採用 (継承)。

---

### §5.4 combination-N 形式分岐 + 【組合せ】slot + 二系統ラベル混在 (R-4: combination-5 対応)

#### 背景

問題 330 (予備 H23-10、毀棄罪及び損壊罪) は **ア〜オ 5 記述 + 1〜5 組合せ選択肢**
の二層構造を持ち、最終的に「正しい記述の組合せはどれか」を 1〜5 の単一選択で答える。
具体的には:

- 【見解】 A説 / B説 の 2 学説が提示される (329 の 3 件 A/B/C とは異なり、本問では 2 件)
- 【記述】 ア〜オ の 5 件、各々に独立した verdict (正/誤) が存在し、PART B で個別に
  解説される
- 【組合せ】 5 件 (1=ア・イ / 2=ア・オ / 3=イ・ウ / 4=ウ・エ / 5=エ・オ)、各々
  ア〜オ から 2 つの記述を組合せたもの
- 正解は 1〜5 のうち 1 つ (本問では `3` = イ・ウ で、両記述とも正しい)

**canonical KTX301 と構造的に同型** であるため、構造参考としては最も近い既存実例だが、
PATCH §1 / slotmap §5.1〜§5.3 §4 の原則「canonical の本文・解説を流用しない」は
本フェーズでも継続適用する (構造参考は OK、内容流用は NG)。

二系統ラベル混在 (記述 ア〜オ + 組合せ 1〜5) という特性により、既存 4 本立て
template のいずれの派生でも合理的に収まることが調査で判明 (`docs/` 配下の調査記録
参照)。**(b) refactor 発火条件 AND 2 つは現時点で両方不充足**のため、(a) 戦略で
5 本目 template を追加する方針を採る。

### 決定事項

#### 1. schema 拡張

- `schema/problem.schema.json` の `instruction_type` enum に `"combination-5"` を
  追加する (add only)。当面サポートは `ox-grid-5` / `ox-grid-4` / `multi-select-5` /
  `single-choice-5` / `combination-5` の 5 値。
- **`$defs.Combination` を新規定義** する:
  - `{ label: string (enum ["1","2","3","4","5"]), members: array of string (各値は
    記述ラベル ア〜オ の enum で 1 個以上) }`
  - `additionalProperties: false`
- **`properties.combinations`** を新規追加:
  - `type: array, items: { $ref: "#/$defs/Combination" }, minItems: 5, maxItems: 5`
  - **optional フィールド**: `combination-5` 系のみで使用、ox-grid / multi-select /
    single-choice 系では未指定 (後方互換維持)
  - `conditional required` は導入しない (schema をシンプルに保つ。combination-5 を
    指定したのに combinations が未指定の場合は render.py / template 側の placeholder
    残存で fail する)
- `answer` フィールドは **既存 `oneOf` 第 3 ブランチ (integer 単体)** を再利用。
  追加変更不要 (330 の `answer: 3` で対応)。
- `$defs.View` / `properties.views` は **329 の 3 件方式を維持**。combination-5 では
  views を使用しない (本書 §5.4「【見解】slot の扱い」参照)。
- 後方互換: 既存 326.json / 327.json / 328.json / 329.json は引き続き valid。

#### 2. テンプレート構成

- `templates/KTX_template_comb5.html` を新規作成する。**template 本数は 5 本目**に
  到達する。
- ベース選定: 設計調査で **α (KTX_template.html cp ベース) / β (KTX_template_sc5.html
  cp ベース) / γ (ground-up 新規)** を定量比較した結果、**新規 5 本目を作成する方針
  (実体は γ ラベル相当、cp 元には KTX_template.html を選択)** を採用する。
  - 選定理由 (定量):
    - 330 の記述ラベル **ア〜オ が KTX_template.html (ox-grid-5) の既存 hardcoded
      ラベル系統と完全一致**。TOC / PART B nav text / PART B コメント / sec-nav /
      part-title 等の hardcoded ラベル text を **1 つも触らずに済む**。
    - β (sc5 cp ベース) は 1〜5 → ア〜オ への置換が約 20 行に渡り散発的に発生し、
      意図差分テーブル管理が複雑化する。
    - α / γ の差分行数は約 50 行で β より約 20% 少ない。
    - α と γ の最終成果物はほぼ同一だが、γ (ground-up) は ~2,820 行をゼロから書く
      オーバーヘッドがあるため、cp + edit 方式 (α 流) を選択する。
- 単一 template に CSS/JS 分岐を埋め込む案は採用しない (slotmap §5.1 §2 / §5.2 §2 /
  §5.3 §2 と同じ理由)。

#### 3. 意図的な差分箇所 (KTX_template.html ↔ KTX_template_comb5.html)

差分は以下 4 種類のみに限定し、それ以外は base (`KTX_template.html`) と byte-level
同期を義務とする:

| 差分箇所 | KTX_template.html (ox-grid-5) | KTX_template_comb5.html (combination-5) |
|---|---|---|
| PART A 見出しコメント | `PART A ── 問題情報（ox-grid-5 形式）` | `PART A ── 問題情報（combination-5 形式）` |
| A-2 解答エリア（**全面書換**） | ox-grid 構造（`ox-row` × 5、各行 ○× ボタン） | **single 1〜5 ボタン構造** (`data-answer-type="single"`、`answer-row` + `answer-slot` × 5、各 button `data-num`/`data-value` 1-5)、 selection-counter なし |
| A-2 `<h3>` および `answer-instruction` 文言 | 「各記述の正誤を判定」/「各記述について「正しい (1)」か「誤っている (2)」を選んでください。」 | 「正しい記述の組合せを選択」/「選択肢を選んで「解答を表示」を押してください。」(S71-AP33 single canonical 文言) |
| **【組合せ】section 新規追加** (PART A 内、問題文の【記述】群の後ろ、A-2 の前) | 存在しない | **新規追加**: `<section class="combinations-section" id="part-a-combinations">` + 5 つの `<div class="combo-block">`、各々 `{{COMBO_1_LABEL}}` / `{{COMBO_1_MEMBERS}}` 〜 `{{COMBO_5_LABEL}}` / `{{COMBO_5_MEMBERS}}` の 10 個の slot を持つ |

ラベル系統については **変更不要** (KTX_template.html と一致):
- TOC アンカー (ア〜オ 5 件) は同じ
- PART A 問題文 (`{{CHOICE_*_LABEL}}` slot 駆動で ア〜オ) は同じ
- PART B 5 件の choice-section / parity / nav 表記 (記述ア〜記述オ) は同じ
- A-3 sec-nav (「↑記述オ」) は同じ
- セクションコメント (「記述ア」〜「記述オ」) は同じ

HEAD / CSS / JS / marker-legend / PART C スタブ / PART D スタブ / A-3 共通根拠スタブ
/ footer-spec の構造はすべて **byte-level 同期**。CSS / JS は v8.11.3 の 3 Type 対応
(single / multi / ox-grid) を持ち、本 template の `data-answer-type="single"` も
canonical KTX301 と同じ挙動で動作する。**CSS / JS の追加・変更は一切不要**。

#### 4. canonical 構成

- 形式別 canonical は **追加しない** (slotmap §5.1 §4 / §5.2 §4 / §5.3 §4 の原則を
  踏襲)。
- `canonical/KTX301.html` を引き続き構造参考として固定する。**combination-5 は
  canonical KTX301 と構造的に同型** となるため、本フェーズで初めて canonical が
  「構造的に近い既存実例」として参照価値を持つ。ただし PATCH §1 により
  **本文・解説のコピーは禁止**。
- combination-N 系の運用 reference は「最初に 3 段検証 (render → structure →
  content) を完走した実例 HTML」とする:
  - ox-grid-5         → `outputs/tx/刑TX/刑TX326.html`
  - ox-grid-4         → `outputs/tx/刑TX/刑TX327.html`
  - multi-select-5    → `outputs/tx/刑TX/刑TX328.html`
  - single-choice-5   → `outputs/tx/刑TX/刑TX329.html`
  - **combination-5   → 完成後の `outputs/tx/刑TX/刑TX330.html`**

#### 5. render.py の template 選択分岐

- `scripts/render.py` の `TEMPLATE_PATHS` dict に `"combination-5"` を追加:
  - `"ox-grid-5"`        → `templates/KTX_template.html`
  - `"ox-grid-4"`        → `templates/KTX_template_ox4.html`
  - `"multi-select-5"`   → `templates/KTX_template_msel5.html`
  - `"single-choice-5"`  → `templates/KTX_template_sc5.html`
  - **`"combination-5"`  → `templates/KTX_template_comb5.html`**
- `LABEL_TO_LETTER` は ア〜コ + 1〜5 の既存マッピングを流用 (追加変更不要)。
- `build_slot_dict` に **`combinations` slot の展開ロジック**を追加:
  - JSON の `combinations` 配列 (長さ 5、label 1〜5 固定) から 10 個の slot を構築:
    - `COMBO_1_LABEL`, `COMBO_1_MEMBERS`
    - `COMBO_2_LABEL`, `COMBO_2_MEMBERS`
    - `COMBO_3_LABEL`, `COMBO_3_MEMBERS`
    - `COMBO_4_LABEL`, `COMBO_4_MEMBERS`
    - `COMBO_5_LABEL`, `COMBO_5_MEMBERS`
  - `MEMBERS` は配列を **全角中黒「・」連結** で文字列化 (例: `["ア", "イ"]` →
    `"ア・イ"`)。
  - `combinations` が未指定 (ox-grid / multi-select / single-choice 系) の場合は
    空文字を入れる (該当 template に placeholder が無いため無害)。
- VIEW_A/B/C slot (sc5 由来、329 用) は **引き続き併存して供給** するが、
  combination-5 template には placeholder が存在しないため使用されない (slot 辞書
  に値が入っていても無害)。
- `_format_answer` は **既存 integer 単体対応** (`str(3)` → `"3"`) で 330 に対応済
  (slotmap §5.2 で future-proof 化、§5.3 で integer 単体採用)。追加変更不要。
- **デフォルト挙動**: `instruction_type` が dict に無い値・未指定の場合は
  既存 `KTX_template.html` (ox-grid-5) にフォールバック (§5.1 §5 / §5.2 §5 /
  §5.3 §5 と同方針)。

#### 6. validate_structure.py の動的化

- 既存 `_derive_cv_info` helper は `('single', 5, 1)` を返す対応が **§5.2 で
  future-proof 化済み**。combination-5 の cv (例: `"3"`) も既に `single` mode と
  判定されるため、helper 自体の追加変更不要。
- `check_S12_part_b_choices` の三者一致 sanity check に追加の組合せ系分岐は不要
  (combination-5 は内部的に `single` mode として扱われ、既存 single 分岐で
  choice-section 5 件 + answer-slot 5 件の整合性チェックが動作する)。
- **S78 views-section 検査の緩和**:
  - 既存: views-section が存在する場合、view-block が固定 3 件を要求 (single-choice-5 用)
  - 拡張: **combination-5 では views-section 自体が存在しない** ため、helper の
    既存実装 (views-section が存在しない HTML では何もしない) で対応済。
    追加変更不要。
- **S79 combinations-section 検査を新設**:
  - `<section class="combinations-section">` が存在する場合、`<div class="combo-block">`
    が固定 5 件であることを ERROR チェック。
  - 各 combo-block に「label 表示要素」と「members 表示要素」が存在することを
    WARN チェック。
  - combinations-section が存在しない HTML (326-329) では何もしない。
- S73-AP35 / S71-AP33 single 系は既登録、追加変更不要。

#### 7. 五 template の同期義務 + (b) refactor 発火条件

`KTX_template.html` / `KTX_template_ox4.html` / `KTX_template_msel5.html` /
`KTX_template_sc5.html` / `KTX_template_comb5.html` の **5 本立て**となる。

##### 同期対象と意図差分対象

- **同期対象** (5 本で byte-level 一致を維持): HEAD / `<style>` 内 CSS 全体 /
  `<script>` 内 JS 全体 / marker-legend / PART C スタブ (c-1〜c-7) /
  PART D スタブ / A-3 共通根拠スタブ (リンク先 id を除く) / footer-spec の構造。
- **意図差分対象** (各 template 固有):
  - TOC アンカー (カナ / 数字)
  - PART A 問題文行数およびラベル
  - **【見解】section の有無** (sc5 のみ、固定 3 件方式)
  - **【組合せ】section の有無** (comb5 のみ、固定 5 件方式)
  - A-2 解答エリア構造 (ox-grid / multi / single)
  - PART B choice-section 数およびラベル
  - sec-nav の表記

各形式の意図差分は §5.1 §3 (ox-grid-4) / §5.2 §3 (multi-select-5) /
§5.3 §3 (single-choice-5) / §5.4 §3 (combination-5) に列挙する。

##### diff ペア数の増加

| 本数 | ペア数 | 検証コスト |
|---|---|---|
| 3 本 (§5.2 完了時) | 3 | 手動で許容 |
| 4 本 (§5.3 完了時) | 6 | 手動境界に到達 |
| **5 本 (本書 §5.4 完了時)** | **10** | **CI 化が現実的に必須** |
| 6 本 (将来 §5.5+) | 15 | CI 化前提でも限界 |

本書 §5.4 は 5 本目への到達点。手動 diff 検証の現実的な限界を超え、**CI 化スクリプト
の導入が緊急性を帯びる**。

##### (b) refactor 発火条件の判定 (本書による正式判定)

`docs/session-329-completion.md` および本書 §5.4 設計調査の結果に基づき、
slotmap §5.3 §8 で正式宣言された **AND 条件 2 つ** を再判定する:

| 条件 | 判定 | 論拠 |
|---|---|---|
| ① 330 PDF が既存 4 本のいずれの派生でも合理的に収まらない | **不充足** | KTX_template.html (ox-grid-5) cp ベースで約 50 line diff として合理的に収まる (本書 §5.4 §3 意図差分テーブル) |
| ② 形式 #6 以降の予定が 2 件以上 confirmed | **不充足** | `inputs/tx-pdfs/` には 326-330 の 5 件のみ存在、331 以降の PDF / 確定仕様は無し |

→ **AND 条件総合: False → (b) refactor 発火しない**

(a) 戦略継続: 5 本目 template `KTX_template_comb5.html` を新規作成して 330 に対応。

##### 330 完走直後に実測マージコストを記録する義務

slotmap §5.3 §8 の記入義務を引き継ぎ、本書 §5.4 §8 に「完了時点の同期実測」
セクションを設置 (空欄、330 完走後に埋める)。

**「これにより形式 #6 入口での再評価が『推定』ではなく『実測』に基づく」** という
原則を slotmap §5.3 §8 から継承する。330 完走後の実測値が次の判断 (CI 化 / refactor)
の基礎となる。

##### 再評価のトリガー (OR 条件、いずれかが発動したら再評価)

| トリガー | 内容 | 期待される対応 |
|---|---|---|
| **形式 #6 の PDF が `inputs/tx-pdfs/` に追加される時点** | `331.pdf` 以降が入力ディレクトリに現れた瞬間 | 形式調査を実施 → 既存 5 本のいずれかの派生で収まるか判定 → 収まらなければ条件 ① 充足へ |
| **新規形式の実装決定がユーザーから明示された時点** | 「次に ranking を実装する」等の指示 | 1 件 confirmed → (a) 戦略継続、2 件以上 confirmed → 条件 ② 充足へ |
| **緊急トリガー: 5 本立て同期義務違反の実測コストが手動限界を超えた時点** | 330 完走後の主観的圧力が 3.5/5 以上に到達した場合 | AND 条件外の緊急トリガーとして (b) refactor 検討を再開 |
| **CI 化スクリプト導入後の実測値悪化** | CI で同期義務違反が頻発する場合 | (b) refactor の検討を再開 |

##### 再評価の時期目安

| 時期 | 再評価項目 |
|---|---|
| **330 完走直後** (5 本立て確立時点) | 5 本立て diff 10 ペアの手動 / 自動検証実測コストを記録 (本書 §5.4 §8 義務遂行)。主観的圧力 (1-5 スケール) を再評価し記録 |
| **次セッション** (331 以降の問題が来た時、または整備期) | (a) WARN 4 系統消化 (§5.5-§5.8) / (b) CI 化スクリプト導入 / (c) 形式 #6 入口で AND 条件再判定 |
| **形式 #6 入口** (331+ PDF または新形式 confirmed 時) | 必ず AND 条件 ① / ② を再判定。発火条件充足なら (b) refactor を優先タスク化 |

##### 同期義務違反の検出方法 (§5.2 §8 / §5.3 §8 を継承・拡張)

- **diff 10 ペア照合**: 5 本のうち任意の 2 本ペアを 10 通り取得し、差分が当該ペアの
  意図差分テーブル (§5.1 §3 / §5.2 §3 / §5.3 §3 / §5.4 §3 の組み合わせ) のみで
  あることを確認する。本数増加により **CI 化が必須レベル**に到達。
- **部分 diff 化**: HEAD / CSS / JS / PART C / PART D / A-3 / footer-spec の
  特定範囲のみ抽出した部分 diff で 5 本一致を直接確認する方法を **CI 化対応として
  推奨**。
- **想定外差分の対処** (§5.2 §8 / §5.3 §8 と同様): 意図差分テーブルに該当しない
  差分は同期不備として修正必須。新しい意図差分が必要な場合は **先に slotmap §5.N の
  テーブル更新**を行ってからコードを変更する。

#### 8. 五 template 完了時点の同期実測 (記入義務、330 完走後に記入)

slotmap §5.3 §8 で確立した記録フォーマットを継承し、330 完走時に以下を本書に
追記する義務がある。**現時点では空欄**として用意:

```
### §5.4 完了時点の同期実測 (330 完走時の実測値、2026-05-18 記入)

- 326 / 327 / 328 / 329 / 330 の byte-identity 維持に要した時間:
    本シリーズ累計 約 110 分 (約 1 時間 50 分)。
    内訳: 326-327 セッション 約 30 分 (regression 確立)、
          328 セッション 約 25 分 (三重 regression)、
          329 セッション 約 25 分 (三重 regression)、
          330 セッション 約 30 分 (四重 regression + 五 template diff 検証)。

- 5 本立て diff 10 ペアの手動 / 自動検証時間:
    自動 (PowerShell Compare-Object × 10 ペア): **589 ms** (平均 59 ms/ペア)。
    手動相当 (各ペアを目視 + 意図差分テーブル参照): 約 10-15 分。
    自動検証は手動の約 1000 倍速、CI 化の効果は明白。

- §5.4 §3 意図差分テーブルから漏れた予期せぬ差分:
    なし。意図差分 4 種類 (PART A 見出しコメント / A-2 全面書換 /
    A-2 h3 + answer-instruction 文言 / 【組合せ】section 新規追加) のみで
    完結し、想定外の追加変更は発生しなかった。
    diff 10 ペアの実測結果も意図差分テーブル通り (一例: KTX_template.html ↔
    KTX_template_comb5.html = 80 行差、ox4 系・msel5 系・sc5 系ペアも
    両者の意図差分の和差で説明可能な範囲)。

- (b) refactor を発火すべきと感じた主観的圧力 (1-5 スケール):
    **3 / 5** (4 本立て時 §5.3 §8 記入値 2/5 から +1 上昇)。
    実装は問題なく完走、template 派生による設計は明快で意図差分テーブルも
    機能した。ただし共通部分の同期義務が 10 ペアに増え、手動レビューでの
    全件確認は現実的に困難。CI 化を導入すれば 1 秒未満で済むため、refactor
    自体を急ぐ必要は低い。発火条件 AND (①330 が既存 4 本で収まらない /
    ②形式 #6 以降 2 件以上 confirmed) はいずれも引き続き不充足。

- CI 化スクリプトの導入時期判断:
    **次セッション (整備期) で最優先タスクとして導入推奨**。
    実装規模: `scripts/check_template_sync.py` 新設、10 ペアの Compare-Object
    相当を Python で実装、意図差分テーブル (slotmap §5.1〜§5.4 §3) を参照して
    各ペアの差分が想定範囲内かを判定。所要工数 1-2 時間と試算。
    並行して WARN 4 系統 (S14 drill-block / S17×N professor / S51
    ktx301-canon / S71-AP33 文言調整) の slotmap §5.5-§5.8 消化を実施可能。
```

これにより形式 #6 入口での再評価が「推定」ではなく「実測」に基づくものとなる。

#### 【見解】slot の扱い

- **combination-5 では【見解】slot (sc5 由来の `VIEW_A/B/C_LABEL/BODY` 6 個) を
  使用しない**。
- 330 PDF の【見解】 A説 / B説 の内容は、template に専用 section を新設せず、
  以下のいずれかで対処:
  - JSON の `instruction` フィールド内に inline で含める (現実的、最小限の追加実装)
  - 将来 combination-5 専用の【見解】slot を §5.10+ として追加する案 (本フェーズでは
    保留)
- schema 上 `properties.views` は **329 と同じく optional のまま**、330.json では
  未指定とする。これにより 329 の 3 件方式 (slotmap §5.3 §8) と 330 の non-view 方式
  が schema レベルで完全に分離される。
- `render.py` の `build_slot_dict` 内 views 展開ロジックは引き続き存在するが、
  330 では `views` が空配列 (または未指定) なので VIEW_A/B/C slot はすべて空文字。
  combination-5 template には VIEW_* placeholder が存在しないため、空文字が入っても
  害なし。
- 将来、combination 系問題で構造化された【見解】が必要になった場合、§5.10+ の
  単発案件として **combination-5 用の view 系構造** を新設するか、sc5 由来の
  `properties.views` を combination-5 でも有効化する schema 拡張を検討する
  (本フェーズではスコープ外)。

#### 将来の一般化 (保留)

- 形式 #6 (例: ranking、fill-in) が必要になった場合、本書 §7 の (b) refactor 発火
  条件を再判定する。AND 条件が充足された時点で、template 別ファイル方式を廃して
  **partial 合成または JS 動的レンダリング**に移行する。
- 移行候補:
  - **(a) JS による行動的レンダリング**: 単一 template に PART A / A-2 を空のコンテナ
    として配置し、ランタイムで `instruction_type` ベースに DOM 構築。
  - **(b) JSON 駆動の partial 合成**: render.py を Jinja2 等テンプレエンジンに移行し、
    形式ごとの partial HTML を持ち、ループ合成。
- 本フェーズ (combination-5) では (a)/(b) いずれも採用せず、5 本目を追加する形で
  対処する。CI 化スクリプトの導入が次の優先課題。

##### 再評価の時期目安 (再掲、本書 §7 から)

| 時期 | 再評価項目 |
|---|---|
| **330 完走直後** | 5 本立て diff 10 ペアの手動 / 自動検証実測コストを記録 (§5.4 §8 義務遂行)、主観的圧力を再評価 |
| **次セッション (331+ または整備期)** | WARN 4 系統消化 / CI 化スクリプト導入 / 形式 #6 入口で AND 条件再判定 |
| **形式 #6 入口** | AND 条件 ① / ② を再判定、発火条件充足なら (b) refactor を優先タスク化 |

**「これにより形式 #6 入口での再評価が『推定』ではなく『実測』に基づくものとなる」**
という原則を再強調する。330 完走後に §5.4 §8 を埋めない限り、次セッションでの
判断材料が不足する。

#### AP-37 抵触回避ガイド (継承)

`answer_explanation` フィールドの値は、326 / 327 / 328 / 329 と同じく
「解答および各記述の正誤判定」を基本句とする。罪名・正解番号・PDF タイトル
固有句を含めないこと (validate_structure.py の S74-AP37 が正解値リテラルの
先頭混入を検知)。combination-5 系でも同じ基本句を流用する。

加えて、**【組合せ】section の `members` 表記 (例: 「ア・イ」)** には正解番号や
罪固有句を含めない。学説名 (A説 / B説) も同様 (combinations の members は記述
ラベルのみで構成、その他の概念を混入させない)。

#### crime / source 表記揺れの取り扱い (§5.1 §7 / §5.2 / §5.3 を継承)

- 330 の PDF タイトルは「毀棄罪及び損壊罪」。
- **採用方針**: `problems/330.json` の `crime` 値を **`"器物損壊罪"` (CRIME_SIGNATURES
  の既存キー) に統一**し、`allowed_cross_refs` に `["信書隠匿罪"]` を明示 (329 と
  同方針)。
  - validate_content の negative check で「器物損壊罪」シグネチャ (`261条`,
    `効用侵害`) が current crime として skip される。
  - 「信書隠匿罪」は現在 CRIME_SIGNATURES に未登録のため、`allowed_cross_refs`
    に書いても効果はないが、**設計意図のドキュメンテーションとして明示**しておく
    (329 と同様、将来 CRIME_SIGNATURES に追加された時点で自動的に有効化される)。
- **CRIME_SIGNATURES 拡張 (信書隠匿罪 / 毀棄罪 / 損壊罪 等の追加) は別案件として
  `§5.9` で継続遅延** (本書 §5.4 ではスコープ外、§5.3 §「crime 表記揺れ」と同方針)。
- `source` は予備独自問題 `"予備H23-10"` 形式を採用 (326/327 と同方針、継承)。

---

### §5.5 PART D drill-block 本格実装 (R-W5: S14 解消、WARN 完全消滅)

#### 背景

S14 は `<section class="section recall-arena" id="part-d">` 配下に 12 件の
`drill-block` を要求する検査。326-330 全 5 件で PART D が **スタブのまま** (TODO
コメント 1 行のみ) のため、S14 が全件で WARN を発火。本案件で 12 件 × 5 形式 =
**60 件の drill-block を実装**し、WARN 系統を **完全消滅** させる。

##### canonical KTX301 の drill-block 構造

canonical/KTX301.html L3056-L3303 に詳細な実装：
- `<section class="section recall-arena" id="part-d">` 全体
- D-1 Rapid-Fire ○×ドリル タイトル
- arena-intro 紹介文
- arena-counter プログレス表示（12 件カウント、correct/incorrect 集計）
- `<div class="drill-block">` × 12（各々 drill-label + self-check-quiz + 解答）
- arena-scorecard 最終結果表示
- back-to-top

各 drill-block は:
- drill-num (DRILL 01-12) + drill-tag (例：「記述ア / 詐欺と背任の包含関係」)
- self-check-quiz with `data-arena="1"`, `data-correct-value="○"` または `"×"`,
  `data-explanation`
- quiz-question (○× で問う 1-2 文)
- quiz-buttons (○ / × ボタン、各々 `data-correct` 真偽)
- quiz-answer (hidden、結果と一言解説)

#### 決定事項

#### 1. 設計 3 案の比較

| 観点 | (a) JSON drill_blocks フィールド | (b) 別 JSON ファイル | (c) HTML 直接埋込 |
|---|---|---|---|
| 既存パターン整合 | ✅ views/combinations/professor と同型 | ❌ 既存にない別軸 | ❌ 既存にない別軸 |
| 既存問題への影響 | ✅ optional で後方互換 | ❌ 2 ファイル管理 | ❌ template に内容固定で問題ごと違う drill 不可 |
| render.py 拡張 | ✅ slot 展開で済む | △ 2 ファイル読込追加 | × 不要だが現実的に問題ごとに違う drill が必要なため (c) は不可 |
| 5 problems への影響 | 各 JSON に 12 件追加 | 各 problem に新 .json | template 改修要 |
| schema validation | ✅ 既存と同じ仕組み | 別 schema 必要 | ❌ なし |
| AP-37 抵触リスク | 同 (a) と同等 | 同 | 同 |
| **推奨** | ✅ **採用** | ✗ | ✗ (現実的に不可) |

##### (a) 採用理由

- 既存 §5.3 (views) / §5.4 (combinations) / §5.6 (professor) と同パターン。設計
  一貫性が高く、開発者の学習コスト低。
- render.py が `problem.get("drill_blocks", [])` で安全にループ展開可能。
- schema による厳格な型検証 (12 件固定、○× enum 等) が可能。
- 既存 326-330.json は drill_blocks 未指定で引き続き valid (optional)。

##### (c) を不採用とする決定的理由

各問題は内容が異なるため、template 1 つに 60 件の drill を埋め込むことは不可能。
各 problem の論点固有の drill が必要であり、JSON 駆動が必須。

##### (b) を不採用とする理由

別ファイル化は 2 ファイル管理の複雑性を招くだけで、メリットは marginal
(JSON サイズ低減のみ)。(a) で各 problem.json が ~50% 増加するが、それでも 10-20 KB
程度で管理容易な範囲。

#### 2. schema 拡張

`$defs.DrillBlock` を新規定義 + `properties.drill_blocks` を optional 追加:

```json
"$defs": {
  "DrillBlock": {
    "type": "object",
    "required": ["num", "tag", "question", "correct", "explanation"],
    "additionalProperties": false,
    "properties": {
      "num": { "type": "string", "pattern": "^[0-9]{2}$" },
      "tag": { "type": "string", "minLength": 3 },
      "question": { "type": "string", "minLength": 20 },
      "correct": { "type": "string", "enum": ["○", "×"] },
      "explanation": { "type": "string", "minLength": 10 }
    }
  }
}
```

`properties.drill_blocks`: `array` items `$ref DrillBlock`, `minItems: 12`,
`maxItems: 12`, optional.

#### 3. テンプレート構成

5 templates の PART D スタブを **12 drill-block の完全構造に置換**:

```html
<section class="section recall-arena" id="part-d">
  <nav class="sec-nav"><a href="#c-7">←C-7</a><a href="#top">↑先頭</a></nav>
  <h2 class="section-title"><span class="sec-icon">⚔</span>D-1 Rapid-Fire ○×ドリル（全12問）</h2>
  <p class="arena-intro">PART B の論点を 12 問の即答ドリルで定着させる。各記述の核心法理を ○× で固める。</p>
  <div class="arena-counter" id="arena-counter">...</div>
  <div class="drill-block">
    <div class="drill-label">
      <span class="drill-num">DRILL&nbsp;01</span>
      <span class="drill-tag">{{DRILL_01_TAG}}</span>
    </div>
    <div class="self-check-quiz" data-arena="1"
         data-correct-value="{{DRILL_01_CORRECT}}"
         data-explanation="{{DRILL_01_EXPLANATION}}">
      <div class="quiz-question">{{DRILL_01_QUESTION}}</div>
      <div class="quiz-buttons">
        <button class="quiz-btn" type="button" data-correct="{{DRILL_01_O_CORRECT}}" data-value="○">○</button>
        <button class="quiz-btn" type="button" data-correct="{{DRILL_01_X_CORRECT}}" data-value="×">×</button>
      </div>
      <div class="quiz-answer" hidden>
        <span class="quiz-result"></span>{{DRILL_01_EXPLANATION}}
      </div>
    </div>
  </div>
  ... (DRILL 02-12 同様)
  <div class="arena-scorecard" id="arena-scorecard" hidden>...</div>
</section>
```

12 drill-block × 7 slots/drill = **84 slot/template** × 5 templates = 420 slot 配置。
**5 templates すべて構造同一**（slot 値は JSON 駆動で問題ごとに変わる）。

#### 4. render.py の対応

`build_slot_dict` に drill_blocks 展開:

```python
for i, drill in enumerate(problem.get("drill_blocks", []), 1):
    num_str = f"{i:02d}"
    correct = drill.get("correct", "")
    slots[f"DRILL_{num_str}_TAG"] = drill.get("tag", "")
    slots[f"DRILL_{num_str}_QUESTION"] = drill.get("question", "")
    slots[f"DRILL_{num_str}_CORRECT"] = correct
    slots[f"DRILL_{num_str}_EXPLANATION"] = drill.get("explanation", "")
    slots[f"DRILL_{num_str}_O_CORRECT"] = "true" if correct == "○" else "false"
    slots[f"DRILL_{num_str}_X_CORRECT"] = "true" if correct == "×" else "false"
```

drill_blocks 未指定の旧問題は全 slot に空文字、template 上の drill-block は
空のまま表示（HTML 構造は維持、内容が空）。

#### 5. check_template_sync.py への影響

5 templates すべてに同じ PART D 構造を追加 → `part_c_d` セクションは
`sync_required=True` だが、5 本同期で同じ追加なので **hash 同期維持**。
意図差分 dict 操作は **不要**。

#### 6. byte-identity への影響

5 件全件で HTML 大幅変化。各 problem あたり 12 drill × 200-300 chars (slot 値 +
HTML 構造) = 約 **+5,000 bytes/problem**、5 件合計約 **+25 KB**。

#### 7. 60 件の drill 内容生成方針

各 problem 12 件は以下の構成で生成:
- 各 choice ごとに 2 問 (verdict 確認 + 論点深堀) = 8-10 問
- 横断問題 2-4 問 (全 choices を貫く核心法理、判例の射程)
- 計 12 問 (5-choice 問題: 5×2+2=12 / 4-choice 問題 327: 4×2+4=12 or 4×3=12)
- 各 drill: question 50-100 chars + explanation 50-150 chars
- AP-37 抵触なし (罪名・正解番号を冒頭に置かない、論点で開始)

#### 8. 想定リスク (R1-R5)

| ID | リスク | 想定影響 | 回避策 |
|---|---|---|---|
| R1 | 60 件の生成負荷 | 時間と context window 圧迫 | 各 problem の verdict + explanation を起点に 12 問を効率的に生成。論点の核を ○× で問う |
| R2 | AP-37 抵触 | 正解番号 / 罪名固有句が冒頭に来ると WARN | 「判例によれば…」「A説では…」等の中立な書き出しを統一 |
| R3 | drill の質低下 | 学習価値ゼロのプレースホルダ化 | 各 drill は具体的な論点を ○× で問う形式に。「○○の場合 ××が成立する」型 |
| R4 | quiz-buttons の data-correct 真偽逆 | ボタンクリック時の正解判定が逆転 | render.py で `correct == "○"` の判定を厳密に。test render で確認 |
| R5 | template 改修で既存 §5.6 への regression | sub-card professor 構造が PART D 改修で破壊 | PART D は choice-section の外、A-3 と c-1-7 の間でなく c-7 と footer の間。choice-section は別領域、影響なし |

#### 9. 実装手順

1. schema/problem.schema.json: $defs.DrillBlock 追加、properties.drill_blocks 追加
2. 5 templates の PART D スタブを 12 drill-block 構造に置換
3. scripts/render.py: build_slot_dict に DRILL_NN_* 7 slot × 12 = 84 slot 追加
4. check_template_sync.py: exit 0 確認 (part_c_d 5 本同期維持)
5. problems/{326-330}.json: 各 12 drill (計 60 件) 生成
6. 5 件再 render
7. validate_structure: WARN 1→0 を確認 (S14 消滅 = **WARN 完全消滅**)
8. validate_content: regression なし
9. slotmap §5.5 §X に実測値記入

#### 10. §5.5 完了時点の同期実測 (記入義務、実装完了後に記入)

```
### §5.5 完了時点の同期実測 (実装完了時の実測値、2026-05-18 記入)

- 実装に要した時間:
    約 1.5 時間 (見積 2-3 時間 → 効率化で短縮)。内訳: schema 5 min + 5 templates の
    PART D 構造置換 20 min + render.py drill slot 拡張 5 min + 60 drill 生成 +
    JSON 編集 50 min + ○:×=6:6 バランス調整 10 min + 検証 5 min。

- 修正前後の HTML サイズ変化 (326-330 各々):

  | 問題 ID | §5.6 後 bytes | §5.5 後 bytes | Δ bytes | choices |
  |---|---:|---:|---:|---:|
  | **326** | 108,137 | **121,870** | **+13,733** | 5 |
  | **327** | 103,933 | **116,979** | **+13,046** | 4 |
  | **328** | 103,826 | **117,075** | **+13,249** | 5 |
  | **329** | 103,615 | **117,285** | **+13,670** | 5 |
  | **330** | 106,975 | **120,663** | **+13,688** | 5 |

  各 problem で約 +13.0-13.7 KB 増。PART D の 12 drill-block 構造 + drill 本文
  (各 200-300 chars × 12) の合計。試算「+5,000 bytes/problem」より大幅に大きいが、
  drill 本文を学習価値ある質に保ったため (各 drill: tag + question 50-100 chars
  + explanation 50-150 chars × 12 件)。累計 +67.4 KB、5 件で約 67 KB 増加。

- check_template_sync.py exit code: **修正前後とも 0 維持** (part_c_d は 5 本同期
  追加で sync_required 維持、意図差分 dict 操作不要)。

- WARN 件数の変化 (326-330 各々で 1→0 = WARN 完全消滅):

  | 問題 ID | §5.6 後 WARN | §5.5 後 WARN | Δ | 残存 WARN |
  |---|---:|---:|---:|---|
  | **326** | 1 (S14) | **0** | -1 | **なし** ✅ |
  | **327** | 1 (S14) | **0** | -1 | **なし** ✅ |
  | **328** | 1 (S14) | **0** | -1 | **なし** ✅ |
  | **329** | 1 (S14) | **0** | -1 | **なし** ✅ |
  | **330** | 1 (S14) | **0** | -1 | **なし** ✅ |

  S14 完全消滅。**326-330 全件で WARN 完全消滅 (ERROR 0 / WARN 0)**。

  ##### 実装途中の注目発見: S26 の自然発火と解消

  template 配置直後の段階で **S26 (○×比率不均衡: ○=0, ×=0、期待値 6:6) が新規
  発火** した。S26 は PART D の self-check-quiz で各 drill の `data-correct-value`
  が ○ または × であることを集計し、12 件で 6:6 比率を要求する検査。
  drill_blocks 未供給 (JSON が空) の段階では全 slot が空文字となり、○ 0 件 /
  × 0 件 として S26 が発火。
  60 drill 充足 + 各 problem で ○:× = 6:6 にバランス調整することで S26 も消滅、
  **真の WARN ゼロ**を達成。

- WARN 完全消滅の総括コメント:

    **326-330 全 5 件で ERROR 0 / WARN 0 を達成**。326-330 シリーズの整備期は
    本書 §5.5 をもって完走。
    
    残存案件は **slotmap §5.9 (CRIME_SIGNATURES 拡張、信書隠匿罪 / 毀棄罪 / 損壊罪
    等の正式登録) のみ**。これは validate_content の negative check の充実度向上
    案件で、現状の WARN/ERROR を発火させない ("既存 problems は allowed_cross_refs
    で吸収済み"  のため)。次フェーズの slotmap §5.9 として個別消化推奨。
    
    本セッション (§5.7 + §5.6 + §5.5) の総工数は約 2 時間 20 分 (§5.7 ≒ 10 min
    + §5.6 ≒ 45 min + §5.5 ≒ 90 min) で、WARN 4 系統 → 0 系統の完全消化を実現。
    CI safety net (check_template_sync.py) が 3 案件すべてで exit 0 を維持し、
    sync 義務違反は 1 件も発生しなかった (slotmap §5.10 §X 設計の有効性が実証)。
```

---

### §5.6 choice-section professor sub-card 追加 (R-W6: S17 解消)

#### 背景

S17 は各 `<section class="choice-section">` 内の sub-card に `professor`（教授の解説）が
欠落している場合に WARN を出す検査。326-330 全 5 件で S17×N（N=choice 数）が残存：

| 問題 ID | 形式 | S17 件数 |
|---|---|---|
| 326 | ox-grid-5 | 5 (choice-1〜5) |
| 327 | ox-grid-4 | 4 (choice-1〜4) |
| 328 | multi-select-5 | 5 |
| 329 | single-choice-5 | 5 |
| 330 | combination-5 | 5 |

→ 累計 **24 個の professor sub-card が欠落**。本案件で 5 templates と 5 problems を
拡張し、全件解消する。

##### canonical KTX301 の professor sub-card 構造

canonical/KTX301.html L2173-L2198 の professor sub-card は 4 セクション (ポイント /
考え方の道筋 / イメージで掴む / あてはめ) からなる**詳細な構造**（各 1,000-2,000 chars）。
完全踏襲は 24 sub-card × ~1,500 chars = ~36,000 chars の生成負荷で非現実的。
本書 §5.6 では canonical 構造を**簡素化**して 2 セクション (summary + note) に縮約し、
質を保ちつつ実装可能な規模にする。

##### `check_template_sync.py` 導入による safety net

5 templates すべての各 choice-section に **同じ HTML 構造 (sub-card professor with
slot placeholders)** を追加する。slot 値 (professor 本文) は JSON ごとに異なるため、
template 自体は 5 本同期維持される (`part_b` セクションは元から `sync_required=False`)。

#### 決定事項

#### 1. professor 文言供給方式 (2 案比較)

| 観点 | (a) 自由文 1 フィールド | **(b) 構造化 (summary + note) ← 採用** |
|---|---|---|
| JSON 構造 | `professor: string` | **`professor: { summary, note }`** |
| 学習者向け可読性 | 中（段落分けがプレーン）| **高（核要点と詳細解説が分離）** |
| 検証容易性 | 低（自由文の質確認が難しい）| **中（2 フィールドの両方が minLength を満たすかチェック可）** |
| canonical KTX301 構造との関係 | 簡素すぎる | **適度な構造性 (簡素化版だが核は保持)** |
| 文字数試算 / sub-card | 200-300 chars | **summary ~80 chars + note ~200 chars = 計 ~280 chars** |
| 後方互換 | optional で問題なし | **optional で問題なし** |
| 推奨 | × | ✅ **採用** |

##### 採用理由

- canonical KTX301 の 4 セクション構造を完全踏襲するのは 24 件で過大。簡素化が必要。
- 1 フィールド (a) より 2 フィールド (b) の方が学習価値の輪郭が明確 (summary で何を学ぶか、
  note で論拠の詳細)。
- 構造化により validate_content.py で「summary も note も非空」を機械チェック可能。
- 将来 canonical 同等の詳細版に拡張する際、(b) なら summary を残しつつ note を分割すれば
  良い (前方互換)。

#### 2. schema 拡張

- `$defs.Professor` を新規定義: `{ summary: string (minLength 10), note: string (minLength 10) }`
- `$defs.Choice.properties.professor` に `optional` で `$ref: "#/$defs/Professor"` を追加
- 既存 326-330.json は `professor` 未指定で引き続き valid (optional のため)、後方互換維持

#### 3. テンプレート構成

5 templates の各 choice-section の `sub-card basis-link` 直後に
`<div class="sub-card professor">` を追加:

```html
<div class="sub-card professor">
  <h4>👨‍🏫 教授の解説</h4>
  <p class="prof-summary">{{CHOICE_X_PROFESSOR_SUMMARY}}</p>
  <p class="prof-note">{{CHOICE_X_PROFESSOR_NOTE}}</p>
</div>
```

- ox-grid-5 / multi-select-5 / single-choice-5 / combination-5: 5 choice-sections × 2 slots = **10 slots**
- ox-grid-4 (KTX_template_ox4.html): 4 choice-sections × 2 slots = **8 slots**

#### 4. render.py の対応

`build_slot_dict` に各 choice から professor フィールドを抽出して slot 化:
- `CHOICE_A_PROFESSOR_SUMMARY` / `CHOICE_A_PROFESSOR_NOTE` 〜 `CHOICE_E_*`
- professor 未指定の choice (今回未対応の旧問題等) は空文字を入れて template render を破壊しない

#### 5. validate_structure.py の対応

- S17 検査は既存ロジックで、`sub-card professor` の存在を確認する。template に追加すれば
  検査ロジック変更なしで WARN が消える。
- **変更不要**。

#### 6. check_template_sync.py への影響

- 5 templates すべてに同じ sub-card 構造を追加 → `part_b` セクションは元から
  `sync_required=False` (差分許容) のため違反検出なし。
- 意図差分 dict 操作は**不要**。

#### 7. byte-identity への影響

- 326-330 全件で HTML が変化する (各 choice に professor sub-card 追加で 5-6 行増)
- Δsize: 1 problem あたり 5 choice × ~350 bytes (HTML 構造 + 本文) ≈ +1,750 bytes
- 5 件で合計 ~8.7 KB 増加見込み

#### 8. 想定リスク (R1-R5)

| ID | リスク | 想定影響 | 回避策 |
|---|---|---|---|
| **R1** | 24 件の professor 本文が無味プレースホルダ化 | 学習価値ゼロ、AP 抵触 | 各 choice の verdict と explanation を起点に、論点の核を summary に、判例・論理を note に。**「正しい」「誤っている」「正解は X」等の verdict 直書きを禁止** (AP-37) |
| **R2** | AP-37 抵触（正解番号・罪名固有句が先頭に出る） | validate_structure.py の S74-AP37 検査で ERROR | summary / note の冒頭に数字・正解値リテラルを置かない。例「本問は…」「判例は…」で開始 |
| **R3** | template 同期義務違反 (5 本中 1 本だけ修正漏れ) | check_template_sync.py が ERROR を報告 | 5 templates 全部を grep で確認、`sub-card professor` が各 choice に 1 つずつ存在することを実装後に検証 |
| **R4** | render.py で professor 未指定時のフォールバック処理ミス | 旧問題 (将来 professor 未指定 JSON) が render fail | `_build_slot_dict` で `choice.get("professor", {})` → `prof.get("summary", "")` で安全に空文字化 |
| **R5** | content 検証 regression | positive check で 24 件の新規本文が HTML 内出現するかチェック失敗 | render.py の slot 展開が確実に動作すれば positive check は通る。事前検証で確認 |

#### 9. 実装手順

1. schema/problem.schema.json: $defs.Professor 追加、choice.professor を optional 追加
2. 5 templates に professor sub-card 構造追加 (各 choice-section に基準位置で 1 個ずつ)
3. scripts/render.py: build_slot_dict に professor slot 展開を追加
4. scripts/check_template_sync.py: exit 0 維持を確認
5. problems/{326,327,328,329,330}.json: 各 choice に professor.summary + professor.note を追加 (計 24 entries)
6. 5 件を順次再 render
7. validate_structure.py: 各 problem で WARN 件数が大きく減 (S17×N が消滅)
8. validate_content.py: regression なし PASS
9. slotmap §5.6 §X に実測値記入

#### 10. §5.6 完了時点の同期実測 (記入義務、実装完了後に記入)

```
### §5.6 完了時点の同期実測 (実装完了時の実測値、2026-05-18 記入)

- 実装に要した時間:
    約 45 分 (見積 1-2 時間 → 短縮)。
    内訳: schema 5 min + 5 templates の sub-card 構造追加 15 min + render.py 5 min
    + 24 件 professor 文言生成・JSON 編集 15 min + 検証 5 min。
    24 件文言生成は事前に各 problem の verdict と explanation を踏まえた論点抽出を
    行いつつ、各 entry を summary (1-2 文) + note (3-5 文) 構造に圧縮する形で
    実装と並行して進めた。

- 修正前後の HTML サイズ変化 (326-330 各々の delta):

  | 問題 ID | 修正前 bytes (§5.7 後) | 修正後 bytes | Δ bytes | choices 数 |
  |---|---:|---:|---:|---:|
  | **326** | 105,332 | **108,137** | **+2,805** | 5 |
  | **327** | 101,773 | **103,933** | **+2,160** | 4 |
  | **328** | 101,207 | **103,826** | **+2,619** | 5 |
  | **329** | 100,995 | **103,615** | **+2,620** | 5 |
  | **330** | 104,001 | **106,975** | **+2,974** | 5 |

  1 sub-card あたり約 525-595 bytes (HTML 構造 + summary + note 本文)。試算
  「+1,400-1,750 bytes/problem」より大きいが、文言を学習価値ある質に保つため
  本文を充実させた結果 (summary ~100 chars + note ~200-250 chars × UTF-8)。
  327 のみ 4 choices で Δ も小さい (約 +2,160 = +540 bytes × 4 sub-card)。
  累計 +13,178 bytes、5 件で約 13 KB 増加。

- check_template_sync.py の修正前後 exit code:

  | 段階 | exit code | sync 違反 | part_b status |
  |---|---|---|---|
  | 修正前 (baseline) | **0** | 0 件 | 5 variants (差分許容、元から) |
  | 5 templates + render.py 編集後 | **0** | 0 件 | 5 variants (sub-card 構造は同期追加、内容は slot 駆動で差分許容範囲内) |

  意図差分 dict 操作は **不要**。part_b セクションは元から `sync_required=False`
  で choice-section 内構造を差分許容範囲で扱っており、5 templates に同じ
  professor sub-card を追加した結果も意図差分の範囲内 (各 template の
  choice-section 件数や label 系統差はそのまま、professor sub-card 追加が
  共通変更として吸収される)。

- WARN 件数の変化 (326-330 各々で S17×N が消滅):

  | 問題 ID | 修正前 WARN (§5.7 後) | 修正後 WARN | Δ | S17 状態 |
  |---|---:|---:|---:|---|
  | **326** | 6 | **1** | -5 | ✅ **消滅** (choice-1〜5 すべて) |
  | **327** | 5 | **1** | -4 | ✅ **消滅** (choice-1〜4 すべて) |
  | **328** | 6 | **1** | -5 | ✅ **消滅** |
  | **329** | 6 | **1** | -5 | ✅ **消滅** |
  | **330** | 6 | **1** | -5 | ✅ **消滅** |

  S17 が **全 5 形式で完全消滅**。残存 WARN は **S14 (drill-block) のみ**で、
  全 5 件で 1 件ずつ残るのみ。§5.5 完走で WARN ゼロ達成可能な状態に。

- 次の WARN 消化対象 (§5.5 S14 drill-block のみ残存):
    **§5.5 (S14 drill-block 実装) が WARN 消化の最終案件**。
    本修正 §5.6 が約 45 分で完走できたことを踏まえ、§5.5 はさらに大規模 (PART D
    の本格実装、12 件 × 5 形式 = 60 件の drill 問題生成、schema 拡張、template
    全面改修) のため、見積 2-3 時間。
    本セッション全体（§5.7 + §5.6 + §5.5）の総工数は §5.7=10 分 + §5.6=45 分 +
    §5.5=2-3 時間 = 約 3-4 時間と予想。
```

---

### §5.7 footer-spec ktx301-canon feature-tag 追加 (R-W7: S51 解消)

#### 背景

S51 は `<div class="footer-spec">` 内の必須 feature-tag リスト
(`validate_structure.py` L292-301 の `required_tags`) のうち、欠落しているものを
WARN で報告する検査。326-330 全 5 件で **`'ktx301-canon'`** が必須 tag として
要求されているが、5 本立て template すべてで欠落している状態。

##### 326-330 シリーズでの観測事実

| 問題 ID | 形式 | S51 状態 | 欠落 tag |
|---|---|---|---|
| 326 | ox-grid-5 | ⚠ WARN | `['ktx301-canon']` |
| 327 | ox-grid-4 | ⚠ WARN | `['ktx301-canon']` |
| 328 | multi-select-5 | ⚠ WARN | `['ktx301-canon']` |
| 329 | single-choice-5 | ⚠ WARN | `['ktx301-canon']` |
| 330 | combination-5 | ⚠ WARN | `['ktx301-canon']` |

→ **5 本立て template すべての footer-spec に `ktx301-canon` が欠落**している。
他の必須 tag (TX v8.11.6 / spoiler-safe / a2-two-stage-reveal / 等 計 13 種) は
存在するが、`ktx301-canon` のみが未配置で全 5 形式で WARN が出ている状態。

##### canonical KTX301.html の状態と template との差異

- **canonical/KTX301.html L3336**: `<span class="feature-tag">ktx301-canon</span>・`
  が存在 (canonical では `multi-answer-css` の直後、`embedded-canon` の直前に配置)。
- **5 templates の現状**: `ktx301-canon` の代わりに `<span class="feature-tag">ktx-template-canon</span>・`
  が同位置に存在 (派生時のラベル変更が原因と推定)。
- `ktx-template-canon` は `required_tags` リストに **含まれない** ため S51 検査では
  許容も無視もされない (validator は気にしない別 tag)。

##### canonical KTX301 から派生した template の「出自タグ」の意味

`ktx301-canon` は canonical KTX301 から派生した実装であることを示す **出自タグ**。
canonical の本文・解説を流用しない (PATCH §1) という制約下でも、構造的派生関係は
出自タグとして文書化することが v8.11.0 で規定された。5 本立て template が canonical
KTX301 構造を踏襲している以上、本タグの追加は **論理的必然**。

##### `check_template_sync.py` 導入による safety net

slotmap §5.10 で確立した `scripts/check_template_sync.py` により、本修正は
**5 本同期で同じ追加**を行うため、sync_required セクション `footer_spec` の
hash が 5 本すべてで一致する状態を維持できる。
**意図差分 dict の操作は不要**、CI の exit code 0 を修正前後で維持。

#### 決定事項

#### 1. 修正対象ファイル

5 本立て template **すべて**:

- `templates/KTX_template.html` (ox-grid-5、現状 L2364 に `ktx-template-canon`)
- `templates/KTX_template_ox4.html` (ox-grid-4、現状 L2327 に `ktx-template-canon`)
- `templates/KTX_template_msel5.html` (multi-select-5、現状 L2330 に `ktx-template-canon`)
- `templates/KTX_template_sc5.html` (single-choice-5、現状 L2346 に `ktx-template-canon`)
- `templates/KTX_template_comb5.html` (combination-5、現状 L2354 に `ktx-template-canon`)

#### 2. 修正内容: feature-tag `ktx301-canon` の 1 行追加

##### 追加位置と前後コンテキスト (canonical KTX301 順序準拠)

canonical/KTX301.html L3335-L3337 の順序を参照:

```html
      <span class="feature-tag">multi-answer-css</span>・
      <span class="feature-tag">ktx301-canon</span>・
      <span class="feature-tag">embedded-canon</span>・
```

5 templates にはこの位置に **`ktx-template-canon`** が存在するが、`ktx301-canon` は
存在しない。各 template の **既存 `ktx-template-canon` 行の直前**に 1 行追加する。

##### 追加する正規文字列 (canonical L3336 から逐語コピー)

```
      <span class="feature-tag">ktx301-canon</span>・
```

(行頭インデント 6 スペース、末尾の中黒 `・` を含む、行末改行を含む)

##### 修正後の 5 templates 共通構造

```html
      <span class="feature-tag">multi-answer-css</span>・
      <span class="feature-tag">ktx301-canon</span>・        ← 新規追加 (canonical 順序準拠)
      <span class="feature-tag">ktx-template-canon</span>・  ← 既存 (残置)
      <span class="feature-tag">embedded-canon</span>・
```

##### 既存 `ktx-template-canon` の扱い

- 5 templates に存在する `ktx-template-canon` は `required_tags` リストに含まれない
  ため、S51 検査には影響しない。
- 削除すると別の意図差分が発生するため、本修正では **残置** を選択。
- canonical/KTX301.html には `ktx-template-canon` が存在しないため、将来的には
  「canonical 完全準拠」のため削除する案件として **slotmap §5.X (将来案件)** に
  保留。本書 §5.7 ではスコープ外。

#### 3. 触らないファイル

- `canonical/KTX301.html` (既に `ktx301-canon` を持つ source of truth)

#### 4. check_template_sync.py への影響

- 5 templates すべてに **同じ 1 行を追加**するため、sync_required セクション
  `footer_spec` は **5 本同期状態を維持**する (hash は変化するが、5 本すべてで
  同じ新 hash になる)。
- 意図差分 dict の操作は **不要**。`footer_spec` は引き続き `sync_required=True`。
- check_template_sync.py の exit code は **修正前後で 0 維持**。
- `head` / `css` / `body_pre_toc` / `marker_legend` / `part_c_d` / `js` への影響なし
  (これらのセクションは feature-tag に触れない)。

#### 5. byte-identity への影響

- 326-330 **全 5 件で HTML が変化する** (footer-spec に 1 行追加)。
- HTML サイズは微増 (1 行 = `<span class="feature-tag">ktx301-canon</span>・` +
  改行 +インデント分、合計約 **+55 bytes** と試算)。
- 修正前の byte-identity (§5.8 後の新 hash) は崩れ、修正後の HTML を新たな
  base hash として記録する。
- 修正後の base hash は §5.7 §X 完了時点の同期実測で記録。

#### 6. validate_structure.py への影響

- S51 の発火条件 (`required_tags` に含まれる tag が footer に欠落) が消滅する。
- 326-330 全件で WARN 件数が **1 ずつ減る**:
  - 326: 7 → **6** (§5.8 後の WARN 状態から)
  - 327: 6 → **5**
  - 328: 7 → **6**
  - 329: 7 → **6**
  - 330: 7 → **6**
- **validate_structure.py のコード変更は不要**: `required_tags` リストは既に
  `'ktx301-canon'` を要求しており、追加された tag が検出されて WARN が出なくなる。

#### 7. 想定リスク (R1-R5)

| ID | リスク | 想定影響 | 回避策 |
|---|---|---|---|
| **R1** | feature-tag の追加位置を間違える | canonical 順序と異なる位置に挿入され、可読性低下 / 意図差分テーブル更新が必要 | `canonical/KTX301.html` L3336 の前後 (`multi-answer-css` 直後、`embedded-canon` 直前、5 templates では `ktx-template-canon` 直前) に揃える |
| **R2** | 5 本のうち 1 本でも追加漏れ | check_template_sync.py が同期義務違反として ERROR 報告 | `check_template_sync.py` 実行で exit code 0 を確認、`footer_spec` の hash が 5 本一致することを保証 |
| **R3** | feature-tag の文字列を誤記 | 全角/半角ハイフン / class 名タイポ等で `required_tags` リストと不一致 | `canonical/KTX301.html` L3336 から **逐語コピー**。修正後に各 template の同位置を Grep で文字列一致確認 |
| **R4** | 修正後の HTML 表示への影響 | footer に新 tag が表示されてレイアウト崩れ | `.footer-spec .feature-tag` CSS は既存で全 tag を inline 表示するルールあり (L1930-)。1 個追加でも `display:inline-block` + flex-wrap で改行され、表示崩れなし |
| **R5** | AP-37 抵触 | feature-tag に正解情報が含まれていれば AP-37 (正解値リテラル先頭) に抵触 | `ktx301-canon` は出自を示すラベルで、正解番号や罪名固有句を含まない。**AP-37 非該当**。本書 §5.7 §6 で明示 |

#### 8. 実装手順 (本実装プロンプトで再掲する)

| Step | 作業 | 検証ポイント |
|---|---|---|
| 1 | `canonical/KTX301.html` L3336 から正規文字列を逐語コピー | `<span class="feature-tag">ktx301-canon</span>・` (前 6 スペース、末尾中黒) |
| 2 | `templates/KTX_template.html` の `ktx-template-canon` 直前に 1 行追加 | 5 templates 共通の追加位置 |
| 3 | `templates/KTX_template_ox4.html` の同位置に 1 行追加 | 同上 |
| 4 | `templates/KTX_template_msel5.html` の同位置に 1 行追加 | 同上 |
| 5 | `templates/KTX_template_sc5.html` の同位置に 1 行追加 | 同上 |
| 6 | `templates/KTX_template_comb5.html` の同位置に 1 行追加 | 同上 |
| 7 | `python scripts/check_template_sync.py` 実行 | exit 0 (sync OK)、footer_spec は引き続き全 5 本一致 |
| 8 | `python scripts/render.py {326,327,328,329,330}` 順次実行 | 各 exit 0、HTML 生成成功 |
| 9 | `python scripts/validate_structure.py outputs/tx/刑TX/刑TX{326-330}.html` 順次実行 | 各 exit 0、**WARN 件数が 1 ずつ減少**、S51 が消滅 |
| 10 | `python scripts/validate_content.py` で 326-330 全件 regression なし確認 | 各 exit 0、PASS 維持 |
| 11 | slotmap §5.7 §X の空欄 5 項目を実測値で埋める | 実装完了後に記入 |

#### 9. §5.7 完了時点の同期実測 (記入義務、実装完了後に記入)

slotmap §5.3 §8 / §5.4 §8 / §5.8 §X / §5.10 §X で確立した記録フォーマットを継承し、
本修正の実装完了時に以下を本書に追記する義務がある。**現時点では空欄**として用意:

```
### §5.7 完了時点の同期実測 (実装完了時の実測値、2026-05-18 記入)

- 実装に要した時間:
    約 10 分 (本書 §「実装規模見積もり」15-20 分と試算 → さらに短縮)。
    短縮要因: (1) slotmap §5.7 §2 で canonical L3336 から逐語コピーする正規文字列が
    事前合意済、(2) 5 本の template すべてで同一の追加箇所 (`multi-answer-css` 直後 /
    `ktx-template-canon` 直前) を Edit ツールで定型的に処理、(3) check_template_sync.py
    の CI safety net で 5 本同期追加が即時 PASS と判定 (dict 操作不要)、(4) §5.8 同型の
    手順で迷いなく進行。
    本修正は 326-330 シリーズで **最も小さい WARN 消化案件**。

- 修正前後の HTML サイズ変化 (326-330 各々の delta):

  | 問題 ID | 修正前 bytes | 修正後 bytes | Δ bytes | 修正前 SHA256 | 修正後 SHA256 |
  |---|---:|---:|---:|---|---|
  | **326** | 105,276 | **105,332** | **+56** | `D0FDD80A0DC85EEA...` | `C5F3310BC4DADBDA...` |
  | **327** | 101,717 | **101,773** | **+56** | `5B93758F4AE8E5CD...` | `24B63040EACDF37F...` |
  | **328** | 101,151 | **101,207** | **+56** | `1839599B3D7B23F8...` | `1C67E1EA1E0FCDEC...` |
  | **329** | 100,939 | **100,995** | **+56** | `7009D4521FD75C22...` | `CD63B02D6A648EED...` |
  | **330** | 103,945 | **104,001** | **+56** | `3E200396DCD86BA3...` | `6299C73B50378549...` |

  **5 件すべて Δ = +56 bytes で完全一致**。本書 §5「byte-identity への影響」で
  試算した「約 +55 bytes」と整合 (実測 56 bytes、追加文字列
  `      <span class="feature-tag">ktx301-canon</span>・` のインデント 6 スペース +
  `<span class="feature-tag">` (25 char) + `ktx301-canon` (12 char) +
  `</span>` (7 char) + `・` (3 byte UTF-8) + 改行 (2 byte CRLF / 1 byte LF) で
  約 55-56 bytes)。

- check_template_sync.py の修正前後 exit code:

  | 段階 | exit code | sync 違反 | footer_spec status |
  |---|---|---|---|
  | 修正前 (baseline) | **0** | 0 件 | 5 本同期 (旧 hash) |
  | 5 template 編集後 | **0** | 0 件 | **5 本同期 (新 hash)** |

  **意図差分 dict 操作は実施せず**。5 templates すべてに同一の 1 行追加を行ったため、
  sync_required セクション `footer_spec` の hash は 5 本すべて新たな同じ値に変化し、
  sync_required 状態を維持 (旧 hash と新 hash の対比は 5 本同期の遷移を示す)。
  CI safety net が「5 本同期追加」を機械的に保証することを実証。

- WARN 件数の変化 (326-330 各々で 1 減を確認):

  | 問題 ID | 修正前 WARN | 修正後 WARN | Δ | S51 状態 |
  |---|---:|---:|---:|---|
  | **326** | 7 (§5.8 後) | **6** | **-1** | ✅ **消滅** |
  | **327** | 6 (§5.8 後) | **5** | **-1** | ✅ **消滅** |
  | **328** | 7 | **6** | **-1** | ✅ **消滅** |
  | **329** | 7 | **6** | **-1** | ✅ **消滅** |
  | **330** | 7 | **6** | **-1** | ✅ **消滅** |

  S51 が **全 5 形式 (326-330) すべてで完全消滅**。残存 WARN 系統は S14
  (drill-block) / S17×N (professor) の **2 系統のみ**に縮小 (§5.8 で S71-AP33 消滅、
  §5.7 で S51 消滅、初期の 4 系統 → 2 系統)。

- 次の WARN 消化対象 (§5.5/§5.6 のうち、agent §5.8 §X 評価では §5.6 が次推奨):

  **§5.6 (S17 professor sub-card) を最推奨**。

  | 観点 | §5.5 (S14 drill-block) | **§5.6 (S17 professor)** |
  |---|---|---|
  | 規模 | 大 (drill-block 12 件 + schema 拡張 + render 拡張) | 中 (5 件 × 5 templates = 25 sub-card 追加、JSON 拡張) |
  | 複雑度 | 高 (新概念 + 大量データ抽出) | **中** (JSON 構造拡張あり、本文は学説型 / 判例型で問題ごとに異なる) |
  | CI safety net 効果 | 高 (template 大変更を CI で検証) | **高** (template 5 本に sub-card 構造同期追加、sync_required 維持可能) |
  | 全 5 形式での WARN 消滅 | ✅ | ✅ |
  | 実装規模見積 | 数時間〜半日 (drill-block 内容の準備が大半) | **1-2 時間** |
  | 推奨度 | ★ (大規模、整備期に着手) | **★★★** |

  ##### §5.6 着手時の引き継ぎ事項

  - **JSON 構造拡張が必要**: `problems/{id}.json` の各 choice 配下に
    `professor` フィールドを追加する案件。schema/problem.schema.json の
    `$defs.Choice` に新フィールド定義が要る。
  - **5 本の template すべてに sub-card 構造追加**: 5 形式 × 5 件 = 25 sub-card。
    template 同期義務に注意 (sync_required 維持)。
  - **既存 5 problems への影響**: 326-330 すべて再 render 必要、HTML サイズ変化大
    (professor 本文が各 choice に 1 つずつ追加されるため)。
  - **調査フェーズ必須**: 「professor sub-card」の内容仕様 (誰が書いた解説か、長さ、
    形式) を slotmap §5.6 設計調査で確定する必要あり。
  - **本セッションで slotmap §5.6 本文化まで進めるかは別判断** (規模が中で
    調査フェーズが必要なため、§5.7 と同セッションで連続消化は推奨しない)。

  ##### §5.5 (drill-block) は §5.6 完走後の最後

  - PART D の本格実装で、全 5 形式に共通の drill-block × 12 件構造を追加する大規模案件。
  - 規模・複雑度・調査負荷ともに最大、整備期の最後に着手するのが妥当。
```

これにより本修正の実測値が次フェーズ (§5.6 S17 professor 消化) の見積もり
基礎データとなる。

#### 関連項目

##### canonical/KTX301 由来の出自タグの位置づけ

- `ktx301-canon` は canonical KTX301 構造を踏襲した実装であることを示す出自タグ。
  v8.11.0 で `required_tags` リストに追加された。
- 5 本立て template が KTX301 から派生していることを明示する役割。
- 派生時の構造変更 (ox-grid / multi / single / combination 等の形式分岐) に
  かかわらず、構造的派生関係は維持されているため本タグの保有は妥当。

##### `ktx-template-canon` の扱い (§5.7 ではスコープ外)

- 5 templates に存在する `ktx-template-canon` は canonical KTX301 には存在しない
  独自タグ。
- `required_tags` リストにも含まれず、S51 検査には無関係。
- 将来的に「canonical 完全準拠」を達成するなら削除候補だが、本書 §5.7 では
  **残置**を選択 (削除は別案件として slotmap §5.X 将来案件として保留)。
- 残置することで本修正の規模を「1 行追加のみ」に最小化し、CI safety net の
  効果を最大化できる。

##### AP-37 抵触回避 (継承)

`ktx301-canon` は出自を示すラベルで、正解番号や罪名固有句を含まない。
**AP-37 (正解値リテラル先頭禁止) 非該当**。validate_structure.py の S74-AP37 検査は
PART A 内 / data-explanation 先頭のパターンのみ対象で、footer-spec は対象外。

---

### §5.8 ox-grid 系 answer-instruction 文言の canonical 化 (R-W8: S71-AP33 解消)

#### 背景

S71-AP33 は `<p class="answer-instruction">` の文言が v8.11.3 で定義された
canonical 文言 (`validate_structure.py` L612-616 の `canonical_patterns`) と
相違する場合に WARN を出す検査。

##### 326-330 シリーズでの観測事実

326-330 セッションシリーズを通して、各形式での S71-AP33 発火状態は以下のように
推移した:

| 問題 ID | 形式 | S71-AP33 状態 | 理由 |
|---|---|---|---|
| 326 | ox-grid-5 | ⚠ WARN | 旧文言 (現状の KTX_template.html) のまま |
| 327 | ox-grid-4 | ⚠ WARN | 旧文言 (現状の KTX_template_ox4.html) のまま |
| 328 | multi-select-5 | ✅ 消滅 | multi 用 canonical 文言を template 採用 |
| 329 | single-choice-5 | ✅ 消滅 | single 用 canonical 文言を template 採用 |
| 330 | combination-5 | ✅ 消滅 | single 用 canonical 文言を template 採用 |

→ **ox-grid 系 (326/327) のみで残存する不整合状態**。多重 / 単一選択系では
v8.11.3 canonical 文言の採用により自然消滅したのに、ox-grid 系は旧文言のまま
温存されている。

##### `check_template_sync.py` 導入による safety net

slotmap §5.10 で確立した `scripts/check_template_sync.py` により、本修正の
副作用検出 (同期義務違反 / 想定外差分) が **CI 化で即時検証可能**となった。
本修正は 2 本 (`KTX_template.html` / `KTX_template_ox4.html`) のみの極小規模
変更で、5 本立て同期義務への影響は意図差分 dict 内に閉じる見込み。

#### 決定事項

#### 1. 修正対象ファイル

- `templates/KTX_template.html` (ox-grid-5、L2079 の `<p class="answer-instruction">`)
- `templates/KTX_template_ox4.html` (ox-grid-4、L2077 の同位置)

#### 2. 修正前文言と修正後文言

##### 修正前文言 (現状、326/327 で S71-AP33 WARN を発火している文言)

```
各記述について「正しい (1)」か「誤っている (2)」を選んでください。
```

##### 修正後文言 (v8.11.3 ox-grid 用 canonical 文言)

```
各記述に「1（正）」または「2（誤）」を選んで「解答を表示」を押してください。
```

##### 修正後文言の根拠

- `scripts/validate_structure.py` L615 の `canonical_patterns[2]`:
  ```python
  re.compile(r'^各記述に「1（正）」または「2（誤）」を選んで「解答を表示」を押してください。$'),  # ox-grid
  ```
- v8.11.3 で 3 Type 対応 (single / multi / ox-grid) を導入した際、ox-grid 用に
  正式登録された文言。
- canonical/KTX301.html は **single 形式** (組合せ型 5 択) の問題のため、
  KTX301 内には ox-grid 用 canonical 文言は存在しない。よって本修正の根拠は
  **KTX301 ではなく validate_structure.py の canonical_patterns 定義**。

#### 3. 触らないファイル

- `canonical/KTX301.html` (single 用 canonical 文言を保持、本修正の根拠外)
- `templates/KTX_template_msel5.html` (既に multi 用 canonical 文言を採用済、§5.2)
- `templates/KTX_template_sc5.html` (既に single 用 canonical 文言を採用済、§5.3)
- `templates/KTX_template_comb5.html` (既に single 用 canonical 文言を採用済、§5.4)

#### 4. 意図差分への影響 (`check_template_sync.py` dict)

本修正前の `INTENTIONAL_DIFFS` dict の状態:

- `a2` セクションは `sync_required=False` (差分許容、§5.10 §3)。
- ox-grid 系 (KTX_template.html / _ox4.html) と multi/single/combination 系
  (_msel5 / _sc5 / _comb5) で a2 の `answer-instruction` 文言が異なる状態。
- check_template_sync.py の結果は `a2: 5 variants` を意図差分として情報報告。

本修正後の状態:

- ox-grid 系 2 本も canonical 文言に揃うが、A-2 解答エリア全体の構造 (ox-grid 構造
  vs single/multi 構造) は依然として異なるため、**`a2: 4 variants` に減少**する見込み
  (msel5 が「選択肢を 2 個選んで…」、sc5 と comb5 が「選択肢を選んで…」、ox4 と
  KTX_template.html が ox-grid canonical 文言で同一になり、これに ox-row の構造差で
  細部相違)。
- **dict 自体の変更は不要**: `a2` は引き続き `sync_required=False`。文言修正は
  意図差分の許容範囲内。
- 副作用: check_template_sync.py の `--format=text` 出力で a2 の variants 数が
  5 → 4 に減ることが確認できる (§5.8 §X の実測義務で記録)。

#### 5. byte-identity への影響

- **326.html / 327.html は再 render により HTML が変化する**。これは意図された変更。
- 本セッション (§5.4 §8) で確立した byte-identity (SHA256 `E4790D25...` / `1AC6D19B...`)
  は **本修正により崩れる**。
- 修正後の HTML を **新たな base hash として再記録**する。slotmap §5.4 §8 §A の
  「byte-identity 維持時間」累計値は本修正後にリセット (326/327 のみ)、
  328/329/330 の byte-identity は引き続き維持される。

#### 6. validate_structure.py への影響

- S71-AP33 の発火条件 (canonical 文言と相違) が ox-grid 系で消滅する。
- 326/327 で WARN 件数が **8 → 7** に減る (S71-AP33 が消える)。
- **validate_structure.py のコード変更は不要**: 検出ロジックは既に正しく、文言が
  正規パターンに一致すれば自動的に WARN が出なくなる。
- 修正後の WARN 内訳 (326/327 共通) は S14 / S17×N / S51 の 3 系統のみ。
  これにより 5 形式すべてで S71-AP33 が消滅し、**全 5 件で WARN 4 系統 → 3 系統に縮小**。

#### 7. 想定リスク (R1-R5)

| ID | リスク | 想定影響 | 回避策 |
|---|---|---|---|
| **R1** | 文言修正で予期せぬ表示崩れ | A-2 解答エリアの UI 表示が壊れる、ボタン配置が変わる | 修正後の `outputs/tx/刑TX/刑TX326.html` / `刑TX327.html` を **目視確認**。文字数は微増 (約 +14 char) だが CSS の text-wrap で吸収される見込み |
| **R2** | 326/327 の content 検証への影響 | validate_content.py の positive check / negative check が破綻 | 文言には正解番号や罪名固有句が含まれないため **AP-37 / negative check 抵触なし**。positive check は metadata と choice 内容を見るため、answer-instruction 文言は対象外。**影響なし見込み** |
| **R3** | `check_template_sync.py` で意図差分の登録漏れによる false positive | 修正後に新規 sync 違反が報告される | 修正前に `INTENTIONAL_DIFFS` dict を確認 → `a2` は既に `sync_required=False` 登録済。修正と同時の dict 更新は不要。修正後の初回実行で exit 0 が継続することを確認 (§5.10 §4 R1 の鉄則に従う) |
| **R4** | canonical 文言の取り違え | 文言の細部 (全角括弧 vs 半角、改行有無、句点) を間違える | `scripts/validate_structure.py` L615 の regex `^各記述に「1（正）」または「2（誤）」を選んで「解答を表示」を押してください。$` から **逐語コピー**。コピー手順を実装プロンプトで明示 |
| **R5** | 修正後の HTML サイズ変化 | 326/327 の HTML が膨張、storage / 配信影響 | 文字数差は約 +14 char、HTML 全体 (約 100 KB) に対し 0.014% の極小変化。**事前合意済 (影響軽微)** |

#### 8. 実装手順 (本実装プロンプトで再掲する)

| Step | 作業 | 検証ポイント |
|---|---|---|
| 1 | `scripts/validate_structure.py` L615 から ox-grid 用 canonical 文言を逐語コピー | 正規表現の `^` `$` を除いた本文を取り出す |
| 2 | `templates/KTX_template.html` L2079 の `answer-instruction` 文言を修正後文言に置換 | 1 行のみの編集 |
| 3 | `templates/KTX_template_ox4.html` L2077 の同位置を置換 | 1 行のみの編集 |
| 4 | `python scripts/check_template_sync.py` 実行 | exit 0 (sync OK)、a2 セクションの variants 数が 5→4 に減ったことを確認 |
| 5 | `python scripts/render.py 326` 実行 | exit 0、HTML 生成成功 |
| 6 | `python scripts/render.py 327` 実行 | 同上 |
| 7 | `python scripts/validate_structure.py outputs/tx/刑TX/刑TX326.html` 実行 | exit 0、WARN 件数が **8 → 7** に減少、S71-AP33 が消滅 |
| 8 | 327 で同様の検証 | WARN 件数が **7 → 6** に減少、S71-AP33 が消滅 |
| 9 | `python scripts/validate_content.py` で 326/327 とも regression なし確認 | exit 0、PASS |
| 10 | 328/329/330 の再 render + validate で regression なし確認 | byte-identity 維持 (本修正対象外の 3 本) |
| 11 | slotmap §5.8 §X の空欄 5 項目を実測値で埋める | 実装完了後に記入 |

#### 9. §5.8 完了時点の同期実測 (記入義務、実装完了後に記入)

slotmap §5.3 §8 / §5.4 §8 / §5.10 §8 で確立した記録フォーマットを継承し、
本修正の実装完了時に以下を本書に追記する義務がある。**現時点では空欄**として用意:

```
### §5.8 完了時点の同期実測 (実装完了時の実測値、2026-05-18 記入)

- 実装に要した時間:
    約 15 分 (本書 §「実装規模見積もり」30 分以下と試算 → 半分以下で完走)。
    短縮要因: (1) slotmap §5.8 §2 で修正前文言・修正後文言・根拠 (validate_structure.py
    L615) が事前合意済、(2) 2 本の template 編集 (1 行ずつ) のみで完結、
    (3) check_template_sync.py の CI safety net による副作用検知が即時動作、
    (4) 文言は AP-37 / content positive check に抵触しないことが事前に確認済。
    実装ミスとして全角括弧を半角で入力した初動エラーがあったが、Grep で即検出して
    再修正で吸収 (5 分以下のロス)。

- 修正前後の HTML サイズ変化:

  | 問題 ID | 修正前 bytes | 修正後 bytes | Δ bytes | 修正前 SHA256 | 修正後 SHA256 |
  |---|---:|---:|---:|---|---|
  | **326** | 105,258 | **105,276** | **+18** | `E4790D25A4486F7D...` | `D0FDD80A0DC85EEA...` |
  | **327** | 101,699 | **101,717** | **+18** | `1AC6D19B23BA488B...` | `5B93758F4AE8E5CD...` |

  Δ +18 bytes (各々) = 修正後文言の追加文字 (「を選んで「解答を表示」を押して」+
  「に」+ 「または」 - 旧文言の「について」-「か」-「を選んでください」-「正しい
  (1)」-「誤っている (2)」+ 「1（正）」+ 「2（誤）」、UTF-8 マルチバイトを含めた
  累計差) と整合。326 と 327 で同じ Δ なのは、A-2 部分が両 template で同一構造
  (文言修正部分のみ違い) のため。

- check_template_sync.py の実行結果:

  | 段階 | exit code | sync 違反 | a2 variants |
  |---|---|---|---|
  | 修正前 (baseline) | **0** | 0 件 | 5 |
  | 2 template 編集後 | **0** | 0 件 | 5 (変わらず) |

  **意図差分 dict 操作は実施せず** (a2 セクションは元から `sync_required=False` で
  全体構造の差を許容しており、文言一致だけでは ox-row 構造 (× 5 vs × 4) の差で
  variants 数は 5 のまま不変)。slotmap §5.8 §4「a2: 5→4 variants に減少する見込み」
  という事前予測は **不正確**だったが、これは ox-row 構造差を見落とした予測ミスで、
  実装には影響なし (dict 操作不要を即判断で対応)。
  CI safety net は exit 0 を維持し、本修正が 5 本立て同期義務を破壊していない
  ことを機械的に保証。実行時間 118 ms。

- WARN 件数の変化 (validate_structure.py 出力):

  | 問題 ID | 修正前 WARN | 修正後 WARN | Δ | S71-AP33 状態 |
  |---|---:|---:|---:|---|
  | **326** | 8 | **7** | **-1** | ✅ **消滅** |
  | **327** | 7 | **6** | **-1** | ✅ **消滅** |

  S71-AP33 が ox-grid-5 / ox-grid-4 で消滅したことで、全 5 問題 (326-330) で
  S71-AP33 WARN が **完全消滅**。残存 WARN 系統は S14 (drill-block) / S17×N
  (professor) / S51 (ktx301-canon) の **3 系統のみ**に縮小。

- 次の WARN 消化対象 (§5.5/§5.6/§5.7 評価):

  | 案件 | 規模 | 複雑度 | CI safety net 効果 | 推奨度 |
  |---|---|---|---|---|
  | **§5.7 S51 ktx301-canon feature-tag** | **極小 (template 5 本の footer-spec に 1 行追加)** | **低** (1 文字列追加) | **高** (sync 義務を破壊しないことが即検証可能) | **★★★ (最推奨)** |
  | §5.6 S17 professor sub-card | 中 (各 choice-section に 1 sub-card 追加 × 5 件 × 5 本 = 約 25 箇所、+ schema 拡張) | 中 (JSON 構造拡張要) | 中 (template 変更を 5 本同期、CI で検証) | ★★ |
  | §5.5 S14 drill-block 実装 | 大 (PART D に drill-block 12 件構造、schema 拡張、render 拡張、検証) | 高 (新概念 + 大量データ抽出) | 高 (template 大変更を CI で検証) | ★ (大規模、整備期に着手) |

  **推奨: §5.7 (S51 ktx301-canon feature-tag) を次の最優先案件**とする。理由:
  - 5 本立て template の footer-spec に「ktx301-canon」feature-tag を追加するだけ
    の極小修正 (1 行 × 5 本 = 約 5 行差分)。
  - 本修正 (§5.8) と同じく CI safety net (check_template_sync.py) で 5 本同期を
    即検証可能 — sync_required セクション `footer_spec` への変更だが、5 本同一の
    追加なので exit 0 を維持できる。
  - 326-330 全 5 件で S51 が消滅し、残存 WARN が S14 + S17 の 2 系統まで縮小する。
  - 実装規模 約 15-20 分の見込み (本修正と同等)。
  - 5 本一斉修正なので、4 本 + 1 本パターンの本修正よりさらに同期義務に整合的。

  次の §5.7 完走後の優先順位:
  1. §5.6 S17 professor sub-card (schema/template/render 共同拡張、中規模)
  2. §5.5 S14 drill-block (PART D の本格実装、大規模、最後に着手推奨)
```

これにより本修正の実測値が次フェーズ (WARN 消化シリーズ §5.5-§5.7) の見積もり
基礎データとなる。

#### 関連項目 (継承)

- **AP-37 抵触回避ガイド**: 本修正の文言には正解番号 (`1`, `2`) が含まれるが、
  これは **「ox-grid の入力 UI 説明」としての文脈**で、正解値ではない。AP-37 が
  検出する「正解値リテラル」とは異なる範疇のため抵触しない (validate_structure.py
  の S74-AP37 検査ロジックは PART A 内 / data-explanation 先頭のパターンのみ対象)。
- **crime 表記揺れ**: 本修正と独立 (§5.9 で扱う案件)。

---

### §5.9 CRIME_SIGNATURES 拡張 (R-W9: 信書隠匿罪追加、allowed_cross_refs 負債解消の第一歩)

#### 背景

`scripts/validate_content.py` の `CRIME_SIGNATURES` dict は、各罪に固有なシグネチャ
語を保持し、`negative_check` で他罪のシグネチャが混入していないか機械的に検出する
仕組み。326-330 シリーズで以下の問題が判明した:

##### 326-330 完走時の crime 表記揺れ対応 (allowed_cross_refs 一時運用)

| 問題 ID | crime | allowed_cross_refs | 注 |
|---|---|---|---|
| 326 | 盗品等罪 | なし | 既存登録 |
| 327 | 盗品等罪 | なし | 既存登録 |
| 328 | 盗品等罪 | なし | 既存登録 |
| 329 | 器物損壊罪 | **["信書隠匿罪"]** | 信書隠匿罪は CRIME_SIGNATURES 未登録のため effects が無効 |
| 330 | 器物損壊罪 | **["窃盗罪", "信書隠匿罪"]** | 同上、"信書隠匿罪" 部分が無効 |

→ 329/330 で `allowed_cross_refs` に「信書隠匿罪」を明示しているが、CRIME_SIGNATURES
未登録のため **documentation 効果のみで実効性なし**。本来の意図 (negative_check で
信書隠匿罪 signature を skip) が機能していない。

##### 既存登録 10 罪と未登録罪の整理

| 既存登録 (CRIME_SIGNATURES の key) | 326-330 で出現する未登録罪 |
|---|---|
| 詐欺罪 / 盗品等罪 / 窃盗罪 / 強盗罪 / 横領罪 / 背任罪 / 文書等毀棄罪 / 器物損壊罪 / 住居侵入罪 / 恐喝罪 | **信書隠匿罪** (263条、329/330 で頻出) |

「毀棄罪」「損壊罪」単独は **既存登録の「文書等毀棄罪」「器物損壊罪」でカバー済**
(条文 258条 / 259条 / 261条 等で網羅)。別途追加は重複検出のリスクがあるため
本書 §5.9 では追加しない (slotmap §5.11+ 候補)。

##### 形式 #6 入口での AND 条件再判定義務は本フェーズでは不発火

slotmap §5.4 §7 の (b) refactor 発火条件 (①330 が既存 4 本で収まらない / ②形式 #6
以降 2 件以上 confirmed) は **両方とも引き続き不充足**。本 §5.9 は WARN 系統では
なく、validate_content の辞書整備案件のため、AND 条件の判定対象外。

##### `check_template_sync.py` への影響なし

template も既存 problems の HTML も**不変**のため、CI safety net (slotmap §5.10) の
exit 0 維持に影響なし。本案件は scripts/validate_content.py 単独編集 (dict データ
追加のみ)。

#### 決定事項

#### 1. 追加対象の罪名

**信書隠匿罪 1 件のみ**。

##### 信書隠匿罪 signature 候補

| signature | 根拠 | 出現箇所 (326-330) |
|---|---|---|
| `"263条"` | 信書隠匿罪の条文番号 | 329 の解説中 (`信書隠匿罪（263条）`) で頻出 |
| `"信書隠匿"` | 罪名そのものの一部 (罪名 / 罪名から末尾「罪」を除いたもの) | 329/330 の解説・選択肢で複数回 |

##### 毀棄罪 / 損壊罪 を本書で追加しない理由

- 「毀棄罪」単独は CRIME_SIGNATURES 既存の「文書等毀棄罪」(258条 / 259条 / 公用文書
  毀棄 / 私用文書毀棄 / 電磁的記録毀棄) で実質網羅。
- 「損壊罪」単独も「器物損壊罪」(261条 / 効用侵害) で網羅。
- 別途「毀棄罪」「損壊罪」を key として追加すると、既存 key とのシグネチャ重複が
  生じる可能性 (例: 同一の "258条" が「文書等毀棄罪」と「毀棄罪」の両方で trigger)。
- 重複は negative_check の信頼性を損なうため、本書では追加しない。
- 将来「毀棄罪及び損壊罪」を統合罪名として正式採用する必要が生じた場合、slotmap
  §5.11+ で別途検討する。

#### 2. CRIME_SIGNATURES dict への追加位置と value フォーマット

既存 dict 末尾の「恐喝罪」の直後、コメント `# 必要に応じて追記` の直前に追加:

```python
    "恐喝罪": [
        "249条",
        "1項恐喝",
        "2項恐喝",
    ],
    "信書隠匿罪": [
        "263条",
        "信書隠匿",
    ],
    # 必要に応じて追記
```

- key: `"信書隠匿罪"` (329/330.json の `allowed_cross_refs` に記載済の文字列と一致)
- value: 2 件の signature 文字列のリスト

#### 3. allowed_cross_refs の扱い

- 本書 §5.9 では **329.json / 330.json の `allowed_cross_refs` を削除しない**。
  - 削除すれば JSON が cleaner になるが、本書 §5.9 のスコープ外。
  - 既存 `["信書隠匿罪"]` / `["窃盗罪", "信書隠匿罪"]` は CRIME_SIGNATURES 登録後
    に **実効性を獲得**するため、削除する必要はない (むしろ自然な状態に到達)。
- 将来、JSON 側を簡素化するため `allowed_cross_refs` を削除するか個別判断するのは
  **slotmap §5.11+ の整備案件**として保留 (本書 §5.9 §7 R3 で明示)。

#### 4. check_template_sync.py への影響

**なし**。template も HTML も不変。validate_content.py 単独編集のため
`check_template_sync.py` の `INTENTIONAL_DIFFS` dict は無関係。

#### 5. byte-identity への影響

**なし**。template 不変 + 既存 problems の JSON 不変 = HTML 出力に変化なし。
326-330 全 5 件で HTML SHA256 hash が完全に維持されることを実装フェーズで実証する。

#### 6. validate_structure.py への影響

**なし**。検査ロジック・データともに変更なし。

#### 7. validate_content.py への影響

- **dict データ追加のみ**、関数定義・ロジックは一切変更しない。
- 326-330 全件で `negative_check` に新規 trigger が発火する可能性を **事前に Grep で
  検証**する:

| 問題 ID | "263条" 出現 | "信書隠匿" 出現 | allowed_cross_refs 設定 | 結果予測 |
|---|---|---|---|---|
| 326 | なし | なし | なし | 影響なし (trigger 不発火) |
| 327 | なし | なし | なし | 影響なし |
| 328 | なし | なし | なし | 影響なし |
| 329 | あり | あり | `["信書隠匿罪"]` | 新規 trigger を allowed_cross_refs で skip → PASS 維持 |
| 330 | なし or あり (B説論点で) | あり | `["窃盗罪", "信書隠匿罪"]` | 同上、skip → PASS 維持 |

→ 326-328 は全くノータッチ、329/330 は事前設定済の allowed_cross_refs が **実効化** する形で PASS 維持。**dict 追加のみで regression なし**の確証。

#### 8. 想定リスク (R1-R3)

| ID | リスク | 想定影響 | 回避策 |
|---|---|---|---|
| **R1** | 罪名の正式表記揺れ (「信書隠匿罪」vs「信書隠匿の罪」等) | 329/330.json の `allowed_cross_refs` 文字列と CRIME_SIGNATURES key が不一致なら skip が機能せず | 329/330.json の `allowed_cross_refs` には既に `"信書隠匿罪"` で統一されており、本書 §5.9 §2 で同じ文字列を key として登録 → 一致確認済み |
| **R2** | 326-330 への regression | dict 追加のみなのでロジック上不可能だが念のため | (1) 326-328 で signature `"263条"` / `"信書隠匿"` が出現しないことを Grep で事前確認、(2) 全 5 件で validate_content 実行して PASS 維持を実証、(3) HTML SHA256 が修正前後で完全一致を実証 |
| **R3** | 将来 `allowed_cross_refs` を削除する際の追加作業 | 329/330.json の cleanup が将来案件として残る | slotmap §5.11+ の整備案件として記録。本書 §5.9 では削除しない。将来 §5.11 着手時に「`allowed_cross_refs` のうち CRIME_SIGNATURES 既登録罪のみのものは削除可」のルールを明示する |

#### 9. 実装手順

1. 修正前 baseline 取得: 326-330 の HTML SHA256 hash 記録、validate_content 全件 PASS 確認
2. 事前 Grep: 326-328 の HTML / JSON で signature `"263条"` `"信書隠匿"` が出現しないことを確認
3. `scripts/validate_content.py` の CRIME_SIGNATURES dict 末尾 (`# 必要に応じて追記` 直前) に `"信書隠匿罪": ["263条", "信書隠匿"]` を追加
4. 326-330 全件で `validate_content.py` を再実行
5. CP1: dict 追加のみ (ロジック変更なし) を Read tool で確証
6. CP2: 326-330 全件 HTML SHA256 byte-identical 維持を確認 (template/JSON 不変なので自明だが念押し)
7. CP3: validate_content 全件 PASS、regression なし
8. slotmap §5.9 §X に実測値記入

#### 10. §5.9 完了時点の実測 (記入義務、実装完了後に記入)

```
### §5.9 完了時点の同期実測 (実装完了時の実測値、2026-05-18 記入)

- 実装に要した時間:
    約 8 分 (見積 30 分以下 → さらに短縮)。
    内訳: 既存 dict 確認 + Grep 事前検証 2 min + dict 4 行追加 1 min +
    326-330 全件 SHA256 + validate_content 検証 5 min。
    本書 §5.9 の slotmap 本文化 (約 20 min) を含めても合計 30 分弱で完走。
    シリーズ最終案件として最小規模の実装となった。

- 追加した罪名数と内訳:
    **1 件** (信書隠匿罪)。signature は `["263条", "信書隠匿"]` の 2 個。
    既存登録 10 罪 (詐欺罪 / 盗品等罪 / 窃盗罪 / 強盗罪 / 横領罪 / 背任罪 /
    文書等毀棄罪 / 器物損壊罪 / 住居侵入罪 / 恐喝罪) に **+1 件で計 11 罪**。
    毀棄罪 / 損壊罪は既存登録 (文書等毀棄罪 + 器物損壊罪) でカバー済のため
    本書では追加せず、slotmap §5.11+ 候補として保留。

- 326-330 各々の HTML SHA256 修正前後 (byte-identical 維持確認):

  | 問題 ID | 修正前 SHA256 | 修正後 SHA256 | identical |
  |---|---|---|---|
  | **326** | `BEF153E033A09A21...` | `BEF153E033A09A21...` | **True ✅** |
  | **327** | `9C30BC5EA89F5BFF...` | `9C30BC5EA89F5BFF...` | **True ✅** |
  | **328** | `8AF2A098FBE1BB70...` | `8AF2A098FBE1BB70...` | **True ✅** |
  | **329** | `1A72A3BF0C6AEEE4...` | `1A72A3BF0C6AEEE4...` | **True ✅** |
  | **330** | `EEFA038D7A3E2EFB...` | `EEFA038D7A3E2EFB...` | **True ✅** |

  **5 件すべて byte-identical 完全維持**。template / JSON / render.py すべて
  不変なので HTML 再生成しても完全一致を確認 (validate_content は HTML を再
  読み込みするだけで、HTML 自体を変更しないため自明だが念のため記録)。

- validate_content 修正前後の結果 (全件 PASS 維持):

  | 問題 ID | crime | allowed_cross_refs | 修正前 | 修正後 | 効果 |
  |---|---|---|---|---|---|
  | 326 | 盗品等罪 | なし | PASS | **PASS** | 影響なし (signature 不出現) |
  | 327 | 盗品等罪 | なし | PASS | **PASS** | 同上 |
  | 328 | 盗品等罪 | なし | PASS | **PASS** | 同上 |
  | 329 | 器物損壊罪 | `["信書隠匿罪"]` | PASS | **PASS** | **allowed_cross_refs が実効化** → 信書隠匿罪 signature を skip して PASS 維持 |
  | 330 | 器物損壊罪 | `["窃盗罪", "信書隠匿罪"]` | PASS | **PASS** | 同上 |

  事前 Grep で 326-328 の HTML 内に "263条" "信書隠匿" の出現が **0 件** で
  あることを確認済 → 新規 trigger 発火の余地なし。329 (47 件) / 330 (10 件) は
  allowed_cross_refs で skip され PASS 維持。**dict 追加のみで regression なし**
  の事前予測が実証された。

- 本セッションシリーズ §5 案件完全完了の宣言コメント:

    **§5 配下の全消化対象案件が完走。326-330 シリーズの整備期は本書 §5.9 を
    もって正式完了。**

    完走した案件:
    - **§5.1-§5.4** (形式仕様): ox-grid-N / multi-select-N / single-choice-N /
      combination-N の 4 仕様。326-330 の 5 問題で全形式を実装。
    - **§5.5-§5.8** (WARN 4 系統消化): S14 drill-block / S17 professor sub-card /
      S51 ktx301-canon feature-tag / S71-AP33 answer-instruction canonical 文言。
      全 5 形式で WARN ゼロを達成。
    - **§5.9** (CRIME_SIGNATURES 拡張): 信書隠匿罪を 11 罪目として追加、
      329/330 の `allowed_cross_refs` を実効化。
    - **§5.10** (保守インフラ): `check_template_sync.py` CI 化スクリプトを
      新設、5 templates 同期義務違反を機械検証可能に。

    残る将来案件:
    - **§5.11+ 候補** (整備案件):
      - 329/330.json の `allowed_cross_refs` のうち、CRIME_SIGNATURES 既登録罪
        のみのものは削除可。本書 §5.9 §3 で保留と明示済。
      - 毀棄罪 / 損壊罪を独立 key として CRIME_SIGNATURES に追加するか判断
        (現状は文書等毀棄罪 + 器物損壊罪でカバー)。
    - **形式 #6 入口での AND 条件再判定** (slotmap §5.4 §7):
      - `inputs/tx-pdfs/331.pdf` 以降の追加または ranking / fill-in confirmed
        の時点で、(b) refactor 発火条件 AND ①/② を再判定。
      - 現時点では両条件とも不充足、(a) 戦略継続が妥当。

    本書 §5.9 で **§5 配下の構造的整備は完了**。次セッションでは新形式の
    追加または別科目 (KEN / MIN / SYO / MINS / KEIS / GSE) への展開を視野に。
```

---

### §5.10 template 同期検証スクリプトの設計と運用 (R-CI: check_template_sync.py)

#### 背景

`docs/session-330-completion.md` §9.3 で「次セッションの最優先タスク」として、また
slotmap §5.4 §8 §E の実測値判断で「次セッション (整備期) で最優先タスクとして導入推奨」
として宣言された、**5 本立て template の同期検証スクリプト**を新設する。

##### 現状の事実関係 (調査済)

- 5 本立て template は **diff 10 ペア**まで膨張、手動レビューは限界。
- 一方、**HEAD + CSS (L1-L2008) と JS block** は調査時点で 5 本すべてで
  byte-identical (sha256 一致) が維持されている:
  - HEAD + CSS: `DCA69064D21FC826...` (5 本一致)
  - JS block: `2480D62DC7C12C20...` (5 本一致、16,571 chars)
- 差分は **L2009 〜 `<script>` 開始直前**の領域に集約。
- 5 本立て diff 10 ペアの自動検証実測値は **589 ms (slotmap §5.4 §8 §B)**。
  手動の約 1000 倍速。

##### CI 化の必要性

- 形式 #6 (`331.pdf` 以降 or `ranking` / `fill-in` confirmed) 入口で
  AND 条件 ①/② を再判定する際、**「330 が既存 4 本で収まったか」の根拠**を
  機械的に再現できる必要がある (slotmap §5.4 §7 「(b) refactor 発火条件の判定」)。
- 手動 diff レビューは 5 本で限界、6 本立て (15 ペア) では不可能。
- CI 化スクリプトを **形式 #6 着手前に確立**することで、6 本立て到達時にも持続可能。

#### 決定事項

#### 1. スクリプトファイル名と配置

- `scripts/check_template_sync.py` を新規作成する。
- 既存スクリプト群 (`render.py` / `validate_structure.py` / `validate_content.py`) と
  同じディレクトリに配置。
- Python 3.10+ で動作、**stdlib のみ依存**（PyYAML 等の追加依存なし）。

#### 2. 11 論理セクション分割方式

template を以下の **11 論理セクション**に分割し、内容 hash で比較する:

| # | セクション名 | 構造マーカー | 同期義務 |
|---|---|---|---|
| 1 | `head` | `<!DOCTYPE html>` 〜 `<style>` 直前 | ✅ |
| 2 | `css` | `<style>` 〜 `</style>` (内側) | ✅ |
| 3 | `body_pre_toc` | `</style>` 〜 `<div class="toc-row">` 直前 | ✅ |
| 4 | `toc` | `<div class="toc-row">` 〜 `</div>` | ❌ 差分許容 (ラベル系統) |
| 5 | `marker_legend` | `<div class="marker-legend">` 〜 `</div>` | ✅ |
| 6 | `part_a` | `<section class="section" id="part-a">` 〜 `</section>` | ❌ 差分許容 |
| 7 | `a2` | `<section class="section" id="answer-area">` 〜 `</section>` | ❌ 差分許容 |
| 8 | `part_b` | PART B 見出し 〜 全 choice-section 終端（Phase 4-14 で `{{PART_B_FRAME}}` 単行 slot 化、レガシーフォールバック温存） | ❌ 差分許容 (件数 / ラベル) |
| 9 | `basis` | `<section class="section" id="basis">` 〜 `</section>` | ❌ 差分許容 (sec-nav back-link のみ) |
| 10 | `part_c_d` | `id="c-1"` 〜 `id="part-d"` 全範囲 + その他スタブ | ✅ |
| 11 | `footer_spec` | `<div class="footer-spec">` 〜 `</div>` | ✅ |
| 12 | `js` | `<script>` 〜 `</script>` (内側) | ✅ |

(計 12 セクションだが運用上は「同期義務 7 / 差分許容 5」の分類で扱う。)

##### 行番号ベース不採用の理由

- 5 本立てで開始行番号が前段の差分で前後する (例: A-2 の開始位置は base=L2070,
  ox4=L2068, sc5=L2087, comb5=L2095)。
- 行番号で「L2070-L2129 を A-2 と定義」のような硬直化はメンテ不能。
- **構造マーカー (HTML タグ / id / class / コメント) で動的抽出**し、抽出後の内容
  ハッシュで比較するのが正しい。

##### 境界マーカーの優先順位

- 第 1 候補: `id="..."` 属性 (一意、変更されにくい)
- 第 2 候補: `class="..."` 属性 (組合せで一意化)
- 第 3 候補: HTML コメント (例: `<!-- PART B ── 記述別解説 -->`、削除可能性あり、
  fallback として併用)

#### 3. 意図差分の表現方式

**Python dict（スクリプト内）を採用**する。

```python
# 意図差分仕様（slotmap.md §5.1 §3 / §5.2 §3 / §5.3 §3 / §5.4 §3 の写し）
# slotmap 更新時は本 dict も同期手動更新すること。
# 二重管理リスクは §5.10 §4 R1 として認識、将来案として YAML front-matter 化を §5.10 §5
# 「将来の一般化」に明記。
INTENTIONAL_DIFFS = {
    "toc":         {"sync_required": False, "varies_by_label_system": True},
    "part_a":      {"sync_required": False, "varies_by_format": True},
    "a2":          {"sync_required": False, "varies_by_answer_type": True},
    "part_b":      {"sync_required": False, "varies_by_choice_count": True},
    "basis":       {"sync_required": False, "back_nav_only": True},
    "head":        {"sync_required": True},
    "css":         {"sync_required": True},
    "body_pre_toc":{"sync_required": True},
    "marker_legend":{"sync_required": True},
    "part_c_d":    {"sync_required": True},
    "footer_spec": {"sync_required": True},
    "js":          {"sync_required": True},
}
```

##### 二重管理を許容する理由

- (1) **slotmap.md は人間向け設計合意**、(2) **dict は機械検証ロジック**、と役割を
  完全分離。
- markdown 表のパース (slotmap →dict 自動抽出) は表フォーマット変更で破綻するため、
  当面 dict は手動同期。
- 二重管理リスクは本書 §4 R1 として明示し、回避策として「template 編集時に必ず
  check_template_sync.py を実行」を作業の鉄則化する。
- 将来案として **YAML front-matter 化** / **dict を source of truth 化** を本書 §5
  「将来の一般化」に明記。

#### 4. CI 化形態

**独立実行（standalone audit）**を採用する。`render.py` パイプラインに組み込まない。

##### 想定するトリガー (3 通り)

| 形態 | 起動契機 | 推奨度 |
|---|---|---|
| (a) 手動 | 開発者が template 編集後に `python scripts/check_template_sync.py` を実行 | ★★★ |
| (b) pre-commit hook | Git `.git/hooks/pre-commit` で `templates/KTX_template*.html` 変更時に自動起動 | ★★ |
| (c) CI on push | GitHub Actions 等で push 時に自動起動 | ★ (将来) |
| (d) 定期監査 | cron / scheduled CI で月 1 回など | ★ (任意) |

##### render.py パイプラインに組み込まない理由

- `render.py` は **per-problem** で実行され、使用 template 1 本のみ参照。他 template の
  同期状態とは無関係。
- 毎 render で 5 本読込 → 10 ペア diff は無駄。
- template 編集トリガーの **イベント駆動**で起動するのが合理的。

#### 5. 計測機能

##### 仕様

- 10 ペア (C(5,2)) の diff を `difflib.unified_diff` + `time.perf_counter` で計測。
- 各ペアで:
  - diff 行数 (`n=0` のコンテキスト)
  - 実行時間 (μs 精度、ms 換算で出力)
- 集計値:
  - 総時間 (total_ms)
  - 平均 (mean_ms)
  - 中央値 (median_ms)

##### 出力フォーマット (3 形式)

| フォーマット | 用途 | フラグ |
|---|---|---|
| **text** (デフォルト) | 人間レビュー、CI ログ | `(default)` |
| **json** | 機械可読、CI ログ集計、自動 parse | `--json` |
| **markdown** | slotmap §5.N §8 への貼り付け用 | `--markdown` |

##### markdown フォーマット例

```markdown
| Pair (A vs B) | Diff lines | Time (ms) |
|---|---:|---:|
| KTX_template.html vs KTX_template_ox4.html | 47 | 3.8 |
| ... | ... | ... |

**Total**: 58.9 ms / **Mean**: 5.9 ms / **Median**: 4.0 ms
```

#### 6. CLI 仕様と exit code

##### コマンドライン引数

```
python scripts/check_template_sync.py [options]

Options:
  --strict          意図差分以外の全差分を ERROR 報告 (デフォルト)
  --summary         件数のみ報告 (CI 簡易モード)
  --measure-only    diff 検証はスキップ、10 ペアの実行時間のみ計測・出力
  --json            機械可読 JSON で結果出力
  --markdown        slotmap §5.N §8 への貼り付け用 markdown 表
  --pair PAIR       特定ペアのみ検証 (例: "KTX_template.html,KTX_template_comb5.html")
  -v / --verbose    各セクションの hash と diff を詳細表示
  -h / --help       使い方
```

##### exit code

| code | 意味 |
|---|---|
| 0 | sync OK (同期義務違反なし、意図差分のみ) |
| 1 | sync 違反検出 (unexpected diff あり) |
| 2 | 実行エラー (file not found / parse error 等) |

#### 7. 既存検証スクリプトとの独立性

| スクリプト | 対象 | 実行タイミング | check_template_sync との関係 |
|---|---|---|---|
| `render.py` | 単一 problem + 単一 template → HTML | per-problem、必要時 | **独立** (render は使用 template のみ参照) |
| `validate_structure.py` | HTML の構造 (S1-S79) | post-render | **独立** (HTML 単位検証) |
| `validate_content.py` | HTML と JSON の整合性 | post-render | **独立** (HTML + JSON 単位検証) |
| `check_template_sync.py` | **template ファイル群間の同期状態** | template 編集時 | 唯一の template 間検証ツール |

→ 4 つのスクリプトは互いに独立し、それぞれ異なる粒度の検証を担当する。

#### 8. 6 本目以降への拡張時の手順

将来 6 本目以降の template が追加される場合、以下の **3 手順**を踏む:

1. **dict 拡張**: `scripts/check_template_sync.py` の `INTENTIONAL_DIFFS` dict に
   新 template 固有の差分許容セクションを追加。
2. **意図差分テーブル追記**: slotmap §5.N §3 (新形式の章) に新 template との意図差分を
   明記。N=10 なら §5.N の §3 形式に従う。
3. **slotmap §5.10 自体の更新**: 11 セクション分割が拡張不要であることを確認し、
   必要なら §5.10 §2 の表に追記。

スクリプト起動時に `templates/` ディレクトリの実 file 数と dict 期待値の整合を
チェックする safety net も実装する (slotmap §5.10 §4 R3 参照)。

#### 想定リスク (R1-R10)

| ID | リスク | 想定影響 | 回避策 |
|---|---|---|---|
| **R1** | **二重管理乖離** (Python dict と slotmap §5.N §3 が不一致) | slotmap 更新時に dict 同期忘れ → 誤検出 | (a) **本書 §3「template 編集時には check_template_sync.py を必ず実行」を作業の鉄則化** (CLAUDE.md 更新は実装フェーズで実施)。(b) dict 冒頭に「slotmap §5.N §3 の写し、同期義務」コメント。(c) 将来 YAML front-matter 化で source of truth を一元化 (§5「将来の一般化」) |
| **R2** | **False positive** (意図差分の登録漏れ) | 既存の意図差分が ERROR 報告される | 初回実装後の WARN 出力を **全件レビュー**し、見落とした意図差分を dict に追加。Step 8 (本書 §H 実装順序) の "regression test" で確認 |
| **R3** | **False negative** (意図差分の過剰登録) | 本来 ERROR にすべき差分を見逃す | 本書 §6 で **件数上限**を設定 (各セクションごとに「diff 行数 ≤ N」の上限を併設)。例: TOC は 10 行以内、PART A は 80 行以内、A-2 は 50 行以内 |
| **R4** | 論理セクション分割の regex が template 編集で壊れる | 境界マーカーが変わると section が誤切り出し | section 境界は **複数のマーカーを併用** (id / class / コメント)。fallback 検出も実装 |
| **R5** | difflib のセマンティクス vs バイトレベル | 同じ意味の差分を「異なる」と判定 / 逆 | 比較は **正規化なしの行単位**に統一。空白・改行コードはそのまま比較 |
| **R6** | 改行コード (CRLF vs LF) の混在 | Windows / Linux 間で hash が一致しない | 読込時に `\r\n` を `\n` に正規化してから hash 計算 |
| **R7** | 文字エンコーディング差 (BOM 付き / なし) | hash が変わる | `encoding='utf-8-sig'` で BOM を吸収 or 明示的に BOM 除去 |
| **R8** | パフォーマンス劣化 (template 肥大化) | 1 本 5,000 行超で 10 ペア diff が秒オーダー | 現状 95KB 程度、10 ペアで 0.6 秒の実測値 (slotmap §5.4 §8 §B)。10 倍肥大しても 6 秒で許容範囲 |
| **R9** | CI 環境差 (Windows / Linux / macOS) | パス区切り / シェル / Python 版差 | Python stdlib のみ、`pathlib.Path` 使用、`os.sep` 依存なし。Python 3.10+ で動作確認 |
| **R10** | 計測ノイズ (OS スケジューラ等) | 10 ペア diff の実測値がブレる | warm-up run、複数回計測の min / median 採用、`--measure-only` で純粋計測モード |

#### 将来の一般化

##### `--auto-fix` モード (v2 候補)

- 同期義務違反箇所を一方の template (base = `KTX_template.html` を canonical) に
  揃える自動修復モード。
- リスク: 意図せず意図差分も上書きする可能性。慎重な実装と確認 prompt が必要。
- 当面は手動修復、`--auto-fix` は v2 で検討。

##### GitHub Actions ワークフロー定義の同梱

- `.github/workflows/template-sync.yml` を将来同梱。
- `templates/*.html` 変更時に自動起動、PR コメントに sync 結果を投稿。
- 本フェーズではスコープ外、v2 候補。

##### 6 本目以降への一般化

- 上記 §8 手順 (dict 拡張 / slotmap §5.N §3 追記 / §5.10 §2 表更新) を踏まえれば、
  6 本目以降も同パターンで対応可能。
- 7 本目 (21 ペア)、8 本目 (28 ペア) と増えても、自動検証の時間は線形増加で
  耐えうる範囲 (現状 589 ms × 倍率)。

##### YAML front-matter 化 / dict を source of truth 化 (二重管理解消策)

- **案 (i)**: slotmap §5.N §3 の表を YAML front-matter として
  `templates/template-diff-spec.yaml` に切り出し、slotmap と dict の両方が
  YAML を参照する。
- **案 (ii)**: Python dict を source of truth とし、slotmap §5.N §3 の表を
  スクリプトから自動生成する (markdown 出力モード追加)。
- 案 (i) は人間レビュー優先、案 (ii) は機械精度優先。
- 本フェーズではどちらも採用せず、二重管理は手動運用 + 鉄則化で吸収する。

#### CLAUDE.md / README への追記項目 (実装時に対応)

本書 §5.10 で確立した運用を実コードに反映するため、実装フェーズで CLAUDE.md /
README に以下を追記する:

##### CLAUDE.md「作業の鉄則」への追加項目

> ### 6. template 編集時の必須手順
> 1. `templates/KTX_template*.html` のいずれかを編集したら、
>    `python scripts/check_template_sync.py` を実行する。
> 2. exit 0 (同期 OK) を確認してからコミット。
> 3. exit 1 (同期違反) なら、報告された違反箇所を修正してから再実行。
> 4. 意図差分が新規追加された場合は **slotmap §5.N §3 と
>    `INTENTIONAL_DIFFS` dict の両方**を更新する。

##### CLAUDE.md「一括処理コマンド」への追加検討

- 一括処理の前段に `check_template_sync.py` を pre-flight check として追加するか検討。
- ただし render の都度 5 本読込はパフォーマンス無駄なので、**一括処理開始時 1 回のみ**
  実行する形が現実的 (起動 prologue として追加)。

##### README (もしくは docs/ 配下) への運用ガイド

- 「template 編集ワークフロー」セクションを新設。
- 上記 4 ステップを記載。
- `--measure-only` / `--markdown` 等のオプションも例示。

#### 実装規模見積もり

| 観点 | 試算 |
|---|---|
| **行数** | 約 **430 行** (CLI 30 + 読込 20 + section split 80 + hash 40 + 意図差分 70 + 計測 50 + 出力 80 + main 30 + docstring 30) |
| **所要時間** | 約 **5 時間** (Step 1-9 + 任意 Step 10-11) |
| **依存** | Python 3.10+ stdlib のみ (argparse / pathlib / difflib / hashlib / time / re / json) |

slotmap §5.4 §8 §E の「1-2 時間」見積もりは楽観的すぎたため、本書で **5 時間**に
修正する。これでも CI 化の費用対効果は明白 (手動 10-15 分 × 毎回 vs 一度の 5 時間
+ ランタイム 1 秒未満)。

#### 推奨実装順序 (Step 1〜11)

| Step | 作業 | 検証ポイント | 工数 |
|---|---|---|---|
| 1 | 論理セクション境界の regex 定義 | 5 本すべてで section 抽出成功 | 30 min |
| 2 | ファイル読込 + section split 実装 | 12 section 抽出される | 45 min |
| 3 | section hash 計算 + 同期義務セクション (7 種) の 5 本一致検証 | §5.10 §1 の実測 hash (`DCA69064...`, `2480D62D...`) と一致 | 30 min |
| 4 | INTENTIONAL_DIFFS dict 実装 + 差分許容セクションのクロスペア検証 | TOC ラベル違いが allowed と認識 | 45 min |
| 5 | 10 ペア diff timing 計測 (difflib + perf_counter) | 実測値 ~590 ms 再現 | 30 min |
| 6 | レポート出力 (text モード) + exit code 実装 | 5 本 sync 維持状態で exit 0 | 45 min |
| 7 | CLI 引数パース (argparse) + 各モード | 各モードで正しい出力 | 30 min |
| 8 | regression test (わざと 1 本の同期義務 section を破壊) | exit 1 + 違反箇所を正しく報告 | 20 min |
| 9 | docstring + 使用例 + slotmap §5.10 への運用 ガイド記載 | 第三者が読んで運用可能 | 30 min |
| 10 (任意) | pre-commit hook サンプル提供 | template 編集 commit で自動起動 | 15 min |
| 11 (任意) | `--markdown` 出力で slotmap §5.N §8 への直接貼り付け | フォーマット確認 | 15 min |
| **合計** | — | — | **約 5 時間** |

#### 8. §5.10 完了時点の同期実測 (記入義務、実装完了後に記入)

slotmap §5.3 §8 / §5.4 §8 で確立した記録フォーマットを継承し、
check_template_sync.py の実装完了時に以下を本書に追記する義務がある。
**現時点では空欄**として用意:

```
### §5.10 完了時点の同期実測 (実装完了時の実測値、2026-05-18 記入)

- 実装に要した時間:
    約 1.5 時間 (本書 §「実装規模見積もり」5 時間と比べ大幅に短縮)。
    短縮要因: (1) slotmap §5.10 §2-§6 で設計が事前合意済みで迷いなく着手、
    (2) §5.4 §8 の実測値で difflib + perf_counter の挙動が事前検証済、
    (3) 11 セクション分割を素直に regex で実装、(4) Python stdlib のみで依存ゼロ。
    最終ファイル: 約 430 行、約 17 KB。

- 初回実行で検出された違反件数 (false positive 込み):
    初回: **1 件**（`pre_part_a` セクション、5 variants 検出）。
    原因: slotmap §5.1-§5.4 §3 で「PART A 見出しコメント」を意図差分として明示済みだったが、
    INTENTIONAL_DIFFS dict の初期定義で `pre_part_a` を sync_required としてしまった
    登録漏れ (R2 false positive の典型例)。
    対処: dict の `pre_part_a` を `sync_required=False` に修正し再実行 → **exit 0 達成**。
    本物の同期義務違反は **0 件** (5 本の HEAD/CSS/JS/marker_legend/part_c_d/footer_spec
    すべて hash 一致を確認、§5.4 §8 §B の `DCA69064...` / `2480D62D...` と整合)。

- dict 登録した意図差分件数:
    **計 13 セクション** = sync_required **7 件** (head / css / body_pre_toc /
    marker_legend / part_c_d / footer_spec / js) + diff_allowed **6 件** (toc /
    pre_part_a / part_a / a2 / part_b / basis)。
    slotmap §5.1 §3 / §5.2 §3 / §5.3 §3 / §5.4 §3 の意図差分テーブルと整合確認済。

- 10 ペア diff timing (実測、`--format=markdown --timing` 出力):

  | Pair (A vs B) | Diff lines | Time (ms) |
  |---|---:|---:|
  | KTX_template.html vs KTX_template_ox4.html | 47 | 5.864 |
  | KTX_template.html vs KTX_template_msel5.html | 100 | 4.920 |
  | KTX_template.html vs KTX_template_sc5.html | 116 | 4.997 |
  | KTX_template.html vs KTX_template_comb5.html | 82 | 4.057 |
  | KTX_template_ox4.html vs KTX_template_msel5.html | 115 | 4.593 |
  | KTX_template_ox4.html vs KTX_template_sc5.html | 131 | 4.619 |
  | KTX_template_ox4.html vs KTX_template_comb5.html | 111 | 4.462 |
  | KTX_template_msel5.html vs KTX_template_sc5.html | 24 | 3.943 |
  | KTX_template_msel5.html vs KTX_template_comb5.html | 76 | 4.714 |
  | KTX_template_sc5.html vs KTX_template_comb5.html | 88 | 4.815 |

  **Total**: 46.984 ms / **Mean**: 4.698 ms / **Median**: 4.714 ms

  §5.4 §8 §B の PowerShell Compare-Object 実測値 (589 ms) と比較し、**Python
  difflib 経由で約 12 倍速** (5.5 → 46.984 ms 換算ではなく、Compare-Object は単発で
  約 59 ms/ペア vs Python は 約 4.7 ms/ペア)。
  CI 化スクリプトが手動 / Compare-Object より高速 = CI 環境での実用性確立。

- (b) refactor 発火条件 ① への影響 (CI 化により実測判定が可能になったか):
    **実測判定が可能になった**。slotmap §5.4 §7 の AND 条件 ① 「330 が既存 4 本の
    いずれの派生でも合理的に収まらない」を、本スクリプトの **exit code (0/1)** で
    機械的に検証可能。
    具体的には: 形式 #6 入口で新 template を追加した直後に
    `python scripts/check_template_sync.py` を実行し、
    - **exit 0**: 同期義務違反なし → 条件 ① **不充足** ((a) 戦略継続が妥当)
    - **exit 1**: 同期義務違反あり → 条件 ① **充足**、(b) refactor 発火を検討
    という形で **「推定」から「実測」への完全移行**が達成された。
    330 完走時 (本書 §5.4 §8) の主観的圧力 3/5 と本実装後の合理性確認により、
    形式 #6 入口での再評価が **CI ベース**で実施可能となった。
```

これにより「CI 化スクリプト導入」自体の実測値も記録され、形式 #6 入口での
判断材料がさらに堅牢化される。

---

## §5.11 326-330 シリーズ最終整備フェーズ — allowed_cross_refs 削除整理 / 毀棄罪・損壊罪独立 key 化 の判定記録

### §5.11 §1 目的

§5.10 までで 326-330 シリーズの format 実装 (5 種) と WARN 4 系統消化 (S14/S17/S51/S71-AP33) が完了し、CI safety net (`check_template_sync.py`) も整備された。byte-identity chain は §5.4 から §5.10 まで継続維持されている。

本セクションは「整備済みシリーズに対する追加 cleanup 案件」として以下 2 件を検討し、各々を「実施」または「見送り」と判定し、理由を本書に明記して将来の重複調査を防ぐ。

- **(a) allowed_cross_refs 削除整理**: 329.json `["信書隠匿罪"]` および 330.json `["窃盗罪", "信書隠匿罪"]` の field を削除し、JSON を簡素化できるか
- **(b) 毀棄罪 / 損壊罪 の独立 key 化**: `validate_content.py` の `CRIME_SIGNATURES` に "毀棄罪" "損壊罪" の独立 key を追加すべきか

「変更しない」も判断の一形態であり、見送る場合も判断根拠を明記する。

### §5.11 §2 対象案件一覧と結論

| # | 案件 | 対象 file | 提案変更 | 判定 |
|---|---|---|---|---|
| (a-1) | ACR 削除 | problems/329.json | `allowed_cross_refs: ["信書隠匿罪"]` 削除 | **見送り** |
| (a-2) | ACR 削除 | problems/330.json | `allowed_cross_refs: ["窃盗罪", "信書隠匿罪"]` 削除 | **見送り** |
| (b-1) | key 追加 | scripts/validate_content.py | `CRIME_SIGNATURES["毀棄罪"]` 追加 | **見送り** |
| (b-2) | key 追加 | scripts/validate_content.py | `CRIME_SIGNATURES["損壊罪"]` 追加 | **見送り** |

→ **4 件すべて見送り**。本セクションは判断記録のみで、コード/JSON/template への変更は **一切行わない**。

### §5.11 §3 意図差分テーブル — 案件 (a) の前提変化

§5.9 で 信書隠匿罪 を CRIME_SIGNATURES に追加した結果、329/330 の `allowed_cross_refs` field の意味が **質的に変化** した。

| 観点 | §5.9 以前 | §5.9 以後（現状） |
|---|---|---|
| 信書隠匿罪 の CRIME_SIGNATURES 登録 | 未登録 | **登録済** (`["263条", "信書隠匿"]`) |
| 信書隠匿罪 signature の negative_check 対象性 | 検査されない (key 自体ない) | **検査される**（current_crime / ACR でなければ） |
| 329 ACR=`["信書隠匿罪"]` の効果 | documentation のみ (no-op filter) | **signature skip filter として機能** |
| 330 ACR=`["信書隠匿罪", "窃盗罪"]` の効果 | "信書隠匿罪" は documentation のみ、"窃盗罪" は filter | **両方とも signature skip filter として機能** |

§5.9 以前であれば「ACR から "信書隠匿罪" は documentation only field なので削除可」と評価できたが、§5.9 以後は **削除すると validate_content が FAIL する実効性のあるフィルタ**へ昇格した。

### §5.11 §4 判定ロジック検証 (a) — ACR 削除時の挙動シミュレーション

`validate_content.py` L130-148 (`negative_check`) のロジック:

```python
skip = set(allowed_cross_refs) | {current_crime}
for crime, signatures in CRIME_SIGNATURES.items():
    if crime in skip:
        continue  # この罪の signature 検査は skip
    for sig in signatures:
        if sig in html:
            errors.append(f"[NEGATIVE] '{sig}' (signature of {crime}) found ...")
```

#### 329 シミュレーション (crime="器物損壊罪")

| 状態 | skip 集合 | 信書隠匿罪 signature 検査 | HTML 内出現 | 判定 |
|---|---|---|---|---|
| **現状**（ACR 保持） | {器物損壊罪, 信書隠匿罪} | 検査 skip | 263条 / 信書隠匿 多数 | **PASS** |
| **ACR 削除後** | {器物損壊罪} のみ | **検査実行** | 263条 / 信書隠匿 trigger | **FAIL** |

329 HTML は信書隠匿罪に関する理論問題（A/B/C 説で信書隠匿罪を器物損壊罪の減軽類型 vs 拡張類型と位置づける学説対立）であり、本文に「263条」「信書隠匿」が頻出することは題意上必然。ACR を削除すれば signature 検査が走り、本来 PASS だった HTML が FAIL に転落する。**削除不可**。

#### 330 シミュレーション (crime="器物損壊罪")

| 状態 | skip 集合 | 信書隠匿罪 検査 | 窃盗罪 検査 | 判定 |
|---|---|---|---|---|
| **現状**（ACR 保持） | {器物損壊罪, 信書隠匿罪, 窃盗罪} | skip | skip | **PASS** |
| **ACR 削除後** | {器物損壊罪} のみ | **実行** → 263条/信書隠匿 trigger | **実行** → 235条/不法領得の意思 trigger | **FAIL** |

330 は「毀棄及び損壊の罪」を抽象的に論ずる学説対立問題で、信書隠匿罪条文（263条）と窃盗罪条文（235条）を比較概念として正面から扱う。ACR を削除すれば両系統の signature が trigger し、二重に FAIL する。**削除不可**。

### §5.11 §5 判定ロジック検証 (b) — 毀棄罪 / 損壊罪 独立 key 化の評価

#### 既存 CRIME_SIGNATURES のカバー範囲 (11 keys)

```
詐欺罪 / 盗品等罪 / 窃盗罪 / 強盗罪 / 横領罪 / 背任罪 /
文書等毀棄罪 / 器物損壊罪 / 住居侵入罪 / 恐喝罪 / 信書隠匿罪
```

毀棄系・損壊系で既登録なのは:

| 既存 key | signature |
|---|---|
| 文書等毀棄罪 | 258条 / 259条 / 公用文書毀棄 / 私用文書毀棄 / 電磁的記録毀棄 |
| 器物損壊罪 | 261条 / 効用侵害 |
| 信書隠匿罪 | 263条 / 信書隠匿 |

#### 「毀棄罪」「損壊罪」独立 key の候補 signature と問題点

| 候補 key | 候補 signature | 問題点 |
|---|---|---|
| 毀棄罪 | `"毀棄"` | **一般語**。「毀棄罪」「文書等毀棄罪」「公用文書毀棄」「毀棄又は隠匿」など多様な複合文脈で出現。**誤検出多発** |
| 毀棄罪 | `"毀棄罪"` | 「文書等毀棄罪」など複合罪名内に部分一致して**誤検出**。326-330 で crime="毀棄罪" 単独使用問題は存在しない |
| 損壊罪 | `"損壊"` | 「器物損壊罪」「損壊行為」「損壊概念」など概念語として **理論問題本文に頻出**。誤検出多発 |
| 損壊罪 | `"損壊罪"` | 「器物損壊罪」など複合罪名内に部分一致して**誤検出** |

#### 326-330 における crime field 使用状況

```
326: crime="盗品等罪"
327: crime="盗品等罪"
328: crime="盗品等罪"
329: crime="器物損壊罪"
330: crime="器物損壊罪"
```

「毀棄罪」「損壊罪」を crime field の値として使用する問題は本シリーズに存在せず、追加しても skip 対象になる場面がない。

#### 「毀棄罪 / 損壊罪」を独立 key として追加した場合の効果

- 329/330 では skip 集合に「器物損壊罪」のみ含まれ、新規追加された「毀棄罪」「損壊罪」key は **skip 対象外**
- HTML 中の「損壊」「毀棄」（理論用語として頻出）が signature trigger → **本来 PASS だった 329/330 が FAIL に転じる**
- 回避するには ACR に「毀棄罪」「損壊罪」を追加する必要があり、それは案件 (a) の「ACR 削除整理」と **正反対の操作** で、JSON が膨張するだけ

→ **追加メリット皆無、誤検出リスク甚大、既存 3 key (文書等毀棄罪 / 器物損壊罪 / 信書隠匿罪) で 326-330 シリーズの毀棄損壊系カバー範囲は十分**。見送り。

### §5.11 §6 結論

| 案件 | 判定 | 理由 |
|---|---|---|
| (a) 329/330 allowed_cross_refs 削除 | **見送り** | §5.9 で信書隠匿罪が CRIME_SIGNATURES に登録された結果、ACR は documentation 用 no-op field から **実効性のある signature skip filter** へ昇格。削除すると validate_content が FAIL する |
| (b) 毀棄罪 / 損壊罪 独立 key 追加 | **見送り** | 候補 signature が一般語すぎて誤検出多発、既存 3 key (文書等毀棄罪 / 器物損壊罪 / 信書隠匿罪) で 326-330 の毀棄損壊系カバー範囲は十分。追加すれば既存 PASS 問題が FAIL に転じる逆効果 |

両見送りの帰結として、本セクションは判断記録のみであり、コード/JSON/template/schema への変更は **一切行わない**。

### §5.11 §7 §5.9 §12.6 記述訂正

§5.9 §12.6 (`templates/KTX_template_slotmap.md` 内) において以下の趣旨の記述を残していた:

> 「信書隠匿罪が CRIME_SIGNATURES 登録済となったため、329/330 の allowed_cross_refs 内の "信書隠匿罪" は削除可（将来 cleanup 案件）」

**これは誤り** である。本セクション §5.11 §4 のシミュレーションで覆る。正しい認識は:

> 「信書隠匿罪が CRIME_SIGNATURES に登録されたことで、329/330 の `allowed_cross_refs` 内の "信書隠匿罪" は documentation field から **signature skip filter へ昇格**した。**削除すると validate_content が FAIL する** ため、削除不可（恒久保持必須）。」

§5.9 §12.6 の旧記述は履歴として残置するが、本 §5.11 §7 で訂正したことを以て公式見解は本セクションが上書きする。次回 slotmap を参照する際は §5.11 §6 / §7 の判定が最終解として有効。

### §5.11 §8 影響範囲

本セクションは判断記録 + 旧記述訂正のみで、実 file 変更ゼロ:

| 対象 | 変更 |
|---|---|
| schema/problem.schema.json | 変更なし |
| 5 templates (KTX_template*.html) | 変更なし |
| scripts/render.py | 変更なし |
| scripts/validate_structure.py | 変更なし |
| scripts/validate_content.py | 変更なし（CRIME_SIGNATURES 11 keys 維持） |
| scripts/check_template_sync.py | 変更なし |
| problems/326.json … problems/330.json | 変更なし（特に 329/330 ACR 保持） |
| outputs/tx/刑TX/刑TX326-330.html | **変更なし**（byte 不変） |
| docs/session-warn-complete.md | §5.11 完了追記（後段） |
| templates/KTX_template_slotmap.md | **本 §5.11 セクション追加のみ** |

→ byte-identity chain (§5.4-§5.10 で確立) は完全維持。CP1-CP5 すべて satisfy。

### §5.11 §9 実装手順 (Phase 3 相当)

判定が両見送りであるため、Phase 3「実装」では **何も実行しない**。具体的に何が「行われない」かを明示:

1. 329.json / 330.json は **touch しない**（`allowed_cross_refs` field 恒久保持）
2. validate_content.py の CRIME_SIGNATURES は **変更しない**（11 keys 維持、毀棄罪/損壊罪 key 追加なし）
3. 5 template の feature-tag を変更しない
4. schema / render.py / validate_structure.py を変更しない
5. **HTML 再生成しない**（byte SHA256 chain は §5.10 末で記録した値が依然 valid）

→ 唯一の成果物は本 slotmap §5.11 セクションと、docs/session-warn-complete.md への追記。

### §5.11 §10 CP1-CP5 維持確認

| CP | 内容 | 維持状態 |
|---|---|---|
| CP1 | schema / template / render / validate ロジック変更禁止 | ✅ 一切変更なし |
| CP2 | check_template_sync.py exit 0 維持 | ✅ template 不変 → 自明 |
| CP3 | 326-330 HTML byte-identical 維持 | ✅ HTML 再生成しない |
| CP4 | validate_content all PASS 維持 | ✅ 既存 ACR 保持により PASS 継続 |
| CP5 | slotmap §5.11 §X 5 項目記入 | ✅ 後段 §5.11 §X で記入完了 |

### §5.11 §11 risk と検出

#### 主 risk

「§5.11 が判断記録のみで終わったことを user / 次セッションが見落とし、何らかの cleanup が行われた前提で作業を進めること」。

#### mitigation

- 本 §5.11 §2 / §6 / §9 で「変更なし」を太字で明示
- docs/session-warn-complete.md にも「§5.11 = 判断記録のみ、実 code 変更なし」を明記
- 次セッションでこの slotmap を参照する際、§5.11 §2 の判定表が即座に視認できるよう配置
- §5.9 §12.6 の誤記述問題と同じ轍を踏まないよう、訂正セクション (§5.11 §7) を独立に設けて参照可能化

### §5.11 §12 evidence appendix

#### A. validate_content.py の現状 CRIME_SIGNATURES (11 keys, L48-117)

```python
"詐欺罪":     ["246条", "1項詐欺", "2項詐欺", "欺罔", "錯誤に基づく交付", "詐欺利得"],
"盗品等罪":   ["256条", "257条", "盗品等保管", "盗品等有償譲受", "盗品等無償譲受",
              "盗品等運搬", "盗品等有償処分あっせん", "贓物", "牙保"],
"窃盗罪":     ["235条", "不法領得の意思", "占有侵害"],
"強盗罪":     ["236条", "238条", "事後強盗", "強盗利得", "反抗を抑圧"],
"横領罪":     ["252条", "253条", "業務上横領", "委託物横領", "占有離脱物横領"],
"背任罪":     ["247条", "任務違背", "図利加害目的"],
"文書等毀棄罪": ["258条", "259条", "公用文書毀棄", "私用文書毀棄", "電磁的記録毀棄"],
"器物損壊罪": ["261条", "効用侵害"],
"住居侵入罪": ["130条", "正当な理由がないのに"],
"恐喝罪":     ["249条", "1項恐喝", "2項恐喝"],
"信書隠匿罪": ["263条", "信書隠匿"],   # §5.9 で追加
```

#### B. 329.json / 330.json の現状 ACR field（保持される値）

```jsonc
// 329.json L7-8
"crime": "器物損壊罪",
"allowed_cross_refs": ["信書隠匿罪"],

// 330.json
"crime": "器物損壊罪",
"allowed_cross_refs": ["窃盗罪", "信書隠匿罪"],
```

#### C. negative_check ロジック原文 (validate_content.py L130-148)

```python
def negative_check(html: str, current_crime: str,
                   allowed_cross_refs: list[str]) -> list[str]:
    errors: list[str] = []
    skip = set(allowed_cross_refs) | {current_crime}
    for crime, signatures in CRIME_SIGNATURES.items():
        if crime in skip:
            continue
        for sig in signatures:
            if sig in html:
                offset = html.find(sig)
                snippet = html[max(0, offset-20): offset+len(sig)+20].replace("\n", " ")
                errors.append(
                    f"[NEGATIVE] '{sig}' (signature of {crime}) "
                    f"found at offset {offset}: ...{snippet}..."
                )
    return errors
```

#### D. 329 / 330 HTML 内 signature 出現概数

| signature | 329 出現 | 330 出現 | trigger 元 |
|---|---|---|---|
| 263条 | 多数 | 数件 | 信書隠匿罪 |
| 信書隠匿 | 多数 | 数件 | 信書隠匿罪 |
| 235条 | 0 | 数件 | 窃盗罪 |
| 不法領得の意思 | 0 | 数件 | 窃盗罪 |
| 占有侵害 | 0 | 0 | 窃盗罪 |

→ ACR 削除時に trigger するのは、329 では信書隠匿罪 (263条 / 信書隠匿) のみ、330 では信書隠匿罪 + 窃盗罪 (235条 / 不法領得の意思) の両系統。

### §5.11 §X 標準 5 項目記録 (CP5 充足)

#### §X.1 目的

326-330 シリーズの最終整備フェーズとして、(a) `allowed_cross_refs` 削除整理 と (b) 毀棄罪 / 損壊罪 独立 key 化 の 2 件を検討し、各々の実施可否を判定する。判定が「見送り」の場合は理由を文書化して将来の重複調査を防ぐ。同時に §5.9 §12.6 の誤記述を訂正する。

#### §X.2 対象

| 対象 | 検討内容 | 判定 |
|---|---|---|
| 329.json `allowed_cross_refs` | 削除して JSON 簡素化 | 見送り（FAIL に転落するため不可） |
| 330.json `allowed_cross_refs` | 削除して JSON 簡素化 | 見送り（FAIL に転落するため不可） |
| CRIME_SIGNATURES["毀棄罪"] | 独立 key 追加 | 見送り（誤検出多発リスク） |
| CRIME_SIGNATURES["損壊罪"] | 独立 key 追加 | 見送り（誤検出多発リスク） |

#### §X.3 変更点

**コード/JSON/template 変更ゼロ**。

| 対象 file | 変更 |
|---|---|
| problems/329.json | なし |
| problems/330.json | なし |
| scripts/validate_content.py | なし |
| その他全 file | なし |
| **templates/KTX_template_slotmap.md** | §5.11 セクション追加（本セクション） |
| **docs/session-warn-complete.md** | §5.11 完了追記 + 326-330 シリーズ最終 close 宣言 |

#### §X.4 検証

| 検証種別 | 実行要否 | 結果 |
|---|---|---|
| check_template_sync.py | 不要（template 不変） | 既存 PASS (exit 0) 継続維持 |
| validate_structure.py (S1-S77) | 不要（HTML 不変） | 既存 ERROR 0 / WARN 0 継続維持 |
| validate_content.py (326-330) | 不要（JSON/HTML 不変） | 既存 all PASS 継続維持 |
| HTML SHA256 chain | 不変（再生成しない） | §5.10 末で記録した hash がそのまま valid |

#### §X.5 次の作業

次セッションで以下 3 候補から方針選択:

- **候補 X**: §5.12+ 追加 cleanup 案件 (ACR 整理以外の整備、template feature 追加、docs 整理 etc.)
- **候補 Y**: 別科目展開 (KEN / MIN / SYO / MINS / KEIS / GSE の 1 科目で 326-330 と同等の format multiplexing を実施)
- **候補 Z**: 形式 #6 待機 (新規 PDF 入手まで休止)

候補別の評価および推奨は、本セッション末の「3-way 比較レポート」（§5.11 §13）で提示する。

### §5.11 §13 X / Y / Z 3-way 比較レポート

#### 評価軸

| 軸 | 説明 |
|---|---|
| **学習価値** | xnh の予備試験対策コンテンツ整備という最終目標への直接寄与度 |
| **CI 安全性** | byte-identity chain / WARN 0 / ERROR 0 の維持しやすさ |
| **テンプレ汎用性** | この作業で確立した知見が他科目・他形式に横展開可能か |
| **実装コスト** | 1 セッションで完了可能か、複数セッションに跨るか |
| **着手敷居** | 開始時に必要な前提準備量 |
| **撤退コスト** | 中途半端な状態で次に切り替える場合の損失 |

#### 候補 X: §5.12+ 追加 cleanup 案件

| 軸 | 評価 |
|---|---|
| 学習価値 | **低**：xnh の学習コンテンツ自体は増えない。整備のための整備になりがち |
| CI 安全性 | 高（既存範囲で完結） |
| テンプレ汎用性 | **低**：326-330 ローカル整備の延長 |
| 実装コスト | 中（案件次第） |
| 着手敷居 | 低（既存環境継続） |
| 撤退コスト | 低 |

**評価**: §5.11 で主要 cleanup 案件 ((a)(b)) の見送りが確定した以上、§5.12+ で着手すべき価値の高い cleanup 案件は **現時点で見当たらない**。ACR / signature 系以外の整備案件 (docs 整理、命名統一 etc.) は xnh の本来目的に直結しないため、低優先度。

#### 候補 Y: 別科目展開（KEN / MIN / SYO / MINS / KEIS / GSE）

| 軸 | 評価 |
|---|---|
| 学習価値 | **最高**：xnh の予備試験対策コンテンツが 1 科目分一気に増える |
| CI 安全性 | 中：別科目で format/schema が刑法と同じか要検証。だが既存 5 format を流用できれば高 |
| テンプレ汎用性 | **最高**：326-330 で確立した 5 format / 12 drill / professor sub-card / feature-tag / CI safety net をそのまま転用可能 |
| 実装コスト | 中〜高：5 問単位なら 326-330 と同等の 5-6 セッション規模 |
| 着手敷居 | 中：別科目の PDF 入手と JSON 化が必要。inputs/tx-pdfs/ 配下に該当科目の PDF があるかの事前確認 |
| 撤退コスト | 中：途中で止めても各問題は独立完成可能 |

**評価**: 326-330 シリーズで以下の **再利用可能資産** を確立した:

1. 5 種 format (ox-grid-5 / ox-grid-4 / multi-select-5 / single-choice-5 / combination-5) と 5 template
2. schema oneOf 分岐 + override_pattern P1-P5
3. validate_structure (S1-S77) + validate_content (signature-based)
4. check_template_sync.py CI safety net
5. drill_blocks 12 個 + professor sub-cards (PART E ロジック)
6. CRIME_SIGNATURES 11 keys (財産罪 + 隣接領域カバー)
7. CP1-CP5 self-defense rules

これらは刑法以外の科目に **70-90% 流用可能**。特に format / template / CI safety net / drill-block 構造は科目非依存。schema の crime field と CRIME_SIGNATURES のみ科目別に拡張が必要。

#### 推奨候補内訳（候補 Y 内）

| 科目 | 接頭辞 | 推奨度 | 理由 |
|---|---|---|---|
| **憲法** | KEN | ★★★ | 学説対立問題が多く 326-330 で確立した combination / single-choice / multi-select 形式と相性良。条文番号 signature が刑法と完全分離（重複検出リスク低）。判例も「百選Ⅰ」系統で別 namespace |
| **民法** | MIN | ★★ | 条文範囲広く CRIME_SIGNATURES 相当 dict 整備に initial cost。学説対立は多いが財産罪と概念混入リスク（"占有" 等が両科目で別意味） |
| **民訴** | MINS | ★ | 罪別 signature 構造が直接は当てはまらない（罪概念がない）。validate_content の signature 設計を「論点別 signature」に拡張する必要 |
| **刑訴** | KEIS | ★★ | 刑法と隣接領域で signature 重複懸念（"窃盗" "強盗" 等が手続事案で再登場）。ACR 必須化のコスト増 |
| **商法** | SYO | ★ | 条文範囲広く signature 設計 initial cost 高 |
| **行政法** | GSE | ★ | 「処分」「適格」など民訴と同様に論点別 signature 拡張要 |

→ **候補 Y 内推奨は憲法 (KEN)**。理由:

1. **signature namespace 完全分離**: 憲法条文 (1条 / 9条 / 14条 / 21条 etc.) は刑法と重複ゼロ。新 dict 追加だけで済む
2. **format 流用率高**: 学説対立問題が多く、326-330 で確立した combination-5 / multi-select-5 / single-choice-5 が高頻度で再利用可能
3. **判例引用形式互換**: 憲法判例は「百選Ⅰ」系統で構造同じ
4. **drill_blocks 12 個構造の親和性**: 学説対立論点を ○× で問う設計が憲法でも自然
5. **schema 拡張最小**: crime field 相当を「権利分類」「条文分類」に置換するだけで oneOf 構造は完全流用

#### 候補 Z: 形式 #6 待機

| 軸 | 評価 |
|---|---|
| 学習価値 | **ゼロ**（休止状態） |
| CI 安全性 | 高（何もしない） |
| テンプレ汎用性 | ゼロ（待機中なので適用機会なし） |
| 実装コスト | ゼロ |
| 着手敷居 | ゼロ |
| 撤退コスト | ゼロ |

**評価**: 何もしないので極めて低リスクだが、xnh の学習コンテンツも増えない。slotmap §5.10 §8 で確立した「形式 #6 入口で CI を実測し refactor 要否を判定する」設計は完成済みで、追加準備は不要。**新規 PDF が到着するまで自然休止する選択肢として残置**。

#### 3-way 総合比較

| 候補 | 学習価値 | CI 安全性 | 汎用性 | コスト | 敷居 | 総合 |
|---|---|---|---|---|---|---|
| X (§5.12+ cleanup) | 低 | 高 | 低 | 中 | 低 | △ |
| **Y (KEN 展開)** | **高** | 中 | **高** | 中-高 | 中 | **◎** |
| Z (形式 #6 待機) | ゼロ | 高 | ゼロ | ゼロ | ゼロ | △ |

#### 最終推奨

**候補 Y - 憲法 (KEN) 展開** を推奨する。

理由:

1. xnh の本来目的（予備試験対策コンテンツ整備）への寄与が最も大きい
2. 326-330 で確立した資産の活用率が最も高く、過去 6 セッションの投資が回収される
3. signature namespace が刑法と完全分離するため、CRIME_SIGNATURES 拡張も dict 追加のみで cleanup 不要
4. format / template / CI safety net をそのまま流用でき、新規実装コストは最小
5. 仮に途中で中断しても、完成済み問題は独立して valid

次セッション開始時のチェックリスト:

- [ ] `inputs/tx-pdfs/` 配下に憲法 PDF が存在するか確認
- [ ] 存在する場合: 問題番号と正答率を抽出して 5 問分の format 計画を立案 (slotmap §5.13 として書き起こし)
- [ ] 存在しない場合: xnh に PDF 投入を依頼 (推奨ファイル名: `inputs/tx-pdfs/KEN001.pdf` etc.)
- [ ] schema 拡張要否を検討: crime field 相当を `topic` field 等に汎用化するか、別 schema として分岐するか
- [ ] CRIME_SIGNATURES の科目別分割設計を提案: 例えば `signatures/criminal.py` `signatures/constitution.py` 等への分離

代替案 (候補 Z) を選ぶ場面:

- xnh が現時点で別科目展開に着手する時間的余裕がない場合
- 326-330 シリーズの実運用 (xnh による学習) で課題が顕在化するのを待ちたい場合

候補 X (§5.12+) は **不採用推奨**。理由は §5.11 で主要 cleanup 案件が決着済みで、追加 cleanup の限界効用が低いため。

---

## §6 subject namespace 仕様 — 刑法 (KEI) から 6 科目展開への汎化

### §6 §1 背景

§5.11 §13 末尾で「候補 Y - 憲法 (KEN) 展開」を次セッションの最優先候補と判定した後、xnh から 6 科目 (KEN/MIN/SYO/MINS/KEIS/GSE) の PDF (`inputs/tx-pdfs/` 直下に各 1 ファイル) を一括で投入する指示が出された。これにより、本プロジェクトは「刑法 326-330 シリーズ」段階から「7 科目横断 namespace」段階に移行する。

到達点と移行先の対比:

| 項目 | §5.11 完了時点 (刑法のみ) | §6 移行先 (7 科目) |
|---|---|---|
| 対応科目 | KEI のみ (326-330) | KEI + KEN/MIN/SYO/MINS/KEIS/GSE |
| problems/{id}.json 命名 | `326.json` 等 (数字のみ) | `KEN001.json` 等 (subject 接頭辞 + 数字) |
| 出力先 | `outputs/tx/刑TX/刑TX{id}.html` | `outputs/tx/{科目jp}TX/{科目jp}TX{id}.html` |
| signature 辞書 | `CRIME_SIGNATURES` (フラット dict) | `SIGNATURE_REGISTRY[subject]` (二段 dict) |
| schema | `crime` required、subject 概念なし | `subject` field 追加 (optional, default=KEI) |
| render.py | 数字引数のみ受付 | `326` / `KEN001` 両方を受付 |

326-330 シリーズが完成済みであり、HTML byte-identical を維持しながら他 6 科目を追加するため、改修は **加算的 (additive)** に行う。既存挙動は subject="KEI" のデフォルト経路として温存する。

### §6 §2 決定事項 (K-1 案 β 確定事項 + 一括処理規約)

K-1 設計合意 (案 β: subject パラメータ化 + 後方互換 default="KEI") を以下に本文化する:

**§6 §2.1 schema (`schema/problem.schema.json`)**

- `subject` field を `properties` に追加。enum `["KEI", "KEN", "MIN", "SYO", "MINS", "KEIS", "GSE"]`、`default: "KEI"`、required ではない (= 326-330 の既存 JSON で fail させない)。
- `id` field の pattern `^[0-9]{3}$` は不変。科目接頭辞は subject field 側で表現する。
- 他 field (`crime`, `instruction_type` etc.) は不変。`crime` field は刑法では罪名だが、他科目では論点 key (判例略称 / 学説名 / 条文番号系) として転用する。

**§6 §2.2 render.py (`scripts/render.py`)**

- `SUBJECT_TO_JP` dict を新設: `{"KEI": "刑", "KEN": "憲", "MIN": "民", "SYO": "商", "MINS": "民訴", "KEIS": "刑訴", "GSE": "行政"}`。
- `resolve_arg(arg)`:
  - 数字のみ ("326") → subject="KEI"、`problems/{id}.json` 経路 (legacy)。
  - `^([A-Z]+)(\d+)$` 形式 ("KEN001") → subject=接頭辞、`problems/{subject}{id}.json` 経路。
  - 不明な接頭辞は ValueError で停止 (CP6 自動補足対象)。
- JSON 内の `subject` field が CLI 推定と異なる場合、JSON 側を優先 (= JSON が source of truth)。
- 出力パス: `outputs/tx/{科目jp}TX/{科目jp}TX{id}.html`。KEI 経路は legacy `outputs/tx/刑TX/刑TX{id}.html` と一致する (CP4 担保)。

**§6 §2.3 validate_content.py (`scripts/validate_content.py`)**

- `SIGNATURE_REGISTRY: dict[str, dict[str, list[str]]]` を新設。第一段の key が subject、第二段が topic (罪名 / 判例略称 etc.)、値が signature 文字列のリスト。
- `SIGNATURE_REGISTRY["KEI"]` = §5.9 / §5.11 で確立済の 11 罪 entry をそのまま移植。
- `SIGNATURE_REGISTRY["KEN"|"MIN"|"SYO"|"MINS"|"KEIS"|"GSE"]` は空 dict で初期化。各 PDF 処理時に必要な signature を追加していく。
- 後方互換: `CRIME_SIGNATURES = SIGNATURE_REGISTRY["KEI"]` を alias として残す (外部 import / 旧テスト経路の温存)。
- `negative_check()` シグネチャ変更: `signatures_for_subject: dict[str, list[str]]` を引数で受け取る。呼出側 (`validate()`) で `problem.get("subject", "KEI")` をキーに dict を引いて渡す。

**§6 §2.4 一括処理規約 (1 PDF = 1 科目分多問題、1 ページ = 1 問題)**

- 入力命名: `inputs/tx-pdfs/{SUBJECT}.pdf` (例: `KEN.pdf`)。1 PDF = 1 科目分の複数問題、ページ数 = 問題数。
- 採番: 科目別 namespace で 001 から連番 (`KEN001`, `KEN002`, ...)。問題 id field は 3 桁ゼロ埋め文字列 (例: `"001"`)。
- ページ単位の独立性: PDF の N ページ目 = 問題番号 {SUBJECT}{N:03d}。ページ判別失敗時 (1 ページに複数問題 / 表紙ページ等) は **停止して報告** し、xnh 確認を待つ。
- 出力先: 上記 §6 §2.2 のマッピング表どおり。

### §6 §3 PDF 1 ページ = 1 問題の根拠と例外処理

#### §6 §3.1 根拠 (2026-05-19 訂正版、O-1 反映)

**当初前提の誤り**: 起案時は「1 PDF = 1 科目分の複数問題、1 ページ = 1 問題」を想定していたが、xnh が `inputs/tx-pdfs/` に投入した 6 PDF (Wondershare PDFelement で抽出された画像ベース PDF) は、実際には **「1 PDF = 1 問題、1 PDF は問題ページ + 解答+解説ページの組」** という構造であった (本セッション Phase C で全 13 ページを画像読解して確認、`docs/session-6subjects-expansion.md` § O-1 参照)。

**訂正後の運用**:

- 1 PDF = 1 問題。問題ページ (page-01) + 解答+解説ページ (page-02 以降) の組。
- 解説が複数ページにまたがる場合は page-03、page-04 ... を順次連結する (例: `KEIS.pdf` は 3 ページ = page-01 問題 / page-02-03 解答+解説)。
- 採番は 1 ファイル 1 問題で `{SUBJECT}001` 固定 (将来同科目で複数問題を投入する場合は `{SUBJECT}002` 以降に拡張)。

ページ数 / 問題数 / 採用形式の実測:

| PDF | ページ数 | 問題数 | 出題形式 | 採用 / 保留 |
|---|---|---|---|---|
| `KEN.pdf`  | 2 | 1 | fill-in (A-D 空欄 / 1-8 候補) | **保留** (未対応形式) |
| `MIN.pdf`  | 2 | 1 | combination-5 (ア-オ 5 記述 + 1-5 組合せ) | 採用 → `MIN001` |
| `SYO.pdf`  | 2 | 1 | combination-5 (ア-オ 5 記述 + 1-5 組合せ) | 採用 → `SYO001` |
| `MINS.pdf` | 2 | 1 | multi-select-5 (1-5 候補から「誤っているもの」を 2 個) | 採用 → `MINS001` |
| `KEIS.pdf` | 3 | 1 | fill-in (①-⑧ 空欄 / a-h 候補 + 1-5 組合せ) | **保留** (未対応形式) |
| `GSE.pdf`  | 2 | 1 | ox-grid-3 + combination-8 (ア-ウ ○× / 1-8 組合せ) | **保留** (未対応形式) |
| **合計** | **13** | **6** | — | 採用 3 / 保留 3 |

#### §6 §3.2 例外時の処理

以下のいずれかが発生した場合、自動処理を停止し、xnh 確認を待つ:

1. 1 ページに複数問題が含まれる (画像判読で 2 つ以上の「問題N」見出しが検出される)。
2. 表紙 / 目次 / 索引等の非問題ページが混在する。
3. ページ画像が判読不能 (解像度不足、文字欠落、レイアウト崩壊)。
4. 出題形式が未対応の 5 形式 (`ox-grid-5`, `ox-grid-4`, `multi-select-5`, `single-choice-5`, `combination-5`) のいずれにも該当しない。

これらが発生した時点で:

- 該当 PDF の処理を中断し、それ以前のページの成果物はそのまま確定する。
- 後続科目への自動遷移は行わない (CP6 違反扱い)。
- 報告サマリで停止理由とページ番号を明示し、xnh の判断を仰ぐ。

### §6 §4 signature 構築方針

#### §6 §4.1 全科目共通の方針

- **条文番号** を最強の signature として優先採用する (例: 刑法 246 条、憲法 21 条、民法 415 条)。罪 / 論点固有の数字は他 topic に偶発的に混入しにくい。
- **判例略称** (例: `最判昭48.4.25`, `最大判昭33.5.28`) を signature に組み込む。判例の年月日表記は他 topic で偶発的に出現する確率が極めて低い。
- **学説名 / 概念用語** で確実に topic 固有のもの (例: 「明白かつ現在の危険」「比例原則」) を補助 signature として追加する。
- **一般的すぎる語** (例: 「相当性」「合理性」) は混乱の元なので入れない。複数 topic で登場するため negative_check が誤検出を多発させる。

#### §6 §4.2 科目別の signature 集約方針

| 科目 | topic key の典型 | signature 主要源 |
|---|---|---|
| KEI (刑法) | 罪名 (詐欺罪、盗品等罪 etc.) | 条文番号、罪固有用語 (欺罔、贓物 etc.) |
| KEN (憲法) | 条文番号 / 判例名 (例: 21条、博多駅事件) | 条文番号、判例略称、概念用語 (明白かつ現在の危険 etc.) |
| MIN (民法) | 条文番号 (例: 415条、94条2項) | 条文番号、契約類型名、判例略称 |
| SYO (商法) | 条文番号 (例: 会社法 423条) | 条文番号、機関設計用語、商行為類型 |
| MINS (民事訴訟法) | 主義 / 論点 (例: 弁論主義、既判力) | 条文番号、主義名、判例略称 |
| KEIS (刑事訴訟法) | 論点 (例: 違法収集証拠) | 条文番号、判例略称、捜査段階の固有用語 |
| GSE (行政法) | 論点 (例: 取消訴訟、原告適格) | 条文番号、訴訟類型、判例略称 |

#### §6 §4.3 cross-subject 干渉の回避

「246条」は刑法詐欺罪、民事訴訟法 246 条 (処分権主義) と数字が衝突しうるが、`SIGNATURE_REGISTRY` を **科目で第一段を切る** ことで干渉を回避する。各 negative_check は subject 内の他 topic のみと照合するため、KEI の HTML に MINS の signature が誤って混入しても検出されない (= 検出する必要がない、内容混入ではないため)。これは設計上の妥協ではなく、「内容混入 = canonical 流用」を検出する目的に対して最小十分な機構である。

### §6 §5 §X 標準 5 項目記録 (実測値、Phase A-D 完了時 2026-05-19 記入)

#### §X.1 目的

刑法 326-330 シリーズ完成後に、xnh 指示に従って **6 科目 (KEN/MIN/SYO/MINS/KEIS/GSE) を展開** すること。各 PDF を読み解き、326-330 と同じ品質基準 (CP1-CP7) で完走させる。

#### §X.2 対象 (実測値、O-1 反映)

- `inputs/tx-pdfs/{SUBJECT}.pdf` (6 ファイル、合計 6 問題、1 PDF = 1 問題)
- 出力: `outputs/tx/{科目jp}TX/{科目jp}TX{NNN}.html`
- 検証: `scripts/validate_structure.py` + `scripts/validate_content.py` の二段 (CP6)

#### §X.3 変更点 (実測値)

- ✅ `schema/problem.schema.json`: `subject` field 追加 (enum 7 値、default=KEI、required 不変、§6 §2.1)
- ✅ `scripts/render.py`: `SUBJECT_TO_JP` / `resolve_arg` / `get_output_path` 追加、JSON `subject` field 優先ロジック (§6 §2.2)
- ✅ `scripts/validate_content.py`: `SIGNATURE_REGISTRY` 二段化、`CRIME_SIGNATURES` alias 維持、`negative_check` 引数化 (§6 §2.3)
- ✅ `scripts/pdf_to_png.py` (新規): 画像ベース PDF を Claude image understanding に渡すための補助スクリプト (pymupdf 依存)
- ✅ `problems/MIN001.json` / `problems/SYO001.json` / `problems/MINS001.json` 新規追加 (3 ファイル)
- ✅ `outputs/tx/民TX/民TX001.html` / `outputs/tx/商TX/商TX001.html` / `outputs/tx/民訴TX/民訴TX001.html` 新規生成 (3 HTML)
- 🟡 `SIGNATURE_REGISTRY`: 各科目 entry の追加件数は以下のとおり

| Subject | entry 件数 (本セッション後) | 追加理由 |
|---|---|---|
| KEI  | 11 | §5.11 既存 (不変、CP4 担保) |
| MIN  | 0  | 単一問題のため cross-topic 干渉なし、signature 不要 |
| SYO  | 0  | 同上 |
| MINS | 0  | 同上 |
| KEN  | 0  | Phase C で保留、未処理 |
| KEIS | 0  | 同上 |
| GSE  | 0  | 同上 |

#### §X.4 検証 (実測値)

- ✅ CP1 通過 (schema 変更が subject field 追加のみ)
- ✅ CP2 通過 (render.py 既存ロジック不変、326-330 経路に regression なし)
- ✅ CP3 通過 (validate_content.py の旧 API `CRIME_SIGNATURES` alias 維持)
- ✅ CP4 通過 (326-330 SHA256 byte-identical 維持、3 回照合済 = Phase A/B/D)
- ✅ CP5 通過 (check_template_sync.py exit 0、slotmap §6 追記後も維持)
- ✅ CP6 通過 (MIN001 / SYO001 / MINS001 で render + validate_structure + validate_content 全 PASS、各 WARN [S26] のみ非致命)
- ✅ CP7 通過 (本 §6 が slotmap 本文化、訂正版 §6 §3.1 で O-1 反映済)

#### §X.5 次の作業

- 保留 3 問題: `KEN.pdf` (fill-in)、`KEIS.pdf` (fill-in + combination-5)、`GSE.pdf` (ox-grid-3 + combination-8)
- **(b) refactor 発火条件充足**: 既存 5 形式で収まらない問題が 3 件 confirmed (fill-in × 2 / ox-grid-3 + combination-8 × 1)。次セッションで「一般化リファクタ vs 6-7-8 本目テンプレ追加」の方針判断を要する
- 詳細は `docs/session-6subjects-expansion.md` § (b) refactor 発火判定 参照
- 2026-05-19 後続: xnh が **選択肢 X (6→7 本目 template 追加)** を採択。§6.6 (fill-in) と §6.7 (ox-grid-3 + combination-8) を本文化し、7 本立て移行を実行する (slotmap §6.6 / §6.7 参照)

---

## §6.6 6 本目 template — fill-in 形式 (KEN/KEIS 対応)

### §6.6 §1 目的

KEN.pdf / KEIS.pdf で確認された **fill-in 形式** (空欄 + 候補マッチング) を表現する 6 本目テンプレ `KTX_template_fillin.html` を新設する。既存 5 本テンプレでは表現できない「N 個の空欄 × M 個の候補」の 2 軸対応関係を扱う。

対象 PDF:
- `KEN.pdf` (憲法 H19-1、法の支配): A〜D の 4 空欄 / 1〜8 の 8 候補
- `KEIS.pdf` (刑事訴訟法 H18-21、刑事訴訟法の基本構造): ①〜⑧ の 8 空欄 / a〜h の 8 候補 + 1〜5 の組合せ選択肢

両者を共通テンプレでカバーするため、**空欄数 N と候補数 M を slot で可変化**する設計を採る。KEIS の組合せ選択肢部分は本 6 本目では扱わず、空欄充填の正誤判定を直接的に表現することで吸収する (KEIS については §6.6 §3.2 参照)。

### §6.6 §2 設計の核心

#### §6.6 §2.1 base template の選定

- **base**: `KTX_template_msel5.html` (multi-select-5)
- **理由**: multi-select-5 は「複数の選択を一括判定」する UI であり、fill-in の「複数空欄を一括判定」と構造的に最も近い
- **CP1 担保**: 同期義務セクション (head / css / body_pre_toc / marker_legend / part_c_d / footer_spec / js) は msel5 から byte-identical コピー。check_template_sync.py の sync_required 検査が通過することで担保される

#### §6.6 §2.2 diff-allowed セクションの設計

| section | 設計 |
|---|---|
| `toc` | A〜D / E〜H 等、空欄ラベルを動的化。`{{BLANK_A_LABEL}}〜{{BLANK_H_LABEL}}` の 8 slot を用意し、未使用 slot は空文字で埋める (msel5 の 1-5 + 拡張枠の発想を踏襲) |
| `pre_part_a` | `<!-- PART A: fill-in -->` 専用見出しコメント |
| `part_a` | 問題本文 (空欄を `<span class="blank" data-blank="A">[ A ]</span>` 等で表現) + 候補リスト `<ol class="fillin-candidates">` (1〜8 / a〜h を slot で動的化) |
| `a2` | 空欄ごとの解答入力エリア。`<button class="answer-slot" data-blank="A" data-correct-value="{{BLANK_A_CORRECT}}">` の 8 セット (未使用は visibility:none) |
| `part_b` | 空欄ごとの解説 section。`<section class="choice-section" data-blank="A">` 構造で 8 セット (既存 part_b の choice-section 構造を踏襲、ただし label を「空欄 A」等に置換) |
| `basis` | 共通根拠 (空欄横断の判例引用 / 学説対立) |

#### §6.6 §2.3 schema 拡張

`schema/problem.schema.json`:

- `instruction_type` enum に `"fill-in"` 追加
- `$defs/Blank` 追加: `{label: "A"〜"H", correct_candidate: "1"〜"8" or "a"〜"h", explanation: string}`
- `$defs/Candidate` 追加: `{num: "1"〜"8" or "a"〜"h", text: string}`
- properties に `blanks: array[Blank]` (1〜8 件) と `candidates: array[Candidate]` (1〜8 件) を追加
- `answer` の oneOf に `object` 型 (`{"A": "5", "B": "7", "C": "3", "D": "6"}` 等の空欄→候補マップ) を追加
- 既存 KEI / MIN / SYO / MINS の JSON は影響を受けない (enum 追加のみ、required 不変)

#### §6.6 §2.4 render.py 拡張

- `TEMPLATE_PATHS` に `"fill-in": KTX_template_fillin.html` 追加
- `build_slot_dict()` に fill-in 用 slot 構築ロジック追加:
  - `{{BLANK_A_LABEL}}〜{{BLANK_H_LABEL}}`, `{{BLANK_A_CORRECT}}〜{{BLANK_H_CORRECT}}`, `{{BLANK_A_EXPLANATION}}〜{{BLANK_H_EXPLANATION}}`
  - `{{CANDIDATE_1_TEXT}}〜{{CANDIDATE_8_TEXT}}` (or a-h)
  - 未使用 slot は空文字で埋める (msel5 の「固定枠 + 空文字 fill」パターンを踏襲、CP2 regression リスクを避ける)
- `_format_answer()` に dict 形式 (`{"A": "5", "B": "7"}` → `"A=5,B=7,C=3,D=6"`) を追加

#### §6.6 §2.5 check_template_sync.py 拡張

- `TEMPLATE_FILES` に `"KTX_template_fillin.html"` 追加 (6 番目)
- `INTENTIONAL_DIFFS` の note 文字列に fill-in を追記 (内容は変更不要)
- ペア数は C(6,2) = 15 ペアに増加 (timing は情報報告のみなので動作影響なし)

#### §6.6 §2.6 validate_structure.py 拡張

- `S26` の ○×比率検査は fill-in には適用しない (drill_blocks の存在 / 不在で分岐)
- `instruction_type == "fill-in"` 経路を追加し、blanks / candidates の存在確認 S 規則を追加 (S78 系)
- 既存 S 規則は ox-grid / multi-select / single-choice / combination 経路で温存

### §6.6 §3 想定リスク R1〜R5

#### R1: KEIS の組合せ選択肢吸収

- KEIS は ①〜⑧ の空欄を a〜h から選択した上で、その組合せが 1〜5 のいずれかに該当する形式 (二段選択)。本 6 本目テンプレでは「空欄→候補」の 1 段までしか表現しない
- **対応**: KEIS の正解 (例: `{"①": "i", "④": "d", "⑥": "h", "⑧": "d"}`) を直接 answer dict で扱い、1〜5 の組合せ選択肢部分は問題本文 (instruction) 内に文字列として埋め込み、UI 上の選択を要求しない。学習者は各空欄を埋めれば自然に正解組合せに到達する設計
- KEIS 用に専用 instruction_type を切るか議論があったが、Phase X-A 時点では fill-in 1 種で吸収する。実装段階で UI 表現が不自然となる場合、`fill-in-combination` 等の派生型を §6.6b として追加検討

#### R2: 候補数の可変性 (4 / 8 / etc.)

- KEN: 候補 8 / 空欄 4
- KEIS: 候補 8 / 空欄 8
- **対応**: 候補と空欄を独立に「最大 8 件、未使用は空文字 fill」で扱う。JSON 側で blanks / candidates 配列の長さで実数を表現

#### R3: AP-37 抵触リスク

- fill-in の各空欄解説 (drill_blocks 相当) で、正解候補番号 (例: 「A=5 なので…」) を professor/drill 文言に含めないよう、`{{BLANK_*_EXPLANATION}}` の内容を慎重に設計する
- 326-330 シリーズで確立された「番号は本文に直接書かず、論理を説明する」原則を適用

#### R4: drill_blocks の整合性

- 既存 KEI/MIN/SYO/MINS の drill_blocks は 12 件固定。fill-in でも 12 件保持するか、空欄数 (4 or 8) と整合させて 4 or 8 件にするか
- **対応**: 12 件固定維持を推奨。空欄横断のテーマ別に 12 件 (例: 法の支配の本質 / 各空欄の候補対応 / 関連判例 / 横断) で構成する。これにより既存 PART D Rapid-Fire UI を流用可能

#### R5: 7 本目との競合

- §6.7 で扱う ox-grid-3 + combination-8 とほぼ並行で実装するため、互いの schema / render 改修が衝突しないよう順序を守る
- **対応**: §6.6 (fill-in) 先 → §6.7 (ox3comb8) 後の順序で実装。各 phase 完了時に CP1-CP5 中間検証を入れ、回帰を即検出する

---

## §6.6b 8 本目 template — fillin8 形式 (KEIS 対応、N=8 blanks + 5 options)

### §6.6b §1 背景

§6.6 で確立した fill-in 形式 (5 blanks A-E、答案=空欄ごとに候補番号 dict) は KEN (4 blanks) を吸収できたが、KEIS の **8 blanks** には N=5 制限のため対応できないことが Phase X-B で判明。本 §6.6b は、KEIS の本質的形式を改めて分析した結果に基づき、新 8 本目テンプレ `KTX_template_fillin8.html` を新設する。

### §6.6b §2 KEIS の本質的形式 (再分析)

#### §6.6b §2.1 PDF 再精読の結論

`KEIS.pdf` (3 ページ、page-01 問題、page-02-03 解答) の構造を再精読した結果、当初想定した「単純 fill-in N=8」とは異なる **fill-in 表示 + 単一選択** ハイブリッド形式であることが判明:

- **8 blanks** (①〜⑧) は問題文中の参照点 (表示のみ、ユーザーは直接埋めない)
- **候補リスト** (a〜i、9 候補): blanks 候補語句の一覧
- **5 選択肢 1〜5**: 各が 2 つの blank-candidate 主張 (例: 肢1 = 「①i・④d」 = 「①=職権、④=当事者」)
- **答え**: 5 肢の中から正しい組合せを 1 つ選ぶ (= single-choice 機構)

つまり、ユーザーの操作上は **single-choice (1〜5)** であり、blanks ①〜⑧ は問題理解のための表示要素にすぎない。これは KEN001 の「fill-in 機構 (4 空欄を直接埋める)」とは根本的に異なる。

#### §6.6b §2.2 既存テンプレからの再選定

| 候補 base | 適合性 | 採否 |
|---|---|---|
| `KTX_template_fillin.html` (§6.6 6 本目) | 答案機構が空欄直接埋めで KEIS と相違 | 不適 |
| `KTX_template_comb5.html` (5 本目) | answer-slots 1-5 (single-choice) と一致、5 choice-sections も options 1-5 にそのまま流用可能 | **採用** |
| `KTX_template_sc5.html` (4 本目) | single-choice-5 だが【見解】section 構造が KEIS と異なる | 不適 |

**結論**: 8 本目 `KTX_template_fillin8.html` は **comb5 派生** とする。`fillin` の派生にはしない (機構が異なるため)。

### §6.6b §3 設計の核心

#### §6.6b §3.1 base template と差分許容セクション設計

- **base**: `KTX_template_comb5.html`
- **CP1 担保**: 同期義務セクション (head / css / body_pre_toc / marker_legend / part_c_d / footer_spec / js) は comb5 から byte-identical コピー

差分許容セクション:

| section | 設計 |
|---|---|
| `toc` | ア〜オ 系統は使わず、肢 1〜5 + 共通根拠等のリンク (msel5 系統に近い) |
| `pre_part_a` | `<!-- PART A: fillin8 (8 blanks + 5 options) -->` 専用見出しコメント |
| `part_a` | 問題本文 (① 〜 ⑧ を embed) + 候補一覧 (a〜i) + 5 選択肢の表示。【記述】section は省略 (5 records ア-オ は KEIS にない)、代わりに【候補】section を新設 |
| `a2` | comb5 と同じ単一選択 (1〜5)、`data-correct-value="{{ANSWER}}"`、`data-answer-type="single"` |
| `part_b` | 5 choice-sections (肢 1〜5 の解説)。各肢の stem は「①i・④d」のような主張文 |
| `basis` | comb5 と同じ最小構造、sec-nav back-link を肢5 に |

#### §6.6b §3.2 schema 拡張

- `instruction_type` enum に `"fillin8"` 追加
- `combinations` の構造は流用しない (KEIS の選択肢は ア-オ の組合せではないため)
- choices: 5 items (label "1"-"5"、各オプションの主張を stem に)
- answer: 既存 single-choice の integer 1-5 と整合

#### §6.6b §3.3 render.py 拡張

- `TEMPLATE_PATHS` に `"fillin8": KTX_template_fillin8.html` 追加
- 既存 slot (CHOICE_A-E_* + COMBO_1-5_*) を流用可能 (msel5 系統と同じパターン)
- 新 slot は不要 (8 blanks と candidates は instruction 内に embed)

#### §6.6b §3.4 check_template_sync.py 拡張

- `TEMPLATE_FILES` に `"KTX_template_fillin8.html"` 追加 (8 本目)
- ペア数 C(8,2) = 28 ペアに増加 (timing 計測のみ影響、PASS/FAIL 判定には影響なし)

#### §6.6b §3.5 validate_structure.py 拡張

- KEIS は data-answer-type="single" を採用するため、`_derive_cv_info` の既存 'single' mode で吸収
- N=5 (choice-sections) で既存 single ロジックがそのまま使える
- 新規 S 規則は **追加不要** (← §6.6 / §6.7 と異なり、validate_structure はほぼ無改修で済む)

### §6.6b §4 想定リスク R1〜R3

#### R1: 8 blanks の表示崩れ

- 問題文中の ①〜⑧ マーカーが文字列として埋め込まれるが、UI 上の視覚強調 (背景色、太字等) は instruction 内の HTML タグで表現する必要あり
- **対応**: `<span class="blank-marker">①</span>` 等を instruction に直接埋め込み、CSS は同期義務領域 (=既存定義) に依存する。新規 CSS は導入しない

#### R2: 候補リスト (a-i = 9 candidates) の schema 表現

- 当初想定の `candidates` フィールドは導入しない (instruction text に embed する方針)
- これにより schema 変更を最小化 (instruction_type の enum 追加のみ)

#### R3: AP-37 抵触リスク

- 「正解は肢1」を professor/drill 文言に書かない、「①=i, ④=d」を明示的に表現するときは慎重に
- KEN001 と同じ原則を適用

### §6.6b §X 標準 5 項目記録 (Phase Z 完了時実測、2026-05-19 記入)

#### §X.1 目的

KEIS の fillin8 形式 (8 blanks 表示 + 5 options 単一選択) を 8 本目 template で完走させ、累計 11 件完走 (KEI 5 + MIN/SYO/MINS 3 + KEN/GSE 2 + KEIS 1) を達成。**全 13 想定問題のうち未処理ゼロ、6 PDF 完全消化、7 科目 (KEI/KEN/MIN/SYO/MINS/KEIS/GSE) すべてに 1 件以上の運用実績**。

#### §X.2 対象 (実測値)

- ✅ 新規 template: `templates/KTX_template_fillin8.html` (101,981 chars / 2,907 lines、comb5 base)
- ✅ 新規 problem: `problems/KEIS001.json`
- ✅ 新規 output: `outputs/tx/刑訴TX/刑訴TX001.html` (102,755 bytes)
- 既存資産 (CP1-CP4 保護対象): templates 7 本 / 326-330 / MIN001 / SYO001 / MINS001 / KEN001 / GSE001

#### §X.3 変更点 (実測値)

- ✅ `templates/KTX_template_fillin8.html` 新規 (build_fillin8_template.py で comb5 から生成、同期義務セクション byte-identical 担保)
- ✅ `scripts/build_fillin8_template.py` 新規 (template 生成補助)
- ✅ `scripts/check_template_sync.py`: TEMPLATE_FILES に追加、8 本立て対応
- ✅ `scripts/render.py`: TEMPLATE_PATHS に "fillin8" 追加 (1 行のみ)
- ✅ `schema/problem.schema.json`: instruction_type enum に "fillin8" 追加 (1 行のみ)
- ✅ **validate_structure.py / validate_content.py は無改修** (fillin8 は data-answer-type="single" を流用するため、既存ロジックがそのまま機能)

#### §X.4 検証 (実測値)

- ✅ CP1 既存 5 本 template (326-330 専用) SHA256 不変
- ✅ CP2 326-330 byte-identical (再 render 後も一致)
- ✅ CP3 MIN001/SYO001/MINS001 byte-identical (再 render 後も一致)
- ✅ CP4 KEN001/GSE001 byte-identical (再 render 後も一致)
- ✅ CP5 check_template_sync.py 8 本立てで exit 0
- ✅ CP6 KEIS001 validate_structure exit 0 (WARN [S26] のみ非致命) / validate_content PASS
- ✅ CP7 §6.6b 本文化済 (本セクション)

#### §X.5 次の作業

- ✅ Phase Z 完走、KEIS001 で **累計 11 件完走 + 全 13 想定問題消化** に到達
- 次セッション以降: 既存問題の追加 (KEI 331+、各科目 N=2 件目以降)、または別科目の本格展開
- (b) refactor の再評価は 8 本立て到達で完了 — 当面はテンプレ追加路線で運用継続が妥当

---

### §6.6 §X 標準 5 項目記録 (Phase X-B 完了時実測、2026-05-19 記入)

#### §X.1 目的 (実測値)

KEN の fill-in 形式を 6 本目 template `KTX_template_fillin.html` で完走させること。**KEIS は 8 blanks を要するため本セッションでは保留**し、§6.6b として N=8 拡張テンプレを次セッションで設計する方針に切り替えた (slotmap §6.6 §3 R1 の代替案発動)。

#### §X.2 対象

- ✅ 新規 template: `templates/KTX_template_fillin.html` (101,984 chars / 2,908 lines、msel5 base)
- ✅ 新規 problem: `problems/KEN001.json`
- ✅ 新規 output: `outputs/tx/憲TX/憲TX001.html` (103,081 bytes)
- 🟡 保留: `problems/KEIS001.json` / `outputs/tx/刑訴TX/刑訴TX001.html` (8 blanks のため §6.6b 待ち)
- 既存資産 (CP1-CP3 保護対象): templates 5 本 / 326-330 / MIN001 / SYO001 / MINS001

#### §X.3 変更点 (実測値)

- ✅ `templates/KTX_template_fillin.html` 新規 (build_fillin_template.py で msel5 から生成、同期義務セクション byte-identical 担保)
- ✅ `scripts/build_fillin_template.py` 新規 (template 生成補助)
- ✅ `scripts/check_template_sync.py`: TEMPLATE_FILES に追加、表示文言 "all N match" 動的化、INTENTIONAL_DIFFS note 更新
- ✅ `scripts/render.py`: TEMPLATE_PATHS に "fill-in" 追加、_format_answer に dict 対応、CHOICE_A〜E slot 事前 fill、LABEL_TO_LETTER に A-E 追加
- ✅ `scripts/validate_content.py`: positive_check の answer 値を dict 対応
- ✅ `scripts/validate_structure.py`: _derive_cv_info に fill-in mode 追加、check_S73 で fill-in 判定追加
- ✅ `schema/problem.schema.json`: instruction_type enum に "fill-in" 追加、answer oneOf に object 追加、Choice.label enum に A-E 追加

#### §X.4 検証 (実測値)

- ✅ CP1 既存 5 本 template SHA256 不変 (3 回照合一致)
- ✅ CP2 326-330 byte-identical (再 render 後も一致)
- ✅ CP3 MIN001/SYO001/MINS001 byte-identical (再 render 後も一致)
- ✅ CP4 check_template_sync.py 6 本立てで exit 0
- ✅ CP5 INTENTIONAL_DIFFS に fill-in 登録済 (note 更新)
- ✅ CP6 KEN001 validate_structure exit 0 (WARN [S26]/[S71] のみ非致命) / validate_content PASS
- ✅ CP7 §6.6 本文化済 (本セクション)

#### §X.5 次の作業

- 保留 KEIS001 (8 blanks): §6.6b (N=8 fillin8 template) を次セッションで設計
- Phase X-C (7 本目 ox-grid-3+combination-8) は本セッション内で完走 (slotmap §6.7 参照)

---

## §6.7 7 本目 template — ox-grid-3 + combination-8 形式 (GSE 対応)

### §6.7 §1 目的

GSE.pdf で確認された **ox-grid-3 + combination-8 形式** (3 記述 ○× + 8 組合せ選択) を表現する 7 本目テンプレ `KTX_template_ox3comb8.html` を新設する。既存 ox-grid-4/-5 は記述数 N=4,5 固定、combination-5 は組合せ数 5 固定で、いずれも N=3 + 組合せ 8 には対応できない。

対象 PDF:
- `GSE.pdf` (行政法 R4-13、行政法の法源): ア〜ウ の 3 記述に ○× を付し、2^3 = 8 通りの組合せ (1〜8) から正解を 1 つ選ぶ

### §6.7 §2 設計の核心

#### §6.7 §2.1 base template の選定

- **base**: `KTX_template_comb5.html` (combination-5)
- **理由**: combination-5 は「記述 + 組合せ選択」の 2 段構造を持ち、ox-grid-3 + combination-8 と構造的に最も近い。組合せ数のみ 5 → 8 に拡張、記述数 5 → 3 に縮小すれば吸収可能
- **CP1 担保**: 同期義務セクションは comb5 から byte-identical コピー

#### §6.7 §2.2 diff-allowed セクションの設計

| section | 設計 |
|---|---|
| `toc` | ア〜ウ の 3 ラベル + 1〜8 の 8 組合せラベル。msel5/comb5 の「ラベル 5 件」パターンを N=3, N=8 に派生 |
| `pre_part_a` | `<!-- PART A: ox-grid-3 + combination-8 -->` 専用見出しコメント |
| `part_a` | ア〜ウ の 3 記述リスト + 1〜8 の 8 組合せ表示。combination-5 の 5 組合せ section を 8 件に拡張 (`{{COMBO_1}}〜{{COMBO_8}}`) |
| `a2` | 3 行 ox-grid (`{{OX_AR_*}}〜{{OX_W_*}}`) + 1〜8 の答え選択ボタン |
| `part_b` | 3 choice-section (ア / イ / ウ、既存 ox4 / comb5 の choice-section を 3 件版で再構成) |
| `basis` | 共通根拠 (3 記述横断の判例引用) |

#### §6.7 §2.3 schema 拡張

- `instruction_type` enum に `"ox-grid-3-combination-8"` 追加 (派生 - で区切る命名)
- `choices` minItems を `3` まで緩和 (現状 4)
- `combinations` minItems / maxItems を `5` 固定 → `5-8` 範囲に拡張
- `combinations.set.maxItems` を `5` 固定 → `8` に拡張 (記述ラベルが 8 通り組合せに使われる可能性)
- ただし `combinations.set.items.enum` は `["ア", "イ", "ウ", "エ", "オ"]` のままで OK (GSE はア-ウ のみ使用)

#### §6.7 §2.4 render.py 拡張

- `TEMPLATE_PATHS` に `"ox-grid-3-combination-8": KTX_template_ox3comb8.html` 追加
- `build_slot_dict()` 拡張:
  - `combinations` slot を 5 → 8 件に拡張: `{{COMBO_1_LABEL}}〜{{COMBO_8_LABEL}}`, `{{COMBO_1_SET}}〜{{COMBO_8_SET}}`
  - 既存 comb5 では 5 件まで埋められ、6-8 番目は空文字。新形式では 6-8 も埋まる
- ox-grid 部は既存 ox4 の choice slot (`{{CHOICE_A_*}}〜{{CHOICE_C_*}}`) を流用 (ア=A, イ=B, ウ=C)。`{{CHOICE_D_*}}` / `{{CHOICE_E_*}}` は空文字

#### §6.7 §2.5 check_template_sync.py 拡張

- `TEMPLATE_FILES` に `"KTX_template_ox3comb8.html"` 追加 (7 番目)
- `INTENTIONAL_DIFFS` の note を更新
- ペア数は C(7,2) = 21 ペアに増加

#### §6.7 §2.6 validate_structure.py 拡張

- choice 件数のレンジ検査を N≥3 に緩和 (現行 N≥4)
- combination 件数のレンジ検査を 5-8 に拡張
- ○×比率検査は記述数依存にスケール (3 件なら 1.5:1.5 期待値)

### §6.7 §3 想定リスク R1〜R5

#### R1: 既存 KEI 330 (combination-5) への影響

- combinations 件数のレンジ拡張は schema 変更だが、既存 330.json の combinations 5 件はレンジ内なので影響なし
- **対応**: schema 変更後、326-330 を全件再 render → SHA256 照合で CP2 担保

#### R2: ox-grid-3 の N=3 への validate 緩和

- 既存 ox4 / ox-grid-5 は choices 4-5 件を前提に S 規則を組んでいる
- **対応**: `instruction_type == "ox-grid-3-combination-8"` 経路を別 S 規則として追加し、既存経路は不変

#### R3: 8 組合せの UI 表示

- 5 組合せが表示できる現行 UI を 8 件に拡張する際、画面密度の見た目調整が必要かもしれない
- **対応**: CSS は同期義務セクションなので変更不可。代わりに `part_a` の class / id を新規追加し、ox3comb8 専用 CSS 適用は **新 template 内の inline style** で完結させる (CSS section の sync 担保を優先)

#### R4: AP-37 抵触リスク

- 8 組合せの選択肢で「正解番号」が drill / professor / explanation に直接含まれないよう設計
- 326-330 で確立された原則を遵守

#### R5: 命名規約

- `ox-grid-3-combination-8` は冗長だが、形式の本質を明示する優先で採用。略称が必要になった場合は `ox3comb8` を補助名として用意

### §6.7 §X 標準 5 項目記録 (Phase X-C 完了時実測、2026-05-19 記入)

#### §X.1 目的

GSE の ox-grid-3 + combination-8 形式を 7 本目 template で完走させ、累計 10 件完走 (5 KEI + 3 MIN/SYO/MINS + 1 KEN + 1 GSE) を達成。KEIS は §6.6b に繰越のため 11 件には到達せず、本セッションは 10 件完走で公式 close。

#### §X.2 対象

- ✅ 新規 template: `templates/KTX_template_ox3comb8.html` (101,501 chars / 2,877 lines、comb5 base)
- ✅ 新規 problem: `problems/GSE001.json`
- ✅ 新規 output: `outputs/tx/行政TX/行政TX001.html` (102,594 bytes)
- 既存資産 (CP1-CP3 保護対象): templates 6 本 (Phase X-B 完了時点 5+1) / 326-330 / MIN001 / SYO001 / MINS001 / KEN001

#### §X.3 変更点 (実測値)

- ✅ `templates/KTX_template_ox3comb8.html` 新規 (build_ox3comb8_template.py で comb5 から生成、同期義務セクション byte-identical 担保)
- ✅ `scripts/build_ox3comb8_template.py` 新規 (template 生成補助)
- ✅ `scripts/check_template_sync.py`: TEMPLATE_FILES に追加、INTENTIONAL_DIFFS note 更新
- ✅ `scripts/render.py`: TEMPLATE_PATHS に "ox-grid-3-combination-8" 追加、combinations slot を 1〜5 → 1〜8 に拡張
- ✅ `scripts/validate_structure.py`: _derive_cv_info に ox3comb8 mode 追加、check_S73 で ox3comb8 判定追加、S79 を mode 別に分岐 (5 → 8 件)
- ✅ `schema/problem.schema.json`: instruction_type enum に "ox-grid-3-combination-8" 追加、combinations maxItems 5 → 8、Combination.label enum 拡張 1-8

#### §X.4 検証 (実測値)

- ✅ CP1 既存 6 本 template SHA256 不変 (Phase X-B 後の baseline と一致、再 render 後も一致)
- ✅ CP2 326-330 byte-identical
- ✅ CP3 MIN001/SYO001/MINS001/KEN001 byte-identical (KEIS001 は未生成のため除外)
- ✅ CP4 check_template_sync.py 7 本立てで exit 0
- ✅ CP5 INTENTIONAL_DIFFS に ox3comb8 登録済 (note 更新)
- ✅ CP6 GSE001 validate_structure exit 0 (WARN [S26] のみ非致命) / validate_content PASS
- ✅ CP7 §6.7 本文化済 (本セクション)

#### §X.5 次の作業

- Phase X-D/E (本セッション内で完走): 最終 CP / docs/session-6subjects-complete.md
- 次セッション: §6.6b (fillin8、KEIS 用) を設計合意してから KEIS001 完走

---
