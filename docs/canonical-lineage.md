# Canonical 系譜・現行版マップ（TX / JX）

> **このファイルの目的**：「いま新規生成で使う雛型（canonical）とバージョンはどれか」を一枚で引く正典。
> コードネーム（GENESIS 等）が世代をまたいで増えたため、active と frozen/legacy を明示する。
> 最終更新：2026-07-01。

---

## 新セッションの番号指定ルーティング

- 「TX355-360を生成」「JX001-010を作って」のような短い自然文は正式な生成依頼として扱う。
- 「生成」「新規」「作って」は、この文書の active 正典から新規生成する。TX は `GENESIS-CORE`、JX は `ATHENA` を唯一の複製起点にする。
- 「既存」「更新」「アップデート」「最新版に」は、legacy upgrade ではなく、この文書の active 正典へ既存ファイルを移行/再生成する依頼として扱う。
- 作業者は固定記憶の版名に頼らず、生成・更新の冒頭で必ずこの文書を読み、active 行を確認する。
- 生成・更新後は各 validator と横断チェック、最新法令・判例・主要学説レビュー、内容レビューを通してから commit/push する。

---

## TX（短答式）

### 現行 active ＝ **v13.1.0 LOOP-CARD**（2026-07-06・刑TX359 gold・正誤表リデザイン。基盤 v13.0.0=2026-07-03）

| 役割 | canonical | 生成コマンド | validator |
|---|---|---|---|
| **_lex コア（v13）**（新規生成・v13 化の唯一起点） | **`canonical/GENESIS-CARD.html`**（v13.1.0・gold=刑TX359）＋ **`canonical/GENESIS-CARD.placeholder.html`**（スロット契約） | `/new-tx`（batch-tx・rb 継承・v13 経路） | `scripts/validate-tx-core.py`（G1〜G45＋**G50 v13構造**）＋`check-tx-lex-engine.py`（G41/script2本）＋`check-duplicates.py` |
| 公式版（本物5択・`000_TX`） | — | `/new-tx` 二系統出力 | `validate-tx-core.py`（single/multi） |

- 構造正典 spec：**`spec/tx-v13.1.0-loopcard-core.md`**（active・byte 正典）。二系統は `spec/tx-v11.1.0-twotrack.md` を継承。
- **v13.1.0 LOOP-CARD（2026-07-06・active＝最新）／基盤 v13.0.0（2026-07-03）**：v12.2.1 の「肢を解く UI（ANSWER箱＋5点フロー＋記憶フック）」を廃し、
  **旧 PART B の統合解説プロースを記述カード本文へ昇格**、条文・判例は各カードの **「📚 BASIS」ボックス**（条文＝本文表示/
  解説トグル・判例＝判旨表示/以下トグル・学説＝ラベンダー任意項目）へ集約。縦順＝正誤表(印付き原文＋法理コア＋成績)→**体系マップ(SVGハイブリッド・規範核バッジ・帰结箱なし)**→
  横断(3軸マトリクス)→肢カード→物語→#basis(現行法note のみ)。**正誤表リデザイン（2026-07-06）**＝各行に印付き記述原文(`data-brief-mark`)＋法理コア(転用タグ)＋成績表示(🎉)＋重厚感、体系マップ各札に✍規範核バッジ、`▼本問の帰結`箱は廃止。gold=刑TX359 適用済／既存は `scripts/tx-lex-verdict-redesign.py`（土台）＋各問執筆で移行。**正誤マーキング**（記述原文の分かれ目を×赤波線/○緑下線）、
  **相互リンク往復**（条文参照→BASIS条文へジャンプ＋戻る・配線JSは単一エンジンへ統合）、**他科目横断は重要接点のみ**（放火では
  失火→民法失火責任法）。使い方説明は載せない。validator G50 と placeholder 契約で回帰を止める。**学説項目（2026-07-06 追加・版据置）**＝BASIS に `.tx-basis-item.is-theory`（ラベンダー・任意）を新設。重要な学説対立・通説/有力説が記述の決め手のときだけ置く（条文青/判例ピンク/学説紫の三分・ARIADNE(JX) と統一）。gold=刑TX363 記述3（焼損＝独立燃焼説 vs 効用喪失説）。任意項目のため版は据え置き。
