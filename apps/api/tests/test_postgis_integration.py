import os
import subprocess
import pytest
from sqlalchemy import create_engine, text

@pytest.mark.skipif('DATABASE_URL' not in os.environ, reason='PostGIS DATABASE_URL not configured')
def test_postgis_migration_and_spatial_query():
    url=os.environ['DATABASE_URL']; subprocess.run(['alembic','upgrade','head'], cwd='.', check=True)
    engine=create_engine(url)
    with engine.begin() as c:
        assert c.scalar(text('select PostGIS_Version()'))
        assert c.scalar(text("select count(*) from pg_indexes where indexname='pond_location_gix'")) == 1
        c.execute(text("insert into pond(source_system,source_record_id,name,prefecture,municipality,latitude,longitude,location) values('test','1','境界池','栃木県','宇都宮市',36,139,ST_SetSRID(ST_MakePoint(139,36),4326)) on conflict do nothing"))
        assert c.scalar(text("select count(*) from pond where ST_Intersects(location, ST_MakeEnvelope(139,36,140,37,4326))")) >= 1
        c.execute(text("insert into pond(source_system,source_record_id,name,source_payload) values('test','json','JSON池','{}') on conflict do nothing"))
    subprocess.run(['alembic','downgrade','base'], cwd='.', check=True)
    subprocess.run(['alembic','upgrade','head'], cwd='.', check=True)
