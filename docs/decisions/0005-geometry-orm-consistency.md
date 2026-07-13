# 0005 Geometry ORM consistency

`pond.location` is the authoritative spatial point in EPSG:4326 and is mapped with GeoAlchemy2 `Geometry(POINT, 4326)`. `latitude` and `longitude` remain as compatibility columns during migration only. Imports set both compatibility columns and `location`; API responses derive coordinates from `ST_X(location)` and `ST_Y(location)` on PostgreSQL.

GiST indexes and schema changes are managed only by Alembic. Application startup must not call `Base.metadata.create_all()`.
