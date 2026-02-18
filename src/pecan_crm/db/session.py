from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from pecan_crm.db.connection import create_db_engine


def make_session_factory(*, server: str, database: str, username: str, password: str) -> sessionmaker[Session]:
    engine = create_db_engine(
        server=server,
        database=database,
        username=username,
        password=password,
    )
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)