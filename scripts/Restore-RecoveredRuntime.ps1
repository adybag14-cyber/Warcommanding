[CmdletBinding()]
param([string]$Destination)
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
$args = @('tools/runtime-payload.py', 'restore')
if ($Destination) { $args += @('--destination', $Destination) }
python @args
