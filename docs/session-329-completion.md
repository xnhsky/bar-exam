# セッション完了記録 — 329 (single-choice-5) 完走

## メタ情報

- **作成日**: 2026-05-18
- **対象セッション**: 329 単独実装セッション（326〜330 連続作業の 4 回目）
- **本書の位置づけ**: 同シリーズの先行セッション記録
  - `docs/ox4-design-investigation-326-330-session.md` (調査・初期 ox-grid-4 設計)
  - `docs/session-326-327-completion.md` (326 ox-grid-5 / 327 ox-grid-4 完了)
  - `docs/session-328-completion.md` (328 multi-select-5 完了)

  に続く第 4 弾。single-choice-5 形式（【見解】slot 新概念を含む）の実装完走と
  検証結果を記録する完了報告書。

---

## 1. 完走した問題

| ID | 形式 | crime | source | answer | パターン | HTML パス | 検証結果 |
|---|---|---|---|---|---|---|---|
| **329** | single-choice-5 | 器物損壊罪 (+ allowed_cross_refs: ["信書隠匿罪"]) | H20-16 (司法試験 平成20年第16問) | `2` (integer 単体) | P1 (ローズシャンブル、正答率 89%) | `outputs/000_TX/001_刑法/刑TX329.html` (100,939 bytes) | 全 3 段 PASS |

### 3 段検証 (render → validate_structure → validate_content) 結果

| 検証段 | 329 |
|---|---|
| render | ✅ exit 0、`template=KTX_template_sc5.html`、`instruction_type=single-choice-5`、未置換 slot 0 |
| validate_structure | ✅ ERROR 0、WARN **7 件** (S14 / S17×5 / S51。**S71-AP33 は消滅**、S78 views 検査 PASS) |
| validate_content | ✅ PASS (negative + positive 共にクリーン、`answer=2` の HTML 出現 + 各 choice の stem/explanation/case_citations 全照合 PASS) |

**S71-AP33 が 328 に続き 329 でも消滅**: single 用 canonical 文言「選択肢を選んで「解答を表示」を押してください。」を template に採用したため (S71-AP33 既登録パターン `^選択肢を選んで「解答を表示」を押してください。$` に整合)。slotmap §5.3 §3 で意図差分として明示した設計が機能している証拠。

**新規 S78 views-section 検査が正常動作**: views-section 1 件、view-block 3 件、view-label `A`/`B`/`C` を grep で目視確認済。slotmap §5.3 §8「固定 3 件方式」の設計通り。

---

## 2. 326 / 327 / 328 三重 regression: HTML byte-identical (SHA256 一致) 確認結果

single-choice-5 実装が **既存 ox-grid 系および multi-select 系の経路に一切の副作用を
与えていない**ことを、326 / 327 / 328 すべての HTML バイト単位比較で実証した。

### 検証手順

1. 実装着手前の `outputs/000_TX/001_刑法/刑TX326.html` / `刑TX327.html` / `刑TX328.html` を
   `.bak` として退避。
2. schema / render.py / validate_structure.py / 新 sc5 template を投入後、3 件を再 render。
3. 新旧 HTML の SHA256 ハッシュを比較。

### 結果

| 問題 | 旧 SHA256 | 新 SHA256 | identical | 使用テンプレ |
|---|---|---|---|---|
| **326** | `E4790D25A4486F7DCC255111C7AEA0E6E6C61E24F26DFF6D9F9C026E9094FF53` | `E4790D25A4486F7DCC255111C7AEA0E6E6C61E24F26DFF6D9F9C026E9094FF53` | **True** | `KTX_template.html` (デフォルト経路、`TEMPLATE_PATHS.get(instruction_type, TEMPLATE_PATH)`) |
| **327** | `1AC6D19B23BA488B4002E3986FE23A24E66BE11CC8AA24B8C5D4A68A95B5CD48` | `1AC6D19B23BA488B4002E3986FE23A24E66BE11CC8AA24B8C5D4A68A95B5CD48` | **True** | `KTX_template_ox4.html` |
| **328** | `1839599B3D7B23F8F64A58891CBCABCE117C9D46EB11559A710094F470160CE7` | `1839599B3D7B23F8F64A58891CBCABCE117C9D46EB11559A710094F470160CE7` | **True** | `KTX_template_msel5.html` |

### validate 結果（前回からの差分）

