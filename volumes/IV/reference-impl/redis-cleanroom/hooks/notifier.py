#!/usr/bin/env python3
"""Stop / SubagentStop notifier.

Emits a structured event row when a session or a subagent finishes, so
the coordinator can be resumed against an external queue. Used by
`/run-cleanroom-pipeline` to step from one milestone to the next without
polling.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("REDIS_CLEANROOM_ROOT", str(Path(__file__).resolve().parent.parent)))
EVENTS = ROOT / "reports" / "audit" / "stop-events.jsonl"


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    event = {
        "kind": "subagent_stop" if "--subagent-stop" in sys.argv else "stop",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "session_id": payload.get("session_id", "unknown"),
        "agent_name": payload.get("agent_type") or payload.get("agent_name") or "main",
    }
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS.open("a") as fh:
        fh.write(json.dumps(event) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
