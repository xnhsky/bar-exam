tx-pdfs/

短答式 TX 生成用の入力 PDF を配置するディレクトリ。

命名規則：
  ファイル名に数字を含むこと。最初の連続数字が出力ファイル名のシリアル番号になる。

例：
  299.pdf                       → 刑TX299.html（科目は内容から判定）
  K310-2024-problem.pdf         → 刑TX310.html（最初の連続数字「310」を採用、2024 は使わない）
  司法R1-16詐欺.pdf             → 刑TX001.html（最初の連続数字「1」を採用、要注意）
  kenpo-question-05.pdf         → 憲TX005.html
  予備H30問15.pdf               → 民TX030.html（最初の連続数字「30」を採用、要注意）
  民法.pdf（数字なし）          → 処理中断、ユーザーに番号確認

使い方：
  Claude Code で `/new-tx inputs/tx-pdfs/{ファイル名}` を実行。

詳細は CLAUDE.md §2 を参照。
