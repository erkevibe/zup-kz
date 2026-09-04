import json
import sys
from decimal import Decimal


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)

assert actual["januaryApproved"] is True
assert actual["usedTimesheetCancellationRejected"] is True
assert actual["februaryCancelled"] is True
assert actual["payrollTimeCollected"] is True
assert Decimal(str(actual["summaryPlannedHoursResult"])) == Decimal("8.00")
assert Decimal(str(actual["summaryWorkedHoursResult"])) == Decimal("8.00")
