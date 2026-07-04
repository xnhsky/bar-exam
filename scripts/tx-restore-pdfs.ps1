# tx-restore-pdfs.ps1 — Drive の「抽出PDF」原本から inputs へ PDF を復元する（v13 移行の前段）。
#
# 背景：生成後に inputs から削除された旧問の PDF（Drive の「抽出PDF」に 445 問の原本が常在）を、
# v13 移行バッチに乗せるためレンジ指定で inputs/000_TX/{科目}/ に戻す。night-batch-runner の
# v13 pending 判定は「_lex が v13 エンジンを持つか」だが、その前に PDF が inputs に無いと
# バッチが問題を enumerate できないため、このスクリプトで先に材料を揃える。
#
# 使い方（ローカル PC・Drive マウント時のみ）:
#   pwsh -NoProfile -File scripts\tx-restore-pdfs.ps1 -FromNumber 360 -ToNumber 445             # dry-run
#   pwsh -NoProfile -File scripts\tx-restore-pdfs.ps1 -FromNumber 360 -ToNumber 445 -Apply      # 実コピー
#   pwsh -NoProfile -File scripts\tx-restore-pdfs.ps1 -Subject 刑訴 -FromNumber 1 -ToNumber 50 -Apply
#
# 既定 dry-run。-Apply で実コピー。既に inputs にある番号はスキップ。Drive 未マウントなら中断。
param(
    [ValidateSet('刑','刑訴','民','商','民訴','行政','憲')]
    [string]$Subject = '刑',
    [int]$FromNumber = 0,
    [int]$ToNumber = 0,
    [string]$ProjectRoot = '',
    [switch]$Apply
)
if ($FromNumber -le 0 -and $ToNumber -le 0) {
    Write-Host "[ERROR] -FromNumber / -ToNumber を指定してください。" -ForegroundColor Red; exit 1
}
if ($ToNumber -le 0) { $ToNumber = $FromNumber }
if ($FromNumber -le 0) { $FromNumber = $ToNumber }

$DefaultProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path

$SubjectFolder = switch ($Subject) { '刑'{'001_刑法'} '刑訴'{'002_刑事訴訟法'} '民'{'003_民法'} '商'{'004_商法'} '民訴'{'005_民事訴訟法'} '行政'{'006_行政法'} '憲'{'007_憲法'} }
$DriveSubjectPat = switch ($Subject) { '刑'{'001_*'} '刑訴'{'002_*'} '民'{'003_*'} '商'{'004_*'} '民訴'{'005_*'} '行政'{'006_*'} '憲'{'007_*'} }
$InputsDir = Join-Path $ProjectRoot (Join-Path "inputs\000_TX" $SubjectFolder)
if (-not (Test-Path $InputsDir)) { New-Item -ItemType Directory -Path $InputsDir -Force | Out-Null }

# === Drive 科目フォルダ検出（night-batch-runner と同ロジック）===
$SubjDir = $null
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
    if (-not $txDir) { continue }
    $sd = Get-ChildItem $txDir.FullName -Directory -ErrorAction SilentlyContinue |
          Where-Object Name -like $DriveSubjectPat | Select-Object -First 1
    if ($sd) { $SubjDir = $sd.FullName; break }
}
if (-not $SubjDir) {
    Write-Host "[ERROR] Drive の科目フォルダ($DriveSubjectPat)が見つからない（未マウント？）。中断。" -ForegroundColor Red
    exit 2
}

# === 抽出PDF フォルダ検出 ===
$PdfSrc = Get-ChildItem $SubjDir -Directory -ErrorAction SilentlyContinue |
          Where-Object Name -like "*抽出*PDF*" | Select-Object -First 1
if (-not $PdfSrc) {
    $PdfSrc = Get-ChildItem $SubjDir -Directory -ErrorAction SilentlyContinue |
              Where-Object Name -like "*抽出*" | Select-Object -First 1
}
if (-not $PdfSrc) {
    Write-Host "[ERROR] 抽出PDF フォルダが $SubjDir に見つからない。中断。" -ForegroundColor Red
    exit 3
}
Write-Host "[SRC] $($PdfSrc.FullName)" -ForegroundColor Cyan
Write-Host "[DST] $InputsDir" -ForegroundColor Cyan
Write-Host "[RANGE] $FromNumber〜$ToNumber / Subject=$Subject / Apply=$Apply`n"

$copied = 0; $skipped = 0; $missing = @()
for ($n = $FromNumber; $n -le $ToNumber; $n++) {
    $dst = Join-Path $InputsDir "$n.pdf"
    if (Test-Path $dst) { $skipped++; continue }   # 既に inputs にある
    # Drive 側ファイル名は {N}.pdf（前ゼロ無し）想定。念のため 0 埋め候補も探す。
    $cand = @("$n.pdf", ("{0:000}.pdf" -f $n)) |
            ForEach-Object { Join-Path $PdfSrc.FullName $_ } |
            Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $cand) { $missing += $n; continue }
    if ($Apply) {
        Copy-Item -LiteralPath $cand -Destination $dst -Force
        Write-Host "  [COPY] $n" -ForegroundColor Green
    } else {
        Write-Host "  [WOULD-COPY] $n <- $cand"
    }
    $copied++
}
Write-Host "`n復元 $copied / スキップ(既存) $skipped / 欠落 $($missing.Count)" -ForegroundColor Yellow
if ($missing.Count) { Write-Host "欠落番号: $($missing -join ', ')" -ForegroundColor Yellow }
if (-not $Apply) { Write-Host "`n[DRY-RUN] 問題なければ -Apply を付けて実コピー。" -ForegroundColor Yellow }
