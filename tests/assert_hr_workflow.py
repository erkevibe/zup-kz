import json
import sys
from decimal import Decimal


actual = {}
for result_path in sys.argv[1:]:
    with open(result_path, encoding="utf-8") as source:
        actual.update(json.load(source))

assert actual["hirePosted"] is True
assert actual["transferPosted"] is True
assert actual["hireAcceptedByEsutd"] is True
assert actual["transferResubmittedAndAccepted"] is True
assert actual["esutdSubmittedTimestampSet"] is True
assert actual["esutdRespondedTimestampSet"] is True
assert actual["esutdExternalIdResult"] == "ESUTD-HIRE-1"
assert actual["terminationCancelled"] is True
assert actual["backdatedRejected"] is True
assert actual["earlierCancellationRejected"] is True
assert actual["hireDateResult"] == "2026-01-10"
assert actual["contractEndRestored"] is True
assert Decimal(str(actual["assignmentCountResult"])) == Decimal("2")
assert actual["firstAssignmentTo"] == "2026-01-31"
assert actual["currentStaffIsTransferred"] is True
assert actual["currentAssignmentRestored"] is True
assert actual["employeeDisplayName"] == "Кадров Тест"
assert actual["contractEmployeeDisplayName"] == "Кадров Тест"
assert actual["assignmentEmployeeDisplayName"] == "Кадров Тест"
assert actual["transferDefaultsFromCurrentAssignment"] is True
assert actual["employmentLegacyFieldsRejected"] is True
assert actual["employmentLegacySalaryPreserved"] is True
assert Decimal(str(actual["employmentCurrentSalaryResult"])) == Decimal("200000.00")
assert actual["employmentCurrentPositionFromAssignment"] is True
