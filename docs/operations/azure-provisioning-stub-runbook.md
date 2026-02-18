# Azure Provisioning Stub Runbook

Issue links: #7, #8, #9, #12

## Scope
This runbook provides stubbed-but-executable scripts/templates for Azure infrastructure setup when direct tenant access is not available during development.

## #7 Azure SQL Server + Database (stub)
Use Bicep template deployment:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/azure/deploy_infra_stub.ps1 `
  -SubscriptionId <sub-id> `
  -ResourceGroup rg-pecan-crm-prod `
  -Location eastus `
  -ParametersFile infra/azure/parameters.example.json `
  -WhatIf
```

Then run without `-WhatIf` to deploy.

Validation:
- Capture deployed server FQDN (`<server>.database.windows.net`).
- Test connection from app settings on a Windows client.

## #8 Firewall/IP allow list (stub)
```powershell
powershell -ExecutionPolicy Bypass -File scripts/azure/configure_firewall_stub.ps1 `
  -ResourceGroup rg-pecan-crm-prod `
  -SqlServerName sql-pecan-crm-prod `
  -AllowedPublicIps @('203.0.113.10','198.51.100.5')
```

Validation:
- Connection succeeds only from allowlisted IPs.
- No broad 0.0.0.0/0 rule used.

## #9 Least-privilege app login/user (stub)
```powershell
powershell -ExecutionPolicy Bypass -File scripts/azure/app_login_stub.ps1 `
  -SqlServerFqdn sql-pecan-crm-prod.database.windows.net `
  -SqlAdminUser pecan_admin `
  -SqlAdminPassword <secure-value> `
  -SqlScriptPath infra/azure/sql/create_app_login_user.sql
```

Validation:
- App login exists and can read/write app tables.
- `db_owner` is not granted.

## #12 Optional Blob receipts archiving (stub)
```powershell
powershell -ExecutionPolicy Bypass -File scripts/azure/deploy_blob_stub.ps1 `
  -ResourceGroup rg-pecan-crm-prod `
  -StorageAccountName stpecancrmprod `
  -ContainerName receipts
```

Upload strategy (for future code path):
- MVP stub recommends scoped SAS token or managed identity via API.
- On upload failures, keep local receipt and log retry queue item.