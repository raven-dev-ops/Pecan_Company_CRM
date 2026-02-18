from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pecan_crm.db.models import Customer, Product, Sale, SaleItem


@dataclass
class EntityReport:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0


@dataclass
class MigrationReport:
    customers: EntityReport
    products: EntityReport
    sales: EntityReport
    sale_items: EntityReport

    def to_dict(self) -> dict[str, dict[str, int]]:
        return {
            "customers": self.customers.__dict__,
            "products": self.products.__dict__,
            "sales": self.sales.__dict__,
            "sale_items": self.sale_items.__dict__,
        }


def normalize_phone(value: str) -> str:
    return "".join(ch for ch in (value or "") if ch.isdigit())


def normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def parse_decimal(value: str) -> Decimal:
    try:
        return Decimal((value or "0").strip() or "0")
    except Exception:
        return Decimal("0")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def pick(row: dict[str, str], *candidates: str) -> str:
    for key in candidates:
        if key in row and str(row[key]).strip():
            return str(row[key]).strip()
    return ""


def migrate(
    *,
    session_factory: sessionmaker[Session],
    customers_rows: list[dict[str, str]],
    products_rows: list[dict[str, str]],
    sales_rows: list[dict[str, str]],
    sale_items_rows: list[dict[str, str]],
    dry_run: bool,
) -> MigrationReport:
    report = MigrationReport(
        customers=EntityReport(),
        products=EntityReport(),
        sales=EntityReport(),
        sale_items=EntityReport(),
    )

    customer_map: dict[str, int] = {}
    product_map: dict[str, int] = {}
    sale_map: dict[str, int] = {}

    with session_factory() as session:
        existing_customers = list(session.scalars(select(Customer)).all())
        by_email = {normalize_text(c.email or ""): c for c in existing_customers if c.email}
        by_phone = {normalize_phone(c.phone or ""): c for c in existing_customers if c.phone}
        by_name = {
            f"{normalize_text(c.first_name or '')}|{normalize_text(c.last_name or '')}": c
            for c in existing_customers
        }

        for row in customers_rows:
            legacy_id = pick(row, "CustomerID", "customer_id", "ID", "Id")
            email = pick(row, "Email", "email")
            phone = pick(row, "Phone", "phone")
            first = pick(row, "FirstName", "first_name")
            last = pick(row, "LastName", "last_name")
            notes = pick(row, "Notes", "notes")

            match = None
            if email and normalize_text(email) in by_email:
                match = by_email[normalize_text(email)]
            elif phone and normalize_phone(phone) in by_phone:
                match = by_phone[normalize_phone(phone)]
            else:
                name_key = f"{normalize_text(first)}|{normalize_text(last)}"
                if name_key in by_name and name_key != "|":
                    match = by_name[name_key]

            try:
                if match is None:
                    entity = Customer(
                        first_name=first or None,
                        last_name=last or None,
                        phone=phone or None,
                        email=email or None,
                        notes=notes or None,
                        is_active=True,
                    )
                    session.add(entity)
                    session.flush()
                    report.customers.inserted += 1
                    match = entity
                else:
                    changed = False
                    if notes and (match.notes or "") != notes:
                        match.notes = notes
                        changed = True
                    if changed:
                        report.customers.updated += 1
                    else:
                        report.customers.skipped += 1

                if legacy_id:
                    customer_map[legacy_id] = match.customer_id

                if match.email:
                    by_email[normalize_text(match.email)] = match
                if match.phone:
                    by_phone[normalize_phone(match.phone)] = match
                by_name[f"{normalize_text(match.first_name or '')}|{normalize_text(match.last_name or '')}"] = match
            except Exception:
                report.customers.errors += 1

        existing_products = list(session.scalars(select(Product)).all())
        by_sku = {normalize_text(p.sku or ""): p for p in existing_products if p.sku}
        by_product_name = {normalize_text(p.name): p for p in existing_products}

        for row in products_rows:
            legacy_id = pick(row, "ProductID", "product_id", "ID", "Id")
            sku = pick(row, "SKU", "sku")
            name = pick(row, "ProductName", "name")
            unit_type = (pick(row, "UnitType", "unit_type") or "EACH").upper()
            price = parse_decimal(pick(row, "Price", "unit_price"))

            key_sku = normalize_text(sku)
            key_name = normalize_text(name)
            match = by_sku.get(key_sku) if key_sku else by_product_name.get(key_name)

            try:
                if match is None:
                    match = Product(
                        sku=sku or None,
                        name=name,
                        unit_type=unit_type,
                        unit_price=price,
                        is_active=True,
                    )
                    session.add(match)
                    session.flush()
                    report.products.inserted += 1
                else:
                    changed = False
                    if match.unit_price != price:
                        match.unit_price = price
                        changed = True
                    if match.unit_type != unit_type:
                        match.unit_type = unit_type
                        changed = True
                    if changed:
                        report.products.updated += 1
                    else:
                        report.products.skipped += 1

                if legacy_id:
                    product_map[legacy_id] = match.product_id

                if match.sku:
                    by_sku[normalize_text(match.sku)] = match
                by_product_name[normalize_text(match.name)] = match
            except Exception:
                report.products.errors += 1

        existing_sales = list(session.scalars(select(Sale)).all())
        by_receipt = {s.receipt_number: s for s in existing_sales}

        for row in sales_rows:
            legacy_id = pick(row, "SaleID", "sale_id", "ID", "Id")
            receipt = pick(row, "ReceiptNumber", "receipt_number")
            customer_legacy = pick(row, "CustomerID", "customer_id")
            customer_id = customer_map.get(customer_legacy) if customer_legacy else None
            payment_method = (pick(row, "PaymentMethod", "payment_method") or "OTHER").upper()
            subtotal = parse_decimal(pick(row, "Subtotal", "subtotal"))
            discount = parse_decimal(pick(row, "Discount", "discount_total"))
            tax = parse_decimal(pick(row, "Tax", "tax_total"))
            total = parse_decimal(pick(row, "Total", "total"))
            sold_at_raw = pick(row, "SaleDate", "sold_at_utc")

            sold_at = datetime.utcnow()
            if sold_at_raw:
                try:
                    sold_at = datetime.fromisoformat(sold_at_raw)
                except Exception:
                    sold_at = datetime.utcnow()

            try:
                if not receipt:
                    report.sales.errors += 1
                    continue

                if receipt in by_receipt:
                    existing = by_receipt[receipt]
                    sale_map[legacy_id or receipt] = existing.sale_id
                    report.sales.skipped += 1
                    continue

                entity = Sale(
                    receipt_number=receipt,
                    customer_id=customer_id,
                    payment_method=payment_method,
                    status="FINALIZED",
                    subtotal=subtotal,
                    discount_total=discount,
                    tax_total=tax,
                    total=total,
                    sold_at_utc=sold_at,
                )
                session.add(entity)
                session.flush()
                by_receipt[receipt] = entity
                sale_map[legacy_id or receipt] = entity.sale_id
                report.sales.inserted += 1
            except Exception:
                report.sales.errors += 1

        existing_items = list(session.scalars(select(SaleItem)).all())
        existing_keys = {
            (
                i.sale_id,
                i.product_id,
                str(i.quantity or ""),
                str(i.weight_lbs or ""),
                str(i.line_subtotal),
            )
            for i in existing_items
        }

        for row in sale_items_rows:
            sale_legacy = pick(row, "SaleID", "sale_id")
            product_legacy = pick(row, "ProductID", "product_id")
            sale_id = sale_map.get(sale_legacy)
            product_id = product_map.get(product_legacy)

            if not sale_id or not product_id:
                report.sale_items.errors += 1
                continue

            unit_type = (pick(row, "UnitType", "unit_type") or "EACH").upper()
            quantity = parse_decimal(pick(row, "Qty", "quantity"))
            weight = parse_decimal(pick(row, "Weight", "weight_lbs"))
            unit_price = parse_decimal(pick(row, "UnitPrice", "unit_price"))
            line_total = parse_decimal(pick(row, "LineTotal", "line_subtotal"))
            product_name = pick(row, "ProductName", "product_name_snapshot")

            key = (
                sale_id,
                product_id,
                str(quantity if unit_type == "EACH" else ""),
                str(weight if unit_type == "WEIGHT" else ""),
                str(line_total),
            )
            if key in existing_keys:
                report.sale_items.skipped += 1
                continue

            try:
                entity = SaleItem(
                    sale_id=sale_id,
                    product_id=product_id,
                    product_name_snapshot=product_name or f"Product {product_id}",
                    unit_type=unit_type,
                    quantity=quantity if unit_type == "EACH" else None,
                    weight_lbs=weight if unit_type == "WEIGHT" else None,
                    unit_price=unit_price,
                    line_subtotal=line_total,
                )
                session.add(entity)
                existing_keys.add(key)
                report.sale_items.inserted += 1
            except Exception:
                report.sale_items.errors += 1

        if dry_run:
            session.rollback()
        else:
            session.commit()

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate Access exports into Azure SQL schema")
    parser.add_argument("--connection-url", required=True, help="SQLAlchemy connection URL")
    parser.add_argument("--customers-csv", required=True, type=Path)
    parser.add_argument("--products-csv", required=True, type=Path)
    parser.add_argument("--sales-csv", required=True, type=Path)
    parser.add_argument("--sale-items-csv", required=True, type=Path)
    parser.add_argument("--report-path", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    engine = create_engine(args.connection_url, future=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    report = migrate(
        session_factory=session_factory,
        customers_rows=load_csv(args.customers_csv),
        products_rows=load_csv(args.products_csv),
        sales_rows=load_csv(args.sales_csv),
        sale_items_rows=load_csv(args.sale_items_csv),
        dry_run=args.dry_run,
    )

    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")

    print(f"Migration complete. Report written to {args.report_path}")
    print(json.dumps(report.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
