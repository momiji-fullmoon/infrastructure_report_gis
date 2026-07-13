setup:
	cd apps/api && python -m pip install -e '.[dev]'
	cd apps/web && npm install
up:
	docker compose up --build
down:
	docker compose down
migrate:
	cd apps/api && alembic upgrade head
migrate-down:
	cd apps/api && alembic downgrade base
seed:
	cd apps/api && python -m scripts.seed_sample
import-ponds:
	cd apps/api && python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --mode upsert --batch-size 5000 --limit 1000 --report ../../artifacts/import-sample.json
import-ponds-full:
	cd apps/api && python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --mode upsert --batch-size 5000 --report ../../artifacts/import-full.json
benchmark-import: import-ponds
benchmark-api:
	cd apps/api && python -m app.cli.benchmark_api || true
test:
	cd apps/api && pytest
test-integration:
	docker compose up -d db
	cd apps/api && DATABASE_URL=postgresql+psycopg://tameike:tameike@localhost:5432/tameike pytest tests/test_postgis_integration.py
test-web:
	cd apps/web && npm test
lint:
	cd apps/api && ruff check app tests
	cd apps/web && npm run lint -- --max-warnings=0
format:
	cd apps/api && ruff format app tests
e2e:
	cd apps/web && npx playwright test
