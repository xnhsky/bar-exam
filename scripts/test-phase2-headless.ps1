# test-phase2-headless.ps1
#
# Phase 2-A: headless プロンプト v0 の単発テスト実行（PROBLEM_ID 連動）。
# 本番夜間運用と同じく PowerShell から `claude -p` を直叩きする。
#
# 実行例：
#   pwsh -File scripts/test-phase2-headless.ps1
# または PowerShell プロンプトから：
#   .\scripts\test-phase2-headless.ps1
#
# 終了後、Claude Code を再起動して claude.ai で「Phase 2-C 進めて」を指示する。

# ---- 設定（テスト用固定値） ---------------------------------------------------

$ProjectRoot = "C:\Users\OWNER\bar-exam"

$PromptSource = Join-Path $ProjectRoot "prompts\new-tx-headless-v0.md"
$LogsDir      = Join-Path $ProjectRoot "logs"
$PromptOut    = Join-Path $LogsDir    "test-phase2-prompt.txt"

# 変数置換（テスト用に事前固定）
$Vars = @{
    'TARGET_PDF'     = 'C:\Users\OWNER\bar-exam\inputs\tx-pdfs\306.pdf'
    'PROBLEM_NUMBER' = '306'
    'PROBLEM_ID'     = '刑TX306'
    'OUTPUT_PATH'    = 'C:\Users\OWNER\bar-exam\outputs\tx\刑TX\刑TX306.html'
}

$JsonOut      = Join-Path $LogsDir    "test-$($Vars['PROBLEM_ID']).json"
$TimingOut    = Join-Path $LogsDir    "test-$($Vars['PROBLEM_ID']).timing.txt"

$ExpectedHtml = $Vars['OUTPUT_PATH']

# ---- 1) プロジェクトルートに cd ----------------------------------------------

if (-not (Test-Path $ProjectRoot)) {
    Write-Error "Project root not found: $ProjectRoot"
    exit 1
}
Set-Location $ProjectRoot
Write-Host "[INFO] cwd = $((Get-Location).Path)"

# ---- 2) エラーハンドリング：claude コマンド存在確認 --------------------------

$claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claudeCmd) {
    Write-Error "[FATAL] 'claude' command not found in PATH. Aborting."
    exit 1
}
Write-Host "[INFO] claude CLI: $($claudeCmd.Source)"

# ---- 3) エラーハンドリング：プロンプトファイル読込 ---------------------------

if (-not (Test-Path $PromptSource)) {
    Write-Error "[FATAL] Prompt file not found: $PromptSource"
    exit 1
}

try {
    $rawPrompt = Get-Content -Path $PromptSource -Raw -Encoding UTF8 -ErrorAction Stop
} catch {
    Write-Error "[FATAL] Failed to read prompt file: $_"
    exit 1
}
Write-Host "[INFO] Loaded prompt: $PromptSource ($($rawPrompt.Length) chars)"

# ---- 4) エラーハンドリング：logs/ ディレクトリ作成 ---------------------------

if (-not (Test-Path $LogsDir)) {
    try {
        New-Item -ItemType Directory -Path $LogsDir -ErrorAction Stop | Out-Null
        Write-Host "[INFO] Created logs dir: $LogsDir"
    } catch {
        Write-Error "[FATAL] Cannot create logs dir '$LogsDir': $_"
        exit 1
    }
}

# ---- 5) 変数置換 -------------------------------------------------------------

$promptResolved = $rawPrompt
foreach ($k in $Vars.Keys) {
    $placeholder = '{' + $k + '}'
    $promptResolved = $promptResolved.Replace($placeholder, $Vars[$k])
}

# 置換後プロンプトを保存（デバッグ用）
try {
    Set-Content -Path $PromptOut -Value $promptResolved -Encoding UTF8 -NoNewline -ErrorAction Stop
    Write-Host "[INFO] Resolved prompt saved: $PromptOut"
} catch {
    Write-Error "[FATAL] Failed to write resolved prompt to '$PromptOut': $_"
    exit 1
}

# ---- 6) claude -p 呼び出し ---------------------------------------------------

Write-Host ""
Write-Host "[INFO] Invoking 'claude -p' (this may take several minutes)..."
Write-Host "[INFO] Output JSON: $JsonOut"
Write-Host ""

$startedAt = Get-Date
$startStr  = $startedAt.ToString("yyyy-MM-dd HH:mm:ss")

# stdin から置換済みプロンプトを流し込み、全出力を JSON ログへ
Get-Content $PromptOut -Raw | claude -p `
    --output-format json `
    --allowedTools "Read,Write,Edit,Bash,Glob,Grep" `
    --permission-mode acceptEdits `
    --verbose `
    *> $JsonOut

$exitCode = $LASTEXITCODE
$endedAt  = Get-Date
$endStr   = $endedAt.ToString("yyyy-MM-dd HH:mm:ss")
$elapsed  = $endedAt - $startedAt

# ---- 7) timing ログ保存 ------------------------------------------------------

$timingLines = @(
    "started_at: $startStr"
    "ended_at:   $endStr"
    "elapsed_sec: $([math]::Round($elapsed.TotalSeconds, 2))"
    "elapsed_min: $([math]::Round($elapsed.TotalMinutes, 2))"
    "claude_exit_code: $exitCode"
)
Set-Content -Path $TimingOut -Value $timingLines -Encoding UTF8

# ---- 8) exit code 非 0 の警告（停止はしない） --------------------------------

if ($exitCode -ne 0) {
    Write-Warning "[WARN] claude -p exited with non-zero code: $exitCode (logs preserved)"
}

# ---- 9) 画面表示（末尾サマリー） ---------------------------------------------

$htmlExists = Test-Path $ExpectedHtml

Write-Host ""
Write-Host "============================================================"
Write-Host " Phase 2-A test run finished"
Write-Host "============================================================"
Write-Host (" elapsed     : {0} min ({1} sec)" -f [math]::Round($elapsed.TotalMinutes, 2), [math]::Round($elapsed.TotalSeconds, 2))
Write-Host (" exit code   : {0}" -f $exitCode)
Write-Host (" prompt log  : {0}" -f $PromptOut)
Write-Host (" json log    : {0}" -f $JsonOut)
Write-Host (" timing log  : {0}" -f $TimingOut)
Write-Host (" output html : {0} ({1})" -f $ExpectedHtml, $(if ($htmlExists) { "EXISTS" } else { "MISSING" }))
Write-Host "============================================================"
Write-Host ""
Write-Host 'Next: Claude Code を再起動して `Phase 2-C 進めて` の指示を出してください'
Write-Host ""
