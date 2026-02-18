from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL


def build_azure_sql_url(*, server: str, database: str, username: str, password: str) -> URL:
    return URL.create(
        "mssql+pyodbc",
        username=username,
        password=password,
        host=server,
        database=database,
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "Encrypt": "yes",
            "TrustServerCertificate": "no",
        },
    )


def create_db_engine(*, server: str, database: str, username: str, password: str) -> Engine:
    url = build_azure_sql_url(
        server=server,
        database=database,
        username=username,
        password=password,
    )
    return create_engine(url, pool_pre_ping=True, future=True)