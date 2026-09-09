import json
import sys
from decimal import Decimal


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source, parse_float=Decimal)

for name in (
    "baselinePackApproved",
    "baselineSocialParametersComplete",
    "baselineTaxParametersComplete",
    "futurePackMissing",
    "futureSocialBlocked",
    "futureTaxBlocked",
):
    assert actual.get(name) is True, (name, actual.get(name))

expected_parameters = {
    "mzp": Decimal("85000"),
    "mrp": Decimal("4325"),
    "livingMinimum": Decimal("50851"),
    "overtimeCoefficient": Decimal("1.5"),
    "holidayCoefficient": Decimal("1.5"),
    "nightCoefficient": Decimal("1.5"),
    "sickLeaveCapMrp": Decimal("25"),
    "opvRate": Decimal("10"),
    "opvMaxMzp": Decimal("50"),
    "opvrRate": Decimal("3.5"),
    "opvrMinMzp": Decimal("1"),
    "opvrMaxMzp": Decimal("50"),
    "socialContributionRate": Decimal("5"),
    "socialContributionMinMzp": Decimal("1"),
    "socialContributionMaxMzp": Decimal("7"),
    "employeeOsmsRate": Decimal("2"),
    "employeeOsmsMaxMzp": Decimal("20"),
    "employerOsmsRate": Decimal("3"),
    "employerOsmsMaxMzp": Decimal("40"),
    "ipnBaseRate": Decimal("10"),
    "ipnHighRate": Decimal("15"),
    "ipnThresholdMrp": Decimal("8500"),
    "ipnBasicMonthlyMrp": Decimal("30"),
    "ipnBasicAnnualMrp": Decimal("360"),
    "ipnSocialStandardMrp": Decimal("882"),
    "ipnSocialDisabilityMrp": Decimal("5000"),
    "socialTaxRate": Decimal("6"),
    "agriculturalSocialTaxRate": Decimal("1.8"),
    "enforcementMaxRate": Decimal("50"),
    "alimonyOneChildRate": Decimal("25"),
    "alimonyTwoChildrenRate": Decimal("33.333333"),
    "alimonyThreeChildrenRate": Decimal("50"),
}

for name, expected in expected_parameters.items():
    assert Decimal(str(actual.get(name))) == expected, (name, actual.get(name), expected)
