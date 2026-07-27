# tjr-claim.ps1 — 二台同時 TJR の衝突対策ライブラリ（claim 予約＋安全 push・2026-07-27）
#
# 【使い方】各ランナーが dot-source して使う（単体起動はしない）:
#   . (Join-Path $ProjectRoot 'scripts\tjr-claim.ps1')
#
# 【背景】T/J/R の対象選定は決定論的（T=フロンティア最若番・R=旧版番号順・J=未生成最若番）なので、
#   OWNER PC と xnrg2 PC が同時に TJR を回すと両者が同じ問題を選び、生成 20〜35 分（JX は 1〜2 時間）を
#   丸ごと二重消費した上で push が衝突する。さらに旧実装は push 衝突時の pull --rebase が同一ファイル
#   add/add で途中停止したまま次問へ進み、以降の全 commit が unmerged paths で失敗する連鎖があった。
#
# 【対策1＝claim 予約】生成開始前に locks/claims/{問題ID}.json（PC名・UTC時刻・ストリーム・TTL）を
#   commit→push して番号を原子的に予約する（GitHub の push 直列化を分散ロックとして使う）。
#   push が拒否されたら pull --rebase -X ours で追随し、claim ファイルの pc を読み直して勝敗を判定
#   （競り負け＝自分の claim commit は空化して自動 drop され、ファイルは相手の内容になる）。
#   先取りされた問題は SKIP して次候補へ繰り上げる。TTL 超過 claim は失効＝他 PC が引き継ぎ可能
#   （クラッシュした PC が番号を永久占有しない）。リモート到達不可ならば予約なしで続行する
#   （オフライン単機運転を止めない。その場合は対策2の push 側防御が最終網）。
#
# 【対策2＝安全 push（first-push-wins）】push 拒否 → `pull --rebase -X ours` → 再 push。
#   rebase 中の ours は upstream（リモート）側なので、同一ファイル衝突はリモート先着版を採用し、
#   自分の commit は空化して自動 drop される（git 2.43 で add/add 同一パス異内容の実測検証済み）。
#   -X で解決できない衝突（claim の modify/delete 等）は必ず rebase --abort で復帰して commit を
#   ローカル保持する＝rebase 途中放置の禁止（連鎖 commit 失敗の根絶）。
#
# 【対策3＝夜間タスクの時差】register-tjr-night-task.ps1 -StaggerMinutes（AUTO＝xnrg2 のみ +60 分）。
#
# 正典ドキュメント: docs/run-patterns.md「二台同時 TJR の衝突対策」の節。
# 検証: 2 クローン＋bare リポジトリでの競走テスト（PR の検証記録参照）。
#
# 【関数の出力規律】PowerShell 関数は捕捉されない出力が全て戻り値に混入するため、
#   本ファイル内の git / New-Item 等は必ず Out-Null か変数受けで出力を殺す（TJR.ps1 の
#   Out-Host 対策と同じ理由）。戻り値は明示の return だけにする。

# リモート名・ブランチは本線 master 固定（テストは環境変数で差し替え可能）
$script:TjrRemoteName   = if ($env:TJR_CLAIM_REMOTE) { $env:TJR_CLAIM_REMOTE } else { 'origin' }
$script:TjrRemoteBranch = if ($env:TJR_CLAIM_BRANCH) { $env:TJR_CLAIM_BRANCH } else { 'master' }

function Get-TjrPcName {
    # claim の所有者識別子。両 PC の git 識別子は同一（xnh）なのでマシン名で区別する。
    if ($env:TJR_CLAIM_PC) { return $env:TJR_CLAIM_PC }
    return [System.Environment]::MachineName
}

function ConvertTo-TjrRelPath { param([string]$ProjectRoot, [string]$Path)
    # 絶対パス → repo 相対（forward slash）。git の pathspec / cat-file 用。
    $root = (Resolve-Path -LiteralPath $ProjectRoot).Path
    $p = $Path
    if ($p.StartsWith($root)) { $p = $p.Substring($root.Length) }
    return ($p -replace '\\', '/').TrimStart('/')
}

function Get-TjrClaimRelPath { param([string]$ProblemId)
    return "locks/claims/$ProblemId.json"
}

