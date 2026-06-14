<#
  tx-deploy.ps1 — TX 生成 HTML を Google Drive「1 TX_短答」閲覧フォルダへ配置

  目的：
    GitHub master が正典バックアップ（CLAUDE.md §9）。本スクリプトは閲覧用ミラー
    （マイドライブ\1 TX_短答\00N_科目\）を最新化するための片方向コピー。
    repo-backup（drive-mirror.ps1）とは別物で、こちらは「科目別の見やすい配置」。

  使い方（PCで・要 Google Drive Desktop 起動）：
    # 事前に必ず最新化
    git checkout master; git pull origin master
    # 全科目を配置
    pwsh -NoProfile -File scripts/tx-deploy.ps1
    # 刑法だけ／番号帯だけ
    pwsh -NoProfile -File scripts/tx-deploy.ps1 -Subject 刑TX
    pwsh -NoProfile -File scripts/tx-deploy.ps1 -Subject 刑TX -FromNumber 326 -ToNumber 445
    # 変更内容の確認だけ（コピーしない）
    pwsh -NoProfile -File scripts/tx-deploy.ps1 -DryRun

  設計：
    - 同名上書き（robocopy 既定：新しい/サイズ差のみ）＝旧 v10 が新 v11 に置換、重複なし。
    - 一方向（ローカル outputs → Drive）。Drive 側の余剰は削除しない（/MIR は使わない）。
    - マイドライブのマウント先（H:/G:/USERPROFILE）は自動検出。
#>
[CmdletBinding()]
param(
  # 対象科目フォルダ名（outputs/tx 配下の接頭辞）。省略時は全科目。
  [ValidateSet('刑TX','刑訴TX','民TX','商TX','民訴TX','行政TX','憲TX')]
  [string]$Subject,
  # 番号帯フィルタ（省略時は全件）
  [int]$FromNumber = 0,
  [int]$ToNumber = 99999,
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

# 接頭辞 → 閲覧フォルダ名（docs/drive-folders.md が正典）
$folderMap = [ordered]@{
  '刑TX'   = '001_刑法'
  '刑訴TX' = '002_刑事訴訟法'
  '民TX'   = '003_民法'
  '商TX'   = '004_商法'
  '民訴TX' = '005_民事訴訟法'
  '行政TX' = '006_行政法'
  '憲TX'   = '007_憲法'
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
$txRoot = Join-Path $myDrive '1 TX_短答'
Write-Host "MyDrive : $myDrive"
Write-Host "配信先  : $txRoot"
Write-Host "DryRun  : $($DryRun.IsPresent)"
Write-Host ("-" * 60)

$repoRoot = Split-Path -Parent $PSScriptRoot
$targets = if ($Subject) { @($Subject) } else { $folderMap.Keys }

$totalCopied = 0
foreach ($prefix in $targets) {
  $srcDir = Join-Path $repoRoot "outputs\tx\$prefix"
  if (-not (Test-Path -LiteralPath $srcDir)) { Write-Host "[skip] $prefix : outputs に無し"; continue }
  $destDir = Join-Path $txRoot $folderMap[$prefix]

  # 番号帯フィルタで対象 HTML を抽出
  $files = Get-ChildItem -LiteralPath $srcDir -Filter '*.html' -File | Where-Object {
    if ($_.BaseName -match '(\d+)') {
      $num = [int]$Matches[1]
      $num -ge $FromNumber -and $num -le $ToNumber
    } else { $false }
  }
  if (-not $files) { Write-Host "[skip] $prefix : 対象ファイル0件"; continue }

  Write-Host "[$prefix] $($files.Count) 件 → $destDir"
  if ($DryRun) {
    $files | ForEach-Object { Write-Host "    (dry) $($_.Name)" }
    continue
  }

  if (-not (Test-Path -LiteralPath $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
  foreach ($f in $files) {
    Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $destDir $f.Name) -Force
    $totalCopied++
  }
}

Write-Host ("-" * 60)
Write-Host "完了: $totalCopied 件をコピー$(if($DryRun){'（DryRun のため未実行）'})"
