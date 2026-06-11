r"""
AI Studio TTS タブ一括準備スクリプト（ポート/ボイス指定版・リトライ対応）

ボイスごとにウィンドウ(=別ポートのChrome)を分けて準備する。

★ AI StudioのUI変更で [FAIL] が出続けるようになったら:
   MAINTENANCE.txt を見て record_tts.py でセレクタを取り直すこと。
   セレクタ定義は下記 _setup_page() 関数の中にある。

== 事前準備（手動でChromeを起動）==
  & "C:\Program Files\Google\Chrome\Application\chrome.exe" `
    --remote-debugging-port=9222 --user-data-dir="C:\chrome-debug-acc1-aoede"
  ※AI Studioにログイン済みであること。

== 実行 ==
  python prep_tts_tabs.py --voice Aoede --port 9222 --count 15
  python prep_tts_tabs.py --voice Aoede --port 9222 --count 1   # テスト
"""
import argparse
import json
import os
import re
import sys
import time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

URL = "https://aistudio.google.com/generate-speech?model=gemini-2.5-pro-preview-tts"

# 1タブあたり最大リトライ回数（AI Studioの一時エラー対策）
MAX_RETRY = 3
# タブ生成の間隔（秒）。連続生成でGoogle側がエラーを返すのを緩和
GAP_SEC = 1.5

# ログイン中アカウント名のキャッシュ（メニュー表示用・このスクリプトと同フォルダ）
CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "account_names.json")

# 右上の Google アカウントボタンを拾うセレクタ候補（英語UI / 日本語UI）
_ACCOUNT_SELECTORS = (
    'a[aria-label*="Google Account"]',
    'a[aria-label*="Google アカウント"]',
    '[aria-label*="Google Account"]',
    '[aria-label*="Google アカウント"]',
)


def detect_account_name(page):
    """開いているページの右上アカウントボタンからメアド/氏名を best-effort で読み取る。

    取得できなければ None。タブ準備の本筋を壊さないよう例外は握りつぶす。
    """
    for sel in _ACCOUNT_SELECTORS:
        try:
            label = page.locator(sel).first.get_attribute("aria-label", timeout=2000)
        except Exception:
            continue
        if not label:
            continue
        # まずメアド（ASCIIで安全）を優先
        m = re.search(r"[\w.+-]+@[\w.-]+\.\w+", label)
        if m:
            return m.group(0)
        # メアドが無ければ "Google Account: 氏名" の氏名部分
        m2 = re.search(r"(?:Google Account|Google アカウント)[:：]\s*(.+)", label)
        if m2:
            return m2.group(1).strip()
        return label.strip()
    return None


def update_account_cache(account: str, name: str):
    """account_names.json に {account: name} を 1 件マージ保存（UTF-8）。"""
    data = {}
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    data[account] = name
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _is_error_page(page) -> bool:
    """AI Studioが 'An unknown error occurred' を出していればTrue。"""
    try:
        err = page.get_by_text("An unknown error occurred")
        return err.is_visible(timeout=500)
    except Exception:
        return False


def _setup_page(page, voice: str):
    """1ページに対する設定操作。例外は呼び出し側で捕捉。"""
    # ページが操作可能になるまで要素ベースで待つ
    preset = page.get_by_role("button", name="The Energetic Co-Host -")
    preset.wait_for(state="visible", timeout=45000)
    preset.click()

    # Textトグル
    page.get_by_role("radio", name="Text").click()

    # Speaker1 の voice settings を開く
    page.locator("ms-voice-settings").filter(
        has_text="Speaker 1"
    ).get_by_label("Open voice settings").first.click()

    # 指定ボイスを選択
    voice_btn = page.get_by_role("button", name=voice, exact=True)
    voice_btn.wait_for(state="visible", timeout=15000)
    voice_btn.click()

    # パネルを閉じる
    page.keyboard.press("Escape")

    # Text欄を空にする
    box = page.get_by_role("textbox", name="Enter a prompt")
    box.click()
    box.press("ControlOrMeta+a")
    box.fill("")

    # ラベル反映を読み取り確認
    page.locator("ms-voice-settings").filter(
        has_text="Speaker 1"
    ).get_by_text(voice).first.wait_for(state="visible", timeout=5000)


