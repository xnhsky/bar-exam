<#
  tx-pull-inputs-from-drive.ps1 — Google Drive の TX 入力（抽出PDF＝1問1PDF）を
  ローカル inputs へ取り込む（PC2 セットアップ用・2026-08-15）

  目的：
    TX の入力 PDF は .gitignore 対象（`inputs/000_TX/**/*.pdf`・2026-07-09 方針転換）で
    git 共有されない。刑法・刑訴だけは方針転換より前にコミット済みのため git pull で降りてくるが、
    民法以降は Drive にしか無く、取り込まないと TJR-T（新規TX）が「該当なし」で永久にスキップされる。
    生成側 PC が `1 TX_短 答\{00N_科目}\抽出PDF\` へ置いた 1問1PDF を、別 PC が
    ローカル `inputs\000_TX\{00N_科目}\` へ取り込むと TJR-T／TJR-R が回る。
    （JX 側の対）scripts/jx-pull-inputs-from-drive.ps1

  使い方：
    pwsh -NoProfile -File scripts/tx-pull-inputs-from-drive.ps1              # 全科目
    pwsh -NoProfile -File scripts/tx-pull-inputs-from-drive.ps1 -Subject 民   # 特定科目
    pwsh -NoProfile -File scripts/tx-pull-inputs-from-drive.ps1 -DryRun       # コピーせず確認

  設計：
    - Drive マウント先（C:/D:/G:/H:/USERPROFILE）を自動検出。共有フォルダ
      `CATALINA＿G共有\■予備試験進行中` 配下の `1 TX_*`（実名は「1 TX_短 答」＝全角内に半角空白）
      をワイルドカードで解決する。
    - **1問1PDF だけを取り込む**＝ステム全体が数字のファイル（`123.pdf`）のみ。
      分割前の原本（`2026 短答過去問パーフェクト民法1.pdf` 等）は数字始まりでも取り込まない
      （tx-v13-runner の番号抽出 `^\d+` が 2026 を拾い 民TX2026 を生成する事故になるため）。
      原本は -IncludeSource 指定時のみローカル `_原本\` へ入れる（刑法のローカル慣行と同じ）。
    - `抽出PDF` に 1問1PDF が無い科目で `別PDF` 等の別系統フォルダがある場合は、
      番号体系が一致する保証が無いため既定では取り込まず、件数だけ報告する（-IncludeAlt で取り込む）。
    - 既存ファイルは上書きせずスキップ（冪等・ローカル優先）。-Force で上書き。
    - 一方向（Drive→ローカル）。ローカルの余剰は削除しない（/MIR ではない）。
#>
[CmdletBinding()]
param(
  [string]$Subject = '',              # 空=全科目。短縮名 民/商/民訴/行政/憲/刑/刑訴 可
  [switch]$DryRun,
  [switch]$Force,                     # 既存ローカルファイルを上書き
  [switch]$IncludeSource,             # 分割前の原本 PDF も `_原本\` へ取り込む
  [switch]$IncludeAlt                 # 抽出PDF に 1問1PDF が無い科目で 別系統フォルダも取り込む
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

# --- Drive 上の「1 TX_短 答」を自動検出 ---
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
  # 「1 TX_短 答」は全角文字の間に半角空白が入るためワイルドカードで解決する
  $tx = @(Get-ChildItem -LiteralPath $parent -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like '1 TX_*' })
  if ($tx.Count -gt 0) { $driveBase = $tx[0].FullName; break }
}
if (-not $driveBase) {
  Write-Error "Drive 上の『1 TX_短 答』が見つかりません。Google Drive Desktop が起動し同期済みか確認してください（相対: $relParent\1 TX_*）。"
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

# 1問1PDF＝ステム全体が数字（原本・目次・注記 PDF を確実に除外する）
function Test-ProblemPdf { param([System.IO.FileInfo]$f)
  return ([System.IO.Path]::GetFileNameWithoutExtension($f.Name) -match '^\d+$')
}

function Copy-Set {
  param([System.IO.FileInfo[]]$Files, [string]$Dst, [string]$Label)
  if (-not (Test-Path -LiteralPath $Dst)) {
    if (-not $DryRun) { New-Item -ItemType Directory -Path $Dst -Force | Out-Null }
  }
  $copied = 0; $skipped = 0
  foreach ($f in $Files) {
    $target = Join-Path $Dst $f.Name
    if ((Test-Path -LiteralPath $target) -and -not $Force) { $skipped++; continue }
    if (-not $DryRun) { Copy-Item -LiteralPath $f.FullName -Destination $target -Force }
    $copied++
  }
  $tag = if ($DryRun) { '[DRYRUN] ' } else { '' }
  Write-Host ("  {0}{1}: コピー {2} / スキップ既存 {3} / ソース総数 {4}" -f $tag,$Label,$copied,$skipped,$Files.Count)
  return $copied
}

$totPdf = 0; $totSrc = 0
foreach ($dir in $targets) {
  $srcSubj = Join-Path $driveBase $dir
  if (-not (Test-Path -LiteralPath $srcSubj)) { Write-Host ("  {0}: Drive に科目フォルダなし＝スキップ" -f $dir) -ForegroundColor DarkGray; continue }
  $dstSubj = Join-Path (Join-Path $ProjectRoot 'inputs\000_TX') $dir

  $src = Join-Path $srcSubj '抽出PDF'
  $all = @()
  if (Test-Path -LiteralPath $src) { $all = @(Get-ChildItem -LiteralPath $src -Filter '*.pdf' -File -ErrorAction SilentlyContinue) }
  $problem = @($all | Where-Object { Test-ProblemPdf $_ })
  $source  = @($all | Where-Object { -not (Test-ProblemPdf $_) })

  if ($problem.Count -eq 0) {
    # 抽出PDF が空／原本だけ＝未分割。別系統フォルダ（別PDF 等）の有無を報告する
    $alts = @(Get-ChildItem -LiteralPath $srcSubj -Directory -ErrorAction SilentlyContinue |
              Where-Object { $_.Name -ne '抽出PDF' } |
              ForEach-Object {
                $c = @(Get-ChildItem -LiteralPath $_.FullName -Filter '*.pdf' -File -ErrorAction SilentlyContinue | Where-Object { Test-ProblemPdf $_ })
                if ($c.Count -gt 0) { [PSCustomObject]@{ Name=$_.Name; Files=$c } }
              })
    if ($alts.Count -eq 0) {
      Write-Host ("  {0}: 1問1PDF なし（Drive 側が未分割）＝スキップ" -f $dir) -ForegroundColor DarkGray
    } elseif ($IncludeAlt) {
      foreach ($a in $alts) { $totPdf += (Copy-Set -Files $a.Files -Dst $dstSubj -Label "$dir/$($a.Name)") }
    } else {
      $names = ($alts | ForEach-Object { "$($_.Name)=$($_.Files.Count)件" }) -join ' / '
      Write-Host ("  {0}: 抽出PDF に 1問1PDF なし。別系統あり（{1}）＝番号体系不明のため既定では取り込まない（-IncludeAlt で取込）" -f $dir,$names) -ForegroundColor Yellow
    }
  } else {
    $totPdf += (Copy-Set -Files $problem -Dst $dstSubj -Label "$dir/抽出PDF")
  }

  if ($source.Count -gt 0) {
    if ($IncludeSource) {
      $totSrc += (Copy-Set -Files $source -Dst (Join-Path $dstSubj '_原本') -Label "$dir/_原本")
    } else {
      Write-Host ("    ※ 分割前の原本 {0} 件は取り込まない（-IncludeSource で `_原本\` へ取込）: {1}" -f $source.Count, (($source | Select-Object -First 3 -ExpandProperty Name) -join ', ')) -ForegroundColor DarkGray
    }
  }
}

Write-Host ("`n完了: 1問1PDF {0} 件 / 原本 {1} 件 取り込み（{2}）" -f $totPdf,$totSrc,$(if($DryRun){'DryRun'}else{'実コピー'})) -ForegroundColor Green
Write-Host "次: pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject <科目>  で TJR-T / TJR-R が回ります。" -ForegroundColor Yellow
