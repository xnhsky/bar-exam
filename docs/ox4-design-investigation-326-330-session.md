# ox-grid-4 形式対応 — 設計調査記録

## メタ情報

- **作成日**: 2026-05-18
- **対象セッション**: 326〜330 一括処理セッション
- **セッション概要**:
  - 326 (ox-grid-5、盗品等罪、H29-12) を 3 段検証パイプライン (render → validate_structure → validate_content) で完走させた。
  - その過程で S13 (PART C c-2〜c-6 欠落) と S16 (answer-area の data-explanation 欠落) を template 最小修正で解消し、さらに S16 を schema 経由の本格対応 (answer_explanation フィールド追加、required 化、template/render.py への slot 化) に格上げした。
  - 327, 328, 329, 330 は形式判定の結果、いずれも ox-grid-5 ではなかったため (327: アからエの 4 択 ○×、328: 1〜5 から 2 個選ぶ multi-select、329: 1〜5 から 1 個選ぶ single-choice、330: ア〜オの組合せ型 single-choice) skip した。
  - skip した 327 の形式 (ox-grid-4: アからエの 4 択 ○× 判定) に本格対応するための設計調査を実施。
- **次セッションでのアクション**:
  1. 本書の §D に記載した slotmap.md §5.1 追記案文を `templates/KTX_template_slotmap.md` に追加し、合意を得る。
  2. 合意後、§E の Step 1〜9 に従って schema / validate_structure / template / render / slotmap / 327.json の順に実装する。
  3. 各 Step の検証ポイントを満たしてから次 Step に進む。Step 8 (326 regression 検証) を必ず実施する。
- **本書のスコープ**: 調査と提案のみ。実装コード変更は含まない。

---

## A. 327.pdf の構造サマリ (326 との diff 形式・全項目)

| 項目 | 326 (ox-grid-5) | 327 (ox-grid-4 候補) | 差分の性質 |
|---|---|---|---|
| **問題 ID** | 326 | 327 | 連番 |
| **PDF ファイル** | `inputs/tx-pdfs/326.pdf` (423,783 B) | `inputs/tx-pdfs/327.pdf` (338,909 B) | — |
| **出題形式 (実体)** | アからオまでの 5 択 ○× 判定 | **アからエまでの 4 択 ○× 判定** | **選択肢数 -1** |
| **`instruction_type` 必要値** | `"ox-grid-5"` | `"ox-grid-4"` (**現 schema enum に未存在**) | **新 enum 値が必要** |
| **設問導入文** | 「次のアからオまでの各記述を判例の立場に従って検討し、正しい場合には1を、誤っている場合には2を選びなさい。」 | 「盗品等に関する罪についての次のアからエまでの各記述を判例の立場に従って検討し、正しい場合には1を、誤っている場合には2を選びなさい。」 | **「アからオ」→「アからエ」**、冒頭に「盗品等に関する罪についての」が付くが構造的差ではなく文言バリエーション |
| **`instruction` 文長** | 約 60 字 | 約 75 字 | minLength 10 を共に充足 |
| **判定方式** | 各選択肢で 1=正しい / 2=誤っている | 各選択肢で 1=正しい / 2=誤っている | **完全に同型** |
| **正答列 (answer)** | `"12222"` (5 桁) | `"2212"` (**4 桁**) | **桁数 -1**。pattern `^[12]+$` は両者を許容済 |
| **正解の verdict 内訳** | ア=1 / イ=2 / ウ=2 / エ=2 / オ=2 | ア=2 / イ=2 / ウ=1 / エ=2 | — |
| **配点 (points)** | 4 | 3 | -1 |
| **正答率 (correct_rate)** | 47% | **37%** | -10pt |
| **override_pattern (自動判定)** | P2 (40–60% 帯、セージブラリー) | **P3** (< 40% 帯、ラベンダードーン) | パターン差 |
| **出典 (source)** | `H29-12` (司法試験 平成29年第12問) | `予備R2-10` (**予備独自問題** 令和2年第10問) | source 文字列規約は同等 |
| **PDF 上の出典バナー表示** | `H29-12` | `予備独自問題 R2-10` | 「予備独自問題」の冠詞付き |
| **crime (CRIME_SIGNATURES キー)** | `"盗品等罪"` | `"盗品等罪"` (同一キーに統一推奨) | **同** (PDF タイトル表記は「盗品等に関する罪」と揺れあり) |
| **PDF タイトル表記** | `盗品等罪` | `盗品等に関する罪` | 表記揺れ。HTML 出力ではどちらに寄せるかは設計判断 |
| **章 (chapter)** | 第4章 財産に対する罪 | 第4章 財産に対する罪 | **同** |
| **節 (section)** | 第8節 盗品等に関する罪 | 第8節 盗品等に関する罪 | **同** |
| **ページ (page)** | 845 | 847 | +2 |
| **解説 explanation の構造** | 「判例名 → 判旨抜粋 → 当てはめ」 | 「判例名 → 判旨抜粋 → 当てはめ」 | **同型** |
| **解説中の判例引用例** | 最判昭24.10.20 (百選Ⅱ77事件) ／最判昭25.3.24／大判明44.12.18／最決昭38.11.8 | 最決昭34.2.9／大判明42.4.15／民法192条／同193条／256条1項／257条1項 等 | 引用判例は別。case_citations 配列の使い方は同型 |
| **「★」マーク等の特殊記号** | なし | ウの verdict 行に「★」あり (おそらく「判例必須」マーク) | 327 のみ。schema には未対応フィールド、無視可 |
| **HTML 上の choice-section 数** | 5 (choice-1〜choice-5) | **4** (choice-1〜choice-4) | -1 |
| **HTML 上の ox-row 数** | 5 | **4** | -1 |
| **HTML 上の PART A problem-text 行数** | 5 | **4** | -1 |
| **HTML 上の TOC アンカー数 (ア〜オ)** | 5 | **4** | -1 |
| **PART C / PART D / A-3 / footer / HEAD / CSS / JS** | スタブ／canonical 部 | スタブ／canonical 部 | **同** |
| **CRIME_SIGNATURES への影響** | 既存 `盗品等罪` シグネチャで content 検証通過 | 同じシグネチャで通過予定 (同一 crime) | **影響なし** |

