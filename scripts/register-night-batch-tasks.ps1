# register-night-batch-tasks.ps1 —【非推奨・TJR へ転送するスタブ】
#
# 旧 v10 night-batch-runner.ps1 を登録するスクリプトだったが、TX 生成は v13 二系統の
# tx-v13-runner（号令 TJR＝scripts\patterns\TJR.ps1）へ移行済み（CLAUDE.md §6-2・引退）。
# 本スクリプトは後方互換のため残置し、呼び出しを新 register-tjr-night-task.ps1 へ転送する。
# 旧引数は次のように写像する：
#   -FromNumber/-ToNumber → T（新規TX）の番号帯 -TxFrom/-TxTo
#   -MaxProblems          → -MaxTX（T の1起動チャンク）
#   -Times/-ProjectRoot/-Unregister はそのまま透過
# 新規に組む場合は register-tjr-night-task.ps1 を直接使うこと（R/J のピンや -Only に対応）。

param(
    [string]$TaskName    = 'BarExam-Night-TJR',   # 既定を TJR タスク名へ（旧 BarExam-NightBatch-TX は掃除される）
    [int]$FromNumber     = 0,
    [int]$ToNumber       = 0,
    [int]$MaxProblems    = 12,
    [string[]]$Times     = @('21:00','23:00','01:00','03:00','05:00'),
    [string]$ProjectRoot = '',
    [switch]$Unregister
)

$ErrorActionPreference = 'Stop'
Write-Host "[DEPRECATED] register-night-batch-tasks.ps1 は TJR へ移行しました。register-tjr-night-task.ps1 へ転送します。" -ForegroundColor Yellow

$Target = Join-Path $PSScriptRoot 'register-tjr-night-task.ps1'
if (-not (Test-Path $Target)) { throw "転送先が見つかりません: $Target" }

# 旧引数 → TJR 引数へ写像
$fwd = @{ TaskName = $TaskName; Times = $Times; MaxTX = $MaxProblems }
if ($FromNumber -gt 0) { $fwd['TxFrom'] = $FromNumber }
if ($ToNumber   -gt 0) { $fwd['TxTo']   = $ToNumber }
if (-not [string]::IsNullOrWhiteSpace($ProjectRoot)) { $fwd['ProjectRoot'] = $ProjectRoot }
if ($Unregister) { $fwd['Unregister'] = $true }

& $Target @fwd
