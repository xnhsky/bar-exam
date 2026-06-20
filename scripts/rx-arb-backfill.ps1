# rx-arb-backfill.ps1
#
# 既存の JX HTML（outputs/001_JX/{科目}JX/*.html）から、Lexia 用の副産物
#   RX      = 論証カード（1論点1HTML / outputs/ux/001_RX/{00N_科目}/{科目}RX{NNN}_{n}.html）
#   TREE    = ARBOR 樹形図（1問1枚 / outputs/ux/002_TREE/{00N_科目}/{科目}JX{NNN}_TREE.html）
#   ARIADNE = 解法ナビ＋周回（1問1枚 / outputs/ux/000_ARIADNE/{00N_科目}/{科目}JX{NNN}_ARIADNE.html）
# が**未生成のものだけ**を後追い生成するバックフィルランナー。
# 新規 JX は jx-batch-runner.ps1 の ②-rx / ②-arb / ②-ariadne 段が自動で副産物を作るので、
# 本スクリプトは「ランナー導入以前に生成済みの JX 資産」を埋めるために使う。
#
# TREE は外部 arbor リポジトリ不在時、canonical/ARBOR.html + validate-tree.py の
# vendored モードへ自動フォールバックする（arbor を持たない PC でも TREE を埋められる）。
#
# 実行例:
#   pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 刑 -DryRun
#   pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 刑 -MaxProblems 3
#   pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 民訴 -SkipArb -SkipAriadne   # RX だけ埋める
#   pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject 刑 -SkipRx -SkipArb          # ARIADNE だけ埋める

param(
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '刑',
    [int]$MaxProblems = 5,              # 1 起動あたり最大処理 JX 数（副産物合計ではなく問題数）
    [int]$FromNumber = 0,
    [int]$ToNumber = 0,
    [switch]$SkipRx,
    [switch]$SkipArb,
    [switch]$SkipAriadne,
    [string]$ArborRoot = 'C:\Users\xnrg2.DESKTOP-5664QR6\arbor',
    [switch]$DryRun
)

