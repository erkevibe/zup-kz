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
    "documentLineCount": Decimal("8"),
    "documentAccrued": Decimal("155452.38"),
    "documentDeducted": Decimal("5000.00"),
    "documentPayable": Decimal("150452.38"),
    "fixedBonusAmount": Decimal("20000.00"),
    "percentAllowanceAmount": Decimal("10000.00"),
    "manualDeductionAmount": Decimal("5000.00"),
    "unclassifiedAccrualAmount": Decimal("7000.00"),
    "ipnAssessmentBase": Decimal("148452.38"),
    "opvAssessmentBase": Decimal("148452.38"),
    "osmsAssessmentBase": Decimal("148452.38"),
    "opv2026": Decimal("14845.24"),
    "opvr2026": Decimal("5195.83"),
    "socialContribution2026": Decimal("6680.36"),
    "employeeOsms2026": Decimal("2969.05"),
    "employerOsms2026": Decimal("4453.57"),
    "payableBeforeIpn": Decimal("132638.09"),
    "maximumOpv2026": Decimal("425000.00"),
    "maximumOpvr2026": Decimal("148750.00"),
    "minimumOpvr2026": Decimal("2975.00"),
    "maximumSocialContribution2026": Decimal("29750.00"),
    "minimumSocialContribution2026": Decimal("4250.00"),
    "maximumEmployeeOsms2026": Decimal("34000.00"),
    "maximumEmployerOsms2026": Decimal("102000.00"),
    "ipnBasicDeduction2026": Decimal("129750.00"),
    "ipnTaxableIncome2026": Decimal("888.09"),
    "ipn2026": Decimal("88.81"),
    "socialTax2026": Decimal("7838.29"),
    "finalPayable2026": Decimal("132549.28"),
    "progressiveIpnAboveThreshold": Decimal("4161875.00"),
    "progressiveIpnCrossingThreshold": Decimal("11875.00"),
    "annualBasicDeductionRemainder": Decimal("7000.00"),
    "agriculturalSocialTax": Decimal("2351.49"),
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
