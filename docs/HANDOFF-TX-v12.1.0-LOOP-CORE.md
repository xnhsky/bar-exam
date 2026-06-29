# Claude 引継ぎ: TX v12.1.0 LOOP-CORE

> 目的: Codex 側で確定した TX/TXLEX 生成物正典の変更分を、Claude 側の新規生成・改修へ正しく引き継ぐ。
> JX / ARIADNE は別セッションで作成中のため、この文書では扱わない。

## まず読むファイル

1. `spec/tx-v12.1.0-inline-core.md`
2. `canonical/GENESIS-CORE.html`
3. `.claude/commands/new-tx.md`
4. `docs/canonical-lineage.md`
5. 参照実装: `outputs/ux/000_TX/001_刑法/刑TX360_lex.html`

## 現行バージョン

- Active: **TX v12.1.0 LOOP-CORE**
- Major change: **v12.0.0**
  - 周回の主導線を下部 ox-grid から、問題文直後の `.tx-inline-card` へ移した。
  - PART B は独立巡回先ではなく、各肢カードの「詳説を開く」に吸収する。
- Minor change: **v12.1.0**
  - TX360 試作で合意した仕上げを正典化した。
  - 上部5秒トースト、iPhone余白、Mildliner 系配色、条文原文カード、記憶フック、答案圧縮、SM2 ミラーを固定した。

## 二系統の絶対ルール

- `outputs/000_TX` は公式TX。過去問本来の5択を保つ。Lexia用導線を入れない。
- `outputs/ux/000_TX` は Lexia 用 `_lex` のみ。物語解説、インライン肢カード、記憶フック、答案圧縮、詳説トグルはここに置く。
- 公式TX混入なし。二重同期なし。
- 変更は対象ファイルだけに限定し、未追跡/退避物を stage しない。

## v12 の画面構造

Lexia 用 `_lex` では、問題文の各肢に対応する `.tx-inline-card[data-stmt]` を置く。

標準順序:

```html
<article class="tx-inline-card" data-stmt="1">
  <div class="tx-inline-head">
    <p class="tx-inline-stmt">...</p>
    <div class="tx-inline-actions">○ / ×</div>
  </div>
  <div class="tx-inline-explain">
    <div class="tx-mini-law">...</div>
    <div class="tx-article-flow">...</div>
    <div class="tx-cycle-aids">...</div>
    <details class="tx-inline-detail">...</details>
  </div>
</article>
```

裏の `.answer-area[data-answer-type="ox-grid"]` と `.answer-ox-grid` は削除しない。Lexia/SM2 記録、answer-key、検証の単一情報源として保持する。

## 条文・判例カード

- 条文番号は「刑法」と「第百八条」のように、法令名と条番号を別ラベルにする。
- 条番号は原則として漢数字表記にする。
- 条文カードは条文本文の原文を主役にする。
- 注釈は条文原文より目立たせない。説明は下の判断ブロックまたは詳説へ寄せる。
- 主条文はブルー系、判例はピンク系、補助条文・文脈条文はグレー系。
- 文言、趣旨、射程、転用は Mildliner レモンイエロー系。切断点は Mildliner ピンク系。

## 判断ブロック

各肢カードには以下を置く。

- 文言
- 趣旨
- 射程
- 切断点
- 転用

二文字ラベル（文言、趣旨、射程、転用など）は字間スペースを入れ、中央に揃える。切断点はピンク系で視覚的に区別する。

## 記憶フック・答案圧縮

- 記憶フックは紫系のバッジ/ボックス。
- 答案圧縮はピンク系のバッジ/ボックス。
- どちらも周回出口の一文であり、正解番号だけを示すネタバレ文にしない。
- 答案圧縮は「要件/条文 -> 本件 -> 結論」の形で、論証や短文答案へ転用できるテーゼにする。

## 詳説トグルと PART B

- 「詳説を開く」は、その肢に対応する PART B 詳説をカード下へ展開する。
- PART B は実質的に詳説ソースであり、独立した周回先にしない。
- 通常周回は `.tx-inline-card` 内で完結する。
- 迷った肢、誤答した肢だけ詳説を開く。

## 解答表示 UX

