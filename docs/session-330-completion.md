# セッション完了記録 — 330 (combination-5) 完走 + 326-330 シリーズ総括

## メタ情報

- **作成日**: 2026-05-18
- **対象セッション**: 330 単独実装セッション（326〜330 連続作業の **最終回 5 回目**）
- **本書の位置づけ**: 同シリーズの先行セッション記録
  - `docs/ox4-design-investigation-326-330-session.md` (調査・初期 ox-grid-4 設計)
  - `docs/session-326-327-completion.md` (326 ox-grid-5 / 327 ox-grid-4 完了)
  - `docs/session-328-completion.md` (328 multi-select-5 完了)
  - `docs/session-329-completion.md` (329 single-choice-5 完了)

  に続く **第 5 弾 (最終)**。combination-5 形式（PART A 二層構造）の実装完走と
  検証結果に加え、**326-330 全 5 形式完走のシリーズ全体総括** を含む。

---

## 1. 完走した問題

| ID | 形式 | crime | source | answer | パターン | HTML パス | 検証結果 |
|---|---|---|---|---|---|---|---|
| **330** | combination-5 | 器物損壊罪 (+ allowed_cross_refs: ["窃盗罪", "信書隠匿罪"]) | 予備H23-10 (予備独自問題 平成23年第10問) | `3` (integer 単体、組合せ番号) | P1 (ローズシャンブル、正答率 84%) | `outputs/000_TX/001_刑法/刑TX330.html` (103,945 bytes) | 全 3 段 PASS |

### 3 段検証 (render → validate_structure → validate_content) 結果

| 検証段 | 330 |
|---|---|
| render | ✅ exit 0、`template=KTX_template_comb5.html`、`instruction_type=combination-5`、未置換 slot 0 |
| validate_structure | ✅ ERROR 0、WARN **7 件** (S14 / S17×5 / S51。**S71-AP33 / S78 / S79 はすべて消滅 or PASS**) |
| validate_content | ✅ PASS (negative + positive 共にクリーン、`answer=3` の HTML 出現 + 各 combination の set 中黒連結が HTML 内出現 + answer-combinations 整合性 PASS + negative check で 窃盗罪 allowed_cross_refs クリア) |

**特筆事項**:

- **S71-AP33 が 328/329 に続き 330 でも消滅**: single canonical 文言 `^選択肢を選んで「解答を表示」を押してください。$` を採用したため。326/327 (ox-grid 系) のみで残存。
- **S78 views-section 検査が PASS**: combination-5 では views-section が存在しないため、helper の「無いなら何もしない」分岐で正常に通過 (slotmap §5.4 §6 の設計通り)。
- **新規 S79 combinations-section 検査が PASS**: combinations-section 1 件、combo-block 5 件、各々 combo-label + combo-set を持つ構造を grep で目視確認済。

---

## 2. 326 / 327 / 328 / 329 四重 regression: HTML byte-identical (SHA256 一致) 確認結果

combination-5 実装が **既存 ox-grid / multi-select / single-choice 全 4 件の経路に
一切の副作用を与えていない**ことを、HTML バイト単位比較で実証した。

### 検証手順

1. 実装着手前の `outputs/000_TX/001_刑法/刑TX326-329.html` をそれぞれ `.bak` として退避。
2. schema / render.py / validate_structure.py / validate_content.py / 新 comb5 template
   を投入後、4 件を再 render。
3. 新旧 HTML の SHA256 ハッシュを比較。

### 結果

