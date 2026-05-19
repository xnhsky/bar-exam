# Session: 7 本立て template 移行 — 累計 10 件完走 (KEIS は §6.6b に繰越)

## サマリ

- **日時**: 2026-05-19
- **目的**: 選択肢 X (6→7 本目 template 追加) で KEN/KEIS/GSE の保留 3 件を完走させる
- **進捗**: 
  - Phase X-A: ✅ slotmap §6.6 / §6.7 本文化
  - Phase X-B: ✅ 6 本目 fillin template 新設 + KEN001 完走 (KEIS001 は 8 blanks のため §6.6b 繰越)
  - Phase X-C: ✅ 7 本目 ox3comb8 template 新設 + GSE001 完走
  - Phase X-D/E: ✅ 最終 CP 確認 + 公式総括
- **完走 10 件**: 326-330 (KEI 5) + MIN001 / SYO001 / MINS001 + KEN001 + GSE001
- **保留 1 件**: KEIS001 (8 blanks 対応に N=8 fillin8 template を要する)

---

## 7 本立て template の確立

| # | template | base | 対応形式 | 用途 |
|---|---|---|---|---|
| 1 | `KTX_template.html` | (元祖) | ox-grid-5 | KEI 326 等 |
| 2 | `KTX_template_ox4.html` | base 派生 | ox-grid-4 | KEI 327 等 |
| 3 | `KTX_template_msel5.html` | base 派生 | multi-select-5 | KEI 328 / MINS001 |
| 4 | `KTX_template_sc5.html` | base 派生 | single-choice-5 | KEI 329 |
| 5 | `KTX_template_comb5.html` | base 派生 | combination-5 | KEI 330 / MIN001 / SYO001 |
| **6** | **`KTX_template_fillin.html`** | **msel5 派生** | **fill-in (5 blanks 最大)** | **KEN001** |
| **7** | **`KTX_template_ox3comb8.html`** | **comb5 派生** | **ox-grid-3 + combination-8** | **GSE001** |

各テンプレ:
- 同期義務セクション (head/css/body_pre_toc/marker_legend/part_c_d/footer_spec/js) は全 7 本 byte-identical
- 差分許容セクション (toc/pre_part_a/part_a/a2/part_b/basis) は形式別

---

## 完走 10 件の最終一覧

| 順 | 問題 ID | 科目 | 形式 | template | 正答率 | HTML パス | バイト数 | ERROR | WARN |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 326 | 刑法 (KEI) | ox-grid-5 | KTX_template.html | 47% | `outputs/tx/刑TX/刑TX326.html` | 121,870 | 0 | 0 |
| 2 | 327 | 刑法 (KEI) | ox-grid-4 | KTX_template_ox4.html | 81% | `outputs/tx/刑TX/刑TX327.html` | 116,979 | 0 | 0 |
| 3 | 328 | 刑法 (KEI) | multi-select-5 | KTX_template_msel5.html | 56% | `outputs/tx/刑TX/刑TX328.html` | 117,075 | 0 | 0 |
| 4 | 329 | 刑法 (KEI) | single-choice-5 | KTX_template_sc5.html | — | `outputs/tx/刑TX/刑TX329.html` | 117,285 | 0 | 0 |
| 5 | 330 | 刑法 (KEI) | combination-5 | KTX_template_comb5.html | 84% | `outputs/tx/刑TX/刑TX330.html` | 120,663 | 0 | 0 |
| 6 | MIN001 | 民法 | combination-5 | KTX_template_comb5.html | 95% | `outputs/tx/民TX/民TX001.html` | 119,619 | 0 | 1 [S26] |
| 7 | SYO001 | 商法 | combination-5 | KTX_template_comb5.html | 32% | `outputs/tx/商TX/商TX001.html` | 120,115 | 0 | 1 [S26] |
| 8 | MINS001 | 民訴 | multi-select-5 | KTX_template_msel5.html | 82% | `outputs/tx/民訴TX/民訴TX001.html` | 118,426 | 0 | 1 [S26] |
| 9 | **KEN001** | **憲法** | **fill-in** | **KTX_template_fillin.html** | **30%** | **`outputs/tx/憲TX/憲TX001.html`** | **103,081** | **0** | **2 [S26]/[S71]** |
| 10 | **GSE001** | **行政法** | **ox-grid-3+combination-8** | **KTX_template_ox3comb8.html** | **59%** | **`outputs/tx/行政TX/行政TX001.html`** | **102,594** | **0** | **1 [S26]** |

出題形式分布: 7 種すべてに少なくとも 1 件の運用実績。

---

## CP1-CP7 全通過状況 (Phase X-D 最終確認)

