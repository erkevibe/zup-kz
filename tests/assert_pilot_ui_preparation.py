"""Read-only verification of September documents created through payroll UI.

Input: pilotUiPreparationVerificationTest JSON. Synthetic employee, unpaid.
"""
import json
import sys
from decimal import Decimal


if len(sys.argv) != 2:
    raise SystemExit("Usage: assert_pilot_ui_preparation.py result.json|-")
if sys.argv[1] == "-":
    actual = json.load(sys.stdin, parse_float=Decimal)
else:
    with open(sys.argv[1], encoding="utf-8") as source:
        actual = json.load(source, parse_float=Decimal)

expected = {
    "socialCount": 1, "taxCount": 1, "enforcementCount": 1, "statementCount": 1,
    "linkedSocial": True, "linkedTaxes": True, "payrollClosed": True,
    "accrued": 350000, "payable": 290175, "statementFilled": True,
    "statementAmount": 290175, "notPaid": True,
    "socialRunLabel": "UI-PREP-2026-09",
    "employeeLabel": "Серикова Айгуль Маратовна",
}
for key, value in expected.items():
    assert actual.get(key) == value, (key, actual.get(key), value)
print("PASS: native UI document creation, linked unique documents and UNPAID statement")
