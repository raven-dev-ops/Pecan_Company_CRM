from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from pecan_crm.db.connection import create_db_engine
from pecan_crm.db.retry import run_with_retry


def test_connection(*, server: str, database: str, username: str, password: str, attempts: int = 3) -> None:
    def _attempt() -> None:
        engine = create_db_engine(
            server=server,
            database=database,
            username=username,
            password=password,
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    run_with_retry(_attempt, attempts=attempts)