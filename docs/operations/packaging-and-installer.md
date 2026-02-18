# Packaging and Installer Guide

Issue links: #38, #39

## Build executable (PyInstaller)
```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1 -Clean
```

Output:
- `dist/PecanCRM/` (Windows app bundle)

## Build installer (Inno Setup)
```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_installer.ps1
```

Output:
- `dist/PecanCRM-Setup.exe`

## Prerequisite handling
- Installer checks for `ODBC Driver 18 for SQL Server` via registry.
- Install aborts with clear message if missing.

## Target machine validation checklist
1. Clean Windows 10/11 machine.
2. Ensure ODBC Driver 18 installed.
3. Run installer and verify app + shortcuts.
4. Launch app, configure settings, run checkout smoke flow.
5. Uninstall app and verify business data is preserved:
   - Azure SQL data remains intact.
   - Receipt folder under `%ProgramData%\PecanCRM\receipts` is not deleted by default.