# Full import runbook

1. Start an empty PostGIS stack: `docker compose down -v && docker compose up --build`.
2. Verify migration and health: `curl --fail http://localhost:8000/health`.
3. Run validation dry-runs:
   - `docker compose run --rm api python -m app.cli.import_ponds --input /data/tameike_ichiranR8.xlsx --mode dry-run --limit 100`
   - `docker compose run --rm api python -m app.cli.import_ponds --input /data/tameike_ichiranR8.xlsx --mode dry-run --limit 1000`
4. Import the full file with idempotent upsert: `make import-ponds-full`.
5. Re-run the same command and confirm total row count does not increase.

Do not use `--resume`; imports are idempotent from the beginning via `UNIQUE(source_system, source_record_id)`.
