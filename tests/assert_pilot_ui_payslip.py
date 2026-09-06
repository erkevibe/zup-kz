"""Check the read-only payslip presentation against the persistent September pilot."""
import json
import sys
from decimal import Decimal

if len(sys.argv) != 2:
    raise SystemExit("Usage: assert_pilot_ui_payslip.py result.json|-")
if sys.argv[1] == "-":
    actual = json.load(sys.stdin, parse_float=Decimal)
else:
    with open(sys.argv[1], encoding="utf-8") as source:
        actual = json.load(source, parse_float=Decimal)

expected = {
    "allowed": True, "nullDenied": True, "withheld": 59825,
    "accrued": 350000, "payable": 290175,
    "organization": "UI Test Organization",
    "employee": "Серикова Айгуль Маратовна",
}
for key, value in expected.items():
    assert actual.get(key) == value, (key, actual.get(key), value)
assert actual["accrued"] - actual["withheld"] == actual["payable"]
print("PASS: payslip access, snapshot totals and employee deduction balance")
