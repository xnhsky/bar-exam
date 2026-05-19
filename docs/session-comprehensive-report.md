# セッション総合報告: 7 科目展開 + 14 件完走

**日時**: 2026-05-19
**スコープ**: 6 科目 PDF 投入から累計 14 件完走までの全工程

---

## エグゼクティブサマリ

| 指標 | 開始時 | 終了時 | 増分 |
|---|---|---|---|
| 完走問題数 | 5 件 (KEI 326-330) | **14 件** | **+9** |
| 対応科目数 | 1 (KEI) | **7** (KEI/KEN/MIN/SYO/MINS/KEIS/GSE) | **+6** |
| 出題形式数 | 5 | **8** | **+3** (fill-in / ox-grid-3+comb-8 / fillin8) |
| テンプレ本数 | 5 | **8** | **+3** |
| slotmap 行数 | 3,267 | **3,820** | +553 (1.17 倍) |
| docs 数 | 7 | **11** | +4 |

全 CP1-CP7 通過、既存資産 byte-identical 完全維持、失敗 0 件。

---

## 時系列フェーズ

### Phase 1: 環境セットアップ (zip 展開 + リネーム)

- `Claude Code科目別検証用.zip` から 6 科目 PDF を `inputs/tx-pdfs/` に配置・リネーム
- 命名: KEN/MIN/SYO/MINS/KEIS/GSE (科目略称)

### Phase 2: K-2 基盤改修 (subject namespace 化)

| Phase | 内容 | 結果 |
|---|---|---|
| A | schema/render.py/validate_content.py に subject パラメータ化 | CP1-CP5 通過 |
| B | slotmap §6 (subject namespace 仕様) を本文化 | 3,267 → 3,423 行 |
| C (初動) | 6 PDF 画像読解 → 想定構造との乖離検出 → 停止 | 3 PDF 未対応形式判明 |

**停止条件発火**: 当初前提「1 PDF = 多問題、1 ページ = 1 問題」に対し、実構造は「1 PDF = 1 問題 (Q ページ + A ページ)」。さらに KEN/KEIS/GSE が未対応形式 (fill-in / fill-in+組合せ / ox-grid-3+組合せ-8) と判明。判断分岐 4 択を提示。

### Phase 3: 選択肢 A (MIN/SYO/MINS の 3 件処理)

- 採用: MIN001 (combination-5、信義則と権利濫用) / SYO001 (combination-5、定款の目的) / MINS001 (multi-select-5、非訟事件)
- 保留: KEN/KEIS/GSE (未対応形式)
- (b) refactor 発火条件充足を判定、3 選択肢 (X/Y/Z) を提示

### Phase 4: 選択肢 X (6→7 本目テンプレ追加)

| Phase | 内容 | 結果 |
|---|---|---|
| X-A | slotmap §6.6 (fill-in) + §6.7 (ox-grid-3+combination-8) 設計 | +241 行 |
| X-B | 6 本目 `KTX_template_fillin.html` (msel5 派生) + KEN001 完走 | KEIS001 は §6.6b 繰越 |
| X-C | 7 本目 `KTX_template_ox3comb8.html` (comb5 派生) + GSE001 完走 | 10 件完走 |

### Phase 5: §6.6b (8 本目 fillin8、KEIS 対応)

| Phase | 内容 | 結果 |
|---|---|---|
| Z-A | slotmap §6.6b 設計 (comb5 派生、single-choice 機構流用) | +130 行 |
| Z-B | 8 本目 `KTX_template_fillin8.html` 新設 | 最小改修 (validate_*.py は無改修) |
| Z-C | KEIS001 完走 | 11 件、全 13 想定問題消化完了 |

### Phase 6: 追加 3 件 (303/304/305)

- 303 (H26-20、ox-grid-5、詐欺・横領・盗品等の交錯) → P2
- 304 (予備 H25-8、multi-select-5 K=1、詐欺の罪) → P1
- 305 (共通 R5-10、fillin8、詐欺罪) → P1

---

## 完走 14 件 最終一覧

