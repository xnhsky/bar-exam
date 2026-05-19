# セッション完了記録 — WARN 4 系統完全消滅 (§5.7 / §5.6 / §5.5 連続消化)

## メタ情報

- **作成日**: 2026-05-18
- **対象セッション**: WARN 系統消化シリーズ (整備期)
- **本書の位置づけ**: 326-330 シリーズの **WARN 完全消滅達成記録**。
  先行する 5 ファイル (調査 1 + 完了報告 4) に続く第 6 弾の整備期総括。
- **達成事項**: 326-330 全 5 件で **ERROR 0 / WARN 0** を達成。

---

## 1. 完走した 3 案件

| 案件 | 内容 | 結果 |
|---|---|---|
| **§5.7** | footer-spec ktx301-canon feature-tag 追加 (5 templates 同期、S51 解消) | ✅ 完走 (前セッション既完了、CP1-CP4 verify 通過) |
| **§5.6** | choice-section professor sub-card 追加 (24 entries、S17 解消) | ✅ 完走 (CP1-CP4 全 PASS) |
| **§5.5** | PART D drill-block 12 件 × 5 = 60 entries 本格実装 (S14 解消、S26 副次解消) | ✅ 完走 (CP1-CP4 全 PASS) |

### 各案件の CP1-CP4 通過状況

| CP | §5.7 | §5.6 | §5.5 |
|---|---|---|---|
| **CP1** check_template_sync exit 0 | ✅ | ✅ | ✅ |
| **CP2** WARN 件数期待値通り減少 | ✅ (326:7→6 / 327:6→5 / 328-330:7→6) | ✅ (326:6→1 / 327:5→1 / 328-330:6→1) | ✅ (全件 1→0) |
| **CP3** validate_content PASS 維持 | ✅ (全 5 件) | ✅ | ✅ |
| **CP4** §X 5 項目 実測値記入 | ✅ | ✅ | ✅ |

---

## 2. 326-330 全件の WARN 件数推移表

| 問題 ID | 初期 (326-330 完走時) | §5.8 後 (S71-AP33 部分消化) | §5.7 後 (S51 消化) | §5.6 後 (S17 消化) | §5.5 後 (S14 消化) |
|---|---:|---:|---:|---:|---:|
| **326** | 8 | 7 | **6** | **1** | **0** ✅ |
| **327** | 7 | 6 | **5** | **1** | **0** ✅ |
| **328** | 7 | 7 (S71 元から無) | **6** | **1** | **0** ✅ |
| **329** | 7 | 7 (S71 元から無) | **6** | **1** | **0** ✅ |
| **330** | 7 | 7 (S71 元から無) | **6** | **1** | **0** ✅ |

→ **5 形式すべてで ERROR 0 / WARN 0 を達成**。WARN 4 系統 (S14 / S17×N / S51 / S71-AP33) 完全消滅。

### WARN 系統別の消滅履歴

| WARN ID | 内容 | 326 | 327 | 328 | 329 | 330 | 消滅セッション |
|---|---|---|---|---|---|---|---|
| **S71-AP33** | answer-instruction 文言相違 | 8→7 | 7→6 | 0 | 0 | 0 | §5.8 (前セッション) で 326/327 から消滅、328-330 は新形式採用時に自然消滅 |
| **S51** | ktx301-canon feature-tag 欠落 | 7→6 | 6→5 | 7→6 | 7→6 | 7→6 | **§5.7** (本セッション) で 5 本同期追加 |
| **S17×N** | choice professor sub-card 欠落 | 6→1 | 5→1 | 6→1 | 6→1 | 6→1 | **§5.6** (本セッション) で 24 entries 追加 |
| **S14** | drill-block 数 = 0 (期待値 12) | 1→0 | 1→0 | 1→0 | 1→0 | 1→0 | **§5.5** (本セッション) で 60 entries 追加 |

---

## 3. 編集 / 新規作成ファイル一覧