- 全5肢を選ばなくても「解説だけ閲覧」で解説を開ける。
- 「解説だけ閲覧」は `answered` を付けず、SM2 記録を発生させない。
- 解答ボタン押下後は、従来の最終解説を残しつつ、上部に5秒トーストを表示する。
  - 正解: `正解🎉`
  - 不正解: `不正解😢`

## iPhone / モバイル

- 入れ子の枠線を増やしすぎない。
- 詳説は右寄りの入れ子表示にせず、カード内で画面幅を使って見せる。
- `.tx-inline-card`、条文カード、詳説パネルは左右余白を詰め、本文幅を確保する。
- 本文はつぶれるほど太くしない。問題文側は読みやすく少し太め、解説本文側は過度な bold を避ける。

## 問題都合ラベルの扱い

記号問題、空欄問題、見解ラベル問題、組合せ問題では、学習資産側に問題都合ラベルを残さない。

- 残さない例: `記述ア`、`肢3`、`A説`、`B説`、`①`、`(a)`、`事例Ⅰ`、`本問`
- 置換先: 論点コア、テーゼ、実体学説名、制度名、要件名、自己完結命題
- 公式問題文の原文は保持する。置換するのは解説、SM2、周回用要約である。

## Lexia / SM2

SM2 は長い読み物ではなく、誤答肢を次回再判定する場所。

優先順位:

1. `.ox-stmt`
2. `.tx-reflex-core`
3. `.tx-cycle-aids`
4. メイン条文本文
5. `.tx-inline-detail` / PART B 詳説

`.fa-narrative` は初回理解用であり、通常カード本文へ載せない。

v12 inline 型では `.tx-reflex-core` と `.tx-cycle-aids` の要点を `.ox-row .ox-pool-explain` にミラーする。SM2 payload に narrative、詳説長文、問題都合ラベルを混ぜない。

## Claude への生成指示テンプレート

以下を Claude に渡す。

```text
TX/TXLEX は v12.1.0 LOOP-CORE を現行正典として生成してください。
必ず spec/tx-v12.1.0-inline-core.md、canonical/GENESIS-CORE.html、.claude/commands/new-tx.md を読み、刑TX360_lex.html を参照実装として扱ってください。

公式 outputs/000_TX は本物の5択のまま、Lexia 用 outputs/ux/000_TX は _lex のみです。公式TXに Lexia 導線を混ぜないでください。

Lexia _lex では、問題文直後に各肢対応の tx-inline-card を置き、条文原文、文言・趣旨・射程・切断点・転用、記憶フック、答案圧縮、詳説トグルを同じカード内に統合してください。

PART B は独立周回先ではなく、各肢カードの「詳説を開く」で展開される詳説ソースとして扱ってください。

記号問題・組合せ問題・見解ラベル問題では、解説・SM2・周回要約に問題都合ラベルを残さず、論点コア・テーゼ・自己完結命題へ置換してください。公式問題文の原文だけは保持します。

SM2 用には .ox-row .ox-pool-explain を最優先ソースとして整備し、tx-reflex-core と tx-cycle-aids の要点をミラーしてください。narrative や詳説長文は通常 SM2 payload に入れないでください。

検証は validate-tx-core.py、check-lexia-sync-contract.py --summary outputs references、check-lexia-preflight.py --skip-self-test を通してください。
```

## 検証コマンド

```powershell
git status --short --branch
git pull --ff-only origin master
python -X utf8 scripts\validate-tx-core.py "outputs\ux\000_TX\001_刑法\刑TX360_lex.html"
python -X utf8 scripts\validate-tx-core.py canonical\GENESIS-CORE.html
python -X utf8 scripts\check-lexia-sync-contract.py --summary outputs references
python -X utf8 scripts\check-lexia-preflight.py --skip-self-test
git diff --check
```

新規問題生成時は、対象の公式TXと `_lex` の両方を検証する。公式TXは real 5-choice、`_lex` は ox-grid / inline-card / SM2 mirror を持つこと。

## 注意

- 刑TX394_lex の G27 は既知注意点として扱い、勝手に大改造しない。
- 既存 v10/v11 問題を一括 v12 化しない。必要な範囲を1問ずつ再生成する。
- JX / ARIADNE / RX / TREE はこの引継ぎの対象外。
- 今後、ユーザーと合意した TX/TXLEX 変更は、都度「試作 -> 恒久対策 -> 正典化 -> validator/preflight」の順で扱う。
