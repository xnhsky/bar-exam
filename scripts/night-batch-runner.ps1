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
    [int]$FromNumber = 0,              # 処理対象の最小問題番号 (0 = 下限なし)
    [int]$ToNumber = 0,                # 処理対象の最大問題番号 (0 = 上限なし)
    [switch]$DryRun,                   # 実 claude -p 呼ばずパス解決確認のみ
    [string]$ProjectRoot = '',         # 別 clone/root で生成する場合に指定（未指定はこの repo）
    [ValidateSet('v13','v10.0.0','v9.2.0','v9.1.0')]
    [string]$SpecVersion = 'v10.0.0',  # 既定 v10.0.0 GOLD-SKELETON（GENESIS baseline）／v13 で LOOP-CARD 二系統
    [ValidateSet('刑','刑訴','民','商','民訴','行政','憲')]
    [string]$Subject = '刑'            # 科目接頭辞。入力=inputs/000_TX/{科目}/・出力=科目別サブフォルダ
)

# === spec ファイル・プロンプト・検証スクリプトの選択 ===
# v13：canonical/GENESIS-CARD.html を起点とした LOOP-CARD 二系統経路（公式＋_lex・旧レイアウト移行）
# v10.0.0：canonical/GENESIS.html を起点としたスケルトン経路（spec md は持たず new-tx.md が正典）
# v9.2.0：旧 DEEP-DIVE 経路（spec md + render.py 想定）
# v9.1.0：旧 MINDMAP 経路
$SpecFile = switch ($SpecVersion) {
    'v13'     { '.claude/commands/new-tx.md' }
    'v10.0.0' { '.claude/commands/new-tx.md' }
    'v9.2.0'  { 'spec/legacy/tx-v9.2.0-deepdive-core.md' }
    'v9.1.0'  { 'spec/legacy/tx-v9.1.0-mindmap-core.md' }
    default   { throw "Unknown spec version: $SpecVersion" }
}
$SpecVersionTag = switch ($SpecVersion) {
    'v13'     { 'TX v13.0.0 LOOP-CARD' }
    'v10.0.0' { 'TX v10.0.0 GOLD-SKELETON' }
    'v9.2.0'  { 'TX v9.2.0 DEEP-DIVE' }
    'v9.1.0'  { 'TX v9.1.0 MINDMAP' }
}
$PromptFile = switch ($SpecVersion) {
    'v13'     { 'prompts/new-tx-headless-v13.md' }
    'v10.0.0' { 'prompts/new-tx-headless-v10.md' }
    default   { 'prompts/new-tx-headless-v0.md' }
}
$ValidateScript = switch ($SpecVersion) {
    'v13'     { 'scripts/validate-tx-core.py' }
    'v10.0.0' { 'scripts/validate-tx-gold.py' }
    default   { 'scripts/validate-tx.py' }
}
# v13：core validator PASS 判定の regex（"Errors: 0"）
# v10.0.0：gold validator PASS 判定の regex（"Errors: 0" or "ALL G1〜G16 PASS"）
# v9.x：従来 validator PASS 判定（"ERROR 0 /"）
$ValidatePassRegex = switch ($SpecVersion) {
    'v13'     { 'Errors:\s*0\b' }
    'v10.0.0' { 'Errors:\s*0\b' }
    default   { 'ERROR\s*0\s*/' }
}

