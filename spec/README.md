# spec/ 現行版インデックス ― 「いま使うのはどれか」早見表

> **迷ったらこの表が正典。** 新規生成では **現行版のみ**を使う。旧版は legacy アップグレード
> ツール（`upgrade-tx`/`upgrade-ktx` 等）が依存するため `spec/` に残置するが、新規生成では参照しない。
> 最終更新：2026-06-13（TX v11.0.0 LOOP-CORE／JX v4.0.0 LOOP-FOLD）。

---

## 現行版（これを使う）

### TX（短答）― **v11.0.0 LOOP-CORE**
コードネーム＝**GENESIS**（v10）→ **GENESIS-CORE ＋ GENESIS-DEEP**（v11 で2ファイル分割）。

| 役割 | ファイル | 備考 |
|---|---|---|
| 正典スケルトン（コア・メイン） | `canonical/GENESIS-CORE.html` | 唯一の clone 起点。周回＋誤答修正で自己充足。PART A=ox-grid（5記述○×）＋answer-key／記述単位 PART B |
| 正典スケルトン（深掘り別冊） | `canonical/GENESIS-DEEP.html` | 解禁条件成立時に後追い生成する `{ID}-deep.html` の起点。PART D（12問）は廃止 |
| 構造骨子 | `spec/tx-v11.0.0-core.md`（v0.4） | v11 の構造規律（第0〜11項）。full master は持たず、これ＋GENESIS-CORE/DEEP＋CLAUDE.md §3 が実質の spec |
| 検証（コア） | `scripts/validate-tx-core.py` | G1〜G26 |
| 検証（別冊） | `scripts/validate-tx-deep.py` | D1〜D13 |
| 生成 | `new-tx`（コア）／`deepen-tx`（別冊）／`batch-tx`／`rb` | GENESIS-CORE/DEEP 複製→鋳造 |

### JX（論文・重問）― **v4.0.0 LOOP-FOLD**
コードネーム＝**ATHENA**（v3.2 から v4 へ**同一ファイルを再編**・単一ファイル維持なので名前・分割なし）。

| 役割 | ファイル | 備考 |
|---|---|---|
| 正典スケルトン | `canonical/ATHENA.html` | 唯一の clone 起点。1枚もの維持・前半コア／後半deep折りたたみ・exec-summary無し・模範答案reveal |
| 構造骨子 | `spec/jx-v4.0.0-core.md`（v0.2） | v4 の構造規律（第0〜12項）。**構造面は v3.2 を上書き**（CLAUDE.md §4-1-bis） |
| 基盤規律 | `spec/jx-v3.2-master.md` | タイポ11役割・5コンポーネント・配色V3・第N部の詳細規律。**v4 が継承**（構造以外は現役） |
| 検証 | `scripts/validate-jx.py` | v4 自動判定で JC1〜JD1＋JSB（タグ均衡）追加。`--core-only`／`--deep-only` |
| 生成 | `new-jx`／`prompts/new-jx-headless.md`／`JX.ps1` | ATHENA 複製で v4 構造を自動継承 |

### 共通副産物・耳トレ
| 役割 | ファイル |
|---|---|
| RX 論証カード検証 | `scripts/validate-rx.py` |
| TTS 台本検証 | `scripts/validate-tts.py` |

---

## 旧版（残置・新規生成では**使わない**）

legacy アップグレードツールや歴史的 docs（計46ファイル）が参照するため**削除しない**。新規生成では無視する。

| 系統 | 旧版ファイル | 位置づけ |
|---|---|---|
| TX v10 GOLD-SKELETON | `canonical/GENESIS.html`／`scripts/validate-tx-gold.py`（G1〜G18） | v10 の凍結正典。既存197問の保守検証に使用 |
| TX v9.x（full master） | `spec/tx-v9.0.0-genkei-core.md`／`tx-v9.1.0-mindmap-core.md`／`tx-v9.2.0-deepdive-core.md` | 歴史的参照（最後の full master・巨大） |
| TX v8.11.x | `spec/tx-v8.11.{1,3,4,5,6}-*`（core＋annex A/A-bis/B/C） | `upgrade-tx`/`upgrade-ktx` が依存。最古 |
| TX 構造参考 | `canonical/KTX301.html` | v9.x 系の構造参考（本文流用は AP-42 違反） |
| TX legacy 検証 | `scripts/validate-tx.py`（S1〜S91） | v8.x〜v9.x 既存ファイルの保守検証 |
| JX v3.2（構造部分） | `spec/jx-v3.2-master.md` の**構造記述のみ** | 構造は v4 が上書き。タイポ等の規律は現役（上の現行版表参照） |

---

## 命名の整理メモ

- **TX のコードネームは GENESIS**（天地創造）：v10 = `GENESIS.html` 単体 → v11 = `GENESIS-CORE` ＋ `GENESIS-DEEP` に分割（コア＝周回本体／別冊＝深掘り後追い）。
- **JX のコードネームは ATHENA**（知の女神）：v3.2 → v4 は**同じ `ATHENA.html` を再編**しただけで改名・分割なし。JX は2ファイルにせず1枚もの維持なので `-deep` 接尾辞は持たない（v4 設計＝副産物 RX/ARB/TTS が第4部に依存するため deep を別生成できない）。
- **「core」「master」「骨子」の使い分け**：`*-core.md`＝現行の構造骨子（v11/v4）。`*-master.md`＝旧来の full 規律本体（jx-v3.2 のみ現役）。TX は v11 で full master を作らず骨子＋正典 HTML を spec とする方式。
- **将来の整理候補（未実施・任意）**：jx-v3.2-master の構造記述を jx-v4 へ畳んで単一 master 化する／旧 TX spec（v8/v9）を legacy ツール側のパス更新とセットで `spec/_legacy/` へ退避する。いずれも参照網（46ファイル）の更新を伴うため、必要になった時点で実施。
