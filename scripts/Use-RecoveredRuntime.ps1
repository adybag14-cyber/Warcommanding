[CmdletBinding()]
param([switch]$SeedAssets, [switch]$NoGpu)
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Exe = Join-Path $RepoRoot 'runtime\windows-x64\WarCommander.exe'
if (-not (Test-Path $Exe)) { throw 'Recovered runtime is missing. Run git lfs pull first.' }
if ($SeedAssets) {
    & (Join-Path $PSScriptRoot 'Seed-AssetCache.ps1') -Force -BackupExisting
}
$args = @()
if ($NoGpu) { $args += '--disable-gpu'; $args += '--disable-gpu-compositing' }
Start-Process -FilePath $Exe -ArgumentList $args -WorkingDirectory (Split-Path $Exe)
