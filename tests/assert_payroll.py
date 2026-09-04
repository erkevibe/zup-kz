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
    "socialSnapshotMzp2026": Decimal("85000.00"),
    "socialSnapshotOpvBase2026": Decimal("148452.38"),
    "socialSnapshotOpvRate2026": Decimal("10.000000"),
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
    "enforcementIncomeAfterTaxes2026": Decimal("130549.28"),
    "defaultOneChildAlimonyPercent": Decimal("25.00"),
    "alimonyWithheld2026": Decimal("25779.99"),
    "damageWithheld2026": Decimal("39494.65"),
    "lowerPriorityWithheld2026": Decimal("0.00"),
    "totalEnforcementWithheld2026": Decimal("65274.64"),
    "payableAfterEnforcement2026": Decimal("67274.64"),
    "payslipAccrued2026": Decimal("155452.38"),
    "payslipOpv2026": Decimal("14845.24"),
    "payslipVosms2026": Decimal("2969.05"),
    "payslipIpn2026": Decimal("88.81"),
    "payslipEnforcement2026": Decimal("65274.64"),
    "payslipPayable2026": Decimal("67274.64"),
    "paymentStatementAmount2026": Decimal("67274.64"),
    "remainingAfterPayment2026": Decimal("0.00"),
    "unpaidAfterPayment2026": Decimal("0.00"),
    "bankRegisterAmount2026": Decimal("67274.64"),
    "opvLiability2026": Decimal("14845.24"),
    "totalPayrollLiability2026": Decimal("42071.15"),
    "overdueLiabilityCount2026": Decimal("2"),
    "socialTransferAmount2026": Decimal("14845.24"),
    "socialTransferExpected2026": Decimal("14845.24"),
    "socialTransferDifference2026": Decimal("0.00"),
    "socialTransferOpvrAmount2026": Decimal("5195.83"),
    "socialTransferSoAmount2026": Decimal("6680.36"),
    "socialTransferVosmsAmount2026": Decimal("2969.05"),
    "socialTransferOosmsAmount2026": Decimal("4453.57"),
    "form200LineCount2026": Decimal("3"),
    "form200Quarter2026": Decimal("1"),
    "form200TotalAccrued2026": Decimal("155452.38"),
    "form200TotalCalculatedIpn2026": Decimal("88.81"),
    "form200TotalPaidIncome2026": Decimal("155452.38"),
    "form200TotalTaxableIncome2026": Decimal("888.09"),
    "form200TotalOpvBase2026": Decimal("148452.38"),
    "form200TotalOpvrBase2026": Decimal("148452.38"),
    "form200TotalSocialTaxBase2026": Decimal("130638.09"),
    "form200TotalSoBase2026": Decimal("133607.14"),
    "form200TotalOosmsBase2026": Decimal("148452.38"),
    "form200TotalVosmsBase2026": Decimal("148452.38"),
    "form200TotalIpn2026": Decimal("88.81"),
    "form200TotalOpv2026": Decimal("14845.24"),
    "form200TotalSocialTax2026": Decimal("7838.29"),
    "form200TotalSo2026": Decimal("6680.36"),
    "form200TotalOosms2026": Decimal("4453.57"),
    "form200TotalVosms2026": Decimal("2969.05"),
    "form200TotalOpvr2026": Decimal("5195.83"),
    "form200JanuaryIpn2026": Decimal("0.00"),
    "form200FebruaryIpn2026": Decimal("88.81"),
    "form200JanuarySocialTax2026": Decimal("7838.29"),
    "form200FebruaryOpv2026": Decimal("14845.24"),
    "form200JanuaryCalculatedIpn2026": Decimal("88.81"),
    "form200FebruaryPaidIncome2026": Decimal("155452.38"),
    "form20005LineCount2026": Decimal("2"),
    "form20005Year2026": Decimal("2026"),
    "form20005IncomeStatus2026": Decimal("1"),
    "taxIncomeStatusEmployeeCode": Decimal("1"),
    "taxIncomeStatusCivilContractCode": Decimal("2"),
    "taxIncomeStatusOtherCode": Decimal("11"),
    "form20005AccruedIncome2026": Decimal("155452.38"),
    "form20005OpvCalculated2026": Decimal("14845.24"),
    "form20005VosmsCalculated2026": Decimal("2969.05"),
    "form20005TaxDeduction2026": Decimal("129750.00"),
    "form20005IpnCalculated2026": Decimal("88.81"),
    "form20005UnpaidIncome2026": Decimal("0.00"),
    "form20005PaidIncome2026": Decimal("155452.38"),
    "form20005IpnPayable2026": Decimal("88.81"),
    "form20005OpvPayable2026": Decimal("14845.24"),
    "form20005VosmsPayable2026": Decimal("2969.05"),
    "form20005SocialTaxIncome2026": Decimal("130638.09"),
    "form20005SocialTaxCalculated2026": Decimal("7838.29"),
    "form20005So2026": Decimal("6680.36"),
    "form20005SocialTaxPayable2026": Decimal("7838.29"),
    "form20005Oppv2026": Decimal("0.00"),
    "form20005Oosms2026": Decimal("4453.57"),
    "form20005Opvr2026": Decimal("5195.83"),
    "civilActOpv2026": Decimal("100000.00"),
    "civilActVosms2026": Decimal("20000.00"),
    "civilActSoBase2026": Decimal("595000.00"),
    "civilActSo2026": Decimal("29750.00"),
    "civilActTaxableIncome2026": Decimal("850250.00"),
    "civilActIpn2026": Decimal("85025.00"),
    "civilActPayable2026": Decimal("765225.00"),
    "form20005CivilStatus2026": Decimal("2"),
    "form20005CivilAccrued2026": Decimal("1000000.00"),
    "form20005CivilOpv2026": Decimal("100000.00"),
    "form20005CivilVosms2026": Decimal("20000.00"),
    "form20005CivilIpn2026": Decimal("85025.00"),
    "form20005CivilSo2026": Decimal("29750.00"),
    "form20005CivilPaidIncome2026": Decimal("1000000.00"),
    "form20005CivilOosms2026": Decimal("0.00"),
    "form20005CivilOpvr2026": Decimal("0.00"),
    "civilLiabilityLineCount2026": Decimal("4"),
    "civilLiabilityTotal2026": Decimal("234775.00"),
    "civilLiabilityOpv2026": Decimal("100000.00"),
    "civilLiabilitySo2026": Decimal("29750.00"),
    "civilLiabilityVosms2026": Decimal("20000.00"),
    "civilLiabilityIpn2026": Decimal("85025.00"),
    "ordinaryLowIncomeEnforcementCap": Decimal("29149.00"),
    "protectedLowIncomeEnforcementCap": Decimal("40000.00"),
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
    # lsFusion omits a computed property from JSON when its value is NULL.
    # Aggregate monetary properties use that representation for an empty sum.
    actual_value = actual.get(name, 0)
    assert Decimal(str(actual_value)) == value, (name, actual_value, value)

