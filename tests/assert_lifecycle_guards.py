#!/usr/bin/env python3
import json
import sys

result = {}
for result_path in sys.argv[1:]:
    with open(result_path, encoding="utf-8") as result_file:
        result.update(json.load(result_file))

expected = {
    "setupSucceeded": True,
    "timesheetStatusBlocked": True,
    "payrollStatusBlocked": True,
    "socialStatusBlocked": True,
    "payrollSnapshotBlocked": True,
    "payrollSnapshotDeleteBlocked": True,
    "taxSnapshotBlocked": True,
    "timesheetStatusPreserved": True,
    "payrollStatusPreserved": True,
    "socialStatusPreserved": True,
    "payrollSnapshotPreserved": True,
    "taxSnapshotPreserved": True,
}

for key, expected_value in expected.items():
    actual_value = result.get(key)
    assert actual_value == expected_value, (
        f"{key}: expected {expected_value!r}, got {actual_value!r}"
    )
