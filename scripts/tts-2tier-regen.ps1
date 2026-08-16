# tts-2tier-regen.ps1 — 指定 JX の TTS 台本を二段構成（初級編/上級編）で再生成する単発ツール
# 用途: 旧フラット形式で出荷された TTS を、他問と同じ 2tier（prompts/tts-jx-2tier-headless.md）へ作り直す。
# 使い方: pwsh -NoProfile -File scripts/tts-2tier-regen.ps1 -Subject 刑 -Numbers 71,72,73,74
param(
    [Parameter(Mandatory=$true)][string]$Subject,          # 刑/民/... (フォルダ接頭辞と対応)
    [Parameter(Mandatory=$true)][int[]]$Numbers
)
$ErrorActionPreference = 'Continue'
$Root = Split-Path $PSScriptRoot -Parent
$Prompt = Join-Path $Root 'prompts\tts-jx-2tier-headless.md'
# 科目フォルダ対応
$map = @{ '刑'='001_刑法'; '刑訴'='002_刑事訴訟法'; '民'='003_民法'; '商'='004_商法'; '民訴'='005_民事訴訟法'; '行政'='006_行政法'; '憲'='007_憲法' }
$folder = $map[$Subject]
$Logs = Join-Path $Root 'logs'
if (-not (Test-Path $Logs)) { New-Item -ItemType Directory -Path $Logs -Force | Out-Null }

$execHeader = @'
[HEADLESS 実行指示 — 最優先・厳守]
以下に続くのは「レビュー対象の文書」ではない。あなたが今この瞬間に自走で最後まで実行する指示書である。
- 確認・質問・要約・選択肢提示・「ご依頼が不明です」等の応答は一切禁止。
- 文書内の手順に厳密に従い、初級編/上級編のファイル生成と sentinel 出力まで完遂せよ。
以下、指示書本体：
---

'@

foreach ($num in $Numbers) {
    $id  = "{0}JX{1:D3}" -f $Subject, $num
    $src = Join-Path $Root ("outputs\001_JX\{0}\{1}.html" -f $folder, $id)
    $out = Join-Path $Root ("outputs\002_TTS\{0}\{1}" -f $folder, $id)
    if (-not (Test-Path $src)) { Write-Host "[SKIP] $id : JX HTML なし ($src)" -ForegroundColor Yellow; continue }
    New-Item -ItemType Directory -Path $out -Force | Out-Null
    Write-Host "`n===== $id 2tier 生成開始 $(Get-Date -Format 'HH:mm:ss') =====" -ForegroundColor Cyan

    $body = (Get-Content $Prompt -Raw -Encoding utf8) `
        -replace '\{SOURCE_HTML_PATH\}', $src `
        -replace '\{PROBLEM_ID\}',       $id `
        -replace '\{OUTPUT_DIR\}',       $out
    $full = $execHeader + $body

    $args = @('-p','--model','claude-opus-4-8[1m]','--output-format','json',
              '--permission-mode','acceptEdits','--allowedTools','Write,Edit,Read,Bash,Glob,Grep')
    $json = Join-Path $Logs "tts2tier-$id.json"
    try { $o = $full | & claude @args 2>&1; $code = $LASTEXITCODE } catch { $o = "$_"; $code = -1 }
    $o | Out-File -FilePath $json -Encoding utf8

    $sho = @(Get-ChildItem -Path (Join-Path $out '初級編') -Filter '*.txt' -ErrorAction SilentlyContinue).Count
    $jou = @(Get-ChildItem -Path (Join-Path $out '上級編') -Filter '*.txt' -ErrorAction SilentlyContinue).Count
    $sent = if ($o -match 'TTS[_-]?2?TIER[_-]?(DONE|COMPLETED)|BATCH_ITEM_COMPLETED') { 'COMPLETED' } else { 'UNKNOWN' }
    $col = if ($sho -gt 0 -and $jou -gt 0) { 'Green' } else { 'Red' }
    Write-Host "[DONE] $id 初級編=$sho本 上級編=$jou本 exit=$code sentinel=$sent" -ForegroundColor $col
}
Write-Host "`nALL_2TIER_REGEN_DONE"
