Local Django backend (Django 6)

Prerequisites
- Python 3.12+ (Django 6.0 drops Python 3.10/3.11).

Quick start (Windows)
1) cd backend
2) copy .env.example .env
3) scripts\run_local.bat

Quick start (macOS/Linux)
1) cd backend
2) cp .env.example .env
3) chmod +x scripts/run_local.sh
4) ./scripts/run_local.sh

What this gives you
- A working Django project wired to a local SQL database (SQLite file: backend/db.sqlite3)
- A health check endpoint: http://127.0.0.1:8000/health/
- Django Admin: http://127.0.0.1:8000/admin/

Create an admin user
- python manage.py createsuperuser

Switching databases later
- Azure SQL / SQL Server: set DATABASE_ENGINE=mssql in .env and provide MSSQL_* variables.
  You will also need to install mssql-django + pyodbc and an ODBC driver.

Azure and legacy integrations
- integrations/azure.py and integrations/legacy.py are stubs.
- Enable toggles (AZURE_ENABLED / LEGACY_ENABLED) when real implementations exist.