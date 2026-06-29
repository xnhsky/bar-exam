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

0. `test-lexia-preflight.py` / `test-check-duplicates.py` / `test-validate-ariadne.py` /
   `test-validate-rx.py` / `test-validate-tree.py` / `test-generated-validators.py` /
   `test-generated-validators-manifest.py` /
   `test-ariadne-backfill-rx-link.py` / `test-lexia-sync-contract.py` / `test-lexia-manifest.py` /
   `test-lexia-manifest-diff.py` / `test-lexia-content-worklist.py` / `test-lexia-worklist.py` / `test-rx-coverage.py` /
   `test-rx-coverage-manifest.py` / `test-lexia-bundle.py` / `test-lexia-stability.py` /
   `test-lexia-change-summary.py` / `test-stamp-footer.py` / `test-stamp-created-date.py` /
   `test-restamp-english.py` / `test-stamp-staged.py`
1. `check-duplicates.py outputs references`
2. `check-lexia-sync-contract.py --summary outputs references`
3. 任意で `check-lexia-manifest.py`（`--json-format manifest` 指定時）
4. `check-rx-coverage.py --summary --strict`
5. 任意で `check-rx-coverage-manifest.py`（`--rx-json` 指定時）
6. 任意で `check-generated-validators.py outputs/ux`（`--generated-validators` 指定時）
7. 任意で `check-generated-validators-manifest.py`（`--generated-validator-json` 指定時）
8. 任意で `lexia-content-worklist.py`
9. 任意で `check-lexia-worklist.py`（worklist `--json-format manifest` 指定時）
10. 任意で `check-lexia-bundle.py`（標準 `--bundle-dir` 一式が揃う場合）

使い方:

```
python scripts/check-lexia-preflight.py
python scripts/check-lexia-preflight.py --keep-going
python scripts/check-lexia-preflight.py --list-steps --final --bundle-dir deploy/lexia-preflight
python scripts/check-lexia-preflight.py --skip-self-test
python scripts/check-lexia-preflight.py --final
python scripts/check-lexia-preflight.py --final --keep-going  # 残件をまとめて見る
python scripts/check-lexia-preflight.py --bundle-dir deploy/lexia-preflight
python scripts/check-lexia-preflight.py --final --bundle-dir deploy/lexia-preflight
python scripts/check-lexia-preflight.py --bundle-dir deploy/lexia-preflight --bundle-fail-on-not-ready
python scripts/check-lexia-preflight.py --final --stability-seconds 0  # 安定性観測を明示的に無効化
python scripts/check-lexia-preflight.py --stability-seconds 2 --stability-json deploy/lexia-file-stability.json
python scripts/check-lexia-bundle.py deploy/lexia-preflight --verify-current --write-index --verify-index
python scripts/check-lexia-preflight.py --json deploy/lexia-sync-audit.json
python scripts/check-lexia-preflight.py --json deploy/lexia-sync-manifest.json --json-format manifest
python scripts/check-lexia-preflight.py --bundle-dir deploy/new --compare-sync-manifest deploy/old/lexia-sync-manifest.json
python scripts/check-lexia-preflight.py --bundle-dir deploy/new --compare-sync-manifest deploy/old/lexia-sync-manifest.json --manifest-diff-fail-on-content-change
python scripts/compare-lexia-manifests.py deploy/old/lexia-sync-manifest.json deploy/new/lexia-sync-manifest.json
python scripts/compare-lexia-manifests.py deploy/old/lexia-sync-manifest.json deploy/new/lexia-sync-manifest.json --fail-on-content-change
python scripts/check-lexia-preflight.py --rx-json deploy/rx-coverage.json
python scripts/check-lexia-preflight.py --worklist-markdown deploy/lexia-content-worklist.md
python scripts/check-lexia-preflight.py --worklist-json deploy/lexia-content-worklist.json --worklist-json-format manifest
python scripts/check-lexia-preflight.py --worklist-prompts-dir deploy/lexia-content-prompts
python scripts/check-lexia-preflight.py --worklist-target 刑JX020 --worklist-prompts-dir deploy/lexia-content-prompts
python scripts/check-lexia-preflight.py --worklist-fail-on any  # 最終同期前: worklist が残っていれば失敗
python scripts/check-lexia-preflight.py --allow-untracked-sync-artifacts  # ローカル内容作業中のみ
python scripts/check-lexia-preflight.py --root-only  # root 改善だけ: ROOT_TOOLING 以外を gate 化
python scripts/check-lexia-preflight.py --root-only --change-summary-limit 3
python scripts/check-lexia-preflight.py --tooling-only  # root/tooling 作業中: 別セッション生成差分を棚卸ししつつ全検査
python scripts/check-lexia-preflight.py --tooling-only --change-summary-limit 3
python scripts/check-lexia-preflight.py --change-fail-preset tooling-only --change-summary-untracked-files normal
python scripts/check-lexia-preflight.py --change-fail-preset root-tooling-only
python scripts/check-lexia-preflight.py --change-fail-preset tooling-only
python scripts/check-lexia-preflight.py --change-fail-preset sync-ready
python scripts/check-lexia-preflight.py --change-fail-on-group GENERATED_SYNC_HTML --change-fail-on-group QUARANTINED_OUTPUT
python scripts/check-lexia-stability.py outputs references --settle-seconds 2  # 別セッションの書き込み停止確認
python scripts/check-lexia-stability.py outputs references --settle-seconds 2 --attempts 5 --retry-delay-seconds 3
python scripts/lexia-change-summary.py --json deploy/lexia-change-summary.json  # コミット前の差分仕分け
python scripts/lexia-change-summary.py --fail-preset root-tooling-only
python scripts/lexia-change-summary.py --fail-preset tooling-only
python scripts/lexia-change-summary.py --fail-preset sync-ready
python scripts/lexia-change-summary.py --fail-on-group GENERATED_SYNC_HTML --fail-on-group QUARANTINED_OUTPUT
```

