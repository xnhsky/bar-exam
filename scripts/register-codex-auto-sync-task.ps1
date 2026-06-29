<#
  register-codex-auto-sync-task.ps1

  Register a local Windows scheduled task that keeps bar-exam-codex on
  origin/master. This is intentionally polling-based instead of a git post-push
  hook because Git has no reliable local post-push hook.

  Manual use:
    pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/register-codex-auto-sync-task.ps1
#>
[CmdletBinding()]
param(
  [string]$TaskName = 'bar-exam-codex-auto-sync',
  [string]$ProjectRoot = 'C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam-codex',
  [int]$IntervalMinutes = 1,
  [switch]$Force,
  [switch]$Quiet
)

$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$script = Join-Path $ProjectRoot 'scripts\sync-repo-from-master.ps1'
$cmdScript = Join-Path $ProjectRoot 'scripts\codex-auto-sync.cmd'
if (-not (Test-Path -LiteralPath $script)) {
  Write-Host "[FAIL] sync script not found in target: $script" -ForegroundColor Red
  exit 1
}
if (-not (Test-Path -LiteralPath $cmdScript)) {
  Write-Host "[FAIL] sync cmd not found in target: $cmdScript" -ForegroundColor Red
  exit 1
}

$exists = $false
schtasks.exe /Query /TN $TaskName 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) { $exists = $true }
if ($exists -and -not $Force) {
  if (-not $Quiet) { Write-Host "[SKIP] task already exists: $TaskName" -ForegroundColor DarkGray }
  exit 0
}

$taskRun = "`"$cmdScript`""

schtasks.exe /Delete /TN $TaskName /F 2>$null | Out-Null
$out = schtasks.exe /Create /TN $TaskName /TR $taskRun /SC MINUTE /MO $IntervalMinutes /RL LIMITED /IT /F /RU $env:USERNAME 2>&1
if ($LASTEXITCODE -ne 0) {
  Write-Host "[FAIL] failed to register task (exit=$LASTEXITCODE)" -ForegroundColor Red
  $out
  exit 1
}

if (-not $Quiet) {
  Write-Host "[OK] registered $TaskName every $IntervalMinutes minute(s)" -ForegroundColor Green
  schtasks.exe /Query /TN $TaskName /FO LIST /V 2>&1 |
    Select-String -Pattern 'TaskName|Next Run|Status|Task To Run|Schedule Type|Repeat: Every' |
    ForEach-Object { $_.Line.Trim() }
}
