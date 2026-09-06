"""Verify the generated September pilot PDF (requires Poppler tools)."""
import re
import subprocess
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: assert_pilot_ui_payslip_pdf.py payslip.pdf")

info = subprocess.run(["pdfinfo", sys.argv[1]], check=True, capture_output=True, text=True).stdout
text = subprocess.run(["pdftotext", "-layout", sys.argv[1], "-"],
                      check=True, capture_output=True, text=True).stdout
assert re.search(r"Pages:\s+1\b", info), info
assert re.search(r"Page size:\s+595 x 842 pts", info), info
assert re.search(r"Page rot:\s+0\b", info), info
normalized = " ".join(text.split())
for label in ["РАСЧЁТНЫЙ ЛИСТОК", "UI Test Organization", "UI-PREP-2026-09",
              "Серикова Айгуль Маратовна", "К ВЫПЛАТЕ", "ПЛАТЕЖИ РАБОТОДАТЕЛЯ",
              "Листок не подтверждает фактическую выплату"]:
    assert label in normalized, (label, normalized)
assert "UI-PAY-2026-08" not in text, "PDF includes another payroll run"
digits = re.sub(r"[\s,.]", "", text)
for amount in [35000000, 5982500, 29017500, 3500000, 700000, 1782500,
               1225000, 1575000, 1050000, 1848000]:
    assert str(amount) in digits, (amount, text)
print("PASS: one portrait A4 payslip, correct employee and snapshot amounts")
