import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "ops" / "observer" / "zup_observer.py"
SPEC = importlib.util.spec_from_file_location("zup_observer", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ObserverTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.log = self.root / "app.log"
        self.config = {
            "database": str(self.root / "observer.db"),
            "alert_file": str(self.root / "alerts.ndjson"),
            "files": [{"name": "app", "globs": [str(self.log)]}],
            "processes": {"payroll": {
                "starts": ["timesheet"],
                "transitions": {"timesheet": ["calculated"], "calculated": []},
            }},
        }
        self.observer = MODULE.Observer(self.config)

    def tearDown(self):
        self.observer.close()
        self.temporary.cleanup()

    def count(self, table):
        return self.observer.db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]

    def test_checkpoint_keeps_partial_line_and_avoids_duplicates(self):
        self.log.write_text("2026-09-09 10:00:00 INFO ready\n2026-09-09 10:00:01 ERROR par", encoding="utf-8")
        self.observer.scan_once()
        self.assertEqual(self.count("raw_event"), 1)
        with self.log.open("a", encoding="utf-8") as stream:
            stream.write("tial failed\n")
        self.observer.scan_once()
        self.observer.scan_once()
        self.assertEqual(self.count("raw_event"), 2)
        self.assertEqual(self.count("incident"), 1)

    def test_multiline_stack_trace_is_one_event(self):
        self.log.write_text(
            "2026-09-09 10:00:00 ERROR operation failed\n"
            " java.lang.IllegalStateException: bad\n"
            "\tat kz.zup.Payroll.run(Payroll.java:10)\n",
            encoding="utf-8",
        )
        self.observer.scan_once()
        row = self.observer.db.execute("SELECT message FROM raw_event").fetchone()
        self.assertIn("IllegalStateException", row[0])
        self.assertEqual(self.count("raw_event"), 1)

    def test_unprefixed_application_lines_remain_separate_events(self):
        self.log.write_text("request accepted\nrequest completed\n", encoding="utf-8")
        self.observer.scan_once()
        self.assertEqual(self.count("raw_event"), 2)

    def test_incident_fingerprint_groups_variable_ids(self):
        self.log.write_text(
            "2026-09-09 10:00:00 ERROR request id=123 failed\n"
            "2026-09-09 10:00:01 ERROR request id=456 failed\n",
            encoding="utf-8",
        )
        self.observer.scan_once()
        row = self.observer.db.execute("SELECT count FROM incident").fetchone()
        self.assertEqual(row[0], 2)

    def test_invalid_process_transition_creates_incident(self):
        self.log.write_text(
            "2026-09-09 10:00:00 INFO ZUP_PROCESS process=payroll case=R1 activity=timesheet\n"
            "2026-09-09 10:00:01 INFO ZUP_PROCESS process=payroll case=R1 activity=closed\n",
            encoding="utf-8",
        )
        self.observer.scan_once()
        self.assertEqual(self.count("process_event"), 2)
        sample = self.observer.db.execute("SELECT sample FROM incident").fetchone()[0]
        self.assertIn("timesheet -> closed", sample)

    def test_invalid_process_start_creates_incident(self):
        self.log.write_text(
            "2026-09-09 10:00:00 INFO ZUP_PROCESS process=payroll case=R2 activity=closed\n",
            encoding="utf-8",
        )
        self.observer.scan_once()
        sample = self.observer.db.execute("SELECT sample FROM incident").fetchone()[0]
        self.assertIn("Invalid payroll start", sample)

    def test_redacts_secrets_and_personal_identifiers(self):
        value = MODULE.redact("password=hunter2 token=abc 901010400010 KZ123456789012345678")
        self.assertNotIn("hunter2", value)
        self.assertNotIn("901010400010", value)
        self.assertNotIn("KZ123456789012345678", value)

    def test_alert_output_is_valid_json_lines(self):
        self.log.write_text("2026-09-09 10:00:00 WARN small issue\n", encoding="utf-8")
        self.observer.scan_once()
        lines = (self.root / "alerts.ndjson").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(json.loads(lines[0])["severity"], "WARN")

    def test_repeated_incident_alerts_use_exponential_backoff(self):
        for index in range(3):
            with self.log.open("a", encoding="utf-8") as stream:
                stream.write(f"2026-09-09 10:00:0{index} WARN request id={index} failed\n")
            self.observer.scan_once()
        lines = (self.root / "alerts.ndjson").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)


if __name__ == "__main__":
    unittest.main()
