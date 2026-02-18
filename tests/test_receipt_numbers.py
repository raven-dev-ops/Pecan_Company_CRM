import pytest

from pecan_crm.domain.receipt_numbers import (
    ReceiptNumberError,
    format_receipt_number,
    parse_receipt_number,
)


def test_format_receipt_number_zero_padded() -> None:
    assert format_receipt_number(1) == "000001"
    assert format_receipt_number(123456) == "123456"


def test_format_receipt_number_rejects_non_positive() -> None:
    with pytest.raises(ReceiptNumberError):
        format_receipt_number(0)


def test_parse_receipt_number_rejects_invalid_format() -> None:
    with pytest.raises(ReceiptNumberError):
        parse_receipt_number("ABC123")


def test_parse_receipt_number_returns_integer() -> None:
    assert parse_receipt_number("000321") == 321