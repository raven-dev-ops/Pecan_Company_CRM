from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class QueuedSale:
    queue_id: int
    idempotency_key: str
    payload_json: str
    created_at_utc: str


class OfflineSaleQueue:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS queued_sales (
                    queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    payload_json TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'PENDING',
                    last_error TEXT NULL
                )
                """
            )
            conn.commit()

    def enqueue(self, *, idempotency_key: str, payload: dict[str, Any]) -> int:
        payload_json = json.dumps(payload)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO queued_sales(idempotency_key, payload_json, created_at_utc, status)
                VALUES (?, ?, ?, 'PENDING')
                """,
                (idempotency_key, payload_json, datetime.now(UTC).isoformat()),
            )
            conn.commit()
            row = conn.execute(
                "SELECT queue_id FROM queued_sales WHERE idempotency_key = ?", (idempotency_key,)
            ).fetchone()
            return int(row["queue_id"])

    def pending(self) -> list[QueuedSale]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT queue_id, idempotency_key, payload_json, created_at_utc FROM queued_sales WHERE status = 'PENDING' ORDER BY queue_id"
            ).fetchall()
            return [
                QueuedSale(
                    queue_id=int(r["queue_id"]),
                    idempotency_key=str(r["idempotency_key"]),
                    payload_json=str(r["payload_json"]),
                    created_at_utc=str(r["created_at_utc"]),
                )
                for r in rows
            ]

    def process_pending(self, sender: Callable[[str, dict[str, Any]], None]) -> dict[str, int]:
        sent = 0
        failed = 0

        for item in self.pending():
            payload = json.loads(item.payload_json)
            try:
                sender(item.idempotency_key, payload)
                with self._connect() as conn:
                    conn.execute(
                        "UPDATE queued_sales SET status = 'SENT', last_error = NULL WHERE queue_id = ?",
                        (item.queue_id,),
                    )
                    conn.commit()
                sent += 1
            except Exception as exc:
                with self._connect() as conn:
                    conn.execute(
                        "UPDATE queued_sales SET status = 'PENDING', last_error = ? WHERE queue_id = ?",
                        (str(exc), item.queue_id),
                    )
                    conn.commit()
                failed += 1

        return {"sent": sent, "failed": failed}
