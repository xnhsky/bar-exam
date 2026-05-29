# jx-batch-runner.ps1
#
# JX→TTS 自動化バッチランナー（commit2 本丸）。
# inputs/jx-pdfs/ の未生成 PDF を最若番から処理し、1 問あたり 2 段で通す：
#   ① claude -p (prompts/new-jx-headless.md)  PDF → JX HTML
#   ② python validate-jx.py                    exit 0 = PASS（ERROR 0・WARNING 許容）
#   ③ claude -p (prompts/tts-jx-headless.md)   JX HTML → TTS 台本（既存 prompt 流用）
#   ④ python validate-tts.py                   exit 0 = PASS
# ②が exit≠0 / HTML 未生成 / sentinel=FAILED の場合は③④をスキップ。
# 成功しても PDF は削除しない（保持）。Drive/Backup 配信も行わない。
#
# 実行例:
#   pwsh -NoProfile -File scripts/jx-batch-runner.ps1 -DryRun
#   pwsh -NoProfile -File scripts/jx-batch-runner.ps1 -Subject 刑 -MaxProblems 3
#   pwsh -NoProfile -File scripts/jx-batch-runner.ps1 -Subject 民訴
#
# 既知の対策:
#   - sentinel は Select-String / -match で grep 検出（JSON parse は脆弱なため不使用）
#   - validate の PASS 判定は $LASTEXITCODE（0=PASS）を主、sentinel grep を従とする
#   - エンコーディングは UTF-8（pwsh 7.x 想定）

param(
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '刑',            # 科目接頭辞（出力先・PROBLEM_ID・配色アンカーに使用）
    [int]$MaxProblems = 5,              # 1 起動あたり最大処理数
    [int]$MaxConsecutiveFailures = 3,   # 連続失敗で abort
    [switch]$DryRun                     # 実 claude -p 呼ばず検出・パス解決・スキップ判定のみ
)

# === パス定義 ===
# スクリプト自身の位置 (= scripts\) の親をプロジェクトルートとする
$ProjectRoot   = Split-Path -Parent $PSScriptRoot
$PdfDir        = Join-Path $ProjectRoot "inputs\jx-pdfs"
$JxOutputBase  = Join-Path $ProjectRoot "outputs\jx"
$TtsOutputBase = Join-Path $ProjectRoot "outputs\tts"
$LogsDir       = Join-Path $ProjectRoot "logs"

$JxPromptSrc   = Join-Path $ProjectRoot "prompts\new-jx-headless.md"
$TtsPromptSrc  = Join-Path $ProjectRoot "prompts\tts-jx-headless.md"
$ValidateJx    = Join-Path $ProjectRoot "scripts\validate-jx.py"
$ValidateTts   = Join-Path $ProjectRoot "scripts\validate-tts.py"

$CostCsv       = Join-Path $LogsDir "jx-cost-summary.csv"
$RunLog        = Join-Path $LogsDir "jx-batch-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# 科目接頭辞 → 出力ディレクトリ名（{Subject}JX）
$SubjectDir    = "${Subject}JX"
$JxOutputDir   = Join-Path $JxOutputBase $SubjectDir

# === stdout/stderr UTF-8 化 ===
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# === logs ディレクトリ確保 ===
if (-not (Test-Path $LogsDir)) { New-Item -Path $LogsDir -ItemType Directory -Force | Out-Null }

# === 開始ログ ===
Start-Transcript -Path $RunLog -Append | Out-Null

Write-Host "=== jx-batch-runner 開始 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "Subject: $Subject (接頭=$SubjectDir) / MaxProblems: $MaxProblems / MaxConsecutiveFailures: $MaxConsecutiveFailures / DryRun: $DryRun"
Write-Host "PDF dir   : $PdfDir"
Write-Host "JX  output: $JxOutputDir"
Write-Host "TTS output: $TtsOutputBase\{PROBLEM_ID}\"

# === 前提ファイル存在確認 ===
$missing = @()
if (-not (Test-Path $PdfDir))       { $missing += "PDF dir: $PdfDir" }
if (-not (Test-Path $JxPromptSrc))  { $missing += "JX prompt: $JxPromptSrc" }
if (-not (Test-Path $TtsPromptSrc)) { $missing += "TTS prompt: $TtsPromptSrc" }
if (-not (Test-Path $ValidateJx))   { $missing += "validate-jx: $ValidateJx" }
if (-not (Test-Path $ValidateTts))  { $missing += "validate-tts: $ValidateTts" }
if ($missing.Count -gt 0) {
    Write-Host "[ABORT] 前提ファイルが見つかりません:" -ForegroundColor Red
    foreach ($m in $missing) { Write-Host "  - $m" -ForegroundColor Red }
    Stop-Transcript | Out-Null
    exit 1
}

