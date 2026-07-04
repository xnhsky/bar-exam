# JX — 【廃止・2026-07-04】TJR に統合。本ファイルは後方互換の転送スタブ。
# 旧：inputs/001_JX/{科目} 最若番から N 問を JX→台本まで生成。
# 現：TJR の J ストリーム（JX＋副産物 RX/TREE/ARIADNE＋台本）へ転送。今後は「TJR処理 {科目}」or「JX {N}-{M} 処理」。
param(
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '刑',
    [int]$MaxProblems = 3,
    [int]$Number = 0,
    [int]$FromNumber = 0,
    [int]$ToNumber = 0,
    [switch]$NoPush,
    [string]$ProjectRoot = '',
    [switch]$DryRun
)
if ($Number -gt 0) { $FromNumber = $Number; $ToNumber = $Number }
Write-Host "[DEPRECATED] JX パターンは廃止。TJR の J ストリームへ転送します。" -ForegroundColor Yellow
$TJR = Join-Path $PSScriptRoot 'TJR.ps1'
$useRange = ($FromNumber -gt 0 -or $ToNumber -gt 0)
$p = @{ Subject = $Subject; Only = 'J'; MaxJX = $MaxProblems }
if ($useRange)    { $p.JxFrom = $FromNumber; $p.JxTo = $ToNumber }
if ($NoPush)      { $p.NoPush = $true }
if ($ProjectRoot) { $p.ProjectRoot = $ProjectRoot }
if ($DryRun)      { $p.DryRun = $true }
& $TJR @p
exit $LASTEXITCODE
