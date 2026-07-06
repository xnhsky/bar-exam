# TX v13.1.0 LOOP-CARD — 構造正典（core spec）

> TX 短答 `_lex`（Lexia 取込用）の第2世代フォーマット。**gold＝`canonical/GENESIS-CARD.html`（刑TX359）**。
> スロット契約＝`canonical/GENESIS-CARD.placeholder.html`。系譜の active 判定は `docs/canonical-lineage.md`。
> v12.2.1 LOOP-CORE（`GENESIS-CORE.html`）を凍結せず**並存**させる（既存 v12 資産の保守のため）。
> **新規生成・v13 化は本 spec と GENESIS-CARD を唯一の起点にする。** 二系統（公式 `000_TX` ＋ Lexia `_lex`）は
> `spec/tx-v11.1.0-twotrack.md` を継承（v13 の対象は `_lex`）。
>
> **版（LOCKED・2026-07-06）：v13.1.0＝最新（active）。** v13.0.0 LOOP-CARD（読む解説昇格＋📚BASIS＋テーゼ正誤表）を
> 基盤に、**v13.1.0 で正誤表を「印付き記述原文＋法理コア＋成績表示＋重厚感」へ再設計、体系マップに ✍規範核バッジを追加、
> 『本問の帰結』箱を廃止、各カード末尾に体系マップ復路リンクを追加**（第2・3・5項）。**完全リデザイン済み**（規範核バッジ
> ＋印付き原文の両方を持つ）の `_lex` が v13.1.0、未適用の v13 本文は v13.0.0（`scripts/tx-lex-verdict-redesign.py` で土台注入
> ＋各問で規範核・印付き原文を執筆して移行）。版は `scripts/tx-lex-v13-stamp.py` が実体から自動判定して feature-tag/genmeta/
> footer の3箇所を揃える。**以後の設計変更は大小を判断して版を整理し、取り残し・漏れを出さない（feedback: バージョン整理）。**

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

## 第2項 正誤表（印付き記述原文＋法理コア＋成績表示）

- 元表 `.statement-verdict-table` は `.final-answer` 内に置き、`inline-prototype-mode` では **display:none**
  （answer-key/検証用にデータ源として DOM 保持）。
- エンジンが元表を複製し `.tx-inline-answer-table-panel` に描画。挿入位置は `getInlineAnswerTablePanel` が
  **`.tx-sysmap` の直前**。見出しは「各記述の原文（誤り箇所に下線＋正解）と転用可能な法理」。
- **各行＝印付き原文＋法理コアの2段（LOCKED）**：論点コア列を、① **印付き記述原文**（`.tx-vb-orig-mark`＝各肢
  カードの `.syn-orig` と同じ marking。×＝誤り核語句に赤波下線 `.tx-stmt-x`＋`.tx-stmt-mk`✕＋`.tx-stmt-fix`で
  「→正解」、○＝決め手に緑下線 `.tx-stmt-o`＋✓）と、② **法理コア**（`.tx-vb-core`＝射程行の1文テーゼ）に再構成。
  印付き原文は各行 `<tr>` の **`data-brief-mark`**（問題固有スロット・属性は二重引用、内側 class は単引用 `'…'`）に
  HTML で持たせ、エンジンが innerHTML 展開する。フル `.syn-orig` は長いので**要約版**を鋳造する（カードは精読、
  正誤表は文脈付き高速復習の役割分担）。
- **成績表示（LOCKED）**：`renderInlineAnswerTablePanel` が `computeInlineScore` で正解数を集計し、パネル見出し行
  `.tx-inline-answer-table-title-row` の右に `.tx-inline-answer-score` を出す（全問正解＝`is-perfect`「🎉 全問正解！ N/N」／
  一部＝`is-partial`「n / N 正解」／`answered==0` は非表示）。行の正誤は `.tx-user-correct`/`.tx-user-incorrect` で判定
  （browse-only では出さない）。
- **重厚感（LOCKED）**：パネル＝額装フレーム（羊皮紙グラデ＋テクスチャ＋深い影）、見出し＝金プレート（📋）、
  ヘッダー＝金グラデ立体、正解/不正解行＝層状グラデ＋左端アクセント帯、ラベル＝押し出しチップ。ラベルは
  text-indent:0（パネル内 `<p>` が継承するグローバル字下げを打ち消す）。CSS は canonical 同梱。
