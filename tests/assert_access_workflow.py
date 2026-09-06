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
assert actual["auditorReadOnly"] is True
assert actual["authenticatedAsRestrictedUser"] is True
assert actual["assignedReadAllowed"] is True
assert actual["hiddenReadBlocked"] is True
assert actual["assignedWriteAllowed"] is True
assert actual["hiddenWriteBlocked"] is True
assert actual["hiddenActionBlocked"] is True
assert actual["hiddenStatusPreserved"] is True
assert actual["hiddenNamePreserved"] is True
