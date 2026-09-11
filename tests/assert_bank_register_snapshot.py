import json
import sys


actual = {}
for result_path in sys.argv[1:]:
    with open(result_path, encoding="utf-8") as source:
        actual.update(json.load(source))

for name in (
    "lineSnapshotTamperRejected",
    "headerSnapshotTamperRejected",
    "lineSnapshotDeleteRejected",
    "lineSnapshotInsertRejected",
    "bankRegisterHeaderPreserved",
    "bankRegisterLineAmountPreserved",
    "bankRegisterLineIbanPreserved",
    "bankRegisterLineIinPreserved",
    "currentPaymentAccountChanged",
    "bankRegisterLineCountPreserved",
    "bankRegisterTotalPreserved",
):
    assert actual[name] is True, (name, actual.get(name))
