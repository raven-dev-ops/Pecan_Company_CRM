"""Initial canonical schema

Revision ID: 20260218_0001
Revises:
Create Date: 2026-02-18 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260218_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("customer_id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("first_name", sa.Unicode(100), nullable=True),
        sa.Column("last_name", sa.Unicode(100), nullable=True),
        sa.Column("phone", sa.Unicode(30), nullable=True),
        sa.Column("email", sa.Unicode(254), nullable=True),
        sa.Column("notes", sa.Unicode(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at_utc",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("SYSUTCDATETIME()"),
        ),
        sa.Column(
            "updated_at_utc",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("SYSUTCDATETIME()"),
        ),
    )

    op.create_table(
        "products",
        sa.Column("product_id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("sku", sa.Unicode(50), nullable=True),
        sa.Column("name", sa.Unicode(200), nullable=False),
        sa.Column("unit_type", sa.Unicode(10), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at_utc",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("SYSUTCDATETIME()"),
        ),
        sa.Column(
            "updated_at_utc",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("SYSUTCDATETIME()"),
        ),
        sa.CheckConstraint("unit_type IN ('EACH', 'WEIGHT')", name="CK_products_unit_type"),
        sa.CheckConstraint("unit_price >= 0", name="CK_products_unit_price_nonnegative"),
    )

    op.create_table(
        "sales",
        sa.Column("sale_id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("receipt_number", sa.Unicode(20), nullable=False),
        sa.Column("customer_id", sa.BigInteger(), nullable=True),
        sa.Column("payment_method", sa.Unicode(20), nullable=False),
        sa.Column(
            "status",
            sa.Unicode(20),
            nullable=False,
            server_default=sa.text("'FINALIZED'"),
        ),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_total", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("tax_total", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("void_reason", sa.Unicode(300), nullable=True),
        sa.Column("sold_at_utc", sa.DateTime(), nullable=False, server_default=sa.text("SYSUTCDATETIME()")),
        sa.Column(
            "created_at_utc",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("SYSUTCDATETIME()"),
        ),
        sa.Column(
            "updated_at_utc",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("SYSUTCDATETIME()"),
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"], name="FK_sales_customer"),
        sa.UniqueConstraint("receipt_number", name="UQ_sales_receipt_number"),
        sa.CheckConstraint(
            "payment_method IN ('CASH', 'CARD', 'OTHER')",
            name="CK_sales_payment_method",
        ),
        sa.CheckConstraint("status IN ('FINALIZED', 'VOIDED')", name="CK_sales_status"),
        sa.CheckConstraint(
            "subtotal >= 0 AND discount_total >= 0 AND tax_total >= 0 AND total >= 0",
            name="CK_sales_money_nonnegative",
        ),
    )

    op.create_table(
        "sale_items",
        sa.Column("sale_item_id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("sale_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("product_name_snapshot", sa.Unicode(200), nullable=False),
        sa.Column("unit_type", sa.Unicode(10), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 3), nullable=True),
        sa.Column("weight_lbs", sa.Numeric(10, 3), nullable=True),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("line_subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "created_at_utc",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("SYSUTCDATETIME()"),
        ),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.sale_id"], name="FK_sale_items_sale"),
        sa.ForeignKeyConstraint(["product_id"], ["products.product_id"], name="FK_sale_items_product"),
        sa.CheckConstraint("unit_type IN ('EACH', 'WEIGHT')", name="CK_sale_items_unit_type"),
        sa.CheckConstraint(
            "(quantity IS NULL OR quantity >= 0) AND (weight_lbs IS NULL OR weight_lbs >= 0) AND unit_price >= 0 AND line_subtotal >= 0",
            name="CK_sale_items_values_nonnegative",
        ),
        sa.CheckConstraint(
            "(unit_type = 'EACH' AND quantity IS NOT NULL AND weight_lbs IS NULL) OR (unit_type = 'WEIGHT' AND weight_lbs IS NOT NULL AND quantity IS NULL)",
            name="CK_sale_items_measure_pair",
        ),
    )

    op.create_table(
        "app_settings",
        sa.Column("setting_key", sa.Unicode(100), primary_key=True),
        sa.Column("setting_value", sa.UnicodeText(), nullable=False),
        sa.Column(
            "updated_at_utc",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("SYSUTCDATETIME()"),
        ),
    )

    op.create_index("IX_sales_sold_at_utc", "sales", ["sold_at_utc"])
    op.create_index("IX_sales_customer_id", "sales", ["customer_id"])
    op.create_index("IX_sale_items_sale_id", "sale_items", ["sale_id"])
    op.create_index("IX_products_name", "products", ["name"])
    op.create_index("IX_customers_phone", "customers", ["phone"])
    op.create_index("IX_customers_email", "customers", ["email"])


def downgrade() -> None:
    op.drop_index("IX_customers_email", table_name="customers")
    op.drop_index("IX_customers_phone", table_name="customers")
    op.drop_index("IX_products_name", table_name="products")
    op.drop_index("IX_sale_items_sale_id", table_name="sale_items")
    op.drop_index("IX_sales_customer_id", table_name="sales")
    op.drop_index("IX_sales_sold_at_utc", table_name="sales")

    op.drop_table("app_settings")
    op.drop_table("sale_items")
    op.drop_table("sales")
    op.drop_table("products")
    op.drop_table("customers")