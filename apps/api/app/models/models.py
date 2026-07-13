import uuid
from datetime import datetime, timezone
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc)

class Pond(Base):
    __tablename__ = "pond"
    pond_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    source_system: Mapped[str] = mapped_column(String, default="tameike_ichiranR8")
    source_record_id: Mapped[str | None] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, index=True)
    normalized_name: Mapped[str | None] = mapped_column(String)
    prefecture: Mapped[str | None] = mapped_column(String, index=True)
    municipality: Mapped[str | None] = mapped_column(String, index=True)
    municipality_code: Mapped[str | None] = mapped_column(String, index=True)
    address: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    coordinate_quality: Mapped[str] = mapped_column(String, default="unknown")
    quality_flags: Mapped[dict] = mapped_column(JSON, default=dict)
    duplicate_candidate: Mapped[bool] = mapped_column(Boolean, default=False)
    dam_height_m: Mapped[float | None] = mapped_column(Float)
    crest_length_m: Mapped[float | None] = mapped_column(Float)
    total_storage_thousand_m3: Mapped[float | None] = mapped_column(Float)
    full_water_area_km2: Mapped[float | None] = mapped_column(Float)
    source_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    normalized_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    data_source: Mapped[str] = mapped_column(String, default="ため池台帳")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    risks = relationship("RiskAssessment", back_populates="pond")

class Observation(Base):
    __tablename__ = "observation"
    observation_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    pond_id: Mapped[str] = mapped_column(ForeignKey("pond.pond_id"))
    variable: Mapped[str] = mapped_column(String)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    value: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String)
    quality: Mapped[str] = mapped_column(String, default="verified")

class DisasterEvent(Base):
    __tablename__ = "disaster_event"
    event_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String)
    event_type: Mapped[str] = mapped_column(String)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    area_geojson: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class RiskAssessment(Base):
    __tablename__ = "risk_assessment"
    risk_assessment_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    pond_id: Mapped[str] = mapped_column(ForeignKey("pond.pond_id"), index=True)
    assessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    hazard_score: Mapped[float] = mapped_column(Float)
    vulnerability_score: Mapped[float] = mapped_column(Float)
    exposure_score: Mapped[float] = mapped_column(Float)
    anomaly_score: Mapped[float] = mapped_column(Float)
    uncertainty_score: Mapped[float] = mapped_column(Float)
    screening_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    model_version: Mapped[str] = mapped_column(String)
    pond = relationship("Pond", back_populates="risks")

class RecommendedAction(Base):
    __tablename__ = "recommended_action"
    action_id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    pond_id: Mapped[str] = mapped_column(ForeignKey("pond.pond_id"))
    risk_assessment_id: Mapped[str | None] = mapped_column(ForeignKey("risk_assessment.risk_assessment_id"))
    action: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    status: Mapped[str] = mapped_column(String, default="proposed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

# Requirement entities (minimal MVP schema)
for _name in ["pond_component","structural_spec","inspection","defect","maintenance","sensor","weather_event","remote_sensing_asset","simulation_run","simulation_result","ai_prediction","audit_log","pond_geometry"]:
    globals()["_"+_name] = type(_name.title().replace("_", ""), (Base,), {"__tablename__": _name, "id": mapped_column(String, primary_key=True, default=uid), "payload": mapped_column(JSON, default=dict), "created_at": mapped_column(DateTime(timezone=True), default=now)})
