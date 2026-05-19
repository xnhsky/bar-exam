# Session: 6 科目 (KEN/MIN/SYO/MINS/KEIS/GSE) 展開 — Phase A-D 完走 (3 件採用 / 3 件保留)

## サマリ

- **日時**: 2026-05-19
- **目的**: 刑法 326-330 (KEI) 完了後、残り 6 科目 (KEN/MIN/SYO/MINS/KEIS/GSE) を展開する。
- **進捗**: 全 4 Phase 完走。Phase C は当初前提 (1 PDF = 多問題、1 ページ = 1 問題) と実 PDF 構造が乖離していたため、xnh と協議のうえ **選択肢 A (1 PDF = 1 問題で 3 件採用、3 件保留)** に方針変更して完走。
- **採用**: `MIN001` / `SYO001` / `MINS001` の 3 件、全件 CP6 PASS (各 WARN [S26] のみ)
- **保留**: `KEN` / `KEIS` / `GSE` の 3 件、未対応形式 (fill-in × 2、ox-grid-3 + combination-8 × 1)
- **(b) refactor 発火**: 既存 5 形式テンプレで収まらない案件が 3 件 confirmed、AND 条件 ①② 共に充足 → 次セッションで refactor 検討すべき

---

## Phase A: 基盤改修 — 完走 (CP1-CP5 全通過)

### CP 通過状況

| CP | 内容 | 結果 |
|---|---|---|
| CP1 | schema 変更は subject field 追加のみ | ✅ |
| CP2 | render.py は subject パラメータ化のみ、既存ロジック不変 | ✅ |
| CP3 | validate_content.py は SIGNATURE_REGISTRY 二段化 + 後方互換 alias | ✅ |
| CP4 | 326-330 全件 byte-identical 維持 (SHA256 で照合) | ✅ |
| CP5 | check_template_sync.py exit 0 維持 | ✅ |

### 編集 / 新規作成ファイル

| ファイル | 種別 | 概要 |
|---|---|---|
| `schema/problem.schema.json` | edit | `subject` field 追加 (enum 7 値、default=KEI、required 不変) |
| `scripts/render.py` | edit | `SUBJECT_TO_JP` / `resolve_arg` / `get_output_path` 追加、JSON `subject` 優先ロジック |
| `scripts/validate_content.py` | edit | `SIGNATURE_REGISTRY` 二段化、`CRIME_SIGNATURES` alias、`negative_check` 引数化 |
| `scripts/pdf_to_png.py` | new | pymupdf で PDF を 1 ページ 1 PNG に展開する補助スクリプト |
| `_sha256_baseline.json` | new | 326-330 SHA256 baseline (CP4 照合用) |

### SHA256 evidence (CP4 担保、3 回照合一致)

```
326 BEF153E033A09A21E9C7E88D496BAAA0AA1F5BEEEC3E2259E9D836D9DFDEE039
327 9C30BC5EA89F5BFF3D4F242011A4A0AC89E03B7E1494E4C0317B9F2D7EBD12C2
328 8AF2A098FBE1BB70C29F2E53DDEB1C4C2A8933910EE6AE5F188088C34087D4CB
329 1A72A3BF0C6AEEE47F282D6DB7DE3C25506EE7507F13072644FF98A7CD2B2D2F
330 EEFA038D7A3E2EFBDFE608558B1BDA6E17FDF7190C578FA016C789C465CE3C65
```

Phase A 完了時 → Phase B 完了時 → Phase D 最終確認時の 3 回照合、全件一致。

### 旧 API 後方互換確認

```python
from validate_content import CRIME_SIGNATURES, SIGNATURE_REGISTRY
assert CRIME_SIGNATURES is SIGNATURE_REGISTRY["KEI"]  # PASS
```

---

## Phase B: slotmap §6 本文化 — 完走 (CP7 通過)

### 追記内容

`templates/KTX_template_slotmap.md` 末尾に §6 を新設:

- §6 §1 背景 (KEI 完了、6 科目展開)
- §6 §2 決定事項 (K-1 案 β 確定事項 + 一括処理規約)
- §6 §3 PDF 1 ページ = 1 問題の根拠と例外処理
  - §3.1 は Phase C 観測値に基づき **訂正版** に書き換え (「1 PDF = 1 問題、Q ページ + A ページ構成」)
- §6 §4 signature 構築方針 (条文番号 + 判例略称、cross-subject 干渉回避)
- §6 §5 §X 標準 5 項目記録 (Phase D 完了時に実測値で記入)

### 行数推移

- セッション開始時: 3267 行
- Phase B 完了時: 3423 行 (+156 行)
- Phase D §X 実測値記入後: 3435 行

---

## Phase C: 6 科目処理 — 選択肢 A (3 件採用 / 3 件保留)

### Phase C 当初の停止と方針変更

