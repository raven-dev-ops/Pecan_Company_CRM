from __future__ import annotations

from pathlib import Path
import os

from pydantic import BaseModel, Field


def default_receipt_folder() -> str:
    program_data = os.getenv("PROGRAMDATA", r"C:\ProgramData")
    return str(Path(program_data) / "PecanCRM" / "receipts")


class DatabaseConfig(BaseModel):
    server: str = ""
    database: str = ""
    username: str = ""


class BusinessProfileConfig(BaseModel):
    name: str = ""
    address: str = ""
    phone: str = ""
    logo_path: str = ""


class TaxConfig(BaseModel):
    enabled: bool = False
    rate_percent: float = Field(default=0.0, ge=0.0, le=100.0)


class AppConfig(BaseModel):
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    business: BusinessProfileConfig = Field(default_factory=BusinessProfileConfig)
    tax: TaxConfig = Field(default_factory=TaxConfig)
    receipt_folder: str = Field(default_factory=default_receipt_folder)
