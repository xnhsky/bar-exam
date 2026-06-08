# BACKLOG

## JX→TTS 自動化

最終ゴール：確定済み JX HTML を入力に、ラジオ番組風 TTS 音声教材の
プレーンテキストサブパート群（1 問あたり 10〜11 ファイル）を自動生成する
夜間バッチパイプラインを稼働させる。

---

### commit1: TTS 層（完了 2026-05-29）

#### `prompts/tts-jx-headless.md` 新規

- 確定版 TTS 変換プロンプト（`prompts/TTSプロンプト.txt` 由来）を本体に逐語転載
- `claude -p` headless 実行用の wrapper を追加：
  - 注入変数 3 つ：`{SOURCE_HTML_PATH}` / `{PROBLEM_ID}` / `{OUTPUT_DIR}`
  - ツール名読み替え：`create_file→Write` / `str_replace→Edit` / `present_files→完了報告`
- PoC 確定の追記：
  - 本文 40K 字級・3 論点で **10〜11 分割**が目安（15 分割は字数下限割れと PoC で実証済み）
  - 各サブパート実目標 **1,400〜1,900 字**（下限 1,200 字を確実に超える）
  - 本文の「800 字緊急例外」は適用しない
- sentinel 3 種：
  - `BATCH_ITEM_COMPLETED` / `BATCH_ITEM_COMPLETED_WITH_ISSUES` / `BATCH_ITEM_FAILED`
  - 本文「自動自己完結ルール」の最終ステップ（present_files 直後）として接続

#### `scripts/validate-tts.py` 新規

- **字数検証**：`\s` 全種（U+3000 全角スペース含む）除去後、1,200〜2,500 字
  レンジ外で FAIL
- **タグ検出 6 種**：
  - `html_or_ssml_tag` (`<...>`)
  - `markdown_bold` (`**`)
  - `markdown_underscore` (`__`)
  - `markdown_header` (行頭 `#`)
  - `markdown_blockquote` (行頭 `>`)
  - `bracket_markup` (`[...]`)
- **命名規則（2026-06-08〜・フラット通し番号）**：`^{PROBLEM_ID}-{連番}\.txt$` 厳密一致（連番は 1 起点・ゼロ埋めなし）
  - 旧式 `{1〜7}{a-d}`（例 `1a`）は廃止。既存ファイルは `scripts/migrate-tts-sequential.py` で移行済み
- **グループ単位**：
  - 連番 `1` 必須
  - 通し番号 1..max 連続性（欠番・重複なし）
- **入力**：`utf-8-sig` 読込（BOM 付き UTF-8・cp932 誤読回避）
- **CLI 2 形態**：
  - `python scripts/validate-tts.py {OUTPUT_DIR}` → ID 別グループ化して一括
  - `python scripts/validate-tts.py {OUTPUT_DIR} {PROBLEM_ID}` → ID 前方一致で絞込（runner 連結用）
- **終了コード**：0=全 PASS / 1=FAIL / 2=引数エラー or 対象 0 件
- **自己テスト**：正常 / 字数不足 / SSML 混入 / prefix filter（2 ID）/ 存在しない ID / 連番 1 欠落 / 通し番号飛ばし / 連番重複

---

### commit2: JX HTML 自動化（未着手）

- `scripts/jx-batch-runner.ps1` 新規予定
  - 既存の TX 用 `night-batch-runner.ps1` の構造を踏襲
  - `inputs/jx-pdfs/*.pdf` を入力に、`outputs/jx/{科目JX}/*.html` を出力
- `prompts/new-jx-headless.md` 新規予定
  - JX 用 headless プロンプト
  - `spec/jx-v3.2-master.md` + `scripts/validate-jx.py` (J1〜J20) を連結

---

### commit3: HTML 確定 → TTS 連結（未着手）

- `jx-batch-runner.ps1` から `validate-jx.py` 通過後に：
  - `prompts/tts-jx-headless.md` を `claude -p` で実行
  - `outputs/tts/{PROBLEM_ID}/*.txt` 群を生成
  - `scripts/validate-tts.py` で検証
- sentinel ロギング・失敗時リトライ・夜間連続稼働の一貫化

---

## 関連既存トラック（参考）

- TX シリーズ v10.0.0 GOLD-SKELETON（稼働中・`night-batch-runner.ps1`）
- JX シリーズ v3.2 master（手動運用中・自動化は本 BACKLOG の commit2 で着手）


---

## 2026-05-30 batch-tx 316-320: tool-format slips and fixes

### Issue
- 316/317 batch-tx had repeated empty runs from 2 causes:
  1. tool-call open tag misspelling -> some Edit/Bash/Write calls did not parse (DRILL blocks etc.)
  2. heredoc breakage: bash heredoc with long JP text + many quotes -> unexpected EOF
- side effects:
  - DRILL12 mis-perceived as duplicate (empty runs showed old+new in log); file was 01-12 unique, DRILL12 body was GENESIS leftover.
  - G13 rework miss on C-2/C-3 section headings -> validate-tx-gold G13 FAIL; reworded per-problem to fix.

### Fix
1. new-tx.md 4h-bis added: canonical drill-block HTML + 4 rules (data-correct == data-correct-value; data-explanation duplicated in attr and .quiz-answer; data-value fixed; no answer-restate).
2. bulk replace: avoid heredoc, Write script to file then run.
3. structural heading per-problem rework done right after generation, verified by G13.

### Result
- 316 and 317 both validate-tx-gold.py G1-G18 ALL PASS (Errors 0).
