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
}
for name, value in expected.items():
    assert Decimal(str(actual[name])) == value, (name, actual[name], value)
