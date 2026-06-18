# -*- coding: utf-8 -*-
r"""
generate_tts.py - Gemini TTS 音声生成（bar-exam JX 音声台本 → wav）

入力 : tts/input_texts/*.txt   （音声台本。JX パイプラインの outputs/002_TTS/{ID}/*.txt を集約したもの）
出力 : tts/output_audio/*.wav  （24kHz / 16bit / モノラル。入力と同じ stem）

仕様:
  - google-genai SDK / model='gemini-2.5-pro-preview-tts' / voice='Laomedeia'
  - 台本の先頭に演技指示 STYLE_PROMPT を付け、本文は「」で囲んで渡す（指示文は読ませない）
  - パスはすべて __file__ 基準（どこから起動しても同じ場所を見る）
  - API キーは環境変数 GEMINI_API_KEY から取得（直書き禁止）
  - 既存 wav はスキップ / API 失敗時は最大 3 回リトライ
  - 生成後にサイズ・長さの異常チェック。ただし「やり直さず・削除せず」、
    警告として記録し、最後に要確認ファイル一覧を表示するだけ

使い方（PowerShell ラッパ経由を推奨）:
  pwsh -NoProfile -File tts\run-tts.ps1
直接実行する場合:
  $env:GEMINI_API_KEY = "..."; python tts\generate_tts.py
"""
import os
import sys
import time
import wave  # WAV 形式の「表紙」をつけて保存するための道具
from pathlib import Path

# Windows コンソール（cp932）で日本語 print が落ちないよう UTF-8 化
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from google import genai
from google.genai import types

# === 設定部分 ===
# API キーは環境変数から読む（直書き禁止）。未設定なら即座に終了。
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: 環境変数 GEMINI_API_KEY が設定されていません。", file=sys.stderr)
    print("  PowerShell 例:  $env:GEMINI_API_KEY = \"your-key\"; python tts\\generate_tts.py", file=sys.stderr)
    print("  （推奨）        pwsh -NoProfile -File tts\\run-tts.ps1", file=sys.stderr)
    sys.exit(2)

client = genai.Client(api_key=API_KEY)

# パスはスクリプトの場所（__file__）基準で固定
SCRIPT_DIR = Path(__file__).resolve().parent
input_dir = SCRIPT_DIR / "input_texts"
output_dir = SCRIPT_DIR / "output_audio"
output_dir.mkdir(exist_ok=True)

# 処理件数と待機時間の設定（環境変数で上書き可）
DAILY_LIMIT = int(os.environ.get("TTS_DAILY_LIMIT", "14"))  # まず 1 件で試すなら 1 に下げる
SLEEP_TIME = int(os.environ.get("TTS_SLEEP_TIME", "6"))     # 連続呼び出し間の待機（秒）

# 使用モデル（環境変数 TTS_MODEL で上書き可）。
# 既定は本番品質の Pro TTS（要・課金有効プロジェクト。無料枠は上限0で 429 になる）。
# 無料枠での検証時は TTS_MODEL=gemini-2.5-flash-preview-tts を指定する。
TTS_MODEL = os.environ.get("TTS_MODEL", "gemini-2.5-pro-preview-tts")

# WAV フォーマット（Gemini TTS 出力基準）
WAV_CHANNELS = 1       # モノラル
WAV_SAMPWIDTH = 2      # 16bit
WAV_FRAMERATE = 24000  # 24kHz

# 読み方の演技指示（全ファイルの先頭に自動で付く）。本文は「」の中だけ読ませる。
STYLE_PROMPT = (
    "明るく元気いっぱい、ハイテンションな女性の声で、弾むように読み上げてください。"
    "読み上げる本文は次の「」の中だけです。指示文は読まないでください。"
)

# === チェック機能の設定 ===
LONG_TEXT_WARN = 4200  # この文字数を超えたら「長め」警告（終盤の乱れ予防の目安）
MIN_WAV_BYTES = 2000   # これ未満の wav は生成失敗とみなす
CHARS_PER_SEC = 6      # 日本語のおおよその読み上げ速度（字/秒）
SHORT_RATIO = 0.3      # 想定時間のこの割合より短ければ「短すぎ」
LONG_RATIO = 3.0       # 想定時間のこの倍率より長ければ「長すぎ」

MAX_RETRIES = 3        # API 失敗時のリトライ回数
RETRY_WAIT = 30        # リトライ間の待機（秒）


