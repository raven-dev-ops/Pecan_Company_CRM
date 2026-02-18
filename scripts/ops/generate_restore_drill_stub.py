from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from pecan_crm.config.env import load_env_file, env_float, env_str


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate restore drill stub report from .env values")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--out", default="reports/restore_drill_stub.json")
    args = parser.parse_args()

    load_env_file(Path(args.env_file))

    payload = {
        "generated_at_utc": datetime.utcnow().isoformat(),
        "operator": env_str("RESTORE_DRILL_OPERATOR", "demo.operator"),
        "source": env_str("RESTORE_DRILL_SOURCE", "azure-pitr-demo"),
        "target_rpo_minutes": env_float("RESTORE_DRILL_RPO_MINUTES", 15.0),
        "target_rto_minutes": env_float("RESTORE_DRILL_RTO_MINUTES", 60.0),
        "validation": {
            "row_counts_checked": True,
            "sample_sales_checked": True,
            "receipt_regen_checked": True,
            "notes": "Stub evidence. Replace with real drill execution artifacts.",
        },
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())