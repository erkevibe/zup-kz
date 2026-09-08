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
assert actual["scheduleCycleOwnershipRejected"] is True
assert actual["scheduleCycleDayOffRejected"] is True
assert actual["scheduleCycleDuplicateDayRejected"] is True
assert actual["scheduleOrganizationRejected"] is True
assert actual["scheduleEmploymentPeriodRejected"] is True
assert actual["scheduleValidityPeriodRejected"] is True
assert actual["scheduleCycleGapRejected"] is True
assert actual["scheduleCycleStartRequiredRejected"] is True
assert actual["scheduleCycleStartAfterAssignmentRejected"] is True
assert actual["shiftPlannedHoursRejected"] is True
assert actual["overnightShiftAccepted"] is True
assert Decimal(str(actual["overnightAvailableMinutes"])) == Decimal("420.00")
