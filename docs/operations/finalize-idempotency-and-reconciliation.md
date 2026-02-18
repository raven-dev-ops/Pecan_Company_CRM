# Finalize Idempotency and Receipt Reconciliation

Issue link: #46

## Transaction boundary
1. Persist `sales` + `sale_items` in DB transaction.
2. Commit DB transaction.
3. Generate receipt PDF from persisted data.

If step 3 fails, sale data remains committed and can be reconciled.

## Idempotent finalize behavior
- Each finalize attempt carries `idempotency_key` (`sales.finalize_idempotency_key`, unique).
- Retry with same key returns existing persisted sale instead of creating duplicates.
- Ring-Up UI retains key after partial failure to allow safe retry.

## Correlation and troubleshooting
- Finalize logs include `correlation_id` (the idempotency key).
- Logs distinguish new finalize vs replay finalize.

## Reconciliation process
Use scripted detection/repair for missing receipt artifacts:

```powershell
python scripts/reconcile_receipts.py \
  --connection-url "mssql+pyodbc://..." \
  --receipt-folder "C:\ProgramData\PecanCRM\receipts" \
  --business-name "Pecan Company" \
  --business-address "123 Main St" \
  --business-phone "555-555-5555" \
  --report-path reports/receipt_reconcile.json
```

Detection-only mode:

```powershell
python scripts/reconcile_receipts.py ... --no-repair
```