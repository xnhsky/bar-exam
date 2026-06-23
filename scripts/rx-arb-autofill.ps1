<#
  rx-arb-autofill.ps1 — 副産物（RX/TREE/ARIADNE）の「秘密裏・強制補完」常駐スイープ
  ------------------------------------------------------------------------------
  背景：操作者が副産物の存在を知らず JX＋TTS だけ生成・push しても（対話/リモート/別PC）、
        副産物がゼロのまま残る（刑JX056〜063 の実害）。生成方法やゲート指示に依存せず、
        「JX HTML はあるのに副産物が欠けている」状態を定期的に検知して**自動で生成・push**する。

  動作：
    1. 自己ロック（多重起動防止）。
    2. 稼働中バッチ回避：logs/jx-batch-*.log が直近 $BusyWindowMin 分以内に更新されていれば
       バッチ進行中とみなしスキップ（バッチ側 ②-verify ゲートに任せ、claude -p/git の競合を避ける）。
    3. git pull --ff-only（別PCの JX を取り込む。失敗してもローカルで続行）。
    4. 全 7 科目について rx-arb-backfill.ps1（生成のみ・既存スキップ）を $MaxPerSubject 件まで実行。
    5. outputs/ux に差分があれば **outputs/ux だけ** commit→push（JX HTML には触れない＝半生成と非干渉）。
       push 失敗時は pull --rebase して 1 回再試行。

  使い方（手動）：
    pwsh -NoProfile -File scripts/rx-arb-autofill.ps1 -DryRun      # 検出のみ（生成・push しない）
    pwsh -NoProfile -File scripts/rx-arb-autofill.ps1             # 補完＋push
    pwsh -NoProfile -File scripts/rx-arb-autofill.ps1 -NoPush     # 補完＋commit（push しない）

  定期実行の登録は register-rx-arb-autofill-task.ps1（schtasks・既定 2時間ごと）。
#>
[CmdletBinding()]
param(
  [int]$MaxPerSubject = 4,     # 1 スイープ・1 科目あたりの最大補完数（暴走防止・頻度で追いつく）
  [int]$BusyWindowMin = 20,    # この分以内に jx-batch-*.log 更新があればバッチ中とみなしスキップ
  [switch]$NoPush,
  [switch]$DryRun
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
$LogsDir = Join-Path $ProjectRoot 'logs'
if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null }
$Backfill = Join-Path $ProjectRoot 'scripts\rx-arb-backfill.ps1'
$AriaOut  = Join-Path $ProjectRoot 'outputs\ux\000_ARIADNE'
$RxOut    = Join-Path $ProjectRoot 'outputs\ux\001_RX'
$TreeOut  = Join-Path $ProjectRoot 'outputs\ux\002_TREE'
$JxBase   = Join-Path $ProjectRoot 'outputs\001_JX'
$Subjects = @('刑','刑訴','民','商','民訴','行政','憲')
$SubjMap  = @{ '刑'='001_刑法';'刑訴'='002_刑事訴訟法';'民'='003_民法';'商'='004_商法';'民訴'='005_民事訴訟法';'行政'='006_行政法';'憲'='007_憲法' }
$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$RunLog = Join-Path $LogsDir "autofill-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$Report = Join-Path $LogsDir 'autofill-report.md'   # ← xnrg2（副産物を知る側）が見る結果サマリ（追記式・最新が下）
function Log($m,$c='Gray'){ $line="[autofill $stamp] $m"; Write-Host $line -ForegroundColor $c; Add-Content -Path $RunLog -Value $line -Encoding utf8 }
function Report($m){ Add-Content -Path $Report -Value "- $stamp $m" -Encoding utf8 }

