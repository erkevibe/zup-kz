import json
import sys
from decimal import Decimal


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source, parse_float=Decimal)

for name in (
    "missingSocialProfileBlocked",
    "calculated",
    "nonresidentRecorded",
    "package2027Blocked",
):
    assert actual.get(name) is True, (name, actual.get(name))

expected = {
    "opv": Decimal("0.00"),
    "vosms": Decimal("0.00"),
    "socialContributions": Decimal("0.00"),
    "basicDeduction": Decimal("0.00"),
    "socialDeduction": Decimal("0.00"),
    "taxableIncome": Decimal("500000.00"),
    "baseRate": Decimal("20.000000"),
    "highRate": Decimal("20.000000"),
    "ipn": Decimal("100000.00"),
    "payable": Decimal("400000.00"),
}

for name, value in expected.items():
    assert Decimal(str(actual.get(name, 0))) == value, (name, actual.get(name), value)

assert actual["regulatoryPack"] == "KZ-2026.1"