$ProjectRoot   = Split-Path -Parent $PSScriptRoot
# 科目 → 00N_科目 サブフォルダ
$SubjDir = switch ($Subject) { '刑'{'001_刑法'} '刑訴'{'002_刑事訴訟法'} '民'{'003_民法'} '商'{'004_商法'} '民訴'{'005_民事訴訟法'} '行政'{'006_行政法'} '憲'{'007_憲法'} default {"$Subject"} }
$JxOutputDir   = Join-Path $ProjectRoot "outputs\001_JX\$SubjDir"
$RxOutputDir   = Join-Path $ProjectRoot "outputs\ux\001_RX\$SubjDir"
$ArbOutputDir  = Join-Path $ProjectRoot "outputs\ux\002_TREE\$SubjDir"
$AriadneOutputDir = Join-Path $ProjectRoot "outputs\ux\000_ARIADNE\$SubjDir"
$LogsDir       = Join-Path $ProjectRoot "logs"
$RxPromptSrc   = Join-Path $ProjectRoot "prompts\new-rx-headless.md"
$ArbPromptSrc  = Join-Path $ProjectRoot "prompts\new-arb-headless.md"
$AriadnePromptSrc = Join-Path $ProjectRoot "prompts\new-ariadne-headless.md"
$ValidateRx    = Join-Path $ProjectRoot "scripts\validate-rx.py"
$ValidateAriadne = Join-Path $ProjectRoot "scripts\validate-ariadne.py"
$CanonicalAriadne = Join-Path $ProjectRoot "canonical\ARIADNE.html"
$ArborMaster   = Join-Path $ArborRoot "ARBOR_v5.0_master_prompt.md"
$ArborRef      = Join-Path $ArborRoot "Reference\ARBOR_002_shucho_tekikaku.html"
$ArborVerify   = Join-Path $ArborRoot "scripts\verify.py"
# 外部 arbor 不在時の vendored フォールバック資産（repo 内）
$CanonicalArbor = Join-Path $ProjectRoot "canonical\ARBOR.html"
$ValidateTree   = Join-Path $ProjectRoot "scripts\validate-tree.py"
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
# 外部 arbor 不在時は vendored モード（canonical/ARBOR.html + validate-tree.py）へフォールバック
if ($ArbEnabled -and -not (Test-Path $ArborMaster)) {
    if ((Test-Path $CanonicalArbor) -and (Test-Path $ValidateTree)) {
        Write-Host "[NOTE] ARBOR 正典不在 → vendored モード（canonical/ARBOR.html + validate-tree.py）で TREE 生成" -ForegroundColor Yellow
        $ArborMaster = $CanonicalArbor; $ArborRef = $CanonicalArbor; $ArborVerify = $ValidateTree
    } else {
        Write-Host "[NOTE] ARBOR 正典不在 かつ vendored 資産も無し → TREE スキップ: $ArborMaster" -ForegroundColor Yellow; $ArbEnabled = $false
    }
}
$AriadneEnabled = (-not $SkipAriadne)
if ($AriadneEnabled -and -not (Test-Path $AriadnePromptSrc)) { Write-Host "[NOTE] ARIADNE prompt 不在 → ARIADNE スキップ" -ForegroundColor Yellow; $AriadneEnabled = $false }
if ($AriadneEnabled -and -not (Test-Path $ValidateAriadne))  { Write-Host "[NOTE] validate-ariadne.py 不在 → ARIADNE スキップ" -ForegroundColor Yellow; $AriadneEnabled = $false }
if ($AriadneEnabled -and -not (Test-Path $CanonicalAriadne)) { Write-Host "[NOTE] canonical ARIADNE 不在 → ARIADNE スキップ: $CanonicalAriadne" -ForegroundColor Yellow; $AriadneEnabled = $false }
if (-not ($RxEnabled -or $ArbEnabled -or $AriadneEnabled)) {
    Write-Host "[ABORT] RX/TREE/ARIADNE とも無効。やることがありません。" -ForegroundColor Red
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
    # RX は問題ごとにサブフォルダ（{科目}JX{NNN}/）へ折る（2026-06-20 恒久化）
    $rxDir   = Join-Path $RxOutputDir $problemId
    $hasRx   = @(Get-ChildItem -Path $rxDir -Filter "${rxBase}_*.html" -File -ErrorAction SilentlyContinue).Count -gt 0
    $arbPath = Join-Path $ArbOutputDir "${problemId}_TREE.html"
    $hasArb  = Test-Path $arbPath
    $ariaPath = Join-Path $AriadneOutputDir "${problemId}_ARIADNE.html"
    $hasAria  = Test-Path $ariaPath
    $needRx  = $RxEnabled -and (-not $hasRx)
    $needArb = $ArbEnabled -and (-not $hasArb)
    $needAria = $AriadneEnabled -and (-not $hasAria)
    if (-not ($needRx -or $needArb -or $needAria)) { continue }
    $Catalog += [PSCustomObject]@{
        ProblemId = $problemId; Number = $num; JxPath = $jx.FullName
        RxBase = $rxBase; RxDir = $rxDir; NeedRx = $needRx; ArbPath = $arbPath; NeedArb = $needArb
        AriaPath = $ariaPath; NeedAria = $needAria
    }
}
$Targets = @($Catalog | Sort-Object { [int]$_.Number } | Select-Object -First $MaxProblems)

