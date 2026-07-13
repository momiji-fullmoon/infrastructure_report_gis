import hashlib, math, os, platform, re, time, tracemalloc, unicodedata, zipfile
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import insert as sa_insert, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.models.models import Pond

IMPORTER_VERSION = "real-excel-dms-v2"
SOURCE_SYSTEM = "tameike_ichiranR8"
REAL_COLUMNS = ["名称","都道府県","市区町村","町域名、番地","緯度","分","秒","経度","分2","秒2","堤高(m)","堤頂長(m)","総貯水量(千m3)","満水面積(km2)"]
COLUMN_MAP = {
    "name":"名称", "prefecture":"都道府県", "municipality":"市区町村", "address":"町域名、番地",
    "latitude_degree":"緯度", "latitude_minute":"分", "latitude_second":"秒",
    "longitude_degree":"経度", "longitude_minute":"分2", "longitude_second":"秒2",
    "dam_height_m":"堤高(m)", "crest_length_m":"堤頂長(m)", "total_storage_thousand_m3":"総貯水量(千m3)", "full_water_area_km2":"満水面積(km2)",
}
SENTINELS = {0.0, 9999.0, 9999.9}

def norm_text(v):
    if v is None or str(v).strip() == "": return None
    return unicodedata.normalize("NFKC", str(v)).strip()

def _to_float(v, flags):
    if v is None or str(v).strip() == "": return None
    s = unicodedata.normalize("NFKC", str(v)).strip().replace(",", "")
    try:
        f = float(s)
    except ValueError:
        flags.add("invalid_numeric_value"); return None
    if math.isnan(f) or f in SENTINELS:
        flags.add("sentinel_missing_value"); return None
    return f

def maybe_float(v, flags=None):
    flags = flags if flags is not None else set()
    return _to_float(v, flags)

def dms_to_decimal(deg, minute=None, second=None, flags=None):
    flags = flags if flags is not None else set()
    if minute is None and second is None and isinstance(deg, str):
        raw = unicodedata.normalize("NFKC", deg).strip()
        nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", raw)]
        if len(nums) >= 2:
            sign = -1 if nums[0] < 0 else 1
            return nums[0] + sign * ((nums[1] if len(nums)>1 else 0)/60 + (nums[2] if len(nums)>2 else 0)/3600)
    d = _to_float(deg, flags); m = _to_float(minute, flags); s = _to_float(second, flags)
    if d is None: return None
    return d + (m or 0) / 60 + (s or 0) / 3600

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def validate_xlsx(path):
    if Path(path).suffix.lower()!='.xlsx': raise ValueError('input must be .xlsx')
    if os.path.getsize(path)>1024*1024*1024: raise ValueError('input exceeds 1GB safety limit')
    if not zipfile.is_zipfile(path): raise ValueError('xlsx ZIP structure is invalid')

def build_record(row, idx, file_hash=""):
    flags=set(); source_payload={c: (str(row.get(c)) if row.get(c) is not None else None) for c in REAL_COLUMNS}
    name=norm_text(row.get(COLUMN_MAP['name'])) or f"unknown-{idx}"
    lat=dms_to_decimal(row.get('緯度'), row.get('分'), row.get('秒'), flags)
    lon=dms_to_decimal(row.get('経度'), row.get('分2'), row.get('秒2'), flags)
    area=maybe_float(row.get('満水面積(km2)'), flags)
    if area is None: flags.add('missing_full_water_area')
    if lat is None or lon is None: flags.add('coordinate_missing')
    elif 122 <= lat <= 154 and 20 <= lon <= 46: flags.add('coordinate_swapped_candidate')
    if lat is not None and lon is not None and not (20 <= lat <= 46 and 122 <= lon <= 154): flags.add('coordinate_out_of_japan')
    normalized={'name':name,'latitude':lat,'longitude':lon,'latitude_degree':maybe_float(row.get('緯度'), set()),'latitude_minute':maybe_float(row.get('分'), set()),'latitude_second':maybe_float(row.get('秒'), set()),'longitude_degree':maybe_float(row.get('経度'), set()),'longitude_minute':maybe_float(row.get('分2'), set()),'longitude_second':maybe_float(row.get('秒2'), set()),'input_sha256':file_hash,'importer_version':IMPORTER_VERSION}
    return {'source_system':SOURCE_SYSTEM,'source_record_id':str(idx),'name':name,'normalized_name':name,'prefecture':norm_text(row.get('都道府県')),'municipality':norm_text(row.get('市区町村')),'municipality_code':None,'address':norm_text(row.get('町域名、番地')),'latitude':lat,'longitude':lon,'coordinate_quality':'map_selected' if lat is not None and lon is not None and 'coordinate_out_of_japan' not in flags else 'unknown','quality_flags':{'issues':sorted(flags)},'duplicate_candidate':False,'dam_height_m':maybe_float(row.get('堤高(m)'), flags),'crest_length_m':maybe_float(row.get('堤頂長(m)'), flags),'total_storage_thousand_m3':maybe_float(row.get('総貯水量(千m3)'), flags),'full_water_area_km2':area,'source_payload':source_payload,'normalized_payload':normalized,'confidence':0.8,'data_source':'ため池台帳','updated_at':datetime.now(timezone.utc)}

