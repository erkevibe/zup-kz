import json
import sys
from decimal import Decimal


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)

expected = {
    "fullMonth": Decimal("100000.00"),
    "halfMonth": Decimal("50000.00"),
    "nightAdditional": Decimal("2380.95"),
    "overtimeAdditional": Decimal("2976.19"),
    "holidayAdditional": Decimal("2380.95"),
    "overtimeTotal": Decimal("108928.57"),
    "documentLineCount": Decimal("4"),
    "documentAccrued": Decimal("118452.38"),
    "documentPayable": Decimal("118452.38"),
    "averageDaily": Decimal("4878.048780"),
    "averageHourly": Decimal("609.756098"),
    "averagePayDays": Decimal("48780.49"),
    "averagePayHours": Decimal("48780.49"),
    "averagePaySummarized": Decimal("48024.39"),
    "positiveRecalculation": Decimal("10000.00"),
    "negativeRecalculation": Decimal("-5000.00"),
    "annualLeaveWithHoliday": Decimal("5"),
    "annualLeaveWithReligiousDay": Decimal("3"),
    "vacationInterimPayment": Decimal("48780.49"),
    "advanceInterimPayment": Decimal("50000.00"),
    "sickLeaveMonthlyCap2026": Decimal("108125.00"),
    "sickLeaveBelowCap": Decimal("80000.00"),
    "sickLeaveAtCap": Decimal("108125.00"),
    "sickLeaveCapExempt": Decimal("150000.00"),
    "sickLeaveAcrossMonths": Decimal("158125.00"),
    "sickLeaveExcluded": Decimal("0.00"),
    "sickLeaveInterimPayment": Decimal("158125.00"),
}
for name, value in expected.items():
    assert Decimal(str(actual[name])) == value, (name, actual[name], value)

assert actual["scheduledLeavePaymentDue"] == "2026-07-08"
assert actual["outsideSchedulePaymentDue"] == "2026-07-16"