| 問題 | ERROR | WARN | 内訳 | 前回からの差分 |
|---|---|---|---|---|
| 326 | 0 | 8 | S14 / S17×5 / S51 / S71-AP33 | **完全同一** |
| 327 | 0 | 7 | S14 / S17×4 / S51 / S71-AP33 | **完全同一** |
| 328 | 0 | 7 | S14 / S17×5 / S51 | **完全同一** |

→ render.py の `TEMPLATE_PATHS.get(instruction_type, TEMPLATE_PATH)` デフォルト経路、
`_format_answer()` の 3 ブランチ分岐、`_derive_cv_info()` の mode 別判定、
`build_slot_dict` の【見解】slot 供給ロジック（views 未指定 → 空文字、既存 template に
placeholder なし → 無害）がすべて正しく既存挙動を温存することを実証。

---

## 3. §5 案件で消化したもの

### 3.1 schema oneOf 第 3 ブランチ（integer 単体）

**経緯**: 326/327 は string answer、328 は array answer に対応済みだったが、
single-choice-5 (329) は **integer 単体の正解番号**（例: `2`）を表現する必要があり、
既存 oneOf 構造を破壊しない設計が要件となった。

**消化内容**:

- `schema/problem.schema.json` の `answer.oneOf` に第 3 ブランチを追加:
  - 第 1 ブランチ: `string` + `pattern: ^[12]+$` (ox-grid 系、既存)
  - 第 2 ブランチ: `array` of integer (1〜5)、`uniqueItems: true` (multi-select 系、既存)
  - **第 3 ブランチ**: `integer` (minimum 1, maximum 5) (single-choice 系、新規)
- 326.json (string) / 327.json (string) / 328.json (array) はそれぞれ第 1/第 1/第 2
  ブランチで引き続き valid。**三重 regression byte-identical で実証**。
- `instruction_type.enum` に `"single-choice-5"` を追加 (add only)。

**結果**:
- 3 種類の answer 形式（string / array / integer）が `oneOf` で共存。後方互換完全維持。
- 将来 ranking / fill-in 等が来ても、oneOf に第 4/第 5 ブランチを追加すれば対応可能。

### 3.2 views フィールド追加 (single-choice 系のみ、後方互換維持)

**消化内容**:

- `schema/problem.schema.json` に `$defs.View` を新規定義:
  - `{ label: enum ["A", "B", "C"], body: string (minLength 10) }`
  - `additionalProperties: false`
- `properties.views`:
  - `type: array, items: { $ref: "#/$defs/View" }, minItems: 3, maxItems: 3`
  - **`required` 配列に追加しない**（optional として実装）
- views が未指定の場合、render.py 側で空文字を埋めるため ox-grid / multi-select 系
  template の `{{VIEW_*_*}}` placeholder が存在しない状況下では無害。
- 326.json / 327.json / 328.json は views 未指定で引き続き valid。

**結果**:
- 329.json は views 3 件を明示し、schema valid。
- 既存 3 問題への影響ゼロ（regression byte-identical で実証）。

### 3.3 【見解】slot 固定 3 件方式 (A/B/C VIEW_X_LABEL/BODY)

**経緯**: 329 PDF には【見解】A/B/C の 3 学説が提示され、各記述がそれら見解の
適用例として書かれている。slotmap §5.3 §8 で「動的 HTML 単一 slot 案を不採用、
固定 3 件個別 slot を採用」と決定済み。

**消化内容**:

- `scripts/render.py` の `build_slot_dict` に **【見解】slot 6 個展開ロジック**を追加:
  - JSON の `views` 配列を label でディクショナリ化（"A"→view A, "B"→view B, "C"→view C）
  - 6 個の slot を構築: `VIEW_A_LABEL` / `VIEW_A_BODY` / `VIEW_B_LABEL` / `VIEW_B_BODY` / `VIEW_C_LABEL` / `VIEW_C_BODY`
  - views が未指定の場合は空文字を入れる（後方互換確保）
- `templates/KTX_template_sc5.html` の PART A 内に **【見解】section** を新規追加:
  - `<section class="views-section" id="part-a-views">` + 3 つの `<div class="view-block">`
  - 各 view-block は `<span class="view-label">{{VIEW_X_LABEL}}</span>` と
    `<p class="view-body">{{VIEW_X_BODY}}</p>` を持つ
- `scripts/validate_structure.py` に **S78 views-section 検査** を新設:
  - views-section が存在する HTML では view-block が固定 3 件であることを ERROR チェック
  - 各 view-block の view-label / view-body 存在を WARN チェック
  - views-section が存在しない HTML (326/327/328) では何もしない（無害）

