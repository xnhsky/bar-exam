# jx-finalize.ps1 — JX 生成物の「永続化＋入力クリーンアップ」を 1 本にまとめる（pwsh ネイティブ）
#
# 各問題 ID について、以下を安全な順序で行う:
#   ① GitHub バックアップ : outputs/001_JX/{Subject}JX/{ID}.html ＋ outputs/002_TTS/{ID}/
#                          ＋ 副産物 outputs/ux/002_RX/{00N_科目}/{Subject}RX{NNN}_*.html
#                          ＋ outputs/ux/003_TREE/{00N_科目}/{ID}_TREE.html
#                          ＋ outputs/ux/001_ARIADNE/{00N_科目}/{ID}_ARIADNE.html を git add → commit
#   ② 入力クリーンアップ  : 【2026-07-09 恒久無効化】入力 PDF＋逐語は削除せず inputs に恒久保管する。
#       旧運用（Drive バックアップ後に git rm）は撤回。foreach 内で②に入る直前に必ず continue で
#       スキップする（①③は維持）。手動で消したい時のみ scripts/jx-cleanup-pdf.sh を明示実行。
#   ③ push（-Push 指定時。既定で実行・-NoPush で抑止）
#
# ※ Drive バックアップは jx-deploy.ps1 が担う。本スクリプトは「バックアップ済みを確認して消す」係。
# ※ 削除は git rm（履歴に残り復元可）。物理 rm はしない。
# ※ Drive 未マウント時はクリーンアップを HOLD（バックアップ確認不可）。--NoDriveCheck で緊急回避可。
#
# 使い方:
#   pwsh -NoProfile -File scripts/jx-finalize.ps1 -Subject 刑 -Ids 刑JX025,刑JX026
#   pwsh -NoProfile -File scripts/jx-finalize.ps1 -Subject 刑 -Ids 刑JX025 -DryRun
#   pwsh -NoProfile -File scripts/jx-finalize.ps1 -Subject 刑 -Ids 刑JX025 -NoPush
param(
    [Parameter(Mandatory=$true)][ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject,
    [Parameter(Mandatory=$true)][string[]]$Ids,   # 例: 刑JX025,刑JX026
    [switch]$NoPush,            # push を抑止（既定は push する）
    [switch]$NoCleanup,         # ①のみ（GitHub バックアップ）で入力削除はしない
    [switch]$NoDriveCheck,      # Drive 未マウント時の緊急用（git 履歴のみが復元元になる）
    [switch]$NoGate,            # 配布前ゲート（重複/ID/同期契約チェック）を抑止する緊急用
    [string]$ProjectRoot = '',  # 別 clone/root の成果物を永続化する場合に指定（未指定はこの repo）
    [switch]$DryRun
)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$DefaultProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
Set-Location $ProjectRoot

# pwsh -File 経由ではカンマ区切りが 1 要素になることがあるため正規化（"a,b" -> a, b）
$Ids = @($Ids | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })

# 科目 → Drive 科目フォルダ名（重問PDF / 講義逐語 はこの直下）
$DriveHtml = @{
    '刑'='001_刑法'; '刑訴'='002_刑事訴訟法'; '民'='003_民法'; '商'='004_商法';
    '民訴'='005_民事訴訟法'; '行政'='006_行政法'; '憲'='007_憲法'
}
$DriveRoot = $null
$cand = 'H:\マイドライブ\CATALINA＿G共有\■予備試験進行中'
if (Test-Path -LiteralPath $cand) {
    $jxDir = Get-ChildItem -LiteralPath $cand -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like '*JX*論*文*' } | Select-Object -First 1
    if ($jxDir) { $DriveRoot = $jxDir.FullName }
}

$PdfInDir   = Join-Path $ProjectRoot "inputs\001_JX\$Subject\重問PDF"
$TransInDir = Join-Path $ProjectRoot "inputs\001_JX\$Subject\講義逐語"
$JxOutDir   = Join-Path $ProjectRoot "outputs\001_JX\$($DriveHtml[$Subject])"
$TtsBase    = Join-Path $ProjectRoot "outputs\002_TTS\$($DriveHtml[$Subject])"