初動では「1 PDF = 多問題、1 ページ = 1 問題」と仮定して PDF 全 13 ページを画像読解した結果、実構造が「1 PDF = 1 問題 (Q ページ + A ページ)」かつ 6 PDF 中 3 PDF が未対応形式と判明 (O-1)。

xnh と協議のうえ、**選択肢 A (採用 3 / 保留 3)** に方針変更:

- 採用: `MIN.pdf` / `SYO.pdf` / `MINS.pdf` (combination-5 / multi-select-5、対応 5 形式内)
- 保留: `KEN.pdf` / `KEIS.pdf` / `GSE.pdf` (fill-in × 2、ox-grid-3 + combination-8 × 1、未対応)

### 完走 3 件の詳細

| 問題 ID | 科目 | 出題形式 | 正答率 | override | template | HTML パス | サイズ | structure | content |
|---|---|---|---|---|---|---|---|---|---|
| `MIN001`  | 民法     | combination-5 | 95% | P1 | KTX_template_comb5.html | `outputs/tx/民TX/民TX001.html`   | 119,619 B | WARN [S26] 1 件 | PASS |
| `SYO001`  | 商法     | combination-5 | 32% | P3 | KTX_template_comb5.html | `outputs/tx/商TX/商TX001.html`   | 120,115 B | WARN [S26] 1 件 | PASS |
| `MINS001` | 民事訴訟法 | multi-select-5 | 82% | P1 | KTX_template_msel5.html | `outputs/tx/民訴TX/民訴TX001.html` | 118,426 B | WARN [S26] 1 件 | PASS |

#### MIN001 (民法、H20-1)

- **topic (crime field)**: 信義則と権利濫用
- **answer**: 5 (= エオ)
- **case_citations**: 最判昭50.2.25（百選Ⅱ2事件）/ 最判昭30.11.22 / 大判大14.12.3 / 大判昭10.10.5（百選Ⅰ1事件、宇奈月温泉事件）/ 大判大8.3.3 / 大判大10.6.2
- **論点**: 信義誠実の原則 (1条2項) vs 権利濫用禁止 (1条3項) の機能領域区別。安全配慮義務 / 権利失効 / 引渡場所協力義務 vs 宇奈月温泉 / 信玄公旗掛松

#### SYO001 (商法、H19-37)

- **topic (crime field)**: 定款の目的
- **answer**: 2 (= アエ)
- **case_citations**: 最判昭27.2.15（百選1事件）
- **論点**: 株式会社の権利能力制限説 (定款所定の目的の範囲内でのみ権利能力) に対する批判の妥当性。記述アは「目的範囲内なら定款変更不要」、記述エは「取締役の責任は会社法423条独自」のため、いずれも判例説固有の批判として的を射ていない

#### MINS001 (民事訴訟法、H19-54)

- **topic (crime field)**: 非訟事件
- **answer**: [4, 5] (順不同)
- **case_citations**: 最大決昭40.6.30（百選1事件）/ 大決昭5.9.30
- **論点**: 夫婦の同居を命じる審判の非訟事件性。形式的執行力の不在 (4) と債務の性質上の強制履行不能 (5、民法414条1項ただし書 + 人格尊重の理念) という 2 つの異なる根拠から強制執行が否定される

### 全 3 件共通の WARN [S26]

すべての完走問題で `validate_structure.py` が `[S26] ○×比率不均衡` を WARN として報告:

- MIN001: ○=9 / ×=3
- SYO001: ○=10 / ×=2
- MINS001: ○=11 / ×=1

これは PART D Rapid-Fire ドリル 12 件の ○×ラベル分布が 6:6 から大きく外れていることを意味する。期待値 6:6 は drill 学習効果を最大化するための設計指針 (slotmap §5.5 §6) だが、本セッションでは「PDF 解説の内容に忠実」を優先したため、自然と ○ 寄りになった。WARN は非致命なので CP6 PASS は維持される。

将来的に drill_blocks をリライトする際は、否定形質問を増やして 6:6 に近づけることが望ましい (簡易リファクタ、別セッション)。

### 保留 3 件の調査結果

#### KEN.pdf (憲法 H19-1)

- **構造**: 2 ページ = 1 問題 (page-01 問題 + page-02 解答+解説)
- **出題形式**: **fill-in** (A-D の 4 空欄を 1-8 候補から穴埋め)
- **正答**: A=5, B=7, C=3, D=6 / 正答率 30%
- **論点**: 法の支配 (人の支配との対比、最高法規性、適正手続、裁判所による違憲審査)
- **未対応理由**: 5 形式 (ox-grid-N / multi-select-N / single-choice-N / combination-N) は「N 個の記述に対する N または 1 の判定 or 組合せ」を前提とするが、KEN は「N 個の空欄 (A-D) に M 個 (1-8) の候補を選択して埋める」構造。空欄位置 × 候補 という 2 軸の対応関係を表現できない

#### KEIS.pdf (刑事訴訟法 H18-21)

