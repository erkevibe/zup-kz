import json
import sys


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)

assert actual["allRolesCreated"] is True
assert actual["userHasHrRole"] is True
assert actual["assignedOrganizationAllowed"] is True
assert actual["hiddenOrganizationRejected"] is True
assert actual["hrPersonnelPermitted"] is True
assert actual["hrPayrollForbidden"] is True
assert actual["auditorReadOnly"] is True
