<#
  register-rx-arb-autofill-task.ps1 — rx-arb-autofill.ps1 を定期実行するタスクを登録
  （副産物の「秘密裏・強制補完」を常駐化。生成方法に依存せず欠落を自動で埋め push する）

  - 方式：schtasks.exe（Register-ScheduledTask は本PCで非管理者だとアクセス拒否のため）
  - スケジュール：既定 2 時間ごと（/SC HOURLY /MO 2）
  - 実行ユーザー：現在のユーザー・/IT（ログオン中のみ＝git/claude 認証が効く時のみ）
  - /RL LIMITED：標準権限
  - 解除：schtasks /Delete /TN 'bar-exam-rx-arb-autofill' /F

  ※ 二台運用：このタスクを動かす PC が pull 後に欠落を埋めるので、1 台で全体を守れる。
     両 PC で動かすとより堅牢（各自このスクリプトを実行）。
#>
[CmdletBinding()]
param(
  [string]$TaskName = 'bar-exam-rx-arb-autofill',
  [int]$IntervalHours = 2
)

$pwshPath = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
if (-not $pwshPath) { $pwshPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" }
$script = 'c:\Users\xnrg2.DESKTOP-5664QR6\bar-exam\scripts\rx-arb-autofill.ps1'
$tr = "`"$pwshPath`" -NoProfile -ExecutionPolicy Bypass -File `"$script`""

schtasks.exe /Delete /TN $TaskName /F 2>$null | Out-Null

$out = schtasks.exe /Create /TN $TaskName /TR $tr `
  /SC HOURLY /MO $IntervalHours /RL LIMITED /IT /F /RU $env:USERNAME 2>&1
if ($LASTEXITCODE -ne 0) {
  Write-Host "[FAIL] schtasks 登録失敗 (exit=$LASTEXITCODE)" -ForegroundColor Red
  $out
  Write-Host "→ 管理者 PowerShell で再実行するか、Start-Process -Verb RunAs で昇格してください。" -ForegroundColor Yellow
  exit 1
}
Write-Host "[OK] $out" -ForegroundColor Green
schtasks.exe /Query /TN $TaskName /FO LIST /V 2>&1 |
  Select-String -Pattern 'TaskName|Next Run|Status|Task To Run|Schedule Type|Repeat: Every' |
  ForEach-Object { $_.Line.Trim() }
