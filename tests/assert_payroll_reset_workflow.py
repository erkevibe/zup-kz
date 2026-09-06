import json
import sys
from decimal import Decimal


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)

for name in (
    "payrollRecalculated",
    "oneFreshPayrollLine",
    "timeSnapshotPreserved",
    "socialCancelled",
    "taxesCancelled",
    "enforcementCancelled",
    "taxReversalCreated",
    "resetReasonSaved",
):
    assert actual[name] is True, (name, actual[name])

assert Decimal(str(actual["recalculatedAmount"])) == Decimal("100000.00")
assert Decimal(str(actual["reversedIpn"])) == Decimal("-80.00")
