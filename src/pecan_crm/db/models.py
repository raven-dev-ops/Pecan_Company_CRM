from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, Unicode, UnicodeText
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str | None] = mapped_column(Unicode(100))
    last_name: Mapped[str | None] = mapped_column(Unicode(100))
    phone: Mapped[str | None] = mapped_column(Unicode(30))
    email: Mapped[str | None] = mapped_column(Unicode(254))
    notes: Mapped[str | None] = mapped_column(Unicode(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sku: Mapped[str | None] = mapped_column(Unicode(50))
    name: Mapped[str] = mapped_column(Unicode(200))
    unit_type: Mapped[str] = mapped_column(Unicode(10))
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Sale(Base):
    __tablename__ = "sales"

    sale_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    receipt_number: Mapped[str] = mapped_column(Unicode(20), unique=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.customer_id"))
    payment_method: Mapped[str] = mapped_column(Unicode(20))
    status: Mapped[str] = mapped_column(Unicode(20), default="FINALIZED")
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2))
    discount_total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    tax_total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2))
    void_reason: Mapped[str | None] = mapped_column(Unicode(300))
    sold_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SaleItem(Base):
    __tablename__ = "sale_items"

    sale_item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.sale_id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"))
    product_name_snapshot: Mapped[str] = mapped_column(Unicode(200))
    unit_type: Mapped[str] = mapped_column(Unicode(10))
    quantity: Mapped[float | None] = mapped_column(Numeric(10, 3))
    weight_lbs: Mapped[float | None] = mapped_column(Numeric(10, 3))
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2))
    line_subtotal: Mapped[float] = mapped_column(Numeric(12, 2))
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AppSetting(Base):
    __tablename__ = "app_settings"

    setting_key: Mapped[str] = mapped_column(Unicode(100), primary_key=True)
    setting_value: Mapped[str] = mapped_column(UnicodeText)
    updated_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)