**結果**:
- 329 で views A/B/C が template に正しく展開（grep で 3 件すべて検出）。
- S78 検査 PASS。WARN/ERROR ゼロ。
- 動的 HTML 単一 slot 方式を不採用とした slotmap §5.3 §8 の判断が機能：
  HTML 構造が template 上で可視、validate も簡潔。

### 3.4 validate_structure に cv 形式分岐の single-choice-5 組み込み

**消化内容**:

- 既存 `_derive_cv_info` helper は `('single', 5, 1)` を返す対応が **§5.2 で既に
  future-proof 化済み**。helper 自体の追加変更不要。
- `check_S12_part_b_choices` の三者一致 sanity check に `single` mode 分岐を追加:
  - single mode: choice-section 数 == answer-slot 数 == 5 (template 固定)、K=1 は
    cv が単一整数文字列で保証される。
- 既存 ox-grid / multi 分岐は完全に温存。
- S73-AP35 (cv 形式と data-answer-type の自動判定整合) は既に single 自動判定済、
  S71-AP33 (answer-instruction canonical 文言) は既に single 用パターン許容済 (v8.11.3)、
  変更不要。

**結果**:
- 326/327/328 への regression なし（既存分岐は完全温存）。
- 329 で single mode の三者一致検査が正常動作。

### 3.5 slotmap §5.3 新設

- 直前のターン（実装着手前）で `templates/KTX_template_slotmap.md` に §5.3
  「single-choice-N 形式分岐 + 【見解】slot 導入 (R-3)」を追記済。
- 章立て: 背景 / 決定事項 1〜8 / 【見解】slot の実装方式 / 将来の一般化 /
  AP-37 抵触回避ガイド / crime 表記揺れの取り扱い。
- **(b) refactor 発火条件を本書 §8 に正式宣言**:
  - AND 条件: ①330 PDF が既存 4 本で収まらない、②形式 #6 以降 2 件以上 confirmed
- **330 入口で実測マージコストを記録する義務**を明示。

**結果**:
- slotmap.md は 640 → 920 行（+280 行 / +17,282 bytes）に拡張。
- 設計合意ベースで実装が迷いなく進み、本セッションで全 PASS。

---

## 4. §5 案件で保留中のもの

326 / 327 / 328 / 329 共通で常駐している WARN は以下の 4 系統。本セッションでも触らず保留。

| WARN ID | 内容 | 326 件数 | 327 件数 | 328 件数 | 329 件数 | 想定対応 |
|---|---|---|---|---|---|---|
| **S14** | drill-block 数 = 0 (期待値: 12) | 1 | 1 | 1 | 1 | slotmap §5.5 候補。PART D スタブを実装する案件 |
| **S17×N** | choice-* の sub-card 欠落: `['professor']` | 5 | 4 | 5 | 5 | slotmap §5.6 候補。各 choice-section に professor sub-card を追加 |
| **S51** | footer-spec 必須 feature-tag 欠落: `['ktx301-canon']` | 1 | 1 | 1 | 1 | slotmap §5.7 候補。template の footer-spec のみの修正 |
| **S71-AP33** | `<p class="answer-instruction">` が canonical 文言と相違 | 1 | 1 | **0** | **0** | **326/327 のみ残存**。slotmap §5.8 候補（次項参照） |

### §5.8 候補: ox-grid 系 answer-instruction 文言を canonical に揃える単発案件

S71-AP33 は 328 / 329 では消滅し、**ox-grid 系の 326 / 327 のみで残存**する状態に
収束した。slotmap.md §5.8 を新設する案件として以下を提案：

- **対象**: `KTX_template.html` (ox-grid-5) と `KTX_template_ox4.html` (ox-grid-4) の
  `<p class="answer-instruction">` 文言を、v8.11.3 ox-grid canonical 文言
  `^各記述に「1（正）」または「2（誤）」を選んで「解答を表示」を押してください。$`
  に揃える。
- **現状文言**: 「各記述について「正しい (1)」か「誤っている (2)」を選んでください。」
- **修正後文言**: 「各記述に「1（正）」または「2（誤）」を選んで「解答を表示」を押してください。」
- **波及**: ox-grid-5 と ox-grid-4 の 2 template を同期して修正、両者で
  HTML byte-identity は **明示的に破壊**される（意図的）。
- **規模**: 約 2 行 × 2 ファイル + slotmap §5.8 追記。極小規模。
- **タイミング**: 326/327/328/329 すべて完走後、または 330 完走後の整備期で消化。

