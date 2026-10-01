<#
  sync-all.ps1 — bar-exam をバックグラウンドで最新に保つ常駐同期（2026-09-30 新設）

  目的：
    「Wi-Fi に繋がっているあいだ、PC 側は勝手に最新になっていてほしい」を 1 本で満たす。
    従来は git の pull が rx-arb-autofill のついで（2h ごと）にしか走らず、Drive ⇄ inputs の
    取り込み／送りは手動、どのタスクもネットワーク接続を条件にしていなかった。

  やること（順に・すべて冪等・失敗は次の段へ進む）：
    1. git    ：fetch → master なら ff-only で取り込み → 未 push のローカルコミットがあれば push
               （作業ツリーが汚れている／分岐している／生成バッチ稼働中は git に触らない）
    2. inputs ：Drive → ローカル（tx-pull-inputs-from-drive.ps1 / jx-pull-inputs-from-drive.ps1・既存はスキップ）
    3. inputs ：ローカル → Drive（tx-push-inputs-to-drive.ps1・Drive 側の余剰は消さない）
    4. mirror ：-Mirror 指定時のみ drive-mirror.ps1（repo-backup へ robocopy /MIR・重いので既定 OFF）

  安全設計：
    - 自己ロック（logs/sync-all.lock・1h で stale 解除）＋ 前回実行から -MinGapMin（既定 10 分）未満なら
      スキップ（ネットワーク接続イベントは短時間に連発するため）。
    - 生成バッチ（TJR / tx-v13-runner / jx-batch-runner / 各 runner / autofill / backfill）の
      プロセスが居れば git 段を丸ごとスキップ（作業ツリーを触らない）。inputs の Drive 往復だけ行う。
    - インターネット到達性が無ければ何もしない。従量制接続（テザリング等）なら Drive の転送段を
      スキップする（-AllowMetered で解除）。Wi-Fi/有線かどうかは Windows のコスト情報で判定する。
    - Drive がマウントされていなければ inputs 段は黙ってスキップ（git 段だけ走る）。

  使い方：
    pwsh -NoProfile -File scripts/sync-all.ps1                # 手動 1 回
    pwsh -NoProfile -File scripts/sync-all.ps1 -DryRun        # 何をするか確認（git は fetch のみ）
    pwsh -NoProfile -File scripts/sync-all.ps1 -Mirror        # repo-backup ミラーも
  常駐登録：scripts/register-sync-all-task.ps1（30 分ごと＋ネットワーク接続時＋ログオン時）。
#>
[CmdletBinding()]
param(
  [string]$ProjectRoot = '',
  [switch]$DryRun,
  [switch]$NoPush,            # 未 push コミットがあっても push しない
  [switch]$NoInputs,          # Drive ⇄ inputs の往復を行わない
  [switch]$Mirror,            # drive-mirror.ps1（repo-backup）も回す
  [switch]$AllowMetered,      # 従量制接続でも Drive 転送を行う
  [int]$MinGapMin = 10,       # 前回実行からこの分数未満なら何もしない（イベント連発対策）
  [switch]$Force              # MinGap とロックを無視して実行
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$DefaultProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
Set-Location $ProjectRoot

$LogsDir = Join-Path $ProjectRoot 'logs'
if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null }
$stamp  = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$RunLog = Join-Path $LogsDir "sync-all-$(Get-Date -Format 'yyyyMMdd').log"   # 日別追記
$Report = Join-Path $LogsDir 'sync-all-report.md'                             # 最新結果の要約（追記式）
$LastRunFile = Join-Path $LogsDir 'sync-all.last'
function Log($m,$c='Gray'){ $line="[sync-all $stamp] $m"; Write-Host $line -ForegroundColor $c; Add-Content -Path $RunLog -Value $line -Encoding utf8 }
function Report($m){ Add-Content -Path $Report -Value "- $stamp $m" -Encoding utf8 }

# --- 0. 間引き（イベント連発対策）---
if (-not $Force -and (Test-Path $LastRunFile)) {
  $gap = (Get-Date) - (Get-Item $LastRunFile).LastWriteTime
  if ($gap.TotalMinutes -lt $MinGapMin) { Log "前回実行から $([int]$gap.TotalMinutes) 分（< $MinGapMin）→ スキップ" 'DarkGray'; exit 0 }
}

