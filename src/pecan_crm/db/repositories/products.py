from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from pecan_crm.db.models import Product


@dataclass(frozen=True)
class ProductInput:
    name: str
    sku: str
    unit_type: str
    unit_price: Decimal
    is_active: bool = True


class ProductRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def list_products(self, *, include_inactive: bool = True, search: str = "") -> list[Product]:
        with self.session_factory() as session:
            query = select(Product)
            if not include_inactive:
                query = query.where(Product.is_active.is_(True))
            if search:
                wildcard = f"%{search.strip()}%"
                query = query.where(Product.name.ilike(wildcard) | Product.sku.ilike(wildcard))
            query = query.order_by(Product.name.asc())
            return list(session.scalars(query).all())

    def save(self, data: ProductInput, *, product_id: int | None = None) -> Product:
        self._validate(data)
        with self.session_factory() as session:
            if product_id is None:
                entity = Product(
                    name=data.name,
                    sku=data.sku or None,
                    unit_type=data.unit_type,
                    unit_price=data.unit_price,
                    is_active=data.is_active,
                )
                session.add(entity)
            else:
                entity = session.get(Product, product_id)
                if entity is None:
                    raise ValueError("Product not found")
                entity.name = data.name
                entity.sku = data.sku or None
                entity.unit_type = data.unit_type
                entity.unit_price = data.unit_price
                entity.is_active = data.is_active
                entity.updated_at_utc = datetime.utcnow()

            session.commit()
            session.refresh(entity)
            return entity

    def archive(self, product_id: int) -> None:
        with self.session_factory() as session:
            entity = session.get(Product, product_id)
            if entity is None:
                raise ValueError("Product not found")
            entity.is_active = False
            entity.updated_at_utc = datetime.utcnow()
            session.commit()

    @staticmethod
    def _validate(data: ProductInput) -> None:
        if not data.name.strip():
            raise ValueError("Product name is required")

        unit_type = data.unit_type.upper()
        if unit_type not in {"EACH", "WEIGHT"}:
            raise ValueError("Unit type must be EACH or WEIGHT")

        if data.unit_price < Decimal("0"):
            raise ValueError("Unit price cannot be negative")