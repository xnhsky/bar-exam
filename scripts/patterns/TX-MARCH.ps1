# TX-MARCH — 【廃止・2026-07-04】TJR に統合。本ファイルは後方互換の転送スタブ。
# 旧：inputs/000_TX/001_刑法 最若番から N 問を night-batch-runner(v10) で生成。
# 現：TJR の T ストリーム（v13 二系統）へ転送する。今後は「TJR処理 {科目}」を使うこと。
param(
    [int]$MaxProblems = 5,
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '刑',
    [string]$ProjectRoot = '',
    [switch]$DryRun
)
Write-Host "[DEPRECATED] TX-MARCH は廃止。TJR の T ストリームへ転送します（現行 v13 二系統）。" -ForegroundColor Yellow
$TJR = Join-Path $PSScriptRoot 'TJR.ps1'
$p = @{ Subject = $Subject; Only = 'T'; MaxTX = $MaxProblems }
if ($ProjectRoot) { $p.ProjectRoot = $ProjectRoot }
if ($DryRun)      { $p.DryRun = $true }
& $TJR @p
exit $LASTEXITCODE
