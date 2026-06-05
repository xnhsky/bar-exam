# tts/ — Gemini TTS 音声生成

JX パイプラインが生成した**音声台本（.txt）を実音声（.wav）に変換**する最終段。

## 構成

| パス | 役割 |
|---|---|
| `generate_tts.py` | Gemini TTS 本体（model=`gemini-2.5-pro-preview-tts` / voice=`Laomedeia`） |
| `run-tts.ps1` | UTF-8 設定 + APIキー確認 + python 起動の薄いラッパ |
| `input_texts/` | 入力 `*.txt`（gitignore 対象） |
| `output_audio/` | 出力 `*.wav` 24kHz/16bit/モノラル（gitignore 対象） |

関連（リポジトリ側）:
- `scripts/tts-stage-inputs.ps1` … `outputs/tts/{ID}/*.txt` を `input_texts/` へ集約する橋渡し

## APIキー（直書き禁止）

環境変数 `GEMINI_API_KEY` から読む。

```powershell
# このセッションだけ
$env:GEMINI_API_KEY = "your-key"
# 永続（要ターミナル再起動）
setx GEMINI_API_KEY "your-key"
```

## 使い方

```powershell
# 1) JX パイプラインの台本を入力フォルダへ集約（既に wav 済みはスキップ）
pwsh -NoProfile -File scripts\tts-stage-inputs.ps1 -ProblemId 刑JX032

# 2) 音声生成（まず 1 件で試すなら -DailyLimit 1）
pwsh -NoProfile -File tts\run-tts.ps1 -DailyLimit 1

# 1)+2) を一気に
pwsh -NoProfile -File scripts\tts-stage-inputs.ps1 -ProblemId 刑JX032 -Run
```

## 仕様メモ

- 台本先頭に演技指示 `STYLE_PROMPT` を付与し、本文は「」で囲んで渡す（指示文は読ませない）
- パスは `__file__` 基準（起動場所に依存しない）
- 既存 wav はスキップ / API 失敗時は最大 3 回リトライ
- 生成後にサイズ・長さの異常を検査するが、**やり直さず・削除せず**警告記録のみ。
  実行末尾に「要確認ファイル一覧」を表示するだけ
- 件数/待機は環境変数 `TTS_DAILY_LIMIT`（既定 14）/ `TTS_SLEEP_TIME`（既定 6 秒）で調整可

## 依存

```powershell
python -m pip install google-genai
```
