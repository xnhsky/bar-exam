# scripts/

## .ps1 ファイル保存規律

- すべての .ps1 ファイルは **BOM 付き UTF-8 (utf-8-sig)** で保存する
- 理由：Windows PowerShell 5.1 系は BOM 無し UTF-8 を cp932 として誤読する
- PowerShell 7+ は BOM 無し UTF-8 も正常に扱うが、互換性のため統一する
- 検証方法：`head -c 3 <file> | xxd` で `efbbbf` を確認
- night-batch-runner.ps1 など本番ファイル新規作成時も必ず BOM 付きで保存すること

## マルチ PC 対応

- `night-batch-runner.ps1` の `$ProjectRoot` は `$PSScriptRoot` から自動算出する
  （`Split-Path -Parent $PSScriptRoot` で scripts\ の親 = プロジェクトルート）
- これにより OWNER PC (`C:\Users\OWNER\bar-exam`) と
  xnrg2 PC (`C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam`) のどちらでも
  同じスクリプトがそのまま動作する
- 新しい PC で運用開始する際は `git pull origin master` のみで同期可能
  （パスのハードコード書き換えは不要）
- 新規 .ps1 を追加する場合も同様に `$PSScriptRoot` 経由で
  プロジェクトルートを解決すること（絶対パスをハードコードしない）

## PDF 運用ルール

### 生成済み PDF の扱い
- 生成済み HTML が存在する PDF (outputs/000_TX/{科目}TX/{科目}TX{番号}.html 存在) は
  inputs/000_TX/001_刑法/ から削除可能（容量節約）
- 削除は git で正式に削除し、両 PC で同期する
- HTML は永続保持（生成済みコンテンツが本体）

### PDF 補充のタイミング
- inputs/000_TX/001_刑法/ の未生成 PDF が 5 件以下になったら補充推奨
- 補充単位: 15-30 件（1-2 週間分のバッファ）
- 補充元: 各 PC で手動配置 → git で同期

## night-batch-runner の自動クリーンアップ

以下の全条件を満たす場合、batch 完走後に PDF を自動削除：
- HTML が生成されている (htmlBytes > 0)
- claude -p の exit code が 0
- sentinel が FAILED でない
- validate-tx.py で "ERROR 0" を確認

上記いずれかが満たされない場合は PDF を残す（再試行 or 手動レビュー用）。

この設計により「PDF 存在 = 未生成」「PDF 不在 = 生成済み」という
物理状態ベースの判定が成立し、HTML を別フォルダに移動した後でも
重複生成を防げる。

cost-summary.csv には `cleanup` (True/False) と `validate_status`
(PASS / ERROR_detected / exec_failed / skipped_failed_generation) の
2 カラムが追加されており、各問の判定結果を後追い確認できる。

## Lexia 同期前一括ゲート: check-lexia-preflight.py

Lexia へ同期する前に、`outputs/` と `references/` を read-only で一括監査する入口。
個別ゲートの呼び忘れや実行順の揺れを防ぐため、以下を同じ順序で実行する。

0. `test-lexia-sync-contract.py`
1. `check-duplicates.py outputs references`
2. `check-lexia-sync-contract.py --summary outputs references`
3. `check-ariadne-canonical.py`
4. `check-rx-coverage.py --summary --strict`

使い方:

```
python scripts/check-lexia-preflight.py
python scripts/check-lexia-preflight.py --keep-going
python scripts/check-lexia-preflight.py --skip-self-test
python scripts/check-lexia-preflight.py --json deploy/lexia-sync-audit.json
```

同期契約チェッカ自体の軽量 self-test:

```
python scripts/test-lexia-sync-contract.py
```

終了コード:

- **exit 1**: いずれかのゲートで ERROR / dangling / UNREACHABLE（strict）がある。
- **exit 0**: Lexia 同期前の機械ゲートを通過。

## 配布前ゲート: check-duplicates.py（ファイル間の重複・ID 不整合）

`validate-tx.py` / `validate-jx.py` は **1 ファイル内** の検証専用で、
「別ファイル同士」の問題は拾えない。これを補うのが `check-duplicates.py`。

