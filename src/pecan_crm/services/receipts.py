from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


@dataclass(frozen=True)
class ReceiptLine:
    name: str
    unit_type: str
    quantity: Decimal | None
    weight_lbs: Decimal | None
    unit_price: Decimal
    line_subtotal: Decimal


@dataclass(frozen=True)
class ReceiptData:
    receipt_number: str
    sold_at_local: datetime
    business_name: str
    business_address: str
    business_phone: str
    payment_method: str
    customer_summary: str
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    total: Decimal
    lines: list[ReceiptLine]


def generate_receipt_pdf(receipt_dir: Path, data: ReceiptData) -> Path:
    receipt_dir.mkdir(parents=True, exist_ok=True)
    output_path = receipt_dir / f"receipt_{data.receipt_number}.pdf"

    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    y = height - 50

    def write_line(text: str, step: int = 16) -> None:
        nonlocal y
        if y < 60:
            c.showPage()
            y = height - 50
        c.drawString(50, y, text)
        y -= step

    write_line(data.business_name)
    write_line(data.business_address)
    write_line(data.business_phone)
    write_line("-" * 70)
    write_line(f"Receipt: {data.receipt_number}")
    write_line(f"Date/Time: {data.sold_at_local.strftime('%Y-%m-%d %H:%M:%S')}")
    write_line(f"Payment: {data.payment_method}")
    if data.customer_summary:
        write_line(f"Customer: {data.customer_summary}")
    write_line("-" * 70)

    for line in data.lines:
        qty_weight = (
            f"qty={line.quantity}" if line.unit_type == "EACH" else f"wt={line.weight_lbs}"
        )
        write_line(
            f"{line.name} | {qty_weight} | ${line.unit_price:.2f} | ${line.line_subtotal:.2f}",
            step=14,
        )

    write_line("-" * 70)
    write_line(f"Subtotal: ${data.subtotal:.2f}")
    write_line(f"Discount: ${data.discount_total:.2f}")
    write_line(f"Tax: ${data.tax_total:.2f}")
    write_line(f"Total: ${data.total:.2f}")

    c.showPage()
    c.save()
    return output_path