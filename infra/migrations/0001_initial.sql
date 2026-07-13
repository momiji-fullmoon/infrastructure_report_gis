-- Alembic-equivalent initial migration for MVP; based on database_schema.sql and extended for required entities.
CREATE EXTENSION IF NOT EXISTS postgis;
-- See apps/api/app/models/models.py for SQLAlchemy-managed schema used by `make migrate`.
