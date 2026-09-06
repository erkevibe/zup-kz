"""Persistent November UI cycle: first calculation, cancellation, replacement."""
import json
import sys

data = json.load(sys.stdin)
stage = sys.argv[1]
assert stage in ('first', 'cancelled', 'prepared', 'approved'), stage
for key in ('payrollStillCalculated', 'noPayment', 'oldMonthsClosed'):
    assert data.get(key) is True, (key, data)
assert (data.get('activeCount') or 0) == (0 if stage == 'cancelled' else 1), data
assert data.get('documentCount') == (1 if stage in ('first', 'cancelled') else 2), data
if stage != 'first':
    for key, value in dict(cancelledAmount=25000, cancelledLines=1,
                           cancelledStamped=True, cancelledSourcePreserved=True).items():
        assert data.get(key) == value, (key, data)
if stage in ('first', 'approved'):
    for key, value in dict(amount=25000, payable=436550, activeLines=1,
                           activeStamped=True).items():
        assert data.get(key) == value, (key, data)
    assert data.get('status') == ('Рассчитан' if stage == 'first' else 'Утверждён'), data
elif stage == 'prepared':
    assert data.get('status') == 'Черновик', data
    assert not data.get('activeStamped') and not data.get('activeLines'), data
print(f'PASS: enforcement cycle {stage}, history and closed months preserved')
