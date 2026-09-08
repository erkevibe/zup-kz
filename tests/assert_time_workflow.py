import json
import sys
from decimal import Decimal


actual = {}
for result_path in sys.argv[1:]:
    with open(result_path, encoding="utf-8") as source:
        actual.update(json.load(source))

assert actual["januaryApproved"] is True
assert actual["januaryApproverSet"] is True
assert actual["usedTimesheetCancellationRejected"] is True
assert actual["februaryCancelled"] is True
assert actual["februaryCancellerSet"] is True
assert actual["payrollTimeCollected"] is True
assert Decimal(str(actual["summaryPlannedHoursResult"])) == Decimal("8.00")
assert Decimal(str(actual["summaryWorkedHoursResult"])) == Decimal("8.00")
assert actual["scheduleOverlapRejected"] is True
assert actual["scheduleOriginalPreserved"] is True
