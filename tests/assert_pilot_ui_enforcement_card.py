"""Verify saved native selector choices on the existing unused UI document."""
import json
import sys

data = json.load(sys.stdin)
expected = dict(owner='Тестов Данияр Контрольный', unused=True, inactive=True,
                usedOwnerPreserved=True, statusName='Не активирован',
                kindName='Прочее требование', methodName='Фиксированная сумма',
                activeStatusName='Действует')
for key, value in expected.items():
    assert data.get(key) == value, (key, value, data)
print('PASS: readable choices saved, document inactive and historical owner preserved')
