# rx-arb-backfill.ps1
#
# 既存の JX HTML（outputs/001_JX/{科目}JX/*.html）から、Lexia 用の副産物
#   RX  = 論証カード（1論点1HTML / outputs/004_JX_EX/RX/{科目}RX/{科目}RX{NNN}_{n}.html）
#   TREE = ARBOR 樹形図（1問1枚 / outputs/004_JX_EX/TREE/{科目}TREE/{科目}JX{NNN}_TREE.html）
# が**未生成のものだけ**を後追い生成するバックフィルランナー。
# 新規 JX は jx-batch-runner.ps1 の ②-rx / ②-arb 段が自動で副産物を作るので、
# 本スクリプトは「ランナー導入以前に生成済みの JX 資産」を埋めるために使う。
#
# 実行例:
#   pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 刑 -DryRun
#   pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 刑 -MaxProblems 3
#   pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 民訴 -SkipArb   # RX だけ埋める

param(
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '刑',
    [int]$MaxProblems = 5,              # 1 起動あたり最大処理 JX 数（RX/TREE 合計ではなく問題数）
    [int]$FromNumber = 0,
    [int]$ToNumber = 0,
    [switch]$SkipRx,
    [switch]$SkipArb,
    [string]$ArborRoot = 'C:\Users\xnrg2.DESKTOP-5664QR6\arbor',
    [switch]$DryRun
)

$ProjectRoot   = Split-Path -Parent $PSScriptRoot
# 科目 → 00N_科目 サブフォルダ
$SubjDir = switch ($Subject) { '刑'{'001_刑法'} '刑訴'{'002_刑事訴訟法'} '民'{'003_民法'} '商'{'004_商法'} '民訴'{'005_民事訴訟法'} '行政'{'006_行政法'} '憲'{'007_憲法'} default {"$Subject"} }
$JxOutputDir   = Join-Path $ProjectRoot "outputs\001_JX\$SubjDir"
$RxOutputDir   = Join-Path $ProjectRoot "outputs\004_JX_EX\RX\$SubjDir"
$ArbOutputDir  = Join-Path $ProjectRoot "outputs\004_JX_EX\TREE\$SubjDir"
$LogsDir       = Join-Path $ProjectRoot "logs"
$RxPromptSrc   = Join-Path $ProjectRoot "prompts\new-rx-headless.md"
$ArbPromptSrc  = Join-Path $ProjectRoot "prompts\new-arb-headless.md"
$ValidateRx    = Join-Path $ProjectRoot "scripts\validate-rx.py"
$ArborMaster   = Join-Path $ArborRoot "ARBOR_v5.0_master_prompt.md"
$ArborRef      = Join-Path $ArborRoot "Reference\ARBOR_002_shucho_tekikaku.html"
$ArborVerify   = Join-Path $ArborRoot "scripts\verify.py"
$RxArbCsv      = Join-Path $LogsDir "rx-arb-summary.csv"
$RunLog        = Join-Path $LogsDir "rx-arb-backfill-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
if (-not (Test-Path $LogsDir)) { New-Item -Path $LogsDir -ItemType Directory -Force | Out-Null }
Start-Transcript -Path $RunLog -Append | Out-Null

Write-Host "=== rx-arb-backfill 開始 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "Subject: $Subject / MaxProblems: $MaxProblems / Range: From=$FromNumber To=$ToNumber / DryRun: $DryRun"

if (-not (Test-Path $JxOutputDir)) {
    Write-Host "[ABORT] JX 出力ディレクトリが無い: $JxOutputDir" -ForegroundColor Red
    Stop-Transcript | Out-Null; exit 1
}

# 副産物の有効判定（jx-batch-runner と同じく前提欠如は自動スキップ）
$RxEnabled = (-not $SkipRx)
if ($RxEnabled -and -not (Test-Path $RxPromptSrc)) { Write-Host "[NOTE] RX prompt 不在 → RX スキップ" -ForegroundColor Yellow; $RxEnabled = $false }
if ($RxEnabled -and -not (Test-Path $ValidateRx))  { Write-Host "[NOTE] validate-rx.py 不在 → RX スキップ" -ForegroundColor Yellow; $RxEnabled = $false }
$ArbEnabled = (-not $SkipArb)
if ($ArbEnabled -and -not (Test-Path $ArbPromptSrc)) { Write-Host "[NOTE] TREE prompt 不在 → TREE スキップ" -ForegroundColor Yellow; $ArbEnabled = $false }
if ($ArbEnabled -and -not (Test-Path $ArborMaster))  { Write-Host "[NOTE] ARBOR 正典不在 → TREE スキップ: $ArborMaster" -ForegroundColor Yellow; $ArbEnabled = $false }
if (-not ($RxEnabled -or $ArbEnabled)) {
    Write-Host "[ABORT] RX/TREE とも無効。やることがありません。" -ForegroundColor Red
    Stop-Transcript | Out-Null; exit 1
}

if (-not (Test-Path $RxArbCsv)) {
    "timestamp,subject,problem_id,kind,elapsed,files,sentinel,exit,validate" | Out-File -FilePath $RxArbCsv -Encoding utf8
}

