from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from pecan_crm.config.secret_store import SecretStore
from pecan_crm.config.store import ConfigStore
from pecan_crm.db.session import make_session_factory


def build_session_factory_from_settings(
    config_store: ConfigStore | None = None,
    secret_store: SecretStore | None = None,
) -> sessionmaker[Session]:
    config_store = config_store or ConfigStore()
    secret_store = secret_store or SecretStore()

    config = config_store.load()
    password = secret_store.get_db_password()

    server = config.database.server.strip()
    database = config.database.database.strip()
    username = config.database.username.strip()

    if not (server and database and username and password):
        raise RuntimeError("Database settings are incomplete. Update Settings and save first.")

    return make_session_factory(
        server=server,
        database=database,
        username=username,
        password=password,
    )