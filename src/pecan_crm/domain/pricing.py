from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass


TWOPLACES = Decimal("0.01")


def as_decimal(value: Decimal | int | float | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def round_money(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class SaleLine:
    unit_type: str
    unit_price: Decimal
    quantity: Decimal | None = None
    weight_lbs: Decimal | None = None


@dataclass(frozen=True)
class SaleTotals:
    subtotal: Decimal
    discount_total: Decimal
    taxable_subtotal: Decimal
    tax_total: Decimal
    total: Decimal


class PricingValidationError(ValueError):
    pass


def validate_line(line: SaleLine) -> None:
    unit_type = line.unit_type.upper()
    if unit_type not in {"EACH", "WEIGHT"}:
        raise PricingValidationError("Invalid unit type")

    if line.unit_price < 0:
        raise PricingValidationError("Unit price cannot be negative")

    if unit_type == "EACH":
        if line.quantity is None or line.weight_lbs is not None:
            raise PricingValidationError("EACH items require quantity and no weight")
        if line.quantity <= 0:
            raise PricingValidationError("Quantity must be positive")

    if unit_type == "WEIGHT":
        if line.weight_lbs is None or line.quantity is not None:
            raise PricingValidationError("WEIGHT items require weight and no quantity")
        if line.weight_lbs <= 0:
            raise PricingValidationError("Weight must be positive")


def line_subtotal(line: SaleLine) -> Decimal:
    validate_line(line)
    measure = line.quantity if line.unit_type.upper() == "EACH" else line.weight_lbs
    assert measure is not None
    return round_money(line.unit_price * measure)


def calculate_totals(
    lines: list[SaleLine],
    *,
    tax_enabled: bool,
    tax_rate_percent: Decimal,
    discount_type: str = "NONE",
    discount_value: Decimal = Decimal("0"),
) -> SaleTotals:
    subtotal = round_money(sum((line_subtotal(line) for line in lines), start=Decimal("0")))

    discount_type = discount_type.upper()
    discount_value = as_decimal(discount_value)
    tax_rate_percent = as_decimal(tax_rate_percent)

    if discount_type == "NONE":
        discount_total = Decimal("0")
    elif discount_type == "PERCENT":
        if discount_value < 0:
            raise PricingValidationError("Discount percent cannot be negative")
        discount_total = round_money(subtotal * (discount_value / Decimal("100")))
    elif discount_type == "FIXED":
        if discount_value < 0:
            raise PricingValidationError("Fixed discount cannot be negative")
        discount_total = round_money(discount_value)
    else:
        raise PricingValidationError("Invalid discount type")

    if discount_total > subtotal:
        discount_total = subtotal

    taxable_subtotal = round_money(subtotal - discount_total)

    if tax_enabled:
        tax_total = round_money(taxable_subtotal * (tax_rate_percent / Decimal("100")))
    else:
        tax_total = Decimal("0.00")

    total = round_money(taxable_subtotal + tax_total)

    return SaleTotals(
        subtotal=subtotal,
        discount_total=discount_total,
        taxable_subtotal=taxable_subtotal,
        tax_total=tax_total,
        total=total,
    )