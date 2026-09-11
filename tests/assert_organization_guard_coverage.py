import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LSF_ROOT = ROOT / "src/main/lsfusion/zupkz"
PRIMARY_GUARDS = LSF_ROOT / "core/AccessControl.lsf"
SECONDARY_GUARDS = LSF_ROOT / "core/OrganizationAccessSecondary.lsf"

PRIMARY_CLASSES = {
    "Organization", "Department", "Position", "StaffPosition", "Employee", "Employment",
    "EmploymentAssignment", "PersonnelEvent", "EmployeeCard",
    "EmployeeIdentityDocument", "EmployeeEducation", "EmployeeFamilyMember",
    "EmployeeMilitaryRecord", "EmployeePreviousEmployment", "WorkSchedule",
    "ShiftTemplate", "ScheduleCycleDay", "EmployeeScheduleAssignment", "Timesheet",
    "TimesheetLine", "PayrollRun", "PayrollInput",
}

PRIMARY_ROLE_GUARDS = {
    "Organization": "masterDataChangeRoleAllowed",
    "Department": "masterDataChangeRoleAllowed",
    "Position": "masterDataChangeRoleAllowed",
    "StaffPosition": "masterDataChangeRoleAllowed",
    "Employee": "employeeMasterDataChangeAllowed",
    "Employment": "personnelChangeRoleAllowed",
    "EmploymentAssignment": "personnelChangeRoleAllowed",
    "PersonnelEvent": "personnelChangeRoleAllowed",
    "EmployeeCard": "personnelChangeRoleAllowed",
    "EmployeeIdentityDocument": "personnelChangeRoleAllowed",
    "EmployeeEducation": "personnelChangeRoleAllowed",
    "EmployeeFamilyMember": "personnelChangeRoleAllowed",
    "EmployeeMilitaryRecord": "personnelChangeRoleAllowed",
    "EmployeePreviousEmployment": "personnelChangeRoleAllowed",
    "WorkSchedule": "workingTimeChangeRoleAllowed",
    "ShiftTemplate": "workingTimeChangeRoleAllowed",
    "ScheduleCycleDay": "workingTimeChangeRoleAllowed",
    "EmployeeScheduleAssignment": "workingTimeChangeRoleAllowed",
    "Timesheet": "workingTimeChangeRoleAllowed",
    "TimesheetLine": "workingTimeChangeRoleAllowed",
    "PayrollRun": "payrollChangeRoleAllowed",
    "PayrollInput": "payrollChangeRoleAllowed",
}

PRIMARY_DELETE_ROLE_GUARDS = {
    **PRIMARY_ROLE_GUARDS,
    "Employee": "employeeMasterDataDeleteAllowed",
}

SECONDARY_CLASSES = {
    "LeaveEntitlement", "LeaveDocument", "VacationSchedule", "VacationScheduleLine",
    "BusinessTripDocument", "PersonnelNotice", "ApprovalRequest", "ApprovalStep",
    "PersonnelNotification", "ArchiveCase", "ArchiveDocument",
    "AccidentInsurancePolicy", "WorkAccident", "AccidentInsuranceClaim",
    "PayrollTimeSummary", "PayrollLine", "AverageEarningsDocument",
    "AverageEarningsBaseLine", "PayrollRecalculation", "PayrollRecalculationLine",
    "InterimPayment", "SickLeaveDocument", "SickLeaveBenefitLine", "EnforcementOrder",
    "EnforcementCalculationDocument", "EnforcementCalculationLine", "CivilContract",
    "CivilContractAct", "CivilLiabilityDocument", "CivilLiabilityLine",
    "PayrollSettlementLine", "PaymentStatement", "PaymentStatementLine",
    "SalaryBankRegister", "SalaryBankRegisterLine", "EmployeePaymentAccount",
    "PayrollLiabilityDocument",
    "PayrollLiabilityLine", "SocialPaymentProfile", "SocialPaymentDocument",
    "SocialPaymentLine", "EmployeeTaxProfile", "OrganizationTaxProfile",
    "TaxCalculationDocument", "TaxCalculationLine", "PersonalTaxLedgerEntry",
    "SocialTransferRegister", "SocialTransferRegisterLine", "Form200Declaration",
    "Form200MonthLine", "Form20005Line",
}


def role_map(classes, role):
    return {class_name: role for class_name in classes}