Write-Host "`n--- 副産物が欠けている JX: $($Catalog.Count) 件 / 本起動の処理対象: $($Targets.Count) 件 ---" -ForegroundColor Yellow
foreach ($t in $Targets) {
    $needs = @(); if ($t.NeedRx) { $needs += 'RX' }; if ($t.NeedArb) { $needs += 'TREE' }; if ($t.NeedAria) { $needs += 'ARIADNE' }
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
        if (-not (Test-Path $t.RxDir)) { New-Item -Path $t.RxDir -ItemType Directory -Force | Out-Null }
        $rxTemplate = Get-Content $RxPromptSrc -Raw -Encoding utf8
        $rxPrompt = $rxTemplate `
            -replace '\{SOURCE_HTML_PATH\}', $t.JxPath `
            -replace '\{PROBLEM_ID\}',       $t.ProblemId `
            -replace '\{PROBLEM_NUMBER\}',   $t.Number `
            -replace '\{SUBJECT_PREFIX\}',   $Subject `
            -replace '\{RX_BASENAME\}',      $t.RxBase `
            -replace '\{OUTPUT_DIR\}',       $t.RxDir `
            -replace '\{VALIDATE_RX\}',      $ValidateRx
        $rxRes = Invoke-ClaudeHeadless -Prompt $rxPrompt -JsonOutPath (Join-Path $LogsDir "rx-$($t.ProblemId).json")
        $rxSent = Get-Sentinel -Text $rxRes.Output -ProblemId "$($t.ProblemId)-RX"
        $rxFiles = @(Get-ChildItem -Path $t.RxDir -Filter "$($t.RxBase)_*.html" -File -ErrorAction SilentlyContinue).Count
        $rxValidate = "skipped_no_files"
        if ($rxFiles -gt 0) {
            $rvOut = & python $ValidateRx $t.RxDir $t.RxBase 2>&1
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

    if ($t.NeedAria) {
        Write-Host "--- ARIADNE 生成 $(Get-Date -Format 'HH:mm:ss') ---" -ForegroundColor Cyan
        $ariaStart = Get-Date
        if (-not (Test-Path $AriadneOutputDir)) { New-Item -Path $AriadneOutputDir -ItemType Directory -Force | Out-Null }
        $ariaTemplate = Get-Content $AriadnePromptSrc -Raw -Encoding utf8
        $ariaPrompt = $ariaTemplate `
            -replace '\{JX_HTML\}',    $t.JxPath `
            -replace '\{SKELETON\}',   $CanonicalAriadne `
            -replace '\{OUT\}',        $t.AriaPath `
            -replace '\{PROBLEM_ID\}', $t.ProblemId `
            -replace '\{SUBJECT\}',    $Subject `
            -replace '\{NNN\}',        $t.Number
        $ariaRes = Invoke-ClaudeHeadless -Prompt $ariaPrompt -JsonOutPath (Join-Path $LogsDir "ariadne-$($t.ProblemId).json")
        $ariaSent = Get-Sentinel -Text $ariaRes.Output -ProblemId "$($t.ProblemId)-ARIADNE"
        $ariaBytes = if (Test-Path $t.AriaPath) { (Get-Item $t.AriaPath).Length } else { 0 }
        $ariaValidate = "no_html"
        if ($ariaBytes -gt 0) {
            $avOut = & python $ValidateAriadne $t.AriaPath 2>&1
            $ariaValidate = if ($LASTEXITCODE -eq 0) { "PASS" } else { "ERROR(exit=$LASTEXITCODE)" }
            ($avOut -join "`n") | Out-File -FilePath (Join-Path $LogsDir "ariadne-validate-$($t.ProblemId).txt") -Encoding utf8
        }
        $ariaElapsed = [int]((Get-Date) - $ariaStart).TotalSeconds
        Write-Host "[ARIADNE DONE] bytes=$ariaBytes, sentinel=$ariaSent, validate=$ariaValidate" -ForegroundColor $(if ($ariaValidate -eq 'PASS') { 'Green' } else { 'Yellow' })
        Add-Content -Path $RxArbCsv -Encoding utf8 -Value (@(
            (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Subject, $t.ProblemId, 'ARIADNE',
            $ariaElapsed, $ariaBytes, $ariaSent, $ariaRes.ExitCode, $ariaValidate) -join ',')
    }
}

Write-Host "`n=== rx-arb-backfill 終了 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "コストログ: $RxArbCsv"
Stop-Transcript | Out-Null
exit 0
