import json
import sys
from decimal import Decimal


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)

assert actual["annualLeaveApproved"] is True
assert actual["approvalTimestampSet"] is True
assert Decimal(str(actual["chargedDaysResult"])) == Decimal("3")
assert Decimal(str(actual["grossAmountResult"])) == Decimal("15000.00")
assert Decimal(str(actual["remainingDaysResult"])) == Decimal("21.00")
assert actual["overlapRejected"] is True
assert actual["paymentCalculated"] is True
assert actual["usedLeaveCancellationRejected"] is True
assert actual["unusedLeaveCancelled"] is True
assert actual["cancellationTimestampSet"] is True
