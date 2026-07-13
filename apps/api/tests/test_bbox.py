import pytest
from fastapi import HTTPException
from app.main import parse_bbox

def test_bbox_valid_boundary(): assert parse_bbox('139,35,140,36') == [139,35,140,36]
@pytest.mark.parametrize('bbox', ['140,35,139,36','a,35,140,36','139,35,140','10,35,140,36'])
def test_bbox_invalid(bbox):
    with pytest.raises(HTTPException) as e: parse_bbox(bbox)
    assert e.value.status_code == 422
