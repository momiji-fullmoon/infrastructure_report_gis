import argparse
import json
from app.db.session import SessionLocal
from app.services.importer import import_excel

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input', required=True); p.add_argument('--mode', choices=['insert','upsert','replace-source','dry-run'], default='upsert')
    p.add_argument('--batch-size', type=int, default=5000); p.add_argument('--limit', type=int); p.add_argument('--resume', action='store_true'); p.add_argument('--dry-run', action='store_true'); p.add_argument('--report')
    args=p.parse_args()
    with SessionLocal() as db: stats=import_excel(db,args.input,limit=args.limit,mode='dry-run' if args.dry_run else args.mode,batch_size=args.batch_size,resume=args.resume)
    print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
    if args.report:
        from pathlib import Path
        Path(args.report).parent.mkdir(parents=True, exist_ok=True); Path(args.report).write_text(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
if __name__=='__main__': main()