function Get-IdNumber([string]$id) {
    if ($id -match '(\d+)\s*$') { return [int]$Matches[1] }
    return $null
}
function Find-TranscriptFile([int]$num) {
    if (-not (Test-Path -LiteralPath $TransInDir)) { return $null }
    $cands = @(Get-ChildItem -LiteralPath $TransInDir -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -in '.txt','.md' } |
        Where-Object { ($_.BaseName -match '重問(?:逐語)?\s*0*(\d+)') -and ([int]$Matches[1] -eq $num) } |
        Sort-Object { $_.Extension -ne '.txt' })
    if ($cands.Count -gt 0) { return $cands[0] }
    return $null
}
# git ヘルパ（相対パスは forward slash で渡す）
function Git-Tracked([string]$relPath) {
    git ls-files --error-unmatch -- $relPath *> $null
    return ($LASTEXITCODE -eq 0)
}
function Git-Clean([string]$relPath) {
    git diff --quiet -- $relPath; $a = $LASTEXITCODE
    git diff --cached --quiet -- $relPath; $b = $LASTEXITCODE
    return (($a -eq 0) -and ($b -eq 0))
}

$pushNeeded = $false
$cleanupHold = $false

# === 作成日時スタンプ（ゲート前に先行実行・順序バグ修正 2026-07-23）===
# 新規/再生成の JX＋副産物は commit 前に lexia-genmeta を持たないため、直後の
# Lexia 同期契約ゲート（genmeta 有無を検査）が必ず ABORT していた（スタンプは従来
# commit ループ内＝ゲートより後で走っていた）。stamp-created-date.py は未追跡/dirty を
# 現在時刻(JST)で刻み既スタンプはスキップする冪等処理なので、ゲート前に先行実行して
# 新規生成物にも genmeta を付与し、ゲートを正しく通す（pre-commit フックの保険とも整合）。
if (-not $NoGate) {
    Write-Host "`n--- 作成日時スタンプ（ゲート前・冪等）: scripts/stamp-created-date.py ---" -ForegroundColor Cyan
    try { python -X utf8 (Join-Path $ProjectRoot 'scripts/stamp-created-date.py') | Out-Null }
    catch { Write-Host "  [stamp] skip: $_" -ForegroundColor Yellow }
}

# === 配布前ゲート: ファイル間の重複・ID 不整合チェック（Lexia 重複バグ再発防止）===
# title/doc-header/footer の問題コード不一致や、同一 title・同一本文の重複を検出したら
# commit/push せず中止する。git(=Lexia の取り込み元)に不整合な生成物を入れないための関門。
# ※ DryRun でも実行（事前確認になる）。緊急回避は -NoGate。
if (-not $NoGate) {
    Write-Host "`n--- 配布前ゲート: scripts/check-duplicates.py outputs ---" -ForegroundColor Cyan
    python (Join-Path $ProjectRoot 'scripts/check-duplicates.py') (Join-Path $ProjectRoot 'outputs')
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ABORT] 重複/ID 不整合を検出。修正するまで finalize（commit/push）を中止します。" -ForegroundColor Red
        Write-Host "        （緊急時のみ -NoGate で回避可能。原因は上記 D80/D81/D82 を参照）" -ForegroundColor DarkGray
        exit 1
    }
    Write-Host "[GATE PASS] 重複・ID 不整合なし。finalize を続行します。" -ForegroundColor Green
}

