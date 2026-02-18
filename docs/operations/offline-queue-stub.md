# Offline Queue Stub

Issue link: #44

## Behavior
- When online finalize fails due connection issues, sale payload can be queued in local SQLite.
- Queue uses idempotency key to avoid duplicate queue entries.
- Sync process replays pending queued payloads when connection returns.

## Storage
- SQLite path from `.env`: `OFFLINE_QUEUE_DB_PATH`
- Default demo path: `C:\ProgramData\PecanCRM\offline_queue.db`

## Conflict handling (stub policy)
- Replay uses same finalize idempotency key.
- If sale already exists server-side, replay is treated as success and queue item marked SENT.
- Server-side data is source of truth for final receipt number.

## Files
- `src/pecan_crm/offline/queue.py`

## Demo integration note
Current implementation provides queue primitives and processing API.
Wire-up into full online/offline UI flow can be expanded without schema changes.