| 問題 | 旧 SHA256 | 新 SHA256 | identical | 使用テンプレ |
|---|---|---|---|---|
| **326** | `E4790D25A4486F7DCC255111C7AEA0E6E6C61E24F26DFF6D9F9C026E9094FF53` | `E4790D25A4486F7DCC255111C7AEA0E6E6C61E24F26DFF6D9F9C026E9094FF53` | **True** | `KTX_template.html` (デフォルト経路) |
| **327** | `1AC6D19B23BA488B4002E3986FE23A24E66BE11CC8AA24B8C5D4A68A95B5CD48` | `1AC6D19B23BA488B4002E3986FE23A24E66BE11CC8AA24B8C5D4A68A95B5CD48` | **True** | `KTX_template_ox4.html` |
| **328** | `1839599B3D7B23F8F64A58891CBCABCE117C9D46EB11559A710094F470160CE7` | `1839599B3D7B23F8F64A58891CBCABCE117C9D46EB11559A710094F470160CE7` | **True** | `KTX_template_msel5.html` |
| **329** | `7009D4521FD75C22C87B14A2D2B3D073FE330CF4439F8AC4F6422CCAC41BF417` | `7009D4521FD75C22C87B14A2D2B3D073FE330CF4439F8AC4F6422CCAC41BF417` | **True** | `KTX_template_sc5.html` |

### validate 結果（前回からの差分）

| 問題 | ERROR | WARN | 内訳 | 前回からの差分 |
|---|---|---|---|---|
| 326 | 0 | 8 | S14 / S17×5 / S51 / S71-AP33 | **完全同一** |
| 327 | 0 | 7 | S14 / S17×4 / S51 / S71-AP33 | **完全同一** |
| 328 | 0 | 7 | S14 / S17×5 / S51 | **完全同一** |
| 329 | 0 | 7 | S14 / S17×5 / S51 | **完全同一** |

→ `TEMPLATE_PATHS.get(instruction_type, TEMPLATE_PATH)` デフォルト経路、`_format_answer()`
の 3 ブランチ分岐、`_derive_cv_info()` の mode 別判定、views slot / combinations slot
の独立供給がすべて正しく既存挙動を温存することを実証。

---

## 3. §5 案件で消化したもの

### 3.1 schema combinations フィールド追加 (combination-5 系のみ、後方互換維持)

**経緯**: 330 は 5 つの組合せ選択肢 (例: 1=ア・イ, 2=ア・オ, ..., 5=エ・オ) を持ち、
これを構造化して保持する schema 概念が必要となった。

**消化内容**:

- `schema/problem.schema.json` に **`$defs.Combination` を新規定義**:
  - `{ label: enum ["1","2","3","4","5"], set: array of string (enum ア〜オ, uniqueItems) }`
  - `additionalProperties: false`、`set` は `minItems: 1, maxItems: 5`
- `properties.combinations` を新規追加:
  - `type: array, items: { $ref: "#/$defs/Combination" }, minItems: 5, maxItems: 5`
  - **optional**: combination-5 系のみで使用、他形式では未指定
- `instruction_type.enum` に `"combination-5"` を追加 (add only)。
- 326/327/328/329.json は combinations 未指定で引き続き valid。**四重 regression
  byte-identical で実証**。

**結果**:
- 5 件固定の組合せ構造を schema レベルで強制 (minItems/maxItems=5)。
- set 内のラベル enum (ア〜オ) と uniqueItems で異常な組合せ (例: `["ア", "ア"]`)
  を schema が弾く。
- 既存 4 件への影響ゼロ。

### 3.2 5 本目 template (KTX_template_comb5.html) 新設

**経緯**: 設計調査 (`docs/` 配下) で α/β/γ 比較を行い、**(α) KTX_template.html cp ベース
での新規 5 本目作成** を採用 (調査記録参照)。

**消化内容**:

- `templates/KTX_template_comb5.html` を新規作成 (2,778 行 / 94,894 bytes)。
- ベース: `templates/KTX_template.html` (ox-grid-5) を cp。
- 意図差分 **4 種類のみ** に限定（slotmap §5.4 §3）:
  1. PART A 見出しコメント (`ox-grid-5 形式` → `combination-5 形式`)
  2. **【組合せ】section 新規追加** (PART A 内、problem-text 群の後ろ、A-2 の前)
  3. A-2 解答エリア全面書換 (`ox-grid` → `single`、`<div class="answer-row">` +
     `<button class="answer-slot">` × 5)
  4. A-2 `<h3>` および `answer-instruction` 文言 (single canonical 文言)
