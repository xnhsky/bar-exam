# run-tts.ps1
#
# generate_tts.py の薄い起動ラッパ。
#   - コンソールを UTF-8 化（日本語 print 文字化け防止）
#   - GEMINI_API_KEY の存在を確認（無ければ中断・キーは直書きしない）
#   - python generate_tts.py を __file__ 基準で起動
#
# 実行例:
#   pwsh -NoProfile -File tts\run-tts.ps1
#   pwsh -NoProfile -File tts\run-tts.ps1 -DailyLimit 1   # まず 1 件だけ試す
#
# API キーの渡し方（いずれか）:
#   1) 事前に  $env:GEMINI_API_KEY = "your-key"  を設定してから本スクリプトを実行
#   2) ユーザー環境変数に GEMINI_API_KEY を永続設定（setx GEMINI_API_KEY "your-key" / 要再起動）

param(
    [int]$DailyLimit = 0,   # 0 = generate_tts.py の既定（14）を使用。1 以上で上書き
    [int]$SleepTime  = 0    # 0 = 既定（6 秒）。1 以上で上書き
)

# === stdout/stderr UTF-8 化 ===
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

# === パス定義（スクリプト自身の位置基準）===
$TtsDir    = $PSScriptRoot
$PyScript  = Join-Path $TtsDir "generate_tts.py"
$InputDir  = Join-Path $TtsDir "input_texts"
$OutputDir = Join-Path $TtsDir "output_audio"

if (-not (Test-Path $PyScript)) {
    Write-Host "[ABORT] generate_tts.py が見つかりません: $PyScript" -ForegroundColor Red
    exit 1
}

# === API キー確認（直書きしない・存在のみチェック）===
if ([string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY)) {
    Write-Host "[ABORT] 環境変数 GEMINI_API_KEY が未設定です。" -ForegroundColor Red
    Write-Host '  このセッションだけ設定する例:' -ForegroundColor Yellow
    Write-Host '    $env:GEMINI_API_KEY = "your-key"' -ForegroundColor Yellow
    Write-Host '  永続設定する例（要ターミナル再起動）:' -ForegroundColor Yellow
    Write-Host '    setx GEMINI_API_KEY "your-key"' -ForegroundColor Yellow
    exit 1
}

# === 入出力フォルダ確保 ===
if (-not (Test-Path $InputDir))  { New-Item -Path $InputDir  -ItemType Directory -Force | Out-Null }
if (-not (Test-Path $OutputDir)) { New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null }

$txtCount = @(Get-ChildItem -Path $InputDir -Filter "*.txt" -File -ErrorAction SilentlyContinue).Count
Write-Host "=== run-tts 開始 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "入力: $InputDir  (*.txt $txtCount 件)"
Write-Host "出力: $OutputDir"
if ($txtCount -eq 0) {
    Write-Host "[INFO] input_texts に *.txt がありません。tts-stage-inputs.ps1 で台本を集約してください。" -ForegroundColor Yellow
}

# === 件数・待機の上書き（指定時のみ）===
if ($DailyLimit -gt 0) { $env:TTS_DAILY_LIMIT = "$DailyLimit"; Write-Host "DAILY_LIMIT 上書き: $DailyLimit" }
if ($SleepTime  -gt 0) { $env:TTS_SLEEP_TIME  = "$SleepTime";  Write-Host "SLEEP_TIME 上書き: $SleepTime" }

# === 起動（python。python3 ではない）===
& python $PyScript
$code = $LASTEXITCODE

Write-Host "`n=== run-tts 終了 (exit=$code) $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
exit $code
