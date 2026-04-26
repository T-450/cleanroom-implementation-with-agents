#!/usr/bin/env python3
"""Token-budget enforcement (PreToolUse hook).

Reads the cost ledger; refuses the tool call if remaining budget falls
below the per-call estimate. Aborts cleanly so no partial Edit happens.

Schema: volumes/IV/schemas/cost-ledger.schema.json.
Budget cap: ANTHROPIC_BUDGET_USD env var (default 15.00).
Per-call estimate: heuristic by tool name; conservative.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("REDIS_CLEANROOM_ROOT", str(Path(__file__).resolve().parent.parent)))
LEDGER = Path(os.environ.get("COST_LEDGER", str(ROOT / "reports" / "audit" / "cost-ledger.json")))
BUDGET = float(os.environ.get("ANTHROPIC_BUDGET_USD", "15.00"))

# Conservative per-call cost estimates in USD. Real spend is reconciled
# from API usage events by a separate process; this is a pre-call guard.
ESTIMATE_USD = {
    "Read": 0.001,
    "Grep": 0.001,
    "Glob": 0.001,
    "Edit": 0.005,
    "Write": 0.005,
    "Bash": 0.005,
    "Task": 0.50,  # delegation triggers a whole subagent run
    "TodoWrite": 0.0005,
}


def load_ledger() -> dict:
    if not LEDGER.exists():
        return {
            "session_id": "unknown",
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "budget_usd": BUDGET,
            "spent_usd": 0.0,
            "remaining_usd": BUDGET,
            "events": [],
            "denials": [],
        }
    return json.loads(LEDGER.read_text())


def save_ledger(ledger: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(ledger, indent=2))


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    tool_name = payload.get("tool_name", "")
    estimate = ESTIMATE_USD.get(tool_name, 0.01)
    ledger = load_ledger()
    remaining = ledger.get("remaining_usd", BUDGET)
    if remaining < estimate:
        agent = payload.get("agent_type") or payload.get("agent_name") or "main"
        ledger.setdefault("denials", []).append({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "agent_name": agent,
            "tool": tool_name,
            "estimated_cost_usd": estimate,
            "remaining_usd_at_denial": remaining,
        })
        save_ledger(ledger)
        sys.stderr.write(
            f"COST CAP DENY: tool={tool_name} estimate=${estimate:.4f} "
            f"remaining=${remaining:.4f} budget=${BUDGET:.2f}\n"
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
