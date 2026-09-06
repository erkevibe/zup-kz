"""Negative organization-access check; pipe isolated auditor verification JSON here."""
import json
import sys

data = json.load(sys.stdin)
assert data.get('authenticated') == 'ui-auditor-isolated', data
for key in ('payrollRole', 'isolatedOrganizationAllowed', 'targetExists', 'nullDenied'):
    assert data.get(key) is True, (key, data)
for key in ('organizationAllowed', 'targetAllowed', 'visibleCount'):
    assert not data.get(key), (key, data)
print('PASS: auditor role retained, existing foreign payslip denied, visible list empty')
