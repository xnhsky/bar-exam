# セッション完了記録 — 328 (multi-select-5) 完走

## メタ情報

- **作成日**: 2026-05-18
- **対象セッション**: 328 単独実装セッション（326〜330 連続作業の 3 回目）
- **本書の位置づけ**: 同シリーズの先行セッション記録
  - `docs/ox4-design-investigation-326-330-session.md` (調査)
  - `docs/session-326-327-completion.md` (326/327 完了)

  に続く第 3 弾。multi-select-5 形式の実装完走と検証結果を記録する完了報告書。

---

## 1. 完走した問題

| ID | 形式 | crime | source | answer | パターン | HTML パス | 検証結果 |
|---|---|---|---|---|---|---|---|
| **328** | multi-select-5 | 盗品等罪 | R7-19 (司法試験 令和7年第19問) | `[1, 4]` (int 配列) | P2 (セージブラリー) | `outputs/000_TX/001_刑法/刑TX328.html` (101,151 bytes) | 全 3 段 PASS |

### 3 段検証 (render → validate_structure → validate_content) 結果

| 検証段 | 328 |
|---|---|
| render | ✅ exit 0、`template=KTX_template_msel5.html`、`instruction_type=multi-select-5`、未置換 slot 0 |
| validate_structure | ✅ ERROR 0、WARN **7 件** (S14 / S17×5 / S51。**S71-AP33 は消滅**) |
| validate_content | ✅ PASS (negative + positive 共にクリーン、`answer="1,4"` の HTML 出現 + 各 choice の stem/explanation/case_citations 全照合 PASS) |

**S71-AP33 が初めて消滅した点が特筆**: 326/327 では ox-grid 用 canonical 文言と一致しないため WARN だったが、328 は v8.11.3 multi canonical 文言 `^選択肢を\d+個選んで「解答を表示」を押してください。$` に厳密に整合した文言を template に採用したため、初めて S71-AP33 WARN がクリアされた。slotmap §5.2 §2 の設計が機能している証拠。

---

## 2. 326 / 327 二重 regression: HTML byte-identical 確認結果

multi-select-5 実装が **既存 ox-grid 経路に一切の副作用を与えていない**ことを、326 と 327 双方の HTML バイト単位比較で実証した。

### 検証手順

1. 実装着手前の `outputs/000_TX/001_刑法/刑TX326.html` と `刑TX327.html` を `.bak` として退避。
2. schema / render.py / validate_structure.py / validate_content.py / 新 msel5 template を投入後、両問題を再 render。
3. 新旧 HTML の SHA256 ハッシュを比較。

### 結果

| 問題 | 旧 SHA256 | 新 SHA256 | identical | 使用テンプレ |
|---|---|---|---|---|
| **326** | `E4790D25A4486F7DCC255111C7AEA0E6E6C61E24F26DFF6D9F9C026E9094FF53` | `E4790D25A4486F7DCC255111C7AEA0E6E6C61E24F26DFF6D9F9C026E9094FF53` | **True** | `KTX_template.html` (デフォルト経路、`TEMPLATE_PATHS.get(instruction_type, TEMPLATE_PATH)`) |
| **327** | `1AC6D19B23BA488B4002E3986FE23A24E66BE11CC8AA24B8C5D4A68A95B5CD48` | `1AC6D19B23BA488B4002E3986FE23A24E66BE11CC8AA24B8C5D4A68A95B5CD48` | **True** | `KTX_template_ox4.html` |

### validate 結果（前回からの差分）

| 問題 | ERROR | WARN | 内訳 | 前回からの差分 |
|---|---|---|---|---|
| 326 | 0 | 8 | S14 / S17×5 / S51 / S71-AP33 | **完全同一** |
| 327 | 0 | 7 | S14 / S17×4 / S51 / S71-AP33 | **完全同一** |
| validate_content | — | — | 326: PASS / 327: PASS | **完全同一** |