# === 設定 ===
# スクリプト自身の位置 (= scripts\) の親を既定プロジェクトルートとする。
# -ProjectRoot / BAREXAM_PROJECT_ROOT 指定時は別 clone/root へ明示的に逃がせる。
$DefaultProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
# 科目解決（-Subject で切替・既定 刑）。接頭辞→科目フォルダ（inputs/outputs 共通の 00N_科目）。
$SubjectPrefix = $Subject
$SubjectFolder = switch ($SubjectPrefix) { '刑'{'001_刑法'} '刑訴'{'002_刑事訴訟法'} '民'{'003_民法'} '商'{'004_商法'} '民訴'{'005_民事訴訟法'} '行政'{'006_行政法'} '憲'{'007_憲法'} default {"${SubjectPrefix}TX"} }
$PdfDir      = Join-Path $ProjectRoot (Join-Path "inputs\000_TX" $SubjectFolder)
$OutputBase  = Join-Path $ProjectRoot "outputs\000_TX"
$LogsDir     = Join-Path $ProjectRoot "logs"
$PromptSource= Join-Path $ProjectRoot ($PromptFile -replace '/', '\')
$CostCsv     = Join-Path $LogsDir "cost-summary.csv"
$RunLog      = Join-Path $LogsDir "night-batch-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# === stdout/stderr UTF-8 化 ===
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# === 開始ログ ===
Start-Transcript -Path $RunLog -Append

# === スリープ抑止（self-contained・DryRun 以外）===
# 長時間バッチ中の PC スリープ/ディスプレイ停止を防ぐ。ES_CONTINUOUS はスレッド/プロセスに
# 紐づくため、本 runner プロセス終了で OS が自動的に既定の電源ポリシーへ復帰する（明示解除不要）。
# NBR 共通方針（feedback_nbr_keep_awake）に従い TX runner も自己完結で組み込む（JX runner と対称）。
if (-not $DryRun) {
    try {
        $sig = '[DllImport("kernel32.dll", SetLastError=true)] public static extern uint SetThreadExecutionState(uint esFlags);'
        $PW = Add-Type -MemberDefinition $sig -Name PW -Namespace Win32 -PassThru -ErrorAction Stop
        # ES_CONTINUOUS(0x80000000)|ES_SYSTEM_REQUIRED(0x1)|ES_DISPLAY_REQUIRED(0x2)
        [void]$PW::SetThreadExecutionState([uint32]2147483651)
        Write-Host "[KEEP-AWAKE] スリープ抑止 ON（プロセス終了で自動復帰）" -ForegroundColor DarkGray
    } catch {
        Write-Host "[KEEP-AWAKE] 抑止設定に失敗（続行）: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "=== night-batch-runner 開始 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "MaxProblems: $MaxProblems / MaxConsecutiveFailures: $MaxConsecutiveFailures / DryRun: $DryRun"
Write-Host "SpecVersion: $SpecVersion / Subject: $Subject / SpecFile: $SpecFile"
Write-Host "NumberRange: From=$FromNumber To=$ToNumber (0 = 無制限)"

# === 科目接頭辞・出力先（$SubjectPrefix/$SubjectFolder は上部で -Subject から解決済み）===
# PDF は inputs/000_TX/{科目}/{NNN}.pdf、生成出力は {科目接頭辞}TX{NNN}.html。
# 生成は local outputs/000_TX/{科目}/ へ。validate PASS 後に Drive と backup へ配信。
$OutputDir = Join-Path $OutputBase $SubjectFolder
# v13 二系統：Lexia 用 _lex の出力先 outputs\ux\000_TX\{科目}（移行 pending 判定に使う）。
$LexOutputDir = Join-Path (Join-Path $ProjectRoot "outputs\ux\000_TX") $SubjectFolder
# Drive 配信先：マイドライブのマウント先(C:/G:/H: 等)とフォルダ改名に強いよう、
# CATALINA＿G共有 を含むマイドライブを自動検出し、科目フォルダ直下をパターン解決する。
# 配信規律(2026-06-01 ユーザー指示)：HTML は各科目フォルダ「直下」に置く
# （"改訂版はここ" 等のサブフォルダには入れない）。
# 旧実装は $env:USERPROFILE\マイドライブ 固定＋旧フォルダ名（"1 短 答\☆TX\…\改訂版はここ"）で、
# xnrg2 PC（H:\マイドライブ・"1 TX_短 答"・科目直下）では全配信が失敗していた。
# 科目接頭辞 → Drive 科目フォルダ番号（"{番号}_{科目名}" に前方一致）
$DriveSubjectPat = switch ($SubjectPrefix) {
    "刑"   { "001_*" }   # 001_刑法
    "刑訴" { "002_*" }   # 002_刑事訴訟法
    "民"   { "003_*" }   # 003_民法
    "商"   { "004_*" }   # 004_商法
    "民訴" { "005_*" }   # 005_民事訴訟法
    "行政" { "006_*" }   # 006_行政法
    "憲"   { "007_*" }   # 007_憲法
    default { $null }
}
$DriveDir = $null
foreach ($myDrive in @(
        (Join-Path $env:USERPROFILE "マイドライブ"),
        "H:\マイドライブ", "G:\マイドライブ",
        (Join-Path $env:USERPROFILE "Google ドライブ"),
        (Join-Path $env:USERPROFILE "Google Drive"),
        "H:\My Drive", "G:\My Drive")) {
    $yobi = Join-Path (Join-Path $myDrive "CATALINA＿G共有") "■予備試験進行中"
    if (-not (Test-Path $yobi)) { continue }
    $txDir = Get-ChildItem $yobi -Directory -ErrorAction SilentlyContinue |
             Where-Object Name -like "1 TX*" | Select-Object -First 1
    if (-not $txDir -or -not $DriveSubjectPat) { continue }
    $subjDir = Get-ChildItem $txDir.FullName -Directory -ErrorAction SilentlyContinue |
               Where-Object Name -like $DriveSubjectPat | Select-Object -First 1
    if ($subjDir) { $DriveDir = $subjDir.FullName; break }
}
if (-not $DriveDir) {
    # 見つからなければ非存在パスを既定にし、配信時に [DELIVER FAIL] を出して継続
    # （backup には必ず配信されるので消失はしない）
    $DriveDir = Join-Path $env:USERPROFILE "マイドライブ\CATALINA＿G共有(未検出)"
}
$BackupDir = "C:\bar-exam-backup\current\${SubjectPrefix}TX"
if (-not (Test-Path $OutputDir)) { New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null }
if (-not (Test-Path $BackupDir)) { New-Item -Path $BackupDir -ItemType Directory -Force | Out-Null }

# === 未生成 PDF の検出 ===
$AllPdfs = Get-ChildItem -Path $PdfDir -Filter "*.pdf" | Sort-Object Name
$Pending = @()
foreach ($pdf in $AllPdfs) {
    $rawNum = [System.IO.Path]::GetFileNameWithoutExtension($pdf.Name)
    $isNumeric = $rawNum -match '^\d+$'
    # レンジ絞り込み（最若番優先の既定動作に対し、特定番号帯だけを対象にする catch-up 用）。
    # FromNumber / ToNumber が 0 のときは無制限（＝従来動作を完全保持）。
    if ($FromNumber -gt 0 -or $ToNumber -gt 0) {
        if (-not $isNumeric) { continue }                                   # 番号なし PDF はレンジ指定時は対象外
        $numInt = [int]$rawNum
        if ($FromNumber -gt 0 -and $numInt -lt $FromNumber) { continue }
        if ($ToNumber  -gt 0 -and $numInt -gt $ToNumber)   { continue }
    }
    # CLAUDE.md §2-3: 3 桁未満は前ゼロで 0 埋め (45 → 045)。4 桁以上は ToString('000') が保持。
    $num = if ($isNumeric) { ([int]$rawNum).ToString('000') } else { $rawNum }
    $expectedHtml = Join-Path $OutputDir "${SubjectPrefix}TX${num}.html"
    if ($SpecVersion -eq 'v13') {
        # v13 は「旧レイアウト _lex の移行」なので公式 HTML の有無では判定できない
        # （移行対象は公式・_lex が既に存在する）。判定は _lex が v13 エンジン
        # （getInlineAnswerTablePanel）を持つか＝未移行なら pending。再実行は冪等
        # （移行済み v13 は素通り）。_lex 不在（未 _lex 化）も pending 扱いで拾う。
        $lexPath = Join-Path $LexOutputDir "${SubjectPrefix}TX${num}_lex.html"
        $needsMigration = $true
        if (Test-Path $lexPath) {
            $lexHead = Get-Content -LiteralPath $lexPath -Raw -Encoding utf8 -ErrorAction SilentlyContinue
            if ($lexHead -and $lexHead.Contains('getInlineAnswerTablePanel')) { $needsMigration = $false }
        }
        if ($needsMigration) {
            $Pending += [PSCustomObject]@{
                PdfPath = $pdf.FullName
                Number  = $num
                ProblemId = "${SubjectPrefix}TX${num}"
                OutputPath = $expectedHtml
                LexPath = $lexPath
            }
        }
    } elseif (-not (Test-Path $expectedHtml)) {
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

    # === 実行命令の前置（最重要）===
    # 生プロンプトは冒頭が説明文（"# new-tx-headless-v10.md ..."）のため、claude -p が
    # 仕様書（参照資料）と解釈して「依頼内容が分かりません」と挨拶で終了する事故が発生。
    # 先頭に強い実行命令を前置し、参照資料ではなく実行指示であることを明示する。
    $promptName = [System.IO.Path]::GetFileNameWithoutExtension($PromptFile)
    $execDirective = @"
【最優先・実行指示 / headless】これは参照資料ではなく実行命令である。あなたは今すぐ
TX 問題 $($target.ProblemId) を生成するタスクを実行せよ。挨拶・確認・「依頼内容を
教えてください」「内容が表示されているだけ」等の応答は禁止。下記手順書（$promptName）に
従い、対象 PDF を読解して直ちに着手し、最後に必ず Section 9/10/11 の
sentinel を 1 つ出力して終了せよ。対象 PDF=$($target.PdfPath) / 出力=$($target.OutputPath)

━━━━━━━━━━━━━━━━ 以下、手順書本体 ━━━━━━━━━━━━━━━━

"@
    $prompt = $execDirective + $prompt

    # プロンプトを一時ファイルに書き出し（debug 用）
    $promptOut = Join-Path $LogsDir "night-prompt-$($target.ProblemId).txt"
    $prompt | Out-File -FilePath $promptOut -Encoding utf8

    # === claude -p 起動 ===
    $jsonOut   = Join-Path $LogsDir "night-$($target.ProblemId).json"
    $resultOut = Join-Path $LogsDir "night-$($target.ProblemId).result.txt"

    # 重要: 大きな複数行プロンプトを `-p $prompt`（引数）で渡すと PowerShell の
    # ネイティブ引数処理で壊れ、claude に未達のまま空プロンプトで起動される
    # （特に nested 実行＝別 claude セッションから起動した場合に再現）。
    # → プロンプトは stdin パイプで渡す（claude -p は引数値が無ければ stdin から読む）。
    # --model を明示固定（2026-06-13）: 既定モデルが claude-fable-5[1m]（アクセス権なし）に
    # 解決され 0秒/0byte/exit1 の即時失敗が連発した事故への対策。動作確認済みモデルに固定する。
    $claudeArgs = @(
        '-p',
        '--model', 'claude-opus-4-8[1m]',
        '--output-format', 'json',
        '--permission-mode', 'acceptEdits',
        '--allowedTools', 'Write,Edit,Read,Bash,Glob,Grep'
    )

    Write-Host "[INFO] claude -p 起動中 (推定 25-30 分)..."

    # 標準出力と stderr 両方をキャプチャ
    try {
        $output = $prompt | & claude @claudeArgs 2>&1
        $exitCode = $LASTEXITCODE
        $output | Out-File -FilePath $jsonOut -Encoding utf8
    } catch {
        Write-Host "[ERROR] claude 起動失敗: $_" -ForegroundColor Red
        $exitCode = -1
        $output = "$_"
    }

    $endTime = Get-Date
    $elapsed = [int]($endTime - $startTime).TotalSeconds

    # === 生成時間異常検知（version-aware）===
    # v10.0.0：想定 20-30 min（baseline clone + section-by-section 鋳造）→ 上限 40 min (2400 秒)
    # v9.x：想定 4-7 min（旧 6 段階 Write）→ 上限 20 min (1200 秒)
    $ElapsedUpperLimit = if ($SpecVersion -eq 'v10.0.0' -or $SpecVersion -eq 'v13') { 2400 } else { 1200 }
    if ($elapsed -gt $ElapsedUpperLimit) {
        Write-Warning "生成時間異常: ${elapsed}秒（上限 ${ElapsedUpperLimit}秒）- claude -p 不完全出力警戒"
        if ($SpecVersion -eq 'v10.0.0') {
            Write-Warning "品質チェック推奨: G1〜G16 / SVG 重なり / genesis-baseline feature-tag"
        } else {
            Write-Warning "品質チェック推奨: feature-tag 33 件 / theory-detail-grid / palette-strategy"
        }
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

    # === v13 移行実測ガード（サイレント no-op 検知）===
    # v13 は「旧レイアウト _lex → LOOP-CARD」への移行。完了後の validate は公式ファイルにしか
    # 走らず、公式は v13 で構造不変なので必ず PASS する。よって claude が旧 _lex を検証しただけで
    # 実移行せず exit0/errors0 を返す no-op（例：会話穴埋め型 刑TX381）を「PASS」と誤報告しうる。
    # そこで完了後に _lex が v13 マーカー（getInlineAnswerTablePanel）を実際に獲得したか確認し、
    # 未獲得なら FAIL 扱いにして成功計上・PDF 保持完了報告を止める（特殊型は個別対応へ回す）。
    $v13NoOp = $false
    if ($SpecVersion -eq 'v13') {
        $lexOk = $false
        if ($target.LexPath -and (Test-Path $target.LexPath)) {
            $lexNow = Get-Content -LiteralPath $target.LexPath -Raw -Encoding utf8 -ErrorAction SilentlyContinue
            if ($lexNow -and $lexNow.Contains('getInlineAnswerTablePanel')) { $lexOk = $true }
        }
        if (-not $lexOk) {
            $v13NoOp = $true
            Write-Host "[V13-NOOP] $($target.ProblemId): _lex が v13 化されていない（未移行の空振り）。FAIL 扱い・要個別対応（特殊型の可能性）。" -ForegroundColor Red
        }
    }

    # === 自動クリーンアップ：成功時のみ PDF を削除 ===
    $cleanupTriggered = $false
    $validateStatus = "skipped"

    if ($htmlBytes -gt 0 -and $exitCode -eq 0 -and $sentinel -ne "FAILED" -and -not $v13NoOp) {
        try {
            $ValidateScriptAbs = Join-Path $ProjectRoot ($ValidateScript -replace '/', '\')
            $validateOutput = & python $ValidateScriptAbs $target.OutputPath 2>&1
            $validateText = $validateOutput -join "`n"
            # PASS 判定（v10.0.0：Errors: 0、v9.x：ERROR 0 /）
            if ($validateText -match $ValidatePassRegex) {
                $validateStatus = "PASS"
                if ($SpecVersion -eq 'v13') {
                    # v13 は「旧レイアウトの移行」。入力 PDF は消さない（再移行のため保持・
                    # PDF は Drive バックアップ済み）。永続化は prompt Section 8 の git commit/push。
                    Write-Host "[KEEP-PDF] $($target.ProblemId): v13 移行のため入力 PDF を保持（validate PASS）" -ForegroundColor Green
                } else {
                    Remove-Item -Path $target.PdfPath -Force
                    $cleanupTriggered = $true
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
    if ($sentinel -eq "FAILED" -or $exitCode -ne 0 -or $htmlBytes -eq 0 -or $v13NoOp) {
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

# === バッチ後監査ゲート: ファイル間の重複・ID 不整合チェック ===
# 各問題は per-item の validate-tx で配信前検証済みだが、それは「1 ファイル内」検査。
# 同一 title・同一本文・footer/title の ID コピペ残り(例 刑TX055←刑TX311)は
# ファイル間でしか分からないため、バッチ終了時に outputs/000_TX 全体を横断チェックする。
# 検出時は exit 1（push 前に気付けるように）。配信自体は per-item で既に済んでいる点に注意。
# v13 は二系統（公式＋ux/000_TX/_lex）を出すため outputs 全体を監査（ミラー除外は check 側）。
$AuditRoot = if ($SpecVersion -eq 'v13') { Join-Path $ProjectRoot 'outputs' } else { Join-Path $ProjectRoot 'outputs\000_TX' }
Write-Host "`n--- バッチ後監査: scripts/check-duplicates.py $AuditRoot ---" -ForegroundColor Cyan
& python (Join-Path $ProjectRoot 'scripts/check-duplicates.py') $AuditRoot
$dupExit = $LASTEXITCODE
if ($dupExit -ne 0) {
    Write-Host "[AUDIT FAIL] 重複/ID 不整合を検出。push 前に上記 D80/D81/D82 を修正してください。" -ForegroundColor Red
} else {
    Write-Host "[AUDIT PASS] ファイル間の重複・ID 不整合なし。" -ForegroundColor Green
}

Stop-Transcript
exit $dupExit
