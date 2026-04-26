#!/usr/bin/env python3
"""User-prompt redactor (UserPromptSubmit hook).

If the user pastes recognisable original-Redis source text into chat (a
common contamination vector when debugging), refuse the submission.
Defense-in-depth only; the primary contamination channel is the
coordinator's Task prompts (see hooks/firewall.py --task).

Exit codes:
  0  allow (no fingerprints found)
  2  deny (Claude Code surfaces stderr to the model and the user)
"""
from __future__ import annotations

import json
import re
import sys

FINGERPRINTS = [
    re.compile(r"#include\s+\"server\.h\""),
    re.compile(r"\bstruct\s+redisCommand\b"),
    re.compile(r"\baddReplyError\w*\s*\("),
    re.compile(r"\baddReplyBulk\w*\s*\("),
    re.compile(r"\brobj\s*\*"),
    re.compile(r"redisCommandTable\s*\["),
    re.compile(r"createObject\s*\(\s*OBJ_STRING"),
]


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    text = payload.get("prompt", "") or payload.get("user_prompt", "") or ""
    hits = [p.pattern for p in FINGERPRINTS if p.search(text)]
    if hits:
        sys.stderr.write(
            "REDACTOR DENY: user prompt contains original-Redis source "
            f"fingerprints: {hits}. The legal firewall forbids pasting "
            "original source into the conversation. Paraphrase the question "
            "in terms of observable behaviour and resubmit.\n"
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