### diff の総括

構造的に異なるのは **「選択肢数 5 → 4」だけ**であり、それに伴って HTML 内の 4 ヶ所 (TOC / PART A 問題文 / A-2 ox-grid / PART B choice-section) が **5 行から 4 行へ機械的に縮む**。それ以外 (CSS、JS、PART C/D/A-3、footer、HEAD、verdict 判定方式、選択肢内部構造、judge 形式) は完全に同型。

---

## B. 変更が必要なファイル一覧と、各ファイルでの変更要点

### B-0. ファイル一覧 (区分付き)

| 区分 | ファイル | 種別 |
|---|---|---|
| 変更必須 | `schema/problem.schema.json` | 既存編集 |
| 変更必須 | `templates/KTX_template_ox4.html` | **新規作成** |
| 変更必須 | `scripts/render.py` | 既存編集 |
| 変更必須 | `scripts/validate_structure.py` | 既存編集 |
| 変更必須 | `templates/KTX_template_slotmap.md` | 既存編集 (§5 追記) |
| 変更必須 | `problems/327.json` | **新規作成** |
| 変更不要 | `templates/KTX_template.html` | 既存 ox-grid-5 専用として固定 |
| 変更不要 | `scripts/validate_content.py` | choices ループは既に動的 |
| 変更不要 | `canonical/KTX301.html` | 構造参考のまま、形式別追加なし |

**「変更必須 6 ファイル」の内訳は上記の通り。** 以下に各ファイルの変更要点を全件記載する。

### B-1. `schema/problem.schema.json` (既存編集)

| 編集箇所 | 現状 | 変更後 | 理由 |
|---|---|---|---|
| `properties.instruction_type.enum` | `["ox-grid-5", "single-choice", "ranking", "fill-in"]` | `["ox-grid-5", "ox-grid-4", "single-choice", "ranking", "fill-in"]` | `ox-grid-4` を許容するため |
| `properties.instruction_type.description` | 「出題形式。ox-grid-5 は アからオの 5 択を ○× 判断するタイプ。」 | 「出題形式。ox-grid-5 は ア〜オの 5 択 ○×、ox-grid-4 は ア〜エの 4 択 ○× 判定。」 | enum 拡張に合わせた説明補強 |
| `properties.answer.description` | 「正解列。ox-grid-5 なら 5 桁 (例: '12222')」 | 「正解列。ox-grid-5 なら 5 桁 (例: '12222')、ox-grid-4 なら 4 桁 (例: '2212')」 | 4 桁例の追加。pattern `^[12]+$` は既に桁数自由のため未変更 |
| `properties.choices.minItems` / `maxItems` | `1` / `10` | 変更不要 | 既に柔軟 |
| `$defs.Choice.properties.label.enum` | `["ア",…,"コ"]` 10 値 | 変更不要 | 既に柔軟 |

**変更行数の見積もり: 2〜3 行**

