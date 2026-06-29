# Canonical 系譜・現行版マップ（TX / JX）

> **このファイルの目的**：「いま新規生成で使う雛型（canonical）とバージョンはどれか」を一枚で引く正典。
> コードネーム（GENESIS 等）が世代をまたいで増えたため、active と frozen/legacy を明示する。
> 最終更新：2026-06-29。

---

## TX（短答式）

### 現行 active ＝ **v12.1.1 LOOP-CORE**（2026-06-29・刑TX360 inline canon + typography patch）

| 役割 | canonical | 生成コマンド | validator |
|---|---|---|---|
| **コア**（全問生成・周回＋誤答修正が単体完結） | **`canonical/GENESIS-CORE.html`**（v12.1.1） | `/new-tx`（batch-tx・rb 継承） | `scripts/validate-tx-core.py`（G1〜G35） |
| **別冊**（深掘り・誤答データ解禁時のみ） | **`canonical/GENESIS-DEEP.html`** | `/deepen-tx` | `scripts/validate-tx-deep.py`（D1〜D13） |

- 構造正典 spec：**`spec/tx-v12.1.0-inline-core.md`**（active。v12.1.1 typography patch を含む）。基盤は `spec/tx-v11.0.0-core.md`（肢単位管理）と `spec/tx-v11.1.0-twotrack.md`（公式/ Lexia 二系統）。
- 設計の核（v11.0.0 から継承）：肢（記述）単位管理／PART A=ox-grid 5記述○×＋answer-key／記述単位 PART B／参考条文判例
  （保護法益・制度趣旨・判例濃淡）／体系ツリー＋放射マップ2枚／PART C・PART D（12問ドリル）は廃止。
- **v11.1.0 デザイン進化（刑TX327 昇格・2026-06-15）**：①誌面リスキン（明朝＋極細罫・`--ed-*`・`<style>` §1〜§17）／
  ②SYNTHESIS 子カード（syn-orig 記述原文・syn-lead THE GIST・syn-path①②③・syn-image INTUITION）＋ PART B+ 横断コラム
  （cross-column／cb-cross・compare・trap／col-key・col-warn・col-type）／③判例カードは判旨に『⚖ 判旨』バッジ＋判旨以外を
  NOTE 化（条文＝スモークブルー系）／④**3層配色**：大前提＝V3 3パターン基調・PART A 問題解答＝ナチュラルマイルド色・
  それ以外＝4分類パレット役割固定色（§18〜§22 に内蔵＝複製で自動継承・生成時に再選定しない）。正誤○緑/×赤は semantic。
- **v12.0.0 major（2026-06-29）**：周回主導線を下部 ox-grid から問題文直後の `.tx-inline-card` へ移行。各肢カードに OX、条文原文、文言・趣旨・射程・切断点・転用、記憶フック、答案圧縮、詳説トグルを集約。PART B は独立巡回先ではなく、各肢カードの詳説ソースに格下げ。
- **v12.1.0 minor（2026-06-29）**：TX360 試作で確定した誌面仕上げを正典化。上部5秒トースト、iPhone向け余白、Mildliner 系配色、条文=ブルー/判例=ピンク/補助根拠=グレー、SM2 用 `.ox-pool-explain` ミラー、問題都合ラベルを論点コア・テーゼへ置換する運用を固定。
- **v12.1.1 patch（2026-06-29・active）**：ストーリー/物語解説の強調太字を軽量化。`.fa-narrative b` は `font-weight:560` 以下を正典化し、モバイルで潰れる700系の太字へ戻さない。validator G35 で回帰を止める。
- Lexia 連携：間違えた肢を `{問題ID}#stmt-{記述}` で要復習プール＋弱点克服帳へ。

### 世代の系譜（frozen / legacy）