- **構造**: 3 ページ = 1 問題 (page-01 問題 + page-02 解答+解説の前半 + page-03 解説の続き)
- **出題形式**: **fill-in + combination-5** (①-⑧ の 8 空欄を a-h 候補から穴埋め、組合せとして 1-5 から 1 つ選ぶ)
- **正答**: ① i / ④ d / ⑥ h / ⑧ d (※部分実測、正答率 88%)
- **論点**: 刑事訴訟法の基本構造 — 審理対象、訴因と公訴事実、職権主義と当事者主義
- **未対応理由**: KEN と同じ fill-in 系だが、空欄数が 8 と多く、さらに 1-5 の組合せ選択肢の上で「複数空欄の組合せ」を一意に決める形式。combination-5 templ の 5 set 構造 (ア-オ から N 個選ぶ) とも整合しない

#### GSE.pdf (行政法 R4-13)

- **構造**: 2 ページ = 1 問題 (page-01 問題 + page-02 解答+解説)
- **出題形式**: **ox-grid-3 + combination-8** (ア-ウ の 3 記述に ○ または × を付し、その組合せを 1-8 から 1 つ選ぶ)
- **正答**: 不明 (page-02 で各記述の○×を判定して組合せを導出)
- **論点**: 行政法の法源 — 慣習法、行政立法の法源性、代執行と条例の関係
- **未対応理由**: 現行 ox-grid 系 template は N=4 (ox-grid-4) と N=5 (ox-grid-5) のみ。N=3 (記述ア-ウ) は未対応。また、N=3 の ○× には 2^3 = 8 通りの組合せがあり、それを 1-8 候補から選ぶ combination 構造もまた 5 一覧前提の combination-5 と整合しない

### 構造比較表 (既存 5 形式 vs 未対応 3 形式)

| 形式 | 記述数 | 判定 | 選択肢 | template |
|---|---|---|---|---|
| **ox-grid-5** | 5 (ア-オ) | 各記述 ○× | — (判定列挙) | KTX_template.html |
| **ox-grid-4** | 4 (ア-エ) | 各記述 ○× | — (判定列挙) | KTX_template_ox4.html |
| **multi-select-5** | 5 (1-5) | 各記述真偽 | K 個選択 | KTX_template_msel5.html |
| **single-choice-5** | — | 見解 3 件 (A/B/C) | 1 個選択 | KTX_template_sc5.html |
| **combination-5** | 5 (ア-オ) | 各記述真偽 | 5 組合せから 1 個選択 | KTX_template_comb5.html |
| **fill-in (KEN)** | 0 (記述なし、空欄のみ) | 候補マッチング | 4 空欄 × 8 候補 | **未実装** |
| **fill-in + combo (KEIS)** | 0 (8 空欄 + h 候補) | 候補マッチング + 組合せ | 8 空欄 × 8 候補 → 1-5 組合せ | **未実装** |
| **ox-grid-3 + combo-8 (GSE)** | 3 (ア-ウ) | 各記述 ○× | 8 組合せから 1 個選択 | **未実装** |

### 新規 template 増設で対応する場合の規模見積もり

#### A. fill-in (KEN 対応)

- 必要な slot: `{{BLANK_A_LABEL}}`〜`{{BLANK_D_LABEL}}`, `{{BLANK_A_ANSWER}}`〜`{{BLANK_D_ANSWER}}`, `{{CANDIDATE_1_TEXT}}`〜`{{CANDIDATE_8_TEXT}}`, 各空欄の `{{EXPLANATION}}`
- schema 拡張: 新 type `Blank` (label + correct_candidate_num + explanation) と `Candidate` (num + text)
- render.py: instruction_type "fill-in" を `TEMPLATE_PATHS` に追加
- validate_structure.py: 新形式専用の S 規則を追加 (S78〜)
- check_template_sync.py: 新 template の DIFF_ALLOWED セクション追加
- **見積規模**: 中 (テンプレ HTML/CSS 約 1500 行、JS 50 行、Python 約 200 行)

#### B. fill-in + combination (KEIS 対応)

- A の拡張版。空欄数を 4 → 8、候補マッチング後に combination-5 から 1 つ選ぶ
- schema: `Blank` を 8 件、combinations を 5 件 (set: 空欄 ID → 候補 ID のマップ)
- **見積規模**: 大 (テンプレ HTML/CSS 約 2000 行、JS 100 行、Python 約 300 行)

#### C. ox-grid-3 + combination-8 (GSE 対応)

- 既存 ox-grid-4/-5 を N=3 に汎化、combination を 5 → 8 に拡張
- schema: choices を minItems 3、combinations を minItems 8 / maxItems 8 にも対応 (現状 5 固定)
- render.py: instruction_type "ox-grid-3" + "combination-8" を `TEMPLATE_PATHS` に追加
- **見積規模**: 小〜中 (ox-grid-4 を base に N=3 派生、combination-5 を N=8 派生、合計約 800 行)

