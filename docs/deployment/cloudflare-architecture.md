# Cloudflare architecture

Status: configuration implemented; production deployment not yet verified.

The deployment keeps Next.js, FastAPI, SQLAlchemy, GeoAlchemy2, Alembic, PostgreSQL, and PostGIS. It does not use D1 for spatial data.

- `app.<DOMAIN>`: Cloudflare Workers running Next.js through OpenNext.
- `api.<DOMAIN>`: Cloudflare Worker routing to a Cloudflare Container.
- Cloudflare Container: FastAPI image built from `apps/api/Dockerfile.cloudflare` on `linux/amd64`.
- Database: external managed PostgreSQL 16-compatible service with PostGIS and TLS.
- R2: object storage for the Excel ledger, import reports, future reports, and satellite assets.
- GitHub Actions: tests, migration, Cloudflare deploy, production smoke, and R2-backed imports.

OpenNext package: `@opennextjs/cloudflare`. Containers use `@cloudflare/containers`, a Durable Object binding, and `new_sqlite_classes` migrations. Containers require Workers Paid plan and a `linux/amd64` image. Custom domains are configured in the Cloudflare dashboard or Wrangler routes after real domains are known.
