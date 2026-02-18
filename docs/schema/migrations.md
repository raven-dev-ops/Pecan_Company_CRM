# Database Migrations

Issue link: #14

## Setup
1. Install dependencies.
2. Set `DATABASE_URL` environment variable.
3. Run migrations with Alembic.

## Example `DATABASE_URL`
`mssql+pyodbc://username:password@server.database.windows.net/database?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no`

## Commands
- Upgrade to latest:
  - `alembic upgrade head`
- Show current revision:
  - `alembic current`
- Roll back one revision:
  - `alembic downgrade -1`

## Policy
- Schema changes must be introduced through Alembic revisions.
- Direct manual production DDL changes are not allowed.