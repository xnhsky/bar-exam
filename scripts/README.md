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
- 生成済み HTML が存在する PDF (outputs/tx/{科目}TX/{科目}TX{番号}.html 存在) は
  inputs/tx-pdfs/ から削除可能（容量節約）
- 削除は git で正式に削除し、両 PC で同期する
- HTML は永続保持（生成済みコンテンツが本体）

### PDF 補充のタイミング
- inputs/tx-pdfs/ の未生成 PDF が 5 件以下になったら補充推奨
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