### B-2. `templates/KTX_template_ox4.html` (新規作成)

`templates/KTX_template.html` を base とし、E 系 (オ) を機械的に削除した派生テンプレート。`templates/KTX_template.html` 自体は触らず (ox-grid-5 専用として凍結)、別ファイルで派生を作る。

| 編集箇所 (行番号は base 側) | 5 件版 (現 KTX_template.html) | 4 件版 (新 KTX_template_ox4.html) | 備考 |
|---|---|---|---|
| L2024-2028 TOC アンカー | `<a href="#choice-1">ア</a>` 〜 `<a href="#choice-5">オ</a>` 5 件 | `<a href="#choice-1">ア</a>` 〜 `<a href="#choice-4">エ</a>` **4 件** (オ削除) | TOC バー |
| L2049-2050 PART A 見出し (コメント) | 「PART A ── 問題情報 (ox-grid-5 形式)」 | 「PART A ── 問題情報 (ox-grid-4 形式)」 | コメント文言 |
| L2061-2065 PART A 問題文 (problem-text) | `<div class="problem-text"><span class="choice-num-inline">{{CHOICE_A_LABEL}}</span>{{CHOICE_A_STEM}}</div>` 〜 E 行まで 5 行 | A 〜 D の **4 行** (E 行削除) | — |
| L2082-2118 A-2 ox-grid (ox-row) | ox-row 5 件 (A〜E) | ox-row **4 件** (A〜D) | data-correct-value 桁数と ox-row 数の一致は S73-AP35 が動的に検証済 |
| L2137-2270 PART B choice-section | choice-1〜choice-5、parity = `odd / even / odd / even / odd` | choice-1〜choice-4、parity = **`odd / even / odd / even`** | choice-4 の forward nav を `←記述ウ` → `↓共通根拠` に修正 (5 件版の choice-5 役を choice-4 が担う) |
| L2245-2270 choice-5 セクション全体 | choice-5 存在 | **削除** | E 系全 slot (CHOICE_E_LABEL/STEM/VERDICT_LABEL/EXPLANATION/CASES) も同時削除 |
| L2275 PART A-3 共通根拠の back-nav | `<a href="#choice-5">↑記述オ</a>` | `<a href="#choice-4">↑記述エ</a>` | 共通根拠 section の前方アンカーを更新 |
| HEAD / CSS (L1-L1944) | canonical 部 | **byte-level 同期** (差分なし) | 完全に同一を保つ |
| JS ブロック (L2420-2580) | canonical 部 | **byte-level 同期** (差分なし) | ox-grid 行数は実行時に DOM 走査で決まるので 4 行で動作する |
| PART C スタブ (c-1〜c-7) | スタブ存在 | **byte-level 同期** | 同 |
| PART D スタブ、A-3、footer-spec | スタブ存在 | **byte-level 同期** | 同 |

**意図的な差分箇所は計 4 種 (TOC / PART A 問題文 / A-2 ox-grid / PART B choice-section) に限定**。他は同期義務とする (slotmap §5 に明記)。

**変更行数の見積もり: 新規ファイル 約 3,700 行 (既存 KTX_template.html とほぼ同サイズ)、意図差分は 60〜80 行**

### B-3. `scripts/render.py` (既存編集)

| 編集箇所 | 現状 | 変更後 | 理由 |
|---|---|---|---|
| パス定義ブロック (L33-36) | `TEMPLATE_PATH = ROOT / "templates" / "KTX_template.html"` 単一 | `TEMPLATE_PATHS = { "ox-grid-5": ROOT / "templates" / "KTX_template.html", "ox-grid-4": ROOT / "templates" / "KTX_template_ox4.html" }` の dict に変更 | template 選択分岐 |
| `main` 関数 (L129-159) | `template = TEMPLATE_PATH.read_text(...)` | `instruction_type = problem.get("instruction_type", "ox-grid-5")` を取得、`template_path = TEMPLATE_PATHS.get(instruction_type)` で選択。**未定義**の `instruction_type` は ERROR で exit 2 | 既存 326 への regression を防ぐためデフォルトは `ox-grid-5` |
| ログ出力 | `OK: ...` のみ | `OK: ... (template=KTX_template_ox4.html, instruction_type=ox-grid-4)` のように使用 template を明示 | 監査性向上 |
| `LABEL_TO_LETTER` (L45-48) | ア→A 〜 コ→J | 変更不要 | 既に 10 件マップで柔軟 |
| `build_slot_dict` (L58-95) | choices をループし JSON にある分だけ slot 化 | 変更不要 | E 系が JSON に無ければ `{{CHOICE_E_*}}` は dict に追加されない。新 ox4 template には `{{CHOICE_E_*}}` slot が存在しないので未置換残りも 0 |

