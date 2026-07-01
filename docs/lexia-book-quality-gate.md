# TXLEX / ARIADNE 品質ゲート

TXLEX、JX、ARIADNE、RX、TREE は、試験合格まで周回する主教材として扱う。単なるHTML出力ではなく、知識・判断手順・答案化の根源になるため、以下の4層で守る。

## 0. 書物ごとの役割

- **TXLEX**：短答の1肢判断を、条文・判例・論点処理マトリクス・切断点・記憶フックへ圧縮する。記憶フックは詳説要約ではなく、論点のコア・テーゼを一言で思い出す標語にする。
- **JX**：論文問題の百科事典本体。論点抽出、詳細解説、模範答案、採点講評、条文・判例・学説・論証集を網羅する。
- **ARIADNE**：JXから蒸留した周回導線。初見で何を拾い、どの順番で答案構成するかを訓練する。
- **RX**：答案に吐き出す論証カード。規範、理由づけ、答案での使い方、規範チェックに絞る。
- **TREE**：論点全体の地図。処理手順、論証文言、あてはめ事実、失点パターン、参照判例、能動想起を枝で接続する。

## 1. 正典

- TXLEX: `spec/tx-v12.1.0-inline-core.md`
- JX: `spec/jx-v4.0.0-core.md`
- ARIADNE: `spec/jx-ariadne-v1.2.0-core.md`
- RX/TREE: `docs/rx-arb-byproducts.md` と各 validator の契約

各項目の役割、禁止文、完了不可条件をここに固定する。

## 2. 生成元

- TX解法ナビ: `scripts/tx-lex-recanon.py` / `canonical/SOLVE-NAV.html` / `scripts/lex/build-*.py`
- JX: `prompts/new-jx-headless.md` / `canonical` 系JX正典
- ARIADNE: `canonical/ARIADNE.html` / `prompts/new-ariadne-headless.md`
- RX/TREE: `scripts/rx-*` / `scripts/validate-rx.py` / `scripts/validate-tree.py`

汎用ヒントや分野ズレ文が再生成で戻らないよう、生成元の既定文も正典に合わせる。

## 3. 単体検査

- TXLEX: `python scripts/validate-tx-core.py <file>`
- JX: `python scripts/validate-jx.py <file>`
- ARIADNE: `python scripts/validate-ariadne.py <file>`
- RX: `python scripts/validate-rx.py <output_dir> <rx_basename>`
- TREE: `python scripts/validate-tree.py <file>`

1ファイルごとに、構造・表示・本文役割の抜けを止める。

## 4. 横断検査

```powershell
python scripts/check-lexia-book-quality.py outputs/ux/000_TX outputs/001_JX outputs/ux/001_ARIADNE outputs/ux/002_RX outputs/ux/003_TREE
```

TXLEX と ARIADNE をまとめて検査する。特定範囲だけ見る場合は、対象ファイルを並べて実行する。

## 完了条件

生成・更新したファイルは、少なくとも次を満たすまで完了扱いにしない。

- 対象ファイルの単体検査が ERROR 0。
- 対象ファイルを含めた横断検査が ERROR 0。
- 最新法令・判例・主要学説レビューが完了。
- 表示確認で、ラベルと本文の距離、条文欄、論点処理マトリクス、ANSWER、解法ナビの回答ボタン、ヒント、記憶フック、模範答案、RXカード、TREE枝が崩れていない。
- 論点処理マトリクスが条文・判例の下、5点セットの上にあり、各肢の処理順と判断式を図解している。
- 記憶フックが長い解説文・判例名の羅列・要件と結論の連結文ではなく、15〜45字程度の記憶標語になっている。
