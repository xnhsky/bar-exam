<#
  tx-push-inputs-to-drive.ps1 — ローカルの TX 入力（1問1PDF＝分割済み）を Google Drive へ配る
  （PC 間共有の「送り」側・2026-09-06 新設）

  目的：
    TX の入力 PDF は .gitignore 対象（`inputs/000_TX/**/*.pdf`・2026-07-09 方針転換）で git 共有されない。
    そのため PC 間の共有チャネルは Drive `1 TX_短 答\{00N_科目}\抽出PDF\` 一本であり、
    受け側には `scripts/tx-pull-inputs-from-drive.ps1`（Drive→ローカル）があった。
    しかし **送り側（ローカル→Drive）が存在しなかった**ため、分割した PC のローカルにだけ
    1問1PDF が溜まり、Drive は未分割のまま＝もう一方の PC は永久に取り込めなかった。
    実害＝xnrg2 PC で TJR-T が全科目「該当なし」（民法以降の PDF が Drive にもローカルにも無い・
    2026-09-06 特定）。本スクリプトがその欠けていた片道を埋める。

  使い方：
    pwsh -NoProfile -File scripts/tx-push-inputs-to-drive.ps1 -DryRun      # 何が上がるか確認
    pwsh -NoProfile -File scripts/tx-push-inputs-to-drive.ps1              # 全科目
    pwsh -NoProfile -File scripts/tx-push-inputs-to-drive.ps1 -Subject 民   # 特定科目

  設計（pull 側と対称）：
    - Drive マウント先（C:/D:/G:/H:/USERPROFILE）を自動検出。共有フォルダ
      `CATALINA＿G共有\■予備試験進行中` 配下の `1 TX_*`（実名「1 TX_短 答」）をワイルドカードで解決。
    - **1問1PDF だけを配る**＝ステム全体が数字のファイル（`123.pdf`）のみ。分割前の原本
      （`2026 短答過去問パーフェクト民法1.pdf` 等・`_原本\`）は既定では配らない
      （受け側の番号抽出 `^\d+` が `2026` を拾い `民TX2026` を生成する事故を防ぐ・pull 側と同じ規律）。
      分割来歴 `_分割一覧.md` は軽いので既定で配る（-NoManifest で抑止）。
    - 既存の Drive ファイルは上書きせずスキップ（冪等・Drive 優先）。-Force で上書き。
    - 一方向（ローカル→Drive）。**Drive 側の余剰は絶対に削除しない**（/MIR ではない）。
    - Drive Desktop がミラー/ストリームのどちらでも、コピー完了後にバックグラウンドで実アップロードされる。
#>
[CmdletBinding()]
param(
  [string]$Subject = '',              # 空=全科目。短縮名 民/商/民訴/行政/憲/刑/刑訴 可
  [switch]$DryRun,
  [switch]$Force,                     # Drive 側の既存ファイルを上書き
  [switch]$IncludeSource,             # 分割前の原本（_原本\）も Drive の `_原本\` へ配る（既定 OFF・大容量）
  [switch]$NoManifest                 # 分割来歴 _分割一覧.md を配らない
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 科目短縮名 → 00N_科目
$SubjMap = @{
  '刑'='001_刑法'; '刑訴'='002_刑事訴訟法'; '民'='003_民法'; '商'='004_商法';
  '民訴'='005_民事訴訟法'; '行政'='006_行政法'; '憲'='007_憲法'
}
foreach ($k in @($SubjMap.Values)) { $SubjMap[$k] = $k }

# --- Drive 上の「1 TX_短 答」を自動検出（pull 側と同一ロジック）---
$relParent = 'CATALINA＿G共有\■予備試験進行中'
$candRoots = @(
  'D:\GoogleDrive', 'G:\GoogleDrive', 'H:\GoogleDrive', 'C:\GoogleDrive',
  'D:\マイドライブ', 'G:\マイドライブ', 'H:\マイドライブ',
  "$env:USERPROFILE\GoogleDrive", "$env:USERPROFILE\マイドライブ"
)
foreach ($L in 'C','D','E','F','G','H','I') {
  $candRoots += @("$L`:\GoogleDrive", "$L`:\マイドライブ", "$L`:")
}
$driveBase = $null
foreach ($root in $candRoots) {
  $parent = Join-Path $root $relParent
  if (-not (Test-Path -LiteralPath $parent)) { continue }
  $tx = @(Get-ChildItem -LiteralPath $parent -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like '1 TX_*' })
  if ($tx.Count -gt 0) { $driveBase = $tx[0].FullName; break }
}
if (-not $driveBase) {
  Write-Error "Drive 上の『1 TX_短 答』が見つかりません。Google Drive Desktop が起動し同期済みか確認してください（相対: $relParent\1 TX_*）。"
  exit 1
}
Write-Host "[Drive] 配布先: $driveBase" -ForegroundColor Cyan

