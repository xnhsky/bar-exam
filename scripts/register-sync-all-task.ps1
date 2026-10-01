<#
  register-sync-all-task.ps1 — sync-all.ps1 を「ネットワーク接続時に常に最新」で常駐させる（2026-09-30）

  トリガー（3 本・すべて同じアクション）：
    - 30 分ごと（繰り返し・無期限）
    - ネットワーク接続イベント（Microsoft-Windows-NetworkProfile/Operational・EventID 10000＝接続・遅延 1 分）
    - ログオン時（遅延 2 分）
  条件：ネットワーク利用可能時のみ実行（RunOnlyIfNetworkAvailable）・電源条件なし・多重起動は無視。
  実行ユーザー：現在のユーザー・ログオン中のみ（git / Drive マウント H: が効くのはこの時だけ）。

  方式：schtasks /XML（Register-ScheduledTask が非管理者で拒否される PC でも登録でき、
        ネットワーク条件とイベントトリガーを XML で持てる）。
  冪等：登録済みならスキップ（-Force で再作成・-Quiet で無出力＝TJR 起動時の自動配線用）。
  解除：schtasks /Delete /TN 'bar-exam-sync-all' /F

  Wi-Fi のときだけ：Task Scheduler は Wi-Fi/有線/テザリングを区別しないため、
  sync-all.ps1 側が従量制接続（テザリング等）のとき Drive 転送段をスキップする。
#>
[CmdletBinding()]
param(
  [string]$TaskName = 'bar-exam-sync-all',
  [int]$IntervalMinutes = 30,
  [string]$ProjectRoot = '',
  [switch]$Mirror,     # sync-all に -Mirror（repo-backup ミラー）も付ける
  [switch]$Force,
  [switch]$Quiet
)

$DefaultProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path

schtasks.exe /Query /TN $TaskName 2>$null | Out-Null
if ($LASTEXITCODE -eq 0 -and -not $Force) {
  if (-not $Quiet) { Write-Host "[SKIP] タスク '$TaskName' は既に登録済み（-Force で再作成）" -ForegroundColor DarkGray }
  exit 0
}

$pwshPath = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
if (-not $pwshPath) { $pwshPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" }
$script = Join-Path $ProjectRoot 'scripts\sync-all.ps1'
$argLine = "-NoProfile -ExecutionPolicy Bypass -File `"$script`" -ProjectRoot `"$ProjectRoot`"" + $(if ($Mirror) { ' -Mirror' } else { '' })

function XmlEsc([string]$s) { [System.Security.SecurityElement]::Escape($s) }
$userId = "$env:USERDOMAIN\$env:USERNAME"
$start  = (Get-Date).AddMinutes(2).ToString('yyyy-MM-ddTHH:mm:ss')
$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>bar-exam sync-all：git pull/push＋Drive⇄inputs をネットワーク接続時に自動同期（$IntervalMinutes 分ごと・接続時・ログオン時）</Description>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <Repetition><Interval>PT${IntervalMinutes}M</Interval><StopAtDurationEnd>false</StopAtDurationEnd></Repetition>
      <StartBoundary>$start</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
    <EventTrigger>
      <Enabled>true</Enabled>
      <Subscription>&lt;QueryList&gt;&lt;Query Id="0" Path="Microsoft-Windows-NetworkProfile/Operational"&gt;&lt;Select Path="Microsoft-Windows-NetworkProfile/Operational"&gt;*[System[Provider[@Name='Microsoft-Windows-NetworkProfile'] and EventID=10000]]&lt;/Select&gt;&lt;/Query&gt;&lt;/QueryList&gt;</Subscription>
      <Delay>PT1M</Delay>
    </EventTrigger>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <UserId>$(XmlEsc $userId)</UserId>
      <Delay>PT2M</Delay>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$(XmlEsc $userId)</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>$(XmlEsc $pwshPath)</Command>
      <Arguments>$(XmlEsc $argLine)</Arguments>
      <WorkingDirectory>$(XmlEsc $ProjectRoot)</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) "bar-exam-sync-all-task.xml"
Set-Content -LiteralPath $tmp -Value $xml -Encoding Unicode
schtasks.exe /Delete /TN $TaskName /F 2>$null | Out-Null
$out = schtasks.exe /Create /TN $TaskName /XML $tmp /F 2>&1
$rc = $LASTEXITCODE
Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
if ($rc -ne 0) {
  if (-not $Quiet) { Write-Host "[FAIL] schtasks 登録失敗 (exit=$rc)" -ForegroundColor Red; $out }
  exit 1
}
if (-not $Quiet) {
  Write-Host "[OK] $out" -ForegroundColor Green
  schtasks.exe /Query /TN $TaskName /FO LIST /V 2>&1 |
    Select-String -Pattern 'TaskName|Next Run|Status|Task To Run' | ForEach-Object { $_.Line.Trim() }
}
exit 0
