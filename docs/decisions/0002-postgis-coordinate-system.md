# ADR 0002: PostGIS coordinate system

全国ため池台帳の永続保存座標系は EPSG:4326 とする。固定の平面直角座標系 EPSG:6677 は全国を単一面で扱う用途に適さないため使用しない。距離・面積解析では対象地域に応じた投影座標系へ `ST_Transform` する。

緯度・経度カラムは互換読み取り用として残し、正の空間検索カラムは `pond.location geometry(Point,4326)` とする。二重管理の不整合対策は、インポータとシードなどアプリケーション層が Geometry を更新し、移行期の `latitude` / `longitude` は表示互換に限定する方式を採用した。将来は生成列またはビューへ移行する。

UUID は既存APIが文字列UUIDを返しているため、モデル上は文字列互換を維持しつつ PostgreSQL では native UUID を使う。
