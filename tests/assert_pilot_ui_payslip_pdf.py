"""Verify the generated pilot PDF, including detail rows (requires Poppler)."""
import re
import subprocess
import sys

if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and sys.argv[2] not in ('august', 'september')):
    raise SystemExit("Usage: assert_pilot_ui_payslip_pdf.py payslip.pdf [august|september]")
august = len(sys.argv) == 3 and sys.argv[2] == 'august'
run = 'UI-PAY-2026-08' if august else 'UI-PREP-2026-09'

info = subprocess.run(["pdfinfo", sys.argv[1]], check=True, capture_output=True, text=True).stdout
text = subprocess.run(["pdftotext", "-layout", sys.argv[1], "-"],
                      check=True, capture_output=True, text=True).stdout
assert re.search(r"Pages:\s+1\b", info), info
assert re.search(r"Page size:\s+595 x 842 pts", info), info
assert re.search(r"Page rot:\s+0\b", info), info
normalized = " ".join(text.split())
for label in ["РАСЧЁТНЫЙ ЛИСТОК", "UI Test Organization", run,
              "Серикова Айгуль Маратовна", "К ВЫПЛАТЕ", "ПЛАТЕЖИ РАБОТОДАТЕЛЯ",
              "Листок не подтверждает фактическую выплату"]:
    assert label in normalized, (label, normalized)
assert ('UI-PREP-2026-09' if august else 'UI-PAY-2026-08') not in text, "PDF includes another payroll run"
assert normalized.count('Оплата по окладу') == 1, normalized
assert normalized.count('Разовая премия') == (1 if august else 0), normalized
assert normalized.count('К ВЫПЛАТЕ') == 1, 'Snapshot totals repeated per detail row'
assert normalized.count('Серикова Айгуль Маратовна') == 1, 'Employee header repeated'
amounts = ([35000000, 5000000, 40000000, 7022500, 32977500, 4000000, 800000,
            2222500, 1400000, 1800000, 1200000, 2112000] if august else
           [35000000, 5982500, 29017500, 3500000, 700000, 1782500,
            1225000, 1575000, 1050000, 1848000])
digits = re.sub(r"[\s,.]", "", text)
for amount in amounts:
    assert str(amount) in digits, (amount, text)
print(f"PASS: {run}, portrait A4, isolated detail rows and single snapshot totals")