def check_audio(path, text):
    """生成された音声が異常なら理由の文字列を、正常なら None を返す。"""
    size = path.stat().st_size
    if size < MIN_WAV_BYTES:
        return f"ファイルが小さすぎます({size}バイト)"

    with wave.open(str(path), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
    duration = frames / rate if rate else 0

    expected = max(1.0, len(text) / CHARS_PER_SEC)
    if duration < expected * SHORT_RATIO:
        return f"音声が短すぎます({duration:.1f}秒/想定{expected:.0f}秒・途中で切れた可能性)"
    if duration > expected * LONG_RATIO:
        return f"音声が長すぎます({duration:.1f}秒/想定{expected:.0f}秒・暴走の可能性)"
    return None


def main():
    if not input_dir.is_dir():
        print(f"ERROR: 入力フォルダがありません: {input_dir}", file=sys.stderr)
        return 2

    text_files = sorted(input_dir.glob("*.txt"))[:DAILY_LIMIT]
    total_files = len(text_files)
    print(f"入力フォルダ: {input_dir}")
    print(f"出力フォルダ: {output_dir}")
    print(f"使用モデル: {TTS_MODEL}")
    print(f"合計 {total_files} 件のファイルを処理します。（DAILY_LIMIT={DAILY_LIMIT}）")

    # 警告が出たファイルを記録するリスト（最後にまとめて表示）
    warnings = []

    for index, text_file in enumerate(text_files, start=1):
        output_filename = output_dir / f"{text_file.stem}.wav"

        # 既に音声ファイルが存在する場合はスキップ（重複課金防止）
        if output_filename.exists():
            print(f"[{index}/{total_files}] {output_filename.name} は既に存在するためスキップします。")
            continue

        print(f"[{index}/{total_files}] {text_file.name} を音声化しています...")

        text_content = text_file.read_text(encoding="utf-8-sig")

        # ① 長い台本の警告（記録のみ・やり直しはしない）
        if len(text_content) > LONG_TEXT_WARN:
            msg = f"台本が長め({len(text_content)}字)"
            print(f"  ⚠ 注意: {msg}。終盤で声が乱れる場合は分割をおすすめします。")
            warnings.append((text_file.name, msg))

        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=TTS_MODEL,
                    contents=STYLE_PROMPT + "\n\n「" + text_content + "」",
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="Laomedeia"
                                )
                            )
                        ),
                    ),
                )

                # 中身が空（テキストだけ返る等）の場合は break せず、例外でリトライに回す
                if (response.candidates
                        and response.candidates[0].content
                        and response.candidates[0].content.parts):
                    audio_data = response.candidates[0].content.parts[0].inline_data.data

                    # 生の音声データに WAV ヘッダをつけて保存（24kHz/16bit/モノラル）
                    with wave.open(str(output_filename), "wb") as wf:
                        wf.setnchannels(WAV_CHANNELS)
                        wf.setsampwidth(WAV_SAMPWIDTH)
                        wf.setframerate(WAV_FRAMERATE)
                        wf.writeframes(audio_data)

                    # ② 生成物の異常チェック（やり直さず・削除せず、警告記録のみ）
                    problem = check_audio(output_filename, text_content)
                    if problem:
                        print(f"  -> 保存完了（⚠ 要確認: {problem}）: {output_filename.name}")
                        warnings.append((output_filename.name, problem))
                    else:
                        print(f"  -> 保存完了: {output_filename.name}")
                    break
                else:
                    print("  -> 音声データが空でした。再試行します...")
                    raise ValueError("empty audio response")

            except Exception as e:
                print(f"  -> エラー発生 (試行 {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    print(f"  -> {RETRY_WAIT}秒待機して再試行します...")
                    time.sleep(RETRY_WAIT)
                else:
                    print(f"  -> {text_file.name} の処理をスキップします。")

        # 次のファイルへ行く前に待機する
        time.sleep(SLEEP_TIME)

    print("\n本日のバッチ処理がすべて完了しました！")

    # === 警告が出たファイルの一覧をまとめて表示（要確認リスト） ===
    print("\n" + "=" * 40)
    if warnings:
        print(f"⚠ 要確認のファイルが {len(warnings)} 件あります：")
        for name, reason in warnings:
            print(f"  - {name} … {reason}")
        print("（音声は生成済みです。削除せず残しています。念のため聞いて確認してください）")
    else:
        print("✓ 警告が出たファイルはありませんでした。")
    print("=" * 40)
    return 0


if __name__ == "__main__":
    sys.exit(main())
