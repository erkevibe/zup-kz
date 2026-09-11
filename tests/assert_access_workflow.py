import json
import sys


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)
for result_path in sys.argv[2:]:
    with open(result_path, encoding="utf-8") as source:
        actual.update(json.load(source))

assert actual["allRolesCreated"] is True
assert actual["userHasHrRole"] is True
assert actual["assignedOrganizationAllowed"] is True
assert actual["hiddenOrganizationRejected"] is True
assert actual["hrPersonnelPermitted"] is True
assert actual["hrPayrollForbidden"] is True
assert actual["hrUiTestForbidden"] is True
assert actual["chiefUiTestForbidden"] is True
assert actual["chiefAdministrationForbidden"] is True
assert actual["auditorAdministrationForbidden"] is True
assert actual["chiefDesignForbidden"] is True
assert actual["selfRegistrationDisabled"] is True
assert actual["auditorReadOnly"] is True
assert actual["authenticatedAsRestrictedUser"] is True
assert actual["assignedReadAllowed"] is True
assert actual["hiddenReadBlocked"] is True
assert actual["assignedWriteAllowed"] is True
assert actual["hiddenWriteBlocked"] is True
assert actual["hiddenActionBlocked"] is True
assert actual["hiddenStatusPreserved"] is True
assert actual["hiddenNamePreserved"] is True
assert actual["hiddenDepartmentPreserved"] is True
assert actual["hiddenDepartmentOwnerPreserved"] is True
assert actual["hiddenDraftPreserved"] is True
assert actual["hiddenPayrollPreserved"] is True
assert actual["hiddenDeletePreserved"] is True
assert actual["hiddenArchiveDocumentPreserved"] is True
assert actual["hiddenArchiveOwnerPreserved"] is True
assert actual["hiddenNoticeDeletePreserved"] is True
assert actual["hiddenEnforcementPreserved"] is True
assert actual["hiddenPaymentPreserved"] is True
assert actual["hiddenReportPreserved"] is True
assert actual["created"] is True
assert actual["organizationAOldSelected"] is True
assert actual["organizationANewSelected"] is True
assert actual["organizationBSelected"] is True
assert actual["noAccountBeforeValidity"] is True
assert actual["paymentAccountOverlapRejected"] is True
assert actual["timekeeperOwnDomainAllowed"] is True
assert actual["payrollOwnDomainAllowed"] is True
assert actual["hrOwnDomainAllowed"] is True
assert actual["chiefTaxesDomainAllowed"] is True
assert actual["singleOrganizationLegacyMigrated"] is True
assert actual["migrationPreservedEffectiveDate"] is True
assert actual["ambiguousLegacyNotMigrated"] is True
assert actual["ambiguousLegacyReported"] is True
assert actual["employeeIinFormatRejected"] is True
assert actual["organizationBinFormatRejected"] is True
assert actual["bankDetailsFormatRejected"] is True
