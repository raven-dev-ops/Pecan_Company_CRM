param(
    [string]$ResourceGroup = "",

    [string]$SqlServerName = "",

    [string[]]$AllowedPublicIps = @()
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent | Split-Path -Parent
$envLoader = Join-Path $root "scripts/azure/load_env.ps1"
if (Test-Path $envLoader) { & $envLoader | Out-Null }

if (-not $ResourceGroup) { $ResourceGroup = $env:AZURE_RESOURCE_GROUP }
if (-not $SqlServerName) { $SqlServerName = $env:AZURE_SQL_SERVER_NAME }
if ($AllowedPublicIps.Count -eq 0 -and $env:AZURE_ALLOWED_IPS) {
    $AllowedPublicIps = $env:AZURE_ALLOWED_IPS.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ }
}

if (-not $ResourceGroup) { throw "ResourceGroup is required (arg or AZURE_RESOURCE_GROUP)." }
if (-not $SqlServerName) { throw "SqlServerName is required (arg or AZURE_SQL_SERVER_NAME)." }
if ($AllowedPublicIps.Count -eq 0) { throw "AllowedPublicIps are required (arg or AZURE_ALLOWED_IPS)." }

foreach ($ip in $AllowedPublicIps) {
    $safe = $ip.Replace('.', '-')
    $rule = "client-$safe"
    az sql server firewall-rule create `
      --resource-group $ResourceGroup `
      --server $SqlServerName `
      --name $rule `
      --start-ip-address $ip `
      --end-ip-address $ip | Out-Null
}

Write-Host "Firewall allowlist updated for $($AllowedPublicIps.Count) IP(s)."
