# KEN 展開 K-1 設計確定報告書

**作成日**: 2026-05-18
**作成セッション**: 326-330 シリーズ §5.11 公式 close 直後、次フェーズとして KEN 展開を選択し、K-1 設計を本セッション内で確定したもの。
**ステータス**: K-1 完了、K-2 着手は KEN PDF 投入待ち。

本書は **PDF 投入後に次セッションが即 K-2 着手できるよう、設計合意を永続記録** するもの。本書を読み込めば、設計議論を再度行うことなく実装に直行できる。

---

## §1. KEN 展開を選択した経緯

### §1.1 326-330 シリーズの公式 close (§5.11 終局)

326-330 シリーズは §5.11 を以て公式 close した。close 時点で以下が確立されていた:

- 5 形式実装完了 (ox-grid-5 / ox-grid-4 / multi-select-5 / single-choice-5 / combination-5)
- WARN 4 系統消化済 (S14 / S17 / S51 / S71-AP33)
- CI safety net 稼働中 (check_template_sync.py)
- byte-identity SHA256 chain 全件保持
- slotmap.md = 3,267 行 / 193,683 B (§1〜§5.11 完備)
- docs/ = 完了報告 6 ファイル体制
- CRIME_SIGNATURES 11 罪 (信書隠匿罪は §5.9 で追加)
- §5.9 §12.6 の誤記述 (ACR 削除可) は §5.11 §7 で訂正済

### §1.2 X / Y / Z 3-way 比較 (slotmap §5.11 §13)

§5.11 §13 で次フェーズ候補を 3-way 比較し、**候補 Y (KEN = 憲法展開)** を推奨した。理由 (再掲):

1. xnh の本来目的 (予備試験対策コンテンツ整備) への寄与最大
2. 326-330 で確立した 7 種資産 (5 format / schema oneOf / S1-S77 / CI safety net / 12 drill / professor sub-card / CP1-CP5 rules) の活用率最大
3. signature namespace が刑法と完全分離 → CRIME_SIGNATURES 拡張は dict 追加のみで cleanup 不要
4. 仮に途中中断しても完成済み問題は独立 valid