→ render.py の `TEMPLATE_PATHS.get(instruction_type, TEMPLATE_PATH)` デフォルト経路と、`_format_answer()` の string ブランチ ("12222"/"2212" → そのまま通過)、`_derive_cv_info()` の ox-grid ブランチ (`^[12]{2,}$` 判定) がすべて正しく既存挙動を温存することを実証。

---

## 3. §5 案件で消化したもの

### 3.1 schema oneOf 型 answer 対応

**経緯**: 326/327 は ox-grid 系で answer が固定長 ○× 列 ("12222"/"2212") の string だったが、multi-select-5 は正解番号集合 ([1, 4]) を表現する必要があり、string 既存パスを破壊しない設計が要件となった。

**消化内容**:

- `schema/problem.schema.json` の `answer` フィールドを `oneOf` 分岐に変更:
  - 第 1 ブランチ: `string` + `pattern: ^[12]+$` (既存 ox-grid 系、後方互換維持)
  - 第 2 ブランチ: `array` of integer (1〜5)、`minItems: 1`、`maxItems: 5`、`uniqueItems: true` (新規 multi-select 系)
- 326.json / 327.json の string answer は引き続き第 1 ブランチで valid。**326 / 327 の HTML byte-identical で実証**。

**結果**:
- schema 上の型多様性を `oneOf` で吸収。今後 single integer（329 候補）や他形式が増えても、第 3 / 第 4 ブランチを追加すれば対応可能。
- `uniqueItems: true` により、`[1, 1]` や `[3, 1]` 重複・降順といった不正な配列を schema レベルで弾く。

### 3.2 multi-select-5 形式分岐 (slotmap §5.2 として確立)

**経緯**: 328 の選択肢が「1〜5 の番号型」「複数選択」「複合 UI (answer-row + answer-slot×5 + selection-counter)」で、現行 template (5 件 ox-grid ハードコード) では構造的に対応不可能。設計調査を経て slotmap §5.2 として方針を凍結し、本セッションで一括実装した。

**消化内容**:

- `templates/KTX_template_slotmap.md` に §5.2「multi-select-N 形式分岐 (R-2: multi-select-5 対応)」を追記 (+189 行 / +11,562 bytes)。背景・決定事項 8 項目・将来一般化・AP-37 ガイド・answer 表記正規化・crime/source 表記揺れの全 12 セクションを記載。
- `schema/problem.schema.json` の `instruction_type.enum` に `"multi-select-5"` を追加 (add only)、`choice.label.enum` に算用数字 `"1"〜"5"` を追加 (既存カナ ア〜コ は維持)。
- `templates/KTX_template_msel5.html` を新規作成 (`KTX_template.html` から派生)。差分は **7 種類** (TOC ラベル / PART A 見出しコメント / PART A sec-nav / A-2 解答エリア全面 multi 化 / A-2 h3 + answer-instruction 文言 / PART B 見出し + コメント + nav / A-3 back-nav) に限定。HEAD/CSS/JS/PART C/D/A-3/footer-spec は base と byte-level 同期。
- `scripts/render.py` の `TEMPLATE_PATHS` dict に `"multi-select-5"` を追加。`LABEL_TO_LETTER` に算用数字マッピング (`"1"→A` 〜 `"5"→E`) を追加。
- `scripts/validate_structure.py` の S12 を mode 別三者一致 sanity check に拡張。`_derive_cv_info` helper で mode/N/K を一括導出。
- `scripts/validate_content.py` の positive check で `answer` 配列を `","連結文字列` に正規化。

**結果**:
- 328 の 3 段検証すべて PASS。
- 326 / 327 の HTML が **byte-identical** で完全維持。regression なし。
- 既存 v8.11.3 multi インフラ (CSS の `.answer-area[data-answer-type="multi"]` ルール / JS の 3 Type 対応 / S73-AP35 の自動判定 / S71-AP33 multi canonical 文言) を **再利用** することで、CSS/JS の追加変更ゼロで対応完了。

