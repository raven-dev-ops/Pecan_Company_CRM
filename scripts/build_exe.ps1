param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Set-Location $root

if ($Clean) {
    if (Test-Path build) { Remove-Item -Recurse -Force build }
    if (Test-Path dist) { Remove-Item -Recurse -Force dist }
}

python -m PyInstaller --noconfirm packaging/pecan_crm.spec
Write-Host "Build complete: $root\\dist\\PecanCRM"