検出ルール（いずれかで exit 1）:

- **D80 ID-MISMATCH** … `<title>` / `.doc-header` / `.footer-problem` の問題コードが
  ファイル名と不一致（例: 刑TX338/358/123 の `<title>` や 刑TX055 の footer が
  「刑TX311」のまま＝**他問からのコピペ残り**）。0 埋め差(JX1/JX001)は数値比較で吸収。
  ※ `validate-jx.py` は footer/header の ID を見ないため、JX/RX もこの D80 がカバーする。
- **D81 DUP-TITLE** … 2 件以上が同一 `<title>`（別問題が同一タイトル＝Lexia 取込時に
  重複誤検出される元凶）。
- **D82 DUP-BODY** … 2 件以上が本文バイト完全一致（同一問題を別名で重複保存）。

使い方:

```
python scripts/check-duplicates.py                # 既定で outputs/ を走査
python scripts/check-duplicates.py outputs deploy # 各ルートを独立に検査（ミラー間一致は無視）
```

### 自動ゲート化

- `night-batch-runner.ps1` … バッチ完走後に `outputs/000_TX` を横断監査。検出時 exit 1。
- `jx-finalize.ps1` … git commit/push の**前**に `outputs` を検査。検出時は commit せず中止
  （緊急回避は `-NoGate`）。これにより **Lexia の取り込み元である git に不整合な HTML を入れない**。

### 運用ルール（重要）

既存 HTML を**コピーして別番号の問題を作らない**こと。コピー編集は `<title>` /
doc-header / footer の ID 書き換え漏れ（D80）や本文重複（D82）の温床になる。
新規問題は必ず生成パイプライン（`night-batch-runner.ps1` / `jx-batch-runner.ps1`）で
PDF・逐語から生成する。万一コピー作成しても、上記ゲートが push 前に検出する。

## Lexia 同期契約ゲート: check-lexia-sync-contract.py

`check-duplicates.py` は title/header/footer と重複の横断検査に特化している。
`check-lexia-sync-contract.py` はその次の層として、Lexia が取り込む HTML の
**同期メタ契約**を `outputs/` と `references/` から read-only で監査する。

主な検出対象:

- **分類不能パス/命名** … `outputs/000_TX` / `001_JX` / `ux/000_TX` / `ux/001_ARIADNE`
  / `ux/002_RX` / `ux/003_TREE` / `ux/004_参考資料` / `references` の既知規約に乗らない HTML。
- **fileName / code / title / subject / category の揺れ** … ファイル名由来の `code`・
  `baseCode` と `<title>`・科目ディレクトリの不一致、`category+code` や `fileName` の重複。
- **生成 HTML の対応欠落** … 公式 TX と `_lex` の片割れ、JX 本体に対応する ARIADNE/TREE/RX、
  または副産物だけが残って JX 本体が無い状態。
- **sourcePath 相当** … repo 相対パスを `/` 区切りで安定化し、JSON 出力で確認可能。
- **作成日フッター** … `class="lexia-genmeta"` と `data-generated`、本文 `Generated:` の欠落・重複。
- **HTML 本文不足** … カテゴリ別の最低サイズ/テキスト量を下回るファイル。
- **ARIADNE→RX** … `data-athena-code` と `data-rx` の形式・参照先 RX 実在。
  `scripts/ariadne-backfill-rx-link.py` の `MAP` で `None` と明示された想起カードは、
  総論/汎用カードまたは対応 RX 無しとして意図的省略扱いにする。MAP に無い省略や MAP 長不一致は WARN。
  真の到達不能は
  `check-rx-coverage.py --strict` が判定する。

使い方:

```
python scripts/check-lexia-sync-contract.py
python scripts/check-lexia-sync-contract.py --summary
python scripts/check-lexia-sync-contract.py --strict
python scripts/check-lexia-sync-contract.py --json deploy/lexia-sync-audit.json
```

終了コード:

- **exit 1**: ERROR あり。`--strict` では WARNING でも exit 1。
- **exit 0**: ERROR なし。WARNING は配布可だが後追い整備候補。

