<#
  drive-mirror.ps1 — 複数リポジトリを Google Drive へ一方向ミラー

  目的：
    GitHub には code/spec のみ（bar-exam の outputs/**/*.html 等は .gitignore 除外）。
    本スクリプトは「生成用資料 + 生成HTML成果物」を含むリポジトリ群を丸ごと
    Google Drive(マイドライブ) へ robocopy /MIR で一方向同期し、バックアップを残す。

  バックアップ対象（2026-06-05 ユーザー確定）：
    - bar-exam      （短答TX / 論文JX 教材生成）
    - bar-exam-gx   （GX シリーズ）
    - Lexia         （host アプリ）
    - arbor

  設計：
    - 保存先：マイドライブ直下 repo-backup\<プロジェクト名>\ （個人・非共有）
    - 頻度：3時間ごと自動（register-drive-mirror-task.ps1 で登録）
    - .git / node_modules / logs / __pycache__ 等は除外（GitHub と重複・容量・同期速度）
    - 一方向（ローカル→Drive）。/MIR は Dest 側の余剰を削除して鏡像化するが、
      Source(ローカル) は読み取りのみ＝ローカル消失事故は起きない
    - robocopy はネイティブ exe＝前面 PowerShell の Copy-Item/Remove-Item ブロックを回避

  Drive 配信先の自動検出：
    マイドライブのマウント先(C:/G:/H:)が環境で変わりうるため候補を順に探索。
#>
[CmdletBinding()]
param(
  [string[]]$Sources = @(),
  [string]$ProjectRoot = '',  # bar-exam clone/root（未指定はこの repo / BAREXAM_PROJECT_ROOT）
  # マイドライブ直下に作るミラー親フォルダ名（配下に <プロジェクト名> を作成）
  [string]$DestRoot = 'repo-backup',
  # マイドライブのマウント候補（先に存在したものを採用）
  [string[]]$MyDriveCandidates = @(
    'H:\マイドライブ', 'G:\マイドライブ',
    "$env:USERPROFILE\マイドライブ",
    'H:\My Drive', 'G:\My Drive',
    "$env:USERPROFILE\Google ドライブ", "$env:USERPROFILE\Google Drive"
  ),
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$DefaultProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path

if (-not $PSBoundParameters.ContainsKey('Sources')) {
  $Sources = @(
    $ProjectRoot,
    'c:\Users\xnrg2.DESKTOP-5664QR6\bar-exam-gx',
    'c:\Users\xnrg2.DESKTOP-5664QR6\Lexia',
    'c:\Users\xnrg2.DESKTOP-5664QR6\arbor'
  )
}

# --- マイドライブのマウント先を自動検出 ---
$myDrive = $null
foreach ($cand in $MyDriveCandidates) {
  if (Test-Path -LiteralPath $cand) { $myDrive = $cand; break }
}
if (-not $myDrive) {
  Write-Error "マイドライブが見つかりません。Google Drive Desktop が起動しているか確認。候補: $($MyDriveCandidates -join ', ')"
  exit 2
}
$destBase = Join-Path $myDrive $DestRoot

# --- ログ先（bar-exam\logs\ は .gitignore 済） ---
$logDir = Join-Path $ProjectRoot 'logs\drive-mirror'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logFile = Join-Path $logDir "mirror_$stamp.log"

Write-Host "=== drive-mirror $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "Drive  : $myDrive"
Write-Host "DestRoot: $destBase"
Write-Host "Log    : $logFile`n"

# --- 共通除外 ---
$excludeDirs  = @(
  '.git', '.codex', '.secrets', 'logs', '_archive', '__pycache__',
  '_tmp_pdf_pages', '_tessdata', 'node_modules', '.vscode',
  'output_audio', 'input_texts'
)
$excludeFiles = @('desktop.ini', '*.pyc', '_tmp_*', '.DS_Store', '*.key', 'account_names.json', 'fail_*.png')

$overall = 0
foreach ($src in $Sources) {
  $name = Split-Path $src -Leaf
  if (-not (Test-Path -LiteralPath $src)) {
    Write-Host "[SKIP] $name : ソースが見つかりません ($src)" -ForegroundColor Yellow
    continue
  }
  $dest = Join-Path $destBase $name
  Write-Host "--- [$name] $src -> $dest ---" -ForegroundColor Cyan

  $rcArgs = @($src, $dest, '/MIR', '/XD') + $excludeDirs + @('/XF') + $excludeFiles + @(
    '/R:2', '/W:5', '/MT:8', '/NP', '/NDL', '/FFT', '/DST',
    "/LOG+:$logFile", '/TEE'
  )
  if ($DryRun) { $rcArgs += '/L' }

  & robocopy.exe @rcArgs
  $rc = $LASTEXITCODE
  # robocopy 終了コード：0-7=正常 / 8以上=失敗
  if ($rc -ge 8) {
    Write-Host "[FAIL] $name : robocopy exit=$rc" -ForegroundColor Red
    if ($rc -gt $overall) { $overall = $rc }
  } else {
    Write-Host "[OK]   $name : robocopy exit=$rc" -ForegroundColor Green
  }
  Write-Host ""
}

if ($overall -ge 8) {
  Write-Host "=== 一部失敗 (max exit=$overall・詳細 $logFile) ===" -ForegroundColor Red
  exit $overall
} else {
  Write-Host "=== drive-mirror 完了 $(Get-Date -Format 'HH:mm:ss') ===" -ForegroundColor Green
  exit 0
}
