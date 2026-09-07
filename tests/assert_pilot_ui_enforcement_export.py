"""Read-only XLSX checks on the persistent UI fixture; Python stdlib only.

Usage: python3 tests/assert_pilot_ui_enforcement_export.py orders|lines full|empty file.xlsx
Also accepts `native-orders full` for the original four-column UI export.
"""
import sys
from decimal import Decimal
from xml.etree import ElementTree as ET
from zipfile import ZipFile


def read_rows(path):
    ns = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with ZipFile(path) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(t.text or '' for t in s.findall('.//x:t', ns))
                       for s in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('x:si', ns)]
        sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        rows = []
        # Read actual cells: Jasper's UI export can declare dimension A1 for a full table.
        for row in sheet.findall('x:sheetData/x:row', ns):
            values = {}
            for cell in row.findall('x:c', ns):
                assert cell.find('x:f', ns) is None, 'Export must contain values, not formulas'
                col = ''.join(c for c in cell.attrib['r'] if c.isalpha())
                value = cell.findtext('x:v', namespaces=ns)
                if cell.get('t') == 's' and value is not None:
                    value = strings[int(value)]
                elif cell.get('t') == 'inlineStr':
                    value = ''.join(t.text or '' for t in cell.findall('.//x:t', ns))
                elif value is not None and cell.get('t') not in ('str', 'b'):
                    value = Decimal(value)
                values[col] = value
            rows.append(values)
    assert rows, 'Missing header'
    headers = rows[0]
    assert len(set(headers.values())) == len(headers), 'Duplicate headers'
    return list(headers.values()), [dict((name, row.get(col)) for col, name in headers.items())
                                   for row in rows[1:]]


kind, scope, path = sys.argv[1:]
assert kind in ('orders', 'lines', 'native-orders') and scope in ('full', 'empty')
headers, rows = read_rows(path)
assert len(headers) == {'orders': 23, 'lines': 22, 'native-orders': 4}[kind], headers
if scope == 'empty':
    assert not rows, rows
else:
    assert len(rows) == (5 if kind == 'lines' else 4), rows
    if kind != 'native-orders':
        assert {r['БИН'] for r in rows} == {'555555555555'}
        assert {r['Организация'] for r in rows} == {'UI Test Organization'}
    if kind in ('orders', 'native-orders'):
        by_number = {r['Документ']: r for r in rows}
        assert set(by_number) == {'UI-DEDUCT-ORDER-001', 'UI-ENFORCE-ORDER-001',
                                  'UI-UNUSED-OWNER-001', 'UI-HISTORY-ORDER-001'}
        unused = by_number['UI-UNUSED-OWNER-001']
        assert unused['Статус'] == 'Не активирован'
        assert unused['Сотрудник'] == 'Тестов Данияр Контрольный'
        if kind == 'orders':
            assert unused['ИИН сотрудника'] == '910202350002'
            assert unused['Дата документа'] is None and unused['Очередь'] is None
            assert unused['Вид требования'] == 'Прочее требование'
            assert unused['Способ расчёта'] == 'Фиксированная сумма'
            assert by_number['UI-HISTORY-ORDER-001']['Доля, %'] == 20
            assert by_number['UI-DEDUCT-ORDER-001']['Фиксированная сумма, KZT'] == 20000
    else:
        old = [r for r in rows if r['Условия расчёта'] == 'Не сохранялись (старый расчёт)']
        assert len(old) == 3
        assert all(r['Применённая доля, %'] is None and r['Номер на дату расчёта'] is None for r in old)
        december = {r['Статус расчёта']: r for r in rows if r['Расчёт зарплаты'] == 'UI-HISTORY-2026-12'}
        assert set(december) == {'Отменён', 'Утверждён'}
        for status, percent, priority, amount, basis in (
            ('Отменён', 10, 5, '29017.50', 'UI: исходные условия 10 процентов'),
            ('Утверждён', 20, 4, '58035.00', 'UI: изменённые условия 20 процентов'),
        ):
            r = december[status]
            assert r['Условия расчёта'] == 'Сохранены'
            assert r['Применённая доля, %'] == percent
            assert r['Очередь на дату расчёта'] == priority
            assert r['Удержано, KZT'] == Decimal(amount)
            assert r['Основание на дату расчёта'] == basis
            assert r['Доход для взыскания, KZT'] == 350000
            assert r['Доход после налогов, KZT'] == 290175
        assert sum(r['Удержано, KZT'] for r in rows if r['Статус расчёта'] == 'Утверждён') == 103035
print(f'PASS: {kind} {scope}, {len(headers)} columns, {len(rows)} rows')
