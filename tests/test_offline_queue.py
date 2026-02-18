from pathlib import Path

from pecan_crm.offline.queue import OfflineSaleQueue


def test_offline_queue_enqueue_and_pending(tmp_path: Path) -> None:
    queue_path = tmp_path / "offline.db"
    q = OfflineSaleQueue(queue_path)

    queue_id = q.enqueue(idempotency_key="abc-123", payload={"sale": 1})
    assert queue_id > 0

    pending = q.pending()
    assert len(pending) == 1
    assert pending[0].idempotency_key == "abc-123"


def test_offline_queue_process_pending_marks_sent(tmp_path: Path) -> None:
    queue_path = tmp_path / "offline.db"
    q = OfflineSaleQueue(queue_path)
    q.enqueue(idempotency_key="abc-123", payload={"sale": 1})

    seen: list[str] = []

    def sender(idempotency_key: str, payload: dict) -> None:
        seen.append(idempotency_key)

    result = q.process_pending(sender)
    assert result["sent"] == 1
    assert result["failed"] == 0
    assert seen == ["abc-123"]
    assert q.pending() == []