| ファイル | 種別 | 初期 (整備期開始時) | 最終 | Δ |
|---|---|---:|---:|---:|
| `schema/problem.schema.json` | 既存編集 | 194 行 / 7,294 B | **254 行 / 9,264 B** | +60 行 / +1,970 B |
| `scripts/render.py` | 既存編集 | 242 行 / 9,516 B | **266 行 / 10,815 B** | +24 行 / +1,299 B |
| `scripts/check_template_sync.py` | 触らず | 472 行 / 18,255 B | 472 行 / 18,255 B | 0 |
| `scripts/validate_structure.py` | 触らず | 1,022 行 / 44,356 B | 1,022 行 / 44,356 B | 0 (検査ロジックは既に正しく、内容供給だけで WARN 消滅) |
| `scripts/validate_content.py` | 触らず | 276 行 / 9,391 B | 276 行 / 9,391 B | 0 |
| `templates/KTX_template.html` | 既存編集 | 2,788 行 / 95,298 B | **2,942 行 / 106,470 B** | +154 行 / +11,172 B (PART D + 5 professor sub-cards + ktx301-canon) |
| `templates/KTX_template_ox4.html` | 既存編集 | 2,751 行 / 93,882 B | **2,899 行 / 104,838 B** | +148 行 / +10,956 B |
| `templates/KTX_template_msel5.html` | 既存編集 | 2,754 行 / 93,835 B | **2,908 行 / 104,989 B** | +154 行 / +11,154 B |
| `templates/KTX_template_sc5.html` | 既存編集 | 2,770 行 / 94,478 B | **2,924 行 / 105,632 B** | +154 行 / +11,154 B |
| `templates/KTX_template_comb5.html` | 既存編集 | 2,778 行 / 94,894 B | **2,932 行 / 106,048 B** | +154 行 / +11,154 B |
| `templates/KTX_template_slotmap.md` | §5.5/§5.6/§5.7 本文 + §X 実測 | 2,182 行 / 132,774 B | **2,621 行 / 155,832 B** | +439 行 / +23,058 B |
| `problems/326.json` | 既存編集 | 57 行 / 6,574 B | **91 行 / 13,572 B** | +34 行 / +6,998 B (5 professor + 12 drill) |
| `problems/327.json` | 既存編集 | 49 行 / 5,121 B | **79 行 / 11,071 B** | +30 行 / +5,950 B (4 professor + 12 drill) |
| `problems/328.json` | 既存編集 | 57 行 / 5,223 B | **91 行 / 11,676 B** | +34 行 / +6,453 B |
| `problems/329.json` | 既存編集 | 72 行 / 5,554 B | **106 行 / 12,199 B** | +34 行 / +6,645 B |
| `problems/330.json` | 既存編集 | 65 行 / 7,783 B | **99 行 / 14,835 B** | +34 行 / +7,052 B |
| `docs/session-warn-complete.md` | **新規作成** (本書) | — | (本書) | — |

### 触っていないもの

- `canonical/KTX301.html` (構造参考として固定)
- `CLAUDE.md` (前セッションで §5.10 §「CLAUDE.md / README への追記項目」記載済、本セッションで追加更新なし)
- `scripts/validate_structure.py` / `validate_content.py` (検査ロジックは正確で、データ供給だけで WARN 消滅)

---

## 4. slotmap.md の累計成長

| 段階 | 行数 | bytes |
|---|---:|---:|
| 初期 (326 ox-grid-5 着手前) | 451 | 27,500 (推定) |
| §5.1-§5.4 + §5.10 (326-330 シリーズ + CI 化基盤) | 1,284 | 79,182 |
| + §5.8 (S71-AP33 案件本文化 + 実装) | 1,898 | 115,921 |
| + §5.7 (S51 案件本文化 + 実装) | 2,118 | 132,774 |
| + §5.6 + §5.5 (本セッション、S17/S14 案件本文化 + 実装) | **2,621** | **155,832** |

→ 初期 451 行 → 最終 **2,621 行** (約 **5.81 倍** に成長)。設計合意ベースの蓄積。

---

## 5. docs/ の最終構成

| ファイル | サイズ | 役割 |
|---|---|---|
| `ox4-design-investigation-326-330-session.md` | 32,810 B | 第 1 弾：初期設計調査 |
| `session-326-327-completion.md` | 13,197 B | 第 2 弾：326/327 完走 |
| `session-328-completion.md` | 21,351 B | 第 3 弾：328 完走 |
| `session-329-completion.md` | 24,254 B | 第 4 弾：329 完走 |
| `session-330-completion.md` | 27,368 B | 第 5 弾：330 完走 + シリーズ総括 |
| `session-warn-complete.md` | (本書) | **第 6 弾：WARN 完全消滅** |

→ docs/ は 5 → **6 ファイル** に成長。

---

## 6. 想定外の挙動 (全件列挙、透明性高く)

### F-1. S26 (○×比率不均衡) の新規発火

**発生段階**: §5.5 実装中、5 templates に 12 drill-block 構造を配置直後の段階で。
JSON drill_blocks が空の状態で render を実行したところ、各 drill の
`data-correct-value` が空文字のまま展開され、validate_structure が
**S26 (○×比率不均衡: ○=0, ×=0, 期待値 6:6) を新規発火**。

**原因**: S26 は PART D の self-check-quiz で集計を行うため、template 構造の
存在だけでなく実際の drill content (data-correct-value) が ○ または × の正しい
比率で供給されることが必要。slotmap §5.5 設計時点では S26 を想定外として
明示していなかった (S14 のみを meta-target としていた)。

