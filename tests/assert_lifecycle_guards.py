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
    "personnelEventStatusBlocked": True,
    "esutdStatusBlocked": True,
    "esutdResponseBlocked": True,
    "paymentStatementStatusBlocked": True,
    "paymentStatementSnapshotBlocked": True,
    "form200StatusBlocked": True,
    "form200SnapshotBlocked": True,
    "approvalStatusBlocked": True,
    "approvalStepStatusBlocked": True,
    "archiveStatusBlocked": True,
    "archiveDocumentStatusBlocked": True,
    "insurancePolicyStatusBlocked": True,
    "insurancePolicySnapshotBlocked": True,
    "workAccidentStatusBlocked": True,
    "insuranceClaimStatusBlocked": True,
    "timesheetStatusPreserved": True,
    "payrollStatusPreserved": True,
    "socialStatusPreserved": True,
    "payrollSnapshotPreserved": True,
    "taxSnapshotPreserved": True,
    "personnelEventStatusPreserved": True,
    "esutdStatusPreserved": True,
    "esutdResponsePreserved": True,
    "paymentStatementStatusPreserved": True,
    "paymentStatementSnapshotPreserved": True,
    "form200StatusPreserved": True,
    "form200SnapshotPreserved": True,
    "approvalStatusPreserved": True,
    "approvalStepStatusPreserved": True,
    "archiveStatusPreserved": True,
    "archiveDocumentStatusPreserved": True,
    "insurancePolicyStatusPreserved": True,
    "insurancePolicySnapshotPreserved": True,
    "workAccidentStatusPreserved": True,
    "insuranceClaimStatusPreserved": True,
}

for key, expected_value in expected.items():
    actual_value = result.get(key)
    assert actual_value == expected_value, (
        f"{key}: expected {expected_value!r}, got {actual_value!r}"
    )
