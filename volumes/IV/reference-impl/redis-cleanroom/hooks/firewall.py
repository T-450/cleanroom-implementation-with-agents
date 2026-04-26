#!/usr/bin/env python3
"""File-level legal firewall (PreToolUse hook).

Reads the active subagent's role from `tool-policy.json`, evaluates the
tool call against the rule list, and exits with non-zero (printing the
denial reason on stderr) when the call would violate the policy.

Also handles `Task`-tool invocations when invoked with `--task`: greps the
prompt content for forbidden source-code tokens and refuses if any match,
which is the "every Task prompt is hashed and forbidden-token-scanned"
enforcement layer described in the Coordinator Contract.

Schema for the policy: volumes/IV/schemas/tool-policy.schema.json.
Hook input contract: stdin is a JSON object with at least:
  {
    "tool_name": "...",
    "tool_input": {...},
    "agent_type": "tdd-implementer" | "spec-extractor" | ...,
    "session_id": "..."
  }
Exit codes:
  0  allow
  2  deny (Claude Code surfaces stderr to the model)
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import sys
from pathlib import Path

POLICY_PATH = Path(os.environ.get(
    "TOOL_POLICY",
    str(Path(__file__).resolve().parent.parent.parent.parent / "schemas" / "tool-policy.json"),
))

FORBIDDEN_SOURCE_TOKENS = [
    r"\bredisCommand\b",
    r"\bcommandTable\b",
    r"\bserver\.c\b",
    r"\bt_string\.c\b",
    r"\bdb\.c\b",
    r"\baddReply\w*\b",
    r"\bdictEntry\b",
    r"\brobj\b",
    r"\brobj_\w+\b",
    r"\bRESP3\b",
    r"\bclient\s*\*\s*c\b",
    r"#include\s+\"server\.h\"",
]
FORBIDDEN_TOKEN_RE = re.compile("|".join(FORBIDDEN_SOURCE_TOKENS))


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text())


def role_for(agent_name: str, policy: dict) -> str:
    return policy.get("roles", {}).get(agent_name, "main")


def tool_path(tool_name: str, tool_input: dict) -> str | None:
    if tool_name in {"Read", "Edit", "Write"}:
        return tool_input.get("file_path")
    if tool_name in {"Grep", "Glob"}:
        return tool_input.get("path") or tool_input.get("pattern")
    if tool_name == "Bash":
        return tool_input.get("command")
    return None


def match_tool(rule_tool: str, tool_name: str, tool_input: dict) -> bool:
    if rule_tool == tool_name:
        return True
    if rule_tool == "*":
        return True
    if rule_tool.startswith("Bash:") and tool_name == "Bash":
        prefix = rule_tool.split(":", 1)[1]
        cmd = (tool_input.get("command") or "").strip()
        return fnmatch.fnmatchcase(cmd.split()[0] if cmd else "", prefix.replace(":*", "*"))
    return False


def match_path(patterns: list[str] | None, path: str | None) -> bool:
    if not patterns:
        return True
    if path is None:
        return False
    for p in patterns:
        if fnmatch.fnmatchcase(path, p):
            return True
        if fnmatch.fnmatchcase(path, "**/" + p):
            return True
    return False


def evaluate(policy: dict, role: str, tool_name: str, tool_input: dict) -> tuple[str, str | None, str | None]:
    path = tool_path(tool_name, tool_input)
    for rule in policy.get("rules", []):
        roles = rule["roles"]
        if "*" not in roles and role not in roles:
            continue
        if not any(match_tool(t, tool_name, tool_input) for t in rule["tools"]):
            continue
        if not match_path(rule.get("path_patterns"), path):
            continue
        return rule["effect"], rule["id"], rule.get("description")
    return policy.get("default", "allow"), None, None


def handle_task_prompt(payload: dict) -> int:
    """Scan a Task-tool delegation prompt for forbidden source tokens."""
    prompt = (payload.get("tool_input") or {}).get("prompt", "")
    matches = sorted(set(m.group(0) for m in FORBIDDEN_TOKEN_RE.finditer(prompt)))
    if matches:
        sys.stderr.write(
            "FIREWALL DENY (Task): coordinator prompt contains forbidden "
            f"source-code tokens: {', '.join(matches)}. Use spec-id references "
            "only; let the implementer resolve content via mcp__spec-store__read_spec.\n"
        )
        return 2
    return 0


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        sys.stderr.write(f"firewall: bad JSON on stdin: {e}\n")
        return 0  # do not break Claude on malformed input; fail open with audit trail
    if "--task" in sys.argv:
        return handle_task_prompt(payload)
    policy = load_policy()
    agent = payload.get("agent_type") or payload.get("agent_name") or "main"
    role = role_for(agent, policy)
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    effect, rule_id, descr = evaluate(policy, role, tool_name, tool_input)
    if effect == "deny":
        sys.stderr.write(
            f"FIREWALL DENY [{rule_id}] role={role} tool={tool_name} "
            f"path={tool_path(tool_name, tool_input)!r} :: {descr}\n"
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
