# ADR 0003: Import strategy

Excel は `openpyxl(load_workbook(..., read_only=True, data_only=True))` でストリーミング読込する。通常経路は SQLAlchemy Core の PostgreSQL `INSERT ... ON CONFLICT (source_system, source_record_id) DO UPDATE` バッチUPSERTで、ORMの1件ずつ `db.add()` は使わない。

COPY + staging はさらに高速化できるが、MVPでは品質フラグ、失敗行サンプル、SQLite単体テスト互換、実装リスクのバランスから Core バッチUPSERTを採用した。冪等性は `(source_system, source_record_id)` 一意制約とデフォルト `upsert` で担保する。動作しない `--resume` オプションは削除し、先頭から安全に再実行できるUPSERT方式に統一する。