assert actual["scheduledLeavePaymentDue"] == "2026-07-08"
assert actual["outsideSchedulePaymentDue"] == "2026-07-16"
assert actual["payrollMarkedPaid2026"] is True
assert actual["latePaymentDetected2026"] is True
assert actual["bankRegisterAccepted2026"] is True
assert actual["bankRegisterEmployeeIin2026"] == "900101300000"
assert actual["liabilitiesPaid2026"] is True
assert actual["latestPayrollPaymentDate2026"] == "2026-02-10"
assert actual["opvLiabilityDue2026"] == "2026-03-25"
assert actual["socialContributionDue2026"] == "2026-02-25"
assert actual["ipnLiabilityDue2026"] == "2026-03-25"
assert actual["socialTransferRecipient2026"] == "ЕНПФ"
assert actual["socialTransferGfssRecipient2026"] == "ГФСС"
assert actual["socialTransferFsmsRecipient2026"] == "ФСМС"
assert actual["socialTransferPeriod2026"] == "2026-01-01"
assert actual["socialTransferAccepted2026"] is True
assert actual["socialTransferEmployeeIin2026"] == "900101300000"
assert actual["form200DueDate2026"] == "2026-05-15"
assert actual["form200Accepted2026"] is True
assert actual["form20005EmployeeName2026"] == "Тестов Работник Первый"
assert actual["form20005EmployeeIin2026"] == "900101300000"
assert actual["form20005CategoryCodes2026"] == "3,4"
assert actual["form20005TaxDeductionCodes2026"] == "1"
assert actual["civilActPaid2026"] is True
assert actual["civilLiabilityDueDate2026"] == "2026-03-25"
assert actual["civilLiabilityPaid2026"] is True
