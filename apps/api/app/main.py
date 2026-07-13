from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import Base, engine, get_db
from app.models import models
from app.models.models import Pond, RiskAssessment, DisasterEvent, RecommendedAction, Observation
from app.services.risk import assess_pond
from app.providers.satellite import NotConfiguredSatelliteProvider
from app.providers.simulation import SampleSimulationProvider

Base.metadata.create_all(engine)
app = FastAPI(title="Tameike Resilience AI / Satellite PondWatch", version="0.1.0")

def pond_dict(p: Pond, risk: RiskAssessment|None=None):
    return {"pondId":p.pond_id,"name":p.name,"prefecture":p.prefecture,"municipality":p.municipality,"location":{"type":"Point","coordinates":[p.longitude,p.latitude]} if p.latitude and p.longitude else None,"coordinateQuality":p.coordinate_quality,"qualityFlags":p.quality_flags,"duplicateCandidate":p.duplicate_candidate,"damHeightM":p.dam_height_m,"crestLengthM":p.crest_length_m,"totalStorageThousandM3":p.total_storage_thousand_m3,"dataSource":p.data_source,"lastUpdatedAt":p.updated_at,"confidence":p.confidence,"risk": risk_dict(risk) if risk else None}
def risk_dict(r):
    return {"assessmentId":r.risk_assessment_id,"pondId":r.pond_id,"assessedAt":r.assessed_at,"hazard":r.hazard_score,"vulnerability":r.vulnerability_score,"exposure":r.exposure_score,"anomaly":r.anomaly_score,"uncertainty":r.uncertainty_score,"screeningScore":r.screening_score,"riskLevel":r.risk_level,"modelVersion":r.model_version,"evidence":r.evidence,"label":"リスクスクリーニングスコア（決壊確率ではありません）"}

@app.get("/health")
def health(): return {"status":"ok","satellite":"not_configured","simulation":"sample_mode"}
@app.get("/ponds")
def ponds(prefecture:str|None=None, municipality:str|None=None, risk_level:str|None=None, bbox:str|None=None, limit:int=1000, db:Session=Depends(get_db)):
    stmt=select(Pond)
    if prefecture: stmt=stmt.where(Pond.prefecture==prefecture)
    if municipality: stmt=stmt.where(Pond.municipality==municipality)
    items=db.scalars(stmt.limit(limit)).all()
    if bbox:
        minx,miny,maxx,maxy=map(float,bbox.split(',')); items=[p for p in items if p.longitude and p.latitude and minx<=p.longitude<=maxx and miny<=p.latitude<=maxy]
    out=[]
    for p in items:
        r=db.scalars(select(RiskAssessment).where(RiskAssessment.pond_id==p.pond_id).order_by(RiskAssessment.assessed_at.desc())).first()
        if risk_level and (not r or r.risk_level!=risk_level): continue
        out.append(pond_dict(p,r))
    return {"items":out,"count":len(out),"dataSource":"ため池台帳+MVP baseline","modelVersion":"baseline-screening-v0.1"}
@app.get("/ponds/{pond_id}")
def pond(pond_id:str, db:Session=Depends(get_db)):
    p=db.get(Pond, pond_id)
    if not p: raise HTTPException(404)
    r=db.scalars(select(RiskAssessment).where(RiskAssessment.pond_id==pond_id).order_by(RiskAssessment.assessed_at.desc())).first()
    return pond_dict(p,r)
@app.get("/ponds/{pond_id}/risk")
def pond_risk(pond_id:str, db:Session=Depends(get_db)):
    p=db.get(Pond, pond_id)
    if not p: raise HTTPException(404)
    r=db.scalars(select(RiskAssessment).where(RiskAssessment.pond_id==pond_id).order_by(RiskAssessment.assessed_at.desc())).first() or assess_pond(db,p)
    return risk_dict(r)
@app.get("/ponds/{pond_id}/inspections")
def inspections(pond_id:str): return {"items":[],"status":"未連携"}
@app.get("/ponds/{pond_id}/observations")
def observations(pond_id:str, db:Session=Depends(get_db)):
    return {"items":[{"variable":o.variable,"observedAt":o.observed_at,"value":o.value,"unit":o.unit,"quality":o.quality} for o in db.scalars(select(Observation).where(Observation.pond_id==pond_id)).all()],"dataSource":"sample_or_sensor"}
@app.get("/ponds/{pond_id}/remote-sensing-assets")
def assets(pond_id:str): return NotConfiguredSatelliteProvider().search_assets(pond_id=pond_id)
@app.get("/disaster-events")
def events(db:Session=Depends(get_db)): return {"items":[e.__dict__ for e in db.scalars(select(DisasterEvent)).all()]}
@app.post("/disaster-events")
def create_event(payload:dict, db:Session=Depends(get_db)):
    e=DisasterEvent(name=payload.get("name","災害イベント"), event_type=payload.get("eventType","heavy_rain"), area_geojson=payload.get("areaGeojson",{})); db.add(e); db.commit(); db.refresh(e); return {"eventId":e.event_id,"name":e.name,"targetPondCount":db.query(Pond).count()}
@app.post("/risk-assessments/run")
def run_risk(payload:dict, db:Session=Depends(get_db)):
    ids=payload.get("pondIds") or [p.pond_id for p in db.scalars(select(Pond).limit(200)).all()]
    return {"items":[risk_dict(assess_pond(db, db.get(Pond,i))) for i in ids if db.get(Pond,i)]}
@app.get("/risk-assessments/{assessment_id}")
def get_risk(assessment_id:str, db:Session=Depends(get_db)):
    r=db.get(RiskAssessment, assessment_id)
    if not r: raise HTTPException(404)
    return risk_dict(r)
@app.get("/recommended-actions")
def actions(db:Session=Depends(get_db)): return {"items":[a.__dict__ for a in db.scalars(select(RecommendedAction).order_by(RecommendedAction.priority)).all()]}
@app.post("/reports/generate")
def report(payload:dict): return {"status":"draft_created","trustedSourcesOnly":payload.get("trustedSourcesOnly",True),"content":"MVP report draft with evidence manifest"}
@app.get("/simulations/sample")
def sim_sample(): return SampleSimulationProvider().get_result()
