param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroup,

    [Parameter(Mandatory = $true)]
    [string]$StorageAccountName,

    [Parameter(Mandatory = $false)]
    [string]$ContainerName = "receipts"
)

$ErrorActionPreference = "Stop"

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