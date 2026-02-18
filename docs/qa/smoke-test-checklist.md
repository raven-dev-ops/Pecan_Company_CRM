# QA Smoke Test Checklist (Target Workflow)

Issue link: #41

## Environment
- [ ] Clean Windows 10/11 machine
- [ ] App installed
- [ ] ODBC driver installed
- [ ] Azure SQL reachable

## Workflow smoke tests
### Fresh install and startup
- [ ] App launches without crash
- [ ] Version is visible in app
- [ ] Log file is created

### Setup and master data
- [ ] Configure DB settings and pass Test Connection
- [ ] Add at least one product
- [ ] Add at least one customer

### Checkout path
- [ ] Add product to cart
- [ ] Finalize sale with payment method
- [ ] Sale persists to DB
- [ ] PDF receipt generated

### History and reprint
- [ ] Sale appears in Sales History
- [ ] Prior receipt can be opened/reprinted/regenerated

## Defect triage
- [ ] Each failure logged as issue with reproduction steps
- [ ] Severity assigned
- [ ] Owner and target fix milestone assigned