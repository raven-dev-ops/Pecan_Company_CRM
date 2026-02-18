# Canonical Schema Design

Issue link: #13

Companion SQL: `docs/schema/canonical_schema.sql`

## Entities
- `customers`
- `products`
- `sales`
- `sale_items`
- `app_settings`

## Key design points
- All primary entities have audit timestamps (`created_at_utc`, `updated_at_utc`).
- `sales.receipt_number` is unique and required at finalize time.
- Product supports `EACH` and `WEIGHT` units.
- `sales` stores persisted totals (`subtotal`, `discount_total`, `tax_total`, `total`).
- Soft deletion/archive is supported through status flags.

## Integrity
- Foreign keys from `sale_items` to `sales` and `products`.
- Check constraints for non-negative money values and valid quantity/weight usage.
- Unique index on `receipt_number`.