**変更行数の見積もり: 10〜15 行**

### B-4. `scripts/validate_structure.py` (既存編集)

| 編集箇所 | 現状 | 変更後 | 理由 |
|---|---|---|---|
| `check_S12_part_b_choices` (L153-158) | `choices = [soup.find(id=f'choice-{i}') for i in range(1, 6)]` 5 件ハードコード | 期待数 N を動的算出: ① HTML 内の `[id^="choice-"]` 実数、または ② `answer-area .answer-area[data-correct-value]` の桁数。**両者が一致**することを **二重要件**化 (不一致は ERROR) | ox-grid-4 と ox-grid-5 を両対応、かつ偽陽性回避 |
| `check_S17_subcards` (L201-217) | `for i in range(1, 6)` 5 件ハードコード | 上記 S12 で算出した N を流用し `range(1, N+1)` | 動的化 |
| `check_S73_AP35` (L617-627) | `if len(rows) != len(cv): ERROR` | 変更不要 | 既に動的に cv 桁数と一致を要求済 (4 桁の cv なら 4 ox-row、5 桁なら 5 を要求) |
| その他 S 群 | — | 変更不要 | choice-1〜5 を直接参照しない |
| 新規 sanity check (追加) | — | choice-section 数 N と ox-row 数と cv 桁数の **3 者一致** を S12 拡張として ERROR 化 | R2 のリスク回避 (誤動作で「3 件で正しい」と認定されないように) |

**変更行数の見積もり: 15〜20 行**

### B-5. `templates/KTX_template_slotmap.md` (既存編集、§5 追記)

§5 末尾に新規サブセクション **§5.1 ox-grid-N 形式分岐 (R-1: ox-grid-4 対応)** を追加。本文は D 節参照。

**変更行数の見積もり: 約 50 行 (D 節の文章をそのまま追加)**

### B-6. `problems/327.json` (新規作成)

| フィールド | 値 (暫定) | 出処 |
|---|---|---|
| `id` | `"327"` | ファイル名 |
| `source` | `"予備R2-10"` | PDF タイトル |
| `chapter` | `"第4章 財産に対する罪"` | PDF ヘッダー |
| `section` | `"第8節 盗品等に関する罪"` | PDF ヘッダー |
| `page` | `847` | PDF |
| `crime` | `"盗品等罪"` | CRIME_SIGNATURES キー統一 (PDF タイトル「盗品等に関する罪」とは表記揺れ) |
| `points` | `3` | PDF |
| `correct_rate` | `"37%"` | PDF |
| `instruction_type` | `"ox-grid-4"` | **新 enum 値** |
| `instruction` | PDF 設問文 (4 択版) | PDF |
| `answer` | `"2212"` | PDF 正解バー (ア2 イ2 ウ1 エ2) |
| `answer_explanation` | `"解答および各記述の正誤判定"` | 326 と同基本値 (AP-37 抵触回避) |
| `override_pattern` | `"P3"` | 正答率 37% → < 40% 帯 |
| `choices[0..3]` | ア / イ / ウ / エ の 4 件 | PDF (オなし) |
| `choices[i].label` | `"ア"` / `"イ"` / `"ウ"` / `"エ"` | — |
| `choices[i].stem` | PDF 各選択肢本文 | PDF |
| `choices[i].verdict` | `"2"` / `"2"` / `"1"` / `"2"` | PDF 解説 |
| `choices[i].verdict_label` | 「誤っている」/「誤っている」/「正しい」/「誤っている」 | 同 |
| `choices[i].case_citations` | 各引用判例 (最決昭34.2.9、大判明42.4.15 等) | PDF 解説 |
| `choices[i].explanation` | 各解説本文 | PDF |

**変更行数の見積もり: 新規 約 50〜60 行 (326.json と同等規模)**

---

## C. canonical 新規作成の要否判断

**判断: `canonical/KTX_ox4_sample.html` は作らない。**

### 理由 (4 点)

1. **KTX301 そのものが ox-grid ですらない**。canonical/KTX301.html は組合せ型 5 択 (アからオの記述と結論Ⅰ/Ⅱ/Ⅲの組合せを 1〜5 から選ぶ形式) で、326 (ox-grid-5) や 327 (ox-grid-4 候補) とは出題形式が異なる。canonical は PATCH §1 で「構造と仕上がりの参考例」と限定され、本文・解説の供給源ではないと明示済み。形式別に canonical を増やすと、コピー禁止対象も増え、事故面積 (流用ミス) が拡大する。

