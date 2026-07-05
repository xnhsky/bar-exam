# register-tjr-night-task.ps1
#
# 現行の唯一の生成入口 TJR（scripts\patterns\TJR.ps1）を Windows タスクスケジューラへ登録する。
# 旧 register-night-batch-tasks.ps1（引退した v10 night-batch-runner 向け）の TJR 版・貼り替え先。
# 既定では 21:00 / 23:00 / 01:00 / 03:00 / 05:00 の 5 トリガー（2 時間間隔・夜間分割生成）＋
# 起動時トリガー（遅延3分）を 1 タスクにまとめて登録する。各起動は科目の T→J→R を直列処理する。
#
# 実行例:
#   # 刑法を毎夜処理（R=旧_lex再生成が主役・T/J は対象があれば）
#   pwsh -NoProfile -File scripts/register-tjr-night-task.ps1 -Subject 刑
#
#   # 刑訴の新規TX だけ夜間生成（T のみ・334件）
#   pwsh -NoProfile -File scripts/register-tjr-night-task.ps1 -Subject 刑訴 -Only T
#
#   # 科目自動（優先順で仕事のある科目を1つ）
#   pwsh -NoProfile -File scripts/register-tjr-night-task.ps1
#
#   # R を番号帯に固定（例：刑法 372-385 の再生成のみ）
#   pwsh -NoProfile -File scripts/register-tjr-night-task.ps1 -Subject 刑 -Only R -RFrom 372 -RTo 385
#
#   # 登録解除（旧 night-batch タスクも同時に掃除）
#   pwsh -NoProfile -File scripts/register-tjr-night-task.ps1 -Unregister
#
# 注意:
#   - claude CLI は実行ユーザーの認証情報（%USERPROFILE%\.claude）を使うため、
#     タスクは「現在のユーザーがログオン時のみ」実行する設定で登録する。
#   - スリープ中でも起動できるよう WakeToRun を有効化。TJR/エンジンは実行中 keep-awake（feedback_nbr_keep_awake）。
#   - .ps1 は BOM 付き UTF-8 で保存すること（scripts/README.md 規律）。

param(
    [string]$TaskName    = 'BarExam-Night-TJR',
    [string]$Subject     = '',          # '' = TJR 側で科目自動選択（優先順で仕事のある科目）
    [ValidateSet('', 'T', 'J', 'R')]
    [string]$Only        = '',          # '' = T→J→R 全部 ／ T|J|R = 1ストリームだけ
    [int]$TxFrom = 0, [int]$TxTo = 0,   # T の番号帯ピン（0 = 通常＝最若番から MaxTX 件）
    [int]$JxFrom = 0, [int]$JxTo = 0,   # J の番号帯ピン
    [int]$RFrom  = 0, [int]$RTo  = 0,   # R の番号帯ピン
    [int]$MaxTX  = 12,                  # T の1起動チャンク
    [int]$MaxJX  = 3,                   # J の1起動チャンク
    [int]$MaxR   = 3,                   # R の1起動チャンク
    [string[]]$Times     = @('21:00','23:00','01:00','03:00','05:00'),
    [switch]$NoPush,                    # commit のみ（push しない）
    [string]$ProjectRoot = '',          # 別 clone/root で登録する場合に指定（未指定はこの repo）
    [switch]$Unregister
)

$ErrorActionPreference = 'Stop'

# === パス解決（マルチ PC / clone 分離対応）===
$DefaultProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$RunnerPath  = Join-Path $ProjectRoot 'scripts\patterns\TJR.ps1'
if (-not (Test-Path $RunnerPath)) { throw "TJR runner not found: $RunnerPath" }

# 旧 night-batch タスク名（貼り替え時に一緒に掃除する）
$LegacyTaskName = 'BarExam-NightBatch-TX'

# === 登録解除モード ===
if ($Unregister) {
    foreach ($tn in @($TaskName, $LegacyTaskName)) {
        if (Get-ScheduledTask -TaskName $tn -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskName $tn -Confirm:$false
            Write-Host "[OK] タスク '$tn' を登録解除しました。" -ForegroundColor Green
        } else {
            Write-Host "[INFO] タスク '$tn' は存在しません。" -ForegroundColor Yellow
        }
    }
    return
}

# === pwsh 実行ファイルの解決 ===
$PwshExe = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
if (-not $PwshExe) { $PwshExe = (Get-Process -Id $PID).Path }  # フォールバック

# === 起動引数の組み立て（TJR の param 体系）===
$argList = @(
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-File', "`"$RunnerPath`"",
    '-ProjectRoot', "`"$ProjectRoot`""
)
if (-not [string]::IsNullOrWhiteSpace($Subject)) { $argList += @('-Subject', $Subject) }
if (-not [string]::IsNullOrWhiteSpace($Only))    { $argList += @('-Only', $Only) }
if ($TxFrom -gt 0) { $argList += @('-TxFrom', $TxFrom) }
if ($TxTo   -gt 0) { $argList += @('-TxTo',   $TxTo) }
if ($JxFrom -gt 0) { $argList += @('-JxFrom', $JxFrom) }
if ($JxTo   -gt 0) { $argList += @('-JxTo',   $JxTo) }
if ($RFrom  -gt 0) { $argList += @('-RFrom',  $RFrom) }
if ($RTo    -gt 0) { $argList += @('-RTo',    $RTo) }
$argList += @('-MaxTX', $MaxTX, '-MaxJX', $MaxJX, '-MaxR', $MaxR)
if ($NoPush) { $argList += '-NoPush' }
$argString = $argList -join ' '

$Action = New-ScheduledTaskAction -Execute $PwshExe -Argument $argString -WorkingDirectory $ProjectRoot

# === 5 トリガー（各時刻の毎日起動）＋ 起動時トリガー（遅延3分）===
$Triggers = @(foreach ($t in $Times) { New-ScheduledTaskTrigger -Daily -At $t })
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

$subjDesc = if ([string]::IsNullOrWhiteSpace($Subject)) { '科目自動' } else { $Subject }
$onlyDesc = if ([string]::IsNullOrWhiteSpace($Only)) { 'T→J→R' } else { "Only $Only" }
$Description = "bar-exam TJR 夜間無人生成（$($Times -join ' / ')・起動時トリガー(遅延3分)含む・$subjDesc / $onlyDesc・keep-awake込み）"

# === 既存タスクがあれば置き換え＋旧 night-batch タスクを掃除（貼り替え）===
foreach ($tn in @($TaskName, $LegacyTaskName)) {
    if (Get-ScheduledTask -TaskName $tn -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $tn -Confirm:$false
        $msg = if ($tn -eq $LegacyTaskName) { "旧 night-batch タスク '$tn' を掃除しました（TJR へ貼り替え）。" } else { "既存タスク '$tn' を置き換えます。" }
        Write-Host "[INFO] $msg" -ForegroundColor Yellow
    }
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
Write-Host "  トリガー: $($Times -join ' / ') ＋ 起動時(遅延3分)"
Write-Host "  対象: $subjDesc / $onlyDesc / チャンク T=$MaxTX J=$MaxJX R=$MaxR"
Write-Host ""
Write-Host "確認:   Get-ScheduledTask -TaskName '$TaskName' | Get-ScheduledTaskInfo"
Write-Host "手動実行: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "解除:     pwsh -NoProfile -File scripts/register-tjr-night-task.ps1 -Unregister"
