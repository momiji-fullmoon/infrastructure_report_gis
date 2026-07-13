from app.services.importer import dms_to_decimal, maybe_float

def test_dms(): assert round(dms_to_decimal('36度30分0秒'), 4)==36.5
def test_missing(): assert maybe_float(9999) is None
