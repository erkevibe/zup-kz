#!/usr/bin/env python3
"""Small, loss-aware log collector and process anomaly detector for ZUP-KZ."""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import re
import shlex
import sqlite3
import subprocess
import sys
import time
from pathlib import Path


UTC = dt.timezone.utc
SEVERITY_ORDER = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40, "FATAL": 50}
SECRET_PATTERNS = (
    re.compile(r"(?i)(password|passwd|token|secret|cookie|authorization)\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9+/=._-]+"),
    re.compile(r"\b\d{12}\b"),
    re.compile(r"\bKZ\d{18}\b", re.I),
)
PROCESS_MARKER = "ZUP_PROCESS "


def utc_now() -> str:
    return dt.datetime.now(UTC).isoformat(timespec="seconds")


def redact(value: str) -> str:
    result = value
    for index, pattern in enumerate(SECRET_PATTERNS):
        if index == 0:
            result = pattern.sub(lambda m: f"{m.group(1)}=<redacted>", result)
        elif index == 1:
            result = pattern.sub(lambda m: f"{m.group(1)} <redacted>", result)
        elif index == 2:
            result = pattern.sub("<iin-redacted>", result)
        else:
            result = pattern.sub("<iban-redacted>", result)
    return result


def severity(message: str, explicit: str | None = None) -> str:
    if explicit:
        value = explicit.upper()
        if value in SEVERITY_ORDER:
            return value
    upper = message.upper()
    if "FATAL" in upper or "PANIC" in upper or "OUTOFMEMORY" in upper:
        return "FATAL"
    if any(token in upper for token in ("ERROR", "EXCEPTION", "TRACEBACK", "SEVERE", " HTTP 5")):
        return "ERROR"
    if any(token in upper for token in ("WARN", "DENIED", "FAILED", " HTTP 4")):
        return "WARN"
    return "INFO"


def fingerprint(logger: str, message: str) -> str:
    normalized = redact(message.lower())
    normalized = re.sub(r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b", "<uuid>", normalized)
    normalized = re.sub(r"\b(?:pid|session|request|id)[=: ]+[-a-z0-9_.]+", "<id>", normalized)
    normalized = re.sub(r"\b\d+\b", "<n>", normalized)
    first_lines = "\n".join(normalized.splitlines()[:3])
    return hashlib.sha256(f"{logger}\n{first_lines}".encode()).hexdigest()


def parse_process_event(message: str) -> dict[str, str] | None:
    marker_at = message.find(PROCESS_MARKER)
    if marker_at < 0:
        return None
    fields: dict[str, str] = {}
    for token in shlex.split(message[marker_at + len(PROCESS_MARKER):]):
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key] = value
    if fields.get("process") and fields.get("case") and fields.get("activity"):
        return fields
    return None


