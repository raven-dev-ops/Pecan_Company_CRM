from __future__ import annotations

import logging
from pathlib import Path


def _default_log_dir(app_name: str) -> Path:
    local_app_data = Path.home() / "AppData" / "Local"
    return local_app_data / app_name / "logs"


def configure_logging(app_name: str) -> Path:
    log_dir = _default_log_dir(app_name)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / "pecan_crm.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return log_path