既定では `outputs/` / `references/` 配下の同期対象 HTML が git 追跡済みかも確認する。
ローカル生成ファイルが未追跡のまま存在すると、Lexia 同期元に載らず「ローカル検査は通るが
同期先では HTML 不足/ID 不一致に見える」状態になるため ERROR にする。内容改善セッション中に
一時的に未追跡ファイルを許す場合だけ `--allow-untracked-sync-artifacts` を付ける。
`git add -N` などで index 上の実体が空の intent-to-add HTML も、同期元に本文が載らないため
未追跡扱いで止める。
`--final` は最終同期前プロファイル。`--worklist-fail-on any` / `--change-fail-preset sync-ready` /
`--generated-validators` / `--generated-validator-show-warnings` を
自動指定し、内容改善 TODO/WARN や `_failed/` / `work/` / ローカル設定の残り物が
1 件でも残っていれば失敗させる。さらに `--stability-seconds 2 --stability-attempts 3` 相当で
`outputs/` / `references/` の HTML が観測中に変わらないか、短い再試行込みで確認する。
`--bundle-dir` と併用した場合は `check-lexia-bundle.py --fail-on-not-ready` も自動指定し、
bundle index v5 の `gates.ready=false` を最終同期前 gate として扱う。
既定では最初の失敗で停止するため、差分 gate と worklist gate などをまとめて見たい場合は
`--final --keep-going` を使う。`--keep-going` の最終 summary は失敗 step 名と exit code を併記する。
`--allow-untracked-sync-artifacts` とは同時指定不可。

`--root-only` は root 改善だけを切り出すプロファイル。
`--change-fail-preset root-tooling-only` / `--allow-untracked-sync-artifacts` / `--keep-going` を
自動指定し、`--change-summary-limit` 未指定時は表示上限を 8 にする。
別セッションの生成 HTML や `scripts/validate-*.py` などの generation tooling 差分も
`change summary` で blocking として残す。生成 validator 横断実行は自動では入れないため、
root の監査ツールだけを軽く確認したい時に使う。`--final` / `--tooling-only` とは同時指定できない。