def prep_one_tab(ctx, voice: str, idx: int, total: int) -> bool:
    """1タブを準備。AI Studioの一時エラー時はリロードして最大MAX_RETRY回試行。"""
    page = ctx.new_page()
    try:
        for attempt in range(1, MAX_RETRY + 1):
            try:
                page.goto(URL, wait_until="domcontentloaded")

                # ロード直後にエラーページが出ていたらリロードして再試行
                time.sleep(1.0)
                if _is_error_page(page):
                    print(f"  [retry] {voice} {idx}/{total}: AI Studio一時エラー (試行{attempt})")
                    page.reload(wait_until="domcontentloaded")
                    time.sleep(2.0)
                    if _is_error_page(page):
                        # まだエラーなら次のattemptへ（少し長めに待つ）
                        time.sleep(3.0)
                        continue

                _setup_page(page, voice)
                print(f"  [OK] {voice} {idx}/{total}")
                return True

            except (PWTimeout, Exception) as e:
                # エラーページ起因なら次のattemptで取り戻せることが多い
                if attempt < MAX_RETRY:
                    print(f"  [retry] {voice} {idx}/{total}: {type(e).__name__} (試行{attempt})")
                    time.sleep(2.0)
                    continue
                # 最終試行も失敗
                print(f"  [FAIL] {voice} {idx}/{total}: {type(e).__name__}: {e}")
                try:
                    page.screenshot(path=f"fail_{voice}_{idx}.png")
                    print(f"        -> screenshot: fail_{voice}_{idx}.png")
                except Exception:
                    pass
                return False
    finally:
        pass  # ページは開いたまま残す（タブとして使うため）

    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", required=True, help="ボイス名 (例: Aoede / Laomedeia)")
    ap.add_argument("--port", type=int, required=True, help="接続先Chromeのデバッグポート")
    ap.add_argument("--count", type=int, default=15, help="準備するタブ数 (default 15)")
    ap.add_argument("--account", default=None,
                    help="アカウントキー(acc1..acc5)。指定すると検知名を account_names.json にキャッシュ")
    args = ap.parse_args()

    cdp = f"http://127.0.0.1:{args.port}"
    fail = 0

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp)
        except Exception as e:
            print(f"ERROR: Chrome(CDP {cdp})に接続できません。")
            print(f"ポート{args.port}でChromeをデバッグ起動しているか確認してください。")
            print(f"詳細: {e}")
            sys.exit(1)

        ctx = browser.contexts[0]
        print(f"接続成功: ポート{args.port} / ボイス={args.voice} / {args.count}タブ")
        print("=" * 50)

        for i in range(1, args.count + 1):
            ok = prep_one_tab(ctx, args.voice, i, args.count)
            if not ok:
                fail += 1
            time.sleep(GAP_SEC)  # 連続生成の負荷を緩和

        # 準備済みタブから今ログイン中のアカウント名を best-effort 検知してキャッシュ。
        # （メニューの自動表示用。失敗してもタブ準備の結果には影響しない）
        if args.account:
            try:
                name = None
                for pg in reversed(ctx.pages):
                    name = detect_account_name(pg)
                    if name:
                        break
                if name:
                    update_account_cache(args.account, name)
                    print(f"  検知したアカウント: {args.account} = {name}")
                else:
                    print(f"  [info] アカウント名を検知できませんでした（{args.account} はキー表示のまま）")
            except Exception as e:
                print(f"  [info] アカウント検知をスキップ: {type(e).__name__}")

    print("=" * 50)
    print(f"完了: {args.voice} 全{args.count}タブ中 成功{args.count - fail} / 失敗{fail}")
    if fail:
        print("  失敗タブのスクショ: fail_<voice>_<n>.png を確認してください")


if __name__ == "__main__":
    main()
