from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session, sessionmaker

from pecan_crm.db.models import Customer, Product, Sale, SaleItem
from pecan_crm.domain.pricing import SaleLine, calculate_totals, line_subtotal
from pecan_crm.domain.receipt_numbers import format_receipt_number
from pecan_crm.services.receipts import ReceiptData, ReceiptLine, generate_receipt_pdf


@dataclass(frozen=True)
class CartLineInput:
    product_id: int
    quantity: Decimal | None
    weight_lbs: Decimal | None


@dataclass(frozen=True)
class FinalizeSaleInput:
    cart_lines: list[CartLineInput]
    payment_method: str
    customer_id: int | None
    discount_type: str
    discount_value: Decimal
    tax_enabled: bool
    tax_rate_percent: Decimal
    receipt_folder: Path
    business_name: str
    business_address: str
    business_phone: str


@dataclass(frozen=True)
class FinalizeSaleResult:
    sale_id: int
    receipt_number: str
    receipt_path: Path


class SalesRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def list_active_products(self, *, search: str = "") -> list[Product]:
        with self.session_factory() as session:
            query = select(Product).where(Product.is_active.is_(True))
            if search:
                wildcard = f"%{search.strip()}%"
                query = query.where(Product.name.ilike(wildcard) | Product.sku.ilike(wildcard))
            query = query.order_by(Product.name.asc())
            return list(session.scalars(query).all())

    def search_customers(self, search: str) -> list[Customer]:
        with self.session_factory() as session:
            query = select(Customer).where(Customer.is_active.is_(True))
            if search.strip():
                wildcard = f"%{search.strip()}%"
                query = query.where(
                    or_(
                        Customer.first_name.ilike(wildcard),
                        Customer.last_name.ilike(wildcard),
                        Customer.phone.ilike(wildcard),
                        Customer.email.ilike(wildcard),
                    )
                )
            query = query.order_by(Customer.last_name.asc(), Customer.first_name.asc())
            return list(session.scalars(query).all())

    def finalize_sale(self, payload: FinalizeSaleInput) -> FinalizeSaleResult:
        payment_method = payload.payment_method.upper().strip()
        if payment_method not in {"CASH", "CARD", "OTHER"}:
            raise ValueError("Payment method must be CASH, CARD, or OTHER")
        if not payload.cart_lines:
            raise ValueError("Cart is empty")

        with self.session_factory() as session:
            product_ids = [line.product_id for line in payload.cart_lines]
            products = list(session.scalars(select(Product).where(Product.product_id.in_(product_ids))).all())
            product_map = {p.product_id: p for p in products}

            if len(product_map) != len(set(product_ids)):
                raise ValueError("One or more selected products no longer exist")

            pricing_lines: list[SaleLine] = []
            receipt_lines: list[ReceiptLine] = []

            for cart_line in payload.cart_lines:
                product = product_map[cart_line.product_id]
                sale_line = SaleLine(
                    unit_type=product.unit_type,
                    unit_price=Decimal(str(product.unit_price)),
                    quantity=cart_line.quantity,
                    weight_lbs=cart_line.weight_lbs,
                )
                pricing_lines.append(sale_line)
                receipt_lines.append(
                    ReceiptLine(
                        name=product.name,
                        unit_type=product.unit_type,
                        quantity=cart_line.quantity,
                        weight_lbs=cart_line.weight_lbs,
                        unit_price=Decimal(str(product.unit_price)),
                        line_subtotal=line_subtotal(sale_line),
                    )
                )

            totals = calculate_totals(
                pricing_lines,
                tax_enabled=payload.tax_enabled,
                tax_rate_percent=payload.tax_rate_percent,
                discount_type=payload.discount_type,
                discount_value=payload.discount_value,
            )

            next_seq = session.execute(text("SELECT NEXT VALUE FOR receipt_number_seq")).scalar_one()
            receipt_number = format_receipt_number(int(next_seq))

            sale = Sale(
                receipt_number=receipt_number,
                customer_id=payload.customer_id,
                payment_method=payment_method,
                status="FINALIZED",
                subtotal=totals.subtotal,
                discount_total=totals.discount_total,
                tax_total=totals.tax_total,
                total=totals.total,
                sold_at_utc=datetime.utcnow(),
            )
            session.add(sale)
            session.flush()

            for cart_line, sale_line in zip(payload.cart_lines, pricing_lines, strict=False):
                product = product_map[cart_line.product_id]
                session.add(
                    SaleItem(
                        sale_id=sale.sale_id,
                        product_id=product.product_id,
                        product_name_snapshot=product.name,
                        unit_type=product.unit_type,
                        quantity=cart_line.quantity,
                        weight_lbs=cart_line.weight_lbs,
                        unit_price=Decimal(str(product.unit_price)),
                        line_subtotal=line_subtotal(sale_line),
                    )
                )

            session.commit()

            customer_summary = ""
            if payload.customer_id:
                customer = session.get(Customer, payload.customer_id)
                if customer:
                    customer_summary = " ".join(
                        part for part in [customer.first_name or "", customer.last_name or ""] if part
                    ).strip()
                    if customer.phone:
                        customer_summary = f"{customer_summary} ({customer.phone})" if customer_summary else customer.phone

            receipt_data = ReceiptData(
                receipt_number=receipt_number,
                sold_at_local=datetime.now(),
                business_name=payload.business_name,
                business_address=payload.business_address,
                business_phone=payload.business_phone,
                payment_method=payment_method,
                customer_summary=customer_summary,
                subtotal=totals.subtotal,
                discount_total=totals.discount_total,
                tax_total=totals.tax_total,
                total=totals.total,
                lines=receipt_lines,
            )
            receipt_path = generate_receipt_pdf(payload.receipt_folder, receipt_data)

            return FinalizeSaleResult(
                sale_id=sale.sale_id,
                receipt_number=receipt_number,
                receipt_path=receipt_path,
            )