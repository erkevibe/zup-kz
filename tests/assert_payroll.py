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
}
for name, value in expected.items():
    assert Decimal(str(actual[name])) == value, (name, actual[name], value)
