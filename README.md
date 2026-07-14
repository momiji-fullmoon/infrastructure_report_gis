# Tameike Resilience AI / Satellite PondWatch

NEDO Space Data Challenge「テーマ2：インフラに係る防災・災害対応」向けのMVPです。衛星データ、ため池台帳、地形、気象、AI、物理シミュレーションを統合する将来構成を前提に、現時点では台帳取り込み、地図検索、詳細、災害イベント、説明可能なリスクスクリーニングを実装しています。

## 推奨起動手順（空DB）

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