- ラベル系統 (ア〜オ) は KTX_template.html とデフォルト一致のため、TOC / PART B
  nav / セクションコメント / sec-nav 等の hardcoded text は **1 つも触らず**。
- HEAD / CSS / JS / marker-legend / PART C / PART D / A-3 / footer-spec は
  base と byte-level 同期。
- **CSS / JS の追加変更は一切なし**（v8.11.3 既存 single インフラを完全活用）。

**結果**:
- 4 種類の意図差分のみで完結、想定外の追加変更なし (slotmap §5.4 §8 実測値で確認)。
- 既存 4 本 template に対する byte-identity に影響ゼロ。

### 3.3 PART A 二層構造 (ア〜オ ox + 組合せ single)

**経緯**: 330 は記述 ア〜オ (5 件) と 組合せ 1〜5 (5 件) の二系統ラベル混在型で、
canonical KTX301 と構造的に同型。

**消化内容**:

- PART A 上半分: 既存の problem-text × 5 (ア〜オ) を **そのまま維持** (KTX_template.html
  と同一)。
- PART A 下半分: **新規【組合せ】section** を 5 件 (1〜5 の組合せ表示)。
  - `<section class="combinations-section" id="part-a-combinations">` 1 件
  - `<div class="combo-block">` × 5
    - `<span class="combo-label">{{COMBO_N_LABEL}}</span>`
    - `<span class="combo-set">{{COMBO_N_SET}}</span>` (例: "ア・イ")
- A-2: `data-answer-type="single"`、`answer-slot` × 5 (番号 1-5)。
- `render.py` に `combinations` slot 展開ロジックを追加:
  - JSON の combinations 配列 → 10 slot (COMBO_1〜5_LABEL/SET)
  - set 配列を **中黒「・」** で連結 (`COMBO_SET_SEPARATOR` 定数)

**結果**:
- HTML 内に combinations-section 1 件、combo-block 5 件、combo-label A〜E と combo-set
  ア・イ/ア・オ/イ・ウ/ウ・エ/エ・オ がすべて正しく展開 (grep で目視確認済)。
- canonical KTX301 と構造的に同型の問題タイプを初めてサポート。

### 3.4 validate_structure S78 緩和 / S79 新設

**消化内容**:

- **S78 (views-section 検査) の緩和**: helper 内部の既存実装 (views-section が存在
  しない HTML では何もしない) で combination-5 に自動対応。**追加変更なしで対応済**。
- **S79 (combinations-section 検査) 新設**:
  - `<section class="combinations-section">` が存在する場合、combo-block が固定 5 件
    であることを **ERROR** チェック
  - 各 combo-block に `combo-label` と `combo-set` が存在することを **WARN** チェック
  - combinations-section が存在しない HTML (326-329) では何もしない
- `validate_content.py` の positive check に **combinations 整合確認** を追加:
  - answer (integer) が combinations の labels と一致するか
  - 各 combination の set 中黒連結文字列 ("ア・イ" 等) が HTML 内に出現するか

**結果**:
- 330 で S79 PASS (combinations-section 1、combo-block 5、各々完備)。
- 326-329 への影響ゼロ (S79 は combinations-section 不在で素通り)。

### 3.5 slotmap §5.4 新設、§8 実測値 5 項目埋め込み完了

**消化内容**:

- 直前のターン (実装着手前) で `templates/KTX_template_slotmap.md` に §5.4
  「combination-N 形式分岐 + 【組合せ】slot + 二系統ラベル混在 (R-4)」を追記済。
- 章立て: 背景 / 決定事項 1〜8 / 【見解】slot の扱い (combination-5 では使わない) /
  将来の一般化 / AP-37 抵触回避ガイド / crime 表記揺れの取り扱い。
