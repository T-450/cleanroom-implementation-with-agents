# redis-cleanroom

A worked example of clean-room re-implementation driven by Claude Code
multi-agent workflows. **Pedagogical only** — see the warning at the
bottom before running against any commercial Redis deployment.

## What this is

A subset of the Redis RESP2 protocol re-implemented in Rust without the
implementation team ever seeing the original `redis-server` source. Every
agent, hook, skill, slash command, MCP server, and `CLAUDE.md` overlay is
authored as a Claude Code primitive — there is no external orchestration
framework. The whole project is the worked example for **Volume IV** of
the [clean-room engineering wiki](../../../) (see chapters 18–22).

## Subset in scope

`PING`, `ECHO`, `SET` (with `EX`/`PX`/`NX`/`XX`), `GET`, `DEL`, `EXISTS`,
`EXPIRE`, `PEXPIRE`, `TTL`, `PTTL`, `INCR`, `DECR`, `INCRBY`, `DECRBY`,
`APPEND`, `STRLEN`, `KEYS` (glob), `DBSIZE`, `FLUSHDB`, `TYPE`,
`COMMAND DOCS`. **Out of scope:** replication, pub/sub, Lua scripting,
cluster, streams, modules, persistence, AUTH/ACL.

## Prerequisites

- Claude Code ≥ 2.0
- Rust ≥ 1.75 (`rustup`, `cargo`)
- `redis-server` ≥ 7.x and `redis-cli` on `$PATH`
- Python ≥ 3.11 with `uv`
- SQLite 3
- `just` (task runner)

## Bootstrap

```sh
just bootstrap   # uv-syncs the 3 MCP servers, pins redis-server, inits audit DB
```

## Smoke

```sh
just smoke       # discover, implement, and verify PING end to end
```

## Full pipeline for one command

```sh
just full-pipeline SET
```

This invokes `/run-cleanroom-pipeline SET`, which delegates Observation
→ Test Generation → Implementation → Verification subagents under the
coordinator's contract.

## Verifying the firewall

The legal firewall has two layers:

1. **File-level RBAC** via `hooks/firewall.py` (PreToolUse): blocks any
   `Read`/`Grep`/`Glob`/`Bash` from an implementation subagent against
   `original/`, `specs-raw/`, `transcripts/observation/`.
2. **Prose-level isolation** via the **Coordinator Contract** in
   `.claude/agents/coordinator.md`: the only subagent allowed to invoke
   `Task`, instructed to forward only spec-ids and never the prose
   returned by Observation. Every Task prompt is hashed and logged; the
   PreToolUse hook (called with `--task`) greps the prompt for forbidden
   source-code tokens.

Both layers are exercised by:

```sh
just verify-firewall
```

## Maintenance

`just doctor` surface-tests every Claude Code primitive and lists the
configured MCP servers, so rot is detected before a full pipeline run.

## Layout

See `CLAUDE.md` for the canonical layout map. Per-team overlays:
`CLAUDE.md.observation`, `CLAUDE.md.implementation`,
`CLAUDE.md.verification`. Schemas live under `../../schemas/`.

## Warning

This project's `original/redis-server` binary is governed by the upstream
Redis license. The clean-room methodology demonstrated here is for
pedagogical purposes; deploying any clean-room implementation of a
licensed product requires legal review specific to your jurisdiction and
intended use. See `../../legal/legal-framework.md` for general guidance
and `comparisons/legal-risk-assessment.md` for a risk model.