# === 配布前ゲート: Lexia 同期契約（fileName/code/title/category/sourcePath/genmeta）チェック ===
# Lexia が HTML を取り込むときに導出する fileName / code / title / subject / category と、
# raw HTML から読む sourcePath 相当・作成日時 genmeta・ARIADNE data-rx を横断検査する。
# 「HTML本文不足」「ID不一致」「作成日欠落で毎回更新扱い」になる生成物を git に入れない。
# ※ DryRun でも実行（事前確認になる）。緊急回避は -NoGate。
if (-not $NoGate) {
    Write-Host "`n--- 配布前ゲート: scripts/check-lexia-sync-contract.py --summary ---" -ForegroundColor Cyan
    python -X utf8 (Join-Path $ProjectRoot 'scripts/check-lexia-sync-contract.py') '--summary'
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ABORT] Lexia 同期契約の不整合を検出。修正するまで finalize（commit/push）を中止します。" -ForegroundColor Red
        Write-Host "        （緊急時のみ -NoGate で回避可能。原因は上記 ERROR を参照）" -ForegroundColor DarkGray
        exit 1
    }
    Write-Host "[GATE PASS] Lexia 同期契約の致命的不整合なし。finalize を続行します。" -ForegroundColor Green
}

# === 配布前ゲート: ARIADNE 正典（v1.2.0 PLACEHOLDER-LOCK）チェック ===
# canonical/ARIADNE.html と生成済み ARIADNE 全体を validate-ariadne.py で横断検証する。
# 問題文1字下げ・拾う文言近接2カラム・data-rx・スロット契約など、ARIADNE 正典化後の退行を
# commit/push 前に止める。※ DryRun でも実行（事前確認になる）。緊急回避は -NoGate。
if (-not $NoGate) {
    Write-Host "`n--- 配布前ゲート: scripts/check-ariadne-canonical.py ---" -ForegroundColor Cyan
    python -X utf8 (Join-Path $ProjectRoot 'scripts/check-ariadne-canonical.py')
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ABORT] ARIADNE 正典ガードで不整合を検出。修正するまで finalize（commit/push）を中止します。" -ForegroundColor Red
        Write-Host "        （緊急時のみ -NoGate で回避可能。原因は上記 check-ariadne-canonical の出力を参照）" -ForegroundColor DarkGray
        exit 1
    }
    Write-Host "[GATE PASS] ARIADNE 正典ガード PASS。finalize を続行します。" -ForegroundColor Green
}

# === 配布前ゲート: RX カバレッジ（dangling / UNREACHABLE 参照）チェック ===
# RX 論証カードの参照が dangling（リンク先なし）／UNREACHABLE（到達不能）になっていないかを
# 検査し、見つかれば commit/push せず中止する。直上の check-duplicates と同じ関門。
# ※ DryRun でも実行（事前確認になる）。緊急回避は -NoGate。
if (-not $NoGate) {
    Write-Host "`n--- 配布前ゲート: scripts/check-rx-coverage.py --strict ---" -ForegroundColor Cyan
    # -X utf8: stdout がパイプ/リダイレクト/headless（バッチ transcript・scheduled task 等）のとき
    #   Python が既定 cp932 で出力し、本スクリプトの ↔(U+2194)/—(U+2014) 等で UnicodeEncodeError
    #   →終了コード1で空振り ABORT してしまう事故を防ぐ（コンソール直結時のみ救われる不安定さを排除）。
    #   呼び出し側（jx-finalize 自分のファイル）に閉じた対処で、check-rx-coverage.py 本体は不変。
    python -X utf8 (Join-Path $ProjectRoot 'scripts/check-rx-coverage.py') '--strict'
    # ↑ 直上の check-duplicates と同じ $LASTEXITCODE / -NoGate 中止ハンドリングを踏襲
    #   （dangling か UNREACHABLE があれば exit 1 で commit を止める）
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ABORT] RX カバレッジの dangling/UNREACHABLE を検出。修正するまで finalize（commit/push）を中止します。" -ForegroundColor Red
        Write-Host "        （緊急時のみ -NoGate で回避可能。原因は上記 check-rx-coverage の出力を参照）" -ForegroundColor DarkGray
        exit 1
    }
    Write-Host "[GATE PASS] RX カバレッジの dangling/UNREACHABLE なし。finalize を続行します。" -ForegroundColor Green
}

