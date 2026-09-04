import json
import sys
from decimal import Decimal


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)

assert Decimal(str(actual["recalculationDelta"])) == Decimal("10000.00")
assert Decimal(str(actual["registeredAmount"])) == Decimal("10000.00")
assert actual["registeredAsAccrual"] is True
assert actual["registeredInTargetRun"] is True
assert actual["recalculationPosted"] is True
assert actual["taxesCancelled"] is True
assert Decimal(str(actual["reversalAmount"])) == Decimal("-9000.00")
assert actual["reversalLinked"] is True
assert Decimal(str(actual.get("ledgerNetIpn", 0))) == Decimal("0.00")