- **v13 本文（`<div class="tx-v13-verdict">`）は 50 本**（刑法49＋刑訴1・`089 125 174 218 256 290-302 355-385[381除く] 420` 等・gold=刑TX359）。**版は `scripts/tx-lex-v13-stamp.py` が実体から自動判定**して feature-tag/genmeta/footer の3箇所を揃える＝**規範核バッジ＋印付き原文の両方**を持てば **v13.1.0**、無ければ **v13.0.0**。現状 **v13.1.0＝刑TX361-371 の11本**（＋canonical 359・正誤表リデザイン＋**体系マップ親箱リデザイン**＋**学説項目**を該当問に適用済／2026-07-06 census＝`grep -l data-brief-mark` と `grep -l pbox-chip` がともに 361-371 の11本）、残り **39本は v13.0.0**（`scripts/tx-lex-verdict-redesign.py` で土台注入＋各問で規範核・印付き原文を執筆＋`scripts/tx-lex-sysmap-pbox.py` で親箱を移行）。**版はスタンプ文字列でなく本文タグで実体判定**（v13 ビルド連鎖がスタンプを更新せず旧版名が残っていた経緯あり）。**未移行＝純 v11 の 326 本＋381**（v12.2.1/GENESIS-CORE 保守のまま）。
- **解説執筆規約 v13m（2026-07-06・構造不変の内容規律）**：記述カード解説の書き方の正典＝`docs/tx-v12.2.1-inline-lock.md` §v13m。
  `.syn-lead`＝やさしい版（用語サンドイッチ・核用語1〜2個・初出のみ太字）／`.syn-image`＝💭INTUITION→**🗝記憶のフック**（締めの一行）／
  `.tx-v13-trap`＝**横串・誤解の罠を積極投入**（民法=観念的/刑法=現実的 等・混同フラグ・判例は年月日を一次確認）／マップ短縮版は作らない。
  初例=刑TX362_lex（全5記述）。既存 `_lex` への一括反映は保留（制限リセット後・当面は執筆時に適用）。
- 旧 active（v12.2.1 LOOP-CORE）の構造正典：`spec/tx-v12.1.0-inline-core.md`＋`docs/tx-v12.2.1-inline-lock.md`。既存 v12 資産は
  `canonical/GENESIS-CORE.html`（v12.2.1）＋`GENESIS-DEEP.html`（`/deepen-tx`・`validate-tx-deep.py`）で保守。
- 設計の核（v11.0.0 から継承）：肢（記述）単位管理／PART A=ox-grid 5記述○×＋answer-key／記述単位 PART B／参考条文判例
  （保護法益・制度趣旨・判例濃淡）／体系ツリー＋放射マップ2枚／PART C・PART D（12問ドリル）は廃止。
- **v11.1.0 デザイン進化（刑TX327 昇格・2026-06-15）**：①誌面リスキン（明朝＋極細罫・`--ed-*`・`<style>` §1〜§17）／
  ②SYNTHESIS 子カード（syn-orig 記述原文・syn-lead THE GIST・syn-path①②③・syn-image INTUITION）＋ PART B+ 横断コラム
  （cross-column／cb-cross・compare・trap／col-key・col-warn・col-type）／③判例カードは判旨に『⚖ 判旨』バッジ＋判旨以外を
  NOTE 化（条文＝スモークブルー系）／④**3層配色**：大前提＝V3 3パターン基調・PART A 問題解答＝ナチュラルマイルド色・
  それ以外＝4分類パレット役割固定色（§18〜§22 に内蔵＝複製で自動継承・生成時に再選定しない）。正誤○緑/×赤は semantic。
- **v12.0.0 major（2026-06-29）**：周回主導線を下部 ox-grid から問題文直後の `.tx-inline-card` へ移行。各肢カードに OX、条文原文、文言・趣旨・射程・切断点・転用、記憶フック、答案圧縮、詳説トグルを集約。PART B は独立巡回先ではなく、各肢カードの詳説ソースに格下げ。
- **v12.1.0 minor（2026-06-29）**：TX360 試作で確定した誌面仕上げを正典化。上部5秒トースト、iPhone向け余白、Mildliner 系配色、条文=ブルー/判例=ピンク/補助根拠=グレー、SM2 用 `.ox-pool-explain` ミラー、問題都合ラベルを論点コア・テーゼへ置換する運用を固定。
- **v12.1.1 patch（2026-06-29）**：ストーリー/物語解説の強調太字を軽量化。`.fa-narrative b` は `font-weight:560` 以下を正典化し、モバイルで潰れる700系の太字へ戻さない。validator G35 で回帰を止める。
- **v12.2.0 minor（2026-06-30）**：重厚感・教科書化リデザイン。ANSWER 箱、条文/判例ボックス、5点フロー、ワンポイント、詳説 panel の順序を固定し、G37/G43 で回帰を止める。
- **v12.2.1 patch（2026-07-01・active）**：TX355-359 実地修正を表示LOCK化。問題文と○×の一体表示、解法ナビ位置と非ネタバレヒント、条文/判例の題名・法理テーマチップ、条文/判例直下の論点処理マトリクス、ラベル付き本文2カラム字下げ、物語解説の reveal 後表示・ラベル非重畳を固定。最新法令・判例・学説レビューでは、新旧差分時に立法経緯/改正経緯・改正趣旨を `tx-current-law-note` へ残す。validator G45 と `check-tx-lex-engine.py` で回帰を止める。
- Lexia 連携：間違えた肢を `{問題ID}#stmt-{記述}` で要復習プール＋弱点克服帳へ。

