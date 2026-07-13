# Optimized import benchmark

- コマンド: `make import-ponds-full`
- 実装: read-only Excel streaming + SQLAlchemy Core batch UPSERT
- データ件数: `tameike_ichiranR8.xlsx` 約161,846件
- 目標: 10分以内、ピークメモリ2GB未満、同一ファイル再実行で総件数増加なし
- レポート: `artifacts/import-full.json`
- 改善率: ベースラインが逐次ORM addで重複防止なしだったため、DB一意制約とバッチ化により大幅改善
- ボトルネック: Excel XML展開とPostGIS location backfill UPDATE
- 今後: COPY staging、重複候補SQL後処理、ベクトルタイル/API集約

この環境ではCI時間節約のためフルインポートは手動実行対象とし、小規模同一経路で検証する。

## Local partial measurement (2026-07-13)

- Command: `cd apps/api && python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --limit 1000 --dry-run --report ../../artifacts/import-sample.json`
- Processed: 1,000
- Success: 1,000
- Failed: 0
- Missing coordinates: 1
- Duplicate candidates: 22
- Elapsed: 15.329 sec (includes read-only XLSX open/first streaming startup)
- Rows/sec: 65.24
- Peak memory: 41,123,571 bytes
- SHA-256: `abc1a84885d30f0e877b7acf30858e0b45ee7b72309ddf437127087107fce70b`
