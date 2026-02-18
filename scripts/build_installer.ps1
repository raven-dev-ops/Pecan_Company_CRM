param()

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Set-Location $root

$inno = "${env:ProgramFiles(x86)}\\Inno Setup 6\\ISCC.exe"
if (-not (Test-Path $inno)) {
    throw "Inno Setup ISCC.exe not found. Install Inno Setup 6 first."
}

& $inno "packaging\\PecanCRM.iss"
Write-Host "Installer build complete."