function Test-TjrRemotePath { param([string]$ProjectRoot, [string]$RelPath)
    # 追跡 ref（origin/master）にそのパスが存在するか。直前の fetch / push 成功が前提の鮮度。
    $spec = "$($script:TjrRemoteName)/$($script:TjrRemoteBranch):$RelPath"
    & git -C $ProjectRoot cat-file -e $spec 2>$null
    return ($LASTEXITCODE -eq 0)
}

function Test-TjrRemoteContent { param([string]$ProjectRoot, [string]$RelPath, [string]$Pattern)
    # 追跡 ref 上のファイル内容に正規表現がヒットするか（R の「相手が v13 再生成済み」判定用）。
    $spec = "$($script:TjrRemoteName)/$($script:TjrRemoteBranch):$RelPath"
    $hit = (& git -C $ProjectRoot show $spec 2>$null | Select-String -Pattern $Pattern -Quiet)
    return [bool]$hit
}

function Invoke-TjrSafePull { param([string]$ProjectRoot)
    # first-push-wins 追随: 同一ファイル衝突はリモート先着版を採用（rebase 中の ours=upstream）。
    # 自分の重複 commit は空化して自動 drop される。解決不能（claim の modify/delete 等）は
    # rebase --abort で必ず復帰して $false（rebase 途中放置＝連鎖 commit 失敗の禁止）。
    & git -C $ProjectRoot -c rebase.autoStash=true pull --rebase -X ours $script:TjrRemoteName $script:TjrRemoteBranch 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { return $true }
    & git -C $ProjectRoot rebase --abort 2>&1 | Out-Null
    return $false
}

function Sync-TjrRepo { param([string]$ProjectRoot)
    # 起動時／バッチ頭の追随。相手 PC の生成済みを「未生成」と誤認して二重生成しないための前提同期。
    # 旧実装は起動時 pull が無く、pull を怠った側が相手の生成済み番号を作り直す事故経路があった。
    & git -C $ProjectRoot fetch $script:TjrRemoteName $script:TjrRemoteBranch 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[SYNC] fetch 失敗（オフライン？）→ ローカル状態で続行" -ForegroundColor Yellow
        return $false
    }
    if (Invoke-TjrSafePull -ProjectRoot $ProjectRoot) { return $true }
    Write-Host "[SYNC] pull --rebase が自動解決不能 → 復帰してローカル状態で続行（push 時に再追随）" -ForegroundColor Yellow
    return $false
}

function Invoke-TjrSafePush { param([string]$ProjectRoot, [int]$MaxTries = 3, [string]$Label = '')
    # push 拒否 → 追随（first-push-wins）→ 再 push。旧実装（tx-v13-runner / jx-finalize /
    # rx-arb-autofill の素朴リトライ）が持っていた「rebase 途中放置」「pull 無し 3 連敗」を根絶する。
    $tag = if ($Label) { "[$Label] " } else { '' }
    for ($i = 1; $i -le $MaxTries; $i++) {
        & git -C $ProjectRoot push $script:TjrRemoteName "HEAD:$($script:TjrRemoteBranch)" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { return $true }
        Write-Host "$($tag)push 拒否/失敗（試行 $i/$MaxTries）→ リモート先行へ rebase 追随（同一ファイルは先着版を採用）" -ForegroundColor Yellow
        if (-not (Invoke-TjrSafePull -ProjectRoot $ProjectRoot)) {
            Write-Host "$($tag)自動解決できない競合 → rebase 中断を復帰。commit はローカル保持（次回 push か TJR-F が回収）" -ForegroundColor Yellow
        }
        Start-Sleep -Seconds ([Math]::Min(30, 5 * $i))
    }
    # 追随で自分の commit が全て drop（相手の先着版採用）され「push する物が無い」なら実質成功
    $ahead = (& git -C $ProjectRoot rev-list --count "$($script:TjrRemoteName)/$($script:TjrRemoteBranch)..HEAD" 2>$null) -join ''
    if ($LASTEXITCODE -eq 0 -and $ahead.Trim() -eq '0') { return $true }
    return $false
}

