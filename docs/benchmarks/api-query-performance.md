# API query performance

測定対象:

- 都道府県絞り込み: `GET /ponds?prefecture=栃木県&limit=1000`
- BBox検索: `GET /ponds?bbox=139,36,140,37&limit=1000`
- 詳細取得: `GET /ponds/{pondId}`
- 最新リスク取得: `GET /ponds/{pondId}/risk`
- 1,000件ページ取得: `GET /ponds?limit=1000`

確認インデックス:

- `pond.location` GiST: `pond_location_gix`
- `pond.prefecture`, `pond.municipality`, `pond.municipality_code`
- `risk_assessment(pond_id, assessed_at)`
- `(source_system, source_record_id)` unique

ローカル測定は `make benchmark-api` またはcurl + `time` で実施する。通常検索とBBox検索は2秒以内、詳細は500ms以内を目標とする。
