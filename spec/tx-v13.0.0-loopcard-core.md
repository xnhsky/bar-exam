# TX v13.0.0 LOOP-CARD — 構造正典（core spec）

> TX 短答 `_lex`（Lexia 取込用）の第2世代フォーマット。**gold＝`canonical/GENESIS-CARD.html`（刑TX359）**。
> スロット契約＝`canonical/GENESIS-CARD.placeholder.html`。系譜の active 判定は `docs/canonical-lineage.md`。
> v12.2.1 LOOP-CORE（`GENESIS-CORE.html`）を凍結せず**並存**させる（既存 v12 資産の保守のため）。
> **新規生成・v13 化は本 spec と GENESIS-CARD を唯一の起点にする。** 二系統（公式 `000_TX` ＋ Lexia `_lex`）は
> `spec/tx-v11.1.0-twotrack.md` を継承（v13 の対象は `_lex`）。

---

## 第0項 設計思想 ── 「肢を解く UI」から「読む解説」へ

v12.2.1 は問題文直下のインライン肢カードに **ANSWER 箱＋5点フロー（文言/趣旨/射程/切断点/転用）＋
記憶フック** を積む「解く」設計だった。v13 は、周回で**読み込む解説**を主役にする再編：

- **廃止**：`.tx-answer-box`（ANSWER 箱）、`.tx-article-flow`（5点フロー）、`.tx-onepoint`（記憶フック）、
  各肢の `.tx-mini-law`（条文判例チップ）。
- **昇格**：旧 PART B（`choice-section`）の統合解説プロース（📜記述原文／💡THE GIST／段階解説／💭INTUITION／
  📌POINT）を、詳説トグルから**記述カード本文の位置へ**。
- **集約**：条文・判例は各カードの **「📚 BASIS」ボックス**へ（下部 `#basis` は現行法note だけ残す）。
- **相互リンク往復**・**正誤マーキング**・**他科目横断（重要接点のみ）**を新設。

---

## 第1項 ページ縦順（LOCKED）

1. **正誤表（テーゼ版パネル）** `.tx-inline-answer-table-panel` … 体系マップの直上。
2. **体系マップ（SVG ハイブリッド）** `.tx-sysmap`（内に `svg.tree-svg`）。
3. **横断** `.tx-sysmap-cross`（体系マップ直下・3軸マトリクス表）。
4. **肢カード群** `.tx-inline-judge-list`（`.tx-inline-card` × N）。
5. **物語** `.tx-inline-story-panel`（肢カード**直後**）。
6. **#basis** … `.tx-current-law-note`（現行法note）のみ。条文/判例カードは各カードへ移設済み。

> 旧 `#mindmap-tree`／`#mindmap-radial`（下部 SVG 2枚）は**廃止**。

---

## 第2項 正誤表（テーゼ版・エンジン自動圧縮）

- 元表 `.statement-verdict-table` は `.final-answer` 内に置き、`inline-prototype-mode` では **display:none**
  （answer-key/検証用にデータ源として DOM 保持）。
- エンジンが元表を複製し、論点コア列を **1文テーゼへ自動圧縮**したクローンを
  `.tx-inline-answer-table-panel` に描画（見出し「登場した論点のコア（転用可能な法理）」）。挿入位置は
  `getInlineAnswerTablePanel` が **`.tx-sysmap` の直前**。
- `moveStatementVerdictTableToTop` は元表を持ち上げ**ない**（fa 内に隠す）。二重表示を作らない。

---

## 第3項 体系マップ（SVG ハイブリッド）

- `.tx-sysmap` 内に `svg.tree-svg.tx-sysmap-svg`。**客体三分ツリー**（例 放火＝108/109/110、機能別トップ色
  108=赤 `#b0635c`／109=アンバー `#c99a3a`／110=青 `#5a86a8`）＋親からの分岐コネクタ。
- **本問N局面**を色分けした記述札（`<a href="#stmt-N">`）＋**○×帰結**ボックス。
- SVG の座標骨格・class は固定。ノード文言・記述リンク・帰結は問題固有スロット。**rect/ellipse は
  全ペア非重なり**（`validate-tx-core` の重なり検査＝旧 G10 相当を SVG に適用可）。
- **使い方説明・凡例テキストは載せない**（`.tx-sysmap-lead`／SVG legend は不要）。

---

## 第4項 横断（体系マップ直下）

- `.tx-sysmap-cross`。**表に見出し**（`.tx-cross-tabletitle`）を付け、`<h4>` の 🔗横断見出しと説明文は
  **載せない**（体系マップと重複するため）。
- 表＝客体×所有×危険犯（抽象/具体）の3軸マトリクス。**決め手**（`.col-key .ck-tag`）と
  **THROUGH-LINE**（`.col-type strong`）は**食み出しタブ**。表ラベルは letter-spacing/text-indent を効かせない。

---

## 第5項 記述カード（`.tx-inline-card > .tx-inline-explain[hidden]`）の物理順（LOCKED）

1. `.tx-v13-verdict` … 判定バッジ（○×＋一言理由）。
2. `.sub-card.synthesis` … 🎯統合解説。中身の順＝
   `.syn-orig`（📜記述原文＋**正誤マーキング**） → `.syn-lead`（💡THE GIST） → `.syn-path`（段階解説・番号） →
   `.syn-image`（💭INTUITION）。**SYNTHESIS の外箱は平坦化**（枠・背景を外し、内側の GIST/INTUITION だけ箱）。
3. `.choice-points` … 📌POINT（ol・要点＋ひっかけの型）。
4. `.sub-card.basis-link` … 📚 BASIS（第6項）。
5. `.tx-v13-trap` … ⚠️間違いやすいポイント（**食み出しタブ**＋本文1字下げ）。
6. `.tx-v13-cross` … 🔗他科目横断（**食み出しタブ**・**重要接点のある記述のみ**・第7項）。

