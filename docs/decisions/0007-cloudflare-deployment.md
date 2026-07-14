# ADR 0007: Cloudflare deployment without D1 migration

Accepted.

We deploy Next.js with OpenNext on Cloudflare Workers and FastAPI inside Cloudflare Containers, connected directly to managed PostgreSQL/PostGIS over TLS. R2 stores ledger and import artifacts.

D1 is rejected for the spatial database because the application depends on PostGIS Geometry, GiST indexes, `ST_Intersects`, `ST_DWithin`, GeoAlchemy2, psycopg, and Alembic.

Hyperdrive is not required in phase 1. It remains a future option if selected API endpoints move from FastAPI Container into a Worker and need pooled database access from Worker runtime.