### (b) refactor 発火判定

タスク指示に従い、refactor 発火条件を判定する:

| 条件 | 内容 | 判定 |
|---|---|---|
| ① 既存 4-5 本で収まらない | 5 本テンプレで対応できない形式が確認されたか | **該当** (KEN/KEIS/GSE の 3 件) |
| ② 形式 #6 以降 2 件以上 confirmed | 未対応形式が 2 件以上独立に確認されたか | **該当** (fill-in × 2、ox-grid-3+combination-8 × 1 の計 3 形式) |
| AND 結果 | 両条件 AND | **発火条件充足** |

### 次セッションで判断すべき選択肢

1. **6-7-8 本目テンプレ追加** (3 本新設、KEN/KEIS/GSE をそれぞれ完走)
   - 規模: 中〜大 (合計 3000 行超)
   - 5 形式テンプレと並列して個別実装、check_template_sync.py の差分許容セクションも拡張
   - メリット: 各形式の独自性を表現できる
   - デメリット: テンプレ 8 本管理の複雑さが増す、共通ロジックの重複が増える

2. **一般化リファクタ** (template を「N 記述 × K 判定/組合せ」のメタモデルに統合)
   - 規模: 大 (既存 5 本の互換性維持コストが極めて高い)
   - render.py をパラメトリックに書き直し、テンプレを 1 本 (もしくは 2-3 本) に集約
   - メリット: 将来の N=6 / K=10 等への拡張が容易
   - デメリット: 326-330 byte-identical 維持の難易度が極端に上がる、CP4 リスク

3. **保留継続** (KEN/KEIS/GSE は本プロジェクトでは扱わない)
   - 規模: ゼロ
   - メリット: 現状維持、326-330 + 3 新規問題で完結
   - デメリット: 6 科目全展開という当初目標が部分達成にとどまる

**現時点の私見**: 選択肢 1 (6-7-8 本目追加) を推奨。理由は (a) CP4 リスクが選択肢 2 より低い、(b) 一般化リファクタは将来形式 #9 以降が見えてから設計するほうが筋がよい、(c) 現状の 5 本テンプレは 326-330 シリーズで十分に投資が回収されており、これを温存する価値が大きい。ただし正式判断は xnh の方針による。

---

## Phase D: 最終確認と総括 — 完走

### 実施項目

- ✅ `check_template_sync.py` 最終実行 (exit 0)
- ✅ 326-330 SHA256 byte-identical 最終確認 (3 回目、全件一致)
- ✅ slotmap §6 §X 実測値記入完了 (3435 行に伸長)
- ✅ 本 docs 作成

### CP1-CP7 各通過状況 (最終)

| CP | 内容 | 結果 |
|---|---|---|
| CP1 | schema 変更は subject field 追加のみ | ✅ |
| CP2 | render.py は subject パラメータ化のみ | ✅ |
| CP3 | validate_content.py は SIGNATURE_REGISTRY 二段化 + alias | ✅ |
| CP4 | 326-330 全件 byte-identical 維持 | ✅ (3 回照合) |
| CP5 | check_template_sync.py exit 0 維持 | ✅ |
| CP6 | 各新規問題で render → 二段検証 PASS | ✅ (3 件、各 WARN [S26] のみ) |
| CP7 | slotmap §6 本文化 | ✅ (3435 行) |

### SIGNATURE_REGISTRY 各科目 entry 件数

| Subject | entries |
|---|---|
| KEI | 11 (既存、不変) |
| KEN | 0 (Phase C 保留) |
| MIN | 0 (単一問題、cross-topic 不要) |
| SYO | 0 (同上) |
| MINS | 0 (同上) |
| KEIS | 0 (Phase C 保留) |
| GSE | 0 (Phase C 保留) |

将来、各科目に問題が追加されたとき (例えば `MIN002` で同義語混入が問題になりそうな別 topic を扱うとき)、初めて `SIGNATURE_REGISTRY["MIN"]` に entry を追加する。

---

## 想定外の挙動 (O 系列)

### O-1: PDF 1 ファイル = 1 問題 (複数ページ)

タスク前提では「1 PDF = 多問題、1 ページ = 1 問題」だったが、実際は **1 PDF = 1 問題 (page-01 問題、page-02 以降 解答+解説)**。Wondershare PDFelement で個別問題を抽出した自然な形態と推測される。slotmap §6 §3.1 を訂正版に書き換えて吸収済。

### O-2: 解答 / 解説が PDF 内に同梱

326-330 では PDF = 問題のみ、解説は xnh 入力 / 他資料起こしだったが、今回の PDF は解答 + 各記述の詳細解説が同 PDF 内に含まれていた。**利点**: render 用 JSON の `explanation` field を捏造せず PDF から起こせる。drill_blocks / professor.note は同じ素材を再構成して生成。

### O-3: KEN / KEIS の fill-in 形式

