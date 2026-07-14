# R2 ledger import

Expected R2 keys:

- `raw/tameike_ichiranR8.xlsx`
- `imports/import-1000.json`
- `imports/import-10000.json`
- `imports/import-full.json`
- `imports/import-rerun.json`
- `imports/import-quality-summary.json`
- `reports/`
- `satellite/`

Use `scripts/r2_download_ledger.sh` and `scripts/r2_upload_import_results.sh`. The production import workflow downloads the ledger from R2 and runs the importer CLI against PostGIS from GitHub Actions; it does not import 160k rows through HTTP.
