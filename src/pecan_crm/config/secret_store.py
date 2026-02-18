from __future__ import annotations

import logging

import keyring
from keyring.errors import KeyringError

from pecan_crm.config.env import env_str


LOGGER = logging.getLogger(__name__)


class SecretStore:
    def __init__(self, app_name: str = "PecanCRM") -> None:
        self.app_name = app_name
        self.db_password_key = "azure_sql_password"

    def get_db_password(self) -> str:
        env_password = env_str("AZURE_APP_PASSWORD")
        if env_password:
            return env_password

        try:
            value = keyring.get_password(self.app_name, self.db_password_key)
            return value or ""
        except KeyringError:
            LOGGER.exception("Failed to read DB password from keyring")
            return ""

    def set_db_password(self, password: str) -> None:
        try:
            keyring.set_password(self.app_name, self.db_password_key, password)
        except KeyringError as exc:
            raise RuntimeError("Unable to store credentials in secure keyring") from exc
