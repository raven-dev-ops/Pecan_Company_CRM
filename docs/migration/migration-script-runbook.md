# Migration Script Runbook

Issue links: #34, #35

## Purpose
Provide repeatable, idempotent migration from Access CSV exports to Azure SQL and generate duplicate-candidate report for customer cleanup.

## Scripts
- `scripts/migrate_access_exports.py`
- `scripts/customer_dedupe_report.py`

## Idempotent strategy
- Customers matched by normalized email, then phone, then full name.
- Products matched by SKU (preferred) or normalized name.
- Sales matched by `receipt_number` (skip if already present).
- Sale items matched by `(sale_id, product_id, measure, line_total)` composite key.
- Re-running script inserts only missing rows and reports skipped rows.

## Migration command
```powershell
python scripts/migrate_access_exports.py \
  --connection-url "mssql+pyodbc://..." \
  --customers-csv data/customers.csv \
  --products-csv data/products.csv \
  --sales-csv data/sales.csv \
  --sale-items-csv data/sale_items.csv \
  --report-path reports/migration_report.json
```

## Dry-run command
```powershell
python scripts/migrate_access_exports.py \
  --connection-url "mssql+pyodbc://..." \
  --customers-csv data/customers.csv \
  --products-csv data/products.csv \
  --sales-csv data/sales.csv \
  --sale-items-csv data/sale_items.csv \
  --report-path reports/migration_report_dry_run.json \
  --dry-run
```

## Duplicate report command
```powershell
python scripts/customer_dedupe_report.py \
  --customers-csv data/customers.csv \
  --out-csv reports/customer_duplicates.csv
```

## Output artifacts
- Migration report JSON with inserted/updated/skipped/errors by entity.
- Customer duplicate CSV for manual review.