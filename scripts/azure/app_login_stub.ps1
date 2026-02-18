param(
    [string]$SqlServerFqdn = "",

    [string]$SqlAdminUser = "",

    [string]$SqlAdminPassword = "",

    [string]$SqlScriptPath = "",

    [Parameter(Mandatory = $false)]
    [string]$DatabaseName = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent | Split-Path -Parent
$envLoader = Join-Path $root "scripts/azure/load_env.ps1"
if (Test-Path $envLoader) { & $envLoader | Out-Null }

if (-not $SqlServerFqdn) { $SqlServerFqdn = $env:AZURE_SQL_SERVER_FQDN }
if (-not $SqlAdminUser) { $SqlAdminUser = $env:AZURE_SQL_ADMIN_LOGIN }
if (-not $SqlAdminPassword) { $SqlAdminPassword = $env:AZURE_SQL_ADMIN_PASSWORD }
if (-not $SqlScriptPath) { $SqlScriptPath = Join-Path $root "infra/azure/sql/create_app_login_user.sql" }
if (-not $DatabaseName) { $DatabaseName = "master" }

if (-not $SqlServerFqdn) { throw "SqlServerFqdn is required (arg or AZURE_SQL_SERVER_FQDN)." }
if (-not $SqlAdminUser) { throw "SqlAdminUser is required (arg or AZURE_SQL_ADMIN_LOGIN)." }
if (-not $SqlAdminPassword) { throw "SqlAdminPassword is required (arg or AZURE_SQL_ADMIN_PASSWORD)." }
if (-not (Test-Path $SqlScriptPath)) { throw "SqlScriptPath not found: $SqlScriptPath" }

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
