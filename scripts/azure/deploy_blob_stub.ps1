param(
    [string]$ResourceGroup = "",

    [string]$StorageAccountName = "",

    [Parameter(Mandatory = $false)]
    [string]$ContainerName = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent | Split-Path -Parent
$envLoader = Join-Path $root "scripts/azure/load_env.ps1"
if (Test-Path $envLoader) { & $envLoader | Out-Null }

if (-not $ResourceGroup) { $ResourceGroup = $env:AZURE_RESOURCE_GROUP }
if (-not $StorageAccountName) { $StorageAccountName = $env:AZURE_STORAGE_ACCOUNT }
if (-not $ContainerName) { $ContainerName = $env:AZURE_STORAGE_CONTAINER; if (-not $ContainerName) { $ContainerName = "receipts" } }

if (-not $ResourceGroup) { throw "ResourceGroup is required (arg or AZURE_RESOURCE_GROUP)." }
if (-not $StorageAccountName) { throw "StorageAccountName is required (arg or AZURE_STORAGE_ACCOUNT)." }

az storage account create `
  --resource-group $ResourceGroup `
  --name $StorageAccountName `
  --sku Standard_LRS `
  --kind StorageV2 `
  --min-tls-version TLS1_2 `
  --allow-blob-public-access false `
  --https-only true | Out-Null

$accountKey = az storage account keys list `
  --resource-group $ResourceGroup `
  --account-name $StorageAccountName `
  --query "[0].value" -o tsv

az storage container create `
  --name $ContainerName `
  --account-name $StorageAccountName `
  --account-key $accountKey `
  --public-access off | Out-Null

Write-Host "Blob storage stub resources ensured: $StorageAccountName / $ContainerName"
