# Quick Start Guide for Joshua

Issue link: #43

## 1. Install
1. Run the provided installer.
2. Confirm desktop/start menu shortcut exists.
3. Ensure ODBC Driver 18 for SQL Server is installed.

## 2. First-run settings
1. Open app and go to Settings.
2. Enter Azure SQL server/database/username/password.
3. Enter business name/address/phone.
4. Enable tax and set tax rate if required.
5. Choose receipt save folder.
6. Click Test Connection.
7. Click Save Settings.

## 3. Products setup
1. Open Products screen.
2. Add products with unit type (EACH or WEIGHT) and price.
3. Save and confirm product appears in list.

## 4. Daily checkout flow
1. Open Ring-Up.
2. Add products to cart.
3. Optionally attach customer.
4. Choose payment method and finalize.
5. Confirm receipt PDF is created.

## 5. Where receipts are saved
- Default: `%ProgramData%\PecanCRM\receipts\`
- Actual path can be changed in Settings.

## 6. Basic troubleshooting
- Connection fails: verify internet, firewall, server/db credentials.
- Receipt missing: check receipt folder path and permissions.
- App errors: check log file under `%LocalAppData%\PecanCRM\logs\`.