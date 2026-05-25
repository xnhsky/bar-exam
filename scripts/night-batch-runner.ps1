# night-batch-runner.ps1
#
# Phase D: 夜間自動運用バッチランナー。
# タスクスケジューラから 21:00 / 23:00 / 01:00 / 03:00 / 05:00 の
# 2 時間ごとに起動され、各起動で未生成 PDF を最若番から 5 問処理する。
# 1 問あたり推定 25-30 分。
#
# 実行例:
#   pwsh -NoProfile -File scripts/night-batch-runner.ps1
#   pwsh -NoProfile -File scripts/night-batch-runner.ps1 -DryRun
#   pwsh -NoProfile -File scripts/night-batch-runner.ps1 -MaxProblems 3
#
# 既知の対策:
#   - JSON parse は脆弱なため sentinel は Select-String / -match で grep 検出
#   - エンコーディングは BOM 付き UTF-8 必須（pwsh 7.6.2 想定）

param(
    [int]$MaxProblems = 5,             # 1 起動あたり最大処理数
    [int]$MaxConsecutiveFailures = 3,  # 連続失敗で abort
    [switch]$DryRun,                   # 実 claude -p 呼ばずパス解決確認のみ
    [ValidateSet('v9.2.0','v9.1.0')]
    [string]$SpecVersion = 'v9.2.0'    # 既定 v9.2.0 DEEP-DIVE（TASK12-13 § 5）
)

# === spec ファイル選択（TASK12-13 § 5）===
$SpecFile = switch ($SpecVersion) {
    'v9.2.0' { 'spec/tx-v9.2.0-deepdive-core.md' }
    'v9.1.0' { 'spec/tx-v9.1.0-mindmap-core.md' }
    default  { throw "Unknown spec version: $SpecVersion" }
}
$SpecVersionTag = switch ($SpecVersion) {
    'v9.2.0' { 'TX v9.2.0 DEEP-DIVE' }
    'v9.1.0' { 'TX v9.1.0 MINDMAP' }
}

# === 設定 ===
# スクリプト自身の位置 (= scripts\) の親をプロジェクトルートとする
# これで OWNER PC / xnrg2 PC など複数環境で同じスクリプトが動作する
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PdfDir      = Join-Path $ProjectRoot "inputs\tx-pdfs"
$OutputBase  = Join-Path $ProjectRoot "outputs\tx"
$LogsDir     = Join-Path $ProjectRoot "logs"
$PromptSource= Join-Path $ProjectRoot "prompts\new-tx-headless-v0.md"
$CostCsv     = Join-Path $LogsDir "cost-summary.csv"
$RunLog      = Join-Path $LogsDir "night-batch-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# === stdout/stderr UTF-8 化 ===
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# === 開始ログ ===
Start-Transcript -Path $RunLog -Append

Write-Host "=== night-batch-runner 開始 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "MaxProblems: $MaxProblems / MaxConsecutiveFailures: $MaxConsecutiveFailures / DryRun: $DryRun"
Write-Host "SpecVersion: $SpecVersion / SpecFile: $SpecFile"

# === 科目接頭辞マップ ===
# PDF は inputs/tx-pdfs/{NNN}.pdf 形式だが、生成出力は {科目接頭辞}TX{NNN}.html。
# 現状は刑のみ運用想定（306-315 は全て刑法 PDF）。将来拡張時に番号レンジ判定を追加予定。
$SubjectPrefix = "刑"
# 2026-05-25: local-first write flow に復帰（validate-tx S81 規律維持のため）
# 生成は local outputs/tx/{Prefix}TX/ へ。validate PASS 後に Drive と backup へ配信。
# 旧 DriveFS 直書き ($env:USERPROFILE\マイドライブ\...) は廃止。
$OutputDir = Join-Path $OutputBase "${SubjectPrefix}TX"
$DriveDir  = Join-Path $env:USERPROFILE "マイドライブ\CATALINA＿G共有\■予備試験進行中\1 短 答\☆TX\001＿刑法TX\改訂版はここ"
$BackupDir = "C:\bar-exam-backup\current\${SubjectPrefix}TX"
if (-not (Test-Path $OutputDir)) { New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null }
if (-not (Test-Path $BackupDir)) { New-Item -Path $BackupDir -ItemType Directory -Force | Out-Null }

