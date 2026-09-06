"""Check one rejected API mutation of the persistent October enforcement snapshot."""
import json
import sys

data = json.load(sys.stdin)
assert data.get('blocked') is True, data
assert data.get('amount') == 20000, data
assert data.get('sourcePreserved') is True, data
assert not data.get('unexpectedWrite') and not data.get('fixtureError'), data
print('PASS: mutation blocked, original enforcement amount and source preserved')
