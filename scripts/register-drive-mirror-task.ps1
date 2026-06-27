<#
  register-drive-mirror-task.ps1 — drive-mirror.ps1 を 3時間ごと自動実行するタスクを登録

  - 方式：schtasks.exe（Register-ScheduledTask は非管理者でアクセス拒否となるため）
  - スケジュール：3時間ごと（/SC HOURLY /MO 3）
  - 実行ユーザー：現在のユーザー・/IT（ログオン中のみ実行＝マイドライブ H: が存在する時のみ）
  - /RL LIMITED：標準権限
  - 解除：schtasks /Delete /TN 'bar-exam-drive-mirror' /F
#>
[CmdletBinding()]
param(
  [string]$TaskName = 'bar-exam-drive-mirror',
  [int]$IntervalHours = 3,
  [string]$ProjectRoot = ''  # 別 clone/root で登録する場合に指定（未指定はこの repo）
)

$DefaultProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path

$pwshPath = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
if (-not $pwshPath) { $pwshPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" }
$script = Join-Path $ProjectRoot 'scripts\drive-mirror.ps1'
$tr = "`"$pwshPath`" -NoProfile -ExecutionPolicy Bypass -File `"$script`" -ProjectRoot `"$ProjectRoot`""

# 既存があれば削除（無ければ無視）
schtasks.exe /Delete /TN $TaskName /F 2>$null | Out-Null

$out = schtasks.exe /Create /TN $TaskName /TR $tr `
  /SC HOURLY /MO $IntervalHours /RL LIMITED /IT /F /RU $env:USERNAME 2>&1
if ($LASTEXITCODE -ne 0) {
  Write-Host "[FAIL] schtasks 登録失敗 (exit=$LASTEXITCODE)" -ForegroundColor Red
  $out
  exit 1
}
Write-Host "[OK] $out" -ForegroundColor Green
schtasks.exe /Query /TN $TaskName /FO LIST /V 2>&1 |
  Select-String -Pattern 'TaskName|Next Run|Status|Task To Run|Schedule Type|Repeat: Every' |
  ForEach-Object { $_.Line.Trim() }
