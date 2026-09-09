#!/usr/bin/env python3
"""Forced-command endpoint: export Guacamole Docker logs as JSON lines."""

import datetime as dt
import hashlib
import json
import subprocess
import sys


def main() -> int:
    since = sys.argv[1] if len(sys.argv) == 2 else "30m"
    try:
        dt.datetime.fromisoformat(since.replace("Z", "+00:00"))
    except ValueError:
        if since != "30m":
            print("invalid since value", file=sys.stderr)
            return 2
    names = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"], text=True, capture_output=True, check=True
    ).stdout.splitlines()
    for name in sorted(names):
        result = subprocess.run(
            ["docker", "logs", "--timestamps", "--since", since, name],
            text=True, capture_output=True, check=False,
        )
        for line in (result.stdout + result.stderr).splitlines():
            timestamp, _, message = line.partition(" ")
            if not message:
                timestamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")
                message = line
            position = hashlib.sha256(f"{name}\n{line}".encode()).hexdigest()
            print(json.dumps({
                "position": position,
                "timestamp": timestamp,
                "logger": f"docker:{name}",
                "message": message,
            }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
