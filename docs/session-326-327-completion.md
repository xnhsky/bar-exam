# セッション完了記録 — 326 (ox-grid-5) / 327 (ox-grid-4) 完走

## メタ情報

- **作成日**: 2026-05-18
- **対象セッション**: 326〜330 一括処理セッション
- **本書の位置づけ**: 同セッションの設計調査記録 `docs/ox4-design-investigation-326-330-session.md` の続編として、実装完走と検証結果を記録する完了報告書。

---

## 1. 完走した問題

| ID | 形式 | crime | source | answer | パターン | HTML パス | 検証結果 |
|---|---|---|---|---|---|---|---|
| **326** | ox-grid-5 | 盗品等罪 | H29-12 (司法試験) | `12222` | P2 (セージブラリー) | `outputs/000_TX/刑TX/刑TX326.html` (105,258 bytes) | 全 3 段 PASS |
| **327** | ox-grid-4 | 盗品等罪 | 予備R2-10 (予備独自問題) | `2212` | P3 (ラベンダードーン) | `outputs/000_TX/刑TX/刑TX327.html` (101,699 bytes) | 全 3 段 PASS |

### 3 段検証 (render → validate_structure → validate_content) 結果

| 検証段 | 326 | 327 |
|---|---|---|
| render | ✅ exit 0 | ✅ exit 0 |
| validate_structure | ✅ ERROR 0、WARN 8 件 | ✅ ERROR 0、WARN 7 件 |
| validate_content | ✅ PASS (negative + positive 共にクリーン) | ✅ PASS (同) |

---

## 2. §5 案件で消化したもの

### 2.1 S16 schema 経由化 (answer_explanation フィールド)

**経緯**: 構造検証 S16 (`answer-area に data-explanation がない`) を解消する際、template にハードコードで埋め込む暫定案を経て、本セッション中盤に schema 経由の本格対応に格上げした。

**消化内容**:

- `schema/problem.schema.json` に `answer_explanation` フィールドを追加 (型 `string`, `minLength: 1`, `required` に追加)。
- `templates/KTX_template.html` の `data-explanation` 属性を `{{ANSWER_EXPLANATION}}` placeholder 化。
- `scripts/render.py` の `build_slot_dict` に `ANSWER_EXPLANATION` slot を追加。
- `problems/326.json` に `"answer_explanation": "解答および各記述の正誤判定"` を追加 (AP-37 抵触回避のため句点なし)。
- 同じ基本句を `problems/327.json` でも採用。

**結果**:

- S16 ERROR は **schema → JSON → template → render の正規ルート**で消滅。
- AP-37 (data-explanation 先頭の正解値リテラル禁止) にも非抵触。
- 326 と 327 で同一フィールドを再利用可能なので将来の問題でもコピー可能。

### 2.2 ox-grid-N 形式分岐 (slotmap §5.1 として確立)

**経緯**: 327 の選択肢が 4 件であることが判明し、現行 template (5 件ハードコード) では render fail することが分かった。設計調査を経て slotmap.md §5.1 として方針を凍結し、本セッション末尾で一括実装した。

**消化内容**:

- `templates/KTX_template_slotmap.md` に §5.1「ox-grid-N 形式分岐 (R-1: ox-grid-4 対応)」を追記し、設計合意を文書化。
- `schema/problem.schema.json` の `instruction_type.enum` に `"ox-grid-4"` を追加 (add only、既存 `ox-grid-5` は破壊せず)。
- `schema/problem.schema.json` の `choices.minItems` を `1 → 4`、`maxItems` を `10 → 5` に変更 (ox-grid-N の N ∈ {4, 5} 凍結に整合)。
- `templates/KTX_template_ox4.html` を新規作成 (`KTX_template.html` から派生、E 系を機械削除)。
- `scripts/render.py` に `TEMPLATE_PATHS` dict を導入、`instruction_type` から template を選択する分岐を実装 (デフォルトは既存 `KTX_template.html` で 326 への regression を防御)。
- `scripts/validate_structure.py` の S12 / S17 を動的化 (helper `_derive_expected_choice_count` を導入、cv 桁数から N を導出、三者一致 sanity check を S12 拡張として組込)。

**結果**:

- 326 (ox-grid-5) は **HTML がバイト単位で前回と完全一致** (ハッシュ `E4790D25A4486F7DCC255111C7AEA0E6E6C61E24F26DFF6D9F9C026E9094FF53`) を保ち、regression なし。
- 327 (ox-grid-4) は 3 段検証すべて PASS。
- slotmap §5.1 §7 で定義したリスク R6 / R7 / R8 / R9 / R10 / R11 / R12 すべて対応済み (詳細は `docs/ox4-design-investigation-326-330-session.md` §F)。

---

## 3. §5 案件で保留中のもの

326 / 327 双方で常駐している WARN は以下の 4 系統 (合計 8 件 / 7 件)。本セッションでは触らず保留。次フェーズで個別案件として扱う。

