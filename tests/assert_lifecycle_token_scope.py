from pathlib import Path


root = Path(__file__).resolve().parents[1] / "src/main/lsfusion/zupkz/hr"
expected = {
    "Approval.lsf": (
        "DATA LOCAL BOOLEAN (PersonnelNotice)",
        "DATA LOCAL BOOLEAN (ApprovalRequest)",
        "DATA LOCAL BOOLEAN (PersonnelNotification)",
    ),
    "Archive.lsf": (
        "DATA LOCAL BOOLEAN (ArchiveCase)",
        "DATA LOCAL BOOLEAN (ArchiveDocument)",
    ),
    "AccidentInsurance.lsf": (
        "DATA LOCAL BOOLEAN (AccidentInsurancePolicy)",
        "DATA LOCAL BOOLEAN (WorkAccident)",
        "DATA LOCAL BOOLEAN (AccidentInsuranceClaim)",
    ),
}

for name, signatures in expected.items():
    source = (root / name).read_text(encoding="utf-8")
    assert "LifecycleTransition = DATA LOCAL BOOLEAN ();" not in source
    for signature in signatures:
        assert signature in source, f"{name}: missing {signature}"