2. **canonical の役割は最小化済み**。PATCH §1 が「内容供給源ではない」と限定した結果、構造参考の役割は実質的に `templates/KTX_template*.html` に移管されている。テンプレ自体が骨格を保持しているため、形式別 canonical を別途持つ必然性がない。

3. **運用上の reference は「最初に完走した実例 HTML」とする**。
   - ox-grid-5 の reference → `outputs/000_TX/001_刑法/刑TX326.html`
   - ox-grid-4 の reference → 完成後の `outputs/000_TX/001_刑法/刑TX327.html`

   これは「実装が 3 段検証を通った証跡」であり、新規 canonical を持つ必要はない。

4. **二重管理のコスト**。形式別 canonical を作ると、template と canonical で同じ構造を二重に保守することになる。template 修正のたびに canonical も追従させる義務が発生し、乖離リスクが恒常化する。

---

## D. slotmap.md §5 に追記すべき設計項目 (実際に追記する文章)

以下を `templates/KTX_template_slotmap.md` の §5 末尾に追加する。

```markdown
---

## §5.1 ox-grid-N 形式分岐 (R-1: ox-grid-4 対応)

### 背景

問題 327 (予備 R2-10、盗品等罪) は ア〜エの 4 択 ○× 判定で構成され、現行
`templates/KTX_template.html` (ア〜オの 5 件ハードコード) では未置換 slot
`{{CHOICE_E_*}}` が残り render fail する。今後の形式拡張可能性を踏まえ、
以下の方針で対応する。

### 決定事項

#### 1. schema 拡張

- `schema/problem.schema.json` の `instruction_type` enum に `"ox-grid-4"` を
  追加する。
- 当面サポートは `ox-grid-5` / `ox-grid-4` の 2 値とする。
- `multi-select-*`, `combination-*`, `single-choice`, `ranking`, `fill-in`
  は別フェーズの案件として扱う (今フェーズではスコープ外)。
- `answer.description` に 4 桁例 `'2212'` を追記する。pattern `^[12]+$` は
  桁数自由のため変更不要。
- `choices.minItems` / `maxItems` および `choice.label.enum` は既に柔軟
  (1〜10、ア〜コ) のため変更不要。

#### 2. テンプレート構成

- `templates/KTX_template_ox4.html` を新規作成する。
- ベースは `templates/KTX_template.html` (ox-grid-5 版) から E 系 (オ) を
  機械的に削除した派生とする。
- 単一 template に CSS/JS 分岐を埋め込む案は採用しない。HTML 構造そのものの
  増減を CSS 表示制御で隠すと:
  - validate_structure.py の S12 / S17 (choice-section 5 件期待) が fail する
  - DOM ノイズが残り、screen reader / DevTools 上で混乱を招く
  - 「非表示の choice-5」を解析する自動化スクリプトを誤動作させる
  という 3 重の害が出る。

#### 3. 意図的な差分箇所 (KTX_template.html ↔ KTX_template_ox4.html)

差分は以下 4 種類のみに限定し、それ以外は byte-level 同期を義務とする:

| 差分箇所 | 5 件版 | 4 件版 |
|---|---|---|
| TOC アンカー | ア〜オ 5 件 | ア〜エ 4 件 |
| PART A 問題文 (problem-text) | A〜E 5 行 | A〜D 4 行 |
| A-2 ox-grid (ox-row) | A〜E 5 件 | A〜D 4 件 |
| PART B choice-section | choice-1〜choice-5、parity = odd/even/odd/even/odd | choice-1〜choice-4、parity = odd/even/odd/even、choice-4 の forward nav は「↓共通根拠」 |

HEAD / CSS / JS / PART C スタブ / PART D スタブ / A-3 / footer-spec は
byte-level 同期。両 template を編集する際は同一の修正を双方に反映すること。

#### 4. canonical 構成

- 形式別 canonical は **追加しない**。
- `canonical/KTX301.html` を引き続き構造参考として固定する。
- ox-grid-N 系の運用 reference は「最初に 3 段検証 (render → structure →
  content) を完走した実例 HTML」とする:
  - ox-grid-5 → `outputs/000_TX/001_刑法/刑TX326.html`
  - ox-grid-4 → 完成後の `outputs/000_TX/001_刑法/刑TX327.html`
- canonical ファイル数を増やさないことで、コピー禁則対象とテンプレ役割の
  分裂を防ぐ。

#### 5. render.py の template 選択分岐

- `scripts/render.py` に `TEMPLATE_PATHS` dict を導入する:
  - `"ox-grid-5"` → `templates/KTX_template.html`
  - `"ox-grid-4"` → `templates/KTX_template_ox4.html`
- `problems/{id}.json` の `instruction_type` から template を選択する。
- **デフォルト挙動**: `instruction_type` が未指定の場合は `ox-grid-5` を選択し
  (既存 326 のセマンティクス維持)、stdout に WARN ログを出力する。
- `instruction_type` が dict に無い値 (例: 旧 `single-choice` 等) の場合は
  ERROR で exit 2。silently 失敗させない。

#### 6. validate_structure.py の動的化

- S12 (PART B choice-section) と S17 (sub-card 検査) を choice-section 数
  ハードコード 5 から動的化する。
- 期待数 N の導出は以下の **三者一致** を要件とする:
  1. HTML 内の `[id^="choice-"]` 実数
  2. `answer-area .answer-area[data-correct-value]` の桁数
  3. (JSON が利用可能な場合) `choices` 配列長
- 三者が不一致の場合は ERROR を発する (誤って「3 件で正しい」と認定される
  リスクを潰すため)。
- S73-AP35 (ox-row 数 == cv 桁数) は既に動的、変更不要。

#### 7. 両 template の同期義務

`templates/KTX_template.html` を修正する際は同一の修正を
`templates/KTX_template_ox4.html` にも反映する。差分は §3 で列挙した 4 種類
のみとし、それ以外の場所が乖離した場合は同期不備とみなす。

将来的な PR / レビュー観点として、両 template の `diff` を取り、差分が想定 4
箇所のみであることを確認する手順を推奨する (CI 化の検討余地あり)。

### 将来の一般化 (保留)

`ox-grid-N` (N=3, 6, ...) が必要になった場合、template 別ファイル方式は
N 個のファイル爆発で破綻する。その時点で以下のいずれかへ移行する:

- (a) JS による行動的レンダリング (ランタイムで `<div class="ox-row">` を生成)
- (b) JSON 駆動の partial 合成 (render.py をテンプレ生成側に拡張、各
      ox-row / problem-text / choice-section をループ展開)

本フェーズでは N ∈ {4, 5} の 2 ファイル方式で凍結する。N=3 または N>=6 の
問題が新規入手された時点で再設計トリガーとする。

### AP-37 抵触回避ガイド

`answer_explanation` フィールドの値は、326 と同じく
「解答および各記述の正誤判定」を基本句とする。罪名・正解番号・PDF タイトル
固有句を含めないこと (validate_structure.py の S74-AP37 が正解値リテラルの
先頭混入を検知)。

### crime 表記揺れの取り扱い

PDF タイトルの罪名表記は問題ごとに揺れる:

- 326: 「盗品等罪」
- 327: 「盗品等に関する罪」

`problems/{id}.json` の `crime` 値は CRIME_SIGNATURES のキーに統一して
`"盗品等罪"` とする (validate_content.py の negative check キーと一致させる
ため)。PDF タイトルの正式名称を HTML 上で表示する必要が出た場合は、将来
`{{CRIME_DISPLAY}}` 等の派生 slot を導入することを検討する (本フェーズでは
スコープ外)。

---
```

