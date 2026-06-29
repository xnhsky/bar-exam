# TX v12.1.1 LOOP-CORE inline canon（2026-06-29）

> **ステータス：現行 active。** ファイル名は `tx-v12.1.0-inline-core.md` のまま維持するが、現行運用は **v12.1.1 typography patch** を含む。v11.0.0 の肢単位管理、v11.1.0 の誌面リスキン、v11.1.0-twotrack の公式/ Lexia 二系統を継承したうえで、Lexia 用 `_lex` の周回導線を **インライン肢カード中心**に正典化する。

## バージョン規律

- **v12.0.0（major）**：周回の主導線を、下部 ox-grid から問題文直後の `.tx-inline-card` へ移す。PART B は独立巡回先ではなく、各肢カードの「詳説を開く」に吸収される。
- **v12.1.0（minor）**：TX360 試作で合意した誌面仕上げを正典へ固定する。上部5秒トースト、iPhone向け余白、条文原文カード、文言/趣旨/射程/切断点/転用、記憶フック、答案圧縮、SM2 用ミラーを含む。
- **v12.1.1（patch / active）**：物語解説のタイポグラフィを固定する。`.fa-narrative` 本文は読み物として軽く、強調語 `.fa-narrative b` は `font-weight:560` 以下に抑え、700系の太字へ戻さない。

## v12 の主導線

1. 問題文の各肢直後に `.tx-inline-card[data-stmt]` を置く。
2. 各カードは、肢本文、○×ボタン、条文原文カード、判断ブロック、記憶フック、答案圧縮、詳説トグルを持つ。
3. 裏の `.answer-area[data-answer-type="ox-grid"]` と `.answer-ox-grid` は削除しない。Lexia/SM2 記録、answer-key、検証の単一情報源として保持し、インライン面から同期する。
4. 「解説だけ閲覧」は `answered` を付けず、SM2 記録を発生させない。
5. `reveal` 時は従来の最終解説を残しつつ、上部トーストで正解/不正解を5秒表示する。

## 各肢カードの標準順序

```
article.tx-inline-card[data-stmt]
  .tx-inline-head
    .tx-inline-stmt
    .tx-inline-actions (.tx-inline-ox ○ / ×)
  .tx-inline-explain
    .tx-mini-law
      .tx-law-item.is-main     # 主条文。ブルー系。
      .tx-law-item.is-support  # 補助条文。グレー系。
      .tx-law-item.is-context  # 文脈条文。薄グレー系。
      .tx-law-item.is-case     # 判例。ピンク系。
    .tx-article-flow
      文言
      趣旨
      射程
      切断点
      転用
      .tx-cycle-aids
        記憶フック
        答案圧縮
      details.tx-inline-detail
```

## 条文・判例カード

- 条文番号は「刑法」「第百八条」のように、法令名と条番号を別ラベルにする。
- 条文本文は原文を主役にする。注釈は条文カード内で目立たせず、下の判断ブロックまたは詳説へ寄せる。
- 主条文はブルー系、判例はピンク系、補助条文・文脈条文はグレー系で、重要度の濃淡を視覚化する。
- 試験慣れのため、条文番号は漢数字表記を標準とする。

## 記憶フック・答案圧縮

- 記憶フックは紫系、答案圧縮はピンク系のバッジ/ボックスに入れる。
- どちらも周回出口の一文であり、正解番号だけを示すネタバレ文にしない。
- 答案圧縮は「要件/条文 → 本件 → 結論」の形で、論証や短文答案へ転用できるテーゼにする。

## 物語解説のタイポグラフィ

- `.fa-narrative` は初回理解のための読み物であり、周回時の主導線ではない。
- 本文は通常ウェイトを基本とし、重要語だけを `<b>` で示す。
- `<b>` は色で目を止める。太さで押し切らない。正典値は `.fa-narrative b{ font-weight:560; }`。
- iPhone では濃い明朝太字が潰れて見えるため、`600` 超や `700` 系の太字へ戻さない。

## 問題都合ラベルの扱い

- 記号問題、空欄問題、見解ラベル問題では、`.ox-stmt`、`.tx-reflex-core`、`.tx-cycle-aids`、`.ox-pool-explain` に問題都合のラベルを残さない。
- Lexia/SM2 の表面に入れるのは、組合せ番号や空欄記号ではなく、論点コア・テーゼ・自己完結命題である。
- 公式問題文の原文は保持する。置換するのは学習資産側だけである。

## Lexia/SM2

- 復習プールの最優先ソースは `.ox-row .ox-pool-explain`。
- v12 inline 型では、`.tx-reflex-core` と `.tx-cycle-aids` の要点を `.ox-pool-explain` にミラーする。
- narrative、詳説本文、問題固有ラベルは SM2 payload に混ぜない。復習プールは「次回それだけを見て○×判断を復元できる最小テーゼ」にする。

## 継承

- 構造基盤：`spec/tx-v11.0.0-core.md`
- 二系統出力：`spec/tx-v11.1.0-twotrack.md`
- active canonical：`canonical/GENESIS-CORE.html`
- validator：`scripts/validate-tx-core.py`
