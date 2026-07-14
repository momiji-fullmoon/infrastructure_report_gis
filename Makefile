.PHONY: setup up down migrate migrate-down seed import-ponds import-ponds-full import-ponds-rerun benchmark-import test test-unit test-integration test-web e2e lint typecheck format
setup:
	cd apps/api && python -m pip install -e '.[dev]'
	cd apps/web && npm ci
up:
	docker compose up --build

down:
	docker compose down -v
migrate:
	cd apps/api && alembic upgrade head
migrate-down:
	cd apps/api && alembic downgrade -1
seed:
	cd apps/api && python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --mode upsert --batch-size 100 --limit 100 --report ../../artifacts/import-sample.json
import-ponds:
	cd apps/api && python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --mode upsert --batch-size 1000 --limit 1000 --report ../../artifacts/import-sample.json
import-ponds-full:
	cd apps/api && python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --mode upsert --batch-size 5000 --report ../../artifacts/import-full.json
import-ponds-rerun:
	cd apps/api && python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --mode upsert --batch-size 5000 --report ../../artifacts/import-rerun.json
benchmark-import: import-ponds
	test -s artifacts/import-sample.json

test: test-unit test-integration test-web

test-unit:
	cd apps/api && pytest -q tests/test_api.py tests/test_risk.py tests/test_importer.py tests/test_bbox.py

test-integration:
	docker compose up -d db
	cd apps/api && DATABASE_URL=postgresql+psycopg://tameike:tameike@localhost:5432/tameike alembic upgrade head
	cd apps/api && DATABASE_URL=postgresql+psycopg://tameike:tameike@localhost:5432/tameike pytest -q tests/test_postgis_integration.py

test-web:
	cd apps/web && npm run typecheck && npm run lint && npm test

e2e:
	cd apps/web && npx playwright test
lint:
	cd apps/api && ruff check app tests
	cd apps/web && npm run lint -- --max-warnings=0

typecheck:
	cd apps/web && npm run typecheck

format:
	cd apps/api && ruff format app tests
