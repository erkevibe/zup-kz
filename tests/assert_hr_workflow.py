import json
import sys
from decimal import Decimal


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)

assert actual["hirePosted"] is True
assert actual["transferPosted"] is True
assert actual["terminationCancelled"] is True
assert actual["backdatedRejected"] is True
assert actual["earlierCancellationRejected"] is True
assert actual["hireDateResult"] == "2026-01-10"
assert actual["contractEndRestored"] is True
assert Decimal(str(actual["assignmentCountResult"])) == Decimal("2")
assert actual["firstAssignmentTo"] == "2026-01-31"
assert actual["currentStaffIsTransferred"] is True
assert actual["currentAssignmentRestored"] is True
