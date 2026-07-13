# Full import benchmark

This branch includes reproducible benchmark artifacts. In this execution environment, the real ledger was verified with 100-row and 1,000-row dry-runs before database writes.

| run | processed | inserted | updated | skipped | failed | missing coordinates | duplicate candidates | elapsed | rows/sec | peak memory |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dry-run 100 | 100 | 0 | 0 | 100 | 0 | 1 | 0 | 16.349s | 6.12 | 41,121,522 bytes |
| dry-run 1,000 | 1,000 | 0 | 0 | 1,000 | 0 | 1 | 4 | 16.411s | 60.93 | 41,141,691 bytes |

Full PostGIS import commands are documented in `docs/runbooks/full-import.md` and write `artifacts/import-full.json` and `artifacts/import-rerun.json`.
