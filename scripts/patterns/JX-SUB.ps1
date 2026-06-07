# JX-SUB — JX 一気通貫パターン②（JX HTML → TTS 台本 まで）
#
# JX-MAIN と同一スコープ（① JX → ② validate-jx → ③ TTS 台本 → ④ validate-tts → ⑥ 配置）。
# 二台運用で番号帯を分けて並行実行するための「第2レーン」として残す。
#
# ※ 音声生成（⑤ Gemini API / AI Studio）は行わない（2026-06-06 方針変更）。
#    音声は台本から AI Studio で手動生成する。鍵（main/sub）・Pro/Flash の指定はもう存在しない。
#
# 使い方:
#   pwsh -NoProfile -File scripts/patterns/JX-SUB.ps1                  # 刑・3問・台本まで
#   pwsh -NoProfile -File scripts/patterns/JX-SUB.ps1 -Subject 商 -MaxProblems 3
#   pwsh -NoProfile -File scripts/patterns/JX-SUB.ps1 -FromNumber 28 -ToNumber 30   # 28〜30 だけ
#   pwsh -NoProfile -File scripts/patterns/JX-SUB.ps1 -DryRun
param(
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '刑',
    [int]$MaxProblems = 3,
    [int]$Number = 0,           # 単一番号（指定時は From/To をこの番号に固定・MaxProblems=1）
    [int]$FromNumber = 0,       # 任意レンジの下限
    [int]$ToNumber = 0,         # 任意レンジの上限
    [switch]$DryRun
)
if ($Number -gt 0) { $FromNumber = $Number; $ToNumber = $Number; $MaxProblems = 1 }
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Runner = Join-Path $ProjectRoot 'scripts\jx-batch-runner.ps1'

# 音声(⑤)は本パターンでは行わない。-SkipAudio で台本集約まで（音声は AI Studio で手動）。
$params = @{ Subject = $Subject; MaxProblems = $MaxProblems; SkipAudio = $true }
if ($FromNumber -gt 0) { $params.FromNumber = $FromNumber }
if ($ToNumber   -gt 0) { $params.ToNumber   = $ToNumber }
if ($DryRun)    { $params.DryRun = $true }

$rangeText = if ($FromNumber -gt 0 -or $ToNumber -gt 0) { "・範囲 $FromNumber〜$ToNumber" } else { "" }
Write-Host "[JX-SUB] JX→台本まで（音声は AI Studio で手動）・$Subject・最大 $MaxProblems 問$rangeText" -ForegroundColor Cyan
& $Runner @params
exit $LASTEXITCODE
