# TX-PICK — TX 任意指定 NBR パターン②（番号/範囲をピンポイント生成）
#
# 単一番号 -Number N、または範囲 -FromNumber A -ToNumber B を GENESIS 経路で生成。
# 内部は night-batch-runner の -FromNumber/-ToNumber/-MaxProblems を使う。
#
# 使い方:
#   pwsh -NoProfile -File scripts/patterns/TX-PICK.ps1 -Number 366          # 366 を1問（既定 v10）
#   pwsh -NoProfile -File scripts/patterns/TX-PICK.ps1 -FromNumber 366 -ToNumber 370   # 366〜370
#   pwsh -NoProfile -File scripts/patterns/TX-PICK.ps1 -Number 366 -DryRun
#   pwsh -NoProfile -File scripts/patterns/TX-PICK.ps1 -FromNumber 55 -ToNumber 60 -SpecVersion v13   # 旧レイアウト_lex を v13 移行
param(
    [int]$Number = 0,         # 単一番号（指定時は From/To をこの番号に固定・MaxProblems=1）
    [int]$FromNumber = 0,
    [int]$ToNumber = 0,
    [int]$MaxProblems = 1,
    [string]$ProjectRoot = '',  # 別 clone/root で生成する場合に指定（未指定はこの repo）
    [ValidateSet('v13','v10.0.0','v9.2.0','v9.1.0')]
    [string]$SpecVersion = 'v10.0.0',   # v13＝旧レイアウト _lex を LOOP-CARD 二系統へ移行
    [ValidateSet('刑','刑訴','民','商','民訴','行政','憲')]
    [string]$Subject = '刑',            # 科目接頭辞（刑訴の新規生成は -Subject 刑訴 -SpecVersion v13）
    [switch]$DryRun
)
if ($Number -gt 0) { $FromNumber = $Number; $ToNumber = $Number; $MaxProblems = 1 }
if ($FromNumber -le 0 -and $ToNumber -le 0) {
    Write-Host "[TX-PICK] -Number か -FromNumber/-ToNumber を指定してください。" -ForegroundColor Red
    exit 1
}
$DefaultProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$Runner = Join-Path $ProjectRoot 'scripts\night-batch-runner.ps1'

$params = @{ FromNumber = $FromNumber; ToNumber = $ToNumber; MaxProblems = $MaxProblems; ProjectRoot = $ProjectRoot; SpecVersion = $SpecVersion; Subject = $Subject }
if ($DryRun) { $params.DryRun = $true }

Write-Host "[TX-PICK] $Subject・任意NBR・範囲 $FromNumber〜$ToNumber・最大 $MaxProblems 問・spec=$SpecVersion" -ForegroundColor Cyan
& $Runner @params
exit $LASTEXITCODE
