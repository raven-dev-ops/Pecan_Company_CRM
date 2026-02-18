from __future__ import annotations

import re


_RECEIPT_PATTERN = re.compile(r"^\d{6}$")


class ReceiptNumberError(ValueError):
    pass


def format_receipt_number(sequence_value: int) -> str:
    if sequence_value <= 0:
        raise ReceiptNumberError("Sequence value must be positive")
    return f"{sequence_value:06d}"


def parse_receipt_number(receipt_number: str) -> int:
    if not _RECEIPT_PATTERN.match(receipt_number):
        raise ReceiptNumberError("Receipt number must be a 6-digit string")
    return int(receipt_number)