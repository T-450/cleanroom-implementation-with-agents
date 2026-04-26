# redis-cleanroom — Project Charter

This project is the **runnable worked example** for Volume IV of the
clean-room engineering wiki. It rebuilds a subset of the Redis RESP protocol
in Rust without ever permitting the implementation team to read the original
`redis-server` source. Every artefact here is a Claude Code primitive
(subagents, skills, slash commands, hooks, MCP servers, `CLAUDE.md`
overlays). There is no orchestration framework — the coordinator is just a
subagent that uses the `Task` tool.

## Layout

| Path | Visibility |
| ---- | ---------- |
| `original/`       | **Observation** team only — pinned `redis-server` binary used as the parity oracle. Implementation team **must not** Read this. |
| `specs-raw/`      | Observation only — raw probe transcripts. |
| `transcripts/observation/` | Observation only — extractor reasoning traces. |
| `specs/`          | Public — JSON spec artifacts validated against `volumes/IV/schemas/spec-artifact.schema.json`. |
| `tests/parity/`   | Public — example-based parity cases per command. |
| `tests/properties/` | Public — `proptest`/`quickcheck` property tests. |
| `src/`            | **Implementation** team only writes here. |
| `reports/parity/`, `reports/audit/` | Public — generated outputs. |

## Roles & the legal firewall

There are four agent roles. Each subagent's frontmatter declares its role,
which `hooks/firewall.py` consults to enforce file-level access rules
(see `volumes/IV/schemas/tool-policy.schema.json` and the per-team overlay
files `CLAUDE.md.observation`, `CLAUDE.md.implementation`,
`CLAUDE.md.verification`):

- **observation** — may probe `original/`, write `specs/` and `specs-raw/`.
- **implementation** — may read `specs/` and `tests/`, write `src/` and
  `tests/properties/`. **Never** reads `original/`, `specs-raw/`, or
  `transcripts/observation/`.
- **verification** — may read everything except `transcripts/observation/`.
  May not write `src/`.
- **coordinator** — only role allowed to invoke the `Task` tool. Its
  prompt-level discipline is the prose-level firewall (see Chapter 20).

`hooks/firewall.py` is necessary but not sufficient: the coordinator can
leak observation prose into impl prompts via `Task` even without touching
the filesystem. The coordinator's contract (in
`.claude/agents/coordinator.md`) is therefore the primary firewall;
`firewall.py` is defense-in-depth for the file-system channel.

## Definition of done (per command)

A RESP command (e.g., `SET`, `EXPIRE`) is "done" only when:
1. `specs/<cmd>.json` exists, validates, has ≥ 6 cited probes, and has
   `status: "frozen"`.
2. `tests/parity/<cmd>/*.json` is non-empty and the curator has signed off.
3. `cargo test` is green for the command's module.
4. The latest `reports/parity/<run>.json` shows
   `summary.deterministic_subset_pass_rate == 1.0` and
   `summary.parity_rate >= 0.99` for the command.
5. `reports/audit/<session>.json` shows zero `decision: "denied"` events
   originating from `agent_role: "implementation"` against forbidden paths,
   and zero `task_prompt_redaction.matched_forbidden_tokens` from the
   coordinator.

## Bootstrap

```
just bootstrap   # set up MCP venvs, pin redis-server, init audit DB
just smoke       # discover & implement PING (the simplest command) end to end
just full-pipeline SET   # run the full clean-room workflow for SET
```

## Pinned versions

- Claude Code: ≥ 2.0 (slash commands, skills, agents, hooks, MCP)
- Rust: ≥ 1.75
- redis-server (original): pinned in `original/VERSION` after `just bootstrap`

## Cross-references

- `volumes/IV/chapters/chapter18_*.md` … `chapter22_*.md` walk through
  every primitive used here.
- `volumes/IV/schemas/` defines the JSON formats every subagent and MCP
  server speaks.
- `volumes/VI/chapters/chapter27..31` describe the abstract patterns this
  project realizes.
