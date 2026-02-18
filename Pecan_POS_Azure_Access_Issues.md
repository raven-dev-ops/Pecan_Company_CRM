# Pecan POS + Customer Database (Local .exe, Python) — Issues List (Azure + Legacy Access)

Goal: Build a Windows desktop app (.exe) in Python that runs locally, supports simple “ring up” transactions for pecans, stores customer + sales data in Azure, and generates a PDF receipt for each sale. The client currently has a legacy Microsoft Access setup that must be treated as the existing system of record during transition (migration + validation + cutover).

---

## Architecture Baseline (current target)
- Front-end: Python desktop GUI (PySide6 or PyQt)
- Packaging: PyInstaller to produce a Windows .exe + installer (Inno Setup / NSIS)
- Cloud data: Azure SQL Database (primary database)
- Optional offline continuity: local SQLite cache/queue (configurable)
- Receipts: generated locally as PDF; optionally uploaded to Azure Blob Storage for centralized retention
- Legacy: Microsoft Access (.accdb/.mdb) and/or Access as a front-end to an existing SQL database (confirm in discovery)

---

## Milestones
1) Discovery + Specs
2) Azure Foundation (Infrastructure + Security)
3) Data Model + Storage
4) Legacy Access Migration & Cutover
5) POS (Ring-Up) Flow
6) Receipt PDF + Printing
7) Customer Management
8) Reporting + Exports + Backups
9) Packaging (.exe) + Installer
10) QA + Release

---

## Issue Format Legend
- Priority: P0 (must), P1 (should), P2 (nice)
- Each issue includes Acceptance Criteria (AC) to define “done”.

---

## Discovery + Specs (high-priority highlights)
- Confirm legacy Access reality: local Access tables vs linked SQL backend.
- Define Azure usage model: direct desktop-to-Azure SQL vs API layer.
- Define MVP workflow/screens and receipt requirements.
- Confirm product pricing model: bag size, weight, or both.

## Data + POS + Receipts (high-priority highlights)
- Canonical Azure SQL schema for customers/products/sales/sale_items/settings.
- Ring-up flow with each/weight item support and payment capture.
- Transaction-safe receipt numbering and PDF generation.
- Reprint/regenerate receipt from history.

## Migration + Operations (high-priority highlights)
- Build repeatable Access → Azure SQL migration tooling.
- Validate data quality and document cutover/rollback plans.
- Define backups (Azure SQL PITR + local receipts/export backup guidance).

For detailed, GitHub-importable issue definitions and labels, see `issues.json` and `scripts/create_issues.py`.
