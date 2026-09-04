#!/usr/bin/env python3
import json
import sys

with open(sys.argv[1], encoding="utf-8") as result_file:
    result = json.load(result_file)
if len(sys.argv) > 2:
    with open(sys.argv[2], encoding="utf-8") as verification_file:
        result.update(json.load(verification_file))

expected = {
    "requestApproved": True,
    "firstStepApproved": True,
    "secondStepApproved": True,
    "hirePosted": True,
    "postingBlockedBeforeApproval": True,
    "approvalNotifications": 3,
    "firstNotificationRead": True,
    "noticeDelivered": True,
    "noticeDaysProvided": 15,
    "noticeDeadlineMet": True,
    "workConditionsLeadDays": 15,
    "rejectedRequestRejected": True,
    "rejectedNotifications": 2,
}

for key, expected_value in expected.items():
    actual_value = result.get(key)
    assert actual_value == expected_value, (
        f"{key}: expected {expected_value!r}, got {actual_value!r}"
    )