- (b) refactor 発火条件を本書 §7 に正式判定 (AND 条件 ①/② 両方とも不充足)。
- **§5.4 §8「五 template 完了時点の同期実測」を本実装中に実測値で埋め込み完了**:
  - byte-identity 維持時間: 累計約 110 分
  - diff 10 ペア自動検証: **589 ms**
  - 意図差分テーブルから漏れた差分: なし
  - (b) refactor 主観的圧力: 3/5
  - CI 化導入時期: 次セッション最優先

**結果**:
- slotmap.md は 920 行 → **1,284 行** に拡張（§5.4 追記 + §8 実測値）。
- 実装が「推定」ではなく「実測」に基づく根拠付き判断材料が確立。

---

## 4. §5 案件で保留中のもの

326-330 共通で常駐している WARN は以下の 4 系統。本セッションでも触らず保留。

| WARN ID | 内容 | 326 | 327 | 328 | 329 | 330 | 想定対応 |
|---|---|---|---|---|---|---|---|
| **S14** | drill-block 数 = 0 (期待値: 12) | 1 | 1 | 1 | 1 | 1 | **slotmap §5.5 候補**。PART D スタブを実装する案件 |
| **S17×N** | choice-* の sub-card 欠落: `['professor']` | 5 | 4 | 5 | 5 | 5 | **slotmap §5.6 候補**。各 choice-section に professor sub-card を追加 |
| **S51** | footer-spec 必須 feature-tag 欠落: `['ktx301-canon']` | 1 | 1 | 1 | 1 | 1 | **slotmap §5.7 候補**。template の footer-spec のみの修正 |
| **S71-AP33** | `<p class="answer-instruction">` が canonical 文言と相違 | 1 | 1 | **0** | **0** | **0** | **slotmap §5.8 候補**。326/327 (ox-grid 系) のみ残存、文言調整で全消滅 |

### CRIME_SIGNATURES 拡張 (slotmap §5.9 候補)

- 信書隠匿罪 / 毀棄罪 / 損壊罪 などが CRIME_SIGNATURES に未登録。
- 329/330 で `allowed_cross_refs: ["信書隠匿罪", "窃盗罪"]` 等で明示的に対処済だが、
  論理的整合性のために CRIME_SIGNATURES への正式追加を slotmap §5.9 として計画。

### 5 本立て同期義務、(b) refactor 発火条件は現時点で発火しないが要監視

- AND 条件 ①/② 両方とも不充足（slotmap §5.4 §7 / §5.4 §8 実測値）。
- **次の判断ポイント**: 形式 #6 入口 (331 以降の PDF または新形式 confirmed) で
  再評価必須。
- **緊急トリガー**: 5 本立て diff 10 ペア手動レビューでの同期義務違反が頻発した場合、
  または CI 化前に主観的圧力が 4/5 以上に到達した場合。

**いずれも構造検証 S レベルでは ERROR ではなく WARN 扱いのため、現在の 3 段検証
パイプラインは全件 PASS している。**

---

## 5. 5 本立て template の同期義務（引き続き義務化、形式 #6 入口で再評価義務）

本セッションで `templates/` 配下の v8.11.6 系 template ファイルは **5 本立て**に
拡張された：

| ファイル | 用途 | 行数 | bytes | byte-identity 確立済 |
|---|---|---|---|---|
| `KTX_template.html` | ox-grid-5 (326 等) | 2,788 | 95,298 | ✅ |
| `KTX_template_ox4.html` | ox-grid-4 (327 等) | 2,751 | 93,882 | ✅ |
| `KTX_template_msel5.html` | multi-select-5 (328 等) | 2,754 | 93,835 | ✅ |
| `KTX_template_sc5.html` | single-choice-5 (329 等) | 2,770 | 94,478 | ✅ |
| `KTX_template_comb5.html` | **combination-5 (330 等)** | **2,778** | **94,894** | ✅ (本セッションで確立) |

