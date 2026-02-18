# Discovery Decision: Azure Usage Model

Issue link: #3

## Decision
For MVP, use direct desktop connection to Azure SQL.

## Selected architecture
PySide6 desktop app -> SQLAlchemy/pyodbc -> Azure SQL Database

## Why this choice
- Fastest path to MVP with smallest moving parts.
- Lower operational overhead than standing up and maintaining an API layer immediately.
- Works with known constraints for a single-site desktop workflow.

## MVP security/networking plan
- Azure SQL firewall limited to known public IP(s) only.
- Dedicated least-privilege SQL login for app runtime.
- Credentials stored using Windows-protected secret storage approach.
- Parameterized queries only.

## Deferred hardening path
Introduce API layer when one or more conditions are true:
- multi-site rollout,
- tighter secret isolation requirements,
- external integrations requiring service boundaries.

Minimal future API endpoints:
- `POST /sales/finalize`
- `GET /sales/{receipt_number}`
- `GET /sales?from=&to=&payment_method=`
- `POST /receipts/regenerate`
- `GET /products`, `POST /products`, `PATCH /products/{id}`
- `GET /customers`, `POST /customers`, `PATCH /customers/{id}`