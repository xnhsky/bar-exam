# jx-batch-runner.ps1
#
# JX→TTS→音声 一気通貫バッチランナー（v2: 逐語入力＋PDF削除＋音声全自動）。
# inputs/jx-pdfs/ の「PDF＋同番号の講義逐語(.txt/.md)」を最若番から処理し、
# 1 問あたり以下の段で通す：
#   ① claude -p (prompts/new-jx-headless.md)  PDF＋逐語 → JX HTML
#   ② python validate-jx.py                    exit 0 = PASS（ERROR 0・WARNING 許容）
#      └→ PASS 時点で入力 PDF のみ削除（逐語は保持）
#   ③ claude -p (prompts/tts-jx-headless.md)   JX HTML → TTS 台本
#   ④ python validate-tts.py                   exit 0 = PASS
#      └→ PASS 時点で台本 *.txt を tts/input_texts/ へ集約（既 wav はスキップ）
#   ⑤ tts/run-tts.ps1 (generate_tts.py)        集約済み台本 → wav（バッチ末尾で一括・全自動）
# 逐語が無い PDF は処理対象外（SKIP_NO_TRANSCRIPT）。②が PASS でなければ③以降をスキップ。
#
# 入力配置（科目フォルダに同居・同番号）:
#   inputs/jx/{科目}/032.pdf  ＋  inputs/jx/{科目}/032.txt（または 032.md）
#   例: inputs/jx/刑/1.pdf ＋ inputs/jx/刑/1.txt
# 生成動線: 各問は canonical/ATHENA.html を clone → 本文空文字列化 → 部ごと差替（TX の GENESIS 同様）
#
# 実行例:
#   pwsh -NoProfile -File scripts/jx-batch-runner.ps1 -DryRun
#   pwsh -NoProfile -File scripts/jx-batch-runner.ps1 -Subject 刑 -MaxProblems 3
#   pwsh -NoProfile -File scripts/jx-batch-runner.ps1 -Subject 民訴 -SkipAudio   # 音声段だけ手動に
#
# 既知の対策:
#   - sentinel は Select-String / -match で grep 検出（JSON parse は脆弱なため不使用）
#   - validate の PASS 判定は $LASTEXITCODE（0=PASS）を主、sentinel grep を従とする
#   - 音声は課金。GEMINI_API_KEY 未設定なら音声段のみ自動スキップ（JX/台本は保持）
#   - エンコーディングは UTF-8（pwsh 7.x 想定）

param(
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '刑',            # 科目接頭辞（出力先・PROBLEM_ID・配色アンカーに使用）
    [int]$MaxProblems = 5,              # 1 起動あたり最大処理数
    [int]$MaxConsecutiveFailures = 3,   # 連続失敗で abort
    [switch]$SkipAudio,                 # 指定時は⑤音声生成をスキップ（台本集約まで・課金回避）
    [ValidateSet('main','sub')]
    [string]$KeyName = 'main',          # 使う鍵：.secrets\gemini_{main|sub}.key を自動読込
    [string]$TtsModel = '',             # ⑤音声のモデル上書き（空=generate_tts.py 既定=Pro / 'gemini-2.5-flash-preview-tts' で無料Flash）
    [switch]$DryRun                     # 実 claude -p 呼ばず検出・パス解決・スキップ判定のみ
)

# === パス定義 ===
# スクリプト自身の位置 (= scripts\) の親をプロジェクトルートとする
$ProjectRoot   = Split-Path -Parent $PSScriptRoot
# 入力は科目フォルダに PDF＋同番号逐語を同居：inputs\jx\{科目}\NN.pdf ＋ NN.txt（2026-06-06 確定）
$PdfDir        = Join-Path $ProjectRoot "inputs\jx\$Subject"
$JxOutputBase  = Join-Path $ProjectRoot "outputs\jx"
$TtsOutputBase = Join-Path $ProjectRoot "outputs\tts"
$LogsDir       = Join-Path $ProjectRoot "logs"

