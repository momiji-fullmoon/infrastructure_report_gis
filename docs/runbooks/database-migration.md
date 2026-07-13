# Database migration runbook

- Upgrade: `make migrate` (`cd apps/api && alembic upgrade head`)
- Downgrade: `make migrate-down` (`alembic downgrade base`)
- PostGIS確認: `SELECT PostGIS_Version();`
- API起動時に `Base.metadata.create_all()` は実行しない。
- Docker Composeは `db healthy -> migrate completed -> api healthy -> web` の順で起動する。
