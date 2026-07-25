[CmdletBinding()]
param(
    [string]$InstallDirectory = (Join-Path $env:LOCALAPPDATA 'WarCommanderRecovered'),
    [switch]$Force
)
$ErrorActionPreference = 'Stop'
$BundleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$CacheDestination = Join-Path $env:APPDATA 'warcommander\asset-cache'

if ((Test-Path $InstallDirectory) -and -not $Force) {
    throw "Install directory exists: $InstallDirectory. Use -Force to update it."
}
New-Item -ItemType Directory -Force -Path $InstallDirectory | Out-Null
Copy-Item (Join-Path $BundleRoot 'WarCommander.exe') $InstallDirectory -Force
New-Item -ItemType Directory -Force -Path $CacheDestination | Out-Null
Copy-Item (Join-Path $BundleRoot 'asset-cache\*') $CacheDestination -Recurse -Force
Copy-Item (Join-Path $BundleRoot 'asset-cache\.cache-manifest.json') $CacheDestination -Force
Write-Host "Installed executable to $InstallDirectory"
Write-Host "Installed cache to $CacheDestination"
