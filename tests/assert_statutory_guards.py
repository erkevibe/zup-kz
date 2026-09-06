import json
import sys


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)

for name in (
    "baselinePackApproved",
    "baselineSocialParametersComplete",
    "baselineTaxParametersComplete",
    "futurePackMissing",
    "futureSocialBlocked",
    "futureTaxBlocked",
):
    assert actual.get(name) is True, (name, actual.get(name))