**いずれも構造検証 S レベルでは ERROR ではなく WARN 扱いのため、現在の 3 段検証
パイプラインは全件 PASS している。**

---

## 5. 4 本立て template の同期義務（引き続き義務化）

本セッションで `templates/` 配下の v8.11.6 系 template ファイルは **4 本立て**に
拡張された：

| ファイル | 用途 | 行数 | bytes | byte-identity 確立済 |
|---|---|---|---|---|
| `KTX_template.html` | ox-grid-5 (326 等) | 2,788 | 95,298 | ✅ |
| `KTX_template_ox4.html` | ox-grid-4 (327 等) | 2,751 | 93,882 | ✅ |
| `KTX_template_msel5.html` | multi-select-5 (328 等) | 2,754 | 93,835 | ✅ |
| `KTX_template_sc5.html` | **single-choice-5 (329 等)** | **2,770** | **94,478** | ✅ (本セッションで確立) |

### 同期義務（slotmap §5.3 §8 を継承）

- **同期対象** (4 本で byte-level 一致を維持): HEAD / CSS 全体 / JS 全体 /
  marker-legend / PART C スタブ (c-1〜c-7) / PART D スタブ /
  A-3 共通根拠スタブ / footer-spec の構造。
- **意図差分対象** (各 template 固有):
  - TOC アンカー (カナ / 数字)
  - PART A 問題文行数とラベル系統
  - **【見解】section の有無** (sc5 のみ)
  - A-2 解答エリア構造 (ox-grid / multi / single)
  - PART B choice-section 数およびラベル
  - sec-nav の表記

### diff ペア数の状況

- 3 本立て (§5.2 完了時): 3 ペア — 手動で許容
- **4 本立て (本セッション、§5.3 完了時): 6 ペア — 手動境界に到達**
- 5 本立て (将来 §5.4 完了時): 10 ペア — CI 化必須

### 限界宣言の維持

`docs/session-328-completion.md` §5 で宣言した **「3 本立ては実用限界、4 本目以降は
別アプローチへ移行する」** という方針は、本セッションで 4 本目を追加することで
**境界を 1 段階拡張**した形になった。slotmap §5.3 §8 で「(b) refactor 発火条件」
を正式宣言済みで、330 入口での評価が次の判断ポイント。

### 330 入口で実測マージコストを記録する義務 (本セッション分の実測値)

slotmap §5.3 §8 で宣言された記入義務に基づき、本セッションでの実測値を記録:

```
### §5.3 完了時点の同期実測（実測値）
- 326 / 327 / 328 / 329 の byte-identity 維持に要した時間:
    約 25 分（baseline backup + 3 件再 render + SHA256 照合 + validate 結果比較）
- 4 本立て diff 6 ペアの手動 / 自動検証時間:
    本セッションでは byte-identity 一括検証で代替 (12 分相当の手動 diff コストは未計上)
- §5.3 §3 意図差分テーブルから漏れた予期せぬ差分:
    なし（template 編集は意図差分 4 種類のみで完結、grep 検証で確認）
- (b) refactor を発火すべきと感じた主観的圧力 (1-5 スケール):
    2 / 5 (4 本立ては手動検証範囲内。5 本立てになると 10 ペアで限界)
```

---

## 6. 編集 / 新規作成ファイル一覧 (最終的な行数差分)

セッション開始時 (328 完了時の状態) と完了時の差分。

| # | ファイル | 種別 | 開始行数 | 終了行数 | Δ 行数 | 開始 bytes | 終了 bytes | Δ bytes |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `schema/problem.schema.json` | 既存編集 | 134 | **164** | **+30** | 4,965 | **6,113** | +1,148 |
| 2 | `scripts/render.py` | 既存編集 | 209 | **224** | **+15** | 7,851 | **8,582** | +731 |
| 3 | `scripts/validate_structure.py` | 既存編集 | 973 | **1,000** | **+27** | 41,395 | **43,043** | +1,648 |
| 4 | `scripts/validate_content.py` | 触らず | 254 | 254 | 0 | 8,281 | 8,281 | 0 |
| 5 | `templates/KTX_template.html` | 触らず | 2,788 | 2,788 | 0 | 95,298 | 95,298 | 0 |
| 6 | `templates/KTX_template_ox4.html` | 触らず | 2,751 | 2,751 | 0 | 93,882 | 93,882 | 0 |
| 7 | `templates/KTX_template_msel5.html` | 触らず | 2,754 | 2,754 | 0 | 93,835 | 93,835 | 0 |
| 8 | `templates/KTX_template_sc5.html` | **新規作成** | — | **2,770** | **+2,770** | — | **94,478** | +94,478 |
| 9 | `templates/KTX_template_slotmap.md` | 既存編集 (§5.3 追記) | 640 | **920** | **+280** | 37,502 | **54,784** | +17,282 |
| 10 | `problems/326.json` | 触らず | 57 | 57 | 0 | 6,574 | 6,574 | 0 |
| 11 | `problems/327.json` | 触らず | 49 | 49 | 0 | 5,121 | 5,121 | 0 |
| 12 | `problems/328.json` | 触らず | 57 | 57 | 0 | 5,223 | 5,223 | 0 |
| 13 | `problems/329.json` | **新規作成** | — | **72** | **+72** | — | **5,554** | +5,554 |
| 14 | `docs/session-329-completion.md` | **新規作成** (本書) | — | — | — | — | — | — |

