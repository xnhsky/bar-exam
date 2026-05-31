_remote-inbox/  — 外出先専用 PDF ドロップゾーン（TX）

目的：
  スマホ / GitHub Web UI から「外出先でアップロードする問題 PDF」を置く専用フォルダ。
  ローカル PC 用の staging（../_pending/）とは役割が違う。混同しないこと。

仕組み：
  batch-tx / night-batch-runner.ps1 は inputs/tx-pdfs/ の *直下* の {NNN}.pdf を読む。
  本フォルダの PDF はそのままでは拾われないため、取り込みスクリプトで
  inputs/tx-pdfs/{NNN}.pdf へ正規化（番号抽出・3 桁ゼロ埋め）してから処理する。

外出先からの運用フロー：
  1. スマホ / GitHub Web で本フォルダ（inputs/tx-pdfs/_remote-inbox/）へ PDF をアップロード
     → ブランチ claude/night-batch-pdf-github-aGVYp にコミット
  2. Claude Code web セッションを起動（同ブランチ）
  3. 取り込み：  bash scripts/remote-intake.sh
     → _remote-inbox/*.pdf を inputs/tx-pdfs/{NNN}.pdf へ展開（CLAUDE.md §2-3 準拠）
  4. バッチ生成：/batch-tx {最若番 NNN}
  5. 回収：     bash scripts/remote-collect.sh
     → 生成 HTML を当ブランチへ push（GitHub から回収）

命名（CLAUDE.md §2-3）：
  ファイル名の *最初の連続数字* がシリアル番号になる。3 桁未満は前ゼロ埋め。
  例：316.pdf → 316 ／ 予備R1-16詐欺.pdf → 001（最初の数字「1」）／ 数字なし → 取り込みスキップ

注意：
  処理済みの PDF は GitHub Web 上から本フォルダ内で削除してよい（履歴は git に残る）。
