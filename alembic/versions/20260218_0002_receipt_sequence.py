"""Add receipt number sequence

Revision ID: 20260218_0002
Revises: 20260218_0001
Create Date: 2026-02-18 01:00:00
"""

from __future__ import annotations

from alembic import op


revision = "20260218_0002"
down_revision = "20260218_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE receipt_number_seq AS BIGINT START WITH 1 INCREMENT BY 1;")


def downgrade() -> None:
    op.execute("DROP SEQUENCE receipt_number_seq;")