[CmdletBinding()]
param([switch]$SkipBuild)
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

if (-not (Test-Path 'seed-assets\asset-cache\.cache-manifest.json')) {
    throw 'Git LFS assets are missing. Run git lfs pull first.'
}
if (-not $SkipBuild) {
    npm ci
    npm run verify:source
    npm run dist:win
}

$portable = Get-ChildItem 'dist\WarCommander-*-portable.exe' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $portable) { throw 'Portable executable was not found in dist.' }

$bundle = Join-Path $RepoRoot 'release\WarCommander-offline-bundle'
if (Test-Path $bundle) { Remove-Item $bundle -Recurse -Force }
New-Item -ItemType Directory -Force -Path $bundle | Out-Null
Copy-Item $portable.FullName (Join-Path $bundle 'WarCommander.exe')
Copy-Item 'seed-assets\asset-cache' (Join-Path $bundle 'asset-cache') -Recurse
Copy-Item 'scripts\Install-OfflineBundle.ps1' (Join-Path $bundle 'Install.ps1')
Copy-Item 'README.md' (Join-Path $bundle 'PROJECT_README.md')

$zip = Join-Path $RepoRoot 'release\WarCommander-offline-bundle.zip'
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $bundle '*') -DestinationPath $zip -CompressionLevel Optimal
Write-Host "Offline bundle created: $zip"