- 元表の `.tx-reflex-core`（5タグ）は **DOM 保持**（answer-key 源＋G33＋`extractReviewCoreSummary` が射程行を法理コアに使う）。
  `moveStatementVerdictTableToTop` は元表を持ち上げ**ない**（fa 内に隠す）。二重表示を作らない。

---

## 第3項 体系マップ（SVG ハイブリッド）

- `.tx-sysmap` 内に `svg.tree-svg.tx-sysmap-svg`。**客体三分ツリー**（例 放火＝108/109/110、機能別トップ色
  108=赤 `#b0635c`／109=アンバー `#c99a3a`／110=青 `#5a86a8`）＋親からの分岐コネクタ。
- **親カテゴリ箱（`translate(265/750/1235,150)` の3ノード）は「科目の骨格」＝問題共通ブロック**（2026-07-06 リデザイン）。
  各箱＝色ヘッダー（`<tspan>` 太字ラベル＋短説明）→ **太字キー行**（`y=60`・font 14/weight 600・箱の暗色で中央）→
  **淡色補足行**（`y=84`・font 12.5・muted）→ **色チップ2枚**（`.pbox-chip`・`y=100`・条文/危険犯型など転用アンカーを白抜き
  ＋立体影）。放火＝108/109/110、文書偽造＝有形/無形/行使。**問題固有の論点は5局面札へ、親箱は科目共通**（＝どの放火問も同じ
  親箱。伝播＝`scripts/tx-lex-sysmap-pbox.py` が親箱領域を科目別ブロックへ決定論置換＋`.pbox-chip` CSS 注入・冪等・本文/5局面不変）。
- **本問N局面**を色分けした記述札（`<a href="#stmt-N">`）。各札に **✍規範核バッジ**（`.nb-badge` 塗り立体＋
  `.nb-badge-text`＝**転用可能な規範核1文**・ノード accent の暗色で白抜き・11〜14字）を1枚積む（ノード高さ118・
  1行目は決め手/直感、バッジ2行目は答案で書く規範核＝役割を分ける・問題固有スロット）。
- **`▼ 本問の帰結（○×）` ボックスは置かない**（答えを先出ししない設計＝結論は周回で自分で組む。旧正典の帰結箱は廃止）。
- SVG の座標骨格・class は固定。ノード文言・記述リンク・規範核バッジは問題固有スロット。帰結箱を除いた分
  **viewBox 下端を詰める**（例 放火 gold＝`0 0 1500 532`）。**rect/ellipse は全ペア非重なり**（badge rect はノード内に収める）。
- **ハブ往復（LOCKED）**：体系マップは全記述カードのハブ。`.tx-sysmap` に `id="tx-sysmap"` を付け、
  記述札 `#stmt-N` が**往路**（マップ→肢）、各カード末尾の `.tx-sysmap-back`（`href="#tx-sysmap"`）が
  **復路**（肢→マップ）。往路だけで復路を欠かさない（第5項7・生成/移行の必須要素）。
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
7. `.tx-sysmap-back` … ↑ 体系マップに戻る（`<div class="tx-sysmap-back"><a href="#tx-sysmap">`）。
   **解説末尾のハブ復路リンク**（体系マップの記述札 `#stmt-N`＝往路、これ＝復路）。CSS は canonical 既存
   （`.tx-sysmap-back` は `text-align:right`）。`.tx-inline-explain` の**最後の子**（trap/cross のどちらで
   終わっても、その直後）に置く。解説を開いた時のみ体系マップが表示されるため、戻り先 `#tx-sysmap` も可視。

> `.tx-inline-stmt-text`（問題文原文＝○×の設問）はカード頭に常時表示（周回で読むため）。記述原文は
> 解説内 `.syn-orig` にも 📜ラベル付きで再掲（前正典どおり）。

