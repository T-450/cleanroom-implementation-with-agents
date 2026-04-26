#!/usr/bin/env python3
"""audit-log MCP server.

Exposes:

  Resources:
    audit://session/{session_id}        full event list for a session
    audit://policy-denials               every event with decision == 'denied'
    audit://task-prompt-redactions       every Task event with matched
                                         forbidden tokens

  Tools:
    query(filter)            structured filter over the event table
    drain_queue()            promote events from events.jsonl into SQLite

The drainer runs in WAL mode so reads do not block writes. The hook
writers append to `events.jsonl`; the MCP server drains lazily on
read/query, avoiding the single-writer-lock serialization that would hit
us if every PostToolUse hook wrote SQLite directly.

Schema for each event: volumes/IV/schemas/audit-event.schema.json.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    sys.stderr.write(
        "audit-log: install dependencies first: `uv sync` in this directory.\n"
    )
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent.parent
DB_PATH = Path(os.environ.get("AUDIT_DB", str(PROJECT_ROOT / "reports" / "audit" / "audit.sqlite")))
QUEUE = PROJECT_ROOT / "reports" / "audit" / "events.jsonl"

mcp = FastMCP("audit-log")


def db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            agent_role TEXT NOT NULL,
            tool TEXT NOT NULL,
            decision TEXT NOT NULL,
            input_summary TEXT,
            event_json TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_events_role_decision ON events(agent_role, decision)")
    return conn


def drain() -> int:
    """Drain events.jsonl into SQLite. Returns rows inserted."""
    if not QUEUE.exists():
        return 0
    inserted = 0
    conn = db()
    with QUEUE.open("r+") as fh:
        lines = fh.readlines()
        fh.seek(0)
        fh.truncate()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            conn.execute(
                "INSERT OR IGNORE INTO events "
                "(event_id, session_id, timestamp, agent_name, agent_role, tool, decision, input_summary, event_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    ev["event_id"],
                    ev["session_id"],
                    ev["timestamp"],
                    ev["agent_name"],
                    ev["agent_role"],
                    ev["tool"],
                    ev["decision"],
                    json.dumps(ev.get("input_summary") or {}),
                    line,
                ),
            )
            inserted += 1
        except Exception as e:
            sys.stderr.write(f"audit-log: drain skip ({e}): {line[:120]}\n")
    return inserted


@mcp.tool()
def drain_queue() -> dict[str, int]:
    """Promote events from the JSONL queue into SQLite. Idempotent."""
    n = drain()
    return {"inserted": n}


@mcp.tool()
def query(
    session_id: str | None = None,
    agent_role: str | None = None,
    decision: str | None = None,
    tool: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Structured query over the audit event table.

    Returns at most `limit` rows, most recent first.
    """
    drain()
    conn = db()
    where = []
    params: list[Any] = []
    if session_id:
        where.append("session_id = ?")
        params.append(session_id)
    if agent_role:
        where.append("agent_role = ?")
        params.append(agent_role)
    if decision:
        where.append("decision = ?")
        params.append(decision)
    if tool:
        where.append("tool = ?")
        params.append(tool)
    sql = "SELECT event_json FROM events"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    return [json.loads(row[0]) for row in conn.execute(sql, params)]


@mcp.resource("audit://session/{session_id}")
def session_log(session_id: str) -> str:
    """Full event list for a session, ordered chronologically."""
    drain()
    conn = db()
    rows = conn.execute(
        "SELECT event_json FROM events WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,),
    ).fetchall()
    return json.dumps([json.loads(r[0]) for r in rows], indent=2)


@mcp.resource("audit://policy-denials")
def policy_denials() -> str:
    """Every event with decision == 'denied' across all sessions."""
    drain()
    conn = db()
    rows = conn.execute(
        "SELECT event_json FROM events WHERE decision = 'denied' ORDER BY timestamp DESC"
    ).fetchall()
    return json.dumps([json.loads(r[0]) for r in rows], indent=2)


@mcp.resource("audit://task-prompt-redactions")
def task_redactions() -> str:
    """Task delegations whose prompt matched a forbidden source token."""
    drain()
    conn = db()
    out: list[dict] = []
    for (j,) in conn.execute(
        "SELECT event_json FROM events WHERE tool = 'Task' ORDER BY timestamp DESC"
    ).fetchall():
        ev = json.loads(j)
        rd = ev.get("task_prompt_redaction") or {}
        if rd.get("matched_forbidden_tokens"):
            out.append(ev)
    return json.dumps(out, indent=2)


if __name__ == "__main__":
    mcp.run()
