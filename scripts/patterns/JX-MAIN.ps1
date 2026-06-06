# JX-MAIN — JX 一気通貫パターン①（メイン鍵・Pro 音声・既定 3 問ずつ）
#
# 何をするか: inputs/jx/{科目} の最若番から MaxProblems 問を
#   ① JX HTML 生成 → ② validate-jx → ③ TTS 台本 → ④ validate-tts → ⑤ Pro 音声(wav)
# まで一気通貫。鍵は .secrets/gemini_main.key を自動読込（git 管理外）。
#
# 使い方:
#   pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1                 # 刑・3問・Pro音声
#   pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1 -Subject 民 -MaxProblems 3
#   pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1 -DryRun         # 検出のみ（無課金）
#   pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1 -SkipAudio      # ④まで（音声スキップ）
param(
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '刑',
    [int]$MaxProblems = 3,
    [switch]$SkipAudio,
    [switch]$DryRun
)
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Runner = Join-Path $ProjectRoot 'scripts\jx-batch-runner.ps1'

$params = @{ Subject = $Subject; MaxProblems = $MaxProblems; KeyName = 'main' }
if ($SkipAudio) { $params.SkipAudio = $true }
if ($DryRun)    { $params.DryRun = $true }

Write-Host "[JX-MAIN] メイン鍵・Pro音声・$Subject・最大 $MaxProblems 問" -ForegroundColor Cyan
& $Runner @params
exit $LASTEXITCODE
