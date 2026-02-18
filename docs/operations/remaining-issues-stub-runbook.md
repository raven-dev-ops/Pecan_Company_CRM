# Remaining-Issue Stubs (Demo .env Driven)

This document maps stub artifacts to remaining issues and uses demo values from `.env`.

## #2 Access inventory stub
```powershell
python scripts/ops/generate_access_inventory_stub.py --env-file .env --out reports/access_inventory_stub.json
```

## #49 Restore drill stub
```powershell
python scripts/ops/generate_restore_drill_stub.py --env-file .env --out reports/restore_drill_stub.json
```

## #50 Code signing + SmartScreen stub
```powershell
powershell -ExecutionPolicy Bypass -File scripts/ops/signing_stub.ps1 -EnvFile .env -ArtifactsDir dist
```

## #44 Offline queue stub
- Queue primitives: `src/pecan_crm/offline/queue.py`
- Policy doc: `docs/operations/offline-queue-stub.md`

## Notes
- All outputs are intentionally demo/stub artifacts.
- Replace demo values in `.env` with real values before production execution.