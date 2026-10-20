from datetime import date

from app.claims import validate_claim

START, END = date(2024, 1, 1), date(2026, 12, 31)


def claim(**overrides):
    base = {"claim_id": "C-001", "vin": "1N4AL3AP8JC123456",
            "repair_date": date(2026, 5, 1), "amount": 12_000}
    return {**base, **overrides}


def test_happy_path_auto_routes():
    r = validate_claim(claim(), START, END)
    assert r.ok and r.route == "auto"


def test_missing_field_rejected_with_reason():
    r = validate_claim(claim(vin=""), START, END)
    assert r.route == "reject" and "missing vin" in r.reasons


def test_boundary_last_day_of_warranty_passes():
    assert validate_claim(claim(repair_date=END), START, END).ok


def test_day_after_warranty_rejected():
    r = validate_claim(claim(repair_date=date(2027, 1, 1)), START, END)
    assert "repair date outside warranty period" in r.reasons


def test_high_amount_goes_to_human():
    assert validate_claim(claim(amount=80_000), START, END).route == "human"


def test_bad_vin_length_rejected():
    assert validate_claim(claim(vin="SHORT"), START, END).route == "reject"
