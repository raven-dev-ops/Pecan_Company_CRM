from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, or_, select, text
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


@dataclass(frozen=True)
class SaleListItem:
    sale_id: int
    receipt_number: str
    sold_at_utc: datetime
    payment_method: str
    status: str
    total: Decimal
    customer_name: str


@dataclass(frozen=True)
class DailySummary:
    gross: Decimal
    tax_total: Decimal
    discounts: Decimal
    net: Decimal
    transaction_count: int


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

            customer_summary = self._customer_summary(session, payload.customer_id)
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

    def list_sales(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
        payment_method: str | None,
        receipt_number_contains: str,
    ) -> list[SaleListItem]:
        with self.session_factory() as session:
            query = select(Sale, Customer).outerjoin(Customer, Sale.customer_id == Customer.customer_id)

            if date_from is not None:
                start_dt = datetime.combine(date_from, time.min)
                query = query.where(Sale.sold_at_utc >= start_dt)

            if date_to is not None:
                end_dt = datetime.combine(date_to, time.max)
                query = query.where(Sale.sold_at_utc <= end_dt)

            if payment_method and payment_method != "ANY":
                query = query.where(Sale.payment_method == payment_method)

            if receipt_number_contains.strip():
                wildcard = f"%{receipt_number_contains.strip()}%"
                query = query.where(Sale.receipt_number.ilike(wildcard))

            rows = session.execute(query.order_by(Sale.sold_at_utc.desc())).all()
            items: list[SaleListItem] = []
            for sale, customer in rows:
                customer_name = ""
                if customer:
                    customer_name = " ".join(
                        part for part in [customer.first_name or "", customer.last_name or ""] if part
                    ).strip()
                items.append(
                    SaleListItem(
                        sale_id=sale.sale_id,
                        receipt_number=sale.receipt_number,
                        sold_at_utc=sale.sold_at_utc,
                        payment_method=sale.payment_method,
                        status=sale.status,
                        total=Decimal(str(sale.total)),
                        customer_name=customer_name,
                    )
                )
            return items

    def get_sale_detail(self, sale_id: int) -> tuple[Sale, list[SaleItem], Customer | None]:
        with self.session_factory() as session:
            sale = session.get(Sale, sale_id)
            if sale is None:
                raise ValueError("Sale not found")

            items = list(
                session.scalars(select(SaleItem).where(SaleItem.sale_id == sale_id).order_by(SaleItem.sale_item_id))
            )
            customer = session.get(Customer, sale.customer_id) if sale.customer_id else None
            return sale, items, customer

    def regenerate_receipt(
        self,
        *,
        sale_id: int,
        receipt_folder: Path,
        business_name: str,
        business_address: str,
        business_phone: str,
    ) -> Path:
        with self.session_factory() as session:
            sale = session.get(Sale, sale_id)
            if sale is None:
                raise ValueError("Sale not found")

            items = list(
                session.scalars(select(SaleItem).where(SaleItem.sale_id == sale_id).order_by(SaleItem.sale_item_id))
            )
            customer_summary = self._customer_summary(session, sale.customer_id)

            receipt_lines = [
                ReceiptLine(
                    name=item.product_name_snapshot,
                    unit_type=item.unit_type,
                    quantity=Decimal(str(item.quantity)) if item.quantity is not None else None,
                    weight_lbs=Decimal(str(item.weight_lbs)) if item.weight_lbs is not None else None,
                    unit_price=Decimal(str(item.unit_price)),
                    line_subtotal=Decimal(str(item.line_subtotal)),
                )
                for item in items
            ]

            receipt_data = ReceiptData(
                receipt_number=sale.receipt_number,
                sold_at_local=sale.sold_at_utc,
                business_name=business_name,
                business_address=business_address,
                business_phone=business_phone,
                payment_method=sale.payment_method,
                customer_summary=customer_summary,
                subtotal=Decimal(str(sale.subtotal)),
                discount_total=Decimal(str(sale.discount_total)),
                tax_total=Decimal(str(sale.tax_total)),
                total=Decimal(str(sale.total)),
                lines=receipt_lines,
            )
            return generate_receipt_pdf(receipt_folder, receipt_data)

    def void_sale(self, *, sale_id: int, reason: str) -> None:
        reason = reason.strip()
        if not reason:
            raise ValueError("Void reason is required")

        with self.session_factory() as session:
            sale = session.get(Sale, sale_id)
            if sale is None:
                raise ValueError("Sale not found")

            sale.status = "VOIDED"
            sale.void_reason = reason
            sale.updated_at_utc = datetime.utcnow()
            session.commit()

    def daily_summary(self, *, for_date: date) -> DailySummary:
        start_dt = datetime.combine(for_date, time.min)
        end_dt = datetime.combine(for_date, time.max)

        with self.session_factory() as session:
            row = session.execute(
                select(
                    func.coalesce(func.sum(Sale.subtotal), 0),
                    func.coalesce(func.sum(Sale.tax_total), 0),
                    func.coalesce(func.sum(Sale.discount_total), 0),
                    func.coalesce(func.sum(Sale.total), 0),
                    func.count(Sale.sale_id),
                ).where(
                    Sale.sold_at_utc >= start_dt,
                    Sale.sold_at_utc <= end_dt,
                    Sale.status != "VOIDED",
                )
            ).one()

            return DailySummary(
                gross=Decimal(str(row[0])),
                tax_total=Decimal(str(row[1])),
                discounts=Decimal(str(row[2])),
                net=Decimal(str(row[3])),
                transaction_count=int(row[4]),
            )

    def export_csv(self, output_dir: Path) -> dict[str, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)

        customers_path = output_dir / "customers.csv"
        sales_path = output_dir / "sales.csv"
        sale_items_path = output_dir / "sale_items.csv"

        with self.session_factory() as session:
            customers = list(session.scalars(select(Customer).order_by(Customer.customer_id)).all())
            sales = list(session.scalars(select(Sale).order_by(Sale.sale_id)).all())
            items = list(session.scalars(select(SaleItem).order_by(SaleItem.sale_item_id)).all())

        with customers_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["customer_id", "first_name", "last_name", "phone", "email", "is_active"])
            for c in customers:
                writer.writerow([c.customer_id, c.first_name, c.last_name, c.phone, c.email, c.is_active])

        with sales_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "sale_id",
                    "receipt_number",
                    "customer_id",
                    "payment_method",
                    "status",
                    "subtotal",
                    "discount_total",
                    "tax_total",
                    "total",
                    "sold_at_utc",
                ]
            )
            for s in sales:
                writer.writerow(
                    [
                        s.sale_id,
                        s.receipt_number,
                        s.customer_id,
                        s.payment_method,
                        s.status,
                        s.subtotal,
                        s.discount_total,
                        s.tax_total,
                        s.total,
                        s.sold_at_utc,
                    ]
                )

        with sale_items_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "sale_item_id",
                    "sale_id",
                    "product_id",
                    "product_name_snapshot",
                    "unit_type",
                    "quantity",
                    "weight_lbs",
                    "unit_price",
                    "line_subtotal",
                ]
            )
            for item in items:
                writer.writerow(
                    [
                        item.sale_item_id,
                        item.sale_id,
                        item.product_id,
                        item.product_name_snapshot,
                        item.unit_type,
                        item.quantity,
                        item.weight_lbs,
                        item.unit_price,
                        item.line_subtotal,
                    ]
                )

        return {
            "customers": customers_path,
            "sales": sales_path,
            "sale_items": sale_items_path,
        }

    @staticmethod
    def _customer_summary(session: Session, customer_id: int | None) -> str:
        if not customer_id:
            return ""
        customer = session.get(Customer, customer_id)
        if customer is None:
            return ""

        customer_summary = " ".join(
            part for part in [customer.first_name or "", customer.last_name or ""] if part
        ).strip()
        if customer.phone:
            customer_summary = f"{customer_summary} ({customer.phone})" if customer_summary else customer.phone
        return customer_summary