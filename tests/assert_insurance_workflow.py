import json
import sys


with open(sys.argv[1], encoding="utf-8") as result_file:
    result = json.load(result_file)

expected = {
    "rateSnapshot": 1.5,
    "premium": 150000.0,
    "policyActive": True,
    "accidentCovered": True,
    "accidentClosed": True,
    "accidentWorkRelated": True,
    "claimPaid": True,
    "acceptedAmount": 450000.0,
    "paidAmount": 450000.0,
    "uninsuredRegistered": True,
    "uninsuredFlag": True,
    "accidentPdfGenerated": True,
}

if result != expected:
    raise AssertionError(f"unexpected insurance workflow result: {result!r}")

print("Insurance workflow test passed")
