# Managed PostGIS

Use a provider-neutral PostgreSQL 16-compatible managed database with PostGIS, TLS, backups, monitoring, and GitHub Actions network access. Configure `DATABASE_URL` only as a secret, for example `postgresql+psycopg://USER:PASSWORD@HOST:5432/DB?sslmode=require`.

Connection pool environment variables:

- `DB_POOL_SIZE` default `3`
- `DB_MAX_OVERFLOW` default `2`
- `DB_POOL_TIMEOUT` default `30`
- `DB_POOL_RECYCLE` default `1800`

Alembic is executed by GitHub Actions, not at API Container startup.
