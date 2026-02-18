param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroup,

    [Parameter(Mandatory = $true)]
    [string]$SqlServerName,

    [Parameter(Mandatory = $true)]
    [string[]]$AllowedPublicIps
)

$ErrorActionPreference = "Stop"

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