# bar-exam側引継ぎ: TX-LEX実装フェーズ

## 現在地

このプロジェクトのフェーズは次の整理。

1. Lexia改善方針: 完了
2. 生成物監査: 完了
3. TX-LEX実装: 現在ここ

ユーザーはLexiaで刑法TXを学習中。現在の学習進度はTX355まで。したがって、今後のbar-exam側作業は、TX356以降を優先して、Lexiaで学習に追いつかれない前方在庫を作る。

## 絶対ルール

- 触るのは `C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam` のみ。
- Lexia repoは触らない。
- destructive commandは禁止。
- `scripts/` は原則触らない。
- push/deployはユーザーが明示したときだけ。
- `title` / `code` / `fileName` / `footer` / `data-rx` / `data-athena-code` を壊さない。
- 配色・フォント・余白・カード感など、正典の見た目を崩さない。
- 作業ツリーに大量の既存変更がある。自分が触る対象以外をstageしない、戻さない。

## repo状態

- repo: `https://github.com/xnhsky/bar-exam.git`
- branch: `claude/gen`
- latest pushed commit: `e571481d Improve TX Lexia reflex cores 356-360`
- pushed target:
  - `outputs/ux/000_TX/001_刑法/刑TX356_lex.html`
  - `outputs/ux/000_TX/001_刑法/刑TX357_lex.html`
  - `outputs/ux/000_TX/001_刑法/刑TX358_lex.html`
  - `outputs/ux/000_TX/001_刑法/刑TX359_lex.html`
  - `outputs/ux/000_TX/001_刑法/刑TX360_lex.html`

## 注意すべき作業ツリー

`git status` には、以前のセッション由来の変更が多数残っている。

- `outputs/ux/000_TX/001_刑法/刑TX001_lex.html` ほか多数のTX-LEX改善済みファイル
- `outputs/ux/001_ARIADNE/001_刑法/*_ARIADNE.html`
- `outputs/ux/002_RX/001_刑法/*`
- `outputs/ux/003_TREE/001_刑法/*`
- `canonical/ARIADNE.html`
- `canonical/GENESIS-CORE.html`
- `docs/tx-lex-two-track.md`
- `scripts/` 配下の既存変更
- 未追跡の指南書・Lexia引継ぎ等

これらはユーザーまたは既存作業の変更として扱い、勝手に戻さない。commit/pushするときは、必ず対象ファイルを明示して `git commit --only ...` などで限定する。

## TX-LEX実装の品質基準

TX-LEXは短答の主力教材。Lexia/SM2で1枚ずつ出ても切れる自己完結カードにする。

最終表「論点のコア」は、原則として次の5点セットにする。

- 文言: 条文・判例の入口
- 趣旨: 制度趣旨・保護法益
- 射程: どこまで当たるか
- 切断点: 誤答をどこで切るか
- 転用: 別問題への使い方

避けるもの:

- 選択肢番号・学生A/B/Cだけに依存する説明
- 「本問では」だけで終わる説明
- 長いストーリー解説を最終表に入れること
- 論文答案風の厚い説明
- 大きいマインドマップ追加
- 正典の配色・フォント・余白を崩す変更

## 実装パターン

対象ファイルに `.tx-reflex-core` CSSがなければ、`.statement-verdict-table` 周辺CSSの直後に追加する。

```css
/* TX-LEX short-answer reflex core: 文言・趣旨・射程・切断点・転用 */
.tx-reflex-core{
  display:grid;
  gap:6px;
  margin:0;
  font-size:.94em;
  line-height:1.7;
}
.tx-reflex-line{
  margin:0;
  padding-left:5.4em;
  text-indent:-5.4em;
}
.tx-reflex-tag{
  display:inline-block;
  min-width:4.2em;
  margin-right:.55em;
  padding:.12em .48em;
  border-radius:999px;
  border:1px solid #d7cfa8;
  background:#efe7cb;
  color:#65581d;
  font-weight:800;
  text-align:center;
  text-indent:0;
}
.tx-reflex-cut .tx-reflex-tag{
  border-color:#dba9b2;
  background:#ffefe7;
  color:#774252;
}
```

