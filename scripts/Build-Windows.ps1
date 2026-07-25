[CmdletBinding()]
param([switch]$SkipInstall)
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
if (-not $SkipInstall) { npm ci }
npm run verify:source
npm run dist:win
Write-Host "Build completed: $RepoRoot\dist"