def _count_existing(db, batch):
    keys=[(r['source_system'], r['source_record_id']) for r in batch]
    if not keys: return 0
    if db.bind.dialect.name=='postgresql':
        vals=','.join([f"(:s{i},:r{i})" for i in range(len(keys))]); params={}
        for i,(s,r) in enumerate(keys): params[f's{i}']=s; params[f'r{i}']=r
        return db.scalar(text(f"select count(*) from pond p join (values {vals}) v(source_system,source_record_id) on p.source_system=v.source_system and p.source_record_id=v.source_record_id"), params) or 0
    return sum(1 for s,r in keys if db.scalar(select(Pond.pond_id).where(Pond.source_system==s, Pond.source_record_id==r)))

def flush(db, batch, mode):
    if not batch or mode=='dry-run': return {'inserted':0,'updated':0,'skipped':len(batch) if mode=='dry-run' else 0}
    existing=_count_existing(db,batch)
    if db.bind.dialect.name=='postgresql':
        stmt=pg_insert(Pond).values(batch)
        if mode=='insert': stmt=stmt.on_conflict_do_nothing(index_elements=['source_system','source_record_id'])
        else: stmt=stmt.on_conflict_do_update(index_elements=['source_system','source_record_id'], set_={k:getattr(stmt.excluded,k) for k in batch[0] if k not in ['source_system','source_record_id','pond_id','created_at']})
        res=db.execute(stmt)
        db.execute(text("UPDATE pond SET location=ST_SetSRID(ST_MakePoint(longitude, latitude),4326) WHERE longitude IS NOT NULL AND latitude IS NOT NULL"))
    else:
        if mode == 'insert':
            batch=[r for r in batch if not db.scalar(select(Pond.pond_id).where(Pond.source_system==r['source_system'], Pond.source_record_id==r['source_record_id']))]
        res=db.execute(sa_insert(Pond), batch) if batch else None
    db.commit()
    affected=getattr(res,'rowcount',0) if res is not None else 0
    return {'inserted': max(0, affected-existing) if mode!='insert' else affected, 'updated': existing if mode!='insert' else 0, 'skipped': existing if mode=='insert' else 0}

def import_excel(db, input_path, limit=None, mode='upsert', batch_size=5000):
    from openpyxl import load_workbook
    if mode not in {'insert','upsert','replace-source','dry-run'}: raise ValueError('unsupported import mode')
    validate_xlsx(input_path); start=time.perf_counter(); tracemalloc.start(); file_hash=sha256(input_path)
    if mode=='replace-source': db.execute(text("delete from pond where source_system=:s"), {'s':SOURCE_SYSTEM}); db.commit(); mode='upsert'
    wb=load_workbook(input_path, read_only=True, data_only=True); ws=wb[wb.sheetnames[0]]
    headers=[str(c).strip() if c is not None else f'col{i}' for i,c in enumerate(next(ws.iter_rows(values_only=True)))]
    missing=[c for c in REAL_COLUMNS if c not in headers]
    if missing: raise ValueError(f'missing real Excel columns: {missing}')
    stats={'input':str(input_path),'sha256':file_hash,'sheet':ws.title,'headers':headers,'mode':mode,'batchSize':batch_size,'processed':0,'inserted':0,'updated':0,'skipped':0,'failed':0,'missing':0,'outOfJapan':0,'duplicateCandidates':0,'failureSamples':[],'importerVersion':IMPORTER_VERSION,'platform':platform.platform()}
    batch=[]; seen_exact=set(); seen_round=set()
    for idx, vals in enumerate(ws.iter_rows(values_only=True), start=2):
        if limit and stats['processed']>=limit: break
        stats['processed']+=1
        try:
            rec=build_record(dict(zip(headers, vals)), idx, file_hash); issues=rec['quality_flags']['issues']
            if 'coordinate_missing' in issues: stats['missing']+=1
            if 'coordinate_out_of_japan' in issues: stats['outOfJapan']+=1
            if rec['latitude'] is not None and rec['longitude'] is not None:
                exact=(rec['latitude'],rec['longitude']); rounded=(round(rec['latitude'],6),round(rec['longitude'],6))
                if exact in seen_exact: rec['quality_flags']['issues'].append('duplicate_exact_coordinate')
                if rounded in seen_round: rec['quality_flags']['issues'].append('duplicate_rounded_coordinate')
                if any(i.startswith('duplicate_') for i in rec['quality_flags']['issues']): rec['duplicate_candidate']=True; stats['duplicateCandidates']+=1
                seen_exact.add(exact); seen_round.add(rounded)
            batch.append(rec)
            if len(batch)>=batch_size:
                r=flush(db,batch,mode); [stats.__setitem__(k, stats[k]+r[k]) for k in r]; batch=[]
        except Exception as e:
            stats['failed']+=1
            if len(stats['failureSamples'])<100: stats['failureSamples'].append({'row':idx,'error':type(e).__name__,'message':str(e)})
    r=flush(db,batch,mode); [stats.__setitem__(k, stats[k]+r[k]) for k in r]
    cur,peak=tracemalloc.get_traced_memory(); tracemalloc.stop(); elapsed=time.perf_counter()-start
    stats.update({'elapsedSeconds':round(elapsed,3),'rowsPerSecond':round(stats['processed']/elapsed,2) if elapsed else 0,'peakMemoryBytes':peak,'completedAt':datetime.now(timezone.utc).isoformat()})
    return stats
