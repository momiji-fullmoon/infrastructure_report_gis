from app.services.importer import REAL_COLUMNS, build_record, dms_to_decimal


def real_row(**overrides):
    row = {
        "名称": "実台帳池",
        "都道府県": "兵庫県",
        "市区町村": "加古川市",
        "町域名、番地": "志方町1",
        "緯度": "３４",
        "分": "45",
        "秒": "30.6",
        "経度": 134,
        "分2": 50,
        "秒2": 15,
        "堤高(m)": "12.5",
        "堤頂長(m)": "80",
        "総貯水量(千m3)": "5.5",
        "満水面積(km2)": "0.02",
    }
    row.update(overrides)
    return row


def test_real_excel_columns_dms_and_payload():
    flags=set()
    assert round(dms_to_decimal("34", "45", "30.6", flags), 6) == 34.7585
    rec=build_record(real_row(), 2, "abc")
    assert set(REAL_COLUMNS).issubset(rec["source_payload"])
    assert rec["address"] == "志方町1"
    assert rec["dam_height_m"] == 12.5
    assert rec["crest_length_m"] == 80
    assert rec["total_storage_thousand_m3"] == 5.5
    assert rec["full_water_area_km2"] == 0.02
    assert rec["latitude"] == 34 + 45/60 + 30.6/3600
    assert rec["longitude"] == 134 + 50/60 + 15/3600
    assert rec["normalized_payload"]["input_sha256"] == "abc"


def test_sentinel_full_width_and_swapped_candidate():
    rec=build_record(real_row(**{"満水面積(km2)":"９９９９．９", "緯度":"139", "分":"48", "秒":"0", "経度":"36", "分2":"30", "秒2":"0"}), 3)
    assert rec["full_water_area_km2"] is None
    assert "sentinel_missing_value" in rec["quality_flags"]["issues"]
    assert "missing_full_water_area" in rec["quality_flags"]["issues"]
    assert "coordinate_swapped_candidate" in rec["quality_flags"]["issues"]
