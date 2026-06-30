# Lexia側引継ぎ: TX-LEX 356-360 取込確認

## 目的

bar-exam側で改善済みのTX-LEX生成物が、Lexia側で正しく取り込まれ、SM2学習カードとして崩れず表示・周回できるかを確認する。

今回のLexia側作業は「アプリ側確認」が主であり、bar-exam生成物の本文改修は完了済み。Lexia repoで本文を書き換えない。

## bar-exam側で完了済み

- 対象: `刑TX356` から `刑TX360`
- 変更: `outputs/ux/000_TX/001_刑法/*_lex.html` の最終表「論点のコア」を、Lexia/SM2向けに「文言・趣旨・射程・切断点・転用」の5点セットへ改善
- 保持: `title` / `code` / `fileName` / `footer` / `data-rx` / `data-athena-code` は破壊なし
- 検証: 対象5ファイルの `validate-tx-core.py` はすべて `Errors: 0 / Warnings: 0 / PASS`
- 本文同期契約: `check-lexia-preflight.py --skip-self-test` は `PASS`
- 直接同期契約: `check-lexia-sync-contract.py --summary outputs references` は `ERROR=0 / WARNING=0`
- push済み: `bar-exam` の `origin/claude/gen`
- commit: `e571481d Improve TX Lexia reflex cores 356-360`

対象ファイル:

- `outputs/ux/000_TX/001_刑法/刑TX356_lex.html`
- `outputs/ux/000_TX/001_刑法/刑TX357_lex.html`
- `outputs/ux/000_TX/001_刑法/刑TX358_lex.html`
- `outputs/ux/000_TX/001_刑法/刑TX359_lex.html`
- `outputs/ux/000_TX/001_刑法/刑TX360_lex.html`

## 重要な注意

Lexiaがどのbar-examブランチを同期元にしているかを最初に確認する。

- Lexiaが `origin/claude/gen` を見ているなら、commit `e571481d` がそのまま確認対象。
- Lexiaが `master` / `main` など既定ブランチを見ているなら、`e571481d` がまだ同期対象に入っていない可能性がある。同期元ブランチと取得commitを確認してから判断する。

## Lexia側で確認すること

1. 取込対象が `ux/000_TX` の `_lex.html` になっていること
2. `刑TX356` から `刑TX360` がLexia上で重複せず、既存カードを更新すること
3. `code` はLexia上で公式TXと増殖せず、従来どおり `TX356` などに正規化されること
4. SM2カードで最終表の5点セットが表示されること
5. 長文化によってカード本文が崩れないこと
6. 「文言・趣旨・射程・切断点・転用」が検索・復習時に本文として拾えること
7. TX356-360以外のカードに更新ノイズが出ていないこと

## 確認観点

短答対策として、各カードは次の状態になっていれば合格。

- 1枚だけ出ても、条文文言から正誤が切れる
- どの制度趣旨・保護法益で区切るかが見える
- 判例・学説の射程が短くまとまっている
- 誤答の切断点が明示されている
- 別問題への転用先が分かる

特に確認すべきテーマ:

- `刑TX356`: 放火罪、公共の危険、建造物一部性、現住性
- `刑TX357`: 放火行為、焼損、建造物性、108条の「人」
- `刑TX358`: 焼損学説、独立燃焼説、効用喪失説、中止犯との関係
- `刑TX359`: 110条、112条、111条、108条艦船、116条2項
- `刑TX360`: 延焼罪、未遂、予備、消火妨害、115条擬制

## Lexia側セッションへ投げるプロンプト

以下をLexiaプロジェクト側に貼る。

```text
bar-exam側でTX-LEX改善済みの5ファイルがpushされています。Lexia側で取込・表示・SM2カード更新を確認してください。

対象:
- 刑TX356
- 刑TX357
- 刑TX358
- 刑TX359
- 刑TX360

bar-exam:
- repo: https://github.com/xnhsky/bar-exam.git
- branch: origin/claude/gen
- commit: e571481d Improve TX Lexia reflex cores 356-360
- files: outputs/ux/000_TX/001_刑法/刑TX356_lex.html から 刑TX360_lex.html

確認してほしいこと:
1. Lexiaが同期元としてどのbar-examブランチ/commitを見ているか確認
2. ux/000_TX の _lex.html が取り込まれていることを確認
3. TX356〜TX360が重複せず既存カード更新として入ることを確認
4. SM2カード本文に「文言・趣旨・射程・切断点・転用」の5点セットが出ることを確認
5. 表示崩れ・本文欠落・ID不一致・更新ノイズがないことを確認
6. 問題がなければLexia側の通常デプロイ手順で反映

注意:
- bar-exam生成物本文はLexia側で編集しない
- Lexia側で必要なのは取込・表示・SM2挙動・デプロイ確認
- もしLexiaがmaster/mainを同期元にしていてe571481dが見えない場合は、その旨を報告して止める
```

## 報告形式

Lexia側の確認後は次の形式で返す。

```text
対象:
確認内容:
同期元:
取込結果:
表示/SM2結果:
デプロイ結果:
残課題:
```