`--tooling-only` は root/tooling 改善セッション用プロファイル。
`--change-fail-preset tooling-only` / `--allow-untracked-sync-artifacts` / `--generated-validators` /
`--generated-validator-show-warnings` / `--keep-going` を自動指定し、
`--change-summary-limit` 未指定時は表示上限を 8 にする。
生成 HTML や `canonical/` など別セッションの差分は `change summary` で blocking として残しつつ、
同期契約・RX 到達性・個別 validator などの検査を最後まで回せる。
最終同期前プロファイルではないため、`--final` とは同時指定できない。

`--bundle-dir` は同期前監査の安定出力一式を同じディレクトリにまとめるショートカット。
未指定の出力先だけを次の既定名で埋める。

- `lexia-sync-manifest.json`（`--json-format manifest`）
- `rx-coverage.json`
- `lexia-content-worklist.md`
- `lexia-content-worklist.json`（`--worklist-json-format manifest`）
- `lexia-content-prompts/`
- `lexia-file-stability.json`（`--final` または `--stability-seconds > 0` の場合）
- `lexia-change-summary.json`
- `lexia-manifest-diff.json`（`--compare-sync-manifest` 指定時）
- `generated-validators.json`（`--generated-validators` 指定時）
- `bundle-index.json`（検証成功時。gate summary、各 manifest の要約、bundle 内ファイルの bytes/sha256）

明示した `--json` / `--rx-json` / `--worklist-json` などは上書きしない。
標準ファイル名一式を使っている場合は、最後に `check-lexia-bundle.py --verify-current` も自動実行し、
manifest 3 種・generated validator JSON・Markdown・target 別 prompt の欠落/過剰をまとめて検証する。
`--bundle-dir` 使用時は、別セッションの生成更新による bytes drift を減らすため、
`lexia-sync-manifest.json` は RX/worklist 生成後、bundle 検証の直前に作る。
検証成功時は `bundle-index.json` も更新し、直後に `--verify-index` で index と bundle 実体の一致も検証する。
index も時刻を入れない安定出力。`schemaVersion=lexia-preflight-bundle-index/v5` では
`gates.ready` / `gates.changeSummary` / `gates.syncContract` / `gates.rxReachability` /
`gates.contentWorklist` / `gates.generatedValidators` を載せるため、あとから bundle だけ見ても
同期前に何が残っていたかを機械的に判定できる。`gates.details` には
`ERROR/WARN/TODO`、`failCount`、`dangling/unreachable` などの理由件数も残す。validator warning は
`gates.generatedValidatorWarnings` に件数として残すが、それ自体では `ready=false` にしない。
`generatedValidators.checked` と `gates.details.generatedValidators.checked` で横断 validator を
実行した bundle かどうかも判別できる。横断 validator が未実行なら
`gates.generatedValidators=false` になり、final-ready の bundle とは扱わない。
監査 JSON / worklist Markdown / prompt は内容が変わった場合だけ書き直すため、mtime だけの
不要な同期差分を出しにくい。
`check-lexia-bundle.py` 単体実行時は、`lexia-change-summary.json` の `failCount` が 1 以上なら
NOTICE として件数・プリセット・先頭数件を表示する。schema 検証だけなら exit 0 のまま。
bundle 単体でも dirty change gate として失敗させたい場合は `--fail-on-change-fail-items` を付ける。
bundle 全体の ready gate として失敗させたい場合は `--fail-on-not-ready` を付ける。
これは `gates.ready=false`、つまり sync contract / RX 到達性 / worklist / change summary /
generated validators の未実行または failure のいずれかが残っている場合に exit 1 にする。
NOTICE には未完 gate 名に加え、`ERROR/WARN/TODO` や `failCount` などの理由件数も出す。