`check-lexia-preflight.py` と `jx-finalize.ps1` は commit/push 前に
`check-duplicates.py` → `check-lexia-sync-contract.py --summary`
→ `check-ariadne-canonical.py`
→ `check-rx-coverage.py --strict` の順で実行する。これにより、Lexia 同期で
「HTML本文不足」「ID不一致」「作成日欠落により更新が毎回出る」原因を git へ入れる前に止める。

## ARIADNE 正典ガード: check-ariadne-canonical.py

ARIADNE v1.2.0 PLACEHOLDER-LOCK（`canonical/ARIADNE.html`＋`canonical/ARIADNE.placeholder.html`＋`spec/jx-ariadne-v1.2.0-core.md`）を
横断検証する read-only ゲート。`validate-ariadne.py` を canonical と
`outputs/ux/001_ARIADNE/**/*_ARIADNE.html` に適用し、ERROR があれば exit 1。

主な恒久対策:

- A30: 問題文 `.problem .pq` の本文1字下げ。`text-indent:0` への退行を ERROR。
- A31: 拾う文言 `.facts li` の近接2カラム、人物関係図/拾う文言カードの固定配置、`.cue` 先頭の不要な `...` / `…`。旧ワイド2カラムや非正典配置を ERROR。
- A32: 照合カード `.collate`、模範答案 `details.reveal-answer`、深掘り `details#deep-dive` を骨子コンテナ `.skeleton` 内に固定。背景上の外置き・旧幅調整CSSを ERROR。
- A29: 想起カード `data-rx` の科目/JX整合と参照先RX実在。
- slot contract: `canonical/ARIADNE.placeholder.html` の v1.2.0 marker と `{{{...}}}` スロット存在。

使い方:

```
python scripts/check-ariadne-canonical.py
python scripts/check-ariadne-canonical.py --verbose
python scripts/check-ariadne-canonical.py outputs/ux/001_ARIADNE/001_刑法/刑JX00[7-9]_ARIADNE.html --no-canonical
```

## TX _lex 要点化 整備: tx-lex-gist-backfill.py（全7科目・後追い掃き取り）

TX `_lex` の選択肢を「移動中に高速で解ける」形（**要点一行＋全文折りたたみ**）にする
規律（2026-06-25 ユーザー指示・正典 `spec/tx-v11.1.0-twotrack.md` 第4項／gold=刑TX351）を、
**新規生成だけでなく既存 `_lex` にも横展開**するための後追い器。全7科目を走査する。

- **機械でできる部分**＝ox-gist CSS（`canonical/SOLVE-NAV.html` [STYLE] と同一塊）の冪等注入。
- **人手（モデル）が要る部分**＝各選択肢の「要点」執筆は worklist に出すだけ（自動執筆しない）。
- `.ox-stmt` 本文（Lexia 記録・G30/G31 対象）は触らない。mc/空欄補充型（`ox-core-wrap` 内）は
  解答前ネタバレになるため要点折りたたみの対象外＝worklist からも除外。

```
python scripts/tx-lex-gist-backfill.py                 # 全科目 dry-run 集計（書込みなし）
python scripts/tx-lex-gist-backfill.py --subject 007_憲法
python scripts/tx-lex-gist-backfill.py --inject-css    # 要点対象ファイルへ CSS 注入（書込み）
python scripts/tx-lex-gist-backfill.py --worklist wl.md  # 要点執筆が必要な問の一覧を出力
```

運用：他科目の TX を生成したら本ツールで worklist を出し、gold(刑TX351) に倣って
1問1エージェント（または `/new-tx` と同じ規律）で要点＋💡コツ一行を執筆→`validate-tx-core.py`
Errors:0→commit。**新規生成は正典 `SOLVE-NAV.html`／`new-tx.md` が最初からこの形を出す**ので、
本ツールは主に「正典更新前に作った既存問」の取りこぼし回収用。刑法 362 問は展開済み（todo 0）。

## 議論形式の作り直し: tx-classify-format.py ＋ tx-build-typeA.py（Type A・解法ナビ主役）

議論形式・空欄補充の組合せ問題は、最終番号が**各空欄の小判断（論点）の集計**にすぎないため、
「組合せ○×」をやめ **解法ナビ主役・空欄単位記録** へ作り直す（2026-06-25 ユーザー指示・gold＝刑TX351）。

