import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from PIL import Image
from pydantic import ValidationError

from billtable.export import to_csv
from billtable.extract import extract_bill, prepare_image
from billtable.schema import Bill, LineItem
from billtable.validate import check


def good_bill():
    return Bill(
        vendor="Fresh Mart",
        total=118.0,
        subtotal=100.0,
        tax=18.0,
        items=[
            LineItem(description="Rice", quantity=2, unit_price=30, amount=60),
            LineItem(description="Dal", quantity=1, unit_price=40, amount=40),
        ],
    )


def png_bytes(size=(3000, 2000)):
    buf = io.BytesIO()
    Image.new("RGB", size, "white").save(buf, format="PNG")
    return buf.getvalue()


def test_consistent_bill_has_no_warnings():
    assert check(good_bill()) == []


def test_wrong_line_math_is_flagged():
    b = good_bill()
    b.items[0].amount = 90
    assert any("Rice" in w for w in check(b))


def test_subtotal_mismatch_is_flagged():
    b = good_bill()
    b.subtotal = 150
    assert any("subtotal" in w.lower() for w in check(b))


def test_total_mismatch_is_flagged():
    b = good_bill()
    b.total = 999
    assert any("total" in w.lower() for w in check(b))


def test_empty_bill_warns():
    assert check(Bill()) == ["No line items were found."]


def test_negative_amount_rejected():
    with pytest.raises(ValidationError):
        LineItem(description="x", amount=-1)


def test_prepare_image_downscales_and_returns_jpeg():
    out = prepare_image(png_bytes())
    img = Image.open(io.BytesIO(out))
    assert img.format == "JPEG" and max(img.size) <= 1600


def test_extract_bill_parses_model_json():
    payload = json.dumps({"vendor": "Cafe", "items": [{"description": "Tea", "amount": 20}], "total": 20})
    bill = extract_bill(png_bytes((100, 100)), call_model=lambda jpeg: payload)
    assert bill.vendor == "Cafe" and bill.items[0].quantity == 1


def test_extract_bill_rejects_garbage_output():
    with pytest.raises(ValidationError):
        extract_bill(png_bytes((100, 100)), call_model=lambda jpeg: "not json")


def test_csv_export_has_header_and_rows():
    lines = to_csv(good_bill()).strip().splitlines()
    assert lines[0] == "description,quantity,unit_price,amount" and len(lines) == 3
