#!/usr/bin/env python3
"""Validate the persisted HR -> time -> payroll -> chief accountant UI journey."""

import json
import sys


def main() -> None:
    source = sys.stdin if len(sys.argv) == 1 or sys.argv[1] == "-" else open(sys.argv[1], encoding="utf-8")
    with source:
        result = json.load(source)

    expected = {
        "employee": "Маршрутова Раяна Проверочная",
        "hirePosted": True,
        "hireDate": "2026-06-01",
        "assignmentCount": 1,
        "assignmentSalary": 300000.0,
        "timesheetApproved": True,
        "timesheetApprover": "ui-time",
        "timesheetLines": 30,
        "payrollStatus": "Выплачен",
        "gross": 300000.0,
        "socialApproved": True,
        "taxesApproved": True,
        "enforcementApproved": True,
        "statementStatus": "Выплачена",
        "nextStep": "Расчёт завершён",
    }
    for key, value in expected.items():
        assert result.get(key) == value, f"{key}: expected {value!r}, got {result.get(key)!r}"
    # lsFusion serializes its null-as-zero numeric result by omitting the JSON key.
    assert result.get("remaining", 0.0) == 0.0, result
    assert result["statementAmount"] > 0, result


if __name__ == "__main__":
    main()