`--compare-sync-manifest` は、今回作る `lexia-sync-manifest.json` と既存 manifest を比較し、
`--bundle-dir` 使用時は `lexia-manifest-diff.json` を同じ bundle に出す。
`--manifest-diff-fail-on-content-change` は本文ハッシュが変わった場合だけ preflight を失敗させる。
`compare-lexia-manifests.py` は 2 つの `lexia-sync-manifest.json` を比較し、
差分を `added` / `removed` / `contentChanged` / `generatedOnly` / `sizeOnly` /
`metadataOnly` に分ける。`stableSha256` が同じで `generated` だけが動いた差分は
`generatedOnly` になるため、Lexia 同期で「毎回更新が出る」原因が本文変更なのか
生成日時フッターだけなのかを切り分けやすい。
`--json` を付けると `schemaVersion=lexia-manifest-diff/v1` の安定 JSON を出力する。
`--fail-on-content-change` は本文ハッシュが変わった場合だけ exit 1 にする。

`check-lexia-stability.py` は `outputs/` / `references/` の HTML を 2 回スナップショットし、
観測中に追加・削除・内容変更があれば exit 1 にする読み取り専用チェック。
`--attempts` と `--retry-delay-seconds` を付けると、別セッションの生成が一時的に走っている場合に
安定するまで数回だけ待てる。
`--stability-json` を付けると `schemaVersion=lexia-file-stability/v1` の安定 JSON も保存する。
別セッションで生成改善を回している間に preflight bundle の `--verify-current` が bytes drift で落ちる場合は、
まずこのコマンドで書き込みが止まったか確認してから `--final --bundle-dir ...` を実行する。

`lexia-change-summary.py` は dirty worktree を `ROOT_TOOLING` / `GENERATION_TOOLING` /
`GENERATED_SYNC_HTML` / `QUARANTINED_OUTPUT` / `DOCS` / `INPUTS` などに仕分ける読み取り専用チェック。
ルート改善と生成内容改善を同じ commit に混ぜないため、最終整理前に使う。
既定では `--untracked-files all` として未追跡ディレクトリもファイル単位に展開するため、
`_failed/` や `work/` の中身を 1 行のディレクトリとして見落としにくい。
preflight 入口からは `--change-summary-untracked-files normal|no` を渡せるため、巨大な未追跡ディレクトリで
ログを抑えたい場合だけ切り替える。
`--fail-on-group` は指定グループに 1 件でも差分があれば exit 1 にする。
同じ gate は preflight 入口から `--change-fail-on-group` としても指定できる。
gate で止まる差分は JSON の `failItems` と標準出力の `blocking changes` にも出るため、
最終同期前に片付ける対象だけを拾いやすい。
`--fail-preset root-tooling-only` / `--change-fail-preset root-tooling-only` は
`ROOT_TOOLING` 以外の差分をまとめて gate 化するショートカット。
`scripts/lex/` と、`scripts/` 直下の `build_*` / `build-*` / `tx-build-*` / `validate-*` は
`GENERATION_TOOLING` として分かれるため、
監査ツール改善と生成・内容検証パイプライン改善を同じ root tooling 差分として見落としにくい。
`--fail-preset tooling-only` / `--change-fail-preset tooling-only` は
`ROOT_TOOLING` と `GENERATION_TOOLING` の差分だけを許し、生成 HTML / canonical / docs / inputs / work /
local config などの別セッション差分をまとめて gate 化する。root 側の監査ツール改善と
生成 validator 改善を一緒に片付けたいが、生成済み HTML は混ぜたくない時に使う。
`--fail-preset sync-ready` / `--change-fail-preset sync-ready` は、別セッションで更新された
`GENERATED_SYNC_HTML` は許しつつ、`QUARANTINED_OUTPUT` / `WORK` / `LOCAL_CONFIG` / `OTHER` が
残っていれば失敗させる同期直前向けショートカット。
ルート改善だけを commit する前は、`GENERATION_TOOLING` / `GENERATED_SYNC_HTML` / `QUARANTINED_OUTPUT` /
`CANONICAL` / `DOCS` / `INPUTS` / `WORK` / `LOCAL_CONFIG` を必要に応じて gate 化する。
`--bundle-dir` では `lexia-change-summary.json` として標準出力し、`bundle-index.json` にも
グループ別件数と `failItems` を載せる。JSON は `schemaVersion=lexia-change-summary/v1` の安定出力で、実行時刻は入れない。

