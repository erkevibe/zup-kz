import json
import sys
from decimal import Decimal


def load(path):
    with open(path, encoding="utf-8") as source:
        return json.load(source)


workflow = load(sys.argv[1])
line_guard = load(sys.argv[2])
input_guard = load(sys.argv[3])
verification = load(sys.argv[4])
period_guard = load(sys.argv[5])

assert Decimal(str(workflow["positiveDelta"])) == Decimal("10000.00")
assert Decimal(str(workflow["negativeDelta"])) == Decimal("-3000.00")
assert Decimal(str(workflow["positiveRegisteredAmount"])) == Decimal("10000.00")
assert Decimal(str(workflow["negativeRegisteredAmount"])) == Decimal("3000.00")
assert workflow["positiveRegisteredAsAccrual"] is True
assert workflow["negativeRegisteredAsDeduction"] is True
assert workflow["registrationCount"] == 2
assert workflow["targetPayrollLineCount"] == 2
assert workflow["targetCalculated"] is True
assert workflow["originalAccrualPreserved"] is True
assert workflow["originalBonusPreserved"] is True
assert workflow["recalculationApproved"] is True
assert line_guard["recalculationLineSnapshotBlocked"] is True
assert input_guard["recalculationInputSnapshotBlocked"] is True
assert period_guard["recalculationPeriodBlocked"] is True
assert verification == {
    "recalculationLineSnapshotPreserved": True,
    "recalculationInputSnapshotPreserved": True,
    "registrationCountPreserved": True,
}
