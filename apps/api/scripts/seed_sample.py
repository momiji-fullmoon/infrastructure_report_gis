from datetime import datetime, timezone, timedelta
from app.db.session import SessionLocal
from app.models.models import Pond, Observation, DisasterEvent
from app.services.risk import assess_pond
with SessionLocal() as db:
    if not db.query(Pond).first():
        for i in range(20):
            p=Pond(name=f"サンプルため池{i+1}", prefecture="栃木県", municipality="宇都宮市", latitude=36.5+i*0.01, longitude=139.8+i*0.01, coordinate_quality="estimated" if i%5==0 else "map_selected", dam_height_m=5+i%8, crest_length_m=80+i*3, total_storage_thousand_m3=50+i*10, source_payload={"sample":True})
            db.add(p); db.flush()
            db.add(Observation(pond_id=p.pond_id, variable="water_level", observed_at=datetime.now(timezone.utc)-timedelta(hours=i), value=1.2+i/20, unit="m"))
            assess_pond(db,p)
        db.add(DisasterEvent(name="サンプル豪雨イベント", event_type="heavy_rain"))
        db.commit()
print("seeded sample data")
