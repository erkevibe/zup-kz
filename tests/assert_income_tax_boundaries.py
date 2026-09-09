import json
import sys
from decimal import Decimal


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source, parse_float=Decimal)

expected = {
    "threshold": Decimal("36762500.00"),
    "ipnAtThreshold": Decimal("3676250.00"),
    "ipnOneTengeAbove": Decimal("3676250.15"),
    "roundedFourTiyinExcess": Decimal("0.01"),
    "salaryTaxable": Decimal("36761500.00"),
    "salaryIpn": Decimal("3676150.00"),
    "civilTaxable": Decimal("2000.00"),
    "civilIpn": Decimal("250.00"),
    "civilPayable": Decimal("1750.00"),
    "combinedTaxable": Decimal("36763500.00"),
    "combinedIpn": Decimal("3676400.00"),
    "opvMaxBase": Decimal("4250000.00"),
    "opvMaxAmount": Decimal("425000.00"),
    "soMaxBase": Decimal("595000.00"),
    "soMaxAmount": Decimal("29750.00"),
    "vosmsMaxBase": Decimal("1700000.00"),
    "vosmsMaxAmount": Decimal("34000.00"),
}

for name, value in expected.items():
    assert Decimal(str(actual.get(name))) == value, (name, actual.get(name), value)

assert actual["salaryPack"] == "KZ-2026.1"
assert actual["civilPack"] == "KZ-2026.1"