### 5-1 正誤マーキング（記述原文の分かれ目）
- ×記述：誤りの核心語句を `.tx-stmt-x`（赤波線）＋先頭 `.tx-stmt-mk`（×）で囲み、直後に `.tx-stmt-fix`（→ 正しい語）。
- ○記述：正しさの決め手語句を `.tx-stmt-o`（緑下線）＋`.tx-stmt-mk.is-ok`（✓）。

---

## 第5-bis項 Lexia 復習プール（SM2）への配線 ★v13 で必ず更新する

Lexia は `_lex` を取り込み、間違えた記述を **肢キー `{問題ID}#stmt-{記述}`** で SM2 追跡し、一問一答の
復習カードとして提示する。Lexia が復習カードに使う要素（`Lexia/src/App.jsx`）:

- **正解＝ `[data-answer-key]`**（正誤表 `.statement-verdict-table` の `data-answer-key`。権威・単一情報源）。
- **記述文＝ `.ox-row .ox-stmt`**（短ラベル）→ 短い場合 `.syn-orig` にフォールバック。
- **解説（最優先）＝ `.ox-row .ox-pool-explain`**：`.ox-pool-gist`（要点1文）＋ `.ox-pool-points li`
  （`ラベル：本文` を Lexia が `/^([^：:]{1,30})[：:](.*)$/` で分解）。
- **物語＝ `.fa-narrative`**（プールカードにストーリーを載せ、該当段落を強調）。

**v13 配線ルール（LOCKED）**：`.ox-pool-explain` は **v13 のカード内容と同期させる**。
- `.ox-pool-gist` ← 各カードの **💡THE GIST（`.syn-lead` の本文）**（○×結論を含む要点1文）。
- `.ox-pool-points` ← 各カードの **📌POINT（`.choice-points` の各 `li`）**（`実体ラベル：本文`。ひっかけの型を含む）。
- **旧 v12 の5点フロー（文言/趣旨/射程/切断点/転用）を `.ox-pool-points` に残さない**（v13 では廃止した内容で、
  劣化コピーの温床。実体ラベルへ置換＝記号フリー・G30/G50）。
- `.ox-pool-explain` の `data-source` は v13 由来と分かる値にする。
- **正誤表 `.statement-verdict-table`（answer-key 源）と `.answer-ox-grid`／`.ox-row[data-stmt]` は DOM 保持**
  （inline-prototype-mode で非表示でも、Lexia/SM2・answer-key・検証の単一情報源として消さない）。

> v13 化・生成では、カード解説（synthesis/POINT）を書いたら **必ず同じ内容で `.ox-pool-explain` を更新**する
> （伝播ツール例＝scratchpad build_v14c：THE GIST→gist、POINT→points を機械再配線）。

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
- **学説 `.tx-basis-item.is-theory`（ラベンダー・任意項目・2026-07-06 追加）**：head（📖 学説名＝立場を明示、例「独立燃焼説（判例・通説）」）
  ＋honbun（**説の内容・常時表示**）＋`.tx-basis-more`（対立する説／判例との関係／本問への帰結）。**重要な学説対立・通説/有力説が
  記述の決め手になる場合だけ置く**（他科目横断と同じ「重要な時だけ」規律。無理に足さない）。色は ARIADNE(JX) と統一＝条文青/判例ピンク/学説紫。
  gold 例＝刑TX363 記述3（焼損既遂＝独立燃焼説 vs 効用喪失説）。id は `theory-{記述}-{key}`。是非は最新学説レビュー（主要基本書・百選）で裏取り。
  - **短答での位置づけ（2026-07-06 ユーザー方針・重要）**：短答で問われるのは判例/通説の**結論（＝触り）**で、それは各カードの統合解説（THE GIST・段階解説）に既にある。よって学説項目は**焼損の既遂時期・公共危険の認識要否のように、判例と少数説の線引きが正誤の分かれ目になる2〜3類型だけに限り、全問へ横展開しない**（新規生成でも既定は「置かない」）。学説の**深掘り**（対立の全体像・答案での書き分け）は **JX/ARIADNE（論文）** に置く。既存の 刑TX361-370 の7項目は残置（触りは見出しに出て詳細は折りたたみ＝短答周回の邪魔にならない）が、これを基準に増やさない。
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
