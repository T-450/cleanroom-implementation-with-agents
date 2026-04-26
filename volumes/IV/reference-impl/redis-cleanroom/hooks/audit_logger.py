#!/usr/bin/env python3
"""Append-only audit logger (PostToolUse hook).

Appends one audit-event row per tool call to a local JSONL queue file.
A separate sidecar (`mcp-servers/audit-log/server.py` exposes the SQLite
view; the drainer is a small loop in the same process) reads the queue
and inserts into SQLite (WAL mode), avoiding the single-writer-lock
serialization that would otherwise bottleneck 15 concurrent subagents on
PostToolUse.

The schema is locked at volumes/IV/schemas/audit-event.schema.json. We
hash inputs and outputs rather than persisting them: legal replay needs
to know "what tool, by whom, against what target, and was it allowed",
not the literal byte content of every tool call.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(os.environ.get("REDIS_CLEANROOM_ROOT", str(Path(__file__).resolve().parent.parent)))
QUEUE = ROOT / "reports" / "audit" / "events.jsonl"


def sha256(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return "sha256:" + hashlib.sha256(data).hexdigest()


def short_event_id() -> str:
    return "evt-" + uuid.uuid4().hex[:16]


def role_of(agent: str) -> str:
    try:
        policy_path = Path(os.environ.get(
            "TOOL_POLICY",
            str(ROOT.parent.parent / "schemas" / "tool-policy.json"),
        ))
        roles = json.loads(policy_path.read_text()).get("roles", {})
        return roles.get(agent, "main")
    except Exception:
        return "main"


def input_summary(tool_name: str, tool_input: dict) -> dict:
    if tool_name in {"Read", "Edit", "Write"}:
        return {"file_path": tool_input.get("file_path")}
    if tool_name == "Grep":
        return {"pattern": tool_input.get("pattern"), "path": tool_input.get("path")}
    if tool_name == "Glob":
        return {"pattern": tool_input.get("pattern")}
    if tool_name == "Bash":
        cmd = (tool_input.get("command") or "").split()
        return {"argv0": cmd[0] if cmd else "", "argc": len(cmd)}
    if tool_name == "Task":
        return {"subagent_type": tool_input.get("subagent_type"), "description": tool_input.get("description")}
    return {}


def task_redaction(tool_name: str, tool_input: dict) -> dict | None:
    if tool_name != "Task":
        return None
    import re

    forbidden = re.compile(r"\b(redisCommand|commandTable|server\.c|t_string\.c|db\.c|addReply\w*|dictEntry|robj)\b")
    prompt = tool_input.get("prompt", "") or ""
    return {
        "matched_forbidden_tokens": sorted(set(m.group(0) for m in forbidden.finditer(prompt))),
        "prompt_hash": sha256(prompt),
    }


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    tool_response = payload.get("tool_response") or {}
    agent = payload.get("agent_type") or payload.get("agent_name") or "main"
    event = {
        "event_id": short_event_id(),
        "session_id": payload.get("session_id", "unknown"),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "agent_name": agent,
        "agent_role": role_of(agent),
        "tool": tool_name,
        "input_hash": sha256(json.dumps(tool_input, sort_keys=True, default=str)),
        "input_summary": input_summary(tool_name, tool_input),
        "output_hash": sha256(json.dumps(tool_response, sort_keys=True, default=str)),
        "duration_ms": payload.get("duration_ms", 0),
        "decision": "allowed",  # hook fires post-tool, so by definition the tool ran
        "policy_version": "1.0.0",
    }
    redaction = task_redaction(tool_name, tool_input)
    if redaction:
        event["task_prompt_redaction"] = redaction
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    with QUEUE.open("a") as fh:
        fh.write(json.dumps(event) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
