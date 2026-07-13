# Docker startup

Startup order is `db healthy -> migrate completed successfully -> api healthy -> web healthy`. The API image includes `alembic.ini`, `alembic/`, `app/`, and `scripts/` so `docker compose run --rm migrate alembic upgrade head` works in the container.