**対応**: 60 件の drill_blocks に ○ : × = 6 : 6 のバランスで correct を割り当て。
各 problem で:
- 326 / 327 / 328: 6:6
- 329: 初期 8:4 → 2 問を × 表現に書き換えて 6:6
- 330: 初期 9:3 → 3 問を × 表現に書き換えて 6:6

調整後、S26 完全消滅、真の WARN ゼロ達成。

### F-2. 全角括弧の半角誤入力 (前回 §5.8 セッションで発生、本セッションでは未発生)

参考まで継承: §5.8 で `「1(正)」` (半角) を入力したが、validator regex は
全角 `「1（正）」` を期待しており、Grep で即検出 → 全角に修正。本セッションでは
類似ミスなし。

### F-3. 想定外の挙動はそれ以外なし

- §5.7 / §5.6 / §5.5 の各案件で、CI safety net (check_template_sync.py) は **常に
  exit 0** を維持。意図差分 dict 操作は **0 回**。
- 5 templates 同期追加が常に sync_required を破壊せず推移。
- byte-identity は意図された変更のみで増大、想定外の構造変化なし。

---

## 7. CI safety net の効果 (3 案件での実績)

| 案件 | check_template_sync.py 実行回数 | exit 0 維持 | false positive | 真の sync 違反検出 | dict 操作 |
|---|---:|---|---:|---:|---|
| §5.7 | 2 回 (修正前 + 修正後) | ✅ | 0 件 | 0 件 | 不要 |
| §5.6 | 2 回 | ✅ | 0 件 | 0 件 | 不要 |
| §5.5 | 2 回 (中間 + 最終) | ✅ | 0 件 | 0 件 | 不要 |

→ **3 案件すべてで sync 違反は 1 件も発生せず**、CI safety net は完璧に機能。
意図差分 dict のメンテナンスも不要だった (5 templates 同期追加で sync_required
セクションが破壊されない設計が功を奏した)。

これにより slotmap §5.10 §「CI 化スクリプトの設計合意」が **実用化された**ことが
3 案件の実績で実証された。

---

## 8. 残る §5 案件 (§5.9 のみ) への引き継ぎ事項

### §5.9 (CRIME_SIGNATURES 拡張) の概要

- **対象**: `scripts/validate_content.py` の `CRIME_SIGNATURES` dict に **信書隠匿罪 / 毀棄罪 / 損壊罪** 等の罪を正式追加。
- **現状**: 329 / 330 で `allowed_cross_refs: ["信書隠匿罪", "窃盗罪"]` 等を明示しているが、`CRIME_SIGNATURES` に未登録のため `allowed_cross_refs` の意味は documentation のみ (実効性なし)。
- **目的**: 横断的な辞書整備で、新規問題に対する negative check の精度向上。
- **影響範囲**: validate_content.py 単独 (data 拡張のみ、ロジック変更なし)。
- **規模見積**: 30 分以下 (新罪の signature 候補語をリストアップして dict に追加)。
- **既存 problems への影響**: 326-330 すべて `allowed_cross_refs` が既に設定済みなので、自動的に skip され regression なし (slotmap §5.3 §7 / §5.4 §「crime / source 表記揺れ」で予告済み)。

### 形式 #6 入口での AND 条件再判定

- 5 本立て template + CI safety net + WARN 0 達成の安定状態を維持しつつ、形式 #6 (331+ PDF または ranking / fill-in confirmed) が入ったときに **slotmap §5.4 §7 の AND 条件 ①/②** を再判定する義務がある。
- 充足時 → (b) refactor 発火、partial 合成 or JS 動的レンダリングへ移行。
- 不充足時 → (a) 6 本目 template 追加で対応継続。

### 331+ 問題追加時の運用フロー

326-330 シリーズで確立した手順:

1. PDF 読込 → 形式判定
2. 既存 5 形式 (ox-grid-5/-4, multi-select-5, single-choice-5, combination-5) のいずれかに該当 → 対応 template + JSON 起こし
3. 該当なし → 新形式設計 (slotmap §5.10+ 案件)
4. JSON で:
   - `professor` 各 choice (slotmap §5.6 必須)
   - `drill_blocks` 12 件 ○:×=6:6 (slotmap §5.5 必須)
5. 検証: render → check_template_sync → validate_structure (WARN 0) → validate_content (PASS)

---

## 9. WARN 完全消滅達成の確認

### 9.1 326-330 全件の最終検証結果