# === 出力ディレクトリ確保 ===
if (-not (Test-Path $JxOutputDir)) { New-Item -Path $JxOutputDir -ItemType Directory -Force | Out-Null }

# === PDF 検出と分類（PENDING / SKIP_EXISTS）===
# inputs/jx-pdfs/{NNN}.pdf を列挙。既に {Subject}JX{NNN}.html があれば SKIP_EXISTS。
$AllPdfs = Get-ChildItem -Path $PdfDir -Filter "*.pdf" | Sort-Object Name
$Catalog = @()
foreach ($pdf in $AllPdfs) {
    $raw = [System.IO.Path]::GetFileNameWithoutExtension($pdf.Name)
    # ファイル名先頭の連続数字を抽出（例: "32a" → "32", "032_x" → "032"）
    if ($raw -match '^\d+') {
        $num = ([int]$Matches[0]).ToString('000')  # 3 桁ゼロ埋め
    } else {
        # 数字抽出不能：処理対象外として記録のみ（headless でも判定不能なため事前除外）
        $Catalog += [PSCustomObject]@{
            PdfPath = $pdf.FullName; Number = $null; ProblemId = $null
            JxOutputPath = $null; TtsOutputDir = $null; Status = "SKIP_NONUMERIC"
        }
        continue
    }
    $problemId    = "${Subject}JX${num}"
    $jxOutputPath = Join-Path $JxOutputDir "${problemId}.html"
    $ttsOutputDir = Join-Path $TtsOutputBase $problemId
    $status = if (Test-Path $jxOutputPath) { "SKIP_EXISTS" } else { "PENDING" }
    $Catalog += [PSCustomObject]@{
        PdfPath      = $pdf.FullName
        Number       = $num
        ProblemId    = $problemId
        JxOutputPath = $jxOutputPath
        TtsOutputDir = $ttsOutputDir
        Status       = $status
    }
}

$Pending = @($Catalog | Where-Object { $_.Status -eq "PENDING" })
$Targets = @($Pending | Select-Object -First $MaxProblems)

# === 検出結果サマリ ===
Write-Host "`n--- PDF 検出結果（全 $($Catalog.Count) 件）---" -ForegroundColor Yellow
foreach ($c in $Catalog) {
    $color = switch ($c.Status) {
        "PENDING"        { "Green" }
        "SKIP_EXISTS"    { "DarkGray" }
        "SKIP_NONUMERIC" { "Red" }
    }
    $idText = if ($c.ProblemId) { $c.ProblemId } else { "(番号抽出不能)" }
    Write-Host ("  [{0,-14}] {1}  <- {2}" -f $c.Status, $idText, (Split-Path $c.PdfPath -Leaf)) -ForegroundColor $color
}
Write-Host "`nPENDING: $($Pending.Count) 件 / 本起動の処理対象: $($Targets.Count) 件（最大 $MaxProblems）" -ForegroundColor Yellow

if ($Targets.Count -eq 0) {
    Write-Host "処理対象（PENDING）なし、終了。" -ForegroundColor Green
    Stop-Transcript | Out-Null
    exit 0
}

# === DryRun はパス解決の確認まで ===
if ($DryRun) {
    Write-Host "`n[DRY-RUN] 以下を処理予定（claude -p / validate は呼ばない）:" -ForegroundColor Yellow
    foreach ($t in $Targets) {
        Write-Host "  ● $($t.ProblemId)" -ForegroundColor Cyan
        Write-Host "      PDF        : $($t.PdfPath)"
        Write-Host "      ① JX 出力  : $($t.JxOutputPath)"
        Write-Host "      ② validate : python `"$ValidateJx`" `"$($t.JxOutputPath)`""
        Write-Host "      ③ TTS 出力 : $($t.TtsOutputDir)\"
        Write-Host "      ④ validate : python `"$ValidateTts`" `"$($t.TtsOutputDir)`" $($t.ProblemId)"
    }
    Write-Host "`n[DRY-RUN] 終了（実生成なし）。" -ForegroundColor Yellow
    Stop-Transcript | Out-Null
    exit 0
}

# === コスト CSV ヘッダ初期化（初回のみ）===
$CsvHeader = "timestamp,subject,problem_id,jx_elapsed,jx_html_bytes,jx_sentinel,jx_exit,jx_validate,tts_elapsed,tts_file_count,tts_sentinel,tts_exit,tts_validate,overall"
if (-not (Test-Path $CostCsv)) {
    $CsvHeader | Out-File -FilePath $CostCsv -Encoding utf8
}

