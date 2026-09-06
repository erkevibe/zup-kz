"""Read-only check of the persistent UI fixture; pipe detail verification JSON here."""
import json
import sys

data = json.load(sys.stdin)
for key, expected in {'augustCount': 2, 'septemberCount': 1, 'augustSalary': 350000,
                      'augustBonus': 50000, 'augustAccrued': 400000, 'allowed': True}.items():
    assert data.get(key) == expected, (key, data)
# lsFusion omits a null GROUP SUM when no rows match.
assert not data.get('crossPeriodLeaks'), data
assert data['augustSalary'] + data['augustBonus'] == data['augustAccrued'], data
print('PASS: two August lines, one September line, no cross-period leakage')
