# Copy-Paste Prompt For Claude: ARIADNE v1.2.0 PLACEHOLDER-LOCK

```text
C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam-codex で作業してください。

これは ARIADNE 正典化分だけの引継ぎです。TX v12 / GENESIS / TX360 は別引継ぎで扱うので、このプロンプトでは触らないでください。

まず読むもの:
1. docs/HANDOFF-ARIADNE-v1.2.0-PLACEHOLDER-LOCK.md
2. spec/jx-ariadne-v1.2.0-core.md
3. canonical/ARIADNE.html
4. canonical/ARIADNE.placeholder.html
5. prompts/new-ariadne-headless.md
6. scripts/validate-ariadne.py
7. scripts/check-ariadne-canonical.py

現行 ARIADNE 正典:
- ARIADNE v1.2.0 PLACEHOLDER-LOCK
- active canonical: canonical/ARIADNE.html
- active slot contract: canonical/ARIADNE.placeholder.html
- active spec: spec/jx-ariadne-v1.2.0-core.md
- generator prompt: prompts/new-ariadne-headless.md
- validator: scripts/validate-ariadne.py A1-A31

目的:
今後の ARIADNE 生成・改修は、Claude 正典の模範答案を維持したまま、JX019 型のマトリクス答案構成を正典として使う。JX から答案構成、想起、RX 論証カード、TREE 樹形図へ自然に回れる学習導線を維持・強化する。

絶対ルール:
- v1.2.0 は PLACEHOLDER-LOCK。`canonical/ARIADNE.html` のHTML/CSS/JS・class・section順・余白・字下げ・機能色・パズルエンジンは固定。
- `canonical/ARIADNE.placeholder.html` の `{{{...}}}` スロット契約を読み、問題ごとに変わる本文・論点・事実・答案・深掘り・属性だけを置換する。
- AIがデザイン判断してよいのは、既存ACTIVEベースカラーの **EASY / STD / HARD** を問題難易度で1つ選ぶことだけ。新色創作、Mildliner機能色変更、レイアウト変更は禁止。
- 模範答案は従来の Claude 正典どおり。問規当結カード、明朝、字下げ、事実/評価語マーカーを維持する。
- 19で一度出た A/B答案分岐方針は撤回済み。採用しない。
- 答案構成は `.bone.matrix-bone` のマトリクス型で作る。
- `.bsec`, `.mrow`, `.bn`, `.mcell`, `.mline`, `.mstage`, `.mtext` を使い、チップ配置で訓練できる構造にする。
- 論点チップは `【論点】...` とし、`【論点①】` や `【論点1】` のような冠番号を付けない。
- RX `data-rx` は、対応論点が明確な想起カードだけに付ける。RXファイルが存在するだけで無理に紐づけない。
- 同じJX内で `data-rx` が重複する場合は、教育上同じ論証を2回聞く意図が明確なときだけ許す。
- TREE は論点構造理解用、RX は答案で吐き出す論証用、ARIADNE は周回導線用。役割を混同しない。
- 教授のひとこと・答案構成の作法・TTS内容は対応させる。TTSと矛盾する汎用助言を足さない。

体裁ルール:
- バッジ、ラベル、見出しは字下げしない。
- それ以外の本文は本文カラム側で字下げする。
- ラベル横へ長文を直置きして本文がぶら下がる形は禁止。
- CASE / 問題文 / draft-problem / draft-digest / facts / bc-inst / matrix outline は、ラベル列＋本文列の2カラムを基本にする。
- `.problem .pq` は `text-indent:1em` を維持する。
- `.facts li` の2カラム正典は以下:
  `grid-template-columns:minmax(18em,32em) minmax(16em,28em); column-gap:18px; justify-content:start`
- 下書き構造は固定: 人物関係図と時系列を上段2カラム、拾う文言を下段の全幅 `.draft-card span2` に置く。人物関係図を `span2` にしない。
- `.cue` の先頭に `...` / `…` を置かない。これは本文ではなく、過去生成で漏れた区切り記号なので禁止。
- 旧ワイド2カラムは禁止:
  `grid-template-columns:minmax(24em,1.35fr) minmax(18em,1fr); column-gap:24px`
- 骨子の `.mline + .mline` と拾う文言の項目間には点線区切りを入れる。
- ラベル色は正典のマイルドライナー系を使う。難易度に応じた既存 ACTIVE ベースカラー（EASY/STD/HARD）の選択だけAI判断可。機能色や新色の創作は禁止。

恒久対策:
- validate-ariadne.py A29: `data-rx` の科目/JX整合と参照先RX実在を確認。
- validate-ariadne.py A30: `.problem .pq` の `text-indent:0` 退行を ERROR。
- validate-ariadne.py A31: `.facts li` の旧ワイド2カラム・非正典2カラム、人物関係図/拾う文言の全幅配置ミス、`.cue` 先頭の `...` / `…` を ERROR。
- check-ariadne-canonical.py は canonical、slot contract、全 ARIADNE 出力を横断検証する。
- check-lexia-preflight.py は ARIADNE canonical guard と RX coverage を含む。
- jx-finalize.ps1 / jx-push.sh は commit/push 前に ARIADNE 正典ガードを通す。

JX生成時の副産物動線:
- jx-batch-runner.ps1 は JX validate PASS 後に RX / TREE / ARIADNE を生成し、その後 TTS を生成する。
- 欠落があれば rx-arb-backfill.ps1 で RX / TREE / ARIADNE を後追い補完する。
- jx-finalize.ps1 は JX本体 + TTS + RX + TREE + ARIADNE を同じコミットに載せる。
- jx-push.sh は remote回収時にも outputs/ux を含め、preflight を通してから commit/push する。

作業前に確認:
git status --short --branch

ARIADNE単体検証:
python scripts/validate-ariadne.py outputs/ux/001_ARIADNE/001_刑法/刑JXNNN_ARIADNE.html

ARIADNE全体検証:
python scripts/check-ariadne-canonical.py

RX coverage:
python scripts/check-rx-coverage.py --summary --strict

Lexia preflight:
python scripts/check-lexia-preflight.py --skip-self-test

対象JXのRX/TREE検証:
python scripts/validate-rx.py outputs/ux/002_RX/001_刑法/刑JXNNN 刑RXNNN
python scripts/validate-tree.py outputs/ux/003_TREE/001_刑法/刑JXNNN_TREE.html

期待される現状:
- check-ariadne-canonical.py: FAIL 0
- check-lexia-preflight.py --skip-self-test: PASS
- check-rx-coverage.py --summary --strict: dangling 0 / UNREACHABLE 0
- SAFETY-NET は残ってよい。Lexiaの遅延注入で回収される実害小扱い。

作業範囲:
- ARIADNE生成・改修・検証に必要な範囲だけ触る。
- TX v12 / GENESIS / TX360 / TX validator は別作業なので触らない。
- 変更したら対象範囲だけ commit/push する。
```
