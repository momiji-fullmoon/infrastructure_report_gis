import math, re
from pathlib import Path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from app.models.models import Pond

MISSING = {0, 9999, 9999.9}
def norm_text(v): return str(v).strip().replace(" ", "") if v is not None else None
def maybe_float(v):
    try:
        f=float(str(v).replace(",","")); return None if f in MISSING or math.isnan(f) else f
    except Exception: return None
def dms_to_decimal(v):
    if v is None: return None
    if isinstance(v,(int,float)): return float(v) if abs(float(v))<=180 and float(v)!=0 else None
    s=str(v).strip();
    try: return float(s)
    except Exception: pass
    nums=[float(x) for x in re.findall(r"\d+(?:\.\d+)?", s)]
    if not nums: return None
    deg=nums[0]; minutes=nums[1] if len(nums)>1 else 0; sec=nums[2] if len(nums)>2 else 0
    return deg + minutes/60 + sec/3600

def pick(row, names):
    for n in names:
        if n in row and row[n] not in (None, ""): return row[n]
    return None

def import_excel(db: "Session", input_path: str, limit: int|None=None):
    from app.models.models import Pond
    from openpyxl import load_workbook
    wb=load_workbook(input_path, read_only=True, data_only=True); ws=wb[wb.sheetnames[0]]
    headers=[str(c).strip() if c is not None else f"col{i}" for i,c in enumerate(next(ws.iter_rows(values_only=True)))]
    stats={"success":0,"failed":0,"missing":0,"anomaly":0,"duplicate_candidates":0}
    seen={}
    for idx, vals in enumerate(ws.iter_rows(values_only=True), start=2):
        if limit and stats["success"]>=limit: break
        row=dict(zip(headers, vals)); name=norm_text(pick(row,["ため池名","名称","name","ため池名称"])) or f"unknown-{idx}"
        lat=dms_to_decimal(pick(row,["緯度","lat","latitude"])); lon=dms_to_decimal(pick(row,["経度","lon","longitude"]))
        flags=[]
        if lat is None or lon is None: flags.append("coordinate_missing"); stats["missing"]+=1
        if lat and not (20<=lat<=46) or lon and not (122<=lon<=154): flags.append("coordinate_out_of_range"); stats["anomaly"]+=1
        key=(round(lat or 0,6), round(lon or 0,6), norm_text(pick(row,["市町村","市区町村","municipality"])))
        dup= key in seen and lat is not None and lon is not None
        if dup: flags.append("duplicate_candidate"); stats["duplicate_candidates"]+=1
        seen[key]=name
        p=Pond(source_record_id=str(idx), name=name, normalized_name=name, prefecture=norm_text(pick(row,["都道府県","県名","prefecture"])), municipality=norm_text(pick(row,["市町村","市区町村","municipality"])), latitude=lat, longitude=lon, coordinate_quality="surveyed" if lat and lon else "unknown", quality_flags={"issues":flags}, duplicate_candidate=dup, dam_height_m=maybe_float(pick(row,["堤高","dam_height_m"])), crest_length_m=maybe_float(pick(row,["堤頂長","crest_length_m"])), total_storage_thousand_m3=maybe_float(pick(row,["総貯水量","total_storage_thousand_m3"])), full_water_area_km2=maybe_float(pick(row,["満水面積","full_water_area_km2"])), source_payload={k:(str(v) if v is not None else None) for k,v in row.items()}, normalized_payload={"name":name,"lat":lat,"lon":lon})
        db.add(p); stats["success"]+=1
    db.commit(); return stats