| # | ID | 科目 | 出典 | 形式 | template | 正答率 | パターン | HTML パス |
|---|---|---|---|---|---|---|---|---|
| 1 | 326 | 刑法 | H29-12 | ox-grid-5 | KTX_template.html | 47% | P2 | `outputs/tx/刑TX/刑TX326.html` |
| 2 | 327 | 刑法 | - | ox-grid-4 | KTX_template_ox4.html | 81% | P1 | `outputs/tx/刑TX/刑TX327.html` |
| 3 | 328 | 刑法 | R7-19 | multi-select-5 | KTX_template_msel5.html | 56% | P2 | `outputs/tx/刑TX/刑TX328.html` |
| 4 | 329 | 刑法 | - | single-choice-5 | KTX_template_sc5.html | - | - | `outputs/tx/刑TX/刑TX329.html` |
| 5 | 330 | 刑法 | 予備 H23-10 | combination-5 | KTX_template_comb5.html | 84% | P1 | `outputs/tx/刑TX/刑TX330.html` |
| 6 | MIN001 | 民法 | 予備 H20-1 | combination-5 | KTX_template_comb5.html | 95% | P1 | `outputs/tx/民TX/民TX001.html` |
| 7 | SYO001 | 商法 | 予備 H19-37 | combination-5 | KTX_template_comb5.html | 32% | P3 | `outputs/tx/商TX/商TX001.html` |
| 8 | MINS001 | 民訴 | 予備 H19-54 | multi-select-5 | KTX_template_msel5.html | 82% | P1 | `outputs/tx/民訴TX/民訴TX001.html` |
| 9 | KEN001 | 憲法 | 予備 H19-1 | fill-in | **KTX_template_fillin.html** | 30% | P3 | `outputs/tx/憲TX/憲TX001.html` |
| 10 | GSE001 | 行政法 | 予備 R4-13 | ox-grid-3+comb-8 | **KTX_template_ox3comb8.html** | 59% | P2 | `outputs/tx/行政TX/行政TX001.html` |
| 11 | KEIS001 | 刑訴 | 予備 H18-21 | fillin8 | **KTX_template_fillin8.html** | 88% | P1 | `outputs/tx/刑訴TX/刑訴TX001.html` |
| 12 | 303 | 刑法 | H26-20 | ox-grid-5 | KTX_template.html | 50% | P2 | `outputs/tx/刑TX/刑TX303.html` |
| 13 | 304 | 刑法 | 予備 H25-8 | multi-select-5 (K=1) | KTX_template_msel5.html | 70% | P1 | `outputs/tx/刑TX/刑TX304.html` |
| 14 | 305 | 刑法 | 共通 R5-10 | fillin8 | KTX_template_fillin8.html | 71% | P1 | `outputs/tx/刑TX/刑TX305.html` |

---

## 8 本立て template 最終構成

| # | template | base | 形式 | 用途 | 行数 |
|---|---|---|---|---|---|
| 1 | KTX_template.html | (元祖) | ox-grid-5 | KEI 326, 303 | 2,909 |
| 2 | KTX_template_ox4.html | base 派生 | ox-grid-4 | KEI 327 | 2,908 |
| 3 | KTX_template_msel5.html | base 派生 | multi-select-5 | KEI 328 / MINS001 / KEI 304 | 2,909 |
| 4 | KTX_template_sc5.html | base 派生 | single-choice-5 | KEI 329 | 2,919 |
| 5 | KTX_template_comb5.html | base 派生 | combination-5 | KEI 330 / MIN001 / SYO001 | 2,933 |
| 6 | **KTX_template_fillin.html** | msel5 派生 | fill-in (N=5) | KEN001 | 2,908 |
| 7 | **KTX_template_ox3comb8.html** | comb5 派生 | ox-grid-3+comb-8 | GSE001 | 2,877 |
| 8 | **KTX_template_fillin8.html** | comb5 派生 | fillin8 (8 blanks+5 options) | KEIS001 / KEI 305 | 2,907 |

**設計原則**:
- 同期義務セクション (head/css/body_pre_toc/marker_legend/part_c_d/footer_spec/js) は全 8 本 byte-identical
- 差分許容セクション (toc/pre_part_a/part_a/a2/part_b/basis) のみ形式別カスタム
- `check_template_sync.py` で 8 本立て exit 0 維持

---

## 主要な技術的変更

### スクリプト / スキーマ拡張

| ファイル | 変更内容 |
|---|---|
| `scripts/render.py` | SUBJECT_TO_JP / resolve_arg / get_output_path 追加、TEMPLATE_PATHS に 3 形式追加、_format_answer に dict 対応 + K=1 末尾カンマ、CHOICE_A-E 事前 fill、COMBO 1-8 拡張 |
| `scripts/validate_content.py` | SIGNATURE_REGISTRY 二段化、CRIME_SIGNATURES alias 維持、negative_check 引数化、dict 答えの positive_check 対応 |
| `scripts/validate_structure.py` | _derive_cv_info に fill-in / ox3comb8 mode 追加、S73 / S79 を mode 別分岐、K=1 末尾カンマを multi 認識 |
| `scripts/check_template_sync.py` | TEMPLATE_FILES に 3 件追加、表示文言 "all N match" 動的化、INTENTIONAL_DIFFS note 更新 |
| `schema/problem.schema.json` | subject field 追加、instruction_type enum 3 値追加、answer oneOf に object 追加、Choice.label 拡張、Combination.label/maxItems 拡張 |

