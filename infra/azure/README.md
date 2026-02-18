# Azure Infrastructure Stubs

Covers issue stubs:
- #7 Azure SQL server + database provisioning
- #8 Azure SQL firewall allow list
- #9 least-privilege app login/user
- #12 optional Blob storage for receipts

These are deployment-ready stubs. They do not create cloud resources until run with real credentials and subscription context.

## Files
- `infra/azure/main.bicep`: SQL + optional Blob resources
- `infra/azure/parameters.example.json`: example parameter file
- `infra/azure/sql/create_app_login_user.sql`: least-privilege SQL login/user script
- `scripts/azure/deploy_infra_stub.ps1`: deploy Bicep template
- `scripts/azure/configure_firewall_stub.ps1`: configure IP allow list
- `scripts/azure/app_login_stub.ps1`: execute least-privilege SQL script
- `scripts/azure/deploy_blob_stub.ps1`: standalone blob setup path

## Stub usage
1. Copy parameter file and replace placeholders.
2. Run infra deployment script with your subscription/resource group.
3. Run firewall script with current office/public IPs.
4. Run app-login script to provision least-privilege runtime user.

## Validation targets
- Server FQDN reachable by Test Connection in app settings.
- Firewall rules restricted to required public IPs only.
- App login can read/write app tables and has no elevated admin permissions.