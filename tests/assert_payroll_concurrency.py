import json
import sys


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)

assert actual == {
    "status": "Утверждён",
    "settlementLineCount": 1,
    "employeeLineCount": 1,
    "closeEntryCount": 1,
    "payable": 120000,
}