予備試験では「空欄補充 + 候補集合」形式が頻出することが本セッションで判明。5 形式テンプレでは表現できないため、テンプレ追加が将来課題 (本セッション (b) refactor 発火判定参照)。

### O-4: GSE の ox-grid-3 + combination-8 形式

3 記述 ○× × 2^3 = 8 組合せは予備試験行政法に特徴的なパターン。`ox-grid-3` 新設 or `combination-N` 可変長化の設計判断が必要。

### O-5: PowerShell 出力エンコーディング (CP932)

Phase A 検証時、`validate_structure.py` が ✅ (U+2705) を出力しようとして CP932 で `UnicodeEncodeError` を起こした。回避策:

```powershell
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

過去セッションでも類似症状が出ているはず。**運用 hint**: 本プロジェクトを Windows + PowerShell で動かすときは、セッション冒頭で上記 3 行を実行することを推奨。CLAUDE.md に追記してもよい。

### O-6: 環境セットアップ

本セッションで新規 install:

- `pymupdf` 1.27.2.3 (PDF → PNG レンダリング、`scripts/pdf_to_png.py` 用)
- `pypdf` (ページ数確認、PoC)

### O-7: verdict_label セマンティクスの拡張

`schema/problem.schema.json` の `verdict_label` enum は `["正しい", "誤っている"]` で hard-coded。これは KEI シリーズ (罪名判定) では「記述の真偽」を直接表現したが、今回の MIN001 (「権利濫用禁止について述べているか」) や SYO001 (「批判としてふさわしいか」) では、「設問の問いに照らした該否」として読み替える必要があった。意味論は文脈で吸収できるが、将来的に「該当する / 該当しない」等のラベル enum を追加するか、enum を撤廃して自由文字列化する選択肢もある。本セッションでは既存 enum を維持。

### O-8: 全 3 件で [S26] ○×比率 WARN

drill_blocks 12 件の ○× ラベル分布が 6:6 想定から偏った (○ に偏る)。これは「PDF 解説に忠実」を優先した結果の自然な偏りで、機能上の問題ではない。将来的に否定形質問を増やして 6:6 化する簡易リファクタは可能。

---

## docs/ 最終構成

```
docs/
├── ox4-design-investigation-326-330-session.md
├── session-326-327-completion.md
├── session-328-completion.md
├── session-329-completion.md
├── session-330-completion.md
├── session-ken-k1-design.md
├── session-warn-complete.md
└── session-6subjects-expansion.md   ← 本ファイル
```

---

## 次セッション最優先項目

1. **KEN / KEIS の fill-in 対応**: 上記 (b) refactor の選択肢 1 (6 本目 template 追加) を採用するか、選択肢 2 (一般化リファクタ) を採るかの方針決定。設計合意 (K-2 相当の design doc) を起草し、xnh とのレビュー後に着手。
2. **GSE の ox-grid-3 + combination-8 対応**: 1 と同時並行で扱うか、別タスクとして切り出すかを決定。ox-grid-3 は既存 ox-grid-4 を base に N=3 派生で比較的軽量に実装可能。
3. **(b) refactor の本格判断**: 一般化リファクタ vs テンプレ追加の選択。327 や 329 のように 1 セッションで完走可能な規模に分割するのが望ましい。
4. **drill_blocks 6:6 化の簡易リファクタ**: MIN001 / SYO001 / MINS001 の各 drill_blocks に否定形質問を 3-4 件追加して [S26] WARN を解消。優先度は低いが、quick win として候補。

本セッションで基盤改修 (Phase A) / 仕様本文化 (Phase B) / 3 件採用 (Phase C) / 総括 (Phase D) を完走したため、次セッションは保留 3 件への対処から再開可能。326-330 シリーズの byte-identical 維持と CP1-CP7 全通過状態を継承できる。

---

## 最終報告 (xnh 指示 A-G)

### A. MIN/SYO/MINS 完走結果

| 問題 ID | 出題形式 | HTML パス | ERROR | WARN |
|---|---|---|---|---|
| MIN001  | combination-5  | `outputs/tx/民TX/民TX001.html`   | 0 | 1 ([S26] ○×比率 9:3) |
| SYO001  | combination-5  | `outputs/tx/商TX/商TX001.html`   | 0 | 1 ([S26] ○×比率 10:2) |
| MINS001 | multi-select-5 | `outputs/tx/民訴TX/民訴TX001.html` | 0 | 1 ([S26] ○×比率 11:1) |

### B. 326-330 byte-identical 維持確認

全 5 件、Phase A/B/D の 3 回照合とも一致。SHA256 は本文書 § Phase A 参照。

### C. KEN/KEIS/GSE の保留理由詳細

本文書 § 「保留 3 件の調査結果」および「構造比較表」参照。要約:

- **KEN.pdf**: fill-in (A-D 4 空欄 / 1-8 候補) — 既存テンプレで空欄位置 × 候補の 2 軸表現不能
- **KEIS.pdf**: fill-in + combination (①-⑧ 8 空欄 + 1-5 組合せ) — KEN の拡張版、空欄数 8、組合せ表現追加
- **GSE.pdf**: ox-grid-3 + combination-8 — N=3 ox-grid (現行 N=4,5 のみ) + 8 組合せ (現行 5 固定)

### D. (b) refactor 発火条件の判定

| 条件 | 判定 |
|---|---|
| ① 既存 4-5 本で収まらない | ✅ 該当 |
| ② 形式 #6 以降 2 件以上 confirmed | ✅ 該当 (3 件、内訳 fill-in × 2 / ox-grid-3+combination-8 × 1) |
| AND | **発火条件充足** |

次セッションで「一般化リファクタ vs 6-7-8 本目追加」を判断すべし。

### E. slotmap §6 §X 実測値記入完了

slotmap.md 3435 行、§6 §5 §X.1〜§X.5 を実測値で記入済。本文書とリンク付け済。

### F. docs/session-6subjects-expansion.md の構成

サマリ → Phase A (基盤改修) → Phase B (slotmap §6) → Phase C (3 件採用 / 3 件保留 / 構造比較 / (b) 判定) → Phase D (最終確認) → 想定外挙動 O-1〜O-8 → 次セッション最優先 → 最終報告 A-G の順。

### G. 想定外の挙動

O-1〜O-8 を本文書 § 「想定外の挙動」に列挙。主要な点は (a) 1 PDF = 1 問題構造 / (b) PDF 内に解説同梱 / (c) fill-in と ox-grid-3+combination-8 の未対応 / (d) PowerShell CP932 エンコーディング / (e) verdict_label セマンティクス拡張。

---

## 本セッション最終状態 (2026-05-19 公式 close)

### 完走 8 件の問題一覧 (科目別)

| 順 | 問題 ID | 科目 | 出題形式 | template | 正答率 | override | HTML パス | バイト数 |
|---|---|---|---|---|---|---|---|---|
| 1 | 326    | 刑法 (KEI)       | ox-grid-5      | KTX_template.html        | 47% | P2 | `outputs/tx/刑TX/刑TX326.html`     | 121,870 |
| 2 | 327    | 刑法 (KEI)       | ox-grid-4      | KTX_template_ox4.html    | 81% | P1 | `outputs/tx/刑TX/刑TX327.html`     | 116,979 |
| 3 | 328    | 刑法 (KEI)       | multi-select-5 | KTX_template_msel5.html  | 56% | P2 | `outputs/tx/刑TX/刑TX328.html`     | 117,075 |
| 4 | 329    | 刑法 (KEI)       | single-choice-5 | KTX_template_sc5.html   | —   | —  | `outputs/tx/刑TX/刑TX329.html`     | 117,285 |
| 5 | 330    | 刑法 (KEI)       | combination-5  | KTX_template_comb5.html  | 84% | P1 | `outputs/tx/刑TX/刑TX330.html`     | 120,663 |
| 6 | MIN001 | 民法 (MIN)       | combination-5  | KTX_template_comb5.html  | 95% | P1 | `outputs/tx/民TX/民TX001.html`     | 119,619 |
| 7 | SYO001 | 商法 (SYO)       | combination-5  | KTX_template_comb5.html  | 32% | P3 | `outputs/tx/商TX/商TX001.html`     | 120,115 |
| 8 | MINS001| 民事訴訟法 (MINS) | multi-select-5 | KTX_template_msel5.html  | 82% | P1 | `outputs/tx/民訴TX/民訴TX001.html` | 118,426 |

出題形式の分布 (8 件): ox-grid-5 × 1 / ox-grid-4 × 1 / multi-select-5 × 2 / single-choice-5 × 1 / combination-5 × 3。**5 形式すべてに少なくとも 1 件の運用実績が積まれた**。

### slotmap.md 累計成長

| 時点 | 行数 | 倍率 (vs 初期) | 主な追加 |
|---|---|---|---|
| 初期 (§1 のみ、326 着手前) | 451  | 1.00 倍 | スロット仕様 §1 のみ |
| §5.1〜§5.11 完了 (326-330 完走時) | 3,267 | 7.24 倍 | 形式分岐 §5.1-5.4 / WARN 解消 §5.5-5.9 / CI §5.10 / 整備 §5.11 |
| 本セッション Phase B 完了 | 3,423 | 7.59 倍 | §6 subject namespace 仕様 (本文化) |
| 本セッション Phase D 完了 (公式 close 時点) | **3,435** | **7.62 倍** | §6 §X 実測値記入 |

**初期 451 → 最終 3,435 行、約 7.6 倍。** 326-330 シリーズで形式分岐と WARN 解消の規律が確立し、本セッションで subject namespace 化の土台が整った。

### (b) refactor 発火判定の最終確認

| 条件 | 内容 | 判定 |
|---|---|---|
| ① | 既存 5 本テンプレで収まらない案件が発生 | ✅ 該当 (KEN/KEIS/GSE) |
| ② | 形式 #6 以降が 2 件以上 confirmed | ✅ 該当 (fill-in × 2 + ox-grid-3+combo-8 × 1 = 3 形式) |
| AND | refactor 発火条件 | **充足 (FIRE)** |

→ 次セッションで「6 本目以降の template 追加」か「一般化リファクタ」かを決定する必要がある。

### 残課題 3 件 (KEN/KEIS/GSE) の状態

| PDF | 形式 | 構造的特徴 | PDF 状態 | JSON | HTML | signature |
|---|---|---|---|---|---|---|
| `KEN.pdf` | fill-in | A-D 4 空欄 / 1-8 候補 | `inputs/tx-pdfs/KEN.pdf` 配置済、`_tmp_pdf_pages/KEN/page-01,02.png` 抽出済 | ❌ 未作成 | ❌ 未生成 | `SIGNATURE_REGISTRY["KEN"]` = {} |
| `KEIS.pdf` | fill-in + combination | ①-⑧ 8 空欄 / a-h 候補 / 1-5 組合せ | `inputs/tx-pdfs/KEIS.pdf` 配置済、`_tmp_pdf_pages/KEIS/page-01-03.png` 抽出済 | ❌ 未作成 | ❌ 未生成 | `SIGNATURE_REGISTRY["KEIS"]` = {} |
| `GSE.pdf` | ox-grid-3 + combination-8 | ア-ウ 3 記述 ○× / 1-8 組合せ | `inputs/tx-pdfs/GSE.pdf` 配置済、`_tmp_pdf_pages/GSE/page-01,02.png` 抽出済 | ❌ 未作成 | ❌ 未生成 | `SIGNATURE_REGISTRY["GSE"]` = {} |

各 PDF は 1 ファイル 1 問題、page-01 = 問題、page-02 以降 = 解答+解説の構造で確定（O-1）。`_tmp_pdf_pages/` 配下に zoom=4.0 (1584×2384 程度) の PNG が抽出済で、次セッションで Claude image understanding に即座に渡せる。

### 次セッション最優先項目 (3 つの選択肢)

(b) refactor 発火判定を受け、以下の 3 選択肢から方針決定が必要。

#### 選択肢 X: 6 本目 template 追加 (fill-in 用) → 7 本目追加 (ox-grid-3 用)

- **構成**: 既存 5 本テンプレに `KTX_template_fillin.html` (KEN/KEIS 用) と `KTX_template_ox3comb8.html` (GSE 用) を逐次追加
- **schema 拡張**: `instruction_type` enum に `fill-in-A-D-1-8` 等を追加、`Blank` / `Candidate` の `$defs` 追加
- **render.py**: `TEMPLATE_PATHS` に 2 entry 追加、KEIS 用に `BLANK_*` / `CANDIDATE_*` slot 構築ロジック追加
- **check_template_sync.py**: 7 本テンプレ間の `INTENTIONAL_DIFFS` 管理規模拡大
- **規模見積**: 中〜大 (HTML/CSS 約 3,000 行、Python 約 500 行)
- **メリット**:
  - 326-330 byte-identical 維持の確度が極めて高い (CP4 リスク最小)
  - 各形式の独自性 (UI / 採点ロジック) を素直に表現可能
  - 「形式分岐は別テンプレ」という現行ポリシーと一貫
- **デメリット**:
  - テンプレ 7 本管理の複雑さ (sync check のメンテコスト)
  - 共通ロジックの重複が増える (PART A〜D の骨格は 7 本で同じ)

#### 選択肢 Y: 一般化リファクタ (partial 合成 or JS 動的レンダリング)

- **構成案 A (partial 合成)**: PART A〜D を独立 partial に分解し、`render.py` で形式ごとに partial を組み合わせる。テンプレファイルは partial 群に分解、最終 HTML は組合せ結果。
- **構成案 B (JS 動的レンダリング)**: 1 本のメタ template にすべての slot を持たせ、JS 側で `instruction_type` を見て不要セクションを非表示にする。template は 1 本に集約。
- **規模見積**: 大〜超大 (既存 5 本の完全互換が課題、CP4 リスク極大)
- **メリット**:
  - 将来形式 #9 以降の追加コストが圧倒的に低くなる
  - 共通ロジックの一元管理
- **デメリット**:
  - 326-330 byte-identical 維持の難易度が極端に上がる (slot ↔ partial 切替の差分管理)
  - check_template_sync.py の前提が崩れる (sync 対象の概念が変質)
  - 設計合意 (K-2 相当の design doc) に 1-2 セッション要する

#### 選択肢 Z: ハイブリッド (6 本目だけ追加、GSE は既存拡張)

- **構成**:
  - 6 本目 `KTX_template_fillin.html` を新設 (KEN/KEIS 両対応、KEIS の組合せ部分は combination-5 と同じ pattern を slot 化で再利用)
  - GSE は既存 `KTX_template_ox4.html` を base に N=3 派生し、`combination-N` を N=8 にパラメトリック化 (現行 combination-5 と共有 slot)
- **schema 拡張**: `Blank` / `Candidate` (KEN/KEIS 用) + `combinations` の minItems/maxItems を 5 固定から可変化 (3-8 範囲)
- **規模見積**: 中 (HTML/CSS 約 1,800 行、Python 約 300 行)
- **メリット**:
  - 選択肢 X の代替案として、テンプレ追加を最小限 (1 本) に抑える
  - 選択肢 Y より CP4 リスクが低い
  - combination-N の可変長化は将来の 4 組合せ問題等にも応用可能
- **デメリット**:
  - 6 本目テンプレが「fill-in 統合」という複合役を担うため、ox4 単独より複雑になる
  - combination-5 / combination-8 の可変長化は schema breaking change の可能性 (現行 KEI 330 への影響を慎重に検証する必要)

#### 各案の評価軸と agent 私見

| 評価軸 | X (テンプレ追加) | Y (リファクタ) | Z (ハイブリッド) |
|---|---|---|---|
| CP4 (326-330 byte-identical) リスク | 最低 | 最高 | 低 |
| 実装規模 | 中〜大 | 大〜超大 | 中 |
| 形式 #9 以降の拡張容易性 | 中 (毎回テンプレ追加) | 高 | 中 |
| 既存 5 本との一貫性 | 高 | 低 | 中 |
| テンプレ管理コスト (long-run) | 高 (本数増) | 低 (集約) | 中 |
| 設計合意コスト (本タスクで要する判断) | 低 | 高 | 中 |

**agent 私見**: 当面は **選択肢 X (テンプレ追加)** を推奨。理由:

1. **CP4 リスクを最小化できる**。326-330 byte-identical は本プロジェクトの最重要担保であり、選択肢 Y はこれを脅かす。
2. **5 本テンプレは 326-330 シリーズで投資が十分に回収されており、温存価値が高い**。動かす理由は「将来コスト」しかなく、現時点で確定していない形式 #9 以降を見越して既存資産を再構築するのは Goodhart 化を招く。
3. **設計合意コストが最小**。本タスクは「KEN/KEIS/GSE を完走させる」のが直接目的であり、X はその実現経路として最短。
4. **形式 #9 以降が 5 本目以上累積した段階で、初めて選択肢 Y を本格検討すべき**。それまでは X で凌ぐ。

ただし選択肢 Z (ハイブリッド) も実装規模で X と Y の中間にあり、特に `combination-N` の可変長化は将来応用性があるため、xnh 側で「テンプレ本数を抑えたい」という方針があれば Z も有力候補。

**正式判断は xnh の方針による**。本セッションでは選択肢の提示まで。

### 次セッション開始時の最初のプロンプト雛形

```
inputs/tx-pdfs/{KEN,KEIS,GSE}.pdf の保留 3 件について、
docs/session-6subjects-expansion.md § 本セッション最終状態 で提示した
選択肢 X / Y / Z のうち [X | Y | Z] を採用して進めてください。

