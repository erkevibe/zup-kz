import json
import sys


with open(sys.argv[1], encoding="utf-8") as source:
    actual = json.load(source)

assert actual == {
    "reopenedAndReasonSaved": True,
    "reclosed": True,
    "settlementLineCount": 1,
    "lifecycleEntryCount": 3,
    "paymentBlocksReopen": True,
    "blockedReasonPreserved": True,
    "workplaceNextStep": "Утвердите ведомость выплаты",
}
