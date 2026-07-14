# Full import result

Status: **not completed in this local environment**.

## Why

The local runner does not provide the `docker` command, so a PostGIS-backed Docker Compose stack could not be started for the required 1,000 / 10,000 / full upsert and rerun checks. Package download commands were also blocked by a 403 proxy for npm/pip registries.

## Completed local measurements

- `cd apps/api && python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --mode dry-run --limit 100 --batch-size 100 --report ../../artifacts/import-dryrun-100.json`
- `cd apps/api && python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --mode dry-run --limit 1000 --batch-size 1000 --report ../../artifacts/import-dryrun-1000.json`

See `artifacts/import-dryrun-100.json` and `artifacts/import-dryrun-1000.json` for measured rows/sec, memory, duplicate and coordinate-quality counts.

## Reproduction commands for the missing PostGIS measurements

```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
cd apps/api
DATABASE_URL=postgresql+psycopg://tameike:tameike@localhost:5432/tameike alembic upgrade head
DATABASE_URL=postgresql+psycopg://tameike:tameike@localhost:5432/tameike python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --mode upsert --batch-size 5000 --report ../../artifacts/import-full.json
DATABASE_URL=postgresql+psycopg://tameike:tameike@localhost:5432/tameike python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --mode upsert --batch-size 5000 --report ../../artifacts/import-rerun.json
```

## Unmet acceptance conditions

- Full 161,846-row PostGIS upsert.
- Same-file rerun idempotency on PostGIS.
- Post-import quality SQL aggregation on PostGIS.
- Remote GitHub Actions success confirmation.