[X 採用時]
- 6 本目 template: KTX_template_fillin.html (KEN/KEIS 共用 fill-in + combination-5)
- 7 本目 template: KTX_template_ox3comb8.html (GSE 専用、ox-grid-3 + combination-8)
- 設計合意 (K-2 相当 design doc) → schema 拡張 → render.py / validate_structure.py / 
  check_template_sync.py 改修 → KEN001 / KEIS001 / GSE001 完走 の順で進行
- CP1-CP7 維持 (特に CP4 = 326-330 + MIN001 + SYO001 + MINS001 byte-identical)

[Z 採用時]
- 6 本目 template: KTX_template_fillin.html (KEN/KEIS 共用)
- GSE は既存 KTX_template_ox4.html を N=3 派生 + combination を 5 固定から N 可変に拡張
- combinations の minItems/maxItems 緩和に伴う KEI 330 への影響を慎重に検証

[Y 採用時]
- まず 1 セッションかけて design doc (K-2 相当) を起草
- 326-330 byte-identical のテスト戦略を最初に確定
- partial 合成 vs JS 動的レンダリング のいずれを採るかも design doc で論じる
```

### 公式 close 時点の確定状態

- **CP1-CP7 全通過**（CP4 は 3 回照合一致、CP6 は 8 件全件 PASS）
- **完走 8 件** (326-330 + MIN001 / SYO001 / MINS001)
- **保留 3 件** (KEN / KEIS / GSE、PDF と PNG 抽出物は配置済)
- **slotmap.md 3,435 行** (初期 451 → 7.6 倍)
- **(b) refactor 発火条件充足**、次セッションで方針決定が必要
- **CLAUDE.md に PowerShell PYTHONIOENCODING 注記追加済** (O-5 由来、毎セッション冒頭 3 行)