# === claude -p 起動ヘルパ（jx-batch-runner.ps1 と同実装）===
function Invoke-ClaudeHeadless {
    param([string]$Prompt, [string]$JsonOutPath)
    # --model を明示固定（2026-06-13）: グローバル既定が claude-fable-5[1m]（アクセス権なし）に
    # 化けると 0秒/0byte/exit1 の即時失敗が連発する事故への対策。動作確認済みモデルに固定。
    $claudeArgs = @(
        '-p',
        '--model', 'claude-opus-4-8[1m]',
        '--output-format', 'json',
        '--permission-mode', 'acceptEdits',
        '--allowedTools', 'Write,Edit,Read,Bash,Glob,Grep'
    )
    $execHeader = @'
[HEADLESS 実行指示 — 最優先・厳守]
以下に続くのは「レビュー対象の文書」ではない。あなたが今この瞬間に自走で最後まで実行する指示書である。
- 確認・質問・要約・選択肢提示・「ご依頼が不明です」等の応答は一切禁止。
- 文書内（特に末尾「実行開始」節）の手順に厳密に従い、ファイル生成と sentinel 出力まで完遂せよ。
- 一部に `{科目}` 等のプレースホルダ表記が残っていても、与えられた実値で実行する（テンプレ原本か否かを問い直さない）。
以下、指示書本体：
---

'@
    $fullPrompt = $execHeader + $Prompt
    try {
        $out = $fullPrompt | & claude @claudeArgs 2>&1
        $code = $LASTEXITCODE
    } catch {
        $out = "$_"
        $code = -1
    }
    $out | Out-File -FilePath $JsonOutPath -Encoding utf8
    return [PSCustomObject]@{ Output = ($out -join "`n"); ExitCode = $code }
}

function Get-Sentinel {
    param([string]$Text, [string]$ProblemId)
    $esc = [regex]::Escape($ProblemId)
    if ($Text -match "BATCH_ITEM_COMPLETED:$esc(\b|`$)") { return "COMPLETED" }
    if ($Text -match "BATCH_ITEM_COMPLETED_WITH_ISSUES:$esc:errors=(\d+):warnings=(\d+)") {
        return "WITH_ISSUES:errors=$($Matches[1]):warnings=$($Matches[2])"
    }
    if ($Text -match "BATCH_ITEM_FAILED:$esc") { return "FAILED" }
    return "UNKNOWN"
}

# === 既存 JX をスキャンし、欠けている副産物を洗い出す ===
$Catalog = @()
foreach ($jx in @(Get-ChildItem -Path $JxOutputDir -Filter "*.html" -File | Sort-Object Name)) {
    if ($jx.BaseName -notmatch "^${Subject}JX(\d{3})$") { continue }
    $num = $Matches[1]
    $numInt = [int]$num
    if (($FromNumber -gt 0 -and $numInt -lt $FromNumber) -or ($ToNumber -gt 0 -and $numInt -gt $ToNumber)) { continue }
    $problemId = "${Subject}JX${num}"
    $rxBase  = "${Subject}RX${num}"
    $hasRx   = @(Get-ChildItem -Path $RxOutputDir -Filter "${rxBase}_*.html" -File -ErrorAction SilentlyContinue).Count -gt 0
    $arbPath = Join-Path $ArbOutputDir "${problemId}_TREE.html"
    $hasArb  = Test-Path $arbPath
    $needRx  = $RxEnabled -and (-not $hasRx)
    $needArb = $ArbEnabled -and (-not $hasArb)
    if (-not ($needRx -or $needArb)) { continue }
    $Catalog += [PSCustomObject]@{
        ProblemId = $problemId; Number = $num; JxPath = $jx.FullName
        RxBase = $rxBase; NeedRx = $needRx; ArbPath = $arbPath; NeedArb = $needArb
    }
}
$Targets = @($Catalog | Sort-Object { [int]$_.Number } | Select-Object -First $MaxProblems)

Write-Host "`n--- 副産物が欠けている JX: $($Catalog.Count) 件 / 本起動の処理対象: $($Targets.Count) 件 ---" -ForegroundColor Yellow
foreach ($t in $Targets) {
    $needs = @(); if ($t.NeedRx) { $needs += 'RX' }; if ($t.NeedArb) { $needs += 'TREE' }
    Write-Host ("  ● {0}  欠落: {1}" -f $t.ProblemId, ($needs -join '+')) -ForegroundColor Cyan
}
if ($Targets.Count -eq 0) {
    Write-Host "全 JX に副産物が揃っています。終了。" -ForegroundColor Green
    Stop-Transcript | Out-Null; exit 0
}
if ($DryRun) {
    Write-Host "`n[DRY-RUN] 終了（実生成なし）。" -ForegroundColor Yellow
    Stop-Transcript | Out-Null; exit 0
}

