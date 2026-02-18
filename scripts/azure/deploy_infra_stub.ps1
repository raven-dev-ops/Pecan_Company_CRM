param(
    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId,

    [Parameter(Mandatory = $true)]
    [string]$ResourceGroup,

    [Parameter(Mandatory = $false)]
    [string]$Location = "eastus",

    [Parameter(Mandatory = $true)]
    [string]$ParametersFile,

    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent | Split-Path -Parent
$mainBicep = Join-Path $root "infra/azure/main.bicep"

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