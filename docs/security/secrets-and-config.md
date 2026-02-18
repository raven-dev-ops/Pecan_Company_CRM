# Azure Secrets and Configuration Management

Issue link: #11

## Objectives
- Keep connection details out of source control.
- Store sensitive credentials securely on Windows.
- Define repeatable setup for new machine installs.

## Storage model
- Non-secret settings stored in JSON:
  - `%LOCALAPPDATA%\PecanCRM\settings.json`
- Secret stored in Windows-backed keyring:
  - service: `PecanCRM`
  - key: `azure_sql_password`

## What is never stored in plaintext repo files
- Azure SQL password
- Production connection strings

## New PC setup steps
1. Install app and ODBC Driver 18 for SQL Server.
2. Open app -> `Settings`.
3. Enter server, database, username, and password.
4. Save settings (password is written via secure keyring API, not plaintext settings file).
5. Click `Test Connection` and confirm success.

## Rotation/revocation impact
When SQL password rotates, update only password in Settings and re-test connection.