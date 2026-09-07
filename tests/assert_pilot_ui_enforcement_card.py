"""Verify saved native selector choices on the existing unused UI document."""
import json
import sys

data = json.load(sys.stdin)
expected = dict(owner='Тестов Данияр Контрольный', unused=True, inactive=True,
                usedOwnerPreserved=True, statusName='Не активирован',
                kindName='Прочее требование', methodName='Фиксированная сумма',
                activeStatusName='Действует', completeOrderReady=True,
                missing='Документ → Дата документа\nДокумент → Удерживать с\nУсловия удержания → Очередь')
for key, value in expected.items():
    assert data.get(key) == value, (key, value, data)
print('PASS: exact missing fields, complete order ready, readable choices and inactive document preserved')