表見出しは次へ変更する。

```html
登場した論点のコア（文言・趣旨・射程・切断点・転用）
```

## 次にやること

次バッチは、学習進度から見て以下が自然。

- 第1候補: `刑TX361_lex.html` から `刑TX365_lex.html`
- その次: `刑TX366_lex.html` から `刑TX370_lex.html`
- 前方30問の目安: `刑TX356` から `刑TX387` 付近。ただし `刑TX381` は既に別作業で改善済みの可能性があるため、重複確認する。

作業開始時は、対象ファイルごとに次を確認する。

- 最終表があるか
- `.tx-reflex-core` が既にあるか
- `data-answer-key` が壊れていないか
- `title/code/fileName/footer/data-athena-code` に触れていないか

## 検証

対象ごとに必ず実行する。

```powershell
python scripts\validate-tx-core.py outputs\ux\000_TX\001_刑法\刑TX361_lex.html
```

複数ファイルなら対象分すべて通す。

本文側の同期契約確認:

```powershell
python scripts\check-lexia-sync-contract.py --summary outputs references
```

補助preflight:

```powershell
python scripts\check-lexia-preflight.py --skip-self-test
```

注意: 現時点では、通常の

```powershell
python scripts\check-lexia-preflight.py
```

は既存の `scripts/` 側自己テスト不整合で停止する。本文変更の問題ではない。ユーザーへの報告では、「通常preflightはscripts自己テストで停止、本文側sync contractはERROR=0/WARNING=0」と具体的に書く。

## pushするとき

pushはユーザー明示時のみ。

作業ツリーが混ざっているため、必ず対象限定でcommitする。

例:

```powershell
git commit --only -m "Improve TX Lexia reflex cores 361-365" -- `
  outputs/ux/000_TX/001_刑法/刑TX361_lex.html `
  outputs/ux/000_TX/001_刑法/刑TX362_lex.html `
  outputs/ux/000_TX/001_刑法/刑TX363_lex.html `
  outputs/ux/000_TX/001_刑法/刑TX364_lex.html `
  outputs/ux/000_TX/001_刑法/刑TX365_lex.html
```

push:

```powershell
git push -u origin claude/gen
```

## 新規bar-examセッション用プロンプト

新しいbar-examプロジェクト側セッションには、以下を貼る。

```text
bar-exam repo 側の作業です。Lexia repo は触らないでください。
このセッションはTX-LEX実装フェーズです。

制約:
- C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam だけ触る
- destructive command禁止
- scripts/ は原則触らない
- title/code/fileName/footer/data-rx/data-athena-code を壊さない
- 正典の配色・フォント・余白・カード感を守る
- push/deployは私が明示したときだけ

現在地:
- Lexia改善方針と生成物監査は完了
- 今はTX-LEX実装フェーズ
- 私の学習進度はTX355まで
- 刑TX356〜360は改善済み・検証済み・push済み
- commit: e571481d Improve TX Lexia reflex cores 356-360

次にやること:
- 刑TX361〜365を優先して、最終表の「論点のコア」を文言・趣旨・射程・切断点・転用の5点セットに改善
- Lexia/SM2で1枚ずつ出ても切れる自己完結カードにする
- 見た目の正典は崩さない

検証:
- 対象ごとに validate-tx-core.py
- check-lexia-sync-contract.py --summary outputs references
- check-lexia-preflight.py --skip-self-test

注意:
- 通常の check-lexia-preflight.py は既存scripts自己テスト不整合で止まる可能性あり
- 作業ツリーに既存変更が多いので、commit/pushする場合は対象ファイルだけ限定

報告形式:
対象:
変更ファイル:
改善内容:
検証結果:
残課題:
```

