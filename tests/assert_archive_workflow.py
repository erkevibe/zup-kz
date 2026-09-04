#!/usr/bin/env python3
import json
import sys

with open(sys.argv[1], encoding="utf-8") as result_file:
    result = json.load(result_file)

expected = {
    "caseStored": True,
    "ruleSnapshotYears": 5,
    "retentionUntilResult": "2025-12-31",
    "documentDestroyed": True,
    "electronicFileRemoved": True,
    "destructionMetadataKept": True,
    "permanentDocumentStored": True,
    "permanentRuleSnapshot": True,
    "inventoryPdfGenerated": True,
}

for key, expected_value in expected.items():
    actual_value = result.get(key)
    assert actual_value == expected_value, (
        f"{key}: expected {expected_value!r}, got {actual_value!r}"
    )
