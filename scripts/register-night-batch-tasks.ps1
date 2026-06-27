# register-night-batch-tasks.ps1
#
# night-batch-runner.ps1 を Windows タスクスケジューラへ登録する。
# 既定では 21:00 / 23:00 / 01:00 / 03:00 / 05:00 の 5 トリガー（2 時間間隔・夜間分割生成）を
# 1 つのタスクにまとめて登録する。各起動は指定レンジの未生成 PDF を最若番から MaxProblems 件処理する。
#
# 実行例:
#   # 326〜345 を 1 起動 5 問で夜間分割生成（5 回 ×5 = 25 枠 ≥ 20 問）
#   pwsh -NoProfile -File scripts/register-night-batch-tasks.ps1 -FromNumber 326 -ToNumber 345
#
#   # レンジ無制限（従来の最若番優先・全未生成を順次）
#   pwsh -NoProfile -File scripts/register-night-batch-tasks.ps1
#
#   # 登録解除
#   pwsh -NoProfile -File scripts/register-night-batch-tasks.ps1 -Unregister
#
# 注意:
#   - claude CLI は実行ユーザーの認証情報（%USERPROFILE%\.claude）を使うため、
#     タスクは「現在のユーザーがログオン時のみ」実行する設定で登録する。
#   - スリープ中でも起動できるよう WakeToRun を有効化する。
#   - .ps1 は BOM 付き UTF-8 で保存すること（scripts/README.md 規律）。

param(
    [string]$TaskName    = 'BarExam-NightBatch-TX',
    [int]$FromNumber     = 0,           # 0 = 下限なし
    [int]$ToNumber       = 0,           # 0 = 上限なし
    [int]$MaxProblems    = 5,           # 1 起動あたり処理数
    [string[]]$Times     = @('21:00','23:00','01:00','03:00','05:00'),
    [string]$ProjectRoot = '',          # 別 clone/root で登録する場合に指定（未指定はこの repo）
    [switch]$Unregister
)

$ErrorActionPreference = 'Stop'

# === パス解決（マルチ PC / clone 分離対応）===
$DefaultProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$RunnerPath  = Join-Path $ProjectRoot 'scripts\night-batch-runner.ps1'
if (-not (Test-Path $RunnerPath)) { throw "runner not found: $RunnerPath" }

# === 登録解除モード ===
if ($Unregister) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "[OK] タスク '$TaskName' を登録解除しました。" -ForegroundColor Green
    } else {
        Write-Host "[INFO] タスク '$TaskName' は存在しません。" -ForegroundColor Yellow
    }
    return
}

# === pwsh 実行ファイルの解決 ===
$PwshExe = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
if (-not $PwshExe) { $PwshExe = (Get-Process -Id $PID).Path }  # フォールバック

# === 起動引数の組み立て ===
$argList = @(
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-File', "`"$RunnerPath`"",
    '-MaxProblems', $MaxProblems,
    '-ProjectRoot', "`"$ProjectRoot`""
)
if ($FromNumber -gt 0) { $argList += @('-FromNumber', $FromNumber) }
if ($ToNumber   -gt 0) { $argList += @('-ToNumber',   $ToNumber) }
$argString = $argList -join ' '

$Action = New-ScheduledTaskAction -Execute $PwshExe -Argument $argString -WorkingDirectory $ProjectRoot

# === 5 トリガー（各時刻の毎日起動）＋ 起動時トリガー ===
$Triggers = @(foreach ($t in $Times) { New-ScheduledTaskTrigger -Daily -At $t })
# 起動時トリガー（BSOD/再起動後の自動再開・DriveFS/ネットワーク準備待ちで 3 分遅延）
$startupTrigger = New-ScheduledTaskTrigger -AtStartup
$startupTrigger.Delay = 'PT3M'
$Triggers += $startupTrigger

# === 実行ユーザー（現在のユーザー・ログオン時のみ）===
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

# === タスク設定 ===
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -WakeToRun `
    -DontStopOnIdleEnd `
    -ExecutionTimeLimit (New-TimeSpan -Hours 4) `
    -MultipleInstances Queue `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

$rangeDesc = if ($FromNumber -gt 0 -or $ToNumber -gt 0) { "範囲 $FromNumber〜$ToNumber" } else { '無制限' }
$Description = "bar-exam NBR 夜間分割生成（$($Times -join ' / ')・起動時トリガー(遅延3分)含む・1 起動 $MaxProblems 問・$rangeDesc）"

# === 既存タスクがあれば置き換え ===
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "[INFO] 既存タスク '$TaskName' を置き換えます。" -ForegroundColor Yellow
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Triggers `
    -Principal $Principal `
    -Settings $Settings `
    -Description $Description | Out-Null

Write-Host "[OK] タスク '$TaskName' を登録しました。" -ForegroundColor Green
Write-Host "  実行: $PwshExe $argString"
Write-Host "  トリガー: $($Times -join ' / ')"
Write-Host "  対象範囲: $rangeDesc / 1 起動 $MaxProblems 問"
Write-Host ""
Write-Host "確認: Get-ScheduledTask -TaskName '$TaskName' | Get-ScheduledTaskInfo"
Write-Host "手動実行: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "解除:     pwsh -NoProfile -File scripts/register-night-batch-tasks.ps1 -Unregister"