### 触らなかったファイル（明示的に温存）

- `canonical/KTX301.html` (構造参考として固定、slotmap §5.3 §4 の原則)
- `templates/KTX_template.html` / `_ox4.html` / `_msel5.html` (4 本立て防壁の温存)
- `problems/326.json` / `327.json` / `328.json` (既存形式の互換性証跡)
- `outputs/000_TX/001_刑法/刑TX326.html` / `327.html` / `328.html` / `329.html` (本書作成時点では再生成しない)
- `docs/ox4-design-investigation-326-330-session.md` / `docs/session-326-327-completion.md` / `docs/session-328-completion.md` (先行セッション記録)

---

## 7. 残タスク（次セッション以降の候補）

`inputs/tx-pdfs/` の以下 1 件は本セッションでも skip 済み。slotmap §5.4 として
個別設計予定。

| ID | 形式 (実体) | crime | source | 正答率 | 想定 §5 サブセクション | 主な設計課題 |
|---|---|---|---|---|---|---|
| **330** | **combination-5** (ア〜オの記述 + 1〜5 の組合せ選択肢) | 毀棄罪及び損壊罪 | 予備H23-10 | 84% | **slotmap §5.4** 候補 | (1) canonical KTX301 と**構造的に同型**、(2) ア〜オの 5 記述に個別 verdict + 最終解答は 1〜5 の組合せ番号（single）、(3) PART A の **二層構造** (ox-grid 表示 + single 番号ボタン)、(4) 新概念 `combinations` フィールド (label と member 配列) |

---

## 8. 引き継ぎポイント

### 8.1 330 (combination-5) への引き継ぎ

#### 8.1.1 構造特性

- **330 は canonical KTX301 と構造的に同型**。canonical 内部に既に「ア〜オの 5 記述 +
  5 つの組合せ選択肢を 1〜5 の単一選択で答える」UI が実装されているため、
  **canonical 自体が「最も近い実装 reference」となる初の問題**。
- ただし PATCH §1 / slotmap §5.1〜§5.3 §4 の原則「canonical の本文・解説を
  コピーしない」は引き続き適用。**構造参考は OK、内容流用は NG**。

#### 8.1.2 template ベース選定の判断点

330 の template ベースとして以下のいずれが適切か、§5.4 設計時に判断する：

- **(α) `KTX_template.html` 派生**: ox-grid-5 構造 (ア〜オ ○×) + 組合せ選択肢を
  追加する派生。PART A の ox-grid 部分が既存、A-2 を組合せ番号ボタン化。
- **(β) `KTX_template_sc5.html` 派生**: single-choice-5 構造（1〜5 番号ボタン）+
  ア〜オの ○× 表示を追加する派生。A-2 が既存 single 構造で活用、PART A に
  ox-grid 風表示を追加。
- **(γ) 5 本目独立 template**: 上記いずれにも依存せず、canonical KTX301 を構造
  参考に新規作成。

  → **§5.4 設計調査時に定量比較**（行数差分、同期義務違反リスク、保守コスト）。

#### 8.1.3 新概念 `combinations` フィールド

330 の核心は「ア〜オの組合せ」表現。JSON で以下の構造を提案：

```json
"combinations": [
  {"label": "1", "members": ["ア", "イ"]},
  {"label": "2", "members": ["ア", "オ"]},
  {"label": "3", "members": ["イ", "ウ"]},
  {"label": "4", "members": ["ウ", "エ"]},
  {"label": "5", "members": ["エ", "オ"]}
]
```

- schema に `$defs.Combination` を新規追加（`{label, members[]}`）。
- `properties.combinations` は **conditional**：`instruction_type === "combination-5"`
  時のみ意味を持つ optional フィールド。
