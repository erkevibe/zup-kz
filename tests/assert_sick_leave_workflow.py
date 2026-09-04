import json
import sys
from decimal import Decimal


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)

assert actual["mainSickApproved"] is True
assert actual["calculatedTimestampSet"] is True
assert actual["approvalTimestampSet"] is True
assert Decimal(str(actual["grossAmountResult"])) == Decimal("15000.00")
assert actual["overlapRejected"] is True
assert actual["paymentCalculated"] is True
assert actual["usedSickCancellationRejected"] is True
assert actual["unusedSickCancelled"] is True
assert actual["cancellationTimestampSet"] is True