### 3.3 `_format_answer` / `_derive_cv_info` の 3 形式 future-proof 化

**経緯**: 329 (single-choice 番号型、answer は integer 単体) / 330 (combination-5、answer は integer 単体) も視野に入れた汎用設計が要件となった。

**消化内容**:

- `scripts/render.py` の `_format_answer(answer)` helper:
  - `list` → `","` 連結文字列 ("1,4")
  - `string` → そのまま ("12222")
  - その他 (int / None など) → `str()` で文字列化 ("3" / "")
- `scripts/validate_structure.py` の `_derive_cv_info(soup)` helper:
  - cv に `","` 含有 → `('multi', 5, K)` (K はカンマ区切り要素数)
  - cv が `^[12]{2,}$` → `('ox-grid', len(cv), len(cv))`
  - cv が `^\d+$` (single integer) → `('single', 5, 1)` ← **329 / 330 で再利用可能**
  - その他 → `('unknown', 5, 5)`

**結果**:
- 329 (answer = single int) / 330 (answer = single int "3") のいずれも、既存 helper が **追加実装なし**で正しく動作可能な見込み。
- 既存 `_derive_expected_choice_count` は `_derive_cv_info` の thin wrapper として API 互換を維持。

### 3.4 slotmap §5.2 の新設

- 既存 §5.1 (ox-grid-4) と同型の章立てを採用。
- **三 template 同期義務違反の検出方法**を §8 に明記 (diff 二重照合 / 部分 diff / 想定外差分の対処 / CI 化候補)。
- 将来一般化セクションで **N 個 template ファイル爆発の閾値**を明示 (本フェーズ 3 ファイル、329/330 で 4 件目を作るかの判断は §5.3 設計時)。
- AP-37 抵触回避ガイドと answer 表記正規化ガイドを multi 用に追加。

---

## 4. §5 案件で保留中のもの

326 / 327 / 328 共通で常駐している WARN は以下の 4 系統。本セッションでは触らず保留。

| WARN ID | 内容 | 326 件数 | 327 件数 | 328 件数 | 想定対応 |
|---|---|---|---|---|---|
| **S14** | drill-block 数 = 0 (期待値: 12) | 1 | 1 | 1 | slotmap §5.5 候補。PART D スタブを実装する案件 |
| **S17×N** | choice-* の sub-card 欠落: `['professor']` | 5 | 4 | 5 | slotmap §5.6 候補。各 choice-section に professor sub-card を追加 |
| **S51** | footer-spec 必須 feature-tag 欠落: `['ktx301-canon']` | 1 | 1 | 1 | slotmap §5.7 候補。template の footer-spec のみの修正 |
| **S71-AP33** | `<p class="answer-instruction">` が canonical 文言と相違 | 1 | 1 | **0**! | 326/327 のみ残存。**328 では multi canonical 文言を採用したため消滅**。326/327 の文言を canonical 準拠に揃える単発案件として slotmap §5.8 候補（または ox-grid 用 canonical 文言を将来再定義する案件） |

**いずれも構造検証 S レベルでは ERROR ではなく WARN 扱いのため、現在の 3 段検証パイプラインは全件 PASS している。**

S71-AP33 が 328 で消滅したことは、ox-grid 系 (326/327) の answer-instruction 文言を canonical 準拠に直す道筋を実証した。次のフェーズで取り組む価値あり。

---

## 5. 三 template 同期義務の限界宣言

本セッションで `templates/` 配下の v8.11.6 系 template ファイルは **3 本立て**となった：

| ファイル | 用途 | 行数 | bytes |
|---|---|---|---|
| `KTX_template.html` | ox-grid-5 (326 等) | 2,788 | 95,298 |
| `KTX_template_ox4.html` | ox-grid-4 (327 等) | 2,751 | 93,882 |
| `KTX_template_msel5.html` | multi-select-5 (328 等) | 2,754 | 93,835 |

