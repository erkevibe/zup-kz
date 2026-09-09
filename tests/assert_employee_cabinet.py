import json
import sys


expected_key_sets = [
    {"employeeMapped", "ownSettlementCreated", "foreignSettlementCreated"},
    {
        "ownSettlementAllowed",
        "foreignSettlementDenied",
        "employeeHasNoOrganizationAccess",
        "employeeCannotChangeBinding",
        "administratorCanChangeBinding",
        "employeeCabinetPermitted",
        "employeePayrollForbidden",
        "employeeReadOnly",
    },
]

for path, expected_keys in zip(sys.argv[1:], expected_key_sets, strict=True):
    with open(path, encoding="utf-8") as source:
        result = json.load(source)
    assert set(result) == expected_keys
    assert all(result.values())

print("Employee cabinet access test passed")
