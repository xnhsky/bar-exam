<#
  register-rx-arb-autofill-task.ps1 — rx-arb-autofill.ps1 を定期実行するタスクを登録
  （副産物の「秘密裏・強制補完」を常駐化。生成方法に依存せず欠落を自動で埋め push する）

  - 方式：schtasks.exe（Register-ScheduledTask は本PCで非管理者だとアクセス拒否のため）
  - スケジュール：既定 2 時間ごと（/SC HOURLY /MO 2）
  - 実行ユーザー：現在のユーザー・/IT（ログオン中のみ＝git/claude 認証が効く時のみ）
  - /RL LIMITED：標準権限
  - 解除：schtasks /Delete /TN 'bar-exam-rx-arb-autofill' /F

  ※ 二台運用（OWNER PC / xnrg2 PC・どちらか一方は常時起動）：両 PC でこのタスクを動かせば、
     点いている方が pull 後に欠落を埋めるので穴がなくなる。パスは $PSScriptRoot 起点で可搬なので
     OWNER PC でもそのまま登録できる（CLAUDE.md §4-6 の「JX 生成時に冪等登録」で自動常駐化）。

  - 冪等：既に登録済みなら何もせず終了（-Force で再作成）。
#>
[CmdletBinding()]
param(
  [string]$TaskName = 'bar-exam-rx-arb-autofill',
  [int]$IntervalHours = 2,
  [switch]$Force,      # 登録済みでも作り直す
  [switch]$Quiet       # 指定で出力を抑制（セッション開始時の冪等確認用）
)

# 冪等確認：既存タスクがあれば（-Force でない限り）即終了
$exists = $false
schtasks.exe /Query /TN $TaskName 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) { $exists = $true }
if ($exists -and -not $Force) {
  if (-not $Quiet) { Write-Host "[SKIP] タスク '$TaskName' は既に登録済み（-Force で再作成）" -ForegroundColor DarkGray }
  exit 0
}

$pwshPath = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
if (-not $pwshPath) { $pwshPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" }
# パス可搬：このスクリプトと同じ scripts\ 配下の autofill を指す（OWNER PC でもそのまま動く）
$script = Join-Path $PSScriptRoot 'rx-arb-autofill.ps1'
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
if (-not $Quiet) {
  Write-Host "[OK] $out" -ForegroundColor Green
  schtasks.exe /Query /TN $TaskName /FO LIST /V 2>&1 |
    Select-String -Pattern 'TaskName|Next Run|Status|Task To Run|Schedule Type|Repeat: Every' |
    ForEach-Object { $_.Line.Trim() }
}