同期契約チェッカ / worklist 生成器自体の軽量 self-test:

```
python scripts/test-lexia-preflight.py
python scripts/test-check-duplicates.py
python scripts/test-validate-ariadne.py
python scripts/test-validate-rx.py
python scripts/test-validate-tree.py
python scripts/test-generated-validators.py
python scripts/test-generated-validators-manifest.py
python scripts/test-ariadne-backfill-rx-link.py
python scripts/test-lexia-sync-contract.py
python scripts/test-lexia-manifest.py
python scripts/test-lexia-manifest-diff.py
python scripts/test-lexia-content-worklist.py
python scripts/test-lexia-worklist.py
python scripts/test-rx-coverage.py
python scripts/test-rx-coverage-manifest.py
python scripts/test-lexia-bundle.py
python scripts/test-lexia-stability.py
python scripts/test-lexia-change-summary.py
python scripts/test-stamp-footer.py
python scripts/test-stamp-created-date.py
python scripts/test-restamp-english.py
python scripts/test-stamp-staged.py
```

終了コード:

- **exit 1**: いずれかのゲートで ERROR / dangling / UNREACHABLE（strict）がある。
- **exit 0**: Lexia 同期前の機械ゲートを通過。

## 内容改善セッション用 worklist: lexia-content-worklist.py

このセッションでルート改善を続けつつ、別セッションへ生成 HTML の内容改善を渡すための
read-only worklist 生成器。`check-lexia-sync-contract.py` の単体 WARN/ERROR と、
TX/JX/ARIADNE/TREE/RX の対応欠落、`outputs/**/_failed/*.html` の隔離物を
対象コード単位にまとめる。

使い方:

```
python scripts/lexia-content-worklist.py
python scripts/lexia-content-worklist.py --markdown deploy/lexia-content-worklist.md
python scripts/lexia-content-worklist.py --json deploy/lexia-content-worklist.json --quiet
python scripts/lexia-content-worklist.py --json deploy/lexia-content-worklist.json --json-format manifest --quiet
python scripts/check-lexia-worklist.py deploy/lexia-content-worklist.json --verify-current
python scripts/lexia-content-worklist.py --prompts-dir deploy/lexia-content-prompts --quiet
python scripts/lexia-content-worklist.py --target 刑JX020 --prompts-dir deploy/lexia-content-prompts --quiet
python scripts/lexia-content-worklist.py --fail-on any --quiet  # worklist が空でなければ exit 1
python scripts/lexia-content-worklist.py --markdown deploy/lexia-content-worklist.md --timestamp
```

出力は `刑JX019` のような target ごとに、対象パス・推奨 action・実行すべき validator を列挙する。
`--prompts-dir` は target ごとの子セッション用プロンプト Markdown も作る。別セッションでは原則その
target の生成ファイルだけを編集し、最後に
`python scripts/check-lexia-preflight.py --allow-untracked-sync-artifacts` まで通す。
親セッションまたは最終同期前は allow なしの `python scripts/check-lexia-preflight.py` で
未追跡の同期対象 HTML も止める。
`--prompts-dir` は同ディレクトリ内の古い `*_content_prompt.md` を現行 worklist に合わせて削除する。
普段は可視化だけ、最終同期前は `--fail-on any` / `--worklist-fail-on any` で残作業を gate 化する。
Markdown は既定で timestamp を入れない安定出力。スナップショット時刻が必要な場合だけ
`--timestamp` または `--generated-at <固定値>` を付ける。
JSON は既定で既存互換の items 配列、`--json-format manifest` では `schemaVersion` / roots /
filters / counts / categories / kinds / items を持つ安定 object を出す。こちらも実行時刻は入れない。
`--target` や `--no-failed` の条件は filters に保存される。
`check-lexia-worklist.py --verify-current` は保存済み worklist manifest を現在の outputs/references
から再計算した worklist と比較し、古い worklist や field order/count の破損を検出する。
`check-lexia-preflight.py --worklist-json ... --worklist-json-format manifest` では生成直後に自動実行される。

