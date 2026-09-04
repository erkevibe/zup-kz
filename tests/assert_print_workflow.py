import json
import sys


with open(sys.argv[1], encoding="utf-8") as result_file:
    result = json.load(result_file)

expected = {
    "hireTitleRu": "ПРИКАЗ О ПРИЁМЕ НА РАБОТУ",
    "hireTitleKz": "ЖҰМЫСҚА ҚАБЫЛДАУ ТУРАЛЫ БҰЙРЫҚ",
    "transferTitleKz": "БАСҚА ЖҰМЫСҚА АУЫСТЫРУ ТУРАЛЫ БҰЙРЫҚ",
    "terminationTitleKz": "ЕҢБЕК ШАРТЫН БҰЗУ ТУРАЛЫ БҰЙРЫҚ",
    "eventEmployeeName": "Печатный Тест Тестович",
    "eventOrganizationMatches": True,
    "eventPrintable": True,
    "leaveTitleRu": "ПРИКАЗ О ПРЕДОСТАВЛЕНИИ ОТПУСКА",
    "leaveTitleKz": "ДЕМАЛЫС БЕРУ ТУРАЛЫ БҰЙРЫҚ",
    "leaveEmployeeName": "Печатный Тест Тестович",
    "leaveDepartmentName": "Отдел кадров",
    "leavePositionName": "Специалист",
    "leavePrintable": True,
    "eventPdfGenerated": True,
    "leaveDocxGenerated": True,
}

for key, expected_value in expected.items():
    actual_value = result.get(key)
    assert actual_value == expected_value, (
        f"{key}: expected {expected_value!r}, got {actual_value!r}"
    )
