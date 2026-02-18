param(
    [Parameter(Mandatory = $true)]
    [string]$SqlServerFqdn,

    [Parameter(Mandatory = $true)]
    [string]$SqlAdminUser,

    [Parameter(Mandatory = $true)]
    [string]$SqlAdminPassword,

    [Parameter(Mandatory = $true)]
    [string]$SqlScriptPath,

    [Parameter(Mandatory = $false)]
    [string]$DatabaseName = "master"
)

$ErrorActionPreference = "Stop"

$sqlcmd = "sqlcmd"
& $sqlcmd `
  -S $SqlServerFqdn `
  -d $DatabaseName `
  -U $SqlAdminUser `
  -P $SqlAdminPassword `
  -b `
  -i $SqlScriptPath `
  -C

Write-Host "App login/user script executed."