function Read-TjrClaim { param([string]$ProjectRoot, [string]$ClaimRel, [switch]$Remote)
    # claim JSON を worktree または追跡 ref から読む。壊れていれば $null（＝失効扱いに落ちる）。
    try {
        if ($Remote) {
            $spec = "$($script:TjrRemoteName)/$($script:TjrRemoteBranch):$ClaimRel"
            $raw = (& git -C $ProjectRoot show $spec 2>$null) -join "`n"
            if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($raw)) { return $null }
        } else {
            $abs = Join-Path $ProjectRoot $ClaimRel
            if (-not (Test-Path -LiteralPath $abs)) { return $null }
            $raw = Get-Content -LiteralPath $abs -Raw -Encoding utf8
        }
        return ($raw | ConvertFrom-Json)
    } catch { return $null }
}

function Test-TjrClaimExpired { param($Claim)
    # TTL 超過＝失効（他 PC が引き継ぎ可能）。解釈不能な claim も失効扱い＝番号の永久ブロックを防ぐ。
    if ($null -eq $Claim) { return $true }
    try {
        $created = [DateTimeOffset]::Parse([string]$Claim.createdAt).UtcDateTime
        $ttl = [double]$Claim.ttlMinutes
        if ($ttl -le 0) { $ttl = 240 }
        return (([DateTime]::UtcNow - $created).TotalMinutes -gt $ttl)
    } catch { return $true }
}

function Undo-TjrClaimCommit { param([string]$ProjectRoot, [string]$ProblemId)
    # 直前の claim commit（HEAD）だけを取り消し、claim パスを元の状態へ戻す。
    # 他の未 push commit・無関係な dirty には触れない（reset --hard は使わない）。
    $claimRel = Get-TjrClaimRelPath $ProblemId
    $claimAbs = Join-Path $ProjectRoot $claimRel
    $head = ((& git -C $ProjectRoot log -1 --format=%s 2>$null) -join '')
    if ($head -notlike "chore(tjr-claim): $ProblemId を予約*") { return }
    & git -C $ProjectRoot reset --soft HEAD~1 2>&1 | Out-Null
    $inHead = ((& git -C $ProjectRoot ls-tree --name-only HEAD -- $claimRel 2>$null) -join '').Trim()
    if ($inHead) {
        & git -C $ProjectRoot checkout -q HEAD -- $claimRel 2>&1 | Out-Null
    } else {
        & git -C $ProjectRoot reset -q HEAD -- $claimRel 2>&1 | Out-Null
        Remove-Item -LiteralPath $claimAbs -Force -ErrorAction SilentlyContinue
    }
}

