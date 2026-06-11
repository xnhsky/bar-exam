"""
=== セレクタ録画スクリプト（メンテ用） ===

AI StudioのUIが変わって prep_tts_tabs.py が動かなくなった時、
これで操作を録画し直して新しいセレクタを取得する。

== 前提 ==
ログイン済みChromeをデバッグ起動しておく（どのプロファイルでもOK）:
  & "C:\Program Files\Google\Chrome\Application\chrome.exe" `
    --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\chrome-tts-profiles\acc1-aoede"

== 使い方 ==
  python record_tts.py

  1. AI Studioのタブが開く
  2. 別ウィンドウで Playwright Inspector が起動
  3. Inspectorの「Record」を押す
  4. 1タブ分の操作を手動でやる:
       - Speaker 1 をクリック → Voiceパネルで Aoede 検索 → Aoede選択 → 閉じる
       - Text欄クリック → Ctrl+A → Delete
  5. Inspectorに出たコードをコピー
  6. そのコードを基に prep_tts_tabs.py の _setup_page() を更新
     （MAINTENANCE.txt の手順を参照）
"""
from playwright.sync_api import sync_playwright

URL = "https://aistudio.google.com/generate-speech?model=gemini-2.5-pro-preview-tts"
CDP = "http://127.0.0.1:9222"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(CDP)
    ctx = browser.contexts[0]
    page = ctx.new_page()
    page.goto(URL)

    print("=" * 60)
    print("AI Studioを開きました。Inspectorで操作を録画してください。")
    print("Recordを押して1タブ分の操作 → コードをコピー。")
    print("=" * 60)

    page.pause()  # Inspector（録画パネル）を起動