| CP | 内容 | 結果 |
|---|---|---|
| CP1 | 既存 5 本 template SHA256 不変 | ✅ |
| CP2 | 326-330 byte-identical 維持 | ✅ (3 回照合 + 再 render 後一致) |
| CP3 | MIN001/SYO001/MINS001 byte-identical 維持 | ✅ |
| CP4 | check_template_sync.py 7 本立て exit 0 | ✅ |
| CP5 | INTENTIONAL_DIFFS に fill-in / ox3comb8 登録済 | ✅ |
| CP6 | 各新規問題 (KEN001/GSE001) で render + 二段検証 PASS | ✅ (WARN [S26]/[S71] のみ非致命) |
| CP7 | slotmap §6.6 / §6.7 本文化 + §X 実測値記入 | ✅ |

---

## 編集・新規作成ファイル (累計)

| カテゴリ | ファイル | 種別 |
|---|---|---|
| template | `templates/KTX_template_fillin.html` | new (6 本目、msel5 派生) |
| template | `templates/KTX_template_ox3comb8.html` | new (7 本目、comb5 派生) |
| script | `scripts/build_fillin_template.py` | new (fillin 生成補助) |
| script | `scripts/build_ox3comb8_template.py` | new (ox3comb8 生成補助) |
| script | `scripts/render.py` | edit (TEMPLATE_PATHS / _format_answer dict / LABEL A-E / CHOICE pre-fill / COMBO 1-8 拡張) |
| script | `scripts/check_template_sync.py` | edit (TEMPLATE_FILES に 2 件追加 / 表示文言動的化 / note 更新) |
| script | `scripts/validate_structure.py` | edit (_derive_cv_info に fill-in/ox3comb8 mode / S73 拡張 / S79 mode 別) |
| script | `scripts/validate_content.py` | edit (positive_check answer dict 対応) |
| schema | `schema/problem.schema.json` | edit (instruction_type 拡張 / answer object oneOf / Choice.label A-E / Combination.label 1-8 / combinations maxItems 8) |
| problem | `problems/KEN001.json` | new |
| problem | `problems/GSE001.json` | new |
| output | `outputs/tx/憲TX/憲TX001.html` | new (render 生成物) |
| output | `outputs/tx/行政TX/行政TX001.html` | new (render 生成物) |
| docs | `docs/session-6subjects-complete.md` | new (本ファイル) |
| slotmap | `templates/KTX_template_slotmap.md` | edit (§6.6 §X / §6.7 §X 実測値記入) |

---

## 既存 8 件 byte-identical 維持の SHA256 証拠

```
326     BEF153E033A09A21E9C7E88D496BAAA0AA1F5BEEEC3E2259E9D836D9DFDEE039
327     9C30BC5EA89F5BFF3D4F242011A4A0AC89E03B7E1494E4C0317B9F2D7EBD12C2
328     8AF2A098FBE1BB70C29F2E53DDEB1C4C2A8933910EE6AE5F188088C34087D4CB
329     1A72A3BF0C6AEEE47F282D6DB7DE3C25506EE7507F13072644FF98A7CD2B2D2F
330     EEFA038D7A3E2EFBDFE608558B1BDA6E17FDF7190C578FA016C789C465CE3C65
民TX001  9683AA963019660A...
商TX001  0CE20947B9ED2FDF...
民訴TX001 89854BB350B5089A...
```

Phase X-A 完了時 / Phase X-B 完了時 / Phase X-C 完了時 / Phase X-D 最終確認時の **4 回照合**、全件一致。再 render 後も同一 SHA256。

---

## 新規 template 2 本のサイズと特徴

| template | チャー数 | 行数 | 派生元 | 主な差分許容セクション |
|---|---|---|---|---|
| `KTX_template_fillin.html` | 101,984 | 2,908 | msel5 | TOC=A〜E, A-2=fill-in (5 slots), Part B=空欄A〜E section |
| `KTX_template_ox3comb8.html` | 101,501 | 2,877 | comb5 | TOC=ア〜ウ, A-1=ア〜ウ+8 組合せ, A-2=ox3comb8 (8 slots), Part B=記述ア〜ウ section |

両テンプレとも、同期義務セクション (約 2,650 行、CSS / JS / head / part_c_d / footer_spec / marker_legend / body_pre_toc) は base から byte-identical 継承。差分許容セクションは ~250-300 行で形式固有のカスタム実装。

---

## slotmap.md / docs/ 最終構成

- `templates/KTX_template_slotmap.md`: **3,690 行** (初期 451 → 8.27 倍、§6.6/§6.7 実測値記入後)
- `docs/`:
  - `ox4-design-investigation-326-330-session.md`
  - `session-326-327-completion.md` / `session-328-completion.md` / `session-329-completion.md` / `session-330-completion.md`
  - `session-ken-k1-design.md`
  - `session-warn-complete.md`
  - `session-6subjects-expansion.md`
  - `session-6subjects-complete.md` (本ファイル、新規)
