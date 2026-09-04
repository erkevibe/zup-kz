import json
import sys


with open(sys.argv[1], encoding="utf-8") as result_file:
    result = json.load(result_file)

expected = {
    "cardReady": True,
    "employeeName": "Карточкин Тест Кадрович",
    "cardOrganizationMatches": True,
    "identityDocuments": 1,
    "educationRecords": 1,
    "familyMembers": 1,
    "militaryRecords": 1,
    "previousEmployments": 1,
    "internalAssignments": 1,
    "pdfGenerated": True,
}

for key, expected_value in expected.items():
    actual_value = result.get(key)
    assert actual_value == expected_value, (
        f"{key}: expected {expected_value!r}, got {actual_value!r}"
    )