class Observer:
    def __init__(self, config: dict):
        self.config = config
        db_path = Path(config["database"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self._create_schema()
        self.rules = config.get("processes", {})
        self.alert_file = Path(config.get("alert_file", db_path.with_name("alerts.ndjson")))

    def close(self) -> None:
        self.db.close()

    def _create_schema(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS checkpoint (
                source TEXT PRIMARY KEY, identity TEXT, position TEXT,
                pending TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS raw_event (
                id INTEGER PRIMARY KEY, source TEXT NOT NULL, position TEXT NOT NULL,
                occurred_at TEXT NOT NULL, severity TEXT NOT NULL, logger TEXT NOT NULL,
                message TEXT NOT NULL, fingerprint TEXT NOT NULL,
                UNIQUE(source, position)
            );
            CREATE TABLE IF NOT EXISTS incident (
                fingerprint TEXT PRIMARY KEY, severity TEXT NOT NULL,
                first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, count INTEGER NOT NULL,
                state TEXT NOT NULL DEFAULT 'open', sample TEXT NOT NULL,
                last_notified_count INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS process_event (
                id INTEGER PRIMARY KEY, raw_event_id INTEGER NOT NULL UNIQUE,
                process_code TEXT NOT NULL, case_id TEXT NOT NULL,
                activity TEXT NOT NULL, from_state TEXT, to_state TEXT,
                organization TEXT, actor TEXT, outcome TEXT, occurred_at TEXT NOT NULL,
                FOREIGN KEY(raw_event_id) REFERENCES raw_event(id)
            );
            CREATE TABLE IF NOT EXISTS case_state (
                process_code TEXT NOT NULL, case_id TEXT NOT NULL,
                activity TEXT NOT NULL, occurred_at TEXT NOT NULL,
                PRIMARY KEY(process_code, case_id)
            );
            """
        )

    def checkpoint(self, source: str) -> sqlite3.Row | None:
        return self.db.execute("SELECT * FROM checkpoint WHERE source = ?", (source,)).fetchone()

    def set_checkpoint(self, source: str, identity: str, position: str, pending: str = "") -> None:
        self.db.execute(
            """INSERT INTO checkpoint(source, identity, position, pending, updated_at)
               VALUES(?, ?, ?, ?, ?)
               ON CONFLICT(source) DO UPDATE SET identity=excluded.identity,
               position=excluded.position, pending=excluded.pending, updated_at=excluded.updated_at""",
            (source, identity, position, pending, utc_now()),
        )

    def add_event(self, source: str, position: str, occurred_at: str, logger: str,
                  message: str, explicit_severity: str | None = None) -> bool:
        clean = redact(message.rstrip())
        level = severity(clean, explicit_severity)
        event_fingerprint = fingerprint(logger, clean)
        cursor = self.db.execute(
            """INSERT OR IGNORE INTO raw_event
               (source, position, occurred_at, severity, logger, message, fingerprint)
               VALUES(?, ?, ?, ?, ?, ?, ?)""",
            (source, position, occurred_at, level, logger, clean, event_fingerprint),
        )
        if not cursor.rowcount:
            return False
        event_id = cursor.lastrowid
        if SEVERITY_ORDER[level] >= SEVERITY_ORDER["WARN"]:
            self._record_incident(event_fingerprint, level, occurred_at, clean)
        process = parse_process_event(clean)
        if process:
            self._record_process(event_id, occurred_at, process)
        return True

    def _record_incident(self, key: str, level: str, occurred_at: str, sample: str) -> None:
        current = self.db.execute("SELECT * FROM incident WHERE fingerprint = ?", (key,)).fetchone()
        if current:
            chosen = level if SEVERITY_ORDER[level] > SEVERITY_ORDER[current["severity"]] else current["severity"]
            self.db.execute(
                "UPDATE incident SET severity=?, last_seen=?, count=count+1, sample=? WHERE fingerprint=?",
                (chosen, occurred_at, sample[:4000], key),
            )
        else:
            self.db.execute(
                "INSERT INTO incident(fingerprint,severity,first_seen,last_seen,count,sample) VALUES(?,?,?,?,1,?)",
                (key, level, occurred_at, occurred_at, sample[:4000]),
            )

    def observer_incident(self, code: str, level: str, message: str) -> None:
        clean = redact(message)
        self._record_incident(fingerprint("zup-observer:" + code, clean), level, utc_now(), clean)

    def _record_process(self, event_id: int, occurred_at: str, fields: dict[str, str]) -> None:
        process_code, case_id, activity = fields["process"], fields["case"], fields["activity"]
        case_ref = hashlib.sha256(case_id.encode()).hexdigest()[:12]
        previous = self.db.execute(
            "SELECT activity,occurred_at FROM case_state WHERE process_code=? AND case_id=?",
            (process_code, case_id),
        ).fetchone()
        process_rules = self.rules.get(process_code, {})
        allowed = process_rules.get("transitions", {})
        dedupe_seconds = int(process_rules.get("dedupe_seconds", 0))
        if previous and previous["activity"] == activity and dedupe_seconds:
            previous_at = dt.datetime.fromisoformat(previous["occurred_at"].replace("Z", "+00:00"))
            current_at = dt.datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
            if abs((current_at - previous_at).total_seconds()) <= dedupe_seconds:
                return
        if not previous and activity not in process_rules.get("starts", []):
            self.observer_incident(
                "invalid-start", "ERROR",
                f"Invalid {process_code} start for case {case_ref}: {activity}",
            )
        if previous and activity not in allowed.get(previous["activity"], []):
            self.observer_incident(
                "invalid-transition", "ERROR",
                f"Invalid {process_code} transition for case {case_ref}: {previous['activity']} -> {activity}",
            )
        self.db.execute(
            "UPDATE incident SET state='resolved' WHERE state='open' AND sample LIKE ?",
            (f"Stalled {process_code} case {case_ref} at %",),
        )
        self.db.execute(
            """INSERT INTO process_event(raw_event_id,process_code,case_id,activity,from_state,to_state,
               organization,actor,outcome,occurred_at) VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (event_id, process_code, case_id, activity,
             fields.get("from") or (previous["activity"] if previous else None),
             fields.get("to") or activity,
             fields.get("organization"), fields.get("actor"), fields.get("outcome"), occurred_at),
        )
        self.db.execute(
            """INSERT INTO case_state(process_code,case_id,activity,occurred_at) VALUES(?,?,?,?)
               ON CONFLICT(process_code,case_id) DO UPDATE SET activity=excluded.activity,
               occurred_at=excluded.occurred_at""",
            (process_code, case_id, activity, occurred_at),
        )

    def check_stalled_processes(self, now: dt.datetime | None = None) -> None:
        current = now or dt.datetime.now(UTC)
        for row in self.db.execute("SELECT * FROM case_state").fetchall():
            rules = self.rules.get(row["process_code"], {})
            threshold = rules.get("max_age_seconds", {}).get(row["activity"])
            if not threshold:
                continue
            occurred = dt.datetime.fromisoformat(row["occurred_at"].replace("Z", "+00:00"))
            if occurred.tzinfo is None:
                occurred = occurred.replace(tzinfo=UTC)
            if (current - occurred).total_seconds() < threshold:
                continue
            case_ref = hashlib.sha256(row["case_id"].encode()).hexdigest()[:12]
            recommendation = rules.get("recommendations", {}).get(
                row["activity"], "Проверить документ и выполнить следующий штатный шаг"
            )
            message = (f"Stalled {row['process_code']} case {case_ref} at {row['activity']} "
                       f"since {row['occurred_at']}; recommendation: {recommendation}")
            key = fingerprint("zup-observer:process-stalled", redact(message))
            if not self.db.execute(
                "SELECT 1 FROM incident WHERE fingerprint=?", (key,)
            ).fetchone():
                self._record_incident(key, "WARN", utc_now(), message)

    def scan_file(self, source_name: str, path: str) -> None:
        source = f"file:{source_name}:{path}"
        try:
            stat = os.stat(path)
        except OSError as error:
            self.observer_incident("source-unavailable", "FATAL", f"Cannot read {source}: {error}")
            self.db.commit()
            return
        identity = f"{stat.st_dev}:{stat.st_ino}"
        saved = self.checkpoint(source)
        offset = 0
        pending = ""
        if saved and saved["identity"] == identity:
            offset = int(saved["position"] or 0)
            pending = saved["pending"]
            if stat.st_size < offset:
                self.observer_incident("source-truncated", "ERROR", f"Source truncated before checkpoint: {source}")
                offset, pending = 0, ""
        elif saved:
            self.observer_incident("source-rotated", "WARN", f"Source inode changed: {source}")
        try:
            with open(path, "rb") as stream:
                stream.seek(offset)
                payload = stream.read()
        except OSError as error:
            self.observer_incident("source-unavailable", "FATAL", f"Cannot read {source}: {error}")
            self.db.commit()
            return
        text = pending + payload.decode("utf-8", errors="replace")
        if text.endswith("\n"):
            complete_text, new_pending = text, ""
        else:
            newline = text.rfind("\n")
            complete_text = text[:newline + 1] if newline >= 0 else ""
            new_pending = text[newline + 1:] if newline >= 0 else text
        records = self._records(complete_text)
        for index, record in enumerate(records):
            position = f"{identity}:{offset + len(payload)}:{index}:{hashlib.sha256(record.encode()).hexdigest()[:12]}"
            self.add_event(source, position, utc_now(), source_name, record)
        self.set_checkpoint(source, identity, str(offset + len(payload)), new_pending)
        self.db.commit()

    @staticmethod
    def _records(text: str) -> list[str]:
        records: list[str] = []
        current: list[str] = []
        for line in text.splitlines():
            continuation = bool(current) and (
                line.startswith((" ", "\t", "at ", "Caused by:", "Suppressed:", "... "))
                or bool(re.match(r"^[A-Za-z0-9_.$]+(?:Exception|Error):", line))
            )
            if current and not continuation:
                records.append("\n".join(current))
                current = []
            current.append(line)
        if current:
            records.append("\n".join(current))
        return records

    def scan_journal(self, item: dict) -> None:
        source = f"journal:{item['name']}"
        saved = self.checkpoint(source)
        command = ["journalctl", "--output=json", "--no-pager"]
        for unit in item.get("units", []):
            command.extend(("--unit", unit))
        if saved and saved["position"]:
            command.extend(("--after-cursor", saved["position"]))
        else:
            command.extend(("--since", f"-{self.config.get('baseline_minutes', 30)} minutes"))
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.returncode:
            self.observer_incident("journal-unavailable", "FATAL", f"{source}: {result.stderr.strip()}")
            self.db.commit()
            return
        last_cursor = saved["position"] if saved else ""
        for line in result.stdout.splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                self.observer_incident("journal-invalid-json", "ERROR", f"Invalid JSON from {source}")
                continue
            cursor = record.get("__CURSOR")
            if not cursor:
                continue
            micros = int(record.get("__REALTIME_TIMESTAMP", "0") or 0)
            occurred = dt.datetime.fromtimestamp(micros / 1_000_000, UTC).isoformat(timespec="milliseconds")
            logger = record.get("SYSLOG_IDENTIFIER") or record.get("_SYSTEMD_UNIT") or item["name"]
            priority = int(record.get("PRIORITY", "6") or 6)
            explicit = "FATAL" if priority <= 2 else "ERROR" if priority <= 3 else "WARN" if priority <= 4 else "INFO"
            self.add_event(source, cursor, occurred, logger, str(record.get("MESSAGE", "")), explicit)
            last_cursor = cursor
        if last_cursor:
            self.set_checkpoint(source, "journal", last_cursor)
        self.db.commit()

    def scan_command(self, item: dict) -> None:
        source = f"command:{item['name']}"
        saved = self.checkpoint(source)
        since = saved["position"] if saved and saved["position"] else (
            dt.datetime.now(UTC) - dt.timedelta(minutes=self.config.get("baseline_minutes", 30))
        ).isoformat(timespec="seconds")
        command = [part.replace("{since}", since) for part in item["argv"]]
        result = subprocess.run(command, text=True, capture_output=True, check=False, timeout=item.get("timeout", 60))
        if result.returncode:
            self.observer_incident("command-unavailable", "FATAL", f"{source}: {result.stderr.strip()}")
            self.db.commit()
            return
        newest = since
        for line in result.stdout.splitlines():
            try:
                record = json.loads(line)
                occurred = record["timestamp"]
                position = record.get("position") or hashlib.sha256(line.encode()).hexdigest()
                self.add_event(source, position, occurred, record.get("logger", item["name"]),
                               record.get("message", ""), record.get("severity"))
                newest = max(newest, occurred)
            except (json.JSONDecodeError, KeyError, TypeError) as error:
                self.observer_incident("command-invalid-json", "ERROR", f"{source}: {error}")
        self.set_checkpoint(source, "command", newest)
        self.db.commit()

    def scan_once(self) -> None:
        for item in self.config.get("files", []):
            matched = set()
            for pattern in item["globs"]:
                matched.update(glob.glob(pattern))
            if not matched:
                self.observer_incident("source-unavailable", "FATAL", f"No files matched source {item['name']}")
            for path in sorted(matched):
                self.scan_file(item["name"], path)
        for item in self.config.get("journals", []):
            self.scan_journal(item)
        for item in self.config.get("commands", []):
            self.scan_command(item)
        self.check_stalled_processes()
        self.db.commit()
        self.write_alerts()

    def write_alerts(self) -> None:
        rows = self.db.execute(
            """SELECT * FROM incident WHERE state='open'
               AND (last_notified_count=0 OR count >= last_notified_count * 2)
               ORDER BY CASE severity WHEN 'FATAL' THEN 0 WHEN 'ERROR' THEN 1 ELSE 2 END, last_seen"""
        ).fetchall()
        if not rows:
            return
        self.alert_file.parent.mkdir(parents=True, exist_ok=True)
        with self.alert_file.open("a", encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(dict(row), ensure_ascii=False) + "\n")
                self.db.execute(
                    "UPDATE incident SET last_notified_count=count WHERE fingerprint=?", (row["fingerprint"],)
                )
        self.db.commit()

    def report(self, limit: int | None = None) -> None:
        chosen_limit = limit or int(self.config.get("report_limit", 50))
        summary = self.db.execute(
            "SELECT severity,count(*) AS incidents,sum(count) AS occurrences FROM incident WHERE state='open' GROUP BY severity"
        ).fetchall()
        rows = self.db.execute(
            """SELECT severity,first_seen,last_seen,count,sample FROM incident WHERE state='open'
               ORDER BY CASE severity WHEN 'FATAL' THEN 0 WHEN 'ERROR' THEN 1 ELSE 2 END,
                        count DESC, last_seen DESC LIMIT ?""",
            (chosen_limit,),
        ).fetchall()
        sources = self.db.execute(
            "SELECT source,updated_at FROM checkpoint ORDER BY source"
        ).fetchall()
        process_states = self.db.execute(
            """SELECT process_code,activity,count(*) AS active_cases
               FROM case_state GROUP BY process_code,activity ORDER BY process_code,activity"""
        ).fetchall()
        process_transitions = self.db.execute(
            """SELECT process_code,from_state,activity AS to_activity,count(*) AS occurrences
               FROM process_event GROUP BY process_code,from_state,activity
               ORDER BY process_code,from_state,activity"""
        ).fetchall()
        print(json.dumps({
            "generatedAt": utc_now(),
            "summary": [dict(row) for row in summary],
            "sources": [dict(row) for row in sources],
            "processStates": [dict(row) for row in process_states],
            "processTransitions": [dict(row) for row in process_transitions],
            "topIncidents": [dict(row) for row in rows],
        }, ensure_ascii=False))


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as stream:
        return json.load(stream)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("once", "run", "report"))
    parser.add_argument("--config", default=os.environ.get("ZUP_OBSERVER_CONFIG", "/etc/zup-observer.json"))
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    observer = Observer(load_config(args.config))
    try:
        if args.command == "report":
            observer.report(args.limit)
            return 0
        if args.command == "once":
            observer.scan_once()
            return 0
        while True:
            observer.scan_once()
            time.sleep(observer.config.get("poll_seconds", 15))
    finally:
        observer.close()


if __name__ == "__main__":
    raise SystemExit(main())
