<#
  start-repo-sync.ps1

  Small launcher used by scripts/git-hooks/pre-push. It starts
  sync-repo-from-master.ps1 in a hidden background process and returns quickly,
  so git push is not blocked while the helper waits for origin/master to update.
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$SyncScript,
  [Parameter(Mandatory = $true)][string]$ProjectRoot,
  [string]$Remote = 'origin',
  [string]$Branch = 'master',
  [string]$WaitForSha = '',
  [int]$TimeoutSec = 240
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$SyncScript = (Resolve-Path -LiteralPath $SyncScript).Path
$SourceRoot = Split-Path -Parent (Split-Path -Parent $SyncScript)
$LogDir = Join-Path $SourceRoot 'logs'
if (-not (Test-Path -LiteralPath $LogDir)) {
  New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$launchLog = Join-Path $LogDir 'post-push-sync-codex-launch.log'
$stdout = Join-Path $LogDir "post-push-sync-codex-$stamp.out.log"
$stderr = Join-Path $LogDir "post-push-sync-codex-$stamp.err.log"

$runner = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
if (-not $runner) { $runner = (Get-Command powershell.exe -ErrorAction Stop).Source }

$argv = @(
  '-NoProfile',
  '-ExecutionPolicy', 'Bypass',
  '-File', $SyncScript,
  '-ProjectRoot', $ProjectRoot,
  '-Remote', $Remote,
  '-Branch', $Branch,
  '-TimeoutSec', "$TimeoutSec"
)
if (-not [string]::IsNullOrWhiteSpace($WaitForSha)) {
  $argv += @('-WaitForSha', $WaitForSha)
}

try {
  $p = Start-Process -FilePath $runner -ArgumentList $argv -WindowStyle Hidden `
    -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
  Add-Content -LiteralPath $launchLog -Encoding utf8 -Value (
    "[launcher $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] started pid=$($p.Id) target=$ProjectRoot branch=$Branch wait=$WaitForSha"
  )
  exit 0
} catch {
  Add-Content -LiteralPath $launchLog -Encoding utf8 -Value (
    "[launcher $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] failed: $($_.Exception.Message)"
  )
  exit 1
}