### 世代の系譜（frozen / legacy）

| 世代 | コードネーム | バージョン | 状態 | 起点/特徴 |
|---|---|---|---|---|
| v8/v9 | `canonical/KTX301.html` | v8.11.x／v9.0.0-genkei／v9.1.0-mindmap／v9.2.0-deepdive | **legacy** | 構造参考のみ。本文流用は AP-42 違反 |
| v10 | `canonical/GENESIS.html` | v10.0.0 GOLD-SKELETON | **凍結** | 刑TX311 ベース。既存197問（v10）の保守用。`validate-tx-gold.py`(G1〜G19)・`validate-tx.py`(legacy S1〜S91) |
| **v11** | **`GENESIS-CORE` ＋ `GENESIS-DEEP`** | **v11.1.0 LOOP-CORE**（v11.0.0→2026-06-15 刑TX327 昇格） | **frozen** | GENESIS を再編して CORE/DEEP に分割。v11.1.0 で誌面リスキン＋3層配色＋SYNTHESIS子カード＋PART B+ |
| **v12** | **`GENESIS-CORE` ＋ `GENESIS-DEEP`** | **v12.2.1 LOOP-CORE**（v12.0.0 major→v12.1.0 TX360 polish→v12.1.1 typography→v12.2.0 redesign→v12.2.1 display lock） | **frozen（純v11 326本＋381 の保守用。355-385[381除く]は既に v13 本文へ移行済）** | 問題文直後のインライン肢カードを主導線にし、PART B を詳説トグルへ吸収。条文/判例ラベル・解法ナビ・物語解説の表示LOCKを G45 で固定する |
| **v13** | **`GENESIS-CARD` ＋ `GENESIS-CARD.placeholder`** | **v13.1.0 LOOP-CARD**（2026-07-06・gold=刑TX359・正誤表リデザイン。基盤 v13.0.0） | **active** | 「肢を解く UI」を廃し「読む解説」中心へ。統合解説をカード本文へ昇格、条文/判例は📚BASISトグルへ集約、体系マップSVGハイブリッド、正誤マーキング、相互リンク往復。G50＋placeholder契約で固定 |

> **「GENESIS」名の整理**：無印 `GENESIS.html` ＝ **v10 凍結**。v11/v12 の起点＝`GENESIS-CORE`／`GENESIS-DEEP`（frozen・保守）。
> **v13 新規生成の唯一起点＝`GENESIS-CARD`（＋`.placeholder`）**。
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
| **ARIADNE**（解法ナビ＋答案構成周回） | **`canonical/ARIADNE.html`**＋**`canonical/ARIADNE.placeholder.html`**（**v1.3.0 TXLEX-UNIFY・2026-07-04 active**／旧 v1.2.0 PLACEHOLDER-LOCK は系譜） | `/new-ariadne` / `prompts/new-ariadne-headless.md` | `scripts/validate-ariadne.py`（A1〜A36）＋`scripts/check-ariadne-canonical.py` |