SECONDARY_ROLE_GUARDS = {
    **role_map({
        "LeaveEntitlement", "LeaveDocument", "VacationSchedule",
        "VacationScheduleLine", "BusinessTripDocument", "PersonnelNotice",
        "ApprovalRequest", "ApprovalStep", "PersonnelNotification", "ArchiveCase",
        "ArchiveDocument", "AccidentInsurancePolicy", "WorkAccident",
        "AccidentInsuranceClaim", "SickLeaveDocument",
    }, "personnelChangeRoleAllowed"),
    **role_map({
        "PayrollTimeSummary", "PayrollLine", "AverageEarningsDocument",
        "AverageEarningsBaseLine", "PayrollRecalculation", "PayrollRecalculationLine",
        "InterimPayment", "SickLeaveBenefitLine", "CivilContract", "CivilContractAct",
        "PayrollSettlementLine", "PaymentStatement", "PaymentStatementLine",
        "SalaryBankRegister", "SalaryBankRegisterLine",
    }, "payrollChangeRoleAllowed"),
    "EmployeePaymentAccount": "masterDataChangeRoleAllowed",
    **role_map({
        "EnforcementOrder", "EnforcementCalculationDocument",
        "EnforcementCalculationLine", "CivilLiabilityDocument", "CivilLiabilityLine",
        "PayrollLiabilityDocument", "PayrollLiabilityLine", "SocialPaymentProfile",
        "SocialPaymentDocument", "SocialPaymentLine", "EmployeeTaxProfile",
        "OrganizationTaxProfile", "TaxCalculationDocument", "TaxCalculationLine",
        "PersonalTaxLedgerEntry", "SocialTransferRegister",
        "SocialTransferRegisterLine", "Form200Declaration", "Form200MonthLine",
        "Form20005Line",
    }, "taxesReportsChangeRoleAllowed"),
}

assert set(PRIMARY_ROLE_GUARDS) == PRIMARY_CLASSES
assert set(SECONDARY_ROLE_GUARDS) == SECONDARY_CLASSES

all_source = "\n".join(path.read_text(encoding="utf-8") for path in LSF_ROOT.rglob("*.lsf"))
primary_source = PRIMARY_GUARDS.read_text(encoding="utf-8")
secondary_source = SECONDARY_GUARDS.read_text(encoding="utf-8")
guard_source = primary_source + "\n" + secondary_source

data_property = re.compile(
    r"(?m)^([A-Za-z][A-Za-z0-9_]*)[^\n=]*=\s*DATA(?!\s+LOCAL\b)"
    r"(?:(?!;).)*\(([A-Za-z][A-Za-z0-9_]*)\)\s*;",
    re.S,
)
properties = {}
for property_name, class_name in data_property.findall(all_source):
    properties.setdefault(class_name, set()).add(property_name)

missing = []
for class_name in sorted(PRIMARY_CLASSES | SECONDARY_CLASSES):
    if not properties.get(class_name):
        missing.append(f"{class_name}: no DATA properties found")
        continue
    for property_name in sorted(properties[class_name]):
        if f"CHANGED({property_name}(" not in guard_source:
            missing.append(f"{class_name}.{property_name}: no mutation guard")

for class_name in sorted(PRIMARY_CLASSES):
    if f"DROPPED({class_name} " not in primary_source:
        missing.append(f"{class_name}: no deletion guard")
    role_guard = PRIMARY_ROLE_GUARDS[class_name]
    mutation_guard = re.compile(
        rf"CONSTRAINT\s+\w+ContentChanged\({class_name}\s+\w+\)"
        rf"(?:(?!MESSAGE)[\s\S])*?{role_guard}\(",
    )
    delete_role_guard = PRIMARY_DELETE_ROLE_GUARDS[class_name]
    deletion_guard = re.compile(
        rf"CONSTRAINT\s+DROPPED\({class_name}\s+\w+\s+IS\s+{class_name}\)"
        rf"(?:(?!MESSAGE)[\s\S])*?{delete_role_guard}\(",
    )
    if not mutation_guard.search(primary_source):
        missing.append(f"{class_name}: no {role_guard} mutation role guard")
    if not deletion_guard.search(primary_source):
        missing.append(f"{class_name}: no {delete_role_guard} deletion role guard")

for class_name in sorted(SECONDARY_CLASSES):
    role_guard = SECONDARY_ROLE_GUARDS[class_name]
    invocation = re.compile(
        rf"@protectSecondaryOrganizationObject\([^,]+,\s*{class_name},\s*"
        rf"[^,]+,\s*{role_guard}\s*\);"
    )
    if not invocation.search(secondary_source):
        missing.append(
            f"{class_name}: no secondary deletion/mutation {role_guard} guard"
        )

assert not missing, "\n".join(missing)
print(
    f"ORGANIZATION_GUARD_COVERAGE_OK classes={len(PRIMARY_CLASSES | SECONDARY_CLASSES)}"
)
