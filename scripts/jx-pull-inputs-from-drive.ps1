<#
  jx-pull-inputs-from-drive.ps1 — Google Drive の JX 入力（重問PDF＋講義逐語）を
  ローカル inputs へ取り込む（PC2 セットアップ用・2026-08-09）

  目的：
    JX の重問PDF・講義逐語は .gitignore 対象で git 共有されない。生成側 PC が
    `2 JX_論 文\{00N_科目}\{重問PDF,講義逐語}\` へミラー済みのものを、別 PC（PC2）が
    ローカル `inputs\001_JX\{00N_科目}\{重問PDF,講義逐語}\` へ取り込むと TJR-J が回る。
    対応表（逐語-PDF対応表.md）は git 管理なので git pull で入手済み前提。

  使い方：
    pwsh -NoProfile -File scripts/jx-pull-inputs-from-drive.ps1              # 全科目
    pwsh -NoProfile -File scripts/jx-pull-inputs-from-drive.ps1 -Subject 民   # 特定科目
    pwsh -NoProfile -File scripts/jx-pull-inputs-from-drive.ps1 -DryRun       # コピーせず確認

  設計：
    - Drive マウント先（C:/D:/G:/H:/USERPROFILE）を自動検出。共有フォルダ
      `CATALINA＿G共有\■予備試験進行中\2 JX_論 文` を含むものを採用。
    - 既存ファイルは上書きせずスキップ（冪等・ローカル優先）。-Force で上書き。
    - 一方向（Drive→ローカル）。ローカルの余剰は削除しない（/MIR ではない）。
#>
[CmdletBinding()]
param(
  [string]$Subject = '',              # 空=全科目。短縮名 民/商/民訴/行政/憲/刑/刑訴 可
  [switch]$DryRun,
  [switch]$Force                      # 既存ローカルファイルを上書き
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 科目短縮名 → 00N_科目
$SubjMap = @{
  '刑'='001_刑法'; '刑訴'='002_刑事訴訟法'; '民'='003_民法'; '商'='004_商法';
  '民訴'='005_民事訴訟法'; '行政'='006_行政法'; '憲'='007_憲法'
}
# フォルダ名直指定も許容
foreach ($k in @($SubjMap.Values)) { $SubjMap[$k] = $k }

# --- Drive 上の「2 JX_論 文」を自動検出 ---
$rel = 'CATALINA＿G共有\■予備試験進行中\2 JX_論 文'
$candRoots = @(
  'D:\GoogleDrive', 'G:\GoogleDrive', 'H:\GoogleDrive', 'C:\GoogleDrive',
  'D:\マイドライブ', 'G:\マイドライブ', 'H:\マイドライブ',
  "$env:USERPROFILE\GoogleDrive", "$env:USERPROFILE\マイドライブ"
)
$driveBase = $null
foreach ($root in $candRoots) {
  $cand = Join-Path $root $rel
  if (Test-Path -LiteralPath $cand) { $driveBase = $cand; break }
}
# ドライブレター総当たり（フォールバック）
if (-not $driveBase) {
  foreach ($L in 'C','D','E','F','G','H','I') {
    foreach ($mid in @("$L`:\GoogleDrive", "$L`:\マイドライブ", "$L`:")) {
      $cand = Join-Path $mid $rel
      if (Test-Path -LiteralPath $cand) { $driveBase = $cand; break }
    }
    if ($driveBase) { break }
  }
}
if (-not $driveBase) {
  Write-Error "Drive 上の『2 JX_論 文』が見つかりません。Google Drive Desktop が起動し同期済みか確認してください（相対: $rel）。"
  exit 1
}
Write-Host "[Drive] 入力ソース: $driveBase" -ForegroundColor Cyan

# --- 対象科目の決定 ---
if ($Subject) {
  if (-not $SubjMap.ContainsKey($Subject)) { Write-Error "未知の科目: $Subject（民/商/民訴/行政/憲/刑/刑訴 または 00N_科目）"; exit 1 }
  $targets = @($SubjMap[$Subject])
} else {
  $targets = @('001_刑法','002_刑事訴訟法','003_民法','004_商法','005_民事訴訟法','006_行政法','007_憲法')
}

$totPdf = 0; $totTr = 0
foreach ($dir in $targets) {
  foreach ($kind in @('重問PDF','講義逐語')) {
    $src = Join-Path (Join-Path $driveBase $dir) $kind
    $dst = Join-Path (Join-Path (Join-Path $ProjectRoot 'inputs\001_JX') $dir) $kind
    if (-not (Test-Path -LiteralPath $src)) { continue }
    if (-not (Test-Path -LiteralPath $dst)) {
      if (-not $DryRun) { New-Item -ItemType Directory -Path $dst -Force | Out-Null }
    }
    $pat = if ($kind -eq '重問PDF') { '*.pdf' } else { '*.txt' }
    $files = @(Get-ChildItem -LiteralPath $src -Filter $pat -File -ErrorAction SilentlyContinue)
    $copied = 0; $skipped = 0
    foreach ($f in $files) {
      $target = Join-Path $dst $f.Name
      if ((Test-Path -LiteralPath $target) -and -not $Force) { $skipped++; continue }
      if ($DryRun) { $copied++; continue }
      Copy-Item -LiteralPath $f.FullName -Destination $target -Force
      $copied++
    }
    if ($kind -eq '重問PDF') { $totPdf += $copied } else { $totTr += $copied }
    $tag = if ($DryRun) { '[DRYRUN] ' } else { '' }
    Write-Host ("  {0}{1}/{2}: コピー {3} / スキップ既存 {4} / ソース総数 {5}" -f $tag,$dir,$kind,$copied,$skipped,$files.Count)
  }
}
Write-Host ("`n完了: 重問PDF {0} 件 / 講義逐語 {1} 件 取り込み（{2}）" -f $totPdf,$totTr,$(if($DryRun){'DryRun'}else{'実コピー'})) -ForegroundColor Green
Write-Host "次: pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject <科目>  で TJR-J が回ります。" -ForegroundColor Yellow