- **AXIOM（RX 正典・2026-06-20）**：従来 RX は正典を持たず自由生成で CSS が 58 種に割れていた。
  gold 刑RX001_1 を基に AXIOM を新設し、**作り込みフォント（TX/JX と同一 Google Fonts）・規範レモン
  (#fff7a8)＋🔑バッジ・カード幅 920px・toggleNorm/lexiaAnswer JS** を正典品質で固定。
  既存 127 枚は `scripts/rx-recanon.py`（内容保持・クイズ逐語・配色継承・フェイルセーフ）で一括移行済み。
- **ARIADNE v1.2.0 PLACEHOLDER-LOCK（2026-06-29）**：JX019 で確定したマトリクス型答案構成を major 正典化した
  v1.1.0 を継承し、さらに **固定HTML＋変数スロット**方式を active にする。`canonical/ARIADNE.html` は
  DOM/CSS/JS/余白/機能色の固定正典、`canonical/ARIADNE.placeholder.html` は AI が置換してよい `{{{...}}}`
  スロット契約。模範答案は Claude 正典の問規当結カードを維持する。AI判断可のデザイン差分は既存
  ACTIVE ベースカラー（EASY/STD/HARD）の難易度選択のみ。恒久対策は `validate-ariadne.py` A30/A31/A32 と
  `check-ariadne-canonical.py`、同期前 `check-lexia-preflight.py` に組込み済み。最新法令・判例・学説レビューも必須で、
  新旧差分時は `ariadne-current-law-note` に立法経緯/改正経緯・改正趣旨を含める。
- **ARIADNE v1.3.0 TXLEX-UNIFY（2026-07-04・現行 active）**：v1.2.0 の placeholder 契約を継承しつつ、
  深掘り層（条文/判例/学説）の**誌面を TX_lex（刑TX420_lex）の配色・意匠に統一**し、**判例カードの構成を
  完全1本化**した major 改定。要点：①**全判例カードを `cx-sec` 形式に統一**（旧 h5・百選 hy-sec・table・
  `<p><strong>ラベル</strong>：`・plain hanging の全様式を吸収）＝節＝`<div class="cx-sec cr-{role}">`＋
  食み出し無しの**パステル薄チップ** `.cx-lab`＋本文 `.cx-body`。②**構成は判例百選スキーム**（事件情報/事案/
  判旨/解説/射程/百選/本問での使い方）に統一し、**事件情報は複数行ラベル**（裁判所：/判決日：/出典：/事件番号：/
  事件名：）に。③**配色＝条文ブルー/判例ピンク/学説ラベンダー/用語スレート＋6色チップ**（事案=シアン/判旨=
  ローズ/解説=黄緑/射程=茶/本問=マリーゴールド/事件情報・百選=ラベンダー）・★★★=violet・緑/紫マーカー。
  ④**重厚感**（深い影＋内側ハイライト＋チップ立体）・**本文1字下げ徹底**・**セクション見出し/導入文を帯＋
  白カードで背景から分離**。Lexia は `extractReferencesFromHtml` を `.cx-sec` 構造抽出対応に更新（main）。
  伝播ツール（全て冪等・本文/内容不変・LF保持）：`ariadne-txlex-theme.py`（配色/意匠/重厚感/字下げ）・
  `ariadne-case-unify.py`＋`ariadne-hy-to-cx.py`＋`ariadne-convert-residual.py`＋`ariadne-convert-compact.py`
  （全様式→cx-sec）・`ariadne-unify-case-structure.py`（百選スキーム統合）・`ariadne-jiken-to-labeled.py`
  （事件情報をラベル化）・`ariadne-problem-restyle.py`（番号付き問題文2カラム）・`ariadne-sechead-contrast.py`。
  版マーカー＝`ARIADNE v1.3.0 TXLEX-UNIFY`／契約＝`ARIADNE_SLOT_CONTRACT v1.3.0 TXLEX-UNIFY`。
- 詳細は **`docs/rx-arb-byproducts.md`**（副産物の正典）。

---

## 検証スクリプト早見

| script | 対象 | チェック |
|---|---|---|
| `validate-tx-core.py` | TX v11/v12 コア | G1〜G45 |
| `validate-tx-deep.py` | TX v11 別冊 | D1〜D13 |
| `validate-tx-gold.py` | TX v10 | G1〜G19（legacy 保守） |
| `validate-tx.py` | TX v8.x〜v9.x | S1〜S91（legacy） |
| `validate-jx.py` | JX | J1〜J21＋JC1〜JD1(v4)＋JSB（タグ均衡） |
| `validate-rx.py` / `validate-tts.py` | RX論証 / TTS台本 | 各系 |
| `validate-ariadne.py` / `check-ariadne-canonical.py` | ARIADNE | A1〜A39／canonical＋全出力横断（A34 骨子 SIMPLE-BONE・**A35 深掘りテンプレ流用 ERROR**・A36-A39 版/未定義box/draft逐語/bc-inst 2カラム・`.ariadne-current-law-note` 正典CSS/slot allowance 含む） |

---

## 旧 spec の扱い（整理済み・2026-06-13）

`spec/` 直下は **active のみ**に整理した：

```
spec/
  tx-v12.1.0-inline-core.md ← TX 現行（v12.2.1 表示LOCK 含む）
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
