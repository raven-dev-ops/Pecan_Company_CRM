# Migration Cutover and Rollback Plan

Issue link: #37

## Planned cutover window
- Final export/import window: after business close, before next opening shift.
- Freeze legacy Access data entry at cutover start.

## Cutover steps
1. Announce cutover start and freeze Access writes.
2. Export final Access snapshot.
3. Run migration script for final delta load.
4. Validate row counts and critical spot-checks.
5. Update app config to production Azure SQL target.
6. Run smoke transaction in new app and verify receipt.
7. Announce go-live and monitor first business hour.

## Rollback trigger conditions
- Critical data mismatch affecting financial totals.
- Repeated transaction save failures.
- Inability to generate or reprint receipts.

## Rollback steps
1. Stop new app usage.
2. Resume Access workflow for transaction entry.
3. Record rollback timestamp and reason.
4. Preserve failed cutover artifacts for analysis.
5. Open remediation issues and schedule next cutover window.

## Post-cutover tasks
- Archive final Access snapshot as immutable backup.
- Document final status and lessons learned.