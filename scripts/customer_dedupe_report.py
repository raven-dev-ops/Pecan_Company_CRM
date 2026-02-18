from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def normalize_phone(value: str) -> str:
    return "".join(ch for ch in (value or "") if ch.isdigit())


def normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def pick(row: dict[str, str], *candidates: str) -> str:
    for key in candidates:
        if key in row and str(row[key]).strip():
            return str(row[key]).strip()
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate duplicate-candidate report for customers")
    parser.add_argument("--customers-csv", required=True, type=Path)
    parser.add_argument("--out-csv", required=True, type=Path)
    args = parser.parse_args()

    with args.customers_csv.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    by_email: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_phone: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_name: dict[str, list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        email = normalize_text(pick(row, "Email", "email"))
        phone = normalize_phone(pick(row, "Phone", "phone"))
        first = normalize_text(pick(row, "FirstName", "first_name"))
        last = normalize_text(pick(row, "LastName", "last_name"))

        if email:
            by_email[email].append(row)
        if phone:
            by_phone[phone].append(row)
        if first or last:
            by_name[f"{first}|{last}"].append(row)

    candidates: list[dict[str, str]] = []

    def add_group(reason: str, key: str, group: list[dict[str, str]]) -> None:
        if len(group) < 2:
            return
        for row in group:
            candidates.append(
                {
                    "reason": reason,
                    "match_key": key,
                    "customer_id": pick(row, "CustomerID", "customer_id", "ID", "Id"),
                    "first_name": pick(row, "FirstName", "first_name"),
                    "last_name": pick(row, "LastName", "last_name"),
                    "phone": pick(row, "Phone", "phone"),
                    "email": pick(row, "Email", "email"),
                }
            )

    for key, group in by_email.items():
        add_group("email", key, group)
    for key, group in by_phone.items():
        add_group("phone", key, group)
    for key, group in by_name.items():
        add_group("name", key, group)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "reason",
                "match_key",
                "customer_id",
                "first_name",
                "last_name",
                "phone",
                "email",
            ],
        )
        writer.writeheader()
        writer.writerows(candidates)

    print(f"Wrote duplicate report: {args.out_csv}")
    print(f"Candidate rows: {len(candidates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())