# --- 1. 自己ロック（多重起動防止・2h で stale 解除） ---
$lock = Join-Path $LogsDir 'rx-arb-autofill.lock'
if (Test-Path $lock) {
  $age = (Get-Date) - (Get-Item $lock).LastWriteTime
  if ($age.TotalHours -lt 2) { Log "別の autofill 実行中（lock $([int]$age.TotalMinutes)分前）→ スキップ" 'Yellow'; exit 0 }
  Log "stale lock を解除（$([int]$age.TotalHours)h 前）" 'DarkGray'
}
"$PID $stamp" | Out-File -FilePath $lock -Encoding utf8
try {
  # --- 2. 稼働中バッチ回避（プロセス検出＝最優先・ログmtimeは補助）---
  #   ① JX 生成中はバッチログが数十分沈黙するため mtime だけでは取りこぼす（実害：
  #   生成中の問題を autofill が二重生成）。実プロセスの CommandLine を見て確実に検出する。
  $procs = @(Get-CimInstance Win32_Process -Filter "Name='pwsh.exe' OR Name='powershell.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine })
  # バッチは patterns\JX.ps1 として起動し jx-batch-runner.ps1 は同一プロセス内呼び出しで
  # CommandLine に出ない。ランチャー名（patterns\JX.ps1）と runner 名の両方を拾う。
  $batchProc = @($procs | Where-Object { $_.CommandLine -match '(jx-batch-runner|night-batch-runner)\.ps1|patterns[\\/]JX\.ps1' })
  if ($batchProc.Count -gt 0) {
    Log "バッチ進行中（JX バッチプロセス稼働・PID $($batchProc[0].ProcessId)）→ 今回スキップ（②-verify に委譲）" 'Yellow'
    exit 0
  }
  $bfProc = @($procs | Where-Object { $_.CommandLine -match 'rx-arb-backfill\.ps1' })
  if ($bfProc.Count -gt 0) {
    Log "backfill が別途稼働中（PID $($bfProc[0].ProcessId)）→ 今回スキップ（多重生成防止）" 'Yellow'
    exit 0
  }
  # 補助：ログ mtime（プロセス検出の取りこぼし保険）
  $recentBatch = @(Get-ChildItem -Path $LogsDir -Filter 'jx-batch-*.log' -File -ErrorAction SilentlyContinue |
    Where-Object { ((Get-Date) - $_.LastWriteTime).TotalMinutes -lt $BusyWindowMin })
  if ($recentBatch.Count -gt 0) {
    Log "バッチログが直近 $BusyWindowMin 分以内に更新（$($recentBatch[0].Name)）→ 今回スキップ（②-verify に委譲）" 'Yellow'
    exit 0
  }

  # --- 3. git pull --ff-only（別PCの JX を取り込む） ---
  if (-not $DryRun) {
    & git fetch origin master 2>&1 | Out-Null
    & git merge --ff-only origin/master 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { Log "ff-only pull 不可（ローカル先行/分岐）→ ローカルのまま続行" 'DarkYellow' }
  }

  # --- 4. 欠落検知（全科目）---
  function Get-Missing([string]$subj){
    $dir = Join-Path $JxBase $SubjMap[$subj]
    if (-not (Test-Path $dir)) { return @() }
    $miss = @()
    foreach ($h in (Get-ChildItem -Path $dir -Filter "${subj}JX*.html" -File -ErrorAction SilentlyContinue)) {
      if ($h.BaseName -notmatch "^${subj}JX(\d{3})$") { continue }
      $id = $h.BaseName; $sd = $SubjMap[$subj]
      $okRx   = @(Get-ChildItem -Path (Join-Path (Join-Path $RxOut $sd) $id) -Filter '*.html' -File -ErrorAction SilentlyContinue).Count -gt 0
      $okTree = Test-Path (Join-Path (Join-Path $TreeOut $sd) "${id}_TREE.html")
      $okAria = Test-Path (Join-Path (Join-Path $AriaOut $sd) "${id}_ARIADNE.html")
      if (-not ($okRx -and $okTree -and $okAria)) { $miss += $id }
    }
    return $miss
  }

  $totalMissing = @()
  foreach ($s in $Subjects) {
    $m = Get-Missing $s
    if ($m.Count -gt 0) { Log "$s：副産物欠落 $($m.Count) 問 → $($m -join ', ')" 'Cyan'; $totalMissing += [PSCustomObject]@{ Subject=$s; Ids=$m } }
  }
  if ($totalMissing.Count -eq 0) { Log "全科目で副産物そろい確認 ✅（補完不要）" 'Green'; exit 0 }
  if ($DryRun) { Log "[DRY-RUN] 上記を補完予定（生成・push なし）" 'Yellow'; exit 0 }
  if (-not (Test-Path $Backfill)) { Log "rx-arb-backfill.ps1 不在 → 中止: $Backfill" 'Red'; exit 1 }

  # --- 5. backfill 実行（科目ごと・MaxPerSubject 件まで）---
  foreach ($t in $totalMissing) {
    $nums = @($t.Ids | ForEach-Object { if ($_ -match '(\d+)\s*$') { [int]$Matches[1] } } | Sort-Object)
    Log "$($t.Subject)：backfill 起動（範囲 $($nums[0])〜$($nums[-1])・最大 $MaxPerSubject 件）" 'Cyan'
    & pwsh -NoProfile -File $Backfill -Subject $t.Subject -FromNumber $nums[0] -ToNumber $nums[-1] -MaxProblems $MaxPerSubject
  }

  # --- 6. outputs/ux だけ commit→push（JX HTML には触れない）---
  # フッターに生成日時＋版を刻む（Lexia が raw 取得して読む・冪等・失敗は非致命）
  try { & python scripts/stamp-created-date.py 2>&1 | Out-Null } catch { Log "stamp skip: $_" 'Yellow' }
  & git add -- outputs/ux 2>&1 | Out-Null
  & git diff --cached --quiet -- outputs/ux
  if ($LASTEXITCODE -eq 0) {
    $tried = ($totalMissing | ForEach-Object { "$($_.Subject)[$($_.Ids -join ',')]" }) -join ' '
    Log "outputs/ux に新規差分なし（生成失敗 or 既存）→ commit せず" 'Yellow'
    Report "⚠️ 補完試行したが副産物が生成されず（要確認・次回再試行）: $tried"
    exit 0
  }

  $filledDesc = ($totalMissing | ForEach-Object { "$($_.Subject)[$($_.Ids -join ',')]" }) -join ' '
  $msg = "chore(jx): 副産物 自動補完（autofill・$($totalMissing.Subject -join '/'))"
  & git commit -q -m $msg
  $sha = git rev-parse --short HEAD
  Log "commit 作成: $sha" 'Green'
  if ($NoPush) { Log "-NoPush 指定 → push 省略" 'Yellow'; Report "✅ 補完 commit（push省略 -NoPush）: $filledDesc  [$sha]"; exit 0 }

  & git push origin master 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Log "push 失敗 → pull --rebase して再試行" 'Yellow'
    & git pull --rebase origin master 2>&1 | Out-Null
    & git push origin master 2>&1 | Out-Null
  }
  if ($LASTEXITCODE -eq 0) { Log "push 完了（副産物を GitHub 永続化）✅" 'Green'; Report "✅ 副産物を自動補完して push: $filledDesc  [$sha]" }
  else { Log "push 再試行も失敗（次回スイープで再送）" 'Red'; Report "⚠️ 補完 commit したが push 失敗（次回再送）: $filledDesc  [$sha]" }
}
finally {
  Remove-Item -Path $lock -Force -ErrorAction SilentlyContinue
}