- **`tx-classify-format.py`** … _lex を Type A（議論・空欄補充）/ B-combo（記述組合せ）/ B-single（独立5択）へ
  機械分類（解答選択肢のトークン構成で判定）。`--map out.md`／`--list-a`。刑法は Type A 22 問。
- **`tx-build-typeA.py <CODE> <DATA.json>`** … 刑TX351 で実証した「解法ナビ（アンカー順・空欄2択）＋
  空欄単位 ox-grid（`ox-core-wrap` でネタバレ防止・`data-oxgrid-mode="blank"`）」へ変換。**エンジン JS は固定**、
  問題固有データ（order / win / 各空欄 loc・frag・q・tip・opts・ans・core）だけ JSON で差し替え（空欄⑮まで）。
  **物語解説（`narrative`）・出題趣旨（`intent`）も DATA.json に持てば `.final-answer` 冒頭に同梱**。
  作り直し手順：分類器で Type A を抽出 → 各問 1 エージェントで会話を読み JSON 執筆 → builder 適用 →
  `validate-tx-core` Errors:0 → commit。Type B は要点化（上記 `tx-lex-gist-backfill.py`）のまま。

## 物語解説（読み物）: tx-inject-narrative.py ＋ tx-extract-source.py（全 TX _lex 標準・初学者向け）

基本書を読まない学習者の「本当にわからない時に読む救済テキスト」として、TX `_lex` の `.final-answer` 冒頭に
**初学者向けの物語解説（一連の読み物）**を入れる（2026-06-26 ユーザー指示・全 TX `_lex` の必須要素・gold＝刑TX311/刑TX351）。
公式 `000_TX` には入れない。`new-tx` Phase 4i で標準搭載。

- **`tx-inject-narrative.py <CODE> <narrative.json>`** … 標準 _lex（Type B＝独立5択・記述組合せ）の `.final-answer`
  冒頭に `.fa-narrative`（＋任意で `.fa-intent`）を**冪等注入**する汎用器。`narrative.json={"title":..,"paras":[..],"intent":{..}?}`。
  既存ブロックは除去してから挿し直す。CSS は GENESIS-CORE 同梱だが無ければ自動注入。Type A は `tx-build-typeA.py` が内蔵。
- **`tx-extract-source.py <CODE>`** … _lex から執筆に要る情報だけ compact 抽出（TITLE／問題の核心 data-explanation／
  各記述 ox-stmt＋正誤＋論点コア／PART A 問題文要旨）。250KB 全読を避けエージェントが数 KB で済む。
- 執筆要件：**初学者レベル**（鍵概念を初出で噛み砕く）／**記号フリー**（①〜・(a)〜・A説/甲乙説・記述記号への言及禁止）／
  **問題の論理に沿って一本に**（核心→各記述の正誤理由→まとめ・幹）／**物語性が薄い寄せ集めは偽の物語を捏造せず共通概念で束ねる**
  （例：過失の下位類型＝「この論点に引かれた複数の境界線」）。6〜9段落・重要語 `<b>`。
  ただし `<b>` は色で目を止める用途に留め、`.fa-narrative b` は `font-weight:560` 以下。iPhone で潰れる600超・700系へ戻さない（validate-tx-core.py G35）。
- 一括展開：分類器で Type A を除いた _lex を抽出 → 1問1エージェント（ワークフロー）で `tx-extract-source` 読込→執筆→
  `tx-inject-narrative`→`validate-tx-core` Errors:0。刑法 362問は展開済み（Type A 22＋Type B 340）。

## TX360 インライン周回正典と Lexia/SM2 解説ペイロード

2026-06-29 以後の TX `_lex` は、`刑TX360_lex.html` を gold として、問題文各肢に OX と逐条解説を対応させる
`.tx-inline-card` を主導線にする。CSS/JS は `canonical/GENESIS-CORE.html` の `tx-inline-*`（TX v12.1.1 inline canon）が正典。