候補 X (§5.12+ cleanup) は §5.11 で主要案件決着済みのため低優先、候補 Z (形式 #6 待機) は新規 PDF 到着まで自然休止選択肢として残置。

### §1.3 K-1 設計調査の実施

xnh の指示により本セッションで K-1 設計調査を実施 (ファイル変更ゼロ条件)。grep / Read で既存資産の刑法依存度を網羅的に確認し、namespace 分離 3 案 (α / β / γ) を比較評価した。

**重要発見**:

- `inputs/tx-pdfs/README.txt` は「科目はPDF内容からAIが自動判定し、outputs/000_TX/{科目}/{接頭辞}{NNN}.html に出力」と明記しており、**本プロジェクトの設計意図は元々マルチ科目**だった (現状は刑法のみ実装が進んだ状態)
- `outputs/000_TX/` には既に 7 科目分のディレクトリが存在 (刑TX / 刑訴TX / 憲TX / 行TX / 商TX / 民TX / 民訴TX)
- `CLAUDE.md` 命名規約に「憲TX{NNN}.html」既載
- `templates/KTX_template*.html` 5 本は **「罪」「crime」を 1 文字も含まず、完全に科目非依存**
- `scripts/check_template_sync.py` は template 構造のみ検査、**完全に科目非依存**
- `scripts/validate_structure.py` は刑法依存はコメント 1 行 (L814 例示) のみ
- `scripts/render.py` の刑法 hardcode は L36 (`OUTPUT_DIR`) + L256 (`f"刑TX{...}"`) の **2 箇所のみ**
- `scripts/validate_content.py` の `CRIME_SIGNATURES` (L48-117) が **唯一の刑法専用 dict**
- `schema/problem.schema.json` は構造非依存、`crime` field 名と description が刑法仕様のみ

→ KEN 展開の **実コード改修箇所は 3 ファイル合計 50-80 行**。設計上、極めて低コストで完遂可能。

---

## §2. 案 β 採用の経緯と確定内容

### §2.1 3 案比較サマリ

| 案 | 概要 | 326-330 regression | KEN 所要 | 6 科目目以降 cost | 衝突回避 | 総合 |
|---|---|---|---|---|---|---|
| α | scripts_kei/, scripts_ken/ に丸ごとコピー | ◎ ゼロ | × 2-3 セッション | × 7 倍化 | ◎ 完全分離 | × overkill |
| **β** | **単一 codebase + subject パラメータ化** | **◯ default=KEI で抑制** | **◎ 約 1 セッション** | **◎ dict 追加のみ** | **◎ subject 切替** | **◎ 採用** |
| γ | 共通 scripts/ + scripts/subjects/{name}/ | ◯ ほぼ案 β 同等 | ◯ 約 1.2 セッション | ◎ boilerplate 最小 | ◎ ファイル分離 | ◯ 5 科目目以降光る |

### §2.2 案 β 採用 + 案 γ への升格パス保持

**採用方針**: 案 β (パラメータ化) を採用、ただし将来の案 γ 升格を阻害しない設計にする。

具体的には:

- `scripts/validate_content.py` の `CRIME_SIGNATURES` を **`SIGNATURE_REGISTRY: dict[str, dict[str, list[str]]] = {"KEI": {...}, "KEN": {...}}`** に rename + 拡張
- subject 切替は **`problem.json` の `subject` field (新規 optional, default "KEI")** で実現
- 将来 6 科目目以降で SIGNATURE_REGISTRY が膨れた時に `scripts/subjects/<name>/signatures.py` へ自然移動可能
- rename に伴う後方互換: `CRIME_SIGNATURES = SIGNATURE_REGISTRY["KEI"]` という alias を残置 (外部 import 元は現状ゼロと推定だが、念のため保険)

### §2.3 確定事項 (K-2 着手時に即適用する仕様)

#### F-1. `subject` field 仕様

```jsonc
// schema/problem.schema.json への追加
"subject": {
  "type": "string",
  "enum": ["KEI", "KEN", "MIN", "SYO", "MINS", "KEIS", "GSE"],
  "default": "KEI",
  "description": "科目コード。KEI=刑法 / KEN=憲法 / MIN=民法 / SYO=商法 / MINS=民訴 / KEIS=刑訴 / GSE=行政法。validate_content.py の SIGNATURE_REGISTRY のキー。未指定時は KEI (後方互換)。"
}
```

- **optional** (required にしない、326-330 への regression 防止)
- **default="KEI"** で既存 326-330 JSON が無改修で valid
- enum は 7 科目全て予約 (将来全科目展開を見据える)

#### F-2. `crime` field の扱い

**rename しない**。description のみ汎用化:

```jsonc
"crime": {
  "type": "string",
  "description": "分類キー (罪名 / 論点 / 権利分類)。validate_content.py の negative check のキー。KEI 科目では '盗品等罪' '詐欺罪' 等、KEN 科目では '表現の自由' '平等権' 等。"
}
```

理由:

- rename (`topic` 等) すると 326-330 JSON 全件 rename が必要 → byte-identity 破壊
- field 名そのものは internal な実装名、description で意味を拡張すれば十分
- `allowed_cross_refs` も同様、description のみ汎用化

#### F-3. 命名規約

| 項目 | 値 |
|---|---|
| 出力先ディレクトリ | `outputs/000_TX/憲TX/` |
| 出力ファイル名 | `憲TX{NNN}.html` |
| problems JSON | `problems/KEN{NNN}.json` |
| inputs PDF | `inputs/tx-pdfs/KEN{NNN}.pdf` または **連番継続** (xnh 選択) |

CLAUDE.md 命名規約と整合。

#### F-4. 問題番号体系

**KEN001 から開始** (科目別 namespace 連番)。

理由:

- 刑法 326-330 と KEN001-005 で番号空間を分離 → 衝突なし
- 将来他科目も `MIN001`, `SYO001` で揃う
- CLAUDE.md ファイル命名規則と整合 (「3 桁ゼロ埋め数字」)

#### F-5. slotmap.md の構成

**§6 を既存 slotmap に追記** (1 ファイル維持)。

- §1〜§5.11 = 刑法 326-330 シリーズ (close 済)
- §6.1 以降 = KEN 展開 (K-2 着手時に起草)
- 5 科目目以降で別ファイル化検討 (R7 リスク)

#### F-6. signature 構築方針

**条文番号 + 判例略称ベース、論点単位 dict**。

KEN 用 `SIGNATURE_REGISTRY["KEN"]` の構造例 (具体内容は K-2 で確定):

```python
"KEN": {
    "表現の自由": ["21条", "二重の基準論", "LRAテスト", "事前抑制", "明確性の理論"],
    "平等権":     ["14条", "厳格な合理性", "国籍法違憲判決", "尊属殺重罰違憲"],
    "私人間効力": ["三菱樹脂事件", "間接適用説", "直接適用説", "公権力性"],
    "生存権":     ["25条", "堀木訴訟", "朝日訴訟", "プログラム規定説"],
    "教育を受ける権利": ["26条", "旭川学テ", "教科書検定", "学習権"],
    # ... K-2 で論点単位に追記
}
```

注意:

- 一般語 (「合理性」「適用」「権利」単独) は誤検出多発のため禁止 (§5.11 §5 教訓継承)
- 判例引用形式は「最判昭33.12.16(百選Ⅰ○○事件)」で刑法と構造同じ
- 刑法 SIGNATURE と KEN SIGNATURE は条文番号で完全分離 (KEI=130-263条 / KEN=1-103条+総則的条文)

#### F-7. canonical 扱い

**KEN 用 canonical 不要**。PATCH §1 で「canonical/KTX301.html は構造と仕上がりの参考例」と既定済。KTX301 を全科目共通の構造参考として残置。

#### F-8. PDF 投入体制

xnh が PDF 投入。次セッション開始時に以下のいずれか:

- **段階投入** (推奨): KEN001 sample 1 件先行投入 → K-2 完走 → 残り 4 件投入 → K-3 batch
- **一括投入**: KEN001-005 を最初から 5 件投入 → K-2 + K-3 連続実施

---

## §3. 想定リスク R1-R8 (調査結果より継承)

| ID | リスク | 影響度 | 緩和策 |
|---|---|---|---|
| R1 | 326-330 への regression (subject 拡張で既存 JSON が validate 失敗) | 高 | `subject` field を optional + default="KEI" にして既存 5 件は無改修で valid 維持。byte-identity SHA256 比較で CP3 維持確認 |
| R2 | render.py パラメータ化のバグで既存 prefix が変わる | 高 | SUBJECT 切替 default="KEI" + 326-330 byte-identical 再生成テストで検出 |
| R3 | KEN signature dict の False positive (一般語 "合理性" "適用" 等が誤検出) | 中 | §5.11 §5 の経験 (誤検出多発 → 一般語禁止) を継承、条文番号 + 判例略称ベースで構築 |
| R4 | KEN PDF 未配置による着手不能 | 高 (現状) | xnh への PDF 投入依頼。本書 §5 に明示 |
| R5 | KEN 出題形式が 5 形式で完全カバーされない (例: 穴埋め系) | 中 | 大半カバー可能。未カバー形式は slotmap §6.2+ で追加 (1-2 セッション増) |
| R6 | canonical KTX301 の刑法的見た目が KEN HTML で違和感 | 低 | PATCH §1 で「構造参考」位置づけ、override_pattern + CSS で吸収可能 |
| R7 | slotmap.md 単一ファイル肥大化 (3,267 → 4,500+ 行で視認性低下) | 低 | §6 章境界明示、目次更新で対応、5 科目目以降で別ファイル化検討 |
| R8 | CRIME_SIGNATURES → SIGNATURE_REGISTRY rename による import / 名前空間衝突 | 中 | 後方互換 alias (`CRIME_SIGNATURES = SIGNATURE_REGISTRY["KEI"]`) を残置、外部参照ゼロを grep 確認 (現状 import 元なしと推定) |

---

## §4. K-2 着手プロトコル (次セッション直行手順)

K-2 = namespace 確立 + KEN sample 1 件完走 = **約 1 セッション**。

### §4.1 K-2 着手前の前提確認

次セッション開始時に以下を確認:

- [ ] `inputs/tx-pdfs/` 配下に KEN PDF が **少なくとも 1 件** 存在 (例: `KEN001.pdf` または `331.pdf` 等)
- [ ] 本書 (`docs/session-ken-k1-design.md`) を読み込み、設計合意を再確認
- [ ] `templates/KTX_template_slotmap.md` §5.11 §13 で X/Y/Z 推奨 = Y (KEN) を再確認

### §4.2 K-2 工程 (9 工程)

| # | 工程 | 改修対象 | 行数 | 検証 |
|---|---|---|---|---|
| ① | `schema/problem.schema.json` 拡張 | `subject` field 追加 + `crime` description 汎用化 | 約 10 行 | jsonschema validate で 326-330 JSON 全件 PASS 確認 |
| ② | `scripts/render.py` パラメータ化 | `SUBJECT_OUTPUT_MAP`, `SUBJECT_PREFIX_MAP` 追加 + OUTPUT_DIR 算出関数化 | 約 20 行 | 326-330 再 render で SHA256 byte-identical 確認 (CP3) |
| ③ | `scripts/validate_content.py` SIGNATURE_REGISTRY 拡張 | `CRIME_SIGNATURES` → `SIGNATURE_REGISTRY["KEI"]` rename + `SIGNATURE_REGISTRY["KEN"]` 初期 dict 投入 + `negative_check` で subject 切替 | 約 30-50 行 | 326-330 全件 validate_content PASS 確認 (CP4) |
| ④ | `problems/KEN001.json` 起草 | PDF から構造抽出 + JSON 化 (PATCH §1 禁則遵守: canonical コピー禁止、explanation null は fail) | 100-150 行 | jsonschema validate PASS |
| ⑤ | `render.py` で KEN001 生成 | `outputs/000_TX/憲TX/憲TX001.html` 出力 | - | render exit 0 |
| ⑥ | KEN001 validate_structure + validate_content | - | - | S1-S77 PASS + content PASS |
| ⑦ | 326-330 regression 確認 | 全 5 件 SHA256 chain + validate_content 再確認 | - | byte-identical 維持 |
| ⑧ | `slotmap.md §6.1` 新設 | KEN 展開設計記録 (本書を slotmap 形式に書き起こし) | 200-400 行 | check_template_sync exit 0 維持 |
| ⑨ | `docs/session-ken-bootstrap.md` 新規完了報告 | K-2 完了総括 | 150-250 行 | - |

### §4.3 327-330 で確立した「設計合意 → 実装」パターンの KEN 適用

326-330 シリーズで確立した工程パターンを KEN にも適用する:

1. **slotmap §N.M に設計合意を本文化** (本書 + slotmap §6.1 が該当)
2. **実装は slotmap §N.M に沿って機械的に進める** (案 β / 確定事項 F-1〜F-8 を踏襲)
3. **§N.M §X に 5 項目実測値を記録** (目的 / 対象 / 変更点 / 検証 / 次の作業)
4. **CP1-CP5 維持を実機検証** (byte-identity + sync exit 0 + all PASS)
5. **docs/ に完了報告ファイル新規作成** (slotmap の長期保管とは別レイヤー)

→ KEN K-2 でもこの 5 ステップを踏襲。326-330 比 0.6-0.8 倍の時間短縮を期待。

---

## §5. K-3 展開プロトコル (KEN002-005 batch)

K-3 = KEN002-KEN005 完成 = **約 2-3 セッション**。

### §5.1 K-3 工程

| 件 | セッション割り当て | 工程 |
|---|---|---|
| KEN002 | 約 0.5-0.7 セッション | PDF → JSON → render → validate (パイプライン安定後) |
| KEN003 | 約 0.5 セッション | 同上 |
| KEN004 | 約 0.4-0.5 セッション | 同上 |
| KEN005 | 約 0.4 セッション | 同上 |
| 完了報告 | 0.3 セッション | docs/session-ken-completion.md 起草 |

合計 約 2-3 セッション。326-330 と異なり、形式・schema・CI safety net がそのまま流用できるため時間短縮効果が大きい。

### §5.2 K-3 完了後の到達点

- KEN001-005 シリーズ完成 = 326-330 と並ぶ 2 科目目シリーズ確立
- SIGNATURE_REGISTRY = `{"KEI": {...11 罪}, "KEN": {...N 論点}}`
- slotmap.md §6.1-§6.5 = KEN 5 件分の設計記録
- docs/ = 完了報告 9 ファイル体制 (本書 + 既存 7 + KEN-bootstrap + KEN-completion)
- byte-identity chain = 刑法 5 件 + KEN 5 件 = 10 件保持

### §5.3 K-3 後の選択肢

- 6 科目目 (民法 MIN / 民訴 MINS 等) への展開
- subjects/ 分離 (案 γ への升格、SIGNATURE_REGISTRY が 3 科目以上で肥大時)
- slotmap.md の章別ファイル化 (`slotmap_KEI.md` / `slotmap_KEN.md`)

---

## §6. 次セッション着手時の手順 (PDF 配置後)

xnh が KEN PDF を配置した次セッションの最初に、agent が実施する手順:

### §6.1 必須確認手順

```
1. `Get-ChildItem inputs/tx-pdfs/ -File` で新規 PDF を確認
   → KEN001.pdf (または 331.pdf 等の連番継続) が見つかること
2. Read tool で `docs/session-ken-k1-design.md` (本書) を読み込み
   → §2.3 確定事項 F-1〜F-8 を再確認
3. Read tool で `templates/KTX_template_slotmap.md` §5.11 §13 を読み込み
   → X/Y/Z 比較で Y (KEN) 推奨が再確認できる
4. 本書 §4 K-2 着手プロトコル に従って実装に直行
```

### §6.2 K-2 着手の最初のプロンプト雛形 (xnh 提示用)

```
KEN K-2 を着手してください。
docs/session-ken-k1-design.md の K-2 着手プロトコル (§4) に従って、
9 工程を順次実施し、KEN001 を完走させてください。

CP1-CP5:
- CP1: 326-330 byte-identical 維持 (regression ゼロ)
- CP2: check_template_sync.py exit 0 維持
- CP3: 既存 validate_content all PASS 維持
- CP4: KEN001 が render + structure + content の全 stage PASS
- CP5: slotmap §6.1 §X 5 項目記入

【禁止】
- canonical/KTX301.html を編集・コピー元にしない (PATCH §1 遵守)
- 326-330 の問題 JSON / template / schema 構造を破壊しない
- explanation 不明時は null のまま提出 (PATCH §1 末尾規定)
```

---

## §7. K-1 段階の最終チェックリスト

- [x] 案 β 採用確定 (本書 §2.2)
- [x] subject field 仕様確定 (optional, default="KEI", enum 7 科目)
- [x] crime field 扱い確定 (rename しない、description 汎用化)
- [x] 命名規約確定 (`outputs/000_TX/憲TX/憲TX{NNN}.html`, `problems/KEN{NNN}.json`)
- [x] 問題番号体系確定 (KEN001 から開始)
- [x] slotmap 構成確定 (§6 を既存 slotmap に追記)
- [x] signature 構築方針確定 (条文番号 + 判例略称ベース、論点単位 dict)
- [x] canonical 扱い確定 (KEN 用不要、KTX301 を構造参考として残置)
- [x] 想定リスク R1-R8 整理済
- [x] K-2 着手プロトコル 9 工程確定 (本書 §4.2)
- [x] K-3 展開プロトコル確定 (本書 §5)
- [x] 次セッション手順確定 (本書 §6)
- [ ] **KEN PDF 投入** (← xnh のアクション待ち)

---

## §8. K-1 完了宣言

本書 §1〜§7 の内容を以て、**KEN 展開 K-1 設計フェーズは公式 close** とする。

次のアクション:

1. **xnh**: `inputs/tx-pdfs/` に KEN PDF を配置 (1 件以上)
2. **次セッション agent**: 本書を読み込み、K-2 着手プロトコル (§4) に従って実装

本書は K-2 着手後も参照される設計合意の永続記録。K-2 完了後は `docs/session-ken-bootstrap.md` が完了報告として加わるが、本書は **設計合意のレファレンス** として残置する。

326-330 シリーズ (§5.11 公式 close) と KEN K-1 設計確定 (本書) を以て、本セッションは公式 close。