| 問題 ID | render | structure ERROR | structure WARN | content | HTML サイズ |
|---|---|---:|---:|---|---:|
| **326** | ✅ exit 0 | **0** | **0** | ✅ PASS | 121,870 B |
| **327** | ✅ exit 0 | **0** | **0** | ✅ PASS | 116,979 B |
| **328** | ✅ exit 0 | **0** | **0** | ✅ PASS | 117,075 B |
| **329** | ✅ exit 0 | **0** | **0** | ✅ PASS | 117,285 B |
| **330** | ✅ exit 0 | **0** | **0** | ✅ PASS | 120,663 B |

### 9.2 CI safety net 最終状態

- `check_template_sync.py` exit code: **0** (PASS)
- sync 違反: **0 件**
- 5 本立て template の sync_required セクション (head / css / body_pre_toc / marker_legend / part_c_d / footer_spec / js) すべて hash 一致

### 9.3 整備期完了宣言

**326-330 全 5 件で ERROR 0 / WARN 0 を達成**。326-330 シリーズの整備期 (§5.7 + §5.6 + §5.5) は本書をもって完走。

残る §5.9 (CRIME_SIGNATURES 拡張) は **WARN/ERROR を発火させない論理的整合性向上案件**で、次セッションで個別消化推奨。

---

## 10. 本セッション全体の所感メモ (将来参照用)

- **CI safety net の有効性が決定的**: slotmap §5.10 で確立した `check_template_sync.py` が 3 案件すべてで exit 0 を維持し、sync 義務違反を機械的に防いだ。意図差分 dict 操作は不要だった (5 本同期追加が sync_required を破壊しない設計の勝利)。
- **schema oneOf + optional フィールドの拡張パターンが熟成**: views / combinations / professor / drill_blocks がすべて同型 (optional、後方互換) で追加され、既存 5 problems への regression ゼロを維持しながら新機能を積層できた。
- **S26 副次発火を吸収できた**: §5.5 で template だけ配置すると S14 が消える一方で S26 が新規発火する複合的挙動を発見。60 drill 内容を ○:×=6:6 でバランス調整して両方解消。設計時点で S26 を想定外にしていたのは反省点だが、対応で吸収できた。
- **content 質と量の両立**: 24 professor + 60 drill = 84 件の content 生成を約 2 時間で完走。各 entry を学習価値ある質に保ちつつ、context window 効率を考慮した簡潔さで実装。
- **slotmap.md 5.81 倍成長**: 451 行 → 2,621 行 (5.81 倍)。設計合意の蓄積は重く、しかし参照精度が高いため迷いなく実装に進める。次セッション以降も同パターン継続を推奨。
- **326-330 シリーズの完走**: 形式 5 種類 + WARN 4 系統消滅で、シリーズの初期目標を完全達成。331+ への拡張または別科目 (KEN/MIN 等) への展開が次のフェーズ。

---

## 11. §5.9 完走報告 (CRIME_SIGNATURES 拡張、シリーズ最終案件)

### 11.1 §5.9 案件サマリ

| 項目 | 内容 |
|---|---|
| 案件名 | **§5.9** CRIME_SIGNATURES 拡張 |
| 対象 | `scripts/validate_content.py` の dict |
| 追加罪 | **信書隠匿罪 1 件** (signature: `["263条", "信書隠匿"]`) |
| 動機 | 329/330 の `allowed_cross_refs: ["信書隠匿罪"]` の **実効化** (現状 documentation 効果のみ) |
| 規模 | 4 行追加 (dict データのみ、ロジック変更なし) |
| 実装時間 | 約 8 分 (見積 30 分以下から大幅短縮) |

### 11.2 §5.9 CP1-CP4 通過状況

| CP | 内容 | 結果 |
|---|---|---|
| **CP1** | dict 追加のみ (ロジック変更なし) | ✅ L112-115 の 4 行追加のみ、関数定義変更なし |
| **CP2** | 326-330 全件 HTML byte-identical 維持 | ✅ 全 5 件で SHA256 完全一致 (`BEF153E0/9C30BC5E/8AF2A098/1A72A3BF/EEFA038D`) |
| **CP3** | 326-330 全件 validate_content PASS 維持 | ✅ 全 5 件 exit 0、326-328 影響なし、329/330 は allowed_cross_refs 実効化で PASS 維持 |
| **CP4** | slotmap §5.9 §X 5 項目記入完了 | ✅ slotmap.md L1430-1483 で全項目実測値で埋め込み |

### 11.3 事前 Grep 検証 (regression 不可能を実証)

dict 追加前に 326-328 の HTML に新規 signature が出現しないことを確認:

| 問題 ID | "263条" + "信書隠匿" 出現数 | 影響予測 |
|---|---:|---|
| 326 | **0** | 完全不変 |
| 327 | **0** | 完全不変 |
| 328 | **0** | 完全不変 |
| 329 | 47 件 | allowed_cross_refs `["信書隠匿罪"]` で skip → PASS |
| 330 | 10 件 | allowed_cross_refs `["窃盗罪", "信書隠匿罪"]` で skip → PASS |

