[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
python tools/runtime-payload.py create
python tools/runtime-payload.py verify
Write-Host 'Recovered runtime payload rebuilt and verified.'
