# 0004 Real Excel schema

The R8 pond ledger is treated as a fixed 14-column source: 名称, 都道府県, 市区町村, 町域名、番地, 緯度, 分, 秒, 経度, 分2, 秒2, 堤高(m), 堤頂長(m), 総貯水量(千m3), 満水面積(km2). The importer uses an explicit mapping dictionary before any fallback logic, converts latitude and longitude independently from degree/minute/second, and stores both the original source payload and normalized payload.

Sentinel numeric values `0`, `9999`, and `9999.9` are preserved in `source_payload` but normalized to null and flagged in `quality_flags`.
