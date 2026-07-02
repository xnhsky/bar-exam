# TXLEX v12.2.2 一括最新化プロジェクト（ハンドオフ／レシピ）

> 既存 TXLEX（`outputs/ux/000_TX/**/*_lex.html`）を **v12.2.2 最新**へ更新し続けるための単一ソース。
> ローカル・リモート（Claude Code on the web）どちらのセッションでもこの文書を読めば継続できる。
> 記憶(memory)はマシン固有で共有されないので、**判断はこの文書と gold 見本・ゲートに従う**こと。

## 0. 現状（2026-07-02 時点）

- **最新 v12.2.2 = 11 件（刑TX360-370）**。gold 見本＝360（体系マップ/穴埋め無し型の基準）・361（体系マップ genuine 見本）・366（各肢マトリクス genuine の別解）。
- **未更新 = 351 件**。2 層に分けて進める（§1）。
- 正典 `canonical/GENESIS-CORE.html` は override2＋SVGテーマ統一＋`.blank-num` を吸収済み。ゲート（G45 体系マップ許容/逐語コピー禁止/ASCII条番号、`check-tx-reuse.py`）導入済み。master 最新は `b21fd4d4` 系。

## 1. スコープ（優先順）

| 層 | 件数 | 内容 | 対応 |
|---|---|---|---|
| A. v12インライン未更新 | 20（**刑TX355-359・371-385**） | インライン構造・内容（ANSWER/条文/フロー/記憶フック/詳説）は完備。体系マップ・重厚CSS・SVGテーマ統一・（旧）解法ナビが未対応 | §3 レシピで更新。**まずここ** |
| B. v11以前（旧 _lex） | 331 | `<article class="tx-inline-card">` が無い旧形式 | v11→v12インライン変換（大規模・別計画） |

判定：`grep -c '<article class="tx-inline-card"'` があれば v12インライン。`tx-sysmap` かつ `重厚感 override 2` かつ `SVGノードをテーマ色` があれば最新。

## 2. エフォート/モデル振り分け（守る）

- **執筆（体系マップ・解法ナビの中身・内容レビュー）＝ Opus / effort MAX**（サブエージェント）。1回の MAX エージェントで**体系マップ HTML と解法ナビ STMT を同時に執筆**させると効率的。
- **機械処理（CSS注入・マトリクス除去・ASCII・probe・伝播）＝ 決定論スクリプト**（モデル不要）。
- **検証・描画 = 低**。**段取り = 適正(medium)**。
- 大規模は **Workflow で「執筆＝MAX ∥ 検証＝low」を並列**（起動に opt-in の一言）。難問（論点構造が割れる/判例に争い）だけ ultra（独立ドラフト＋判定パネル）に自動エスカレーション。

## 3. 1問あたりレシピ（層A）

0. **診断**：`python -X utf8 scripts/validate-tx-core.py <file>`。KEY（`data-answer-key`）で記述idがカタカナ(ア〜オ)か数字(1〜5)かを判別。条番号チップが漢数字なら要ASCII化。マトリクスがあれば rehash（5点フロー逐語コピー）か確認。
1. **体系マップ .tx-sysmap 執筆（MAX）**：その問題の実際の論点構造から genuine に。**他問の丸写し禁止**（`check-tx-reuse.py` が完全一致=ERROR）。骨格・class は 360/361 と同一、section1＝客体三分等・section2＝本問の論点を各記述に対応、probe は `#stmt-N`（idに合わせカタカナ/数字）、×/○結論は書かず論点・規範のみ。判例は短縮形（最判昭32.6.21 等）、条番号ASCII。
2. **解法ナビ更新（G44 が出る場合）**：旧 solve-nav を現行エンジン（`canonical/SOLVE-NAV.html` ＝ 360-370 の2本目 `<script>` と同一）へ差し替え、`STMT={"1":{q,tip,note,hint},…}`＋`ORDER`＋`MODE`（correct/incorrect）を執筆。tip/note/hint は**問題固有**（汎用は `check-lexia-book-quality` の TX-HINT で弾かれる）。360の STMT を形式見本にする。
3. **機械組込**（360から抽出したブロックを流用）：
   - `</style>` 直前に **体系マップ基盤CSS(block A：`/* === TX360 体系マップ:` 〜 次の override コメント直前)** ＋ **`重厚感 override 2`** ＋ **`SVGノードをテーマ色(accent)統一`** の3ブロックを注入。穴埋め問は `.blank-num`（canonical から）も。
   - マトリクスがあれば除去：`re.sub(r'<div class="tx-logic-matrix".*?tx-matrix-verdict.*?</p></div>\s*','',h,flags=re.S)`。
   - 漢数字条番号→ASCII：`<span class="tx-mini-law-article">第百十二条</span>`→`112条` 等（span丸ごと置換・本文の条文原文は漢数字のまま）。
   - 体系マップ挿入：`<div ...class="tx-inline-judge-list">` か `tx-inline-list` 容器の直前、無ければ最初の `<article class="tx-inline-card"` 直前。
   - 各解説末尾に戻りリンク：`<details class="tx-inline-detail">…</details>` の直後へ `<div class="tx-sysmap-back"><a href="#tx-sysmap">↑ 体系マップに戻る</a></div>`。
   - ファイル書込は `io.open(...,newline='')`（改行保全）。
4. **内容レビュー（MAX・敵対的）**：条文番号・判例・正誤・体系ツリー/解法ナビが問題内容と一致するか反証的に照合。フラグが立てば ultra へ。
5. **検証（全PASS必須）**：`validate-tx-core.py`(0 err)／`check-lexia-book-quality.py`／`check-tx-lex-engine.py`（接ぎ木）／`check-tx-reuse.py <file> outputs/ux/000_TX/001_刑法/刑TX36{0,1,6}_lex.html …`（既最新と横断・完全一致0）。可能なら Playwright で reveal 動作・0コンソールエラー確認（**リモートはブラウザ非搭載のことがあり描画は省略可＝検証器と使い回し検査を必須ゲートに**）。

## 4. 制約（重要）

- **ARIADNE 系ファイル（`canonical/ARIADNE*`, `outputs/ux/001_ARIADNE/*`, `scripts/validate-ariadne.py`, `scripts/ariadne-*`, `docs/ariadne-*` 等）には触れない**。別プロセスが並行作業中。**commit は自分の対象ファイルのみ明示 `git add <paths>`**（`-A`/`-a` 禁止）。
- **本線 master 一本**。作業前に `git fetch && git rev-parse origin/master`。push は fast-forward を確認。二台/リモート並行時は**番号帯を分ける**（例：ローカル 355-359／リモート 371-385）。他方が push したら pull。
- 1問（または数問）ずつ commit。ARIADNE を巻き込まない。
- 検証器・正典は原則いじらない（レシピは既存ゲートを通すだけ）。

## 5. 進め方

1. 層A の 20 問を §3 レシピで更新（推奨：Workflow 並列 or 番号帯分割で二台）。
2. 完了後、層B（v11 331件）の v11→v12 変換を別計画で。
3. 疑問が出たら 360/361/366 の実物と本文書・ゲートを基準に判断（記憶に依存しない）。