### 同期義務 (slotmap §5.2 §8)

- **同期対象** (3 本で byte-level 一致を維持): HEAD / CSS 全体 / JS 全体 / marker-legend / PART C スタブ (c-1〜c-7) / PART D スタブ / A-3 共通根拠スタブ / footer-spec の構造。
- **意図差分対象** (各 template 固有): TOC アンカー / PART A 問題文行数とラベル系統 / A-2 解答エリア構造 / PART B choice-section 数およびラベル / nav の表記。

### 限界宣言

**3 本立ては保守限界。4 本目以降は別アプローチへ移行する。**

#### 理由

1. **diff 検証コストの線形増加**: 3 本立ては 3 ペア (3 通り) の diff、4 本立ては 6 ペア、5 本立ては 10 ペアで検証が必要。CI 化しないと人力では維持不能。
2. **共通部分の重複コスト**: HEAD/CSS/JS/PART C/D/A-3/footer は 3 本で約 2,700 行 × 3 = 8,100 行の重複。4 本立てなら 10,800 行、5 本立てなら 13,500 行。修正時の同期義務違反リスクが急増。
3. **設計意図の伝達コスト**: 「どの差分が意図的で、どこが同期対象か」を毎回 slotmap で明示する必要があり、§5.3 / §5.4 と増えていくと参照コストも増える。

#### 4 件目以降の対処方針

slotmap §5.3 / §5.4 設計時に以下の選択肢を比較検討し、判断する：

- **(a) JS による行動的レンダリング**: 単一 template に PART A / A-2 を空のコンテナとして配置し、ランタイムで `instruction_type` ベースに DOM 構築。
- **(b) JSON 駆動の partial 合成**: render.py を拡張し、PART A / A-2 部分を formatごとに partial HTML として持ち、ループ合成。Jinja2 等テンプレエンジンへの移行も視野。
- **(c) 既存 template の分岐パラメータ化**: 同じ template 内で `<!-- if-instruction-type="..." -->` のような独自ディレクティブを CSS/JS で解釈。— **slotmap §5.2 §2 で既に否定済み** (validate fail / DOM ノイズ / 自動化スクリプト誤動作の 3 重害)。

本セッションでは (c) を採用しない方針を維持。次フェーズで (a) または (b) のいずれかへ移行することになる可能性が高い。

---

## 6. 編集 / 新規作成ファイル一覧 (最終的な行数差分)

セッション開始時 (326/327 完了時の状態) と完了時の差分。

| # | ファイル | 種別 | 開始行数 | 終了行数 | Δ 行数 | 開始 bytes | 終了 bytes | Δ bytes |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `schema/problem.schema.json` | 既存編集 | 121 | **134** | **+13** | 4,222 | **4,965** | +743 |
| 2 | `scripts/render.py` | 既存編集 | 187 | **209** | **+22** | 6,766 | **7,851** | +1,085 |
| 3 | `scripts/validate_structure.py` | 既存編集 | 944 | **973** | **+29** | 39,915 | **41,395** | +1,480 |
| 4 | `scripts/validate_content.py` | 既存編集 | 248 | **254** | **+6** | 7,886 | **8,281** | +395 |
| 5 | `templates/KTX_template.html` | 触らず | 2,788 | 2,788 | 0 | 95,298 | 95,298 | 0 |
| 6 | `templates/KTX_template_ox4.html` | 触らず | 2,751 | 2,751 | 0 | 93,882 | 93,882 | 0 |
| 7 | `templates/KTX_template_msel5.html` | **新規作成** | — | **2,754** | **+2,754** | — | **93,835** | +93,835 |
| 8 | `templates/KTX_template_slotmap.md` | 既存編集 | 451 | **640** | **+189** | 25,940 | **37,502** | +11,562 |
| 9 | `problems/326.json` | 触らず | 57 | 57 | 0 | 6,574 | 6,574 | 0 |
| 10 | `problems/327.json` | 触らず | 49 | 49 | 0 | 5,121 | 5,121 | 0 |
| 11 | `problems/328.json` | **新規作成** | — | **57** | **+57** | — | **5,223** | +5,223 |
| 12 | `docs/session-328-completion.md` | **新規作成** (本書) | — | — | — | — | — | — |

