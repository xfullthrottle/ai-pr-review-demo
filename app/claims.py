"""Warranty-claim intake validation (synthetic demo).

Mirrors the real pattern: validate at intake, reject with a reason,
never silently drop a record.
"""
from dataclasses import dataclass
from datetime import date

REQUIRED_FIELDS = ("claim_id", "vin", "repair_date", "amount")
MAX_AUTO_APPROVE = 50_000  # PHP; anything above goes to a human


@dataclass
class Result:
    ok: bool
    reasons: list[str]
    route: str  # "auto" | "human" | "reject"


def validate_claim(claim: dict, warranty_start: date, warranty_end: date) -> Result:
    reasons = [f"missing {f}" for f in REQUIRED_FIELDS if not claim.get(f)]
    if reasons:
        return Result(False, reasons, "reject")

    vin = str(claim["vin"])
    if len(vin) != 17:
        reasons.append("vin must be 17 characters")

    repair_date = claim["repair_date"]
    if not (warranty_start <= repair_date <= warranty_end):
        reasons.append("repair date outside warranty period")

    amount = claim["amount"]
    if amount < 0:
        reasons.append("amount must be positive")

    if reasons:
        return Result(False, reasons, "reject")
    if amount > MAX_AUTO_APPROVE:
        return Result(True, ["amount above auto-approve limit"], "human")
    return Result(True, [], "auto")