# === 未生成 PDF の検出 ===
$AllPdfs = Get-ChildItem -Path $PdfDir -Filter "*.pdf" | Sort-Object Name
$Pending = @()
foreach ($pdf in $AllPdfs) {
    $num = [System.IO.Path]::GetFileNameWithoutExtension($pdf.Name)
    # CLAUDE.md §2-3: 3 桁未満は前ゼロで 0 埋め (45 → 045)。4 桁以上は ToString('000') が保持。
    if ($num -match '^\d+$') { $num = ([int]$num).ToString('000') }
    $expectedHtml = Join-Path $OutputDir "${SubjectPrefix}TX${num}.html"
    if (-not (Test-Path $expectedHtml)) {
        $Pending += [PSCustomObject]@{
            PdfPath = $pdf.FullName
            Number  = $num
            ProblemId = "${SubjectPrefix}TX${num}"
            OutputPath = $expectedHtml
        }
    }
}

Write-Host "`n未生成 PDF: $($Pending.Count) 件 (本起動で最大 $MaxProblems 件処理)" -ForegroundColor Yellow
foreach ($p in ($Pending | Select-Object -First $MaxProblems)) {
    Write-Host "  - $($p.ProblemId) <- $($p.PdfPath)"
}

if ($Pending.Count -eq 0) {
    Write-Host "未生成 PDF なし、終了。" -ForegroundColor Green
    Stop-Transcript
    exit 0
}

# === DryRun モードはここまで ===
if ($DryRun) {
    Write-Host "`n[DRY-RUN] claude -p 呼び出しはスキップして終了。" -ForegroundColor Yellow
    Stop-Transcript
    exit 0
}

# === コスト CSV ヘッダ初期化（初回のみ）===
if (-not (Test-Path $CostCsv)) {
    "timestamp,problem_id,elapsed_seconds,html_bytes,sentinel,exit_code,cleanup,validate_status" | Out-File -FilePath $CostCsv -Encoding utf8
} else {
    # 既存 CSV が旧ヘッダーの場合は警告のみ出して継続（古いログは保持）
    $firstLine = Get-Content $CostCsv -TotalCount 1
    if ($firstLine -notmatch "cleanup,validate_status") {
        Write-Host "[WARN] cost-summary.csv has old header format (no cleanup/validate_status columns)." -ForegroundColor Yellow
        Write-Host "[WARN] New rows will be appended with extra fields; old rows remain unchanged." -ForegroundColor Yellow
    }
}

# === 1 問処理ループ ===
$ConsecutiveFailures = 0
$ProcessedCount = 0
$Targets = $Pending | Select-Object -First $MaxProblems

