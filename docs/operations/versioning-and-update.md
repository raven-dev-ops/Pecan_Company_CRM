# Versioning and Manual Update Approach

Issue link: #40

## Versioning policy
- Semantic versioning for app releases: `MAJOR.MINOR.PATCH`.
- Version source: `src/pecan_crm/__init__.py`.
- App displays current version in main window status bar.

## Manual update flow
1. Download new installer package.
2. Close running app.
3. Run installer for new version.
4. Re-open app and confirm version display.

## Data preservation expectations
- Business data remains in Azure SQL and is not removed by app update.
- Local receipts remain in configured receipt folder.
- Uninstall should not delete business data by default.

## Release operator checklist
- Verify installer checksum/signature (when enabled).
- Verify app launches and version display updates.
- Verify settings persisted after update.