# --- 対象科目の決定 ---
if ($Subject) {
  if (-not $SubjMap.ContainsKey($Subject)) { Write-Error "未知の科目: $Subject（民/商/民訴/行政/憲/刑/刑訴 または 00N_科目）"; exit 1 }
  $targets = @($SubjMap[$Subject])
} else {
  $targets = @('001_刑法','002_刑事訴訟法','003_民法','004_商法','005_民事訴訟法','006_行政法','007_憲法')
}

# 1問1PDF＝ステム全体が数字
function Test-ProblemPdf { param([System.IO.FileInfo]$f)
  return ([System.IO.Path]::GetFileNameWithoutExtension($f.Name) -match '^\d+$')
}

function Copy-Set {
  param([System.IO.FileInfo[]]$Files, [string]$Dst, [string]$Label)
  if ($Files.Count -eq 0) { return @{ Copied = 0; Bytes = 0 } }
  if (-not (Test-Path -LiteralPath $Dst)) {
    if (-not $DryRun) { New-Item -ItemType Directory -Path $Dst -Force | Out-Null }
  }
  $copied = 0; $skipped = 0; $bytes = 0
  foreach ($f in $Files) {
    $target = Join-Path $Dst $f.Name
    if ((Test-Path -LiteralPath $target) -and -not $Force) { $skipped++; continue }
    if (-not $DryRun) { Copy-Item -LiteralPath $f.FullName -Destination $target -Force }
    $copied++; $bytes += $f.Length
  }
  $tag = if ($DryRun) { '[DRYRUN] ' } else { '' }
  Write-Host ("  {0}{1}: 配布 {2} ({3:N0} MB) / スキップ既存 {4} / ローカル総数 {5}" -f `
    $tag,$Label,$copied,($bytes/1MB),$skipped,$Files.Count)
  return @{ Copied = $copied; Bytes = $bytes }
}

$totPdf = 0; $totBytes = 0; $totSrc = 0
foreach ($dir in $targets) {
  $srcSubj = Join-Path (Join-Path $ProjectRoot 'inputs\000_TX') $dir
  if (-not (Test-Path -LiteralPath $srcSubj)) { Write-Host ("  {0}: ローカルに科目フォルダなし＝スキップ" -f $dir) -ForegroundColor DarkGray; continue }
  $dstSubj = Join-Path $driveBase $dir
  if (-not (Test-Path -LiteralPath $dstSubj)) {
    Write-Host ("  {0}: Drive に科目フォルダなし＝作成する" -f $dir) -ForegroundColor Yellow
    if (-not $DryRun) { New-Item -ItemType Directory -Path $dstSubj -Force | Out-Null }
  }

  $all = @(Get-ChildItem -LiteralPath $srcSubj -Filter '*.pdf' -File -ErrorAction SilentlyContinue)
  $problem = @($all | Where-Object { Test-ProblemPdf $_ })
  if ($problem.Count -eq 0) {
    Write-Host ("  {0}: ローカルに 1問1PDF なし＝スキップ" -f $dir) -ForegroundColor DarkGray
  } else {
    $r = Copy-Set -Files $problem -Dst (Join-Path $dstSubj '抽出PDF') -Label "$dir/抽出PDF"
    $totPdf += $r.Copied; $totBytes += $r.Bytes
  }

  # 分割来歴（軽量・受け側の番号照合に効く）
  if (-not $NoManifest) {
    $man = @(Get-ChildItem -LiteralPath $srcSubj -Filter '_分割一覧.md' -File -ErrorAction SilentlyContinue)
    if ($man.Count -gt 0) { [void](Copy-Set -Files $man -Dst (Join-Path $dstSubj '抽出PDF') -Label "$dir/_分割一覧.md") }
  }

  # 分割前の原本（既定 OFF＝大容量。番号抽出の事故防止で `抽出PDF` には絶対に置かない）
  $srcOrig = Join-Path $srcSubj '_原本'
  if (Test-Path -LiteralPath $srcOrig) {
    $orig = @(Get-ChildItem -LiteralPath $srcOrig -Filter '*.pdf' -File -ErrorAction SilentlyContinue)
    if ($orig.Count -gt 0) {
      if ($IncludeSource) {
        $r2 = Copy-Set -Files $orig -Dst (Join-Path $dstSubj '_原本') -Label "$dir/_原本"
        $totSrc += $r2.Copied; $totBytes += $r2.Bytes
      } else {
        Write-Host ("    ※ 分割前の原本 {0} 件は配らない（-IncludeSource で Drive の `_原本\` へ）" -f $orig.Count) -ForegroundColor DarkGray
      }
    }
  }
}

Write-Host ("`n完了: 1問1PDF {0} 件 / 原本 {1} 件 配布（{2:N0} MB・{3}）" -f `
  $totPdf,$totSrc,($totBytes/1MB),$(if($DryRun){'DryRun'}else{'実コピー'})) -ForegroundColor Green
if (-not $DryRun -and $totPdf -gt 0) {
  Write-Host "Drive Desktop のアップロード完了を待ってから、受け側 PC で次を実行:" -ForegroundColor Yellow
  Write-Host "  pwsh -NoProfile -File scripts/tx-pull-inputs-from-drive.ps1" -ForegroundColor Yellow
}