→ regression 発生の余地ゼロ。実測でも全件 byte-identical 維持を確認。

---

## 12. 本セッションシリーズの最終総括 (326-330 シリーズ完全終了)

### 12.1 完走した案件一覧 (時系列)

| # | 案件 | 内容 | 完走日 |
|---|---|---|---|
| 1 | §5.1 | ox-grid-N 形式分岐 (ox-grid-4 対応) | 2026-05-18 |
| 2 | §5.2 | multi-select-N 形式分岐 (multi-select-5 対応) | 2026-05-18 |
| 3 | §5.3 | single-choice-N 形式分岐 + 【見解】slot 導入 | 2026-05-18 |
| 4 | §5.4 | combination-N 形式分岐 + 【組合せ】slot + 二系統ラベル混在 | 2026-05-18 |
| 5 | §5.10 | template 同期検証スクリプト (check_template_sync.py) | 2026-05-18 |
| 6 | §5.8 | ox-grid 系 answer-instruction 文言の canonical 化 (S71-AP33 解消) | 2026-05-18 |
| 7 | §5.7 | footer-spec ktx301-canon feature-tag 追加 (S51 解消) | 2026-05-18 |
| 8 | §5.6 | choice-section professor sub-card 追加 (S17 解消) | 2026-05-18 |
| 9 | §5.5 | PART D drill-block 12 件本格実装 (S14 解消 + S26 副次解消) | 2026-05-18 |
| 10 | **§5.9** | **CRIME_SIGNATURES 拡張 (信書隠匿罪追加)** | **2026-05-18** ← 本書で完走 |

→ **§5 配下 10 案件すべて完走** (§5.1-§5.10、§5.9 を含む)。

### 12.2 326-330 全 5 問題の最終状態

| 問題 ID | 形式 | crime | answer | HTML サイズ | ERROR | WARN | content |
|---|---|---|---|---:|---:|---:|---|
| 326 | ox-grid-5 | 盗品等罪 | "12222" | 121,870 B | **0** | **0** | ✅ PASS |
| 327 | ox-grid-4 | 盗品等罪 | "2212" | 116,979 B | **0** | **0** | ✅ PASS |
| 328 | multi-select-5 | 盗品等罪 | [1,4] | 117,075 B | **0** | **0** | ✅ PASS |
| 329 | single-choice-5 | 器物損壊罪 | 2 | 117,285 B | **0** | **0** | ✅ PASS |
| 330 | combination-5 | 器物損壊罪 | 3 | 120,663 B | **0** | **0** | ✅ PASS |

→ **5 問題すべてで完全な ERROR 0 / WARN 0 / content PASS 達成**。

### 12.3 累計編集ファイル

| ファイル | セッション開始時 → 最終 |
|---|---|
| `schema/problem.schema.json` | 121 行 → **254 行** (約 2.10 倍) |
| `scripts/render.py` | 187 行 → **266 行** (約 1.42 倍) |
| `scripts/check_template_sync.py` | **新規作成 472 行** |
| `scripts/validate_structure.py` | 944 行 → **1,022 行** (+78 行) |
| `scripts/validate_content.py` | 248 行 → **280 行** (+32 行、§5.9 で +4 行) |
| `templates/KTX_template.html` | 2,788 行 → **2,942 行** |
| `templates/KTX_template_ox4.html` | **新規 2,899 行** |
| `templates/KTX_template_msel5.html` | **新規 2,908 行** |
| `templates/KTX_template_sc5.html` | **新規 2,924 行** |
| `templates/KTX_template_comb5.html` | **新規 2,932 行** |
| `templates/KTX_template_slotmap.md` | 451 行 → **2,848 行** (約 **6.31 倍**) |
| `problems/326.json` | **新規 91 行** |
| `problems/327.json` | **新規 79 行** |
| `problems/328.json` | **新規 91 行** |
| `problems/329.json` | **新規 106 行** |
| `problems/330.json` | **新規 99 行** |
| `CLAUDE.md` | template 編集時の必須手順を追記 |

### 12.4 slotmap.md の最終成長

**初期 451 行 → 最終 2,848 行 (約 6.31 倍)**

§5.9 追記で +227 行 (2,621 → 2,848)、シリーズ累計で +2,397 行。設計合意の累積が
迷いない実装を支えた最大の資産。

### 12.5 docs/ 最終構成 (6 ファイル → 6 ファイル維持)

