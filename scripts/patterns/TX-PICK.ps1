# TX-PICK — 【廃止・2026-07-04】TJR に統合。本ファイルは後方互換の転送スタブ。
# 旧：指定番号/範囲の TX を night-batch-runner(v10) で生成。
# 現：TJR の短縮形 TX ストリーム（v13 二系統）へ転送。今後は「TX {N}-{M} 処理」を使うこと。
param(
    [int]$Number = 0,
    [int]$FromNumber = 0,
    [int]$ToNumber = 0,
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '刑',
    [string]$ProjectRoot = '',
    [switch]$DryRun
)
if ($Number -gt 0) { $FromNumber = $Number; $ToNumber = $Number }
if ($FromNumber -le 0 -and $ToNumber -le 0) {
    Write-Host "[TX-PICK] -Number か -FromNumber/-ToNumber を指定してください。" -ForegroundColor Red; exit 1
}
Write-Host "[DEPRECATED] TX-PICK は廃止。TJR の TX ストリームへ転送します（現行 v13 二系統）。" -ForegroundColor Yellow
$TJR = Join-Path $PSScriptRoot 'TJR.ps1'
$p = @{ Subject = $Subject; Only = 'T'; TxFrom = $FromNumber; TxTo = $ToNumber }
if ($ProjectRoot) { $p.ProjectRoot = $ProjectRoot }
if ($DryRun)      { $p.DryRun = $true }
& $TJR @p
exit $LASTEXITCODE
