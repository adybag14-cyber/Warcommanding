[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$Destination = (Join-Path $env:APPDATA 'warcommander\asset-cache'),
    [switch]$Force,
    [switch]$BackupExisting
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $RepoRoot 'seed-assets\asset-cache'
if (-not (Test-Path $Source)) { throw "Seed asset directory is missing. Run git lfs pull first: $Source" }

if (Test-Path $Destination) {
    if ($BackupExisting) {
        $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
        $backup = "$Destination.backup_$stamp"
        Copy-Item $Destination $backup -Recurse -Force
        Write-Host "Existing cache backed up to $backup"
    }
    if (-not $Force) { throw "Destination already exists: $Destination. Use -Force or -BackupExisting -Force." }
}

if ($PSCmdlet.ShouldProcess($Destination, 'Install recovered asset cache')) {
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Copy-Item (Join-Path $Source '*') $Destination -Recurse -Force
    Copy-Item (Join-Path $Source '.cache-manifest.json') $Destination -Force
    Write-Host "Asset cache installed at $Destination"
}
