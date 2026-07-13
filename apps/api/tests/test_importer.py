from app.services.importer import dms_to_decimal, build_record

def test_coordinate_formats_and_flags():
    assert round(dms_to_decimal('35度30分0秒'), 6) == 35.5
    assert round(dms_to_decimal('35°30′0″'), 6) == 35.5
    assert dms_to_decimal('３５．５') == 35.5
    assert dms_to_decimal('') is None
    assert dms_to_decimal('0') is None
    assert dms_to_decimal('9999') is None
    assert dms_to_decimal('-35.5') == -35.5
    rec=build_record({'ため池名':'A','緯度':'139.8','経度':'36.5'},2)
    assert 'coordinate_swapped_candidate' in rec['quality_flags']['issues']
