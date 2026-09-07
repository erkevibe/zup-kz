"""A rejected source mutation must not transfer a calculated withholding."""
import json
import sys

data = json.load(sys.stdin)
if len(sys.argv) > 1:
    assert data.get('owner') == sys.argv[1], data
    for key in ('unused', 'inactive', 'usedOwnerPreserved'):
        assert data.get(key) is True, (key, data)
    print('PASS: unused document owner editable, used document owner preserved')
    sys.exit(0)
for key in ('blocked', 'ownerPreserved', 'organizationPreserved',
            'taxRunPreserved', 'taxSocialPreserved', 'socialRunPreserved'):
    assert data.get(key) is True, (key, data)
assert data.get('firstAmount') == 25000, data
assert not data.get('secondAmount'), data
assert not data.get('unexpectedWrite') and not data.get('fixtureError'), data
print('PASS: source mutation blocked, withholding belongs to original employee')
