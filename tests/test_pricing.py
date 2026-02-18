from decimal import Decimal

import pytest

from pecan_crm.domain.pricing import PricingValidationError, SaleLine, calculate_totals


def test_calculate_totals_mixed_with_percent_discount() -> None:
    lines = [
        SaleLine(unit_type="EACH", unit_price=Decimal("10.00"), quantity=Decimal("1")),
        SaleLine(unit_type="WEIGHT", unit_price=Decimal("7.20"), weight_lbs=Decimal("1.250")),
    ]

    totals = calculate_totals(
        lines,
        tax_enabled=True,
        tax_rate_percent=Decimal("8.25"),
        discount_type="PERCENT",
        discount_value=Decimal("10"),
    )

    assert totals.subtotal == Decimal("19.00")
    assert totals.discount_total == Decimal("1.90")
    assert totals.tax_total == Decimal("1.41")
    assert totals.total == Decimal("18.51")


def test_fixed_discount_is_capped_at_subtotal() -> None:
    lines = [SaleLine(unit_type="EACH", unit_price=Decimal("12.00"), quantity=Decimal("1"))]

    totals = calculate_totals(
        lines,
        tax_enabled=True,
        tax_rate_percent=Decimal("8.25"),
        discount_type="FIXED",
        discount_value=Decimal("20.00"),
    )

    assert totals.discount_total == Decimal("12.00")
    assert totals.tax_total == Decimal("0.00")
    assert totals.total == Decimal("0.00")


def test_invalid_negative_unit_price_fails_validation() -> None:
    lines = [SaleLine(unit_type="EACH", unit_price=Decimal("-1.00"), quantity=Decimal("1"))]

    with pytest.raises(PricingValidationError):
        calculate_totals(lines, tax_enabled=False, tax_rate_percent=Decimal("0"))


def test_invalid_weight_line_with_quantity_fails_validation() -> None:
    lines = [
        SaleLine(
            unit_type="WEIGHT",
            unit_price=Decimal("5.00"),
            quantity=Decimal("1"),
            weight_lbs=Decimal("1.00"),
        )
    ]

    with pytest.raises(PricingValidationError):
        calculate_totals(lines, tax_enabled=False, tax_rate_percent=Decimal("0"))