> `.tx-inline-stmt-text`（問題文原文＝○×の設問）はカード頭に常時表示（周回で読むため）。記述原文は
> 解説内 `.syn-orig` にも 📜ラベル付きで再掲（前正典どおり）。

### 5-1 正誤マーキング（記述原文の分かれ目）
- ×記述：誤りの核心語句を `.tx-stmt-x`（赤波線）＋先頭 `.tx-stmt-mk`（×）で囲み、直後に `.tx-stmt-fix`（→ 正しい語）。
- ○記述：正しさの決め手語句を `.tx-stmt-o`（緑下線）＋`.tx-stmt-mk.is-ok`（✓）。

---

## 第6項 BASIS ボックス（各カード内の条文・判例）

- `.sub-card.basis-link` ＝ `.tx-v13-basis-label`（📚 BASIS・**食み出しタブ**）＋ `.tx-basis-items`。
- 条文 `.tx-basis-item`：
  - `.tx-basis-head`（条文名・★頻度バッジ・**常時表示**）＋ 戻り用 `.tx-basis-back`（既定非表示）。
  - `.tx-basis-honbun`（**条文原文＝本文・常時表示**。`p.hanging` は**2カラム**＝項ラベル `.para-num`｜本文
    `.hang-body`。本文頭1字下げ）。
  - `.tx-basis-more`（`<details>`＝**要件性質/保護法益/本問への帰結の note を折りたたみ**。`.kd-item` は
    **ラベル行→本文行**の縦積み、本文1字下げ）。
- 判例 `.tx-basis-item.is-case`：head（判例名）＋honbun（**判旨・常時表示**）＋`.tx-basis-more`（射程/帰結）。
- 各 `.tx-basis-item` に `id="bref-{記述}-{条番号}"`（111条/112条など複合は先頭番号を id、両番号を配線対象に）。
- どの記述にどの条文/判例を置くかは、旧 `#basis` の ref-backlinks（記述N）に従って配分。

---

## 第7項 相互リンク（往復・LOCKED 配線規約）

- 解説内 `a.ref-stat`（条文参照・**背景色は維持**）の `href` を、同カードの `#bref-{記述}-{条番号}` へ配線。
  条番号を含まない語句参照はリンクにせず背景色のみ。
- クリック：対象条文へスムーズスクロール＋`.tx-basis-more` 展開＋`.tx-basis-flash` ハイライト、
  `data-backto` に参照元 id を記録。
- 戻る：`.tx-basis-back`（ジャンプ後のみ表示）で `data-backto` の参照元へ戻る（無ければ同カードの synthesis へ）。
- 配線 JS は **canonical 単一エンジン `<script>` の末尾へ統合**（別 `<script>` を足さない＝**script は最大2本**、
  G41）。`<script>` 内に body 閉じタグ文字列を書かない（Lexia の正規表現マッチ対策）。

---

## 第8項 他科目横断（方針1・重要接点のみ）

- 無理に他教科を足さない。**本当に重要な他科目接点がある記述だけ** `.tx-v13-cross` を置く。
- 刑法内（総論・各論）の横断は他科目横断に**含めない**（別概念）。
- 例（放火 gold）＝失火 → 民法「失火責任法」（刑事＝軽過失で失火罪成立／民事＝重過失がなければ709条責任なし
  の対照）だけ。他の記述は接点が薄ければ付けない。

---

## 第9項 体裁（LOCKED）

- **使い方（操作方法）の説明文は載せない**：体系マップlead／SVG凡例（記述札を押すと…）／BASIS移設note／
  PART B詳説note は不要。
- **タブラベル**（BASIS／間違いやすい／他科目横断／決め手／THROUGH-LINE）は letter-spacing/text-indent を効かせない。
- **本文段落は頭1字下げ**（text-indent:1em）：条文本文・判旨・note 本文・間違いやすい・他科目横断など。
- 重厚感（影・グラデ・立体タブ）は各ボックスに付与。読み幅 container 1080px。

---

## 第10項 検証・配布ゲート

- `python scripts/validate-tx-core.py <_lex>`：**v13 判定＝`.tx-v13-verdict` 検出**。v13 では
  choice-section / ANSWER 箱 / 5点フロー / 記憶フックの旧必須を解除し、v13 構造（synthesis 昇格・BASIS
  トグル・体系マップ SVG・#basis 現行法note）を検査。旧 v12 ファイルは従来どおり検証（非退行）。
- `python scripts/check-tx-lex-engine.py`：G41 単一エンジン＋script 最大2本。
- `python scripts/check-duplicates.py outputs`：他ファイルとの重複・ID 不整合。
- レンダリング実測（playwright）で、正誤表テーゼ／体系マップ／相互リンク往復／トグル／マーキングの
  表示と pageerror 0 を確認する（省エネ検証は執筆者本人が丁寧に1回＋自己照合＋的絞りWeb一次確認）。

---

## 第11項 移行・並存

- **v13 は当面 gold（刑TX359）のみ**。既存 355-358・360-385 は v12.2.1 のまま保守（GENESIS-CORE）。
- 他問の v13 化は、GENESIS-CARD を複製して本 spec のスロットを埋め直す（決定論 recanon か再生成）。
  旧 _lex への band-aid・接ぎ木は禁止（§7 保守的書き換え禁止）。
- 実装来歴：gold は patch script 連鎖（scratchpad build_v13b〜v14b）で 885aea1c/049cebf2 から生成。
  今後の正典改定は GENESIS-CARD を単一情報源にし、決定論スクリプトで載せ替える。
