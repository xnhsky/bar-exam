# JX-MAIN — JX 一気通貫パターン①（JX HTML → TTS 台本 まで・既定 3 問ずつ）
#
# 何をするか: inputs/jx/{科目} の最若番から MaxProblems 問を
#   ① JX HTML 生成 → ② validate-jx → ③ TTS 台本 → ④ validate-tts → ⑥ 配置（Drive＋repoミラー）
# まで通す。
#
# ※ 音声生成（⑤ Gemini API / AI Studio）は本パターンでは行わない（2026-06-06 方針変更）。
#    音声は台本（outputs/tts/{問題ID}/ ＝ 配置先 TTSファイル原本\）から AI Studio で手動生成する。
#    そのため鍵（main/sub）・Pro/Flash の指定はもう存在しない。
#
# 使い方:
#   pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1                 # 刑・3問・台本まで
#   pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1 -Subject 民 -MaxProblems 3
#   pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1 -DryRun         # 検出のみ
#   pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1 -FromNumber 25 -ToNumber 27   # 25〜27 だけ（catch-up）
#   pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1 -Number 25      # 25 を1問だけ
param(
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '刑',
    [int]$MaxProblems = 3,
    [int]$Number = 0,           # 単一番号（指定時は From/To をこの番号に固定・MaxProblems=1）
    [int]$FromNumber = 0,       # 任意レンジの下限（最若番優先の既定に対し特定番号帯のみ対象に）
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
Write-Host "[JX-MAIN] JX→台本まで（音声は AI Studio で手動）・$Subject・最大 $MaxProblems 問$rangeText" -ForegroundColor Cyan
& $Runner @params
exit $LASTEXITCODE
