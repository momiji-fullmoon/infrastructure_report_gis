import hashlib
import math
import os
import platform
import re
import time
import tracemalloc
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import insert as sa_insert
from app.models.models import Pond

MISSING={0,9999,9999.0,9999.9}; IMPORTER_VERSION='bulk-upsert-v1'
def norm_text(v): return unicodedata.normalize('NFKC', str(v)).strip().replace(' ','') if v is not None and str(v).strip()!='' else None
def maybe_float(v):
    try:
        f=float(unicodedata.normalize('NFKC',str(v)).replace(',','')); return None if f in MISSING or math.isnan(f) else f
    except Exception: return None
def dms_to_decimal(v):
    if v is None or str(v).strip()=='': return None
    s=unicodedata.normalize('NFKC',str(v)).strip(); sign=-1 if s.startswith('-') else 1
    try:
        f=float(s); return f if f not in MISSING and abs(f)<=180 and f!=0 else None
    except Exception: pass
    nums=[float(x) for x in re.findall(r"\d+(?:\.\d+)?", s)]
    if not nums: return None
    val=nums[0]+(nums[1] if len(nums)>1 else 0)/60+(nums[2] if len(nums)>2 else 0)/3600
    return sign*val
def pick(row,names):
    for n in names:
        if n in row and row[n] not in (None,''): return row[n]
    return None
def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def validate_xlsx(path):
    if Path(path).suffix.lower()!='.xlsx': raise ValueError('input must be .xlsx')
    if os.path.getsize(path)>1024*1024*1024: raise ValueError('input exceeds 1GB safety limit')
    if not zipfile.is_zipfile(path): raise ValueError('xlsx ZIP structure is invalid')

def build_record(row, idx):
    name=norm_text(pick(row,['ため池名','名称','name','ため池名称'])) or f'unknown-{idx}'
    lat=dms_to_decimal(pick(row,['緯度','lat','latitude'])); lon=dms_to_decimal(pick(row,['経度','lon','longitude']))
    flags=[]
    if lat is None or lon is None: flags.append('coordinate_missing')
    if lat is not None and lon is not None:
        if 122<=lat<=154 and 20<=lon<=46: flags.append('coordinate_swapped_candidate')
        if not (20<=lat<=46 and 122<=lon<=154): flags.append('coordinate_out_of_japan')
    rec={'source_system':'tameike_ichiranR8','source_record_id':str(idx),'name':name,'normalized_name':name,'prefecture':norm_text(pick(row,['都道府県','県名','prefecture'])),'municipality':norm_text(pick(row,['市町村','市区町村','municipality'])),'municipality_code':norm_text(pick(row,['市町村コード','municipality_code'])),'address':norm_text(pick(row,['所在地','住所','address'])),'latitude':lat,'longitude':lon,'coordinate_quality':'map_selected' if lat is not None and lon is not None else 'unknown','quality_flags':{'issues':flags},'duplicate_candidate':False,'dam_height_m':maybe_float(pick(row,['堤高','dam_height_m'])),'crest_length_m':maybe_float(pick(row,['堤頂長','crest_length_m'])),'total_storage_thousand_m3':maybe_float(pick(row,['総貯水量','total_storage_thousand_m3'])),'full_water_area_km2':maybe_float(pick(row,['満水面積','full_water_area_km2'])),'source_payload':{k:(str(v) if v is not None else None) for k,v in row.items()},'normalized_payload':{'name':name,'lat':lat,'lon':lon},'confidence':0.5,'data_source':'ため池台帳','updated_at':datetime.now(timezone.utc)}
    return rec

def flush(db, batch, mode):
    if not batch or mode=='dry-run': return {'inserted':0,'updated':0,'skipped':len(batch)}
    if db.bind.dialect.name=='postgresql':
        stmt=pg_insert(Pond).values(batch)
        if mode=='insert': stmt=stmt.on_conflict_do_nothing(index_elements=['source_system','source_record_id'])
        else: stmt=stmt.on_conflict_do_update(index_elements=['source_system','source_record_id'], set_={k:getattr(stmt.excluded,k) for k in batch[0] if k not in ['source_system','source_record_id']})
        res=db.execute(stmt); db.execute(text("UPDATE pond SET location=ST_SetSRID(ST_MakePoint(longitude, latitude),4326) WHERE longitude IS NOT NULL AND latitude IS NOT NULL AND (location IS NULL OR ST_X(location)<>longitude OR ST_Y(location)<>latitude)"))
    else:
        res=db.execute(sa_insert(Pond), batch)
    db.commit(); return {'inserted':getattr(res,'rowcount',0) or 0,'updated':0,'skipped':0}

def import_excel(db, input_path, limit=None, mode='upsert', batch_size=5000, resume=False):
    from openpyxl import load_workbook
    validate_xlsx(input_path); start=time.perf_counter(); tracemalloc.start(); file_hash=sha256(input_path)
    wb=load_workbook(input_path, read_only=True, data_only=True); ws=wb[wb.sheetnames[0]]
    headers=[str(c).strip() if c is not None else f'col{i}' for i,c in enumerate(next(ws.iter_rows(values_only=True)))]
    stats={'input':str(input_path),'sha256':file_hash,'fileSize':os.path.getsize(input_path),'sheet':ws.title,'headers':headers,'startedAt':datetime.now(timezone.utc).isoformat(),'mode':mode,'batchSize':batch_size,'processed':0,'success':0,'inserted':0,'updated':0,'skipped':0,'failed':0,'missing':0,'duplicateCandidates':0,'failureSamples':[],'importerVersion':IMPORTER_VERSION,'platform':platform.platform()}
    batch=[]; seen=set()
    for idx, vals in enumerate(ws.iter_rows(values_only=True), start=2):
        if limit and stats['processed']>=limit: break
        stats['processed']+=1
        try:
            rec=build_record(dict(zip(headers, vals)), idx); issues=rec['quality_flags']['issues']
            if 'coordinate_missing' in issues: stats['missing']+=1
            key=(rec['municipality'], round(rec['latitude'] or 0,6), round(rec['longitude'] or 0,6), rec['name'])
            dup=key in seen and rec['latitude'] is not None and rec['longitude'] is not None
            if dup: rec['duplicate_candidate']=True; rec['quality_flags']['issues'].append('duplicate_exact_coordinate'); stats['duplicateCandidates']+=1
            seen.add(key); batch.append(rec); stats['success']+=1
            if len(batch)>=batch_size:
                r=flush(db,batch,mode); stats['inserted']+=r['inserted']; stats['updated']+=r['updated']; stats['skipped']+=r['skipped']; batch=[]
        except Exception as e:
            stats['failed']+=1
            if len(stats['failureSamples'])<100: stats['failureSamples'].append({'row':idx,'error':type(e).__name__})
    r=flush(db,batch,mode); stats['inserted']+=r['inserted']; stats['updated']+=r['updated']; stats['skipped']+=r['skipped']
    cur,peak=tracemalloc.get_traced_memory(); tracemalloc.stop(); elapsed=time.perf_counter()-start
    stats.update({'completedAt':datetime.now(timezone.utc).isoformat(),'elapsedSeconds':round(elapsed,3),'rowsPerSecond':round(stats['processed']/elapsed,2) if elapsed else 0,'peakMemoryBytes':peak})
    return stats
