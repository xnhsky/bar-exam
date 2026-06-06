# JX-SUB — JX 一気通貫パターン②（サブ鍵）
#
# JX-MAIN と同じ一気通貫だが、鍵は .secrets/gemini_sub.key を使う。
# 既定の音声モデルは無料の Flash（サブ鍵が無料枠想定のため）。
# サブ鍵が課金有効（Pro 可）なら -TtsModel '' を渡すと Pro になる。
#
# 使い方:
#   pwsh -NoProfile -File scripts/patterns/JX-SUB.ps1                  # 刑・3問・Flash音声(無料)
#   pwsh -NoProfile -File scripts/patterns/JX-SUB.ps1 -Subject 商 -MaxProblems 3
#   pwsh -NoProfile -File scripts/patterns/JX-SUB.ps1 -TtsModel ''     # サブ鍵が課金可なら Pro 音声に
#   pwsh -NoProfile -File scripts/patterns/JX-SUB.ps1 -DryRun
param(
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '刑',
    [int]$MaxProblems = 3,
    [string]$TtsModel = 'gemini-2.5-flash-preview-tts',  # 既定=無料 Flash（'' で generate_tts 既定=Pro）
    [switch]$SkipAudio,
    [switch]$DryRun
)
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Runner = Join-Path $ProjectRoot 'scripts\jx-batch-runner.ps1'

$params = @{ Subject = $Subject; MaxProblems = $MaxProblems; KeyName = 'sub'; TtsModel = $TtsModel }
if ($SkipAudio) { $params.SkipAudio = $true }
if ($DryRun)    { $params.DryRun = $true }

$modelLabel = if ($TtsModel) { $TtsModel } else { 'generate_tts 既定(Pro)' }
Write-Host "[JX-SUB] サブ鍵・音声=$modelLabel・$Subject・最大 $MaxProblems 問" -ForegroundColor Cyan
& $Runner @params
exit $LASTEXITCODE
