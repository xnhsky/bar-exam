# Canonical 系譜・現行版マップ（TX / JX）

> **このファイルの目的**：「いま新規生成で使う雛型（canonical）とバージョンはどれか」を一枚で引く正典。
> コードネーム（GENESIS 等）が世代をまたいで増えたため、active と frozen/legacy を明示する。
> 最終更新：2026-06-13。

---

## TX（短答式）

### 現行 active ＝ **v11.0.0 LOOP-CORE**

| 役割 | canonical | 生成コマンド | validator |
|---|---|---|---|
| **コア**（全問生成・周回＋誤答修正が単体完結） | **`canonical/GENESIS-CORE.html`** | `/new-tx`（batch-tx・rb 継承） | `scripts/validate-tx-core.py`（G1〜G26） |
| **別冊**（深掘り・誤答データ解禁時のみ） | **`canonical/GENESIS-DEEP.html`** | `/deepen-tx` | `scripts/validate-tx-deep.py`（D1〜D13） |

- 正典 spec：**`spec/tx-v11.0.0-core.md`**。
- 設計の核：肢（記述）単位管理／PART A=ox-grid 5記述○×＋answer-key／記述単位 PART B／参考条文判例
  （保護法益・制度趣旨・判例濃淡）／体系ツリー＋放射マップ2枚／PART C・PART D（12問ドリル）は廃止。
- Lexia 連携：間違えた肢を `{問題ID}#stmt-{記述}` で要復習プール＋弱点克服帳へ。

### 世代の系譜（frozen / legacy）

| 世代 | コードネーム | バージョン | 状態 | 起点/特徴 |
|---|---|---|---|---|
| v8/v9 | `canonical/KTX301.html` | v8.11.x／v9.0.0-genkei／v9.1.0-mindmap／v9.2.0-deepdive | **legacy** | 構造参考のみ。本文流用は AP-42 違反 |
| v10 | `canonical/GENESIS.html` | v10.0.0 GOLD-SKELETON | **凍結** | 刑TX311 ベース。既存197問（v10）の保守用。`validate-tx-gold.py`(G1〜G19)・`validate-tx.py`(legacy S1〜S91) |
| **v11** | **`GENESIS-CORE` ＋ `GENESIS-DEEP`** | **v11.0.0 LOOP-CORE** | **active** | GENESIS を再編して CORE/DEEP に分割 |

> **「GENESIS」名の整理**：無印 `GENESIS.html` ＝ **v10 凍結**。新規生成の起点は **`GENESIS-CORE`／`GENESIS-DEEP`**。
> 改名はしない（spec・validator・commands・CLAUDE.md に配線済みで churn のみ）。曖昧さは本表で解消する。

### 既存 v10 問題の v11 化について

既存197問は **v10 のまま温存**（spec/CLAUDE.md §3 既定）。v11 は機械置換では適用できない構造改訂のため、
必要分を `/rb 範囲` で **1問ずつ再生成**（PDF から）するのが gold 品質。一括全変換は費用対効果が低い。

---

## JX（論文・事例式）

| 役割 | canonical | spec | validator |
|---|---|---|---|
| 現行 | `canonical/ATHENA.html` | `spec/jx-v3.2-master.md`（現行運用）／`spec/jx-v4.0.0-core.md`（LOOP-FOLD 骨子・branch jx-v4-loopfold で実装中） | `scripts/validate-jx.py`（J1〜J20／v4 は JC/JD 系） |

- JX v4.0.0 LOOP-FOLD は TX v11 と**意図的に分岐**：物理2ファイル分割せず**1枚もの維持**＋前半コア/後半 deep 折りたたみ。
  詳細は `spec/jx-v4.0.0-core.md`・memory `[[tx-jx-structure-review-pending]]`。

---

## 検証スクリプト早見

| script | 対象 | チェック |
|---|---|---|
| `validate-tx-core.py` | TX v11 コア | G1〜G26 |
| `validate-tx-deep.py` | TX v11 別冊 | D1〜D13 |
| `validate-tx-gold.py` | TX v10 | G1〜G19（legacy 保守） |
| `validate-tx.py` | TX v8.x〜v9.x | S1〜S91（legacy） |
| `validate-jx.py` | JX | J1〜J20 |
| `validate-rx.py` / `validate-tts.py` | RX論証 / TTS台本 | 各系 |

---

## 旧 spec の扱い（整理メモ）

`spec/` には legacy が多数残存（`tx-v8.11.1〜8.11.6` の core＋annex A/B/C/css 計36点・`tx-v9.0/9.1/9.2`）。
read-only で参照されるのみ（CLAUDE.md §3-1 が v9.x を「歴史的参照」と明記、upgrade 系スキルが v8.11.x を参照）。
**現行で使うのは `spec/tx-v11.0.0-core.md` のみ。** 退避（`spec/legacy/` 等）する場合は参照元
（CLAUDE.md §3-1・upgrade-tx/upgrade-ktx スキル）も更新すること。
