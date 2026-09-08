import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LSF_ROOT = ROOT / "src/main/lsfusion/zupkz"
PRIMARY_GUARDS = LSF_ROOT / "core/AccessControl.lsf"
SECONDARY_GUARDS = LSF_ROOT / "core/OrganizationAccessSecondary.lsf"

PRIMARY_CLASSES = {
    "Organization", "Department", "Position", "StaffPosition", "Employment",
    "EmploymentAssignment", "PersonnelEvent", "EmployeeCard",
    "EmployeeIdentityDocument", "EmployeeEducation", "EmployeeFamilyMember",
    "EmployeeMilitaryRecord", "EmployeePreviousEmployment", "WorkSchedule",
    "ShiftTemplate", "ScheduleCycleDay", "EmployeeScheduleAssignment", "Timesheet",
    "TimesheetLine", "PayrollRun", "PayrollInput",
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
    "SalaryBankRegister", "SalaryBankRegisterLine", "PayrollLiabilityDocument",
    "PayrollLiabilityLine", "SocialPaymentProfile", "SocialPaymentDocument",
    "SocialPaymentLine", "EmployeeTaxProfile", "OrganizationTaxProfile",
    "TaxCalculationDocument", "TaxCalculationLine", "PersonalTaxLedgerEntry",
    "SocialTransferRegister", "SocialTransferRegisterLine", "Form200Declaration",
    "Form200MonthLine", "Form20005Line",
}

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

for class_name in sorted(SECONDARY_CLASSES):
    invocation = re.compile(
        rf"@protectSecondaryOrganizationObject\([^,]+,\s*{class_name},"
    )
    if not invocation.search(secondary_source):
        missing.append(f"{class_name}: no secondary deletion/mutation guard")

assert not missing, "\n".join(missing)
print(
    f"ORGANIZATION_GUARD_COVERAGE_OK classes={len(PRIMARY_CLASSES | SECONDARY_CLASSES)}"
)
