[CmdletBinding()]
param([switch]$SeedAssets, [switch]$NoGpu)
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Exe = Join-Path $RepoRoot 'runtime\windows-x64\WarCommander.exe'
if (-not (Test-Path $Exe)) {
    Write-Host 'Recovered runtime is not extracted; restoring from split payloads.'
    & (Join-Path $PSScriptRoot 'Restore-RecoveredRuntime.ps1')
}
if (-not (Test-Path $Exe)) { throw 'Recovered runtime restoration failed.' }
if ($SeedAssets) {
    & (Join-Path $PSScriptRoot 'Seed-AssetCache.ps1') -Force -BackupExisting
}
$args = @()
if ($NoGpu) { $args += '--disable-gpu'; $args += '--disable-gpu-compositing' }
Start-Process -FilePath $Exe -ArgumentList $args -WorkingDirectory (Split-Path $Exe)
