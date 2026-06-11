============================================================
 AI Studio TTS タブ一括準備ツール  使い方メモ
============================================================

【構成ファイル（2つ・同じフォルダに置く）】
  run_tts_prep.ps1   … ランチャー（Chrome起動＋準備をまとめて実行）
  prep_tts_tabs.py   … 本体（Playwrightでタブを準備）

  ※両PC（xnrg2 / OWNER PC）共用。パスは自動判別なので編集不要。

------------------------------------------------------------
【初回だけ・各PCで1回】
------------------------------------------------------------
1) 実行ポリシーを緩める（xnrg2は設定済み。OWNER PCでは初回必要）
     Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

2) 初回起動時、各Chromeで AI Studio にログイン
   （acc1で2ウィンドウ、acc2で2ウィンドウ = 計4回。一度きり）

------------------------------------------------------------
【通常運用：acc1を使う】
------------------------------------------------------------
  cd $env:USERPROFILE        # スクリプトを置いたフォルダへ
  powershell -ExecutionPolicy Bypass -File .\run_tts_prep.ps1 -Account acc1

  → Chrome2つ起動 → 「Press Enter」でEnter → 各15タブ準備

------------------------------------------------------------
【acc2に切り替え（acc1終了後）】
  ※選択肢A：時間差運用。メモリ節約のため必ずacc1を閉じてから。
------------------------------------------------------------
  Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force
  Start-Sleep 3
  powershell -ExecutionPolicy Bypass -File .\run_tts_prep.ps1 -Account acc2

  ※注意: Stop-Process は普段使いのChromeも閉じます。
          作業中のChromeタブは先に保存してから実行。

------------------------------------------------------------
【タブ数を変える（例：各5タブ・テスト）】
------------------------------------------------------------
  powershell -ExecutionPolicy Bypass -File .\run_tts_prep.ps1 -Account acc1 -Count 5

------------------------------------------------------------
【ポート割り当て（参考）】
------------------------------------------------------------
  acc1 Aoede=9222  Laomedeia=9223
  acc2 Aoede=9224  Laomedeia=9225

  プロファイル保存先: %USERPROFILE%\chrome-tts-profiles\

------------------------------------------------------------
【困ったとき】
------------------------------------------------------------
・署名エラーで動かない:
    先頭に  powershell -ExecutionPolicy Bypass -File  を付けて実行
・ランチャーが動かない → Python直接実行でも同じ結果:
    python prep_tts_tabs.py --voice Aoede --port 9222 --count 15
    python prep_tts_tabs.py --voice Laomedeia --port 9223 --count 15
・タブ準備が失敗(FAIL): fail_<voice>_<n>.png を確認
    （AI Studioの一時エラーは自動で最大3回リトライ）
・メモリ不足: 4ウィンドウ同時は重い。acc1→acc2の時間差運用推奨。
    タブ数を --Count 5〜10 に減らすのも有効。
============================================================