| ファイル | サイズ | 役割 |
|---|---|---|
| `ox4-design-investigation-326-330-session.md` | 32,810 B | 第 1 弾：初期設計調査 |
| `session-326-327-completion.md` | 13,197 B | 第 2 弾：326/327 完走 |
| `session-328-completion.md` | 21,351 B | 第 3 弾：328 完走 |
| `session-329-completion.md` | 24,254 B | 第 4 弾：329 完走 |
| `session-330-completion.md` | 27,368 B | 第 5 弾：330 完走 + シリーズ総括 |
| `session-warn-complete.md` | (本書) | **第 6 弾：WARN 完全消滅 + §5.9 完走 + 最終総括** |

(docs/session-warn-complete.md は本書 §11-§12 で更新、最終版に)。

### 12.6 残る将来案件 (§5.11+ と形式 #6)

#### §5.11+ 候補 (整備案件、優先度低)

1. **`allowed_cross_refs` 削除整理**: 329/330.json の `allowed_cross_refs` のうち、
   CRIME_SIGNATURES 既登録罪のみのものは削除可能 (本書 §5.9 §3 で保留と明示済)。
   - 329: `["信書隠匿罪"]` → 信書隠匿罪が CRIME_SIGNATURES 登録済となったため削除可
   - 330: `["窃盗罪", "信書隠匿罪"]` → 窃盗罪と信書隠匿罪はいずれも登録済のため削除可
   - 削除する場合、§5.9 で確立した signature trigger と allowed skip の関係を再検証
2. **毀棄罪 / 損壊罪を独立 key として CRIME_SIGNATURES に追加するか判断**: 
   現状は文書等毀棄罪 + 器物損壊罪でカバー、追加の必要性低。
3. **slotmap §5.11+ のスケルトン本文化**: §5.5-§5.9 と同じパターンで設計合意の
   蓄積を継続。

#### 形式 #6 入口での AND 条件再判定 (slotmap §5.4 §7)

- `inputs/tx-pdfs/331.pdf` 以降の追加または `ranking` / `fill-in` 形式の confirmed
  の時点で、(b) refactor 発火条件 AND ①/② を再判定。
- 現時点では両条件とも不充足、(a) 戦略継続が妥当。
- 6 本立て (diff 15 ペア) に到達する場合は CI safety net 下で運用可能だが、それ以上
  の拡張は (b) refactor (partial 合成 or JS 動的レンダリング) への移行を強く検討。

#### 次セッション着手時の最優先項目 (推奨順)

1. **形式 #6 PDF が現れた場合**: slotmap §5.4 §7 の AND 再判定 → (a) / (b) 戦略決定
   → 該当案件の slotmap §5.10+ 設計調査 → 実装
2. **問題追加 (331+) が現れない場合**: §5.11+ 整備案件 (allowed_cross_refs 削除整理
   等) を低優先で進めるか、別科目 (KEN/MIN/SYO/MINS/KEIS/GSE) への展開に着手
3. **別科目展開**: 326-330 シリーズで確立した形式 5 種類 + WARN 解消パターン + CI
   safety net をそのまま KEN/MIN 等に適用可能。schema / template の流用設計を
   slotmap §5.10+ で検討

### 12.7 326-330 シリーズ完全終了の正式宣言

**本書 §11-§12 をもって、326-330 シリーズおよび §5 配下 10 案件 (§5.1-§5.10) の
すべてが完走したことを正式に宣言する。**

- 5 形式 (ox-grid-5 / ox-grid-4 / multi-select-5 / single-choice-5 / combination-5)
  の実装完了
- WARN 4 系統 (S14 / S17×N / S51 / S71-AP33) の完全消滅
- 5 problems 全件で ERROR 0 / WARN 0 / content PASS
- CRIME_SIGNATURES に信書隠匿罪追加 (11 罪体制)
- CI safety net (check_template_sync.py) の確立と運用実証
- slotmap.md の設計合意蓄積 (451 → 2,848 行)
- docs/ 完了報告 6 ファイル体制 (調査 1 + 完了報告 5 + 本書)

