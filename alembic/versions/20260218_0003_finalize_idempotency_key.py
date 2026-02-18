"""Add finalize idempotency key

Revision ID: 20260218_0003
Revises: 20260218_0002
Create Date: 2026-02-18 02:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260218_0003"
down_revision = "20260218_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sales", sa.Column("finalize_idempotency_key", sa.Unicode(64), nullable=True))
    op.create_unique_constraint(
        "UQ_sales_finalize_idempotency_key",
        "sales",
        ["finalize_idempotency_key"],
    )


def downgrade() -> None:
    op.drop_constraint("UQ_sales_finalize_idempotency_key", "sales", type_="unique")
    op.drop_column("sales", "finalize_idempotency_key")