---

## E. 推奨実装順序 (Step 番号付き、各 Step の検証ポイント込み)

| Step | 作業 | 検証ポイント | 完了条件 | 所要工数の目安 |
|---|---|---|---|---|
| **Step 1** | `schema/problem.schema.json` の enum 拡張 | (a) `ox-grid-5` を含む既存 enum を破壊していないか<br>(b) `ox-grid-4` 値が JSON Schema の validator で受理されるか<br>(c) `answer.description` の追記が読み手に矛盾しないか | 326.json を schema validator にかけても引き続き valid。`ox-grid-4` を持つダミー JSON も valid | 5 分 |
| **Step 2** | `scripts/validate_structure.py` の S12 / S17 動的化 | (a) 既存の 5 件 HTML (刑TX326.html) に対し ERROR を新規に発しない (regression なし)<br>(b) わざと 3 件しかない不正 HTML を作って ERROR が出るか (三者一致チェックの逆方向確認)<br>(c) 既存 WARN×8 (S14, S17×5, S51, S71-AP33) の内訳が変わらない | 326.html を再検証して「ERROR 0、WARN 8 件 (既存と同一)」を維持 | 30 分 |
| **Step 3** | `templates/KTX_template_ox4.html` の新規作成 | (a) `diff KTX_template.html KTX_template_ox4.html` の差分が §5.1 §3 で定めた 4 種類のみに限定されているか<br>(b) `{{CHOICE_E_*}}` slot が完全に消滅しているか (`grep -E "CHOICE_E_(LABEL|STEM|VERDICT|EXPLANATION|CASES)"` がヒット 0 件)<br>(c) HEAD / CSS / JS / PART C / PART D / A-3 / footer が byte-level で同一か<br>(d) choice-4 の forward nav が `↓共通根拠` に変更されているか | 上記 a〜d すべて満たす | 1〜2 時間 |
| **Step 4** | `scripts/render.py` の template 選択分岐 | (a) `instruction_type: "ox-grid-5"` または未指定 → `KTX_template.html` を選ぶ<br>(b) `instruction_type: "ox-grid-4"` → `KTX_template_ox4.html` を選ぶ<br>(c) 未知の値 (例: `"foo"`) → exit 2 で安全停止<br>(d) ログに使用 template 名を明示 | 326.json で再 render し以前と同 HTML (ハッシュ一致または差分なし) が出力される。ダミー 327.json (仮置き) で ox4 template が選ばれる | 30 分 |
| **Step 5** | `templates/KTX_template_slotmap.md` への §5.1 追記 | (a) D 節の本文を逐語で追加<br>(b) 既存 §0〜§5 の節番号と整合しているか<br>(c) 内部リンク・コード例の文法が崩れていないか | 追記後の slotmap.md が markdown として正しく表示される (プレビューで確認) | 15 分 |
| **Step 6** | `problems/327.json` を 327.pdf から起こす | (a) schema validator で valid (required 全充足、enum 値正しい、`instruction_type: "ox-grid-4"`、`answer: "2212"`、choices 4 件)<br>(b) canonical/KTX301.html から本文・解説を一切コピーしていない<br>(c) `crime` 値が `"盗品等罪"` で CRIME_SIGNATURES キーに一致<br>(d) `answer_explanation` が「解答および各記述の正誤判定」基本句<br>(e) Read tool で読み戻して書いた内容と完全一致 | 上記 a〜e すべて満たす | 1〜2 時間 |
| **Step 7** | 327 の 3 段検証完走 | (a) `python scripts/render.py 327` exit 0、`outputs/000_TX/001_刑法/刑TX327.html` が生成、未置換 slot 0<br>(b) `python scripts/validate_structure.py outputs/000_TX/001_刑法/刑TX327.html` exit 0、ERROR 0<br>(c) `python scripts/validate_content.py outputs/000_TX/001_刑法/刑TX327.html problems/327.json` exit 0 (negative + positive 双方 PASS)<br>(d) ブラウザで開いて ox-grid 4 行が正しく動作するか目視 (任意) | 上記 a〜c すべて exit 0 | 30 分 |
| **Step 8** | **326 の regression 検証** | (a) `python scripts/render.py 326` で生成された HTML が以前のものと同一 (変更前後で diff 0、または 5 件版 template を選んだログが出る)<br>(b) `validate_structure.py` で ERROR 0、WARN 8 件 (既存内訳)<br>(c) `validate_content.py` PASS | 326 のパイプラインが完全に維持されている | 15 分 |
| **Step 9** | (任意) 両 template の同期 diff 取得をルーチン化 | (a) `diff KTX_template.html KTX_template_ox4.html` の出力が §5.1 §3 の 4 種類のみ<br>(b) 想定外の差分があれば修正<br>(c) 将来の CI チェックに組み込む候補として記録 | 同期不備なし | 15 分 |

