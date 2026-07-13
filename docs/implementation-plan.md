# Implementation plan/status

- Alembic/PostGIS初期マイグレーションを追加し、`create_all()` 起動時実行を廃止。
- ため池は `location geometry(Point,4326)` + GiST インデックスでBBox検索する。
- 台帳インポータはread-only Excel streaming、バッチUPSERT、冪等一意制約、レポート出力を実装。
- Next.jsは内部URLと公開URLを分離し、rewriteプロキシ経由でFastAPIへ接続する。
- 接続エラーは空データにせずエラーパネルで表示する。
