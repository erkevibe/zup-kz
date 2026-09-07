"""Historical enforcement conditions survive source edits and replacement."""
import json
import sys

d = json.load(sys.stdin)
stage = sys.argv[1]
if stage == 'guard':
    assert d.get('blocked') is True and not d.get('unexpectedWrite'), d
else:
    assert stage in ('first', 'changed', 'replaced'), stage
    expected = dict(recorded=True, percent=10, priority=5,
                    basis='UI: исходные условия 10 процентов', gross=350000,
                    net=290175, amount=29017.5, activeCount=1,
                    legacyUnrecorded=True, legacyPercentAbsent=True, noPayment=True)
    expected['sourcePercent'] = 10 if stage == 'first' else 20
    expected['count'] = 2 if stage == 'replaced' else 1
    expected['currentPercent'] = 20 if stage == 'replaced' else 10
    expected['currentPriority'] = 4 if stage == 'replaced' else 5
    expected['currentAmount'] = 58035 if stage == 'replaced' else 29017.5
    expected['currentBasis'] = ('UI: изменённые условия 20 процентов' if stage == 'replaced'
                                else 'UI: исходные условия 10 процентов')
    for key, value in expected.items():
        assert d.get(key) == value, (key, value, d)
    assert bool(d.get('firstCancelled')) == (stage == 'replaced'), d
print(f'PASS: enforcement history {stage}')