### 触らなかったファイル（明示的に温存）

- `canonical/KTX301.html` (構造参考として固定、slotmap §5.2 §4 の原則)
- `templates/KTX_template.html` / `KTX_template_ox4.html` (デフォルト経路と ox-grid-4 経路の防壁)
- `problems/326.json` / `problems/327.json` (既存形式の互換性証跡)
- `outputs/000_TX/001_刑法/刑TX326.html` / `刑TX327.html` / `刑TX328.html` (本書作成時点では再生成しない)
- `docs/ox4-design-investigation-326-330-session.md` / `docs/session-326-327-completion.md` (先行セッションの記録)

---

## 7. 残タスク（次セッション以降の候補）

`inputs/tx-pdfs/` の以下 2 件は本セッションでも skip 済み。それぞれ slotmap §5.3 / §5.4 として個別設計予定。

| ID | 形式 (実体) | crime | source | 正答率 | 想定 §5 サブセクション | 主な設計課題 |
|---|---|---|---|---|---|---|
| **329** | **single-choice-5 番号型** (1〜5 から誤っているもの **1 個選択**、【見解】A/B/C 付き) | 信書隠匿罪 / 器物損壊罪 | H20-16 | 89% | **slotmap §5.3** 候補 | (1) `data-answer-type="single"` で msel5 派生だが selection-counter 削除、(2) **【見解】slot 新概念**（A/B/C の各見解本文を JSON で保持）、(3) answer は integer 単体（型 oneOf 第 3 ブランチ要検討） |
| **330** | **combination-5** (ア〜オの記述 + 1〜5 の組合せ選択肢) | 毀棄罪及び損壊罪 | 予備H23-10 | 84% | **slotmap §5.4** 候補 | (1) canonical KTX301 と**同型**、(2) 各記述に個別 verdict あり + 最終解答は単一の組合せ番号、(3) **二層構造** (5 記述 + 5 組合せ選択肢) を JSON でどう表現するか、(4) 新規 template が必要かを設計時に判断 |

---

## 8. 引き継ぎポイント

### 8.1 329 (single-choice-5 番号型) への引き継ぎ

- **template 設計の起点**: `KTX_template_msel5.html` から派生して以下を変更
  - `data-answer-type="multi"` → `data-answer-type="single"`
  - `<p class="selection-counter">` 削除
  - `<p class="answer-instruction">` を single canonical 文言（`^選択肢を選んで「解答を表示」を押してください。$`）に変更
  - PART A 問題文の上に **【見解】A/B/C** を表示する section が追加で必要
- **新概念**: **【見解】slot**
  - JSON フィールド候補: `views: [{label: "A", body: "..."}, ...]`
  - template 上の placeholder: `{{VIEWS_HTML}}` または個別 `{{VIEW_A_BODY}}` 等
  - slot 化方法は §5.3 設計時に詳細化（render.py に views 専用の loop ロジックを入れるか、HTML 文字列を JSON 側で組み立てるか）
- **schema 拡張**:
  - `instruction_type.enum` に `"single-choice-5"` を追加
  - `answer` に第 3 ブランチ (integer) を `oneOf` で追加（または既存 string ブランチで `^[1-5]$` をカバーする方法も検討）
  - `views: [{label, body}]` の構造定義を新規追加
- **render.py**: `_format_answer` の integer ブランチは既に対応済み (str(int) で "3" 等になる)。`_derive_cv_info` も single 形式を判定済み。**追加実装は views 系のみ**。
- **slotmap §5.3 候補**として設計調査が必要。本書 §5 の限界宣言の通り、**4 件目 template を作るかどうかが最大の設計判断**。

