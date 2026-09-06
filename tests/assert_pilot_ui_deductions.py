"""Check the persistent October UI fixture; read verification JSON from stdin."""
import json
import sys

data = json.load(sys.stdin)
expected = {
    'closed': True, 'settlementCount': 2, 'firstAccrued': 350000,
    'firstOther': 15000, 'firstEnforcement': 20000, 'firstWithheld': 94825,
    'firstPayable': 255175, 'firstLines': 2, 'secondAccrued': 200000,
    'secondOther': 4000, 'secondWithheld': 32625, 'secondPayable': 167375,
    'secondLines': 2, 'noPayment': True,
}
for key, value in expected.items():
    assert data.get(key) == value, (key, value, data)
assert not data.get('secondEnforcement'), data
assert not data.get('wrongEmployeeLines'), data
for prefix in ('first', 'second'):
    assert data[prefix + 'Accrued'] - data[prefix + 'Withheld'] == data[prefix + 'Payable'], data
print('PASS: October deductions, two isolated payslips, correct balances, no payment')