### diff ペア数の状況

- 3 本立て (§5.2 完了時): 3 ペア — 手動で許容
- 4 本立て (§5.3 完了時): 6 ペア — 手動境界に到達
- **5 本立て (本書 §5.4 完了時): 10 ペア — CI 化が現実的に必須**
- 6 本立て (将来 §5.5+): 15 ペア — CI 化前提でも限界

### 同期義務の明文化 (slotmap §5.4 §7 を継承)

- **同期対象**: HEAD / CSS / JS / PART C スタブ / PART D スタブ / A-3 / footer-spec
- **意図差分対象**: TOC アンカー / PART A 問題文行数とラベル / 【見解】section
  (sc5 のみ) / 【組合せ】section (comb5 のみ) / A-2 解答エリア構造 / PART B
  choice-section / sec-nav 表記

### 形式 #6 入口で AND 条件再判定の義務

slotmap §5.4 §7 で正式宣言された再評価義務:

- **AND 条件 ①**: 形式 #6 PDF が既存 5 本のいずれの派生でも合理的に収まらない
- **AND 条件 ②**: 形式 #6 以降の予定が 2 件以上 confirmed

→ AND 充足時に **(b) refactor 発火**（partial 合成 / JS 動的レンダリングへ移行）。
それまでは CI 化スクリプトで 10 ペア diff を自動検証する運用。

---

## 6. §5.4 §8 に記録した実測コスト 5 項目のサマリ

slotmap §5.3 §8 で確立した記入義務を踏襲し、本セッション完走時に §5.4 §8 に
記入完了:

| # | 項目 | 実測値 / 判定 |
|---|---|---|
| A | **326-330 byte-identity 維持時間（累計）** | **約 110 分** (326-327 約 30 分 / 328 約 25 分 / 329 約 25 分 / 330 約 30 分) |
| B | **5 本立て diff 10 ペア検証時間** | **自動 (PowerShell Compare-Object): 589 ms (平均 59 ms/ペア)**、手動相当 約 10-15 分。自動は手動の約 1000 倍速 |
| C | **意図差分テーブルから漏れた予期せぬ差分** | **なし** (4 種類の意図差分のみで完結、grep + diff で確認) |
| D | **(b) refactor 主観的圧力 (1-5 スケール)** | **3 / 5** (前回 §5.3 §8 値 2/5 から +1 上昇、CI 化で対処可能と判断) |
| E | **CI 化スクリプト導入時期判断** | **次セッション (整備期) で最優先タスクとして導入推奨**。`scripts/check_template_sync.py` 新設、実装規模 1-2 時間 |

→ この実測値が **形式 #6 入口での再評価を「推定」ではなく「実測」に基づく
判断**にする基礎データとなる。

---

## 7. 編集 / 新規作成ファイル一覧 (最終的な行数差分)

セッション開始時 (329 完了時の状態) と完了時の差分。