## 配布前ゲート: check-duplicates.py（ファイル間の重複・ID 不整合）

`validate-tx.py` / `validate-jx.py` は **1 ファイル内** の検証専用で、
「別ファイル同士」の問題は拾えない。これを補うのが `check-duplicates.py`。

検出ルール（いずれかで exit 1）:

- **D80 ID-MISMATCH** … `<title>` / `.doc-header` / `.footer-problem` の問題コードが
  ファイル名と不一致（例: 刑TX338/358/123 の `<title>` や 刑TX055 の footer が
  「刑TX311」のまま＝**他問からのコピペ残り**）。0 埋め差(JX1/JX001)、
  RX 枝番 separator 差(RX001-1/RX001_01)は数値比較で吸収。KJX は JX と区別する。
  ※ `validate-jx.py` は footer/header の ID を見ないため、JX/RX もこの D80 がカバーする。
- **D81 DUP-TITLE** … 2 件以上が同一 `<title>`（別問題が同一タイトル＝Lexia 取込時に
  重複誤検出される元凶）。
- **D82 DUP-BODY** … 2 件以上が生成日時だけを除いて本文一致（同一問題を別名で重複保存）。

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

- **分類不能パス/命名** … `outputs/000_TX` / `001_JX` / `NNN_KJX` / `ux/000_TX`
  / `ux/001_ARIADNE` / `ux/002_RX` / `ux/003_TREE` / `ux/004_参考資料` / `references`
  の既知規約に乗らない HTML。KJX は論文過去問系の予約分類として `outputs/NNN_KJX/{subject}/{prefix}KJXNNN.html` を受ける。
- **fileName / code / title / subject / category の揺れ** … ファイル名由来の `code`・
  `baseCode` と `<title>`・科目ディレクトリの不一致、`category+code` や `fileName` の重複。
- **生成 HTML の対応欠落** … 公式 TX と `_lex` の片割れ、JX 本体に対応する ARIADNE/TREE/RX、
  または副産物だけが残って JX 本体が無い状態。
- **sourcePath 相当** … repo 相対パスを `/` 区切りで安定化し、JSON 出力で確認可能。
- **作成日フッター** … `class="lexia-genmeta"` と `data-generated`、本文 `Generated:` の欠落・重複。
  `data-generated` はタイムゾーン付き ISO 8601、本文表示は `Generated: YYYY-MM-DD HH:MM` と一致必須。
  `stamp_footer.py` は既存 stamp が複数あっても 1 件に正規化する。
  `stamp-staged.py` は `git add -N` の空 index entry も検出し、genmeta 済み HTML でも本文を再ステージする。
- **HTML 本文不足** … カテゴリ別の最低サイズ/テキスト量を下回るファイル。
- **ARIADNE→RX** … `data-athena-code` と `data-rx` の形式・参照先 RX 実在。
  `data-rx` の重複は既存互換のため WARN とし、worklist で想起カード単位の割当確認へ回す。
  `scripts/ariadne-backfill-rx-link.py` の `MAP` で `None` と明示された想起カードは、
  総論/汎用カードまたは対応 RX 無しとして意図的省略扱いにする。MAP に無い省略や MAP 長不一致は WARN。
  MAP 外の ARIADNE でも全想起カードに `data-rx` が直接入っている場合、backfill は direct 済みとして skip する。
  真の到達不能は
  `check-rx-coverage.py --strict` が判定する。
