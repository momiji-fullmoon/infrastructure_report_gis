"""initial PostGIS schema"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision='0001_initial_postgis'; down_revision=None; branch_labels=None; depends_on=None
JSONB=postgresql.JSONB

def jcol(name, nullable=False): return sa.Column(name, JSONB, nullable=nullable, server_default=sa.text("'{}'::jsonb"))
def ts(name): return sa.Column(name, sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
def uuid_pk(name): return sa.Column(name, postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()'))

def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')
    op.create_table('pond', uuid_pk('pond_id'), sa.Column('source_system',sa.String(),nullable=False), sa.Column('source_record_id',sa.String()), sa.Column('name',sa.String(),nullable=False), sa.Column('normalized_name',sa.String()), sa.Column('prefecture',sa.String()), sa.Column('municipality',sa.String()), sa.Column('municipality_code',sa.String()), sa.Column('address',sa.Text()), sa.Column('latitude',sa.Float()), sa.Column('longitude',sa.Float()), sa.Column('location', sa.Text()), sa.Column('coordinate_quality',sa.String(),server_default='unknown',nullable=False), jcol('quality_flags'), sa.Column('duplicate_candidate',sa.Boolean(),server_default='false',nullable=False), sa.Column('dam_height_m',sa.Float()), sa.Column('crest_length_m',sa.Float()), sa.Column('total_storage_thousand_m3',sa.Float()), sa.Column('full_water_area_km2',sa.Float()), jcol('source_payload'), jcol('normalized_payload'), sa.Column('confidence',sa.Float(),server_default='0.5',nullable=False), sa.Column('data_source',sa.String(),server_default='ため池台帳',nullable=False), ts('created_at'), ts('updated_at'), sa.UniqueConstraint('source_system','source_record_id', name='uq_pond_source_record'))
    op.execute('ALTER TABLE pond ALTER COLUMN location TYPE geometry(Point,4326) USING CASE WHEN location IS NULL THEN NULL ELSE ST_GeomFromText(location,4326) END')
    for c in ['prefecture','municipality','municipality_code']: op.create_index(f'ix_pond_{c}','pond',[c])
    op.create_index('pond_location_gix','pond',['location'],postgresql_using='gist')
    op.execute("UPDATE pond SET location=ST_SetSRID(ST_MakePoint(longitude, latitude),4326) WHERE longitude IS NOT NULL AND latitude IS NOT NULL AND location IS NULL")
    # named MVP tables
    op.create_table('pond_geometry', uuid_pk('pond_geometry_id'), sa.Column('pond_id',postgresql.UUID(as_uuid=False),sa.ForeignKey('pond.pond_id'),nullable=False), sa.Column('geometry_type',sa.String(),nullable=False,server_default='outline'), sa.Column('geom',sa.Text()), sa.Column('source_system',sa.String()), jcol('metadata'), ts('created_at'))
    op.execute('ALTER TABLE pond_geometry ALTER COLUMN geom TYPE geometry(Geometry,4326) USING CASE WHEN geom IS NULL THEN NULL ELSE ST_GeomFromText(geom,4326) END')
    tables=['inspection','defect','maintenance','sensor','observation','weather_event','disaster_event','remote_sensing_asset','simulation_run','simulation_result','risk_assessment','ai_prediction','recommended_action','audit_log','import_job','import_checkpoint']
    for t in tables:
        cols=[uuid_pk(f'{t}_id'), ts('created_at'), ts('updated_at'), sa.Column('source_system',sa.String()), sa.Column('data_quality',sa.String(),server_default='unknown',nullable=False), jcol('metadata')]
        if t not in ['weather_event','disaster_event','audit_log','import_job','import_checkpoint']:
            cols.insert(1, sa.Column('pond_id',postgresql.UUID(as_uuid=False),sa.ForeignKey('pond.pond_id')))
        op.create_table(t,*cols)
    op.add_column('risk_assessment', sa.Column('assessed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False));
    for c in ['hazard_score','vulnerability_score','exposure_score','anomaly_score','uncertainty_score','screening_score']: op.add_column('risk_assessment', sa.Column(c, sa.Float(), server_default='0', nullable=False))
    op.add_column('risk_assessment', sa.Column('risk_level', sa.String(), server_default='low', nullable=False)); op.add_column('risk_assessment', sa.Column('model_version', sa.String(), server_default='baseline-screening-v0.1', nullable=False)); op.add_column('risk_assessment', sa.Column('evidence', JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False))
    op.add_column('observation', sa.Column('variable', sa.String(), server_default='water_level', nullable=False)); op.add_column('observation', sa.Column('observed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)); op.add_column('observation', sa.Column('value', sa.Float())); op.add_column('observation', sa.Column('unit', sa.String())); op.add_column('observation', sa.Column('quality', sa.String(), server_default='verified', nullable=False))
    op.add_column('disaster_event', sa.Column('name', sa.String(), server_default='災害イベント', nullable=False)); op.add_column('disaster_event', sa.Column('event_type', sa.String(), server_default='heavy_rain', nullable=False)); op.add_column('disaster_event', sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)); op.add_column('disaster_event', sa.Column('area_geojson', JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False)); op.add_column('disaster_event', sa.Column('status', sa.String(), server_default='active', nullable=False))
    op.add_column('recommended_action', sa.Column('risk_assessment_id', postgresql.UUID(as_uuid=False), sa.ForeignKey('risk_assessment.risk_assessment_id'))); op.add_column('recommended_action', sa.Column('action', sa.String(), server_default='現地確認', nullable=False)); op.add_column('recommended_action', sa.Column('reason', sa.Text(), server_default='MVP screening', nullable=False)); op.add_column('recommended_action', sa.Column('priority', sa.Integer(), server_default='3', nullable=False)); op.add_column('recommended_action', sa.Column('status', sa.String(), server_default='proposed', nullable=False))
    for t in ['pond_geometry','inspection','defect','maintenance','sensor','observation','remote_sensing_asset','simulation_run','simulation_result','risk_assessment','ai_prediction','recommended_action']: op.create_index(f'ix_{t}_pond_id',t,['pond_id'])
    op.create_index('ix_risk_assessment_pond_assessed','risk_assessment',['pond_id','assessed_at'])

def downgrade():
    for t in ['import_checkpoint','import_job','audit_log','recommended_action','ai_prediction','risk_assessment','simulation_result','simulation_run','remote_sensing_asset','disaster_event','weather_event','observation','sensor','maintenance','defect','inspection','pond_geometry','pond']:
        op.drop_table(t)
