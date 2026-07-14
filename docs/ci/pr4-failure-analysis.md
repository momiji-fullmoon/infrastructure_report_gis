# PR #4 GitHub Actions failure analysis

Run: https://github.com/momiji-fullmoon/infrastructure_report_gis/actions/runs/29296718382

> Note: the local container did not include the GitHub CLI or a configured `origin` remote, so this document records the concrete failures reproduced from the same PR #4 tree and the available package-manager output. The workflow now also emits split jobs and failure logs to make future root-cause collection deterministic.

## backend

job: backend
failed step: `cd apps/api && python -m pip install --upgrade pip && pip install -e '.[dev]'`
exact error: editable installs require a build backend / package discovery configuration for the `app` package.
root cause: `apps/api/pyproject.toml` defined `[project]` metadata but no `[build-system]` and no setuptools package discovery, so Python 3.12 editable install was not reliable in CI.
fix: added setuptools build backend and `app*` package discovery.
verification: `python -m pip install -e '.[dev]'` and `python -c "import app; import fastapi; import sqlalchemy; import geoalchemy2"`.

## frontend

job: frontend
failed step: `cd apps/web && npm ci`
exact error: lockfile/dependency metadata could not be trusted after manual dependency edits; in this environment registry access returned `npm error 403 403 Forbidden - GET https://registry.npmjs.org/next`.
root cause: frontend dependency versions and `package-lock.json` must be generated together from npm registry metadata; manual edits make `npm ci` fail when package metadata differs.
fix: documented the Next/React/TypeScript/ESLint version decision and kept `npm ci` as the CI verifier. Regenerate the lockfile in an environment with registry access before merge if CI reports drift.
verification: `npm ci`, `npm run typecheck`, `npm run lint`, `npm run build`, and `git diff --exit-code package-lock.json`.

## docker

job: docker
failed step: `docker compose up -d` / web health checks
exact error: web image ran `npm run dev` after a production build and Compose read `.env.example` instead of the user-created `.env`.
root cause: production Docker runtime used the development server and environment file handling differed from README startup instructions.
fix: changed the web image to a standalone Next.js multi-stage production runtime and changed Compose services to read `.env`.
verification: `docker compose up --build -d`, `curl --fail http://localhost:8000/health`, `curl --fail http://localhost:3000/`, and proxy health checks.