# --- 1. 自己ロック ---
$lock = Join-Path $LogsDir 'sync-all.lock'
if (-not $Force -and (Test-Path $lock)) {
  $age = (Get-Date) - (Get-Item $lock).LastWriteTime
  if ($age.TotalHours -lt 1) { Log "別の sync-all 実行中（lock $([int]$age.TotalMinutes)分前）→ スキップ" 'Yellow'; exit 0 }
  Log "stale lock を解除（$([int]$age.TotalMinutes)分前）" 'DarkGray'
}
"$PID $stamp" | Out-File -FilePath $lock -Encoding utf8
$summary = @()
try {
  # --- 2. ネットワーク判定（到達性・従量制）---
  $online = $true; $metered = $false
  try {
    $prof = @(Get-NetConnectionProfile -ErrorAction Stop | Where-Object { $_.IPv4Connectivity -eq 'Internet' -or $_.IPv6Connectivity -eq 'Internet' })
    $online = $prof.Count -gt 0
  } catch { $online = $true }   # cmdlet が無い環境では到達性を仮定（git fetch の失敗で判明する）
  if (-not $online) { Log "インターネット到達性なし → 何もしない" 'Yellow'; exit 0 }
  try {
    # WinRT の接続コスト（Windows PowerShell 5.1 で利用可・pwsh 7 では取れないことがある→未判定＝非従量扱い）
    $null = [Windows.Networking.Connectivity.NetworkInformation, Windows.Networking.Connectivity, ContentType=WindowsRuntime]
    $cp = [Windows.Networking.Connectivity.NetworkInformation]::GetInternetConnectionProfile()
    if ($cp) {
      $cost = $cp.GetConnectionCost()
      $metered = ($cost.NetworkCostType -ne 'Unrestricted') -or $cost.Roaming -or $cost.OverDataLimit
    }
  } catch { $metered = $false }
  Log ("接続: online=$online metered=$metered" + $(if ($metered -and -not $AllowMetered) { '（Drive 転送段はスキップ）' } else { '' })) 'DarkGray'

  # --- 3. 生成バッチ稼働中の検出（git 段の可否）---
  $busy = $false
  try {
    $procs = @(Get-CimInstance Win32_Process -Filter "Name='pwsh.exe' OR Name='powershell.exe'" -ErrorAction SilentlyContinue |
      Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine })
    $pat = '(TJR|tx-v13-runner|jx-batch-runner|night-batch-runner|v13q-runner|v13v-runner|v14-gist-runner|v15-dedup-runner|rx-arb-backfill|rx-arb-autofill|jx-finalize|jx-push)\.ps1|patterns[\\/](JX|TX-MARCH|TX-PICK|TJR)\.ps1'
    $bp = @($procs | Where-Object { $_.CommandLine -match $pat })
    if ($bp.Count -gt 0) { $busy = $true; Log "生成バッチ稼働中（PID $($bp[0].ProcessId)）→ git 段はスキップ" 'Yellow' }
  } catch {}

  # --- 4. git（fetch → ff-only → push）---
  if (-not $busy) {
    try {
      $hp = (& git config --get core.hooksPath) 2>$null
      if ($hp -ne 'scripts/git-hooks') { & git config core.hooksPath scripts/git-hooks 2>$null }
    } catch {}
    $branch = (& git rev-parse --abbrev-ref HEAD 2>$null)
    $dirty  = @(& git status --porcelain --untracked-files=no 2>$null)
    & git fetch origin master 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
      Log "git fetch 失敗（オフライン／認証）→ git 段を中断" 'DarkYellow'; $summary += 'git:fetch失敗'
    } elseif ($branch -ne 'master') {
      Log "現在ブランチ '$branch'（master 以外）→ fetch のみ" 'DarkYellow'; $summary += "git:fetchのみ($branch)"
    } elseif ($dirty.Count -gt 0) {
      Log "作業ツリーに未コミット変更 $($dirty.Count) 件 → fetch のみ（pull/push しない）" 'DarkYellow'; $summary += 'git:fetchのみ(dirty)'
    } else {
      $behind = [int](& git rev-list --count 'master..origin/master' 2>$null)
      $ahead  = [int](& git rev-list --count 'origin/master..master' 2>$null)
      if ($behind -gt 0 -and $ahead -eq 0) {
        if ($DryRun) { Log "DryRun: origin/master を $behind コミット取り込む" 'Cyan' }
        else {
          & git merge --ff-only origin/master 2>&1 | Out-Null
          if ($LASTEXITCODE -eq 0) { Log "pull: $behind コミット取り込み" 'Green'; $summary += "git:pull+$behind" }
          else { Log "ff-only merge 失敗" 'Red'; $summary += 'git:merge失敗' }
        }
      } elseif ($ahead -gt 0 -and $behind -eq 0) {
        if ($NoPush -or $DryRun) { Log "未 push コミット $ahead 件（push しない）" 'Cyan'; $summary += "git:未push$ahead" }
        else {
          $ok = $false
          foreach ($w in 2,4,8,16) {
            & git push -u origin master 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) { $ok = $true; break }
            Start-Sleep -Seconds $w
          }
          if ($ok) { Log "push: $ahead コミット" 'Green'; $summary += "git:push+$ahead" }
          else { Log "push 失敗（再試行 4 回）" 'Red'; $summary += 'git:push失敗' }
        }
      } elseif ($ahead -gt 0 -and $behind -gt 0) {
        Log "master が分岐（ahead $ahead / behind $behind）→ 自動では触らない。手動で rebase するか次の TJR に任せる" 'Red'
        $summary += "git:分岐(a$ahead/b$behind)"
      } else {
        Log "git: 最新（差分なし）" 'DarkGray'
      }
    }
  }

  # --- 5. Drive ⇄ inputs ---
  if (-not $NoInputs) {
    $driveOk = $false
    foreach ($cand in @('H:\マイドライブ','G:\マイドライブ',"$env:USERPROFILE\マイドライブ",'H:\My Drive','G:\My Drive',"$env:USERPROFILE\Google Drive")) {
      if (Test-Path -LiteralPath $cand) { $driveOk = $true; break }
    }
    if (-not $driveOk) { Log "Drive 未マウント → inputs 段をスキップ" 'DarkGray' }
    elseif ($metered -and -not $AllowMetered) { Log "従量制接続 → inputs 段をスキップ（-AllowMetered で解除）" 'DarkGray' }
    else {
      foreach ($s in @('tx-pull-inputs-from-drive.ps1','jx-pull-inputs-from-drive.ps1','tx-push-inputs-to-drive.ps1')) {
        $sp = Join-Path $ProjectRoot "scripts\$s"
        if (-not (Test-Path $sp)) { continue }
        try {
          $psArgs = @('-NoProfile','-File',$sp); if ($DryRun) { $psArgs += '-DryRun' }
          $out = & pwsh @psArgs 2>&1
          $tail = ($out | Select-Object -Last 1)
          Log ("$s → " + $tail) 'DarkGray'; $summary += "$($s.Split('-')[0..1] -join '-')"
        } catch { Log "$s 失敗: $($_.Exception.Message)" 'DarkYellow' }
      }
    }
  }

  # --- 6. repo-backup ミラー（任意）---
  if ($Mirror) {
    if ($metered -and -not $AllowMetered) { Log "従量制接続 → mirror スキップ" 'DarkGray' }
    else {
      $mp = Join-Path $ProjectRoot 'scripts\drive-mirror.ps1'
      if (Test-Path $mp) {
        $psArgs = @('-NoProfile','-File',$mp,'-ProjectRoot',$ProjectRoot); if ($DryRun) { $psArgs += '-DryRun' }
        & pwsh @psArgs 2>&1 | Out-Null
        Log "drive-mirror exit=$LASTEXITCODE" 'DarkGray'; $summary += 'mirror'
      }
    }
  }

  (Get-Date -Format 'o') | Out-File -FilePath $LastRunFile -Encoding utf8
  if ($summary.Count -gt 0) { Report ($summary -join ' / ') }
  Log ("完了: " + $(if ($summary.Count -gt 0) { $summary -join ' / ' } else { '変更なし' })) 'Green'
}
finally {
  Remove-Item -LiteralPath $lock -Force -ErrorAction SilentlyContinue
}
exit 0