- **生成 HTML 個別バリデータ** … 内容改善の節目では
  `python scripts/check-lexia-preflight.py --generated-validators --generated-validator-show-warnings --generated-validator-json deploy/generated-validators.json --allow-untracked-sync-artifacts`
  で ARIADNE/RX/TREE の既存 validator を横断実行し、WARNING の場所を一行表示する。
  JSON は `schemaVersion=generated-validators/v1` の安定出力で、実行時刻を入れない。
  `--bundle-dir` と併用し、`--generated-validator-json` 未指定なら `generated-validators.json` を同ディレクトリへ出す。
  保存直後に `check-generated-validators-manifest.py --verify-current` も自動実行し、古い JSON や
  schema 破損を止める。
  WARNING も gate 化したい最終確認では `--generated-validator-fail-on-warning` を足す。
  通常 preflight では重くしないため任意。

使い方:

```
python scripts/check-lexia-sync-contract.py
python scripts/check-lexia-sync-contract.py --summary
python scripts/check-lexia-sync-contract.py --strict
python scripts/check-lexia-sync-contract.py --json deploy/lexia-sync-audit.json
python scripts/check-lexia-sync-contract.py --json deploy/lexia-sync-manifest.json --json-format manifest
python scripts/check-lexia-sync-contract.py --summary --allow-untracked-sync-artifacts  # ローカル内容作業中のみ
python scripts/check-lexia-manifest.py deploy/lexia-sync-manifest.json
python scripts/check-lexia-manifest.py deploy/lexia-sync-manifest.json --verify-current
```

`--json` の既定は既存互換の entries 配列。`--json-format manifest` は
`schemaVersion` / 件数 / category counts / `entries` を持つ object を出す。どちらも実行時刻を
入れない安定出力なので、差分監査で毎回更新が出る原因にしない。
`check-lexia-manifest.py` は保存済み manifest の schemaVersion、entry field order、sourcePath 昇順、
sourcePath が `roots` 配下の HTML であること、重複、category counts を単独で再検証する。
`--verify-current` を付けると manifest の `roots` を現在のファイルシステムで再走査し、entries と
ERROR/WARN 件数が stale でないことも確認する。
`check-lexia-preflight.py --json ... --json-format manifest` では生成直後に `--verify-current` 付きで
自動実行される。

終了コード:

- **exit 1**: ERROR あり。`--strict` では WARNING でも exit 1。
- **exit 0**: ERROR なし。WARNING は配布可だが後追い整備候補。

`check-lexia-preflight.py` と `jx-finalize.ps1` は commit/push 前に
`check-duplicates.py` → `check-lexia-sync-contract.py --summary`
→ `check-rx-coverage.py --strict` の順で実行する。これにより、Lexia 同期で
「HTML本文不足」「ID不一致」「作成日欠落により更新が毎回出る」原因を git へ入れる前に止める。

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
- 一括展開：分類器で Type A を除いた _lex を抽出 → 1問1エージェント（ワークフロー）で `tx-extract-source` 読込→執筆→
  `tx-inject-narrative`→`validate-tx-core` Errors:0。刑法 362問は展開済み（Type A 22＋Type B 340）。

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
python scripts/check-rx-coverage.py --no-color  # ログ保存用に ANSI 色コードを抑止
python scripts/check-rx-coverage.py --json deploy/rx-coverage.json
python scripts/check-rx-coverage-manifest.py deploy/rx-coverage.json --verify-current
```

`check-lexia-preflight.py` では `--summary --strict --no-color` で自動実行される。
`--rx-json` を指定すると `schemaVersion=lexia-rx-coverage/v1` の安定 JSON も保存する。
保存直後に `check-rx-coverage-manifest.py --verify-current` も自動実行し、古い JSON や
detail/count の破損を検出する。

実測（2026-06-28）: 刑法 JX 66 / RX present 214 / referenced 138 / ARIADNE 不在 2 問 →
**UNREACHABLE 0** / SAFETY-NET 76 / dangling 0。刑法以外 6 科目は RX 未生成のため graceful skip。
