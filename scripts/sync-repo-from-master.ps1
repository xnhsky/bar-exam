<#
  sync-repo-from-master.ps1

  Update another local clone/worktree to origin/master after a successful push.
  The target working tree is switched to master and fast-forwarded. Local work is
  preserved with git stash -u before switching branches.

  Manual use:
    pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-repo-from-master.ps1 `
      -ProjectRoot C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam-codex
#>
[CmdletBinding()]
param(
  [string]$ProjectRoot = 'C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam-codex',
  [string]$Remote = 'origin',
  [string]$Branch = 'master',
  [string]$WaitForSha = '',
  [int]$TimeoutSec = 240,
  [int]$PollSec = 3,
  [switch]$NoStash,
  [switch]$Quiet
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Say([string]$Message, [string]$Color = 'Gray') {
  $line = "[repo-sync $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
  if (-not $Quiet) { Write-Host $line -ForegroundColor $Color }
  if ($script:LogPath) { Add-Content -LiteralPath $script:LogPath -Value $line -Encoding utf8 }
}

$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$script:GitExe = (Get-Command git -CommandType Application -ErrorAction Stop).Source
function Invoke-RepoGit {
  & $script:GitExe -C $ProjectRoot @args
}

$LogsDir = Join-Path $ProjectRoot 'logs'
if (-not (Test-Path -LiteralPath $LogsDir)) {
  New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
}
$script:LogPath = Join-Path $LogsDir 'repo-sync-from-master.log'

Invoke-RepoGit rev-parse --is-inside-work-tree 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
  Say "not a git repository: $ProjectRoot" 'Red'
  exit 1
}

$remoteRef = "$Remote/$Branch"
$deadline = (Get-Date).AddSeconds($TimeoutSec)

while ($true) {
  Invoke-RepoGit fetch $Remote $Branch 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Say "fetch failed: $Remote $Branch" 'Red'
    exit 1
  }

  $remoteSha = (Invoke-RepoGit rev-parse $remoteRef 2>$null).Trim()
  if ([string]::IsNullOrWhiteSpace($WaitForSha)) { break }

  Invoke-RepoGit merge-base --is-ancestor $WaitForSha $remoteSha 2>$null
  if ($LASTEXITCODE -eq 0) { break }

  if ((Get-Date) -ge $deadline) {
    Say "remote did not reach pushed commit within ${TimeoutSec}s: $WaitForSha" 'Yellow'
    exit 3
  }
  Start-Sleep -Seconds $PollSec
}

$status = @(Invoke-RepoGit status --porcelain)
if ($status.Count -gt 0) {
  if ($NoStash) {
    Say "target has local changes; stopped because -NoStash was specified" 'Yellow'
    exit 2
  }
  $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
  Invoke-RepoGit stash push -u -m "auto-sync before $remoteRef $stamp" 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Say "git stash failed; target was not updated" 'Red'
    exit 1
  }
  Say "local changes were stashed before updating" 'Yellow'
}

$currentBranch = (Invoke-RepoGit branch --show-current 2>$null).Trim()
if ($currentBranch -ne $Branch) {
  $localBranch = (Invoke-RepoGit branch --list $Branch 2>$null).Trim()
  if ([string]::IsNullOrWhiteSpace($localBranch)) {
    Invoke-RepoGit switch -c $Branch --track $remoteRef
  } else {
    Invoke-RepoGit switch $Branch
  }
  if ($LASTEXITCODE -ne 0) {
    Say "failed to switch target to $Branch" 'Red'
    exit 1
  }
}

Invoke-RepoGit pull --ff-only $Remote $Branch
if ($LASTEXITCODE -ne 0) {
  Say "fast-forward pull failed; target was left on $Branch without destructive reset" 'Red'
  exit 1
}

$head = (Invoke-RepoGit rev-parse --short HEAD).Trim()
Say "updated $ProjectRoot to $Branch@$head" 'Green'
exit 0
