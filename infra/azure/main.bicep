@description('Azure region for deployment.')
param location string

@description('Resource group name; should be supplied by deployment scope.')
param resourceGroupName string

@description('Azure SQL logical server name (globally unique).')
param sqlServerName string

@description('Azure SQL admin username.')
param sqlAdminLogin string

@secure()
@description('Azure SQL admin password.')
param sqlAdminPassword string

@description('Azure SQL database name.')
param databaseName string

@description('Database SKU (example: Basic, S0, GP_S_Gen5_1).')
param databaseSku string = 'S0'

@description('Create optional Blob resources for receipt archiving.')
param createBlobResources bool = false

@description('Storage account name for optional blob receipts (must be globally unique, 3-24 lowercase alphanumerics).')
param storageAccountName string = ''

@description('Container name for optional blob receipts.')
param receiptsContainerName string = 'receipts'

resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: sqlAdminLogin
    administratorLoginPassword: sqlAdminPassword
    publicNetworkAccess: 'Enabled'
    minimalTlsVersion: '1.2'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sqlServer
  name: databaseName
  location: location
  sku: {
    name: databaseSku
    tier: databaseSku == 'Basic' ? 'Basic' : 'Standard'
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
  }
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = if (createBlobResources) {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = if (createBlobResources) {
  parent: storageAccount
  name: 'default'
}

resource receiptsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = if (createBlobResources) {
  parent: blobService
  name: receiptsContainerName
  properties: {
    publicAccess: 'None'
  }
}

output sqlServerFqdn string = '${sqlServer.name}.database.windows.net'
output sqlDatabaseName string = sqlDatabase.name
output blobContainerResourceId string = createBlobResources ? receiptsContainer.id : ''