| # | ファイル | 種別 | 開始行数 | 終了行数 | Δ 行数 | 開始 bytes | 終了 bytes | Δ bytes |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `schema/problem.schema.json` | 既存編集 | 164 | **194** | **+30** | 6,113 | **7,294** | +1,181 |
| 2 | `scripts/render.py` | 既存編集 | 224 | **242** | **+18** | 8,582 | **9,516** | +934 |
| 3 | `scripts/validate_structure.py` | 既存編集 | 1,000 | **1,022** | **+22** | 43,043 | **44,356** | +1,313 |
| 4 | `scripts/validate_content.py` | 既存編集 | 254 | **276** | **+22** | 8,281 | **9,391** | +1,110 |
| 5 | `templates/KTX_template.html` | 触らず | 2,788 | 2,788 | 0 | 95,298 | 95,298 | 0 |
| 6 | `templates/KTX_template_ox4.html` | 触らず | 2,751 | 2,751 | 0 | 93,882 | 93,882 | 0 |
| 7 | `templates/KTX_template_msel5.html` | 触らず | 2,754 | 2,754 | 0 | 93,835 | 93,835 | 0 |
| 8 | `templates/KTX_template_sc5.html` | 触らず | 2,770 | 2,770 | 0 | 94,478 | 94,478 | 0 |
| 9 | `templates/KTX_template_comb5.html` | **新規作成** | — | **2,778** | **+2,778** | — | **94,894** | +94,894 |
| 10 | `templates/KTX_template_slotmap.md` | 既存編集 (§5.4 追記 + §5.4 §8 実測値記入) | 920 | **1,284** | **+364** | 54,784 | **79,182** | +24,398 |
| 11 | `problems/326.json` | 触らず | 57 | 57 | 0 | 6,574 | 6,574 | 0 |
| 12 | `problems/327.json` | 触らず | 49 | 49 | 0 | 5,121 | 5,121 | 0 |
| 13 | `problems/328.json` | 触らず | 57 | 57 | 0 | 5,223 | 5,223 | 0 |
| 14 | `problems/329.json` | 触らず | 72 | 72 | 0 | 5,554 | 5,554 | 0 |
| 15 | `problems/330.json` | **新規作成** | — | **65** | **+65** | — | **7,783** | +7,783 |
| 16 | `docs/session-330-completion.md` | **新規作成** (本書) | — | — | — | — | — | — |

### 触らなかったファイル（明示的に温存）

- `canonical/KTX301.html` (構造参考として固定、slotmap §5.4 §4 の原則)
- `templates/KTX_template.html` / `_ox4.html` / `_msel5.html` / `_sc5.html` (5 本立て防壁の温存)
- `problems/326.json` / `327.json` / `328.json` / `329.json` (既存形式の互換性証跡)
- `outputs/000_TX/001_刑法/刑TX326-330.html` (本書作成時点では再生成しない)
- `docs/ox4-design-investigation-326-330-session.md` / `docs/session-326-327-completion.md` / `docs/session-328-completion.md` / `docs/session-329-completion.md` (先行セッション記録)

---

## 8. 残タスク（次セッション以降の候補）

`inputs/tx-pdfs/` の 5 件 (326-330) **すべて完走**。`331.pdf` 以降は現時点で
存在せず、次セッションは **整備期** として以下を実施推奨:

| 案件 | slotmap §候補 | 内容 |
|---|---|---|
| **CI 化スクリプト** | （新設） | `scripts/check_template_sync.py` 新規実装。5 本立て diff 10 ペアを Python で機械検証 |
| S14 PART D drill-block 実装 | §5.5 | drill-block 12 件構造を JSON schema + template に追加 |
| S17 professor sub-card 実装 | §5.6 | 各 choice-section に教授解説 sub-card 追加 |
| S51 ktx301-canon feature-tag | §5.7 | footer-spec への小修正 |
| S71-AP33 文言調整 | §5.8 | ox-grid 系 (326/327) の answer-instruction を canonical 準拠に |
| CRIME_SIGNATURES 拡張 | §5.9 | 信書隠匿罪 / 毀棄罪 / 損壊罪等の追加、横断的辞書整備 |

---

## 9. 本セッションシリーズ全体の総括 (326-330 全 5 形式完走)

### 9.1 量的成果