# === claude -p 共通起動ヘルパ ===
# プロンプト本文を渡して JSON 出力で起動し、生出力とexit codeを返す
function Invoke-ClaudeHeadless {
    param([string]$Prompt, [string]$JsonOutPath)
    $claudeArgs = @(
        '-p', $Prompt,
        '--output-format', 'json',
        '--permission-mode', 'acceptEdits',
        '--allowedTools', 'Write,Edit,Read,Bash,Glob,Grep'
    )
    try {
        $out = & claude @claudeArgs 2>&1
        $code = $LASTEXITCODE
    } catch {
        $out = "$_"
        $code = -1
    }
    $out | Out-File -FilePath $JsonOutPath -Encoding utf8
    return [PSCustomObject]@{ Output = ($out -join "`n"); ExitCode = $code }
}

# sentinel grep（PROBLEM_ID 限定）
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

# === 1 問処理ループ ===
$ConsecutiveFailures = 0
$ProcessedCount = 0

foreach ($t in $Targets) {
    Write-Host "`n==================== [$($t.ProblemId)] ====================" -ForegroundColor Cyan

    # ----- 初期化 -----
    $jxElapsed = 0; $jxBytes = 0; $jxSentinel = "UNKNOWN"; $jxExit = $null; $jxValidate = "skipped"
    $ttsElapsed = 0; $ttsCount = 0; $ttsSentinel = "skipped"; $ttsExit = $null; $ttsValidate = "skipped"
    $overall = "INCOMPLETE"

    # =========================================================
    # ① JX 生成（claude -p / new-jx-headless.md）
    # =========================================================
    Write-Host "`n--- ① JX 生成開始 $(Get-Date -Format 'HH:mm:ss')（推定 1〜2 時間）---" -ForegroundColor Cyan
    $jxStart = Get-Date

    $jxTemplate = Get-Content $JxPromptSrc -Raw -Encoding utf8
    $jxPrompt = $jxTemplate `
        -replace '\{TARGET_PDF\}',      $t.PdfPath `
        -replace '\{PROBLEM_NUMBER\}',  $t.Number `
        -replace '\{PROBLEM_ID\}',      $t.ProblemId `
        -replace '\{OUTPUT_PATH\}',     $t.JxOutputPath `
        -replace '\{SUBJECT_PREFIX\}',  $Subject
    ($jxPrompt) | Out-File -FilePath (Join-Path $LogsDir "jx-prompt-$($t.ProblemId).txt") -Encoding utf8

    $jxRes = Invoke-ClaudeHeadless -Prompt $jxPrompt -JsonOutPath (Join-Path $LogsDir "jx-$($t.ProblemId).json")
    $jxExit = $jxRes.ExitCode
    $jxElapsed = [int]((Get-Date) - $jxStart).TotalSeconds
    $jxSentinel = Get-Sentinel -Text $jxRes.Output -ProblemId $t.ProblemId
    if (Test-Path $t.JxOutputPath) { $jxBytes = (Get-Item $t.JxOutputPath).Length }

    Write-Host "[① DONE] elapsed=$([math]::Round($jxElapsed/60,1))min, html=$jxBytes bytes, sentinel=$jxSentinel, exit=$jxExit"

    # ----- ② validate-jx（exit 0 = PASS）-----
    $jxPass = $false
    if ($jxBytes -gt 0 -and $jxSentinel -ne "FAILED") {
        Write-Host "--- ② validate-jx.py ---"
        $vOut = & python $ValidateJx $t.JxOutputPath 2>&1
        $vCode = $LASTEXITCODE
        ($vOut -join "`n") | Out-File -FilePath (Join-Path $LogsDir "jx-validate-$($t.ProblemId).txt") -Encoding utf8
        if ($vCode -eq 0) {
            $jxValidate = "PASS"; $jxPass = $true
            Write-Host "[② validate-jx] PASS (exit 0)" -ForegroundColor Green
        } else {
            $jxValidate = "ERROR(exit=$vCode)"
            Write-Host "[② validate-jx] ERROR (exit $vCode) — TTS 段スキップ" -ForegroundColor Yellow
        }
    } else {
        $jxValidate = "skipped_no_html"
        Write-Host "[② validate-jx] スキップ（HTML 未生成 or FAILED）" -ForegroundColor Yellow
    }

    # =========================================================
    # ③ TTS 生成（jxPass 時のみ / tts-jx-headless.md）
    # =========================================================
    if ($jxPass) {
        Write-Host "`n--- ③ TTS 生成開始 $(Get-Date -Format 'HH:mm:ss')---" -ForegroundColor Cyan
        $ttsStart = Get-Date
        if (-not (Test-Path $t.TtsOutputDir)) { New-Item -Path $t.TtsOutputDir -ItemType Directory -Force | Out-Null }

        $ttsTemplate = Get-Content $TtsPromptSrc -Raw -Encoding utf8
        $ttsPrompt = $ttsTemplate `
            -replace '\{SOURCE_HTML_PATH\}', $t.JxOutputPath `
            -replace '\{PROBLEM_ID\}',       $t.ProblemId `
            -replace '\{OUTPUT_DIR\}',       $t.TtsOutputDir
        ($ttsPrompt) | Out-File -FilePath (Join-Path $LogsDir "tts-prompt-$($t.ProblemId).txt") -Encoding utf8

        $ttsRes = Invoke-ClaudeHeadless -Prompt $ttsPrompt -JsonOutPath (Join-Path $LogsDir "tts-$($t.ProblemId).json")
        $ttsExit = $ttsRes.ExitCode
        $ttsElapsed = [int]((Get-Date) - $ttsStart).TotalSeconds
        $ttsSentinel = Get-Sentinel -Text $ttsRes.Output -ProblemId $t.ProblemId
        $ttsCount = @(Get-ChildItem -Path $t.TtsOutputDir -Filter "*.txt" -ErrorAction SilentlyContinue).Count

        Write-Host "[③ DONE] elapsed=$([math]::Round($ttsElapsed/60,1))min, files=$ttsCount, sentinel=$ttsSentinel, exit=$ttsExit"

        # ----- ④ validate-tts（exit 0 = PASS）-----
        if ($ttsCount -gt 0 -and $ttsSentinel -ne "FAILED") {
            Write-Host "--- ④ validate-tts.py ---"
            $tvOut = & python $ValidateTts $t.TtsOutputDir $t.ProblemId 2>&1
            $tvCode = $LASTEXITCODE
            ($tvOut -join "`n") | Out-File -FilePath (Join-Path $LogsDir "tts-validate-$($t.ProblemId).txt") -Encoding utf8
            if ($tvCode -eq 0) {
                $ttsValidate = "PASS"
                Write-Host "[④ validate-tts] PASS (exit 0)" -ForegroundColor Green
            } else {
                $ttsValidate = "ERROR(exit=$tvCode)"
                Write-Host "[④ validate-tts] ERROR (exit $tvCode)" -ForegroundColor Yellow
            }
        } else {
            $ttsValidate = "skipped_no_txt"
            Write-Host "[④ validate-tts] スキップ（.txt 未生成 or FAILED）" -ForegroundColor Yellow
        }
    } else {
        Write-Host "`n--- ③④ TTS 段スキップ（JX validate 未達）---" -ForegroundColor Yellow
    }

    # =========================================================
    # 総合判定（PDF は削除しない・配信もしない）
    # =========================================================
    if ($jxPass -and $ttsValidate -eq "PASS") {
        $overall = "OK"
        Write-Host "`n[OVERALL] $($t.ProblemId): OK（両段 PASS・PDF は保持）" -ForegroundColor Green
    } elseif ($jxSentinel -eq "FAILED" -or $jxBytes -eq 0) {
        $overall = "JX_FAILED"
        Write-Host "`n[OVERALL] $($t.ProblemId): JX_FAILED" -ForegroundColor Red
    } else {
        $overall = "PARTIAL"
        Write-Host "`n[OVERALL] $($t.ProblemId): PARTIAL（要確認・PDF は保持）" -ForegroundColor Yellow
    }

    # ----- コスト CSV 追記 -----
    $csvLine = @(
        (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Subject, $t.ProblemId,
        $jxElapsed, $jxBytes, $jxSentinel, $jxExit, $jxValidate,
        $ttsElapsed, $ttsCount, $ttsSentinel, $ttsExit, $ttsValidate, $overall
    ) -join ','
    Add-Content -Path $CostCsv -Value $csvLine -Encoding utf8

    # ----- 連続失敗判定 -----
    if ($overall -eq "JX_FAILED" -or $jxExit -ne 0 -or $jxBytes -eq 0) {
        $ConsecutiveFailures++
        Write-Host "[WARN] 連続失敗: $ConsecutiveFailures / $MaxConsecutiveFailures" -ForegroundColor Yellow
        if ($ConsecutiveFailures -ge $MaxConsecutiveFailures) {
            Write-Host "[ABORT] 連続失敗 $MaxConsecutiveFailures 件に達したため中断。" -ForegroundColor Red
            break
        }
    } else {
        $ConsecutiveFailures = 0
    }

    $ProcessedCount++
}

Write-Host "`n=== jx-batch-runner 終了 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "処理件数: $ProcessedCount / $($Targets.Count)"
Write-Host "コストログ: $CostCsv"

Stop-Transcript | Out-Null
exit 0