- template には `{{COMBO_1_LABEL}}` / `{{COMBO_1_MEMBERS}}` 〜 `{{COMBO_5_LABEL}}` /
  `{{COMBO_5_MEMBERS}}` の 10 個の slot で展開。

#### 8.1.4 PART A の二層構造

- **第 1 層**: ア〜オの 5 記述（個別 verdict 持ち）— ox-grid 表示と同型、しかし
  ○× ボタンは無し（PART B で verdict を解説する形）。
- **第 2 層**: 1〜5 の組合せ選択肢（single-choice の番号ボタン）— A-2 解答エリアに
  配置、`data-answer-type="single"` で 5 ボタン。
- 両層を併存させるか、PART A は ア〜オ 記述だけ、A-2 で 1〜5 組合せボタンを
  表示する 2 セクション構成にするか、§5.4 設計時に決定。

### 8.2 future-proof helper の継続利用

本セッションで確認した通り、以下の helper は **追加変更不要**で 330 でも再利用可能:

- `LABEL_TO_LETTER` (render.py): ア〜コ + 1〜5 の併用済み。330 の ア〜オ (既存) +
  1〜5 組合せラベル (既存) の両方を含む可能性、追加変更不要。
- `_format_answer` (render.py): string / array / integer の 3 形式に対応済。
  330 の answer は integer 単体（例: `3`）の見込みで既存対応で OK。
- `_derive_cv_info` (validate_structure.py): single mode 判定済。330 が
  `data-answer-type="single"` ならそのまま動作。
- `oneOf` answer schema (problem.schema.json): 第 3 ブランチ integer で 330 に対応済。

### 8.3 共通の引き継ぎ事項

- **5 本目 template を作るか refactor へ移行するかの判断は slotmap §5.4 設計時**。
  本書 §5 の限界宣言と slotmap §5.3 §8 の (b) refactor 発火条件を起点に評価する。
  本セッションで記録した「主観的圧力 2/5」を出発点に、330 設計調査でさらに上昇するか
  観測する。
- **CI 化スクリプトの導入**：4 本立て (本セッション後) で diff 6 ペアの自動検証を
  仕組み化する価値が、5 本立てになる前に高まっている。次セッション前に CI 化の
  着手も検討。
- **既存 v8.11.3 single インフラ**（CSS / JS / S71-AP33 single canonical 文言 /
  S73-AP35 single 自動判定）は本セッションで完全に活用済。330 の組合せ型 single も
  同インフラで対応可能な見込み。
- **§5.8 候補（ox-grid 系 answer-instruction 文言調整）** は単発・極小規模なので、
  330 完走後の整備期に消化推奨。326/327 の S71-AP33 が解消されると、
  全 5 問題で同 WARN が消滅し、WARN 4 系統 → 3 系統に縮小する。

---

## 9. 本セッションの所感メモ（将来参照用）

- **v8.11.3 single インフラの存在** が今回も最大の追い風だった。CSS / JS /
  S71-AP33 single canonical 文言 / S73-AP35 single 自動判定がすべて事前に
  整備されていたため、template 派生 + schema 拡張 + 【見解】slot 追加のみで完走。
  CSS / JS の追加変更ゼロ。
- **【見解】slot の固定 3 件方式** が功を奏した。HTML 構造が template 上で可視で、
  S78 検査も簡潔に書け、render.py の slot 供給ロジックも明快。動的 HTML 単一 slot
  案を不採用とした slotmap §5.3 §8 の判断は正しかった。
- **三重 regression が完全 byte-identical** で確立。326 / 327 / 328 のいずれも
  HTML が 1 byte も変わらず、新機能が既存経路を完全に避けて実装できることを実証。
  この defensive design pattern は本シリーズの最大の財産。
- **S71-AP33 の自然消滅は 2 件目** (328 / 329 で消滅、326 / 327 のみ残存)。
  ox-grid 用 canonical 文言の調整 (§5.8 候補) で全件消滅まであと一歩。
- **4 本立て diff 6 ペアは手動検証範囲内** だが、5 本立て (10 ペア) では限界。
  330 入口で (b) refactor 発火条件を厳密に評価する必要あり。slotmap §5.3 §8 で
  正式宣言した発火条件 AND 2 つを満たすかどうかが分岐点。
- 設計→実装→完走→引き継ぎの 4 段流れがシリーズで定着。次の 330 でも同パターンを
  踏襲する。