# === 生成ループ ===
foreach ($t in $Targets) {
    Write-Host "`n==================== [$($t.ProblemId)] ====================" -ForegroundColor Cyan

    if ($t.NeedRx) {
        Write-Host "--- RX 生成 $(Get-Date -Format 'HH:mm:ss') ---" -ForegroundColor Cyan
        $rxStart = Get-Date
        if (-not (Test-Path $RxOutputDir)) { New-Item -Path $RxOutputDir -ItemType Directory -Force | Out-Null }
        $rxTemplate = Get-Content $RxPromptSrc -Raw -Encoding utf8
        $rxPrompt = $rxTemplate `
            -replace '\{SOURCE_HTML_PATH\}', $t.JxPath `
            -replace '\{PROBLEM_ID\}',       $t.ProblemId `
            -replace '\{PROBLEM_NUMBER\}',   $t.Number `
            -replace '\{SUBJECT_PREFIX\}',   $Subject `
            -replace '\{RX_BASENAME\}',      $t.RxBase `
            -replace '\{OUTPUT_DIR\}',       $RxOutputDir `
            -replace '\{VALIDATE_RX\}',      $ValidateRx
        $rxRes = Invoke-ClaudeHeadless -Prompt $rxPrompt -JsonOutPath (Join-Path $LogsDir "rx-$($t.ProblemId).json")
        $rxSent = Get-Sentinel -Text $rxRes.Output -ProblemId "$($t.ProblemId)-RX"
        $rxFiles = @(Get-ChildItem -Path $RxOutputDir -Filter "$($t.RxBase)_*.html" -File -ErrorAction SilentlyContinue).Count
        $rxValidate = "skipped_no_files"
        if ($rxFiles -gt 0) {
            $rvOut = & python $ValidateRx $RxOutputDir $t.RxBase 2>&1
            $rxValidate = if ($LASTEXITCODE -eq 0) { "PASS" } else { "ERROR(exit=$LASTEXITCODE)" }
            ($rvOut -join "`n") | Out-File -FilePath (Join-Path $LogsDir "rx-validate-$($t.ProblemId).txt") -Encoding utf8
        }
        $rxElapsed = [int]((Get-Date) - $rxStart).TotalSeconds
        Write-Host "[RX DONE] files=$rxFiles, sentinel=$rxSent, validate=$rxValidate" -ForegroundColor $(if ($rxValidate -eq 'PASS') { 'Green' } else { 'Yellow' })
        Add-Content -Path $RxArbCsv -Encoding utf8 -Value (@(
            (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Subject, $t.ProblemId, 'RX',
            $rxElapsed, $rxFiles, $rxSent, $rxRes.ExitCode, $rxValidate) -join ',')
    }

    if ($t.NeedArb) {
        Write-Host "--- TREE 生成 $(Get-Date -Format 'HH:mm:ss') ---" -ForegroundColor Cyan
        $arbStart = Get-Date
        if (-not (Test-Path $ArbOutputDir)) { New-Item -Path $ArbOutputDir -ItemType Directory -Force | Out-Null }
        $arbTemplate = Get-Content $ArbPromptSrc -Raw -Encoding utf8
        $arbPrompt = $arbTemplate `
            -replace '\{SOURCE_HTML_PATH\}', $t.JxPath `
            -replace '\{PROBLEM_ID\}',       $t.ProblemId `
            -replace '\{PROBLEM_NUMBER\}',   $t.Number `
            -replace '\{SUBJECT_PREFIX\}',   $Subject `
            -replace '\{OUTPUT_PATH\}',      $t.ArbPath `
            -replace '\{ARBOR_MASTER\}',     $ArborMaster `
            -replace '\{ARBOR_REFERENCE\}',  $ArborRef `
            -replace '\{ARBOR_VERIFY\}',     $ArborVerify
        $arbRes = Invoke-ClaudeHeadless -Prompt $arbPrompt -JsonOutPath (Join-Path $LogsDir "arb-$($t.ProblemId).json")
        $arbSent = Get-Sentinel -Text $arbRes.Output -ProblemId "$($t.ProblemId)-TREE"
        $arbBytes = if (Test-Path $t.ArbPath) { (Get-Item $t.ArbPath).Length } else { 0 }
        $arbValidate = if ($arbBytes -gt 0 -and $arbSent -eq "COMPLETED") { "PASS" }
                       elseif ($arbBytes -gt 0) { "CHECK($arbSent)" }
                       else { "no_html" }
        $arbElapsed = [int]((Get-Date) - $arbStart).TotalSeconds
        Write-Host "[TREE DONE] bytes=$arbBytes, sentinel=$arbSent, validate=$arbValidate" -ForegroundColor $(if ($arbValidate -eq 'PASS') { 'Green' } else { 'Yellow' })
        Add-Content -Path $RxArbCsv -Encoding utf8 -Value (@(
            (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Subject, $t.ProblemId, 'TREE',
            $arbElapsed, $arbBytes, $arbSent, $arbRes.ExitCode, $arbValidate) -join ',')
    }
}

Write-Host "`n=== rx-arb-backfill 終了 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "コストログ: $RxArbCsv"
Stop-Transcript | Out-Null
exit 0
