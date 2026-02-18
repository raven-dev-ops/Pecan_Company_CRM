from __future__ import annotations

import os
from pathlib import Path

from pecan_crm.config.env_parser import parse_env_file


ROOT_ENV_FILE = Path.cwd() / ".env"


def load_env_file(path: Path | None = None, *, override: bool = False) -> dict[str, str]:
    env_path = path or ROOT_ENV_FILE
    values = parse_env_file(env_path)

    for key, value in values.items():
        if override or key not in os.environ:
            os.environ[key] = value

    return values


def env_str(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_float(name: str, default: float = 0.0) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default