foreach ($target in $Targets) {
    $startTime = Get-Date
    Write-Host "`n=== [$($target.ProblemId)] 開始 $(Get-Date -Format 'HH:mm:ss') ===" -ForegroundColor Cyan

    # === プロンプト読み込み + 変数置換 ===
    $promptTemplate = Get-Content $PromptSource -Raw -Encoding utf8
    $prompt = $promptTemplate `
        -replace '\{TARGET_PDF\}',     $target.PdfPath `
        -replace '\{PROBLEM_NUMBER\}', $target.Number `
        -replace '\{PROBLEM_ID\}',     $target.ProblemId `
        -replace '\{OUTPUT_PATH\}',    $target.OutputPath `
        -replace '\{SPEC_FILE\}',      $SpecFile `
        -replace '\{SPEC_VERSION\}',   $SpecVersion `
        -replace '\{SPEC_VERSION_TAG\}', $SpecVersionTag

    # プロンプトを一時ファイルに書き出し（debug 用）
    $promptOut = Join-Path $LogsDir "night-prompt-$($target.ProblemId).txt"
    $prompt | Out-File -FilePath $promptOut -Encoding utf8

    # === claude -p 起動 ===
    $jsonOut   = Join-Path $LogsDir "night-$($target.ProblemId).json"
    $resultOut = Join-Path $LogsDir "night-$($target.ProblemId).result.txt"

    $claudeArgs = @(
        '-p', $prompt,
        '--output-format', 'json',
        '--permission-mode', 'acceptEdits',
        '--allowedTools', 'Write,Edit,Read,Bash,Glob,Grep'
    )

    Write-Host "[INFO] claude -p 起動中 (推定 25-30 分)..."

    # 標準出力と stderr 両方をキャプチャ
    try {
        $output = & claude @claudeArgs 2>&1
        $exitCode = $LASTEXITCODE
        $output | Out-File -FilePath $jsonOut -Encoding utf8
    } catch {
        Write-Host "[ERROR] claude 起動失敗: $_" -ForegroundColor Red
        $exitCode = -1
        $output = "$_"
    }

    $endTime = Get-Date
    $elapsed = [int]($endTime - $startTime).TotalSeconds

    # === 罠 9 早期警戒: 生成時間異常 (Phase 13C-3) ===
    # 正常実績: 303=4.3 min / 305=6.87 min / 304 v2=28.9 min (regen 完全)
    # 罠 9 発火例: 304 v1=24 min (不完全出力・theory-deep-dive 等 15 tag 欠落)
    # 閾値 20 min (1200 秒) = 正常上限 7 min + バッファ
    if ($elapsed -gt 1200) {
        Write-Warning "生成時間異常: ${elapsed}秒（想定 4-7 min）- 罠 9（claude -p 不完全出力）警戒"
        Write-Warning "品質チェック推奨: feature-tag 33 件 / theory-detail-grid / palette-strategy"
    }

    # === sentinel grep 検出（JSON parse は使わない）===
    $sentinel = "UNKNOWN"
    $outputText = $output -join "`n"
    $outputText | Out-File -FilePath $resultOut -Encoding utf8

    if ($outputText -match "BATCH_ITEM_COMPLETED:$([regex]::Escape($target.ProblemId))") {
        $sentinel = "COMPLETED"
    } elseif ($outputText -match "BATCH_ITEM_COMPLETED_WITH_ISSUES:$([regex]::Escape($target.ProblemId)):errors=(\d+):warnings=(\d+)") {
        $sentinel = "WITH_ISSUES:errors=$($Matches[1]):warnings=$($Matches[2])"
    } elseif ($outputText -match "BATCH_ITEM_FAILED:$([regex]::Escape($target.ProblemId))") {
        $sentinel = "FAILED"
    }

    # === HTML サイズ確認 ===
    $htmlBytes = 0
    if (Test-Path $target.OutputPath) {
        $htmlBytes = (Get-Item $target.OutputPath).Length
    }

    Write-Host "[DONE] $($target.ProblemId): elapsed=$([math]::Round($elapsed/60,1))min, html=$htmlBytes bytes, sentinel=$sentinel, exit=$exitCode" -ForegroundColor Green

    # === 自動クリーンアップ：成功時のみ PDF を削除 ===
    $cleanupTriggered = $false
    $validateStatus = "skipped"

    if ($htmlBytes -gt 0 -and $exitCode -eq 0 -and $sentinel -ne "FAILED") {
        try {
            $validateOutput = & python "$ProjectRoot\scripts\validate-tx.py" $target.OutputPath 2>&1
            $validateText = $validateOutput -join "`n"
            # ERROR 0 を厳密判定（正規表現で「ERROR 0」を捕捉）
            if ($validateText -match "ERROR\s*0\s*/") {
                Remove-Item -Path $target.PdfPath -Force
                $cleanupTriggered = $true
                $validateStatus = "PASS"
                Write-Host "[CLEANUP] $($target.ProblemId): PDF auto-deleted (validate-tx PASS)" -ForegroundColor Green

                # === Deliver to Drive + Backup (validate PASS 時のみ) ===
                try {
                    Copy-Item -Path $target.OutputPath -Destination $DriveDir -Force -ErrorAction Stop
                    Write-Host "[DELIVER] Drive OK: $($target.ProblemId)" -ForegroundColor Green
                } catch {
                    Write-Host "[DELIVER FAIL] Drive: $_" -ForegroundColor Yellow
                }
                try {
                    Copy-Item -Path $target.OutputPath -Destination $BackupDir -Force -ErrorAction Stop
                    Write-Host "[BACKUP]  OK: $($target.ProblemId)" -ForegroundColor Green
                } catch {
                    Write-Host "[BACKUP FAIL] $_" -ForegroundColor Yellow
                }
            } else {
                $validateStatus = "ERROR_detected"
                Write-Host "[KEEP] $($target.ProblemId): PDF retained (validate-tx ERROR detected)" -ForegroundColor Yellow
            }
        } catch {
            $validateStatus = "exec_failed"
            Write-Host "[KEEP] $($target.ProblemId): PDF retained (validate-tx exec failed)" -ForegroundColor Yellow
        }
    } else {
        $validateStatus = "skipped_failed_generation"
        Write-Host "[KEEP] $($target.ProblemId): PDF retained (generation incomplete)" -ForegroundColor Yellow
    }

    # === コスト CSV 追記 ===
    $csvLine = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'),$($target.ProblemId),$elapsed,$htmlBytes,$sentinel,$exitCode,$cleanupTriggered,$validateStatus"
    Add-Content -Path $CostCsv -Value $csvLine -Encoding utf8

    # === 連続失敗判定 ===
    if ($sentinel -eq "FAILED" -or $exitCode -ne 0 -or $htmlBytes -eq 0) {
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

Write-Host "`n=== night-batch-runner 終了 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "処理件数: $ProcessedCount / $($Targets.Count)"
Write-Host "コストログ: $CostCsv"

Stop-Transcript
exit 0
