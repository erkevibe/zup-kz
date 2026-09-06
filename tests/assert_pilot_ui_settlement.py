"""Verify the persistent UI pilot after closing payroll and filling a statement.

Synthetic resident employee, August 2026, basic deduction, no enforcement orders.
Input: pilotUiSettlementVerificationTest JSON. No writes or external payments.
"""
import json
import sys
from decimal import Decimal


if len(sys.argv) != 2:
    raise SystemExit("Usage: assert_pilot_ui_settlement.py result.json|-")
if sys.argv[1] == "-":
    actual = json.load(sys.stdin, parse_float=Decimal)
else:
    with open(sys.argv[1], encoding="utf-8") as source:
        actual = json.load(source, parse_float=Decimal)

expected = {
    "socialApproved": True, "taxesApproved": True, "enforcementApproved": True,
    "payrollClosed": True, "settlementCount": 1,
    "accrued": 400000, "opv": 40000, "opvr": 14000, "so": 18000,
    "vosms": 8000, "oosms": 12000, "ipn": 22225, "socialTax": 21120,
    "basicDeduction": 129750, "payable": 329775,
    "statementFilled": True, "statementLines": 1, "statementAmount": 329775,
    "unpaid": 329775, "notPaid": True,
    "socialPack": "KZ-2026.1", "taxPack": "KZ-2026.1",
}
for key, value in expected.items():
    assert actual.get(key) == value, (key, actual.get(key), value)
assert actual["payable"] == actual["accrued"] - actual["opv"] - actual["vosms"] - actual["ipn"]
print("PASS: UI taxes, closed payslip and filled UNPAID statement")
