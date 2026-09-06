"""Read-only verification after the UI timekeeper/payroll scenario.

Read pilotUiVerificationTest JSON from a file or stdin (-); never reset the DB.
"""
import json
import sys
from decimal import Decimal


if len(sys.argv) != 2:
    raise SystemExit("Usage: assert_pilot_ui_workflow.py result.json|-")
if sys.argv[1] == "-":
    actual = json.load(sys.stdin, parse_float=Decimal)
else:
    with open(sys.argv[1], encoding="utf-8") as source:
        actual = json.load(source, parse_float=Decimal)

expected = {
    "employee": "Серикова Айгуль Маратовна",
    "fullMonthDays": 31,
    "timesheetApproved": True,
    "approver": "ui-time",
    "approverLabel": "ui-time",
    "originalPreserved": True,
    "plannedHours": 168,
    "workedHours": 168,
    "calculated": True,
    "lineCount": 2,
    "accrued": Decimal("400000.00"),
    "expectedAccrued": True,
}
for key, value in expected.items():
    assert actual.get(key) == value, (key, actual.get(key), value)
print("PASS: persistent UI pilot, approved time and gross payroll")
