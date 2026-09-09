import json
import sys
from decimal import Decimal


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source, parse_float=Decimal)

expected = {
    "scenarioCount": Decimal("5"),
    "residentOpv": Decimal("50000.00"),
    "residentOpvr": Decimal("17500.00"),
    "residentSo": Decimal("22500.00"),
    "residentVosms": Decimal("10000.00"),
    "residentOosms": Decimal("15000.00"),
    "residentBasicDeduction": Decimal("129750.00"),
    "residentTaxableIncome": Decimal("310250.00"),
    "residentIpn": Decimal("31025.00"),
    "nonresidentBasicDeduction": Decimal("0.00"),
    "nonresidentSocialDeduction": Decimal("0.00"),
    "nonresidentTaxableIncome": Decimal("440000.00"),
    "nonresidentIpn": Decimal("44000.00"),
    "disabilityBasicDeduction": Decimal("129750.00"),
    "disabilitySocialDeduction": Decimal("310250.00"),
    "disabilityTaxableIncome": Decimal("0.00"),
    "disabilityIpn": Decimal("0.00"),
    "opvrBoundaryAmount": Decimal("17500.00"),
    "opvrBeforeBoundaryAmount": Decimal("0.00"),
}

for name, value in expected.items():
    assert Decimal(str(actual.get(name, 0))) == value, (name, actual.get(name), value)

assert actual["nonresidentRecorded"] is True
assert actual["disabilityDeductionCodes"] == "1,2"
assert actual["opvrBoundaryIncluded"] is True
assert actual["opvrBeforeBoundaryExempt"] is True
assert actual["regulatoryPack"] == "KZ-2026.1"
