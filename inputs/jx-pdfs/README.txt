jx-pdfs/

事例問題型 JX 生成用の入力を配置するディレクトリ。
JX→TTS→音声 を一気通貫で回す jx-batch-runner.ps1 の入力フォルダ。

────────────────────────────────────────────────────
■ 配置するもの（1 問につき 2 ファイル・同番号・同フォルダ）
────────────────────────────────────────────────────
  1) 問題 PDF              例: 032.pdf
  2) 講義の逐語ファイル    例: 032.txt （または 032.md）
     ※ whisper 文字起こし等。本問解説講義の逐語。JX 生成の第一次情報源。

  ファイル名の「先頭の連続数字」が問題番号になり、PDF と逐語は
  この番号が一致するものどうしで自動ペアリングされる。
    032.pdf  ↔  032.txt        （一致）
    32.pdf   ↔  32.md          （一致：int 比較なので 32 と 032 は同一）
    刑法32.pdf ↔ ...           （先頭が数字でないため番号抽出不能＝対象外）

  逐語が無い PDF は「逐語必須」方針により処理対象外（SKIP_NO_TRANSCRIPT）。
  逐語は .txt を .md より優先。先頭数字が PDF と一致する最初の 1 件を採用。

────────────────────────────────────────────────────
■ 一気通貫バッチの実行（PDF を大量に入れてから）
────────────────────────────────────────────────────
  # まず予定確認（生成・削除・音声を一切行わない）
  pwsh -NoProfile -File scripts\jx-batch-runner.ps1 -Subject 刑 -DryRun

  # 本実行（1 科目ずつ・最大 5 問）
  pwsh -NoProfile -File scripts\jx-batch-runner.ps1 -Subject 刑 -MaxProblems 5

  科目は -Subject で固定（刑 / 刑訴 / 民 / 商 / 民訴 / 憲 / 行政）。
  混在させず、科目ごとにバッチを起動する。

  各問の流れ:
    ① PDF＋逐語 → JX HTML（claude -p / new-jx-headless.md）
    ② validate-jx.py PASS  →  PASS 時点で「PDF のみ削除」（逐語は保持）
    ③ JX → TTS 台本（claude -p / tts-jx-headless.md）
    ④ validate-tts.py PASS →  台本 *.txt を tts/input_texts/ へ集約
    ⑤ バッチ末尾で tts/run-tts.ps1 を一括起動 → wav 生成（全自動・課金）

────────────────────────────────────────────────────
■ 音声段（⑤）について
────────────────────────────────────────────────────
  Google AI Studio の Gemini TTS（generate_tts.py）で課金が発生する。
  環境変数 GEMINI_API_KEY が必要。
    $env:GEMINI_API_KEY = "your-key"   # このセッションだけ
  未設定の場合は音声段のみ自動スキップ（JX・台本・集約までは完了）。
  音声を後で回す/手動にする:
    pwsh -NoProfile -File scripts\jx-batch-runner.ps1 -Subject 刑 -SkipAudio
    pwsh -NoProfile -File tts\run-tts.ps1

────────────────────────────────────────────────────
■ 補足
────────────────────────────────────────────────────
  - 既に outputs/jx/{科目JX}/{ID}.html がある番号は SKIP_EXISTS（再生成しない）。
  - JX が検証 PASS した時点で PDF は削除される。逐語は残るので再生成時は
    PDF を再配置すること。
  - 単発生成は従来どおり Claude Code で /new-jx も使用可。
  - 詳細は CLAUDE.md §2 / §4、scripts/jx-batch-runner.ps1 冒頭コメントを参照。
