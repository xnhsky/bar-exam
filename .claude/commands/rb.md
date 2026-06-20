---
description: RB（リモートバッチ）— inputs/000_TX/001_刑法 の「N番からM番まで」をリモートで連続バッチ生成し、各問完了ごとに git commit/push で永続化する。「346-350 を RB して」「RB 346〜350」等で起動。
---

# rb：リモートバッチ（Remote Batch）コマンド

## 何をするか

`inputs/000_TX/001_刑法/` 配下の **指定番号レンジ（N番〜M番）** を、`batch-tx` / `new-tx` の
v11.0.0 LOOP-CORE 規律そのままで連続生成し、**各問の検証通過ごとに git commit/push**
で GitHub に永続化する。リモート実行環境（Claude Code on the web）でのバッチ運用を
1 コマンドで回すための薄いラッパー。

## 引数（レンジ指定・必須）

`$ARGUMENTS` から **開始番号と終了番号** を読み取る。次のいずれの表記も許容：

- `346-350` / `346〜350` / `346~350`
- `346 350`
- `346から350`（「から」「まで」「を」「RBして」等の語は無視して数字だけ抽出）

抽出ルール：
- 数字グループを 2 つ取り、小さい方を `START`、大きい方を `END` とする。
- 数字が 1 つしか無い場合：その番号から **5 問**（`START`〜`START+4`）を既定とする。
- 数字が 0 個 → **処理中断**し、user にレンジを確認（無断推定禁止）。

## Phase 0：プリフライト（必須・自動）

1. **本線同期の確認**（二台運用・CLAUDE.md §8）：作業前提として master が最新か確認。
   ```bash
   git fetch && git log --oneline origin/master -3
   ```
   ローカルが遅れていれば user に `git pull origin master` を促す。
2. **対象 PDF の実在確認**：`START`〜`END` の各 `inputs/000_TX/001_刑法/{N}.pdf` が存在するか点検。
   - 欠番があれば一覧で報告し、**欠番を除いた実在分のみ**を対象にするか、
     Drive「抽出PDF」（`1rUu4fadQYnlKNnjcZ5hBbSV7ceVBKChY`・原本 445 問）から
     回収するかを user に確認。
3. **対象リスト提示 → 即実行**（RB は明示レンジ起動なので確認は 1 回だけ）：
   ```
   RB 対象：346.pdf 〜 350.pdf（5 ファイル・実在 5 / 欠番 0）
   経路：canonical/GENESIS-CORE.html（v11.0.0 LOOP-CORE）
   配色：問題ごとに正答率帯→P1/P2/P3 自動判定、11 パレットから AI 選定（V3）
   保存：各問完了ごとに git commit/push（本線 master へ集約）で GitHub 永続化
   開始します。
   ```
   欠番ゼロ・PDF 実在が確認できれば、原則そのまま Phase 1 へ進む
   （ブロッキングの y/n は取らない。中断を嫌う運用方針 CLAUDE.md §8）。

## Phase 1〜N：レンジ・ループ実行

`START` から `END` まで 1 問ずつ、`.claude/commands/new-tx.md` の **Phase 0〜7 を完全実施**：

- Phase 0 環境確認 → Phase 1 PDF 解析・配色判定・冒頭応答
- Phase 2 命名（CLAUDE.md §2） → Phase 3 GENESIS clone + 本文空初期化
- Phase 4 section 差替 → Phase 5 SVG 重なり機械検査
- Phase 6 `scripts/validate-tx-core.py` で G1〜G18 ERROR 0 件確認
- **Phase 7 git コミット（必須）**：検証通過後、`outputs/000_TX/{科目TX}/{ファイル名}.html` を
  `git add` → **1 問ごとに commit** → `git push`（本線 master へ集約・§8 / §9）。
  生成＝コミットで GitHub に永続化し、コンテナ回収による HTML ロストを防ぐ。
  **問が 1 つ完了するたびに即 commit/push**（数十問を 1 コミットにまとめない）。

各問完了時に内部記録（`pdf_number` / `output_path` / `validate_errors` /
`palette_pattern` / `committed`(commit hash) / `status` / `failure_reason`）を保持。

## エラーハンドリング（batch-tx 継承）

- API socket error → その問 **PARTIAL**、次へ（停止しない）。
- validate ERROR → その問 **FAILED**、出力残置、次へ。
- **3 問連続失敗で停止**し、user に報告。
- 失敗問の再生成は `/new-tx inputs/000_TX/001_刑法/{N}.pdf` で個別実施（自動 retry はしない）。

## 完了レポート（必須）

- 各問：番号 / status / サイズ / validate 結果 / 採用パレット / **commit hash**
- **`committed` 未完の問が無いか点検**し、全 SUCCESS 問の GitHub 反映（push 済み）を
  保証してから終了。
- HTML は git 管理（§9）。**生成＝コミットで GitHub が永続先**。未 commit/push の問が
  残る場合は、コンテナ回収前に最優先で commit/push する。

## v11.0.0 LOOP-CORE 鉄則（new-tx / batch-tx から継承）

- 唯一の skeleton 起点 `canonical/GENESIS-CORE.html`。`outputs/*/` 流用・`render.py` 経路は禁止。
- 本文は空初期化してから PDF を見て新規執筆。配色 V3（P1/P2/P3・11 パレット）。
- SVG bounding box 全ペア AABB 検査。ヘッダー／フッター本文に配色記載禁止。
- 1 メッセージ 50KB 超出力禁止（section 分割）。冒頭応答必須。

$ARGUMENTS
