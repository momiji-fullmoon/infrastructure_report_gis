# Tameike Resilience AI / Satellite PondWatch

NEDO Space Data Challenge「テーマ2：インフラに係る防災・災害対応」向けのMVPです。衛星データ、ため池台帳、地形、気象、AI、物理シミュレーションを統合する将来構成を前提に、現時点では台帳取り込み、地図検索、詳細、災害イベント、説明可能なリスクスクリーニングを実装しています。

## 起動

```bash
cp .env.example .env
make setup
make migrate
make seed
make up
```

- Web UI: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

## 主要コマンド

```bash
make setup
make up
make down
make migrate
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
