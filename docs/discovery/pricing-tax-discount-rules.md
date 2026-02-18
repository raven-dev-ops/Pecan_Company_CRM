# Discovery Spec: Pricing, Tax, Discount, and Rounding Rules

Issue links: #5, #47

## Product pricing model
- Support both `EACH` (unit quantity) and `WEIGHT` (price per pound).
- Quantity and weight are mutually exclusive per line item.

## Tax policy
- Tax can be enabled/disabled in settings.
- When enabled, tax rate is configurable per business settings.
- Tax is computed on taxable subtotal after sale-level discount allocation.

## Discount policy
- MVP default: no discount required.
- Supported when enabled: sale-level `PERCENT` or `FIXED`.
- Discount cannot exceed pre-tax subtotal.

## Precision and rounding
- Monetary storage precision: `DECIMAL(12,2)` for persisted currency fields.
- Computation precision: decimal math (no float).
- Rounding mode: `ROUND_HALF_UP` to 2 decimals for money values.
- Weight precision: `DECIMAL(10,3)`.
- Line subtotal for weight items is rounded to 2 decimals before sale totals.

## Canonical calculation order
1. `line_subtotal = unit_price * qty_or_weight`
2. `subtotal = sum(line_subtotal)`
3. `discount_total = percent_or_fixed(subtotal)`
4. `taxable_subtotal = max(subtotal - discount_total, 0)`
5. `tax_total = taxable_subtotal * tax_rate`
6. `total = taxable_subtotal + tax_total`

## Executable example set
Example A: unit-only, tax on, no discount
- Items: 2 x $5.00, 1 x $3.50
- Subtotal: $13.50
- Discount: $0.00
- Tax 8.25%: $1.11
- Total: $14.61

Example B: mixed unit + weight, percent discount
- Items: 1 x $10.00, 1.250 lb x $7.20 = $9.00
- Subtotal: $19.00
- Discount 10%: $1.90
- Taxable subtotal: $17.10
- Tax 8.25%: $1.41
- Total: $18.51

Example C: fixed discount capped at subtotal
- Subtotal: $12.00
- Fixed discount request: $20.00
- Applied discount: $12.00
- Taxable subtotal: $0.00
- Tax: $0.00
- Total: $0.00

Example D: weight precision
- Item: 0.333 lb x $12.00 = $3.996 -> $4.00 (line rounded)