次フェーズ (形式 #6 / 別科目 / §5.11+ 整備) への移行準備が整った。

---

## §5.11 326-330 シリーズ最終整備フェーズ — 整備案件判定記録

### §5.11 概要

326-330 シリーズの最終整備フェーズとして以下 2 件の cleanup 案件を検討し、両方とも **見送り** と判定した。本セクションはその判断記録。

| # | 案件 | 判定 |
|---|---|---|
| (a) | 329/330.json の `allowed_cross_refs` 削除整理 | **見送り** |
| (b) | validate_content.py CRIME_SIGNATURES への 毀棄罪 / 損壊罪 独立 key 追加 | **見送り** |

→ **実 file 変更ゼロ**。slotmap.md への §5.11 セクション追加と、本書への本追記のみが成果物。

### §5.11 判定根拠サマリ

#### 案件 (a): ACR 削除整理 → 見送り

§5.9 で 信書隠匿罪 を CRIME_SIGNATURES に登録した結果、`allowed_cross_refs` field の意味が質的に変化した:

- **§5.9 以前**: ACR は documentation only (no-op filter)
- **§5.9 以後**: ACR は **signature skip filter として実効性を持つ**

`validate_content.py negative_check` は `skip = set(ACR) | {current_crime}` で skip 集合を構築する。329/330 (crime="器物損壊罪") の HTML には信書隠匿罪条文 (263条 / 信書隠匿) が題意上頻出するため、ACR を削除すると signature 検査が trigger し **validate_content が FAIL する**。

これは §5.9 §12.6 で残した「将来 cleanup 案件として削除可」との記述が **誤り** だったことを意味し、slotmap §5.11 §7 で公式訂正した。

#### 案件 (b): 毀棄罪 / 損壊罪 独立 key 化 → 見送り

候補 signature (`"毀棄"`, `"損壊"`, `"毀棄罪"`, `"損壊罪"`) はすべて一般語または複合罪名の部分一致対象であり、誤検出多発リスクが高い。既存 3 key (文書等毀棄罪 / 器物損壊罪 / 信書隠匿罪) で 326-330 の毀棄損壊系カバー範囲は十分。追加すれば既存 PASS 問題が FAIL に転じる逆効果。

### §5.11 CP1-CP5 維持確認 (実測値)

| CP | 内容 | 維持状態 (実測) |
|---|---|---|
| CP1 | schema/template/render/validate ロジック変更禁止 | ✅ 一切変更なし |
| CP2 | check_template_sync.py exit 0 維持 | ✅ exit 0 確認済 |
| CP3 | 326-330 byte-identical 維持 | ✅ SHA256 全件不変 |
| CP4 | validate_content all PASS 維持 | ✅ 326-330 全件 PASS 確認済 |
| CP5 | slotmap §5.11 §X 5 項目記入 + §13 X/Y/Z 比較 | ✅ slotmap.md +419 行 (2,848 → 3,267) |

実測 SHA256 chain (先頭 16 桁):

| ID | SHA256 (head16) |
|---|---|
| 326 | BEF153E033A09A21 |
| 327 | 9C30BC5EA89F5BFF |
| 328 | 8AF2A098FBE1BB70 |
| 329 | 1A72A3BF0C6AEEE4 |
| 330 | EEFA038D7A3E2EFB |

### §5.11 X/Y/Z 次フェーズ 3-way 比較サマリ

| 候補 | 学習価値 | 汎用性 | 総合 |
|---|---|---|---|
| X (§5.12+ cleanup) | 低 | 低 | △ |
| **Y (KEN = 憲法 展開)** | **高** | **高** | **◎ 推奨** |
| Z (形式 #6 待機) | ゼロ | ゼロ | △ |

#### 推奨: 候補 Y - 憲法 (KEN) 展開

理由 (詳細は slotmap §5.11 §13 参照):

1. xnh の本来目的（予備試験対策コンテンツ整備）への寄与最大
2. 326-330 で確立した 7 種の再利用可能資産 (5 format / schema oneOf / S1-S77 / CI safety net / 12 drill / professor sub-card / CP1-CP5 rules) の活用率最大
3. signature namespace が刑法と完全分離 → CRIME_SIGNATURES 拡張は dict 追加のみで cleanup 不要
4. 仮に途中中断しても完成済み問題は独立 valid

次セッション開始時のチェックリスト (slotmap §5.11 §13 参照):

- [ ] `inputs/tx-pdfs/` 配下に憲法 PDF が存在するか確認
- [ ] 存在する場合: 問題番号と正答率を抽出して 5 問分の format 計画を立案 (slotmap §5.13 として書き起こし)
- [ ] 存在しない場合: xnh に PDF 投入を依頼
- [ ] schema 拡張要否を検討 (crime field の汎用化 or 別 schema 分岐)
- [ ] CRIME_SIGNATURES の科目別分割設計を提案

### §5.11 326-330 シリーズ 公式 close 宣言

§5.4 (330 完走) から §5.11 (整備案件判定) まで、326-330 シリーズに関する全議論が決着した:

- 5 問完成 (326-330) + 5 種 format + WARN 4 系統消化 + CI safety net + signature dict 拡張 (信書隠匿罪) + 整備案件判定
- byte-identity chain 完全保持 (本書記録 SHA256 が永続有効)
- slotmap.md = 3,267 行 / 193,683 B、docs/ = 完了報告 7 ファイル体制 (本書含む)

**326-330 シリーズは本セクションを以て公式 close とする**。次セッションは 候補 Y (憲法展開) を推奨方針として継続するか、xnh の指示で X/Z へ切り替えるかを選択する。

---

## KEN 展開 K-1 設計確定報告 (本セッション末追記)

### 経緯

§5.11 公式 close 直後、xnh の指示により次フェーズとして **候補 Y (KEN = 憲法展開)** を選択。本セッション内で K-1 設計調査を実施 (ファイル変更ゼロ条件)、namespace 分離 3 案 (α / β / γ) を比較評価し **案 β (パラメータ化 + 後方互換 default)** を採用、K-2 着手プロトコルまで合意した。

### K-1 で確定したこと

| 項目 | 確定値 |
|---|---|
| namespace 設計 | **案 β** (単一 codebase + subject パラメータ化、案 γ 升格パス保持) |
| `subject` field | optional, enum=["KEI","KEN","MIN","SYO","MINS","KEIS","GSE"], default="KEI" |
| `crime` field | rename しない、description のみ汎用化 (「分類キー (罪名 / 論点 / 権利分類)」) |
| 出力 dir / prefix | `outputs/tx/憲TX/憲TX{NNN}.html` (CLAUDE.md 既定) |
| problem JSON 命名 | `problems/KEN{NNN}.json` |
| 問題番号体系 | **KEN001 から開始** (科目別 namespace 連番) |
| slotmap 構成 | §6 を既存 slotmap.md に追記 (1 ファイル維持、5 科目目以降で別ファイル化検討) |
| signature 構築方針 | 条文番号 + 判例略称ベース、論点単位 dict (一般語禁止 = §5.11 教訓継承) |
| canonical 扱い | KEN 用不要、KTX301 を構造参考として残置 (PATCH §1 維持) |
| K-2 工程 | 9 工程約 1 セッション (schema 拡張 + render パラメータ化 + SIGNATURE_REGISTRY 拡張 + KEN001 完走 + slotmap §6.1 + docs/session-ken-bootstrap) |
| K-3 規模 | KEN002-005 batch 約 2-3 セッション |

### K-1 で未確定 = K-2 着手後の判断事項

- KEN signature dict の具体内容 (条文 / 判例 / 学説の具体的列挙)
- KEN001 PDF の形式判定 (5 形式中どれに該当するか)
- 追加形式 (fill-in / ranking) の要否
- override_pattern P1-P5 の KEN 仕様適用 (正答率帯と色パターン対応)
- subjects/ 分離 (案 γ への升格) の要否

### 未確定 = PDF 待ち (xnh アクション)

- `inputs/tx-pdfs/` に KEN PDF が **未配置** (現状 326-330.pdf + README.txt のみ)
- xnh が KEN PDF を配置するまで K-2 着手不能 (explanation null は PATCH §1 で fail のため、捏造禁止)

### 想定リスク R1-R8 (継承)

slotmap §5.11 §13 で整理した X/Y/Z 比較を発展させ、KEN 展開固有リスク R1-R8 を docs/session-ken-k1-design.md §3 に整理。主な高影響リスク:

- R1: 326-330 regression → `subject` default="KEI" で抑制
- R2: render.py パラメータ化バグ → 326-330 byte-identical 再生成テストで検出
- R4: KEN PDF 未配置 (現状) → xnh への投入依頼

### 本セッション全体の完成形

326-330 シリーズ完了 (§1〜§5.11 公式 close) + KEN 展開 K-1 設計確定 = 本セッションの公式到達点。

成果物:

- `templates/KTX_template_slotmap.md`: 3,267 行 (初期 451 → +2,816 行)
- `docs/`: 完了報告 7 ファイル体制 (調査 1 + 326-327 完了 + 328 完了 + 329 完了 + 330 完了 + WARN 完了 + KEN K-1 設計)
- 326-330 HTML: byte-identity SHA256 chain 全件保持
- CRIME_SIGNATURES: 11 罪 (§5.9 で信書隠匿罪追加)
- CI safety net: check_template_sync.py 稼働、5 本立て template 同期義務違反検出可能

### 次セッション着手プロトコル

詳細は `docs/session-ken-k1-design.md` §6 参照。要約:

```
1. inputs/tx-pdfs/ に KEN PDF 配置を確認
2. docs/session-ken-k1-design.md を読み込み (設計合意 §2.3 F-1〜F-8 再確認)
3. K-2 着手プロトコル (本書 §4.2 / 9 工程) に従って実装に直行
4. KEN001 完走 + 326-330 regression 確認 + slotmap §6.1 起草
5. docs/session-ken-bootstrap.md で K-2 完了報告
```

**本セッションは KEN K-1 設計確定を以て公式 close**。326-330 シリーズと併せ、本書が示す通り「設計合意 → 実装 → 完了報告」のサイクルが 2 シリーズ目に進む準備が整った。
