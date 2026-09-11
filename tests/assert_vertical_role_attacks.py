import json
import sys


actual = {}
for result_path in sys.argv[1:]:
    with open(result_path, encoding="utf-8") as source:
        actual.update(json.load(source))

expected_true = (
    "assignedPaymentAccountReadAllowed",
    "hiddenPaymentAccountReadBlocked",
    "paymentAccountOverlapRejected",
    "paymentAccountOverlapEditRejected",
    "timekeeperEmployeeWritePreserved",
    "timekeeperOrganizationWritePreserved",
    "payrollAccountWritePreserved",
    "payrollDepartmentWritePreserved",
    "timekeeperPayrollAttackRejected",
    "payrollWorkingTimeAttackRejected",
    "payrollPersonnelAttackRejected",
    "payrollTaxesAttackRejected",
    "hiddenPaymentAccountMutationRejected",
    "hiddenPaymentAccountReparentRejected",
    "hiddenPaymentAccountDeleteRejected",
    "hiddenEmployeePaymentAccountRejected",
    "hiddenEmployeeEmploymentRejected",
    "overlapEditStatePreserved",
)
for name in expected_true:
    assert actual[name] is True, (name, actual.get(name))
