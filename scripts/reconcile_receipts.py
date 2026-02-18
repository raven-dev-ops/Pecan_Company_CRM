# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pecan_crm.db.models import Sale
from pecan_crm.db.repositories.sales import SalesRepository


@dataclass
class ReconcileReport:
    scanned: int = 0
    missing: int = 0
    regenerated: int = 0
    errors: int = 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect and repair missing receipt PDFs")
    parser.add_argument("--connection-url", required=True)
    parser.add_argument("--receipt-folder", required=True, type=Path)
    parser.add_argument("--business-name", required=True)
    parser.add_argument("--business-address", required=True)
    parser.add_argument("--business-phone", required=True)
    parser.add_argument("--report-path", required=True, type=Path)
    parser.add_argument("--no-repair", action="store_true", help="Detect only; do not regenerate")
    args = parser.parse_args()

    engine = create_engine(args.connection_url, future=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    repo = SalesRepository(session_factory)

    report = ReconcileReport()

    with session_factory() as session:
        sales = list(session.scalars(select(Sale).order_by(Sale.sale_id)).all())

    for sale in sales:
        report.scanned += 1
        path = args.receipt_folder / f"receipt_{sale.receipt_number}.pdf"
        if path.exists():
            continue

        report.missing += 1
        if args.no_repair:
            continue

        try:
            repo.regenerate_receipt(
                sale_id=sale.sale_id,
                receipt_folder=args.receipt_folder,
                business_name=args.business_name,
                business_address=args.business_address,
                business_phone=args.business_phone,
            )
            report.regenerated += 1
        except Exception:
            report.errors += 1

    payload = {
        "scanned": report.scanned,
        "missing": report.missing,
        "regenerated": report.regenerated,
        "errors": report.errors,
        "repair_mode": not args.no_repair,
    }

    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"Report written: {args.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