- `CLAUDE.md`: 568 行 (PowerShell PYTHONIOENCODING 注記済)

---

## 想定外の挙動 (本セッション)

### Y-1: KEIS の 8 blanks 問題

`KEIS.pdf` は ①-⑧ の 8 空欄を持つ fill-in 形式だが、本セッションで設計した 6 本目 fillin template は最大 5 blanks (A-E、msel5 base の CHOICE 構造を踏襲) で運用。KEIS001 を完走させるには `KTX_template_fillin8.html` のような 8 本目テンプレが必要となるため、**§6.6b として次セッションに繰越**。

### Y-2: combination N=8 への汎化

GSE 用に combinations の最大件数を 5 → 8 に拡張した結果、`scripts/render.py` の COMBO_*_LABEL / COMBO_*_SET slot supply が `("1","2","3","4","5","6","7","8")` ループに、`schema/problem.schema.json` の `combinations.maxItems` が 5 → 8 に、`Combination.label.enum` が `["1","2","3","4","5"]` → `["1","2","3","4","5","6","7","8"]` に拡張された。**KEI 330 (combination-5、N=5) には影響なし**。byte-identical 維持 (CP2 担保) で確認済。

### Y-3: validate_structure.py の S73 / S79 mode 別分岐

新形式 (fill-in / ox3comb8) を扱うため、S73 (answer-type 整合性) / S79 (combo-block 件数) を mode 別に分岐。既存 5 形式の判定経路は不変、新形式が追加されただけ。CP4 (326-330 byte-identical) で動作を担保。

### Y-4: WARN [S71] の許容

KEN001 では fillin template の answer-instruction 文言が canonical (ox-grid 系の文言) と異なるため [S71-AP33] WARN が発生。これは fill-in 形式の本質的な差分 (空欄数による文言調整) であり、形式追加に伴う自然な拡張とみなして許容。将来 [S71] を mode 別に分岐するリファクタが望ましい。

### Y-5: SIGNATURE_REGISTRY の各科目 entry

KEN / GSE とも本セッションでは初の問題追加だったため、`SIGNATURE_REGISTRY["KEN"]` / `["GSE"]` は空 dict のまま。topic 横断検出は 2 件目以降の問題追加時に有効化する設計。

---

## 残課題と次セッション最優先項目

### 残課題 1 件: KEIS001 (§6.6b)

- **対象 PDF**: `inputs/tx-pdfs/KEIS.pdf` (3 ページ、page-01 問題、page-02-03 解答+解説)
- **形式**: fill-in (①-⑧ 8 空欄 / a-h 候補) + 組合せ判定 (1-5 のいずれか)
- **対応案**: `KTX_template_fillin8.html` (8 本目テンプレ、msel5 base、N=8 blanks)
- **必要な拡張**:
  - schema: instruction_type enum に "fill-in-8" 追加、Choice.label enum に F/G/H 追加、Blank/Candidate types 検討
  - render.py: TEMPLATE_PATHS 追加、CHOICE_A〜H に拡張 (or 別 slot 命名 BLANK_A〜H)
  - validate_structure.py: fill-in mode の N=8 ケース処理 (現状 N=5 固定)
  - 7 本目への影響なし、CP1-CP7 維持

### 次セッション最優先項目

1. **§6.6b 設計合意 (slotmap)**: N=8 fillin8 template の差分許容セクション設計
2. **`KTX_template_fillin8.html` 構築** (msel5 派生、N=8 slots)
3. **KEIS001 完走**: 全 13 想定問題のうち未処理は KEIS のみとなる

完了時の累計:
- 完走 11 件 (326-330 + MIN/SYO/MINS + KEN + GSE + KEIS)
- 8 本立て template (現行 7 本 + fillin8)
- 全 7 科目の運用実績達成 (KEI/KEN/MIN/SYO/MINS/KEIS/GSE)

---

## 公式 close 時点の確定状態

- ✅ CP1-CP7 全通過 (CP4 = 既存資産 byte-identical 4 回照合一致)
- ✅ 完走 10 件 (KEI 5 + MIN/SYO/MINS 3 + KEN + GSE)
- ✅ 7 本立て template 確立 (5 既存 + 2 新規)
- 🟡 残課題 1 件 (KEIS001、§6.6b 次セッション)
- ✅ slotmap.md 3,690 行 (初期 451 → 8.18 倍)
- ✅ (b) refactor 発火条件への対応完了 (選択肢 X 採択、テンプレ追加路線確立)

本セッションは 10 件完走で公式 close。次セッションは KEIS001 (§6.6b) から再開可能。
