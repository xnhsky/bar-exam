# TX-MARCH — TX 連番 NBR パターン①（最若番から順に生成）
#
# inputs/000_TX/001_刑法 の未生成 PDF を最若番から MaxProblems 問、GENESIS 経路で
# 生成→validate-tx-core→各問 commit/push（night-batch-runner の既定動線）。
#
# 使い方:
#   pwsh -NoProfile -File scripts/patterns/TX-MARCH.ps1                # 最若番から5問
#   pwsh -NoProfile -File scripts/patterns/TX-MARCH.ps1 -MaxProblems 3
#   pwsh -NoProfile -File scripts/patterns/TX-MARCH.ps1 -DryRun        # 検出のみ
param(
    [int]$MaxProblems = 5,
    [switch]$DryRun
)
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Runner = Join-Path $ProjectRoot 'scripts\night-batch-runner.ps1'

$params = @{ MaxProblems = $MaxProblems }
if ($DryRun) { $params.DryRun = $true }

Write-Host "[TX-MARCH] 連番NBR・最若番から最大 $MaxProblems 問" -ForegroundColor Cyan
& $Runner @params
exit $LASTEXITCODE