### 新規ツール

- `scripts/pdf_to_png.py`: 画像ベース PDF を Claude image understanding に渡すための補助 (pymupdf 依存、zoom=4.0)
- `scripts/build_fillin_template.py` / `build_ox3comb8_template.py` / `build_fillin8_template.py`: 新テンプレを既存テンプレから派生生成する補助

---

## CP gate 通過証跡

| CP | 内容 | 通過状況 |
|---|---|---|
| CP1 | 既存 5 本 template SHA256 不変 | ✅ 全フェーズで照合一致 |
| CP2 | 326-330 byte-identical | ✅ 多回照合 + 再 render 後も一致 |
| CP3 | MIN001/SYO001/MINS001 byte-identical | ✅ |
| CP4 | KEN001/GSE001/KEIS001 byte-identical | ✅ |
| CP5 | check_template_sync.py exit 0 | ✅ 8 本立て対応 |
| CP6 | 全 14 件 render + 二段検証 PASS | ✅ |
| CP7 | slotmap §6 / §6.6 / §6.7 / §6.6b 本文化 | ✅ 3,820 行 |

---

## 想定外の挙動 (O/Y/Z 系列、抜粋)

| Code | 内容 | 対応 |
|---|---|---|
| O-1 | PDF が 1 ファイル = 1 問題構造 (当初想定と異なる) | slotmap §6 §3.1 を訂正版に書換 |
| O-5 | PowerShell CP932 で UnicodeEncodeError | CLAUDE.md に PYTHONIOENCODING=utf-8 注記追加 |
| O-7 | verdict_label enum を「該否」セマンティクスで読替運用 | 既存 enum 維持、将来の拡張余地として記録 |
| Y-1 | KEIS の 8 blanks 問題 | §6.6b として独立設計、Phase Z で完走 |
| Z-1 | KEIS は単純 fill-in ではなく「fill-in 表示 + single-choice」ハイブリッド | comb5 派生で fillin8 を実装、validate 改修不要 |
| 追加 | multi-select-5 K=1 の cv "3" が single mode 誤判定 | _format_answer に末尾カンマ機構導入、3 ファイル同期 |
| 追加 | 詐欺・横領・盗品等の交錯問題で他罪 signature 検出 | allowed_cross_refs で正当な比較言及を許可 |

---

## docs 構成 (11 ファイル)

```
docs/
├── ox4-design-investigation-326-330-session.md     (32 KB)
├── session-326-327-completion.md                   (13 KB)
├── session-328-completion.md                       (21 KB)
├── session-329-completion.md                       (24 KB)
├── session-330-completion.md                       (27 KB)
├── session-ken-k1-design.md                        (17 KB)
├── session-warn-complete.md                        (31 KB)
├── session-6subjects-expansion.md                  (33 KB) ← 本セッション
├── session-6subjects-complete.md                   (11 KB) ← 本セッション
├── session-6subjects-final.md                      (12 KB) ← 本セッション
└── session-comprehensive-report.md                 (本ファイル) ← 本セッション
```

---

## 残課題と次回方針

### 残課題

**なし**。当初投入の 6 PDF + 後続 3 PDF (303-305) = 全 9 PDF 消化完了。CP1-CP7 全通過、回帰なし。

### 推奨される次の方向性

1. **既存科目の問題追加** (KEI 306+、各科目 002+)
   - テンプレ・パイプライン完成済、追加コストは JSON 作成のみ
   - 2 件目以降の問題追加で SIGNATURE_REGISTRY[科目] の cross-topic 検出が機能し始める
   - 最も効率的かつ低リスク

2. **別科目の本格展開**
   - 現在 N=1 件の 6 科目 (KEN/MIN/SYO/MINS/KEIS/GSE) を体系的に増やす
   - 司法試験/予備試験の予想範囲ごとに横断展開

3. **(b) refactor 再評価**
   - 8 本立てに到達済、テンプレ追加路線の限界点は当面なし
   - 一般化リファクタ (partial 合成 / JS 動的レンダリング) は形式 #9 以降の追加圧力が継続する場合のみ検討

**agent 推奨**: 上記 1 (既存科目の問題追加) — テンプレ資産が完成しており、追加コストが最小。

---

**全工程通じて**:
- 既存資産の byte-identical 維持を最優先 (CP1-CP4)
- 新形式追加は「ベース派生 + 差分許容セクション置換」で同期義務領域を不変に
- 不明形式遭遇時は停止して報告 (拙速な実装を回避)
- 全変更を slotmap.md に本文化、再現可能な設計記録を残存
