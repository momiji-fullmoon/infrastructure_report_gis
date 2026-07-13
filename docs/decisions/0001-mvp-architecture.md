# ADR 0001: MVP architecture and schema/API reconciliation

## Status
Accepted

## Context
`openapi.yaml` and `database_schema.sql` describe a PoC v0.9 subset. The MVP requirements add disaster events, recommended actions, data-quality management, provider adapters, and explicit baseline risk scoring.

## Decision
- Keep OpenAPI-compatible `/ponds`, `/ponds/{pondId}`, `/ponds/{pondId}/observations` semantics and add required MVP endpoints.
- Use SQLAlchemy-managed schema for local MVP migrations while preserving `database_schema.sql` as the source reference.
- Store location as latitude/longitude in SQLite-compatible MVP columns and document PostGIS Geometry migration in `infra/migrations/0001_initial.sql` for Docker PostgreSQL/PostGIS.
- Display and return `risk screening score` only; never expose it as breach probability.

## Consequences
- Local tests can run without PostGIS, while Docker deployment can evolve to Geometry columns.
- Some advanced spatial operations are implemented as BBox filtering in the MVP and must be replaced by PostGIS predicates before production load testing.