| 世代 | コードネーム | バージョン | 状態 | 起点/特徴 |
|---|---|---|---|---|
| v8/v9 | `canonical/KTX301.html` | v8.11.x／v9.0.0-genkei／v9.1.0-mindmap／v9.2.0-deepdive | **legacy** | 構造参考のみ。本文流用は AP-42 違反 |
| v10 | `canonical/GENESIS.html` | v10.0.0 GOLD-SKELETON | **凍結** | 刑TX311 ベース。既存197問（v10）の保守用。`validate-tx-gold.py`(G1〜G19)・`validate-tx.py`(legacy S1〜S91) |
| **v11** | **`GENESIS-CORE` ＋ `GENESIS-DEEP`** | **v11.1.0 LOOP-CORE**（v11.0.0→2026-06-15 刑TX327 昇格） | **frozen** | GENESIS を再編して CORE/DEEP に分割。v11.1.0 で誌面リスキン＋3層配色＋SYNTHESIS子カード＋PART B+ |
| **v12** | **`GENESIS-CORE` ＋ `GENESIS-DEEP`** | **v12.1.1 LOOP-CORE**（v12.0.0 major→v12.1.0 TX360 polish→v12.1.1 narrative typography） | **active** | 問題文直後のインライン肢カードを主導線にし、PART B を詳説トグルへ吸収。Lexia/SM2 は裏 ox-grid と `.ox-pool-explain` を単一情報源にする |

> **「GENESIS」名の整理**：無印 `GENESIS.html` ＝ **v10 凍結**。新規生成の起点は **`GENESIS-CORE`／`GENESIS-DEEP`**。
> 改名はしない（spec・validator・commands・CLAUDE.md に配線済みで churn のみ）。曖昧さは本表で解消する。

### 既存 v10/v11 問題の v12 化について

既存197問は **v10 のまま温存**（spec/CLAUDE.md §3 既定）。v12 は機械置換では適用できない構造改訂のため、
必要分を `/rb 範囲` で **1問ずつ再生成**（PDF から）するのが gold 品質。一括全変換は費用対効果が低い。

---

## JX（論文・事例式）

### 現行 active ＝ **v4.0.0 LOOP-FOLD**（2026-06-13 master 反映済み）

| 役割 | canonical | spec | validator |
|---|---|---|---|
| 現行 | **`canonical/ATHENA.html`**（v4 再編済み） | 構造骨子 **`spec/jx-v4.0.0-core.md`**（v0.2）／基盤規律 `spec/jx-v3.2-master.md`（タイポ11役割・5コンポ・配色V3 等を v4 が継承） | `scripts/validate-jx.py`（J1〜J21＋v4 判定で **JC1〜JD1＋JSB**・`--core-only`/`--deep-only`） |

- 設計の核：**1枚もの維持・前半コア／後半 deep（第4-5部）デフォルト折りたたみ・exec-summary 削除・模範答案+採点講評は reveal・照合ナビ・各 H 口頭骨格**。用語集5-5/略語5-6は折りたたみ外。
- TX v12 と**意図的に分岐**：物理2ファイル分割しない（副産物 RX/TREE/TTS が第4部に依存し deep を別生成できないため＝**(A) 一括生成＋順序再編**を採用）。
- 生成：`new-jx`／`prompts/new-jx-headless.md`（v4 ガードレール）／`JX.ps1`。ATHENA 複製で v4 構造を自動継承。
- 実証：**刑JX044 を v4 で生成・validate-jx 全件通過（2026-06-13）**。詳細は `spec/jx-v4.0.0-core.md`・memory `[[tx-jx-structure-review-pending]]`。

---

## UX 副産物（RX / TREE / ARIADNE）の正典

検証 PASS 済み JX から生成する Lexia 用副産物も、TX/JX と同じく **canonical 物理複製方式**で正典化済み。

| 副産物 | 正典スケルトン（複製起点） | 生成プロンプト | 検証 |
|---|---|---|---|
| **RX**（論証カード・1論点1HTML） | **`canonical/AXIOM.html`**（v1.0・2026-06-20 新設） | `prompts/new-rx-headless.md`（複製方式） | `scripts/validate-rx.py`（R1〜R10） |
| **TREE**（樹形図・ARBOR 仕様） | `canonical/ARBOR.html`（gold TREE 複製） | `prompts/new-arb-headless.md` | `scripts/validate-tree.py`（T1〜T9） |
| **ARIADNE**（解法ナビ＋答案構成周回） | **`canonical/ARIADNE.html`**＋**`canonical/ARIADNE.placeholder.html`**（v1.2.0 PLACEHOLDER-LOCK・2026-06-29 active） | `/new-ariadne` / `prompts/new-ariadne-headless.md` | `scripts/validate-ariadne.py`（A1〜A31）＋`scripts/check-ariadne-canonical.py` |