function Request-TjrClaim {
    param(
        [string]$ProjectRoot,
        [string]$ProblemId,
        [string]$Stream = '',
        [int]$TtlMinutes = 240,
        [string[]]$RemoteExistsRelPaths = @()
    )
    # 問題 1 件の生成予約。戻り値（文字列）:
    #   CLAIMED          … 予約成立（リモートに claim が載った）→ 生成してよい
    #   CLAIMED_OFFLINE  … リモート到達不可等で予約は載っていないが続行してよい（単機運転）
    #   REMOTE_EXISTS    … 相手 PC が成果物を push 済み → この問題は SKIP
    #   CLAIMED_BY_OTHER … 相手 PC が予約中（TTL 内）→ この問題は SKIP して次候補へ
    #   ERROR            … 予約手続きが自動解決不能 → この問題は今回 SKIP（次バッチで再挑戦）
    $pc = Get-TjrPcName
    $claimRel = Get-TjrClaimRelPath $ProblemId
    $claimAbs = Join-Path $ProjectRoot $claimRel

    & git -C $ProjectRoot fetch $script:TjrRemoteName $script:TjrRemoteBranch 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[CLAIM] $ProblemId：リモート到達不可 → 予約なしで続行（オフライン運転）" -ForegroundColor Yellow
        return 'CLAIMED_OFFLINE'
    }
    # ローカルが古いまま claim を書くと、リモートに既存の claim ファイルが在るケース（失効引き継ぎ等）で
    # add/add になり、-X ours（リモート先着優先）が失効 claim 側を勝たせて正当な引き継ぎが失敗する
    # （2 クローン実機テストで検出）。書く前に必ず追随し、引き継ぎを「modify」として乗せる。
    [void](Invoke-TjrSafePull -ProjectRoot $ProjectRoot)

    # 相手 PC が既に成果物を push 済みなら生成不要（新規系のみ。R/F は存在が前提なので渡さない）
    foreach ($rel in @($RemoteExistsRelPaths | Where-Object { $_ })) {
        if (Test-TjrRemotePath -ProjectRoot $ProjectRoot -RelPath $rel) {
            Write-Host "[SKIP-REMOTE] $ProblemId：リモートに成果物あり（相手 PC が生成済み）: $rel" -ForegroundColor DarkYellow
            return 'REMOTE_EXISTS'
        }
    }

    # 有効な他 PC claim があれば見送り。失効 claim は引き継ぐ（上書き＝modify なので add/add にならない）
    $remoteClaim = Read-TjrClaim -ProjectRoot $ProjectRoot -ClaimRel $claimRel -Remote
    if ($null -ne $remoteClaim -and "$($remoteClaim.pc)" -ne $pc) {
        if (-not (Test-TjrClaimExpired $remoteClaim)) {
            Write-Host "[SKIP-CLAIMED] $ProblemId：$($remoteClaim.pc) が予約中（$($remoteClaim.createdAt)・TTL $($remoteClaim.ttlMinutes) 分）→ 次候補へ" -ForegroundColor DarkYellow
            return 'CLAIMED_BY_OTHER'
        }
        Write-Host "[CLAIM] $ProblemId：$($remoteClaim.pc) の失効 claim を引き継ぐ（TTL 超過）" -ForegroundColor DarkYellow
    }

    # claim 書き込み → commit（claim パスのみの部分 commit）→ push（成功＝予約成立）
    $dir = Split-Path -Parent $claimAbs
    if (-not (Test-Path $dir)) { New-Item -Path $dir -ItemType Directory -Force | Out-Null }
    $payload = [ordered]@{
        problemId  = $ProblemId
        pc         = $pc
        stream     = $Stream
        createdAt  = [DateTime]::UtcNow.ToString('o')
        ttlMinutes = $TtlMinutes
        note       = 'TJR 生成予約（docs/run-patterns.md 衝突対策の節）'
    } | ConvertTo-Json
    [System.IO.File]::WriteAllText($claimAbs, $payload + "`n", (New-Object System.Text.UTF8Encoding($false)))
    & git -C $ProjectRoot add -- $claimRel 2>&1 | Out-Null
    & git -C $ProjectRoot commit -m "chore(tjr-claim): $ProblemId を予約（$pc・$Stream）" -- $claimRel 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[CLAIM] $ProblemId：claim commit 失敗（repo 状態異常？）→ この問題は今回見送り" -ForegroundColor Yellow
        Remove-Item -LiteralPath $claimAbs -Force -ErrorAction SilentlyContinue
        & git -C $ProjectRoot checkout -q -- $claimRel 2>$null
        return 'ERROR'
    }

    for ($i = 1; $i -le 3; $i++) {
        & git -C $ProjectRoot push $script:TjrRemoteName "HEAD:$($script:TjrRemoteBranch)" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $mine = Read-TjrClaim -ProjectRoot $ProjectRoot -ClaimRel $claimRel
            if ($null -ne $mine -and "$($mine.pc)" -eq $pc) {
                # 押し込み中に相手の完成品が届いた稀ケースの最終確認（rebase 追随で取り込まれる）
                foreach ($rel in @($RemoteExistsRelPaths | Where-Object { $_ })) {
                    if (Test-TjrRemotePath -ProjectRoot $ProjectRoot -RelPath $rel) {
                        Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $ProblemId -Reason '成果物が先に出現'
                        Write-Host "[SKIP-REMOTE] $ProblemId：予約中に相手 PC の成果物が到着 → 予約解放して SKIP" -ForegroundColor DarkYellow
                        return 'REMOTE_EXISTS'
                    }
                }
                Write-Host "[CLAIM] $ProblemId を予約（$pc・TTL $TtlMinutes 分）" -ForegroundColor DarkGray
                return 'CLAIMED'
            }
            Write-Host "[SKIP-CLAIMED] $ProblemId：予約競走で相手 PC が先着 → 次候補へ" -ForegroundColor DarkYellow
            return 'CLAIMED_BY_OTHER'
        }
        # push 拒否＝リモート先行。追随して claim の所有者を読み直す
        if (-not (Invoke-TjrSafePull -ProjectRoot $ProjectRoot)) {
            Undo-TjrClaimCommit -ProjectRoot $ProjectRoot -ProblemId $ProblemId
            Write-Host "[CLAIM] $ProblemId：予約手続きが自動解決不能 → claim commit を取り消して見送り" -ForegroundColor Yellow
            return 'ERROR'
        }
        $now = Read-TjrClaim -ProjectRoot $ProjectRoot -ClaimRel $claimRel
        if ($null -eq $now -or "$($now.pc)" -ne $pc) {
            Write-Host "[SKIP-CLAIMED] $ProblemId：予約競走で相手 PC が先着（rebase 追随で確認）→ 次候補へ" -ForegroundColor DarkYellow
            return 'CLAIMED_BY_OTHER'
        }
        Start-Sleep -Seconds (3 * $i)
    }
    Write-Host "[CLAIM] $ProblemId：claim push 未達（ネットワーク？）→ 予約 commit をローカル保持のまま続行" -ForegroundColor Yellow
    return 'CLAIMED_OFFLINE'
}

