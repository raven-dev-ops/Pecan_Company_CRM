param(
    [string]$SubscriptionId = "",

    [string]$ResourceGroup = "",

    [Parameter(Mandatory = $false)]
    [string]$Location = "",

    [string]$ParametersFile = "",

    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent | Split-Path -Parent
$mainBicep = Join-Path $root "infra/azure/main.bicep"
$envLoader = Join-Path $root "scripts/azure/load_env.ps1"
if (Test-Path $envLoader) { & $envLoader | Out-Null }

if (-not $SubscriptionId) { $SubscriptionId = $env:AZURE_SUBSCRIPTION_ID }
if (-not $ResourceGroup) { $ResourceGroup = $env:AZURE_RESOURCE_GROUP }
if (-not $Location) { $Location = $env:AZURE_LOCATION }
if (-not $ParametersFile) { $ParametersFile = Join-Path $root "infra/azure/parameters.example.json" }

if (-not $SubscriptionId) { throw "SubscriptionId is required (arg or AZURE_SUBSCRIPTION_ID)." }
if (-not $ResourceGroup) { throw "ResourceGroup is required (arg or AZURE_RESOURCE_GROUP)." }

az account set --subscription $SubscriptionId | Out-Null
az group create --name $ResourceGroup --location $Location | Out-Null

if ($WhatIf) {
    az deployment group what-if `
      --resource-group $ResourceGroup `
      --template-file $mainBicep `
      --parameters @$ParametersFile
}
else {
    az deployment group create `
      --resource-group $ResourceGroup `
      --template-file $mainBicep `
      --parameters @$ParametersFile
}