- 裏の `.answer-ox-grid` は Lexia/SM2 記録・answer-key・検証の単一情報源なので削除しない。
- `.tx-inline-browse-btn`（解説だけ閲覧）は `answered` を付けず、SM2 記録を発生させない。
- `.tx-inline-detail` は対応 PART B をその場に展開するトグル。通常周回はインライン面で完結し、PART B は詳説アーカイブ扱い。
- 記号問題・組合せ・見解A/B・事例Ⅰ/Ⅱなどの問題都合ラベルは、SM2 に残さず論点コア・テーゼへ置換する。
- SM2 に渡す解説は `.ox-stmt` → `.tx-reflex-core` → `.tx-cycle-aids` → メイン条文本文 → 詳説の順。`fa-narrative` は初回理解用で、通常カード本文には載せない。
- 既存 Lexia は `.ox-row` 直下の `.ox-pool-explain` を GIST/POINT の最優先ソースとして読むため、TX360 inline 型では `scripts/tx-sm2-payload-backfill.py` で `.tx-reflex-core`＋`.tx-cycle-aids` を `.ox-pool-explain` にミラーする。`validate-tx-core.py` G34 が欠落・narrative/詳説混入・問題都合ラベル残留を止める。

```
python scripts/tx-sm2-payload-backfill.py outputs/ux/000_TX/001_刑法/刑TX360_lex.html
python scripts/validate-tx-core.py outputs/ux/000_TX/001_刑法/刑TX360_lex.html
```

## カバレッジゲート: check-rx-coverage.py（RX 論証カードの復習プール到達性）

Lexia は ARIADNE 想起カードの `data-rx` を辿って RX 論証カードを復習プールへ注入する
（`ariadne-backfill-rx-link.py` が `data-recall` タグに `data-rx="{科目}RX{NNN}_{序号}"` を刻む）。
1 問の RX 枚数 > `data-rx` 参照数 のとき、どの想起にも直接紐づかない RX（孤児）が生じる。
`check-rx-coverage.py` は各 `outputs/ux/002_RX/{科目}/{科目JX}/` の **rx_present**（ファイル名コード集合）と、
対応 `001_ARIADNE/.../{科目JX}_ARIADNE.html` の **rx_referenced**（`data-rx` 値集合）を JX 別に突き合わせる。

**Lexia 安全網を織り込んだ層別**（Lexia `src/App.jsx` の `supplementJxRx`・3562-3571 行を機械反映）：

- **SAFETY-NET** … 孤児だが、その JX に `data-rx` 起点が 1 つでも在れば、想起失敗時に
  `supplementJxRx` が同 JX の RX を `_1.._8` 手繰りで一括補充する＝遅延注入で回収される（実害小・WARN）。
- **UNREACHABLE** … 真の取りこぼし。(A) その JX の ARIADNE に `data-rx` が**皆無**（起点なし→発火せず）、
  または (B) RX 連番が手繰り上限 `_8` を超える。当該 JX の ARIADNE を `data-rx` 起点付きで**再生成**すれば、
  起点 1 つで安全網が `_1.._8` を回収する。
- **dangling** … `data-rx` が実在しない RX を参照（リンク切れ）＝ERROR。

検出ルール:

- **exit 1**：dangling あり（既定）。`--strict` 指定時は UNREACHABLE があっても exit 1。
- **exit 0**：dangling 無し（uncovered は WARN）。
- RX 未生成の科目（刑法以外＝RX フォルダが無い）は graceful skip。read-only・冪等。

使い方:

```
python scripts/check-rx-coverage.py            # 全科目（科目別・JX 別レポート＋総計）
python scripts/check-rx-coverage.py 刑          # 科目を絞る（ディレクトリ名の部分一致）
python scripts/check-rx-coverage.py --summary   # OK 行を省き ERROR/UNREACHABLE と集計のみ
python scripts/check-rx-coverage.py --strict    # UNREACHABLE を exit 1 ゲート化（CI 用）
```

実測（2026-06-28）: 刑法 JX 66 / RX present 214 / referenced 138 / ARIADNE 不在 2 問 →
**UNREACHABLE 0** / SAFETY-NET 76 / dangling 0。刑法以外 6 科目は RX 未生成のため graceful skip。