**合計工数の目安: 4〜6 時間**

各 Step の検証ポイントを充足してから次 Step に進む。Step 7 で fail した場合は Step 3 (template) と Step 4 (render.py) に戻る。Step 8 で fail した場合は Step 4 のデフォルト分岐ロジックを最優先で修正する。

---

## F. 想定リスクと回避策

| ID | リスク | 想定影響 | 回避策 |
|---|---|---|---|
| **R1** | テンプレ 2 本立ての**保守乖離** | `KTX_template.html` 修正時に `KTX_template_ox4.html` への取り込み忘れ → 両者が別物に分化 | (a) slotmap §5 に「両 template 同期義務」を明記<br>(b) 差分許容ポイント (TOC・PART A 問題文・A-2 ox-grid・PART B choice-section の 4 箇所のみ) を固定化<br>(c) `diff KTX_template.html KTX_template_ox4.html` を定期的に取り、想定外差分を検出 |
| **R2** | **validate_structure.py 動的化の副作用** | choice-section が誤って 3 件しかない HTML を「3 件で正しい」と誤認 | choice-section 数・ox-row 数・`data-correct-value` 桁数の **三者一致** を S12 拡張として要件化。不一致なら ERROR |
| **R3** | **`instruction_type` 未指定の旧 JSON** | `instruction_type` は schema 上 optional のため、未指定の旧 JSON が template 選択を素通り | render.py のデフォルトを `ox-grid-5` に倒し、未指定時は stdout に WARN を出す。将来的に required 化する場合は migration を別案件として扱う |
| **R4** | **将来の ox-grid-3, ox-grid-6** | 別ファイル方式が N ファイル爆発で破綻 | 当面は N ∈ {4, 5} に凍結 (slotmap §5 で明示)。3 件目 (ox-grid-3 または >=6) が出る時点で一般化リファクタを発火 (JS レンダリング or render.py の partial 合成) させる。decision-triggered な技術負債管理 |
| **R5** | **canonical 追加リスク** (仮に新規したら) | KTX301 と矛盾する skeleton ができて参照源が分裂 | C 節および slotmap §5.1 §4 の通り **canonical を追加しない**ことを明文化。reference は完走した実例 HTML に委ねる |
| **R6** | **`answer_explanation` の AP-37 抵触** | ox4 用に流用する際、罪名・正解番号が混入 | 326 と同じ「解答および各記述の正誤判定」基本句を踏襲、罪固有句・先頭数字は禁止と slotmap §5.1 末尾で明示 |
| **R7** | **327 の crime 表記揺れ** | PDF タイトル「盗品等に関する罪」、326 は「盗品等罪」、`CRIME_SIGNATURES` キーは「盗品等罪」 | 327.json の `crime` 値は CRIME_SIGNATURES のキーに合わせ `"盗品等罪"` で統一。PDF タイトル表記は HTML に出さないか、将来 `{{CRIME_DISPLAY}}` 派生 slot で別途対応 |
| **R8** | **render.py 分岐ミスで 326 退行** | template 選択ロジックの誤りで既存 326 が ox4 template で render → 構造崩れ | デフォルト分岐を「`ox-grid-5` 既存パス維持」に倒し、追加した条件分岐は `ox-grid-4` の場合のみ ox4 template を選ぶ。Step 8 (326 regression) で必ず確認 |
| **R9** | **schema enum 拡張による既存 JSON の妥当性破壊** | 既存 326.json の `instruction_type: "ox-grid-5"` が無効化される可能性 | 新 enum は既存値を**包含する追加のみ** (remove なし、add のみ)。schema validator が後方互換となる |
| **R10** | **「予備独自問題」表示の取り扱い** | 327 PDF タイトルに「予備独自問題」と特記、326 (司法試験) には無い | `source` 値で `"予備R2-10"` と識別。HTML への展開は既存 `{{SOURCE_ID}}` slot で吸収。将来 `{{EXAM_TYPE_BADGE}}` 等の派生 slot を検討する余地あり (slotmap §1.2 で既出だがスタブ化済み) |
| **R11** | **`ox4` の `parity` 末尾の odd/even の見た目崩れ** | 4 件版で parity が `odd/even/odd/even` となり、5 件版 (最後が odd) と背景パターンが異なる | CSS (`.choice-section.even::before` 等) は parity に応じた装飾を持つだけで論理破綻はしないが、ユーザーが見た目の差異に気付く可能性あり。意図的差分として slotmap §5.1 に明記する |
| **R12** | **「★」マーク等の PDF 固有記号** | 327 の選択肢ウに「★」マークがあるが、現 schema にフィールドなし | 当面は無視。将来必要になれば `choices[*].marks` 配列を追加検討。本フェーズではスコープ外 |

---

## 調査結果の総括

- **schema, render.py, validate_content.py, choice.label enum は既に 5 件固定ではない**。実質固定は 3 箇所のみ:
  - `schema/problem.schema.json` の `instruction_type` enum
  - `templates/KTX_template.html` の HTML ハードコード (オ × 5 行群 = TOC, PART A 問題文, A-2 ox-grid, PART B choice-section)
  - `scripts/validate_structure.py` の S12 / S17 の `range(1, 6)`
- 修正規模は schema 2〜3 行 + validator 約 15〜20 行 + 新 template 1 ファイル + render.py 約 10〜15 行 + slotmap 約 50 行 + 327.json 約 60 行 = **総計 約 150 行以内の追加**で吸収可能。
- canonical は触らない、両 template 同期義務を slotmap で固定する、render.py のデフォルトを ox-grid-5 に倒す、の 3 点を守れば 326 への regression と将来の保守乖離が同時に抑えられる。
