from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from pecan_crm.config.env import load_env_file, env_str


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Access inventory stub evidence from .env values")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--out", default="reports/access_inventory_stub.json")
    args = parser.parse_args()

    load_env_file(Path(args.env_file))

    payload = {
        "generated_at_utc": datetime.utcnow().isoformat(),
        "storage_mode": env_str("ACCESS_STORAGE_MODE", "LOCAL_TABLES"),
        "access_db_path": env_str("ACCESS_DB_PATH"),
        "linked_table_dsn": env_str("ACCESS_LINKED_TABLE_DSN"),
        "forms_used": [x.strip() for x in env_str("ACCESS_FORMS_USED").split(",") if x.strip()],
        "reports_used": [x.strip() for x in env_str("ACCESS_REPORTS_USED").split(",") if x.strip()],
        "notes": "Stub inventory generated from demo env values. Replace with real findings from client Access workstation.",
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())