| WARN ID | 内容 | 326 件数 | 327 件数 | 想定対応 |
|---|---|---|---|---|
| **S14** | drill-block 数 = 0 (期待値: 12) | 1 | 1 | PART D スタブを実装する案件。JSON schema に drill 系フィールド追加、template の PART D スタブを drill-block 12 件構造に拡張。slotmap §5.2 候補 |
| **S17×N** | choice-* の sub-card 欠落: `['professor']` | 5 (choice-1〜5) | 4 (choice-1〜4) | 各 choice-section に `professor` sub-card (教授の解説) を追加する案件。JSON schema に `choices[*].professor` フィールド追加、template の choice-section 構造拡張。slotmap §5.3 候補 |
| **S51** | footer-spec 必須 feature-tag 欠落: `['ktx301-canon']` | 1 | 1 | footer-spec に `ktx301-canon` feature-tag を追加する案件。template のみの修正で済む。slotmap §5.4 候補 (小規模) |
| **S71-AP33** | `<p class="answer-instruction">` が canonical 文言と相違 | 1 | 1 | answer-instruction の文言を canonical 準拠に揃える案件。template のみの修正で済む。slotmap §5.5 候補 (小規模) |

**いずれも構造検証 S レベルでは ERROR ではなく WARN 扱いのため、現在の 3 段検証パイプラインは PASS している。**

---

## 4. 326 HTML byte-identical 検証成立

ox-grid-4 対応の実装が **既存 326 経路に一切の副作用を与えていない**ことを、HTML のバイト単位比較で実証した。

### 検証手順

1. ox-grid-4 実装着手前の `outputs/000_TX/刑TX/刑TX326.html` を `.bak` として退避。
2. schema / render.py / validate_structure.py / 新 template を投入後、`python scripts/render.py 326` を再実行。
3. 新旧 HTML の SHA256 ハッシュを比較。

### 結果

- **旧ハッシュ**: `E4790D25A4486F7DCC255111C7AEA0E6E6C61E24F26DFF6D9F9C026E9094FF53`
- **新ハッシュ**: `E4790D25A4486F7DCC255111C7AEA0E6E6C61E24F26DFF6D9F9C026E9094FF53`
- **判定**: identical = True
- **使用テンプレ**: `KTX_template.html` (既存パス、`TEMPLATE_PATHS.get(instruction_type, TEMPLATE_PATH)` のデフォルト経路)
- **validate_structure**: ERROR 0、WARN 8 件 (前回と完全同一内訳: S14 / S17×5 / S51 / S71-AP33)
- **validate_content**: PASS

これにより、render.py のデフォルト分岐 (未マッチ・未指定 → 既存 KTX_template.html) が正しく機能していることが客観的に証明された (slotmap §5.1 §5 R8 リスク回避の実証)。

---

## 5. 編集 / 新規作成ファイル一覧 (最終的な行数差分)

セッション開始時点と完了時点の差分。326.json の作成も本セッション内で行ったため含む。

| # | ファイル | 種別 | 最終行数 | 最終 bytes | 主な変更内容 |
|---|---|---|---:|---:|---|
| 1 | `schema/problem.schema.json` | 既存編集 | 121 | 4,222 | `answer_explanation` フィールド追加 + required に追加 (S16 schema 経由化)。`instruction_type.enum` に `"ox-grid-4"` 追加。`answer.description` に 4 桁例追加。`choices.minItems` 1→4、`maxItems` 10→5。 |
| 2 | `scripts/render.py` | 既存編集 | 187 | 6,766 | `build_slot_dict` に `ANSWER_EXPLANATION` slot 追加。`TEMPLATE_PATHS` dict 追加、`main` を template 選択分岐 + 未指定時 WARN + ログに template 名と instruction_type 明示。 |
| 3 | `scripts/validate_structure.py` | 既存編集 | 944 | 39,915 | helper `_derive_expected_choice_count` を追加 (cv 桁数から N 導出、既定 5)。S12 を動的化 + 三者一致 sanity check (choice-section 数 / ox-row 数 / cv 桁数)。S17 を range(1, N+1) 化。 |
| 4 | `scripts/validate_content.py` | 触らず | 248 | 7,886 | 変更なし (choices ループは既に動的) |
| 5 | `templates/KTX_template.html` | 既存編集 | 2,788 | 95,298 | PART C スタブの c-2〜c-6 を追加 (S13 解消)。`data-explanation` 属性を `{{ANSWER_EXPLANATION}}` placeholder 化 (S16 schema 経由化)。 |
| 6 | `templates/KTX_template_ox4.html` | **新規作成** | 2,751 | 93,882 | `KTX_template.html` から派生。TOC オ削除 / PART A 問題文 E 行削除 / A-2 ox-row E 削除 / PART B 記述オ section 削除 / choice-4 nav forward `↓共通根拠` / A-3 back-nav `←記述エ` / コメント文言更新。差分は -37 行 / -1,416 bytes。 |
| 7 | `templates/KTX_template_slotmap.md` | 既存編集 | 451 | 25,940 | §5.1「ox-grid-N 形式分岐 (R-1: ox-grid-4 対応)」を追記 (背景 / 決定事項 1〜7 / 将来の一般化 / AP-37 抵触回避ガイド / crime 表記揺れの取り扱い)。+128 行 / +6,269 bytes。 |
| 8 | `problems/326.json` | **新規作成** | 57 | 6,574 | 326.pdf からゼロベース抽出。ox-grid-5、ア〜オ 5 件、answer "12222"、crime "盗品等罪"、override_pattern "P2"。`answer_explanation` 追加。 |
| 9 | `problems/327.json` | **新規作成** | 49 | 5,121 | 327.pdf からゼロベース抽出。ox-grid-4、ア〜エ 4 件、answer "2212"、crime "盗品等罪"、source "予備R2-10"、override_pattern "P3"。`answer_explanation` 採用。 |
| 10 | `docs/ox4-design-investigation-326-330-session.md` | **新規作成** | 372 | 32,810 | A〜F の設計調査全文 + R1〜R12 + 総括。次セッションでの実装の前提資料。 |
| 11 | `docs/session-326-327-completion.md` | **新規作成** (本書) | — | — | 本セッションの完了報告。実装ファイル一覧、検証結果、保留事項、残タスク。 |

