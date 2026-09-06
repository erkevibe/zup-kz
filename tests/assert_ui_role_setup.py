import json
import sys


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)

expected_key_sets = [
    {"hrReady", "timeReady", "payrollReady", "chiefReady", "auditorReady"},
    {
        "hrPersonnelPermitted",
        "hrPayrollForbidden",
        "timeWorkingTimePermitted",
        "payrollPayrollPermitted",
        "chiefReportsPermitted",
        "auditorReadOnly",
    },
]

assert set(actual) in expected_key_sets
assert all(actual.values())