function Remove-TjrClaimLocal { param([string]$ProjectRoot, [string]$ProblemId)
    # 完成 commit に同梱する claim 解放（削除＋stage のみ・commit しない）。
    # 自分の claim の時だけ削除する＝他 PC の claim には触れない（modify/delete 衝突の予防。
    # 解放漏れは TTL 失効＋Clear-TjrStaleClaims が回収する）。
    $claimRel = Get-TjrClaimRelPath $ProblemId
    $claimAbs = Join-Path $ProjectRoot $claimRel
    $mine = Read-TjrClaim -ProjectRoot $ProjectRoot -ClaimRel $claimRel
    if ($null -eq $mine -or "$($mine.pc)" -ne (Get-TjrPcName)) { return $false }
    Remove-Item -LiteralPath $claimAbs -Force -ErrorAction SilentlyContinue
    & git -C $ProjectRoot add -- $claimRel 2>&1 | Out-Null
    return $true
}

function Release-TjrClaim { param([string]$ProjectRoot, [string]$ProblemId, [string]$Reason = '解放', [switch]$NoPush)
    # 生成失敗などで成果物 commit が無い場合の単独解放（commit＋push・非致命）。
    $claimRel = Get-TjrClaimRelPath $ProblemId
    if (-not (Remove-TjrClaimLocal -ProjectRoot $ProjectRoot -ProblemId $ProblemId)) { return }
    & git -C $ProjectRoot commit -m "chore(tjr-claim): $ProblemId の予約を解放（$Reason）" -- $claimRel 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[CLAIM] $ProblemId の予約を解放（$Reason）" -ForegroundColor DarkGray
        if (-not $NoPush) { [void](Invoke-TjrSafePush -ProjectRoot $ProjectRoot -MaxTries 2 -Label 'claim解放') }
    }
}

function Clear-TjrStaleClaims { param([string]$ProjectRoot, [switch]$NoPush)
    # TTL 失効 claim の掃除（TJR が毎バッチ先頭で呼ぶ）。クラッシュ・解放漏れの残骸を回収し、
    # 番号の永久占有を防ぐ。対象が無ければ無音で戻る。
    $dirAbs = Join-Path $ProjectRoot 'locks/claims'
    if (-not (Test-Path $dirAbs)) { return }
    $removed = @()
    foreach ($f in @(Get-ChildItem -Path $dirAbs -Filter '*.json' -File -ErrorAction SilentlyContinue)) {
        $rel = "locks/claims/$($f.Name)"
        $c = Read-TjrClaim -ProjectRoot $ProjectRoot -ClaimRel $rel
        if (Test-TjrClaimExpired $c) {
            & git -C $ProjectRoot rm -q --ignore-unmatch -- $rel 2>&1 | Out-Null
            if (Test-Path -LiteralPath $f.FullName) { Remove-Item -LiteralPath $f.FullName -Force -ErrorAction SilentlyContinue }
            $removed += [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
        }
    }
    if ($removed.Count -eq 0) { return }
    & git -C $ProjectRoot commit -m "chore(tjr-claim): 失効 claim を掃除（$($removed -join '、')）" -- 'locks/claims' 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[CLAIM] 失効 claim $($removed.Count) 件を掃除: $($removed -join ', ')" -ForegroundColor DarkGray
        if (-not $NoPush) { [void](Invoke-TjrSafePush -ProjectRoot $ProjectRoot -MaxTries 2 -Label 'claim掃除') }
    }
}
