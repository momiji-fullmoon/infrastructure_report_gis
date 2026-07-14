# Tameike Resilience AI / Satellite PondWatch

NEDO Space Data Challenge「テーマ2：インフラに係る防災・災害対応」向けのMVPです。衛星データ、ため池台帳、地形、気象、AI、物理シミュレーションを統合する将来構成を前提に、現時点では台帳取り込み、地図検索、詳細、災害イベント、説明可能なリスクスクリーニングを実装しています。

## Docker なしのローカル起動手順（SQLite）

Docker を使わずに、ホスト上の Python / Node.js だけで API と Web UI を起動できます。この手順では `apps/api/tameike.db` の SQLite DB を作成し、サンプルデータを投入します。

```bash
git clone https://github.com/momiji-fullmoon/infrastructure_report_gis.git
cd infrastructure_report_gis
make setup-local
```

API と Web UI は別々のターミナルで起動してください。

```bash
make api-local
```

```bash
make web-local
```

- Web UI: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ローカル SQLite DB: `apps/api/tameike.db`

SQLite 起動では PostGIS カラムを通常のテキストカラムとして作成し、緯度経度カラムで地図検索します。本番相当の PostGIS 動作確認は Docker Compose または外部 PostgreSQL/PostGIS を使ってください。

## Docker Compose 推奨起動手順（空DB）

Docker Compose は `.env` を読み込みます。`.env.example` はテンプレート専用です。

```bash
git clone https://github.com/momiji-fullmoon/infrastructure_report_gis.git
cd infrastructure_report_gis
cp .env.example .env
docker compose down -v
docker compose up --build -d
docker compose ps
curl --fail http://localhost:8000/health
curl --fail http://localhost:3000/
make seed
```

Compose の `migrate` サービスが Alembic を実行するため、通常起動時に `make migrate` は不要です。ホストから手動でマイグレーションする場合のみ次を実行してください。

```bash
cd apps/api
DATABASE_URL=postgresql+psycopg://tameike:tameike@localhost:5432/tameike alembic upgrade head
```

- Web UI: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Docker 内 DATABASE_URL: `postgresql+psycopg://tameike:tameike@db:5432/tameike`
- ホスト上 DATABASE_URL: `postgresql+psycopg://tameike:tameike@localhost:5432/tameike`

## 主要コマンド

```bash
make setup
make up
make down
make seed
make import-ponds
make test
make lint
make format
make e2e
```

## 台帳インポート

```bash
cd apps/api
python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --limit 1000
```

インポートでは元値を `source_payload`、正規化値を `normalized_payload`、品質問題を `quality_flags` に保持します。`0`、`9999`、`9999.9` は欠損候補として扱い、重複候補はフラグ付けのみで自動統合しません。

## MVP API

- `GET /health`
- `GET /ponds`
- `GET /ponds/{pond_id}`
- `GET /ponds/{pond_id}/risk`
- `GET /ponds/{pond_id}/inspections`
- `GET /ponds/{pond_id}/observations`
- `GET /ponds/{pond_id}/remote-sensing-assets`
- `GET/POST /disaster-events`
- `POST /risk-assessments/run`
- `GET /risk-assessments/{assessment_id}`
- `GET /recommended-actions`
- `POST /reports/generate`

## 未接続範囲

- 衛星API: Providerインターフェースのみ。未設定時は `not_configured` を返します。
- 物理シミュレータ: Providerインターフェースとサンプル結果のみ。実行済みとは表示しません。
- PLATEAU / 3D Tiles: 画面はサンプルモードを前提に拡張可能です。
- 認証・RBAC: ロール設計を想定していますが、MVPでは外部認証基盤未接続です。

## リスク評価

`hazard`、`vulnerability`、`exposure`、`anomaly`、`uncertainty` を0〜1に正規化し、設定可能な重みで合成します。これは「リスクスクリーニングスコア」であり、決壊確率ではありません。

## Cloudflare deployment status

- Cloudflare deployment configuration: implemented
- Cloudflare production deployment: not yet verified
- Full production import: not yet run

### Local development

For Docker-free local development, use `make setup-local`, then run `make api-local` and `make web-local` in separate terminals. This path uses SQLite at `apps/api/tameike.db` and sample data. Docker Compose remains available for PostGIS parity: PostGIS container, FastAPI container, and Next.js container. Use `make up`, `make migrate`, and `make seed` (`seed-docker`) for container-based data loading. Use `make seed-host` only when intentionally writing from the host to a configured PostGIS database.

### Cloudflare architecture

The planned production architecture is OpenNext on Cloudflare Workers for the web app, an API Worker backed by a Cloudflare Container running FastAPI, managed PostgreSQL/PostGIS outside Cloudflare, and R2 for ledgers/import artifacts. D1 is not used for PostGIS data.

### First deployment

See `docs/deployment/cloudflare-first-deploy.md`. Deployment is manual through the `Deploy Cloudflare production` GitHub Actions workflow until real production smoke tests pass.

### Required secrets

See `docs/deployment/cloudflare-secrets.md`. Secret values must be configured in Wrangler/GitHub environments, not committed.

### Production migration

Alembic migrations run in the deployment workflow before API deployment. The API Container does not run migrations at startup.

### Production import

Use the manual `Import production ledger` workflow. It downloads the Excel ledger from R2 and runs the importer CLI on the GitHub Actions runner against PostGIS.

### Smoke tests

Production smoke checks verify API `/health/ready`, API `/ponds?limit=1`, Web `/`, Web `/map`, and Web proxy `/api/backend/*` endpoints.

### Known limitations

Cloudflare production deployment, custom domains, and the full production import require real Cloudflare, R2, and managed PostGIS credentials. The default MapLibre fallback style is for development; configure `NEXT_PUBLIC_MAP_STYLE_URL` for production.