$JxPromptSrc   = Join-Path $ProjectRoot "prompts\new-jx-headless.md"
$TtsPromptSrc  = Join-Path $ProjectRoot "prompts\tts-jx-headless.md"
# JX 正典スケルトン（唯一の clone 起点・TX の GENESIS に相当）
$CanonicalAthena = Join-Path $ProjectRoot "canonical\ATHENA.html"
$ValidateJx    = Join-Path $ProjectRoot "scripts\validate-jx.py"
$ValidateTts   = Join-Path $ProjectRoot "scripts\validate-tts.py"

# 音声段（⑤）: 台本集約先と generate_tts.py 起動ラッパ
$TtsInputDir   = Join-Path $ProjectRoot "tts\input_texts"   # generate_tts.py の入力
$TtsAudioDir   = Join-Path $ProjectRoot "tts\output_audio"  # 既 wav 判定
$RunTts        = Join-Path $ProjectRoot "tts\run-tts.ps1"
$StagedAny     = $false   # この起動で input_texts へ何か集約したか（末尾の音声生成トリガ）

$CostCsv       = Join-Path $LogsDir "jx-cost-summary.csv"
$RunLog        = Join-Path $LogsDir "jx-batch-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# 科目接頭辞 → 出力ディレクトリ名（{Subject}JX）
$SubjectDir    = "${Subject}JX"
$JxOutputDir   = Join-Path $JxOutputBase $SubjectDir

# === API キー自動読込（⑤音声用・直書き禁止／git管理外の .secrets から）===
# 既に環境変数 GEMINI_API_KEY があればそれを優先。無ければ .secrets\gemini_{KeyName}.key を読む。
$SecretsDir    = Join-Path $ProjectRoot ".secrets"
$KeyFile       = Join-Path $SecretsDir "gemini_$KeyName.key"
if ([string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY)) {
    if (Test-Path $KeyFile) {
        $loadedKey = (Get-Content $KeyFile -Raw -ErrorAction SilentlyContinue).Trim()
        if (-not [string]::IsNullOrWhiteSpace($loadedKey)) {
            $env:GEMINI_API_KEY = $loadedKey
            # 鍵そのものは表示しない（先頭数文字のみ）
            $env:GEMINI_API_KEY_SOURCE = "secrets:$KeyName"
        }
    }
}
# ⑤音声モデルの上書き（指定時のみ）。generate_tts.py が TTS_MODEL を参照する。
if (-not [string]::IsNullOrWhiteSpace($TtsModel)) { $env:TTS_MODEL = $TtsModel }

# === stdout/stderr UTF-8 化 ===
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# === logs ディレクトリ確保 ===
if (-not (Test-Path $LogsDir)) { New-Item -Path $LogsDir -ItemType Directory -Force | Out-Null }

# === 開始ログ ===
Start-Transcript -Path $RunLog -Append | Out-Null

Write-Host "=== jx-batch-runner 開始 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "Subject: $Subject (接頭=$SubjectDir) / MaxProblems: $MaxProblems / MaxConsecutiveFailures: $MaxConsecutiveFailures / DryRun: $DryRun / SkipAudio: $SkipAudio"
Write-Host "PDF dir   : $PdfDir  (PDF＋同番号逐語 .txt/.md)"
Write-Host "JX  output: $JxOutputDir"
Write-Host "TTS output: $TtsOutputBase\{PROBLEM_ID}\"
Write-Host "音声(⑤)   : $TtsInputDir → $TtsAudioDir  (run-tts.ps1)"
# 鍵ソース表示（値は出さない・先頭4文字のみ）
$keyHint = if ($env:GEMINI_API_KEY) { $env:GEMINI_API_KEY.Substring(0,[Math]::Min(4,$env:GEMINI_API_KEY.Length)) + '…' } else { '(なし)' }
$keySrc  = if ($env:GEMINI_API_KEY_SOURCE) { $env:GEMINI_API_KEY_SOURCE } elseif ($env:GEMINI_API_KEY) { 'env' } else { '未設定' }
$modelHint = if ($env:TTS_MODEL) { $env:TTS_MODEL } else { 'generate_tts.py 既定(Pro)' }
Write-Host "APIキー   : 源=$keySrc  先頭=$keyHint  / TTSモデル=$modelHint  (KeyName=$KeyName)"

