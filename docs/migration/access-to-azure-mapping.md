# Migration Mapping: Microsoft Access -> Azure SQL

Issue link: #33

## Scope
Define field mapping and transformation rules for migration from Access exports to canonical Azure SQL schema.

## Assumptions
- Final column names from Access will be confirmed via inventory in `docs/discovery/legacy-access-inventory.md`.
- This mapping will be finalized after table catalog extraction.

## Proposed table mapping

### Access `Customers` -> Azure `customers`
- `FirstName` -> `first_name`
- `LastName` -> `last_name`
- `Phone` -> `phone`
- `Email` -> `email`
- `Notes` -> `notes`

### Access `Products` -> Azure `products`
- `SKU` -> `sku`
- `ProductName` -> `name`
- `UnitType` -> `unit_type` (`EACH`/`WEIGHT` normalization)
- `Price` -> `unit_price`
- `Active` -> `is_active`

### Access `Sales` -> Azure `sales`
- `ReceiptNumber` -> `receipt_number`
- `CustomerID` -> `customer_id`
- `PaymentMethod` -> `payment_method`
- `Subtotal` -> `subtotal`
- `Discount` -> `discount_total`
- `Tax` -> `tax_total`
- `Total` -> `total`
- `SaleDate` -> `sold_at_utc` (timezone normalization required)

### Access `SaleItems` -> Azure `sale_items`
- `SaleID` -> `sale_id`
- `ProductID` -> `product_id`
- `ProductName` -> `product_name_snapshot`
- `UnitType` -> `unit_type`
- `Qty` -> `quantity`
- `Weight` -> `weight_lbs`
- `UnitPrice` -> `unit_price`
- `LineTotal` -> `line_subtotal`

## Transform rules
- Phone normalization: strip punctuation; retain leading `+` where present.
- Null handling: blank strings convert to `NULL` for optional fields.
- Unit type normalization: map aliases (`UNIT`, `EACH`, `LB`, `WEIGHT`) to canonical enum.
- Monetary normalization: decimal conversion with 2-digit rounding.
- Deduping: customer candidate duplicates flagged by normalized phone/email/full-name tuple.

## Idempotency strategy for migration
- Use natural/legacy key crosswalk tables during load.
- Upsert by crosswalk key to avoid duplicate inserts on reruns.
- Emit migration report with inserted/updated/skipped/error counts.