### 8.2 330 (combination-5) への引き継ぎ

- **canonical KTX301 と同型** のため、初の「canonical 構造をリファレンスとして直接活用できる問題」。
- **template 選択肢**:
  - (i) 新規 `KTX_template_comb5.html` を作る（4 件目、本書 §5 の限界宣言と相反）
  - (ii) 既存 `KTX_template.html` を派生せず、canonical KTX301 構造を踏襲して **新規 template を作らない**（PART A の組合せ選択肢部分を slot 化する手も）
  - (iii) 一般化リファクタ (JS 動的レンダリングまたは partial 合成) へ移行する初の試行案件として位置付ける
- **二層構造の表現**:
  - 第 1 層: ア〜オの記述（個別 verdict 持ち）
  - 第 2 層: 1〜5 の組合せ選択肢（例: 「アイ」「アオ」「イウ」「ウエ」「エオ」）
  - JSON 設計候補: `choices` 配列に 5 件（既存）+ `combinations: [{label: "1", set: ["ア","イ"]}, ...]` 新規フィールド
- **schema 拡張**:
  - `instruction_type.enum` に `"combination-5"` を追加
  - `answer` は string "3" または integer 3 (oneOf で対応可能)
  - `combinations` 構造定義を新規追加
- **slotmap §5.4 候補**として設計調査が必要。

### 8.3 共通の引き継ぎ事項

- **4th / 5th template を作るか、既存テンプレに分岐パラメータで吸収するかの設計判断は slotmap §5.3 設計フェーズで決定する**。本書 §5 の限界宣言を起点に、(a)/(b) のいずれかへ移行する判断を、329 着手前に必ず行う。
- 既存 v8.11.3 multi インフラ (CSS / JS / S73-AP35 / S71-AP33 multi canonical / answer-num-multi CSS) は **3 Type 対応** (single / multi / ox-grid) なので、**329 (single) は CSS/JS の追加変更なし**で対応可能な見込み。330 (組合せ single) も同様。
- `_format_answer` / `_derive_cv_info` は **future-proof**：integer 単体・配列・文字列の 3 形式すべてに対応済み。329 / 330 の answer フォーマットがどれであっても再利用できる。
- **二重 regression 検証パターン**（本セッションで確立した「baseline backup → 実装 → SHA256 ハッシュ照合」手順）を 329 / 330 でも継続採用。次回は 326/327/328 の **三重 regression** になる。

---

## 9. 本セッションの所感メモ（将来参照用）

- **v8.11.3 multi インフラの既存** が最大の追い風だった。CSS / JS / S73-AP35 / S71-AP33 multi canonical 文言がすべて事前に整備されていたため、本セッションでは schema + template + render + validator の最小修正のみで対応完了。
- **`oneOf` 分岐による answer 型多様化** が成功したことで、今後 single integer / array / string の 3 形式が混在する環境を schema レベルで安全に扱える基盤ができた。後方互換も完全維持できることを 326/327 byte-identical で実証。
- **三 template 同期義務は 3 本で実用限界**。本書 §5 で明示した「4 件目以降は別アプローチ」の境界線を、次セッション (329) 着手前に必ず決定する必要がある。
- **slotmap §5.2 §8 の「同期義務違反の検出方法」を機械化（CI 化）する**価値が、本書時点で 3 本になったことで急浮上した。次セッションで CI スクリプトの導入も検討。
- 328 で **S71-AP33 が初めて消滅**したことは、ox-grid 用 (326/327) の同 WARN も canonical 文言調整で消せる道筋を示した。slotmap §5.8 として小規模案件化できる。
- 本セッションは「設計調査 → 設計合意 → 一括実装 → 完走 → 完了報告」の流れが ox-grid-4 セッションと同型で進み、迷いなく完走した。同パターンを 329 / 330 でも踏襲する。
