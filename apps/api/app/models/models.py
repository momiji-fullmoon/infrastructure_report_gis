import uuid
from datetime import datetime, timezone
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc)
def json_type(): return JSON().with_variant(JSONB, 'postgresql')

def pk(name='id'): return mapped_column(String().with_variant(UUID(as_uuid=False), 'postgresql'), primary_key=True, default=uid)

class Pond(Base):
    __tablename__='pond'; __table_args__=(UniqueConstraint('source_system','source_record_id',name='uq_pond_source_record'), Index('ix_pond_prefecture','prefecture'), Index('ix_pond_municipality','municipality'), Index('ix_pond_municipality_code','municipality_code'))
    pond_id:Mapped[str]=pk('pond_id')
    source_system:Mapped[str]=mapped_column(String,default='tameike_ichiranR8')
    source_record_id:Mapped[str|None]=mapped_column(String)
    name:Mapped[str]=mapped_column(String,index=True)
    normalized_name:Mapped[str|None]=mapped_column(String)
    prefecture:Mapped[str|None]=mapped_column(String); municipality:Mapped[str|None]=mapped_column(String); municipality_code:Mapped[str|None]=mapped_column(String)
    address:Mapped[str|None]=mapped_column(Text); latitude:Mapped[float|None]=mapped_column(Float); longitude:Mapped[float|None]=mapped_column(Float)
    coordinate_quality:Mapped[str]=mapped_column(String,default='unknown'); quality_flags:Mapped[dict]=mapped_column(json_type(),default=dict); duplicate_candidate:Mapped[bool]=mapped_column(Boolean,default=False)
    dam_height_m:Mapped[float|None]=mapped_column(Float); crest_length_m:Mapped[float|None]=mapped_column(Float); total_storage_thousand_m3:Mapped[float|None]=mapped_column(Float); full_water_area_km2:Mapped[float|None]=mapped_column(Float)
    source_payload:Mapped[dict]=mapped_column(json_type(),default=dict); normalized_payload:Mapped[dict]=mapped_column(json_type(),default=dict)
    confidence:Mapped[float]=mapped_column(Float,default=.5); data_source:Mapped[str]=mapped_column(String,default='ため池台帳')
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now); updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)
    risks=relationship('RiskAssessment',back_populates='pond')

class RiskAssessment(Base):
    __tablename__='risk_assessment'; __table_args__=(Index('ix_risk_assessment_pond_assessed','pond_id','assessed_at'),)
    risk_assessment_id:Mapped[str]=pk('risk_assessment_id'); pond_id:Mapped[str]=mapped_column(ForeignKey('pond.pond_id'),index=True); assessed_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    hazard_score:Mapped[float]=mapped_column(Float,default=0); vulnerability_score:Mapped[float]=mapped_column(Float,default=0); exposure_score:Mapped[float]=mapped_column(Float,default=0); anomaly_score:Mapped[float]=mapped_column(Float,default=0); uncertainty_score:Mapped[float]=mapped_column(Float,default=0); screening_score:Mapped[float]=mapped_column(Float,default=0)
    risk_level:Mapped[str]=mapped_column(String,default='low'); evidence:Mapped[dict]=mapped_column(json_type(),default=dict); model_version:Mapped[str]=mapped_column(String,default='baseline-screening-v0.1'); pond=relationship('Pond',back_populates='risks')

class DisasterEvent(Base):
    __tablename__='disaster_event'; event_id:Mapped[str]=pk('event_id'); name:Mapped[str]=mapped_column(String); event_type:Mapped[str]=mapped_column(String); occurred_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now); area_geojson:Mapped[dict]=mapped_column(json_type(),default=dict); status:Mapped[str]=mapped_column(String,default='active'); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Observation(Base):
    __tablename__='observation'; observation_id:Mapped[str]=pk('observation_id'); pond_id:Mapped[str]=mapped_column(ForeignKey('pond.pond_id'),index=True); variable:Mapped[str]=mapped_column(String,default='water_level'); observed_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now); value:Mapped[float|None]=mapped_column(Float); unit:Mapped[str|None]=mapped_column(String); quality:Mapped[str]=mapped_column(String,default='verified')
class RecommendedAction(Base):
    __tablename__='recommended_action'; action_id:Mapped[str]=pk('action_id'); pond_id:Mapped[str]=mapped_column(ForeignKey('pond.pond_id'),index=True); risk_assessment_id:Mapped[str|None]=mapped_column(ForeignKey('risk_assessment.risk_assessment_id')); action:Mapped[str]=mapped_column(String,default='現地確認'); reason:Mapped[str]=mapped_column(Text,default='MVP screening'); priority:Mapped[int]=mapped_column(Integer,default=3); status:Mapped[str]=mapped_column(String,default='proposed'); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)

def _simple(cls, table, pkname, pond=True):
    attrs={'__tablename__':table, pkname:pk(pkname), 'created_at':mapped_column(DateTime(timezone=True),default=now), 'updated_at':mapped_column(DateTime(timezone=True),default=now), 'source_system':mapped_column(String), 'data_quality':mapped_column(String,default='unknown'), 'metadata_json':mapped_column('metadata', json_type(), default=dict)}
    if pond: attrs['pond_id']=mapped_column(ForeignKey('pond.pond_id'), index=True)
    return type(cls,(Base,),attrs)
PondGeometry=_simple('PondGeometry','pond_geometry','pond_geometry_id')
Inspection=_simple('Inspection','inspection','inspection_id')
Defect=_simple('Defect','defect','defect_id')
Maintenance=_simple('Maintenance','maintenance','maintenance_id')
Sensor=_simple('Sensor','sensor','sensor_id')
WeatherEvent=_simple('WeatherEvent','weather_event','weather_event_id',False)
RemoteSensingAsset=_simple('RemoteSensingAsset','remote_sensing_asset','remote_sensing_asset_id')
SimulationRun=_simple('SimulationRun','simulation_run','simulation_run_id')
SimulationResult=_simple('SimulationResult','simulation_result','simulation_result_id')
AiPrediction=_simple('AiPrediction','ai_prediction','ai_prediction_id')
AuditLog=_simple('AuditLog','audit_log','audit_log_id',False)
ImportJob=_simple('ImportJob','import_job','import_job_id',False)
ImportCheckpoint=_simple('ImportCheckpoint','import_checkpoint','import_checkpoint_id',False)
