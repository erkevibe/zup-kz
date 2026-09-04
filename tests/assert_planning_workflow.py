import json
import sys


with open(sys.argv[1], encoding="utf-8") as result_file:
    result = json.load(result_file)

expected = {
    "scheduleApproved": True,
    "plannedDays": 14,
    "leaveDraftCreated": True,
    "schedulePdfGenerated": True,
    "tripApproved": True,
    "tripCalendarDaysResult": 3,
    "tripWorkDaysResult": 3,
    "tripLines": 3,
    "tripPayResult": 30000,
    "tripAdvanceResult": 140000,
    "tripPdfGenerated": True,
    "cancellableTripCancelled": True,
}

for key, expected_value in expected.items():
    actual_value = result.get(key)
    assert actual_value == expected_value, (
        f"{key}: expected {expected_value!r}, got {actual_value!r}"
    )
