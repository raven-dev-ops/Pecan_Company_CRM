# Discovery: Legacy Microsoft Access Inventory

Issue link: #2

## Purpose
Remove ambiguity around what the current Access solution stores and how data is connected.

## Current status
- Inventory run: `NOT YET EXECUTED`
- Blocking dependency: access to the production `.accdb/.mdb` file and workstation where it is used.

## Required findings
1. Storage model
- Determine whether Access contains local tables or linked SQL/ODBC tables.
- Capture evidence: screenshot of Navigation Pane table icons and Linked Table Manager output.

2. Entity and field inventory
- Export table list with row counts.
- For each table, record columns, types, nullability, keys, indexes.

3. Environment and assets
- File location(s) of Access DB and related assets.
- Any passwords or startup macros/forms/reports in active daily workflow.
- External linked sources and DSN names.

## Data capture checklist
- [ ] Access file path captured
- [ ] File size and last modified timestamp captured
- [ ] Linked table manager results captured
- [ ] Table catalog exported
- [ ] Forms/reports used in operations listed
- [ ] Credential handling method documented

## Next action
Run this inventory on the target client machine and update this document with concrete findings.