#!/usr/bin/env python3
"""spec-store MCP server.

Resources:
  spec://command/{spec_id}      a single frozen spec artifact
  spec://command-list           list of spec_ids and statuses

Tools:
  read_spec(spec_id)            return the full spec artifact
  write_spec(spec_artifact)     validate against schema, write to specs/
  freeze_spec(spec_id)          set status=frozen, refuse further edits
  list_specs()                  list spec_ids with status

Validates every read and write against
volumes/IV/schemas/spec-artifact.schema.json. Refuses writes that
introduce a behaviour without at least one probe_ref (the schema enforces
this at the JSON-Schema level; this server adds the friendlier error
message).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
    from mcp.server.fastmcp import FastMCP
except ImportError:
    sys.stderr.write("spec-store: install dependencies first: `uv sync`.\n")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent.parent
SPEC_DIR = Path(os.environ.get("SPEC_DIR", str(PROJECT_ROOT / "specs")))
SCHEMA_PATH = Path(os.environ.get(
    "SPEC_SCHEMA",
    str(PROJECT_ROOT.parent.parent / "schemas" / "spec-artifact.schema.json"),
))

mcp = FastMCP("spec-store")
_validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))


def _spec_path(spec_id: str) -> Path:
    if not spec_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError(f"invalid spec_id: {spec_id!r}")
    return SPEC_DIR / f"{spec_id}.json"


def _validate(artifact: dict) -> None:
    errors = sorted(_validator.iter_errors(artifact), key=lambda e: list(e.path))
    if errors:
        msgs = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in errors[:5]]
        raise ValueError("spec-artifact validation failed: " + "; ".join(msgs))


@mcp.tool()
def read_spec(spec_id: str) -> dict[str, Any]:
    """Return the full spec artifact for a given id."""
    path = _spec_path(spec_id)
    if not path.exists():
        raise FileNotFoundError(f"no spec for id={spec_id}")
    artifact = json.loads(path.read_text())
    _validate(artifact)
    return artifact


@mcp.tool()
def write_spec(spec_artifact: dict[str, Any]) -> dict[str, str]:
    """Validate and persist a spec artifact. Refuses overwrite of frozen specs."""
    _validate(spec_artifact)
    spec_id = spec_artifact["spec_id"]
    path = _spec_path(spec_id)
    if path.exists():
        existing = json.loads(path.read_text())
        if existing.get("status") == "frozen":
            raise PermissionError(f"spec {spec_id} is frozen; cannot overwrite")
    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec_artifact, indent=2) + "\n")
    return {"spec_id": spec_id, "path": str(path), "status": spec_artifact.get("status", "draft")}


@mcp.tool()
def freeze_spec(spec_id: str) -> dict[str, str]:
    """Mark a spec as frozen. After this no agent may edit it."""
    path = _spec_path(spec_id)
    artifact = json.loads(path.read_text())
    artifact["status"] = "frozen"
    _validate(artifact)
    path.write_text(json.dumps(artifact, indent=2) + "\n")
    return {"spec_id": spec_id, "status": "frozen"}


@mcp.tool()
def list_specs() -> list[dict[str, str]]:
    """Return the list of spec_ids with their statuses."""
    out: list[dict[str, str]] = []
    if not SPEC_DIR.exists():
        return out
    for p in sorted(SPEC_DIR.glob("*.json")):
        try:
            a = json.loads(p.read_text())
            out.append({"spec_id": a["spec_id"], "status": a.get("status", "draft"), "version": a.get("version", "")})
        except Exception as e:
            out.append({"spec_id": p.stem, "status": "invalid", "error": str(e)})
    return out


@mcp.resource("spec://command/{spec_id}")
def spec_resource(spec_id: str) -> str:
    return json.dumps(read_spec(spec_id), indent=2)


@mcp.resource("spec://command-list")
def spec_list_resource() -> str:
    return json.dumps(list_specs(), indent=2)


if __name__ == "__main__":
    mcp.run()
