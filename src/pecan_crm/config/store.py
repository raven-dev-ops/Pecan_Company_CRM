from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from pecan_crm.config.models import AppConfig


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (Path.home() / "AppData" / "Local" / "PecanCRM" / "settings.json")

    def load(self) -> AppConfig:
        if not self.path.exists():
            return AppConfig()

        raw = self.path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
            return AppConfig.model_validate(data)
        except (json.JSONDecodeError, ValidationError):
            return AppConfig()

    def save(self, config: AppConfig) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(config.model_dump_json(indent=2), encoding="utf-8")