### 触らなかったファイル

- `canonical/KTX301.html` (構造参考として固定、slotmap §5.1 §4 の原則)
- `CLAUDE.md` (プロジェクト指示書、本セッション中変更不要)

---

## 6. 残タスク (次セッション以降の候補)

`inputs/tx-pdfs/` の以下 3 件は本セッションでは skip 済み。形式が異なるため、それぞれ slotmap §5.2 / §5.3 / §5.4 として個別設計予定。

| ID | 形式 (実体) | crime | source | 正答率 | 想定 §5 サブセクション | 主な設計課題 |
|---|---|---|---|---|---|---|
| **328** | **multi-select-5** (1〜5 から誤っているもの **2 個選択**) | 盗品等罪 (盗品等に関する罪) | R7-19 | 56% | **slotmap §5.2** 候補 | answer フィールドの複数値表現 (現在 `^[12]+$` は ○× 用)、template の answer-area type が `data-answer-type="multi"`、`selection-counter` 必要 |
| **329** | **single-choice 番号型** (1〜5 から誤っているもの **1 個選択**、A/B/C 見解付き) | 信書隠匿罪 / 器物損壊罪 | H20-16 | 89% | **slotmap §5.3** 候補 | 設問の【見解】A/B/C を保持するフィールド (例: `views: [...]`)、5 番号 single-choice の template (ア〜オ → 1〜5)、answer は単一桁 |
| **330** | **combination-5** (ア〜オの記述 + 1〜5 の組合せ選択肢) | 毀棄罪及び損壊罪 | 予備H23-10 | 84% | **slotmap §5.4** 候補 | 設問の【見解】A/B 学説 + 5 つの組合せ選択肢 (アイ / アオ / イウ / ウエ / エオ) を保持するフィールド、canonical KTX301 と同型構造 |

### 推奨次セッション着手順

1. **328 の調査と §5.2 設計** (multi-select-5)。 schema の `answer` pattern 拡張が必要。
2. **329 の調査と §5.3 設計** (single-choice 番号型)。 ア〜オ → 1〜5 への label 系統変更が必要。
3. **330 の調査と §5.4 設計** (combination-5)。 canonical KTX301 と同型のため、構造参考が活用できる初の問題タイプ。
4. 各 §5.N の合意後、本セッションと同様に schema → validate → template → render → JSON → 3 段検証完走の順で実装。
5. WARN 4 系統 (S14 / S17 professor / S51 / S71-AP33) は別の slotmap §5.5+ 案件として個別に消化。

---

## 7. 本セッションの所感メモ (将来参照用)

- **S16 schema 経由化** は当初「最小修正」として data-explanation 属性のハードコードに倒したが、ユーザー指示で本格対応に格上げした流れが好例。**最小修正 → 設計昇格** のパターンが、暫定対応の証跡を残したまま正規ルートに乗せ替える優れた方法だった。
- **slotmap §5.1 の事前調査 → 設計合意 → 実装** の流れにより、ox-grid-4 対応の実装は迷いなく一発で完走した。次セッションの 328 / 329 / 330 も同様のパターンで進めるのが安全。
- **326 HTML の byte-identical 維持** は、render.py の `TEMPLATE_PATHS.get(instruction_type, TEMPLATE_PATH)` のデフォルト経路設計が効いた。新機能を入れる際の「既存パス凍結」設計の有効性を実証。
- 327 で WARN が S17×5 から S17×4 に減ったのは仕様通り。動的化された S17 が choice-1〜N をループするようになったため。
