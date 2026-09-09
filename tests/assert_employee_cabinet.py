import json
import sys


for path in sys.argv[1:]:
    with open(path, encoding="utf-8") as source:
        result = json.load(source)
    assert result
    assert all(result.values())

print("Employee cabinet access test passed")