foreach ($id in $Ids) {
    Write-Host "`n=== finalize $id ===" -ForegroundColor Cyan
    $num = Get-IdNumber $id
    $htmlRel = "outputs/001_JX/$($DriveHtml[$Subject])/$id.html"
    $htmlAbs = Join-Path $JxOutDir "$id.html"
    if (-not (Test-Path -LiteralPath $htmlAbs)) {
        Write-Host "[SKIP] HTML が無い: $htmlAbs" -ForegroundColor Yellow; continue
    }

    # --- ① GitHub バックアップ（HTML + TTS 台本 + RX/TREE 副産物）---
    $addPaths = @($htmlRel)
    $ttsDir = Join-Path $TtsBase $id
    if (Test-Path -LiteralPath $ttsDir) { $addPaths += "outputs/002_TTS/$($DriveHtml[$Subject])/$id" }
    # 副産物（RX 論証カード / ARBOR 樹形図）も同じコミットで永続化（存在するものだけ）
    if ($null -ne $num) {
        # RX は問題ごとにサブフォルダ（{科目}JX{NNN}/）へ折る（2026-06-20 恒久化）
        $rxDirAbs = Join-Path $ProjectRoot "outputs\ux\002_RX\$($DriveHtml[$Subject])\$id"
        $rxFilter = "${Subject}RX" + $num.ToString('000') + "_*.html"
        foreach ($r in @(Get-ChildItem -Path $rxDirAbs -Filter $rxFilter -File -ErrorAction SilentlyContinue)) {
            $addPaths += "outputs/ux/002_RX/$($DriveHtml[$Subject])/$id/$($r.Name)"
        }
    }
    $arbAbs = Join-Path $ProjectRoot "outputs\ux\003_TREE\$($DriveHtml[$Subject])\${id}_TREE.html"
    if (Test-Path -LiteralPath $arbAbs) { $addPaths += "outputs/ux/003_TREE/$($DriveHtml[$Subject])/${id}_TREE.html" }
    # ARIADNE 解法ナビ＋周回（Lexia 取込・存在すれば同じコミットで永続化）
    $ariaAbs = Join-Path $ProjectRoot "outputs\ux\001_ARIADNE\$($DriveHtml[$Subject])\${id}_ARIADNE.html"
    if (Test-Path -LiteralPath $ariaAbs) { $addPaths += "outputs/ux/001_ARIADNE/$($DriveHtml[$Subject])/${id}_ARIADNE.html" }
    if ($DryRun) {
        Write-Host "  [DRYRUN] git add $($addPaths -join ' ') ; commit"
    } else {
        # フッターに生成日時＋版を刻む（Lexia が raw 取得して読む・冪等・失敗は非致命）
        try { python scripts/stamp-created-date.py | Out-Null } catch { Write-Host "  [stamp] skip: $_" -ForegroundColor Yellow }
        git add -- $addPaths
        # 差分があれば commit（無ければ既コミット済みとして続行）
        git diff --cached --quiet -- $addPaths
        if ($LASTEXITCODE -ne 0) {
            git commit -q -m "chore(jx): $id を生成・GitHub バックアップ保存（HTML＋TTS台本＋RX/TREE/ARIADNE）"
            Write-Host "  [① backup] commit 済み: $id" -ForegroundColor Green
            $pushNeeded = $true
        } else {
            Write-Host "  [① backup] 既にコミット済み（差分なし）: $id" -ForegroundColor DarkGray
        }
    }

    if ($NoCleanup) { continue }

    # === 入力削除は恒久無効化（2026-07-09 ユーザー方針転換：入力を inputs に恒久保管）===
    # 旧運用「Drive バックアップ後に入力 PDF＋逐語を git rm」は撤回。①GitHub バックアップ（HTML＋
    # TTS＋副産物の commit/push）と③push は維持し、②入力クリーンアップ（git rm）は行わない。
    # どうしても削除したい場合のみ scripts/jx-cleanup-pdf.sh を手動で明示実行する（自動経路からは呼ばない）。
    Write-Host "  [② cleanup] 入力削除は恒久無効（inputs 恒久保管方針）→ スキップ" -ForegroundColor DarkGray
    continue

    # --- ② 入力クリーンアップ（PDF + 逐語）--- ※以下は無効化済み（復活は直上の continue を外す）
    if ($null -eq $num) { Write-Host "  [② cleanup] 番号抽出不可 → スキップ" -ForegroundColor Yellow; continue }

    # ガード(a): HTML がコミット済み＆差分なし
    if (-not $DryRun) {
        if (-not (Git-Tracked $htmlRel)) { Write-Host "  [HOLD] HTML 未追跡 → 入力を消さない" -ForegroundColor Yellow; $cleanupHold=$true; continue }
        if (-not (Git-Clean   $htmlRel)) { Write-Host "  [HOLD] HTML に未コミット差分 → 入力を消さない" -ForegroundColor Yellow; $cleanupHold=$true; continue }
    }

    $pdfAbs   = Join-Path $PdfInDir "$num.pdf"
    $trFile   = Find-TranscriptFile $num
    $rmRel = @()

    # ガード(b): Drive バックアップ存在確認
    $driveOk = $true
    if (-not $NoDriveCheck) {
        if ($null -eq $DriveRoot) {
            Write-Host "  [HOLD] Drive 未マウント → バックアップ確認不可。クリーンアップ中止（-NoDriveCheck で緊急回避可）" -ForegroundColor Yellow
            $cleanupHold=$true; continue
        }
        $drivePdf = Join-Path (Join-Path $DriveRoot $DriveHtml[$Subject]) "重問PDF\$num.pdf"
        if ((Test-Path -LiteralPath $pdfAbs) -and -not (Test-Path -LiteralPath $drivePdf)) {
            Write-Host "  [HOLD] PDF の Drive バックアップ無し: $drivePdf → 先に jx-deploy" -ForegroundColor Yellow; $driveOk=$false
        }
        if ($trFile) {
            $driveTr = Join-Path (Join-Path $DriveRoot $DriveHtml[$Subject]) "講義逐語\$($trFile.Name)"
            if (-not (Test-Path -LiteralPath $driveTr)) {
                Write-Host "  [HOLD] 逐語の Drive バックアップ無し: $driveTr → 先に jx-deploy" -ForegroundColor Yellow; $driveOk=$false
            }
        }
    }
    if (-not $driveOk) { $cleanupHold=$true; continue }

    if (Test-Path -LiteralPath $pdfAbs) { $rmRel += "inputs/001_JX/$Subject/重問PDF/$num.pdf" }
    if ($trFile) { $rmRel += "inputs/001_JX/$Subject/講義逐語/$($trFile.Name)" }
    if ($rmRel.Count -eq 0) { Write-Host "  [② cleanup] 削除対象なし（既に削除済み）" -ForegroundColor DarkGray; continue }

    if ($DryRun) {
        Write-Host "  [DRYRUN] git rm $($rmRel -join ' ') ; commit"
    } else {
        git rm --quiet -- $rmRel
        git commit -q -m "chore(jx): $id 処理済み入力（PDF＋逐語）を削除（Drive バックアップ済）"
        Write-Host "  [② cleanup] 入力削除 commit 済み: $($rmRel -join ', ')" -ForegroundColor Green
        $pushNeeded = $true
    }
}

# --- ③ push ---
if (-not $DryRun -and $pushNeeded -and -not $NoPush) {
    Write-Host "`n--- push origin master ---" -ForegroundColor Cyan
    $ok = $false
    for ($i=1; $i -le 3; $i++) {
        git push origin master
        if ($LASTEXITCODE -eq 0) { $ok=$true; break }
        Write-Host "[push] 失敗（試行 $i/3）。再試行..." -ForegroundColor Yellow
        Start-Sleep -Seconds ([math]::Pow(2,$i))
    }
    if ($ok) { Write-Host "[push] 完了。" -ForegroundColor Green }
    else { Write-Host "[push] 3 回失敗。後で手動 push してください。" -ForegroundColor Red; exit 1 }
}
if ($cleanupHold) { Write-Host "`n[NOTE] 一部 HOLD（入力未削除）あり。上記理由を解消後に再実行してください。" -ForegroundColor Yellow }
exit 0
