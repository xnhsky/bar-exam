# /new-ariadne — 検証済み JX から ARIADNE 解法ナビを生成

**用途**：既存の検証済み JX（ATHENA）から、初学者向けの「解法ナビ＋周回」教材 ARIADNE を1問生成する。
ATHENA（百科事典）はそのまま。ARIADNE は別系統の副産物（RX/TREE と同じく検証済み JX から蒸留）。

## 使い方
```
/new-ariadne 刑 001          # 科目＋番号
/new-ariadne outputs/001_JX/001_刑法/刑JX001.html   # JX HTML パス直指定
```

## 正典・依存
- 骨子 spec：`spec/jx-ariadne-v0.1-core.md`
- 複製起点（スケルトン）：`canonical/ARIADNE.html`（v0.3 誌面風）
- 生成プロンプト：`prompts/new-ariadne-headless.md`
- 検証：`python scripts/validate-ariadne.py <出力>`（A1〜A21）

## 工程（要約）
1. `outputs/001_JX/{科目}JX/{科目}JX{NNN}.html`（ATHENA）を一次情報源に Read。事案と論点の自己照合（不一致は中断）。
2. `canonical/ARIADNE.html` を `outputs/ux/000_ARIADNE/{00N_科目}/{科目}JX{NNN}_ARIADNE.html` へ複製→空化→鋳造。
3. 解法7ステップ（SCAN→BUILD）＋骨子＋自己採点＋模範reveal＋深掘り＋**自己完結○× 10〜15枚**（`data-arena="1"`＋`data-correct-value`）。
   **深掘り層はアテナ級（spec §11）**：論点・条文・判例・学説・用語を **刑TX328 の本物の型（basis-card）に流し込む**
   （`.basis-card.statute-card/.case-card/.doctrine-card/.term-card`＋`basis-card-header`／`basis-card-body`・kd-label役割色・
   freq-badge ゴールド・判旨ティールバッジ・フォント/文字色も TX328 同値）。末尾に**「アテナで詳しく」ボタン**
   （`.go-athena data-athena-code="{元問題ID}"`＝postMessage `lexia:navigate` で本物のアテナ版へジャンプ）。
   後追いは `scripts/ariadne-graft-athena-deep.py`（移植）／`ariadne-athena-deep-backfill.py`（ジャンプ＋CSS）。
4. `validate-ariadne.py` で A1〜A21 ERROR 0 を確認。
5. **master に commit/push**（Lexia は `barExamSync.js` で outputs/ を自動スキャン＝push で自動同期）。

## 規律
- **答案構成パズル（spec §9・周回の主役）**：エンジンは canonical 継承。生成時に骨子へ
  規範 `.krule`／あてはめ `.kfact` タグ、`.bone` に `data-kp-decoys`、骨子直前に試験下書き `.drafting`、
  ○× の3枚前後を想起カード（`.recall`/`data-recall`）へ格上げ。下書きは「生の事実抽出」までに留める。
  **下書き先頭は `.draft-problem`＝問題文原文の再掲（`.problem .pq` 逐語）＋直下に `.draft-digest`＝骨子用圧縮メモ**
  （答案構成で上へ遡らず済むよう原文を必ず再掲。原文＋圧縮の二段）。
- **模範答案の問規当結カード（spec §10）**：`.model-answer` の各段落 `<p>` に役割クラスを付与＝問題提起 `role r-issue`／規範 `role r-norm`（説名 `<b class="rule">`）／あてはめ `role r-apply`／結論 `role r-concl`（`.ma-h` には付けない）。あてはめは 事実 `<span class="fact">`／評価語 `<span class="eval">` を括る。CSS は canonical 継承（マイルドライナー5系統・食い出しバッジ・一行点線）。
- 法的正確性は検証済み JX に厳密準拠（規範すり替え・条文誤り・判例射程の誤用禁止）。
- ○× は**本問前提なしで解ける一般原則／例題**（復習プール孤立表示でも解ける）。メタ除去regex・`</body>`リテラルを避ける。
- **教示↔ドリル 非重複（spec §4-bis・最重要）**：各手のドリルは直上の教示（`.do`/`.peek`）の言い換えにしない。教示＝本問の手続ナビ／ドリル＝転用可能な規範・定義・区別・要件の能動想起、と的を分ける。「教示を隠さず読んでもドリルが解けてしまわないか」を各手で自己点検し、被るなら一段深い転用知識へ振り替える（根拠はファイル内に限る）。
- 配色・フォントは TX v11（V3 Twilight Violet・刑TX327）見本＝canonical 継承（spec §5）。役割別フォント（Shippori Mincho B1／Zen Kaku Gothic Antique／Zen Maru Gothic／Source Code Pro）・字下げ・バッジ＋色分けボックス。
- **★ ベースカラーは難易度別に染色選定**：`:root` の「▼ ACTIVE」プリセットを **EASY=ローズ(P1)／STD=クリスタルブルー(P2)／HARD=バイオレット(P3)** から問題の難易度で1つ選び、ラベル＋値2行を差し替える（カタログ3案は `:root` コメント常時記載）。基礎・典型→EASY／中堅・頻出→STD／重論点・罠多・錯誤や不作為等の難所→HARD。○×ボタンはコンパクト固定（横幅いっぱいにしない）。
