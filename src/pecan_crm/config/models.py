from __future__ import annotations

from pathlib import Path
import os

from pydantic import BaseModel, Field

from pecan_crm.config.env import env_bool, env_float, env_str


def default_receipt_folder() -> str:
    program_data = os.getenv("PROGRAMDATA", r"C:\ProgramData")
    return env_str("APP_RECEIPT_FOLDER", str(Path(program_data) / "PecanCRM" / "receipts"))


class DatabaseConfig(BaseModel):
    server: str = Field(default_factory=lambda: env_str("AZURE_SQL_SERVER_FQDN"))
    database: str = Field(default_factory=lambda: env_str("AZURE_SQL_DATABASE"))
    username: str = Field(default_factory=lambda: env_str("AZURE_APP_LOGIN"))


class BusinessProfileConfig(BaseModel):
    name: str = Field(default_factory=lambda: env_str("APP_BUSINESS_NAME"))
    address: str = Field(default_factory=lambda: env_str("APP_BUSINESS_ADDRESS"))
    phone: str = Field(default_factory=lambda: env_str("APP_BUSINESS_PHONE"))
    logo_path: str = ""


class TaxConfig(BaseModel):
    enabled: bool = Field(default_factory=lambda: env_bool("APP_TAX_ENABLED", False))
    rate_percent: float = Field(
        default_factory=lambda: env_float("APP_TAX_RATE_PERCENT", 0.0),
        ge=0.0,
        le=100.0,
    )


class AppConfig(BaseModel):
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    business: BusinessProfileConfig = Field(default_factory=BusinessProfileConfig)
    tax: TaxConfig = Field(default_factory=TaxConfig)
    receipt_folder: str = Field(default_factory=default_receipt_folder)
