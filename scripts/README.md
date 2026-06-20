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