# 音声段の事前診断（課金。キー未設定なら音声のみ自動スキップ予告）
$AudioEnabled = (-not $SkipAudio)
if ($AudioEnabled -and [string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY)) {
    Write-Host "[NOTE] GEMINI_API_KEY 未設定 → 音声段(⑤)は自動スキップ。JX/台本は生成・集約する。" -ForegroundColor Yellow
    Write-Host "       後で音声化する場合:  `$env:GEMINI_API_KEY='...'; pwsh -NoProfile -File `"$RunTts`"" -ForegroundColor Yellow
}

# === 前提ファイル存在確認 ===
$missing = @()
if (-not (Test-Path $PdfDir))       { $missing += "PDF dir: $PdfDir" }
if (-not (Test-Path $JxPromptSrc))  { $missing += "JX prompt: $JxPromptSrc" }
if (-not (Test-Path $TtsPromptSrc)) { $missing += "TTS prompt: $TtsPromptSrc" }
if (-not (Test-Path $ValidateJx))   { $missing += "validate-jx: $ValidateJx" }
if (-not (Test-Path $ValidateTts))  { $missing += "validate-tts: $ValidateTts" }
if (-not (Test-Path $CanonicalAthena)) { $missing += "canonical ATHENA: $CanonicalAthena" }
if ($missing.Count -gt 0) {
    Write-Host "[ABORT] 前提ファイルが見つかりません:" -ForegroundColor Red
    foreach ($m in $missing) { Write-Host "  - $m" -ForegroundColor Red }
    Stop-Transcript | Out-Null
    exit 1
}

# === 出力ディレクトリ確保 ===
if (-not (Test-Path $JxOutputDir)) { New-Item -Path $JxOutputDir -ItemType Directory -Force | Out-Null }

# === PDF 検出と分類（PENDING / SKIP_EXISTS / SKIP_NO_TRANSCRIPT / SKIP_NONUMERIC）===
# 入力レイアウト（2026-06-06 分類確定）:
#   PDF  : inputs\jx\{科目}\重問PDF\NN.pdf
#   逐語 : inputs\jx\{科目}\講義逐語\{科目名}_重問NN[_文字起こし].txt（または .md）
# 後方互換: 旧フラット（{科目}\NN.pdf ＋ {科目}\NN.txt）も拾う。
$PdfSubDir   = Join-Path $PdfDir "重問PDF"
$TransSubDir = Join-Path $PdfDir "講義逐語"

# PDF は 重問PDF\ を優先、その後フラット {科目}\ 直下。同名 PDF はサブフォルダ優先で 1 つに。
$PdfSearchDirs = @()
if (Test-Path $PdfSubDir) { $PdfSearchDirs += $PdfSubDir }
$PdfSearchDirs += $PdfDir
$seenPdf = @{}
$AllPdfs = @()
foreach ($dir in $PdfSearchDirs) {
    foreach ($p in @(Get-ChildItem -Path $dir -Filter "*.pdf" -File -ErrorAction SilentlyContinue | Sort-Object Name)) {
        if (-not $seenPdf.ContainsKey($p.Name)) { $seenPdf[$p.Name] = $true; $AllPdfs += $p }
    }
}

# 逐語候補（.txt/.md）は 講義逐語\ ＋ フラット {科目}\ 直下の両方から（.txt 優先）
$TransSearchDirs = @()
if (Test-Path $TransSubDir) { $TransSearchDirs += $TransSubDir }
$TransSearchDirs += $PdfDir
$TranscriptCands = @($TransSearchDirs | ForEach-Object {
        Get-ChildItem -Path $_ -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in '.txt', '.md' }
    } | Sort-Object @{ Expression = { $_.Extension } } -Descending)  # .txt > .md

# 逐語ファイル名から問題番号を抽出（'重問NN' を最優先、無ければ先頭連続数字）
function Get-TranscriptNumber {
    param([string]$Stem)
    if ($Stem -match '重問\s*0*(\d+)') { return [int]$Matches[1] }
    if ($Stem -match '^0*(\d+)')       { return [int]$Matches[1] }
    return $null
}

# 同番号逐語の探索ヘルパ（番号一致する最初の .txt/.md）
function Find-Transcript {
    param([int]$NumInt)
    foreach ($f in $TranscriptCands) {
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
        $n = Get-TranscriptNumber -Stem $stem
        if ($null -ne $n -and $n -eq $NumInt) { return $f.FullName }
    }
    return $null
}

$Catalog = @()
foreach ($pdf in $AllPdfs) {
    $raw = [System.IO.Path]::GetFileNameWithoutExtension($pdf.Name)
    # ファイル名先頭の連続数字を抽出（例: "32a" → "32", "032_x" → "032"）
    if ($raw -match '^\d+') {
        $numInt = [int]$Matches[0]
        $num = $numInt.ToString('000')  # 3 桁ゼロ埋め
    } else {
        # 数字抽出不能：処理対象外として記録のみ（headless でも判定不能なため事前除外）
        $Catalog += [PSCustomObject]@{
            PdfPath = $pdf.FullName; Number = $null; ProblemId = $null
            JxOutputPath = $null; TtsOutputDir = $null; TranscriptPath = $null; Status = "SKIP_NONUMERIC"
        }
        continue
    }
    $problemId    = "${Subject}JX${num}"
    $jxOutputPath = Join-Path $JxOutputDir "${problemId}.html"
    $ttsOutputDir = Join-Path $TtsOutputBase $problemId
    $transcript   = Find-Transcript -NumInt $numInt   # 同番号逐語（必須）
    # 判定優先順位：既存 HTML > 逐語欠如 > 処理対象
    $status = if (Test-Path $jxOutputPath) { "SKIP_EXISTS" }
              elseif (-not $transcript)    { "SKIP_NO_TRANSCRIPT" }
              else                         { "PENDING" }
    $Catalog += [PSCustomObject]@{
        PdfPath        = $pdf.FullName
        Number         = $num
        ProblemId      = $problemId
        JxOutputPath   = $jxOutputPath
        TtsOutputDir   = $ttsOutputDir
        TranscriptPath = $transcript
        Status         = $status
    }
}

# 番号で数値ソート（文字列ソートだと "10" が "2" より前に来てしまうため）
$Pending = @($Catalog | Where-Object { $_.Status -eq "PENDING" } | Sort-Object { [int]$_.Number })
$Targets = @($Pending | Select-Object -First $MaxProblems)

# === 検出結果サマリ ===
Write-Host "`n--- PDF 検出結果（全 $($Catalog.Count) 件）---" -ForegroundColor Yellow
foreach ($c in $Catalog) {
    $color = switch ($c.Status) {
        "PENDING"            { "Green" }
        "SKIP_EXISTS"        { "DarkGray" }
        "SKIP_NO_TRANSCRIPT" { "Magenta" }
        "SKIP_NONUMERIC"     { "Red" }
    }
    $idText = if ($c.ProblemId) { $c.ProblemId } else { "(番号抽出不能)" }
    $trText = if ($c.TranscriptPath) { " ＋逐語=" + (Split-Path $c.TranscriptPath -Leaf) } `
              elseif ($c.Status -eq "SKIP_NO_TRANSCRIPT") { " ＋逐語=なし(要配置)" } else { "" }
    Write-Host ("  [{0,-18}] {1}  <- {2}{3}" -f $c.Status, $idText, (Split-Path $c.PdfPath -Leaf), $trText) -ForegroundColor $color
}
$NoTrans = @($Catalog | Where-Object { $_.Status -eq "SKIP_NO_TRANSCRIPT" })
if ($NoTrans.Count -gt 0) {
    Write-Host "[NOTE] 逐語欠如で除外 $($NoTrans.Count) 件。同番号の .txt/.md を $PdfDir に置くと対象化されます。" -ForegroundColor Magenta
}
Write-Host "`nPENDING: $($Pending.Count) 件 / 本起動の処理対象: $($Targets.Count) 件（最大 $MaxProblems）" -ForegroundColor Yellow

if ($Targets.Count -eq 0) {
    Write-Host "処理対象（PENDING）なし、終了。" -ForegroundColor Green
    Stop-Transcript | Out-Null
    exit 0
}

# === DryRun はパス解決の確認まで ===
if ($DryRun) {
    Write-Host "`n[DRY-RUN] 以下を処理予定（claude -p / validate / 削除 / 音声 は呼ばない）:" -ForegroundColor Yellow
    foreach ($t in $Targets) {
        Write-Host "  ● $($t.ProblemId)" -ForegroundColor Cyan
        Write-Host "      PDF        : $($t.PdfPath)"
        Write-Host "      逐語       : $($t.TranscriptPath)  (注入: {TRANSCRIPT_PATH})"
        Write-Host "      ① JX 出力  : $($t.JxOutputPath)"
        Write-Host "      ② validate : python `"$ValidateJx`" `"$($t.JxOutputPath)`""
        $pdfParentDr = Split-Path -Parent $t.PdfPath
        if ((Split-Path $pdfParentDr -Leaf) -eq '重問PDF') {
            Write-Host "          [DRYRUN] PASS 時 PDF は保持（原本ストア 重問PDF\）: $($t.PdfPath)"
        } else {
            Write-Host "          [DRYRUN] PASS 時 would delete PDF（フラット配置）: $($t.PdfPath)  (逐語は保持)"
        }
        Write-Host "      ③ TTS 出力 : $($t.TtsOutputDir)\"
        Write-Host "          [DRYRUN] would clean: $($t.TtsOutputDir)  (*.txt のみ・leaf=$($t.ProblemId) 一致時のみ・他フォルダは触らない)"
        Write-Host "      ④ validate : python `"$ValidateTts`" `"$($t.TtsOutputDir)`" $($t.ProblemId)"
        Write-Host "          [DRYRUN] PASS 時 would stage *.txt → $TtsInputDir  (既 wav はスキップ)"
    }
    $audioPlan = if ($SkipAudio) { "スキップ(-SkipAudio)" }
                 elseif ([string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY)) { "スキップ(GEMINI_API_KEY 未設定)" }
                 else { "末尾で run-tts.ps1 を一括実行（課金）" }
    Write-Host "  ⑤ 音声生成   : $audioPlan" -ForegroundColor Cyan
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
    # 重要: 大きな複数行プロンプトを `-p $Prompt`（引数）で渡すと PowerShell の
    # ネイティブ引数処理で壊れ、claude に未達のまま空プロンプトで起動される
    # （実測: 40KB 級の複数行プロンプトが未達。"no stdin data received" 警告 → 汎用応答）。
    # → プロンプトは stdin パイプで渡す（claude -p は引数値が無ければ stdin から読む）。
    $claudeArgs = @(
        '-p',
        '--output-format', 'json',
        '--permission-mode', 'acceptEdits',
        '--allowedTools', 'Write,Edit,Read,Bash,Glob,Grep'
    )
    # 重要: ヘッドレスプロンプト本文は「# new-jx-headless.md … 実行用プロンプト」と
    # 自己紹介する文書体裁のため、能力の高いモデルは「レビュー対象の文書」と誤認し
    # 「具体的な依頼が無い」と確認を返して実行を拒否することがある（実測）。
    # → 文書ではなく今すぐ自走実行する指示書であることを冒頭で強制フレーミングする。
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

# TTS 出力dir の stale クリーン（限定的・安全）
#   - その問題の dir 内の *.txt のみ削除（非再帰・他フォルダや他拡張子は触らない）
#   - dir が無ければ作成のみ
#   - 誤爆防止：dir の leaf が PROBLEM_ID と一致しない場合は何もしない
function Clear-TtsOutputDir {
    param(
        [Parameter(Mandatory)][string]$Dir,
        [Parameter(Mandatory)][string]$ExpectedLeaf  # = PROBLEM_ID
    )
    $leaf = Split-Path $Dir -Leaf
    if ($leaf -ne $ExpectedLeaf) {
        Write-Host "[CLEAN-SKIP] dir leaf '$leaf' != PROBLEM_ID '$ExpectedLeaf'、安全のためクリーンしない" -ForegroundColor Yellow
        return
    }
    if (Test-Path $Dir) {
        $stale = @(Get-ChildItem -Path $Dir -Filter "*.txt" -File -ErrorAction SilentlyContinue)
        if ($stale.Count -gt 0) {
            $stale | Remove-Item -Force
            Write-Host "[CLEAN] $Dir 内の旧 *.txt $($stale.Count) 件を削除" -ForegroundColor DarkYellow
        } else {
            Write-Host "[CLEAN] $Dir に旧 *.txt なし（クリーン不要）"
        }
    } else {
        New-Item -Path $Dir -ItemType Directory -Force | Out-Null
        Write-Host "[CLEAN] $Dir を新規作成（既存ファイルなし）"
    }
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
        -replace '\{TARGET_PDF\}',       $t.PdfPath `
        -replace '\{TRANSCRIPT_PATH\}',  $t.TranscriptPath `
        -replace '\{PROBLEM_NUMBER\}',   $t.Number `
        -replace '\{PROBLEM_ID\}',       $t.ProblemId `
        -replace '\{OUTPUT_PATH\}',      $t.JxOutputPath `
        -replace '\{CANONICAL_PATH\}',   $CanonicalAthena `
        -replace '\{SUBJECT_PREFIX\}',   $Subject
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

    # ----- ②-bis 入力 PDF 削除（validate PASS 時のみ・逐語は保持）-----
    # 旧フラット運用ではテスト用の使い捨てコピーを削除していたが、新レイアウトの
    # 重問PDF\ は恒久的な原本ストアなので削除しない（再処理は SKIP_EXISTS で防止済み）。
    # → 削除対象はフラット {科目}\ 直下に置かれた PDF のみ。重問PDF\ 配下の原本は保持。
    if ($jxPass) {
        $pdfParent = Split-Path -Parent $t.PdfPath
        $isCanonicalStore = ((Split-Path $pdfParent -Leaf) -eq '重問PDF')
        if ($isCanonicalStore) {
            Write-Host "[②-bis PDF削除] 原本ストア(重問PDF\)のため削除しません（保持）: $($t.PdfPath)" -ForegroundColor DarkGray
        } elseif (Test-Path $t.PdfPath) {
            try {
                Remove-Item -Path $t.PdfPath -Force -ErrorAction Stop
                Write-Host "[②-bis PDF削除] フラット配置の入力 PDF を削除しました（逐語は保持）: $($t.PdfPath)" -ForegroundColor DarkYellow
            } catch {
                Write-Host "[②-bis PDF削除] 削除失敗（手動削除可・処理は継続）: $_" -ForegroundColor Yellow
            }
        }
    }

    # =========================================================
    # ③ TTS 生成（jxPass 時のみ / tts-jx-headless.md）
    # =========================================================
    if ($jxPass) {
        Write-Host "`n--- ③ TTS 生成開始 $(Get-Date -Format 'HH:mm:ss')---" -ForegroundColor Cyan
        $ttsStart = Get-Date
        # stale クリーン：この問題の TTS dir 内 *.txt のみ削除（dir 無ければ作成）
        Clear-TtsOutputDir -Dir $t.TtsOutputDir -ExpectedLeaf $t.ProblemId

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

                # ----- ④-bis 台本 *.txt を tts/input_texts/ へ集約（音声は末尾で一括生成）-----
                if (-not (Test-Path $TtsInputDir)) { New-Item -Path $TtsInputDir -ItemType Directory -Force | Out-Null }
                $staged = 0; $skipWav = 0
                foreach ($txt in @(Get-ChildItem -Path $t.TtsOutputDir -Filter "*.txt" -File -ErrorAction SilentlyContinue)) {
                    $stem = [System.IO.Path]::GetFileNameWithoutExtension($txt.Name)
                    if (Test-Path (Join-Path $TtsAudioDir "$stem.wav")) { $skipWav++; continue }  # 既 wav は再集約しない
                    Copy-Item -Path $txt.FullName -Destination (Join-Path $TtsInputDir $txt.Name) -Force
                    $staged++
                }
                if ($staged -gt 0) { $StagedAny = $true }
                Write-Host "[④-bis 集約] input_texts へ $staged 件コピー（既 wav スキップ $skipWav 件）" -ForegroundColor Green
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
    # 真の失敗のみカウント（JX_FAILED or HTML 0 バイト）。claude -p が exit≠0 を
    # 返しても、validate-jx PASS かつ bytes>0 なら実質成功なので失敗に数えない
    # （headless で sentinel echo 周りが非0終了することがあり、誤って連続失敗 abort を招く）。
    if ($overall -eq "JX_FAILED" -or $jxBytes -eq 0) {
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

# =========================================================
# ⑤ 音声生成（バッチ末尾で一括・全自動・課金）
#   - input_texts へ何か集約された場合のみ run-tts.ps1 を 1 回起動
#   - generate_tts.py 側で既 wav はスキップ・DAILY_LIMIT/リトライを内蔵
#   - GEMINI_API_KEY 未設定 or -SkipAudio の場合は集約のみで停止（後で手動起動可）
# =========================================================
Write-Host "`n--- ⑤ 音声生成（run-tts.ps1）---" -ForegroundColor Cyan
$inTxtCount = @(Get-ChildItem -Path $TtsInputDir -Filter "*.txt" -File -ErrorAction SilentlyContinue).Count
if (-not $StagedAny) {
    Write-Host "[⑤ AUDIO] 本起動で新規集約された台本なし → 音声生成スキップ（input_texts に未処理 $inTxtCount 件）" -ForegroundColor Yellow
} elseif ($SkipAudio) {
    Write-Host "[⑤ AUDIO] -SkipAudio 指定 → 集約のみで停止。手動起動:  pwsh -NoProfile -File `"$RunTts`"" -ForegroundColor Yellow
} elseif ([string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY)) {
    Write-Host "[⑤ AUDIO] GEMINI_API_KEY 未設定 → 音声生成スキップ。後で:  `$env:GEMINI_API_KEY='...'; pwsh -NoProfile -File `"$RunTts`"" -ForegroundColor Yellow
} elseif (-not (Test-Path $RunTts)) {
    Write-Host "[⑤ AUDIO] run-tts.ps1 が見つかりません: $RunTts（集約のみ完了）" -ForegroundColor Yellow
} else {
    Write-Host "[⑤ AUDIO] input_texts $inTxtCount 件を音声化します（既 wav はスキップ・課金）" -ForegroundColor Cyan
    & pwsh -NoProfile -File $RunTts
    Write-Host "[⑤ AUDIO] run-tts 完了 (exit=$LASTEXITCODE)。残件があれば再実行で続行可。" -ForegroundColor Cyan
}

Write-Host "`n=== jx-batch-runner 終了 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "処理件数: $ProcessedCount / $($Targets.Count)"
Write-Host "コストログ: $CostCsv"

Stop-Transcript | Out-Null
exit 0