- **AXIOM（RX 正典・2026-06-20）**：従来 RX は正典を持たず自由生成で CSS が 58 種に割れていた。
  gold 刑RX001_1 を基に AXIOM を新設し、**作り込みフォント（TX/JX と同一 Google Fonts）・規範レモン
  (#fff7a8)＋🔑バッジ・カード幅 920px・toggleNorm/lexiaAnswer JS** を正典品質で固定。
  既存 127 枚は `scripts/rx-recanon.py`（内容保持・クイズ逐語・配色継承・フェイルセーフ）で一括移行済み。
- **ARIADNE v1.2.0 PLACEHOLDER-LOCK（2026-06-29）**：JX019 で確定したマトリクス型答案構成を major 正典化した
  v1.1.0 を継承し、さらに **固定HTML＋変数スロット**方式を active にする。`canonical/ARIADNE.html` は
  DOM/CSS/JS/余白/機能色の固定正典、`canonical/ARIADNE.placeholder.html` は AI が置換してよい `{{{...}}}`
  スロット契約。模範答案は Claude 正典の問規当結カードを維持する。AI判断可のデザイン差分は既存
  ACTIVE ベースカラー（EASY/STD/HARD）の難易度選択のみ。恒久対策は `validate-ariadne.py` A30/A31 と
  `check-ariadne-canonical.py`、同期前 `check-lexia-preflight.py` に組込み済み。
- 詳細は **`docs/rx-arb-byproducts.md`**（副産物の正典）。

---

## 検証スクリプト早見

| script | 対象 | チェック |
|---|---|---|
| `validate-tx-core.py` | TX v11/v12 コア | G1〜G35 |
| `validate-tx-deep.py` | TX v11 別冊 | D1〜D13 |
| `validate-tx-gold.py` | TX v10 | G1〜G19（legacy 保守） |
| `validate-tx.py` | TX v8.x〜v9.x | S1〜S91（legacy） |
| `validate-jx.py` | JX | J1〜J21＋JC1〜JD1(v4)＋JSB（タグ均衡） |
| `validate-rx.py` / `validate-tts.py` | RX論証 / TTS台本 | 各系 |
| `validate-ariadne.py` / `check-ariadne-canonical.py` | ARIADNE | A1〜A31／canonical＋全出力横断 |

---

## 旧 spec の扱い（整理済み・2026-06-13）

`spec/` 直下は **active のみ**に整理した：

```
spec/
  tx-v12.1.0-inline-core.md ← TX 現行（v12.1.1 typography patch 含む）
  tx-v11.0.0-core.md     ← TX 基盤（v12 が継承）
  tx-v11.1.0-twotrack.md ← TX 二系統（v12 が継承）
  jx-v3.2-master.md      ← JX 現行運用
  jx-v4.0.0-core.md      ← JX v4 骨子
  README.md
  legacy/                ← ★ 退避済み（read-only・新規生成では使わない）
    tx-v8.11.1〜8.11.6 の core＋annex A/B/C/css（30点）
    tx-v9.0.0-genkei / tx-v9.1.0-mindmap / tx-v9.2.0-deepdive（3点）
```

`tx-v8.11.x`・`tx-v9.x`（計33点）は `spec/legacy/` へ `git mv`（履歴保持）。
アクティブな参照（CLAUDE.md §3-1・`upgrade-tx`/`upgrade-ktx`/`new-ktx` スキル・night-batch-runner・
new-tx-headless・README・MIGRATION）のパスも `spec/legacy/` に更新済み。歴史的 handoff/session 文書
（docs/PHASE-*・SESSION-*・v9.2.0-*）は記録として旧パスのまま据置。
