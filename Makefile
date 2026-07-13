setup:
	cd apps/api && python -m pip install -e '.[dev]'
	cd apps/web && npm install
up:
	docker compose up --build
down:
	docker compose down
migrate:
	cd apps/api && python -c "from app.db.session import Base,engine; from app.models import models; Base.metadata.create_all(engine); print('migrated')"
seed:
	cd apps/api && python -m scripts.seed_sample
import-ponds:
	cd apps/api && python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --limit 1000
test:
	cd apps/api && pytest
lint:
	cd apps/api && ruff check app tests
format:
	cd apps/api && ruff format app tests
e2e:
	cd apps/web && npx playwright test
