import argparse
from app.db.session import Base, engine, SessionLocal
from app.models import models
from app.services.importer import import_excel

def main():
    p=argparse.ArgumentParser(); p.add_argument('--input', required=True); p.add_argument('--limit', type=int)
    args=p.parse_args(); Base.metadata.create_all(engine)
    with SessionLocal() as db: print(import_excel(db,args.input,args.limit))
if __name__=='__main__': main()