| 指標 | セッション開始時 (326 着手前) | セッション完了時 (330 完走後) | 増分 / 倍率 |
|---|---|---|---|
| **完走問題数** | 0 | **5 (326-330)** | +5 |
| **サポート形式数** | 0 | **5 形式** (ox-grid-5 / ox-grid-4 / multi-select-5 / single-choice-5 / combination-5) | +5 |
| **template 本数** | 1 (KTX_template.html、初期は無設計) | **5 本立て** | +4 |
| **schema 行数** | 121 | **194** | +73 行 (+60%) |
| **render.py 行数** | 187 | **242** | +55 行 (+29%) |
| **validate_structure.py 行数** | 944 | **1,022** | +78 行 (+8%) |
| **validate_content.py 行数** | 248 | **276** | +28 行 (+11%) |
| **新規 template ファイル** | 0 | **4 ファイル** (ox4 / msel5 / sc5 / comb5) | +4 |
| **slotmap.md 行数** | 451 | **1,284** | **+833 行 (約 2.85 倍に成長)** |
| **problems/*.json (新規作成)** | 0 | **5 ファイル** (326 / 327 / 328 / 329 / 330) | +5 |
| **docs/ ファイル数** | 0 | **5 ファイル** (調査 1 + 完了報告 4) | +5 |
| **生成 HTML** | 0 | **5 ファイル**、合計約 515 KB | +5 |

### 9.2 質的成果

#### 1. **byte-identity の連鎖確立**
326 → 327 → 328 → 329 → 330 と進む各セッションで、前段までの HTML が SHA256 ハッシュ
レベルで完全に維持される設計を実現。**5 段階の連鎖で 1 度も regression が発生せず**、
defensive infrastructure として機能。

#### 2. **設計→実装の事前合意パターン定着**
各形式で以下の 5 段プロセスが繰り返し検証され、**再現性のある手順として確立**:
1. PDF 設計調査 (`docs/` または session 内で実施)
2. slotmap §5.N 追記（設計合意）
3. 実装一括 (schema → validator → template → render → JSON → 完走)
4. 完了報告 (`docs/session-N-completion.md`)
5. 引き継ぎポイント明示

#### 3. **schema oneOf による型多様性吸収**
answer フィールドで **3 形式 (string / int[] / integer)** が後方互換維持で共存:
- ox-grid 系: string ("12222", "2212")
- multi-select 系: int[] ([1, 4])
- single-choice / combination 系: integer (2, 3)

将来 ranking / fill-in 形式が来ても oneOf に第 4/第 5 ブランチ追加で対応可能。

#### 4. **future-proof helper の継続活用**
本シリーズで導入した以下の helper はフェーズを通して再利用、各セッションで
追加変更ゼロで動作:
- `_format_answer` (render.py): string / int[] / integer の 3 形式正規化
- `_derive_cv_info` (validate_structure.py): ox-grid / multi / single mode 自動判定
- `LABEL_TO_LETTER` (render.py): カナ ア〜コ + 算用数字 1〜5 の混成マッピング

#### 5. **v8.11.3 multi/single インフラの完全活用**
- CSS の 3 Type 対応 (single / multi / ox-grid) → **CSS 追加変更ゼロで 5 形式に対応**
- JS の `type === 'single'` / `'multi'` / `'ox-grid'` 分岐 → **JS 追加変更ゼロ**
- S71-AP33 canonical 文言 3 種 (single / multi / ox-grid) → **328/329/330 で WARN 消滅**
- S73-AP35 自動判定 (cv 形式 → data-answer-type) → **追加変更ゼロ**

#### 6. **意図差分テーブルによる diff 管理**
5 本立て template でも diff 10 ペアすべて意図差分テーブル (slotmap §5.N §3) で
説明可能。**実測 589 ms** で機械検証が完結し、CI 化への土台が固まった。

### 9.3 次セッションへの引き継ぎ事項 (最優先 5 項目)

1. **`scripts/check_template_sync.py` 新規実装 (CI 化、最優先)**
   - slotmap §5.4 §8 で根拠付きで宣言済。
   - 実装規模: Python で 10 ペア Compare-Object 相当、意図差分テーブル参照、所要 1-2 時間。
   - 効果: 手動 10-15 分 → 自動 1 秒未満、約 1000 倍速。
   - 形式 #6 着手前に完了させることで、6 本立て (15 ペア) でも CI 化前提なら持続可能。

2. **WARN 4 系統消化 (slotmap §5.5-§5.8)**
   - §5.5: S14 PART D drill-block 12 件実装
   - §5.6: S17 professor sub-card × choice-section
   - §5.7: S51 ktx301-canon feature-tag 追加
   - §5.8: S71-AP33 ox-grid 系 (326/327) の文言調整 → **全 5 形式で S71-AP33 完全消滅**

3. **CRIME_SIGNATURES 拡張 (slotmap §5.9)**
   - 信書隠匿罪 / 毀棄罪 / 損壊罪 を CRIME_SIGNATURES に正式登録。
   - 329/330 で `allowed_cross_refs` に書いた「信書隠匿罪」が自動的に有効化される。
   - 横断的な辞書整備として実施。

4. **形式 #6 入口準備**
   - schema enum に残存する `"single-choice"` / `"ranking"` / `"fill-in"` の実装決定が
     来た時点で、slotmap §5.4 §7 の AND 条件 ①/② を再判定。
   - 条件充足時は (b) refactor 発火、CI 化完了後ならば移行コスト最小化可能。

5. **331 以降の問題追加への備え**
   - `inputs/tx-pdfs/` に新規 PDF が来た時点で:
     - 既存 5 形式のいずれかに収まるなら → 当該 template + JSON 作成のみ
     - 新形式が必要なら → slotmap §5.10+ で設計調査 → 実装パターン継続
   - 326-330 シリーズで確立したパターンを次以降にも適用可能。

### 9.4 撤退ポイント: 6 本立て到達時に (b) refactor 発火条件再判定

- 6 本立て (diff 15 ペア) は **手動レビューでは限界**。CI 化前提でも管理負荷が
  指数的に増える可能性あり。
- slotmap §5.4 §7 で正式宣言された **AND 条件 ①/②** を、6 本目に到達する直前で
  必ず再判定する。
- 条件充足時は **(b) refactor (partial 合成 or JS 動的レンダリング) へ移行**。
  CI 化 + WARN 消化の整備期を経た上での移行なら円滑。
- 移行候補:
  - (a) JS による行動的レンダリング (ランタイムで PART A / A-2 を DOM 構築)
  - (b) JSON 駆動の partial 合成 (Jinja2 等テンプレエンジン、formats ごとの partial)
- 本シリーズ (326-330) では 5 本立てまでで実用可能と実証。6 本目を作るかどうかが
  次の分岐点。

### 9.5 シリーズ全体の所感メモ（将来参照用）

- **v8.11.3 multi/single インフラの先見性** が本シリーズ最大の追い風だった。
  CSS / JS / validator が 3 Type 対応で事前整備されていたため、新形式追加のたびに
  CSS/JS 追加変更ゼロで対応可能だった。今後も新形式が来た場合、まず既存インフラで
  対応可能か確認することが重要。
- **byte-identity 連鎖の維持** は defensive design の好例。1 件目から 5 件目まで
  累積 110 分の検証時間で 5 形式すべてを ノンデグレーションで進められた。次以降も
  この連鎖を維持する価値が高い。
- **slotmap.md の成長** (451 → 1,284 行、約 2.85 倍) は設計合意の蓄積。次セッションでは
  slotmap 自体の整理 (例: §5 配下を別ファイル化、§5.1/§5.2 の階層揺れ調整等) も
  検討余地あり。
- **5 本立て diff 10 ペア = 589 ms** という実測値は、CI 化の費用対効果を強く支持。
  次セッションで CI 化を最優先実装することで、6 本立てに到達しても持続可能な保守
  体制が確立する。
- **PDF 抽出ベースの JSON 起こし** は学説型問題 (329 / 330) でも問題なく対応可能。
  case_citations 空配列の運用も確立 (positive check 影響なし、explanation 内に学説
  参照を含める形)。
- 326-330 全 5 形式の完走をもって、本シリーズ「初期テスト 5 問」の目標達成。次は
  整備期 → 331 以降への拡張、または別シリーズ (KEN / MIN 等の他科目) への展開を
  視野に。
