# Full import runbook

1. `cp .env.example .env`
2. `make up`
3. `make seed`（任意）
4. `make import-ponds-full`
5. `artifacts/import-full.json` で processed/success/failed/rowsPerSecond/peakMemoryBytes を確認
6. 同じコマンドを再実行し、`pond` 総件数が増えないことを確認

入力Excelは数式を評価せず `data_only=True` で読み込む。失敗行は最大100件の行番号とエラー種別のみ保存する。
