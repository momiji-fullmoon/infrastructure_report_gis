from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.models import Pond, RiskAssessment, DisasterEvent, RecommendedAction, Observation
from app.services.risk import assess_pond
from app.providers.satellite import NotConfiguredSatelliteProvider
from app.providers.simulation import SampleSimulationProvider

app = FastAPI(title='Tameike Resilience AI / Satellite PondWatch', version='0.2.0')
origins=[o.strip() for o in getattr(settings,'cors_allowed_origins','http://localhost:3000').split(',') if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

def _is_pg(db): return db.bind.dialect.name == 'postgresql'
def coords_expr(db):
    if _is_pg(db): return func.ST_X(Pond.__table__.c.location), func.ST_Y(Pond.__table__.c.location)
    return Pond.longitude, Pond.latitude

def parse_bbox(bbox):
    try: vals=[float(x) for x in bbox.split(',')]
    except Exception: raise HTTPException(422,'bbox must be minLon,minLat,maxLon,maxLat')
    if len(vals)!=4: raise HTTPException(422,'bbox requires four numbers')
    minx,miny,maxx,maxy=vals
    if minx>maxx or miny>maxy: raise HTTPException(422,'bbox min values must be <= max values')
    if not (122<=minx<=154 and 122<=maxx<=154 and 20<=miny<=46 and 20<=maxy<=46): raise HTTPException(422,'bbox must be a Japan non-antimeridian range')
    return vals

def risk_dict(r):
    return {'assessmentId':r.risk_assessment_id,'pondId':r.pond_id,'assessedAt':r.assessed_at,'hazard':r.hazard_score,'vulnerability':r.vulnerability_score,'exposure':r.exposure_score,'anomaly':r.anomaly_score,'uncertainty':r.uncertainty_score,'screeningScore':r.screening_score,'riskLevel':r.risk_level,'modelVersion':r.model_version,'evidence':r.evidence,'label':'リスクスクリーニングスコア（決壊確率ではありません）'}
def pond_dict(p, lon=None, lat=None, risk=None):
    lon = p.longitude if lon is None else lon; lat = p.latitude if lat is None else lat
    return {'pondId':p.pond_id,'name':p.name,'prefecture':p.prefecture,'municipality':p.municipality,'municipalityCode':p.municipality_code,'location':{'type':'Point','coordinates':[lon,lat]} if lat is not None and lon is not None else None,'coordinateQuality':p.coordinate_quality,'qualityFlags':p.quality_flags,'duplicateCandidate':p.duplicate_candidate,'damHeightM':p.dam_height_m,'crestLengthM':p.crest_length_m,'totalStorageThousandM3':p.total_storage_thousand_m3,'dataSource':p.data_source,'lastUpdatedAt':p.updated_at,'confidence':p.confidence,'risk':risk_dict(risk) if risk else None}

@app.get('/health')
def health(db:Session=Depends(get_db)):
    out={'status':'ok','database':'unknown','postgis':'unknown','satellite':'not_configured','simulation':'sample_mode'}
    try:
        db.execute(text('select 1')); out['database']='ok'
        if _is_pg(db): db.execute(text('select PostGIS_Version()')); out['postgis']='ok'
        else: out['postgis']='not_applicable_sqlite_unit_tests'
    except Exception:
        out['status']='error'; out['database']='error'; out['postgis']='error'
        return JSONResponse(out, status_code=503)
    return out

@app.get('/ponds')
def ponds(prefecture:str|None=None, municipality:str|None=None, risk_level:str|None=None, bbox:str|None=None, limit:int=Query(100, ge=1, le=5000), cursor:int=Query(0, ge=0), db:Session=Depends(get_db)):
    lon_e, lat_e = coords_expr(db)
    latest = select(RiskAssessment.pond_id, func.max(RiskAssessment.assessed_at).label('assessed_at')).group_by(RiskAssessment.pond_id).subquery()
    stmt=select(Pond, lon_e.label('lon'), lat_e.label('lat'), RiskAssessment).outerjoin(latest, latest.c.pond_id==Pond.pond_id).outerjoin(RiskAssessment, (RiskAssessment.pond_id==latest.c.pond_id) & (RiskAssessment.assessed_at==latest.c.assessed_at))
    if prefecture: stmt=stmt.where(Pond.prefecture==prefecture)
    if municipality: stmt=stmt.where(Pond.municipality==municipality)
    if risk_level: stmt=stmt.where(RiskAssessment.risk_level==risk_level)
    if bbox:
        minx,miny,maxx,maxy=parse_bbox(bbox)
        if _is_pg(db): stmt=stmt.where(text('ST_Intersects(pond.location, ST_MakeEnvelope(:minx,:miny,:maxx,:maxy,4326))')).params(minx=minx,miny=miny,maxx=maxx,maxy=maxy)
        else: stmt=stmt.where(Pond.longitude>=minx,Pond.longitude<=maxx,Pond.latitude>=miny,Pond.latitude<=maxy)
    total=db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows=db.execute(stmt.order_by(Pond.pond_id).offset(cursor).limit(limit)).all()
    out=[pond_dict(p,lon,lat,r) for p,lon,lat,r in rows]
    return {'items':out,'count':len(out),'nextCursor':cursor+len(rows) if cursor+len(rows)<total else None,'total':total,'dataSource':'ため池台帳+MVP baseline','modelVersion':'baseline-screening-v0.1'}
@app.get('/ponds/{pond_id}')
def pond(pond_id:str, db:Session=Depends(get_db)):
    p=db.get(Pond, pond_id)
    if not p: raise HTTPException(404,'pond not found')
    r=db.scalars(select(RiskAssessment).where(RiskAssessment.pond_id==pond_id).order_by(RiskAssessment.assessed_at.desc())).first(); return pond_dict(p,risk=r)
@app.get('/ponds/{pond_id}/risk')
def pond_risk(pond_id:str, db:Session=Depends(get_db)):
    p=db.get(Pond, pond_id)
    if not p: raise HTTPException(404,'pond not found')
    return risk_dict(db.scalars(select(RiskAssessment).where(RiskAssessment.pond_id==pond_id).order_by(RiskAssessment.assessed_at.desc())).first() or assess_pond(db,p))
@app.get('/ponds/{pond_id}/inspections')
def inspections(pond_id:str): return {'items':[],'status':'未連携'}
@app.get('/ponds/{pond_id}/observations')
def observations(pond_id:str, db:Session=Depends(get_db)): return {'items':[{'variable':o.variable,'observedAt':o.observed_at,'value':o.value,'unit':o.unit,'quality':o.quality} for o in db.scalars(select(Observation).where(Observation.pond_id==pond_id)).all()],'dataSource':'sample_or_sensor'}
@app.get('/ponds/{pond_id}/remote-sensing-assets')
def assets(pond_id:str): return NotConfiguredSatelliteProvider().search_assets(pond_id=pond_id)
@app.get('/disaster-events')
def events(db:Session=Depends(get_db)): return {'items':[{'eventId':e.event_id,'name':e.name,'eventType':e.event_type,'occurredAt':e.occurred_at,'status':e.status} for e in db.scalars(select(DisasterEvent)).all()]}
@app.post('/disaster-events')
def create_event(payload:dict, db:Session=Depends(get_db)):
    e=DisasterEvent(name=payload.get('name','災害イベント'), event_type=payload.get('eventType','heavy_rain'), area_geojson=payload.get('areaGeojson',{})); db.add(e); db.commit(); db.refresh(e); return {'eventId':e.event_id,'name':e.name,'targetPondCount':db.query(Pond).count()}
@app.post('/risk-assessments/run')
def run_risk(payload:dict, db:Session=Depends(get_db)):
    ids=payload.get('pondIds') or [p.pond_id for p in db.scalars(select(Pond).limit(200)).all()]
    return {'items':[risk_dict(assess_pond(db, db.get(Pond,i))) for i in ids if db.get(Pond,i)]}
@app.get('/risk-assessments/{assessment_id}')
def get_risk(assessment_id:str, db:Session=Depends(get_db)):
    r=db.get(RiskAssessment, assessment_id)
    if not r: raise HTTPException(404,'risk not found')
    return risk_dict(r)
@app.get('/recommended-actions')
def actions(db:Session=Depends(get_db)): return {'items':[{'actionId':a.action_id,'pondId':a.pond_id,'action':a.action,'priority':a.priority,'status':a.status} for a in db.scalars(select(RecommendedAction).order_by(RecommendedAction.priority)).all()]}
@app.post('/reports/generate')
def report(payload:dict): return {'status':'draft_created','trustedSourcesOnly':payload.get('trustedSourcesOnly',True),'content':'MVP report draft with evidence manifest'}
@app.get('/simulations/sample')
def sim_sample(): return SampleSimulationProvider().get_result()
